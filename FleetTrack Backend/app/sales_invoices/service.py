from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException

from app.master_data import database_errors
from . import repository as repo


TYPE_TO_VOUCHER_NAME = {
    "rental": "Rental Invoice",
    "salik": "Salik Invoice",
    "fine": "Fine Invoice",
    "misc": "Misc Invoice",
    "vehicle": "Vehicle Invoice",
}
VOUCHER_ID_TO_TYPE = {31: "rental", 32: "salik", 33: "fine", 34: "misc", 38: "vehicle"}
MONEY = Decimal("0.00001")


def _decimal(value) -> Decimal:
    return Decimal(value or 0)


def _round(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def _voucher_type(db, invoice_type):
    row = repo.get_voucher_type(db, TYPE_TO_VOUCHER_NAME[invoice_type])
    if row is None:
        raise HTTPException(422, f"{invoice_type} invoice type is not configured")
    return row


def _require_lookup(db, table, key, value, field):
    if repo.get_lookup(db, table, key, value) is None:
        raise HTTPException(422, f"{field}: selected lookup record does not exist")


def _validate_payload(db, payload, voucher):
    customer = repo.get_customer(db, payload.customerId)
    if customer is None:
        raise HTTPException(422, "customerId must be an existing customer")
    _require_lookup(db, repo.LEDGER, "ledgerId", payload.salesAccountId, "salesAccountId")
    _require_lookup(db, repo.EXCHANGE_RATE, "exchangeRateId", payload.exchangeRateId, "exchangeRateId")
    _require_lookup(db, repo.LOCATION, "LocationId", payload.locationId, "locationId")
    financial_year = repo.get_financial_year(db, payload.invoiceDate)
    if financial_year is None:
        raise HTTPException(422, "invoiceDate does not belong to a configured financial year")
    suffix_prefix = None
    if payload.invoiceType != "vehicle":
        suffix_prefix = repo.get_suffix_prefix(db, voucher["voucherTypeId"], payload.invoiceDate)
        if suffix_prefix is None:
            raise HTTPException(422, "invoiceDate does not have a configured invoice numbering rule")
    if payload.salesPersonId is not None:
        _require_lookup(db, repo.EMPLOYEE, "employeeId", payload.salesPersonId, "salesPersonId")

    contract = None
    if payload.contractId is not None:
        contract = repo.get_contract(db, payload.contractId)
        if contract is None:
            raise HTTPException(422, "contractId: selected contract does not exist")
        if int(contract["CustomerId"] or 0) != payload.customerId:
            raise HTTPException(422, "contractId does not belong to customerId")
    if payload.invoiceType == "vehicle" and payload.contractId is not None:
        raise HTTPException(422, "Vehicle Invoice cannot be linked to a rental contract")
    if payload.invoiceType in {"rental", "salik", "fine"} and contract is None:
        raise HTTPException(422, f"{payload.invoiceType} invoice requires contractId")

    for line in payload.lines:
        item = repo.get_lookup(db, repo.ITEM_TYPE, "ItemType", line.itemTypeId)
        if item is None or item["IsActive"] is not True or int(item["VoucherType"] or 0) != int(voucher["voucherTypeId"]):
            raise HTTPException(422, "itemTypeId is not active for the selected invoice type")
        _require_lookup(db, repo.UNIT, "unitId", line.unitId, "unitId")
        tax = repo.get_lookup(db, repo.TAX, "taxId", line.taxId)
        if tax is None or tax["isActive"] is not True:
            raise HTTPException(422, "taxId must be an active tax")
        if not repo.tax_is_available_for_invoice(db, voucher["voucherTypeId"], line.itemTypeId, line.taxId):
            raise HTTPException(422, "taxId is not available for the selected invoice type and item type")
        if line.vehicleId is not None:
            if repo.get_vehicle(db, line.vehicleId) is None:
                raise HTTPException(422, "vehicleId: selected vehicle does not exist")
            if contract is not None and not repo.vehicle_belongs_to_contract(db, payload.contractId, line.vehicleId):
                raise HTTPException(422, "vehicleId is not assigned to contractId")
        if payload.invoiceType == "vehicle" and line.vehicleId is None:
            raise HTTPException(422, "Vehicle Invoice requires a registered vehicle on every line")
    return customer, contract, financial_year, suffix_prefix


def _build_lines(db, payload):
    values = []
    tax_totals = defaultdict(lambda: Decimal("0"))
    total_amount = Decimal("0")
    for sl_no, line in enumerate(payload.lines, start=1):
        tax = repo.get_lookup(db, repo.TAX, "taxId", line.taxId)
        base = _round(line.quantity * line.rate)
        net = _round(base - line.discount)
        if net < 0:
            raise HTTPException(422, "line discount cannot exceed quantity multiplied by rate")
        tax_amount = _round(net * _decimal(tax["rate"]) / Decimal("100"))
        amount = _round(net + tax_amount)
        total_amount += amount
        tax_totals[line.taxId] += tax_amount
        values.append({
            "itemTypeId": line.itemTypeId,
            "vehicleId": line.vehicleId,
            "description": line.description,
            "qty": line.quantity,
            "rate": line.rate,
            "unitId": line.unitId,
            "discount": line.discount,
            "taxId": line.taxId,
            "taxAmount": tax_amount,
            "grossAmount": base,
            "netAmount": net,
            "amount": amount,
            "slNo": sl_no,
        })
    total_amount = _round(total_amount)
    if payload.billDiscount > total_amount:
        raise HTTPException(422, "billDiscount cannot exceed total amount")
    taxes = [{"taxId": tax_id, "taxAmount": _round(amount)} for tax_id, amount in tax_totals.items() if amount]
    return values, taxes, _round(sum(t["taxAmount"] for t in taxes)), total_amount, _round(total_amount - payload.billDiscount)


def _vehicle_summary(db, payload):
    labels = []
    seen_vehicle_ids = set()
    for line in payload.lines:
        if line.vehicleId is None or line.vehicleId in seen_vehicle_ids:
            continue
        seen_vehicle_ids.add(line.vehicleId)
        vehicle = repo.get_vehicle(db, line.vehicleId)
        labels.append(str(vehicle["PlateNo"]))
    return "; ".join(labels)


def _response(db, header):
    if header is None:
        raise HTTPException(404, "Sales invoice not found")
    voucher_type_id = int(header["voucherTypeId"])
    invoice_type = VOUCHER_ID_TO_TYPE.get(voucher_type_id)
    if invoice_type is None:
        raise HTTPException(404, "Sales invoice is not a FleetTrack sales invoice type")
    location_name = header.get("extra1")
    lines = []
    for row in repo.list_invoice_lines(db, int(header["salesMasterId"])):
        lines.append({
            "salesDetailsId": int(row["salesDetailsId"]), "slNo": row["slNo"],
            "itemTypeId": row["itemTypeId"], "itemTypeName": row["itemTypeName"],
            "vehicleId": row["vehicleId"], "description": row["description"],
            "quantity": _decimal(row["qty"]), "unitId": row["unitId"], "unitName": row["unitName"],
            "rate": _decimal(row["rate"]), "discount": _decimal(row["discount"]),
            "taxId": row["taxId"], "taxName": row["taxName"], "taxRate": row["taxRate"],
            "taxAmount": _decimal(row["taxAmount"]), "grossAmount": _decimal(row["grossAmount"]),
            "netAmount": _decimal(row["netAmount"]), "amount": _decimal(row["amount"]),
        })
    taxes = [{"taxId": int(row["taxId"]), "taxName": row["taxName"], "taxAmount": _decimal(row["taxAmount"])} for row in repo.list_invoice_taxes(db, int(header["salesMasterId"]))]
    return {
        "salesMasterId": int(header["salesMasterId"]), "invoiceType": invoice_type,
        "voucherTypeId": voucher_type_id, "voucherNo": header["voucherNo"], "invoiceNo": header["invoiceNo"],
        "invoiceDate": header["date"], "customerId": header["ledgerId"], "customerName": header["customerName"],
        "contractId": header["contractId"], "contractRefNo": header["contractRefNo"],
        "creditPeriod": int(header["creditPeriod"]), "lpoNo": header["lpoNo"],
        "salesAccountId": header["salesAccount"], "salesAccountName": header["salesAccountName"],
        "salesPersonId": header["employeeId"], "exchangeRateId": header["exchangeRateId"],
        "locationName": location_name, "taxAmount": _decimal(header["taxAmount"]),
        "billDiscount": _decimal(header["billDiscount"]), "totalAmount": _decimal(header["totalAmount"]),
        "grandTotal": _decimal(header["grandTotal"]), "narration": header["narration"],
        "isPosted": header["isPosted"], "vehicleNos": header["vehicleNos"], "lines": lines, "taxes": taxes,
    }


def get_invoice(db, sales_master_id):
    with database_errors(db):
        return _response(db, repo.get_invoice_header(db, sales_master_id))


def list_invoices(db, q=None, invoice_type=None, posted=None, offset=0, limit=10):
    with database_errors(db):
        voucher_id = None
        if invoice_type is not None:
            voucher_id = int(_voucher_type(db, invoice_type)["voucherTypeId"])
        rows, total = repo.list_invoices(db, q=q, invoice_type_id=voucher_id, posted=posted, offset=offset, limit=limit)
        items = [{
            "salesMasterId": int(row["salesMasterId"]), "invoiceType": VOUCHER_ID_TO_TYPE[int(row["voucherTypeId"])],
            "voucherTypeId": int(row["voucherTypeId"]), "voucherNo": row["voucherNo"], "invoiceNo": row["invoiceNo"],
            "invoiceDate": row["invoiceDate"], "customerName": row["customerName"], "contractRefNo": row["contractRefNo"],
            "vehicleNos": row["vehicleNos"], "grandTotal": _decimal(row["grandTotal"]), "isPosted": row["isPosted"],
        } for row in rows]
        return {"items": items, "total": total, "offset": offset, "limit": limit}


def _draft_values(payload, customer, contract, voucher, suffix_prefix, tax_amount, total_amount, grand_total, user_id, location_name, financial_year_id):
    return {
        "creditPeriod": payload.creditPeriod, "voucherNo": None, "invoiceNo": None,
        "voucherTypeId": voucher["voucherTypeId"],
        "suffixPrefixId": int(suffix_prefix["suffixprefixId"]) if suffix_prefix is not None else 0,
        "date": payload.invoiceDate,
        "lpoNo": payload.lpoNo, "ledgerId": payload.customerId, "employeeId": payload.salesPersonId,
        "salesAccount": payload.salesAccountId, "narration": payload.narration,
        "customerName": customer["ledgerName"], "exchangeRateId": payload.exchangeRateId,
        "taxAmount": tax_amount, "additionalCost": Decimal("0"), "billDiscount": payload.billDiscount,
        "grandTotal": grand_total, "totalAmount": total_amount, "userId": user_id,
        "POS": False, "counterId": None, "financialYearId": financial_year_id, "extraDate": None,
        "extra1": location_name, "extra2": None,
        "contractId": payload.contractId or 0, "contractRefNo": contract["ContractRefNo"] if contract else "NA",
        "trafficFineNo": "", "isPosted": False,
    }


def create_draft(db, payload, user_id):
    with database_errors(db):
        if payload.invoiceType == "rental":
            raise HTTPException(422, "Rental Invoice drafts must be created through the contract rental-billing workflow")
        result = create_draft_in_transaction(db, payload, user_id)
        db.commit()
        return result


def create_draft_in_transaction(db, payload, user_id):
    """Create a validated draft in the caller's transaction without committing it."""
    voucher = _voucher_type(db, payload.invoiceType)
    customer, contract, financial_year, suffix_prefix = _validate_payload(db, payload, voucher)
    lines, taxes, tax_amount, total_amount, grand_total = _build_lines(db, payload)
    location = repo.get_lookup(db, repo.LOCATION, "LocationId", payload.locationId)
    sales_master_id = repo.create_sales_master(db, _draft_values(payload, customer, contract, voucher, suffix_prefix, tax_amount, total_amount, grand_total, user_id, location["LocationName"], financial_year["financialYearId"]))
    repo.replace_details(db, sales_master_id, [{**line, "salesMasterId": sales_master_id} for line in lines], [{**tax, "salesMasterId": sales_master_id} for tax in taxes])
    repo.update_sales_master(db, sales_master_id, {"vehicleNos": _vehicle_summary(db, payload)})
    return _response(db, repo.get_invoice_header(db, sales_master_id))


def update_draft(db, sales_master_id, payload, user_id):
    with database_errors(db):
        existing = repo.get_invoice_header(db, sales_master_id)
        if existing is None:
            raise HTTPException(404, "Sales invoice not found")
        if existing["isPosted"] is True:
            raise HTTPException(409, "Posted sales invoices cannot be edited")
        if int(existing["voucherTypeId"] or 0) == 31:
            raise HTTPException(422, "Rental Invoice drafts are managed through the contract rental-billing workflow")
        voucher = _voucher_type(db, payload.invoiceType)
        if int(existing["voucherTypeId"]) != int(voucher["voucherTypeId"]):
            raise HTTPException(422, "invoiceType cannot be changed after draft creation")
        customer, contract, financial_year, suffix_prefix = _validate_payload(db, payload, voucher)
        lines, taxes, tax_amount, total_amount, grand_total = _build_lines(db, payload)
        location = repo.get_lookup(db, repo.LOCATION, "LocationId", payload.locationId)
        values = _draft_values(payload, customer, contract, voucher, suffix_prefix, tax_amount, total_amount, grand_total, user_id, location["LocationName"], financial_year["financialYearId"])
        values.pop("voucherNo")
        values.pop("invoiceNo")
        repo.update_sales_master(db, sales_master_id, values)
        repo.replace_details(db, sales_master_id, [{**line, "salesMasterId": sales_master_id} for line in lines], [{**tax, "salesMasterId": sales_master_id} for tax in taxes])
        repo.update_sales_master(db, sales_master_id, {"vehicleNos": _vehicle_summary(db, payload)})
        db.commit()
        return _response(db, repo.get_invoice_header(db, sales_master_id))


def delete_draft(db, sales_master_id):
    with database_errors(db):
        existing = repo.get_invoice_header(db, sales_master_id)
        if existing is None:
            raise HTTPException(404, "Sales invoice not found")
        if existing["isPosted"] is True:
            raise HTTPException(409, "Posted sales invoices cannot be deleted")
        if int(existing["voucherTypeId"] or 0) == 31:
            raise HTTPException(422, "Rental Invoice drafts must be deleted through the contract rental-billing workflow")
        repo.delete_draft(db, sales_master_id, existing["voucherTypeId"], existing["voucherNo"])
        db.commit()


def post_invoice(db, sales_master_id):
    raise HTTPException(501, "Posting is not enabled until VAT output-ledger and Sold-status mappings are verified in the live database")


def unpost_invoice(db, sales_master_id):
    raise HTTPException(501, "Unposting is not enabled until complete ledger, party-balance, source-charge, and vehicle-status reversal rules are verified")


def _vehicle_lookup(row):
    plate_code = (row.get("PlateCodeName") or "").strip()
    plate_no = (row.get("PlateNo") or "").strip()
    return {
        "id": int(row["VehicleId"]),
        "name": " ".join(value for value in (plate_code, plate_no) if value),
        "vehicleId": int(row["VehicleId"]),
        "plateCode": plate_code or None,
        "plateNo": plate_no or None,
        "statusId": int(row["StatusId"]) if row["StatusId"] is not None else None,
    }


def numbering_rule(db, invoice_type, invoice_date):
    with database_errors(db):
        if invoice_type == "vehicle":
            raise HTTPException(422, "Vehicle Invoice has no configured prefix/suffix numbering rule")
        voucher = _voucher_type(db, invoice_type)
        rule = repo.get_suffix_prefix(db, voucher["voucherTypeId"], invoice_date)
        if rule is None:
            raise HTTPException(422, "invoiceDate does not have a configured invoice numbering rule")
        return {
            "suffixPrefixId": int(rule["suffixprefixId"]),
            "prefix": rule["prefix"], "suffix": rule["suffix"],
            "startIndex": int(rule["startIndex"]) if rule["startIndex"] is not None else None,
            "widthOfNumericalPart": rule["widthOfNumericalPart"],
            "prefillWithZero": rule["prefillWithZero"],
            "fromDate": rule["fromDate"], "toDate": rule["toDate"],
        }


def lookups(db, name, invoice_type=None, customer_id=None, contract_id=None):
    with database_errors(db):
        if name == "types":
            return [{"id": int(row["voucherTypeId"]), "name": row["voucherTypeName"]} for row in repo.invoice_types(db)]
        if name == "item-types":
            if invoice_type is None:
                raise HTTPException(422, "invoiceType is required")
            voucher = _voucher_type(db, invoice_type)
            return [{"id": int(row["ItemType"]), "name": row["ItemTypeName"], "taxId": row["TaxId"], "taxRate": row["taxRate"]} for row in repo.item_types(db, voucher["voucherTypeId"])]
        if name == "taxes":
            if invoice_type is None:
                raise HTTPException(422, "invoiceType is required")
            voucher = _voucher_type(db, invoice_type)
            return [{"id": int(row["taxId"]), "name": row["taxName"], "taxRate": row["rate"]} for row in repo.taxes(db, voucher["voucherTypeId"])]
        if name == "units":
            return [{"id": int(row["unitId"]), "name": row["unitName"]} for row in repo.units(db)]
        if name == "sales-accounts":
            return [{"id": int(row["ledgerId"]), "name": row["ledgerName"]} for row in repo.sales_accounts(db)]
        if name == "locations":
            return [{"id": int(row["LocationId"]), "name": row["LocationName"]} for row in repo.locations(db)]
        if name == "exchange-rates":
            return [{
                "id": int(row["exchangeRateId"]),
                "name": " | ".join(value for value in (row["currencyName"], row["currencySymbol"]) if value) or str(row["rate"]),
                "rate": row["rate"],
                "currencyId": int(row["currencyId"]) if row["currencyId"] is not None else None,
                "currencyName": row["currencyName"],
                "currencySymbol": row["currencySymbol"],
            } for row in repo.exchange_rates_with_currency(db)]
        if name == "contracts":
            if customer_id is None:
                raise HTTPException(422, "customerId is required")
            if repo.get_customer(db, customer_id) is None:
                raise HTTPException(422, "customerId must be an existing customer")
            return [{
                "id": int(row["ContractId"]), "name": row["ContractRefNo"],
                "contractId": int(row["ContractId"]), "contractRefNo": row["ContractRefNo"],
                "statusId": int(row["Status"]) if row["Status"] is not None else None,
                "startDate": row["ContractStartDate"], "endDate": row["ContractExpectedEndDate"],
            } for row in repo.contracts_for_customer(db, customer_id)]
        if name == "vehicles":
            if invoice_type is None:
                raise HTTPException(422, "invoiceType is required")
            if invoice_type in {"rental", "fine", "salik"}:
                if contract_id is None:
                    raise HTTPException(422, "contractId is required")
                if repo.get_contract(db, contract_id) is None:
                    raise HTTPException(422, "contractId does not exist")
                return [_vehicle_lookup(row) for row in repo.contract_vehicles(db, contract_id)]
            # Vehicle status is included for the UI, but whether a status is sellable
            # is not yet verified, so this endpoint does not make that claim.
            return [_vehicle_lookup(row) for row in repo.registered_vehicles(db)]
        raise HTTPException(404, "Unknown sales invoice lookup")


def _source_setup(db, invoice_type, item_type_name):
    voucher = _voucher_type(db, invoice_type)
    item = repo.get_item_type_by_name(db, voucher["voucherTypeId"], item_type_name)
    unit = repo.get_unit_by_name(db, "NOS")
    if item is None or item["TaxId"] is None or unit is None:
        raise HTTPException(422, f"{invoice_type} source configuration is incomplete")
    return item, unit


def _source_contract(db, contract_id):
    contract = repo.get_contract(db, contract_id)
    if contract is None:
        raise HTTPException(404, "contractId does not exist")
    return contract


def rental_source(db, contract_id, through_date=None):
    with database_errors(db):
        contract = _source_contract(db, contract_id)
        item, unit = _source_setup(db, "rental", "Rental Rate")
        vehicles = repo.contract_vehicles(db, contract_id)
        vehicle_id = int(vehicles[0]["VehicleId"]) if len(vehicles) == 1 else None
        source_date = through_date or contract["ContractExpectedEndDate"]
        description = f"Rental contract # {contract['ContractRefNo']}"
        if source_date is not None:
            description += f" through {source_date.date().isoformat()}"
        return {
            "invoiceType": "rental", "contractId": contract_id, "contractRefNo": contract["ContractRefNo"],
            "lines": [{
                "sourceType": "rental", "sourceId": f"contract:{contract_id}",
                "itemTypeId": int(item["ItemType"]), "vehicleId": vehicle_id,
                "description": description, "quantity": Decimal("1"), "unitId": int(unit["unitId"]),
                "rate": _decimal(contract["Rate"]), "taxId": int(item["TaxId"]), "sourceDate": source_date,
            }],
        }


def fine_source(db, contract_id):
    with database_errors(db):
        contract = _source_contract(db, contract_id)
        item, unit = _source_setup(db, "fine", "Traffic Fine")
        lines = []
        for row in repo.unposted_fines_for_contract(db, contract_id):
            details = " - ".join(value for value in (row["AUTHORITY"], row["FINEDESCRIPTION"]) if value)
            description = f"Traffic fine {row['TICKETNO']}"
            if details:
                description += f": {details}"
            lines.append({
                "sourceType": "fine", "sourceId": str(row["TICKETNO"]),
                "itemTypeId": int(item["ItemType"]), "vehicleId": int(row["VEHICLEID"]),
                "description": description, "quantity": Decimal("1"), "unitId": int(unit["unitId"]),
                "rate": _decimal(row["AMOUNT"]), "taxId": int(item["TaxId"]), "sourceDate": row["FINEDATETIME"],
            })
        return {"invoiceType": "fine", "contractId": contract_id, "contractRefNo": contract["ContractRefNo"], "lines": lines}


def salik_source(db, contract_id, from_date, to_date):
    if from_date > to_date:
        raise HTTPException(422, "from must be on or before to")
    with database_errors(db):
        contract = _source_contract(db, contract_id)
        item, unit = _source_setup(db, "salik", "Salik Toll")
        lines = []
        for row in repo.unposted_salik_for_contract(db, contract_id, from_date, to_date):
            details = " - ".join(value for value in (row["LOCATION"], row["DIRECTION"]) if value)
            description = "Salik toll"
            if details:
                description += f": {details}"
            lines.append({
                "sourceType": "salik", "sourceId": str(row["TRANSID"]),
                "itemTypeId": int(item["ItemType"]), "vehicleId": int(row["VehicleId"]),
                "description": description, "quantity": Decimal("1"), "unitId": int(unit["unitId"]),
                "rate": _decimal(row["AMOUNT"]), "taxId": int(item["TaxId"]), "sourceDate": row["DATEANDTIME"],
            })
        return {"invoiceType": "salik", "contractId": contract_id, "contractRefNo": contract["ContractRefNo"], "lines": lines}
