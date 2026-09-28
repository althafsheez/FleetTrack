from calendar import monthrange
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_CEILING

from fastapi import HTTPException

from app.master_data import database_errors
from app.sales_invoices import repository as sales_repo
from app.sales_invoices import service as sales_service
from app.sales_invoices.schemas import InvoiceLineInput, SalesInvoiceDraftInput
from . import repository as repo


OPEN_CONTRACT_STATUS = 8
DAILY_PAYMENT_TYPE = 1
WEEKLY_PAYMENT_TYPE = 2
MONTHLY_PAYMENT_TYPE = 3
MONTH_END_BILLING_TYPE = 1
DATE_TO_DATE_BILLING_TYPE = 2
def _decimal(value):
    return Decimal(value or 0)


def _legacy_ceiling(value):
    return _decimal(value).quantize(Decimal("1"), rounding=ROUND_CEILING)


def _add_month(value):
    month = value.month + 1
    year = value.year
    if month == 13:
        month = 1
        year += 1
    return value.replace(year=year, month=month, day=min(value.day, monthrange(year, month)[1]))


def _first_day_next_month(value):
    return _add_month(value).replace(day=1)


def _require_contract(contract):
    if contract is None:
        raise HTTPException(404, "Contract not found")
    if int(contract["Status"] or 0) != OPEN_CONTRACT_STATUS:
        raise HTTPException(409, "Rental Invoice can be created only for an open contract")
    if int(contract["PaymentType"] or 0) == DAILY_PAYMENT_TYPE:
        raise HTTPException(422, "Daily contracts are invoiced at check-in and are outside this release")
    if int(contract["PaymentType"] or 0) not in {WEEKLY_PAYMENT_TYPE, MONTHLY_PAYMENT_TYPE}:
        raise HTTPException(422, "Contract payment type is not supported for rental billing")
    if contract["NextInvStDate"] is None:
        raise HTTPException(422, "Contract does not have a rental billing schedule")


def _cycle_boundary(value, payment_type, billing_type):
    if payment_type == WEEKLY_PAYMENT_TYPE:
        return value + timedelta(days=7)
    if billing_type == MONTH_END_BILLING_TYPE:
        return _first_day_next_month(value)
    if billing_type == DATE_TO_DATE_BILLING_TYPE:
        return _add_month(value)
    raise HTTPException(422, "Contract billing type is not supported for rental billing")


def _schedule(contract, initial):
    payment_type = int(contract["PaymentType"])
    billing_type = int(contract["BillingType"] or 0)
    is_advance = bool(contract["IsAdvanceInvoice"])
    if is_advance:
        period_start = contract["NextInvStDate"]
        invoice_date = contract["ContractStartDate"] if initial else contract["NextInvStDate"]
        next_invoice_date = _cycle_boundary(period_start, payment_type, billing_type)
        return period_start, next_invoice_date - timedelta(days=1), invoice_date, next_invoice_date

    period_start = contract["LastInvoiceDate"] or contract["ContractStartDate"]
    invoice_date = contract["NextInvStDate"]
    next_invoice_date = _cycle_boundary(invoice_date, payment_type, billing_type)
    return period_start, invoice_date - timedelta(days=1), invoice_date, next_invoice_date


def _discount_amount(contract):
    rate = _decimal(contract["Rate"])
    discount = _decimal(contract["Discount"])
    discount_type = int(contract["DiscountType"] or 0)
    if discount_type == 1:
        return _legacy_ceiling(rate * discount / Decimal("100"))
    if discount_type == 2:
        return discount
    raise HTTPException(422, "Contract discount type is not supported for rental billing")


def _description(contract, vehicle_id, item_name, period_start, period_end):
    ref = contract["ContractRefNo"] or contract["RTACode"] or str(contract["ContractId"])
    return (
        f"{item_name} | Contract # {ref} | Vehicle {vehicle_id} | "
        f"{period_start.date().isoformat()} to {period_end.date().isoformat()}"
    )


def _build_input(db, contract, settings, initial):
    assignment = repo.get_current_vehicle_assignment(db, int(contract["ContractId"]))
    if assignment is None:
        raise HTTPException(422, "Contract has no assigned vehicle")
    period_start, period_end, invoice_date, next_invoice_date = _schedule(contract, initial)
    voucher = sales_repo.get_voucher_type(db, "Rental Invoice")
    unit = sales_repo.get_unit_by_name(db, "NOS")
    if voucher is None or unit is None:
        raise HTTPException(422, "Rental Invoice item or unit configuration is incomplete")

    rate = _legacy_ceiling(_decimal(contract["Rate"]) - _discount_amount(contract))
    if rate < 0:
        raise HTTPException(422, "Contract discount cannot exceed rental rate")
    charge_values = [
        ("Rental Rate", "Rental Rate", rate),
        ("Driver Charges", "Rental Driver Charges", _legacy_ceiling(contract["DriverCharges"])),
        ("Additional Driver", "Rental Add. Driver Charges", _legacy_ceiling(contract["AddDriverCharges"])),
        ("CDW", "Rental CDW", _legacy_ceiling(contract["CDW"])),
        ("PAI", "Rental PAI", _legacy_ceiling(contract["PAI"])),
    ]
    lines = []
    line_names = {}
    for description_name, item_type_name, amount in charge_values:
        if amount <= 0:
            continue
        item = sales_repo.get_item_type_by_name(db, voucher["voucherTypeId"], item_type_name)
        if item is None or item["TaxId"] is None:
            raise HTTPException(422, f"Rental Invoice item configuration is incomplete for {item_type_name}")
        line_names[int(item["ItemType"])] = item_type_name
        lines.append(InvoiceLineInput(
            itemTypeId=int(item["ItemType"]),
            vehicleId=int(assignment["VehicleId"]),
            description=_description(contract, assignment["VehicleId"], description_name, period_start, period_end),
            quantity=Decimal("1"),
            unitId=int(unit["unitId"]),
            rate=amount,
            taxId=int(item["TaxId"]),
        ))
    if not lines:
        raise HTTPException(422, "Contract has no positive rental charges to invoice")

    ref = contract["ContractRefNo"] or contract["RTACode"] or str(contract["ContractId"])
    narration = f"Rental contract # {ref}; {period_start.date().isoformat()} to {period_end.date().isoformat()}"
    payload = SalesInvoiceDraftInput(
        invoiceType="rental",
        invoiceDate=invoice_date,
        customerId=int(contract["CustomerId"]),
        contractId=int(contract["ContractId"]),
        creditPeriod=settings.creditPeriod,
        lpoNo=settings.lpoNo,
        salesAccountId=settings.salesAccountId,
        salesPersonId=int(contract["SalesPersonId"]) if contract["SalesPersonId"] is not None else None,
        exchangeRateId=settings.exchangeRateId,
        locationId=int(contract["ContractLocId"]),
        narration=narration,
        lines=lines,
    )
    return payload, period_start, period_end, next_invoice_date, line_names


def _preview(db, contract, settings, initial):
    payload, period_start, period_end, next_invoice_date, line_names = _build_input(db, contract, settings, initial)
    line_values, _taxes, tax_amount, total_amount, grand_total = sales_service._build_lines(db, payload)
    return {
        "contractId": int(contract["ContractId"]),
        "contractRefNo": contract["ContractRefNo"],
        "invoiceDate": payload.invoiceDate,
        "periodStart": period_start,
        "periodEnd": period_end,
        "nextInvoiceDate": next_invoice_date,
        "taxAmount": tax_amount,
        "totalAmount": total_amount,
        "grandTotal": grand_total,
        "narration": payload.narration,
        "lines": [{
            "itemTypeId": int(line["itemTypeId"]),
            "itemTypeName": line_names[int(line["itemTypeId"])],
            "vehicleId": int(line["vehicleId"]),
            "description": line["description"],
            "quantity": line["qty"],
            "unitId": int(line["unitId"]),
            "rate": line["rate"],
            "taxId": int(line["taxId"]),
            "taxAmount": line["taxAmount"],
            "amount": line["amount"],
        } for line in line_values],
    }, payload, next_invoice_date


def _validate_due(contract, as_of_date, initial):
    if initial:
        return
    if as_of_date < contract["NextInvStDate"]:
        raise HTTPException(422, "Contract is not due for its next Rental Invoice")


def preview_invoice(db, contract_id, settings, as_of_date=None):
    with database_errors(db):
        contract = repo.get_contract(db, contract_id)
        _require_contract(contract)
        _validate_due(contract, as_of_date or datetime.now(), initial=False)
        preview, _payload, _next = _preview(db, contract, settings, initial=False)
        return preview


def _create_invoice(db, contract_id, settings, user_id, initial, as_of_date=None):
    contract = repo.get_contract(db, contract_id, lock=True)
    _require_contract(contract)
    _validate_due(contract, as_of_date or datetime.now(), initial)
    preview, payload, next_invoice_date = _preview(db, contract, settings, initial)
    if repo.has_rental_invoice_for_schedule(db, contract_id, payload.invoiceDate):
        raise HTTPException(409, "A Rental Invoice already exists for this contract billing date")
    invoice = sales_service.create_draft_in_transaction(db, payload, user_id)
    repo.update_schedule(db, contract_id, next_invoice_date, payload.invoiceDate)
    return invoice, preview


def create_initial_invoice(db, contract_id, settings, user_id):
    """Called by contract creation; caller owns the surrounding transaction."""
    invoice, _preview_value = _create_invoice(db, contract_id, settings, user_id, initial=True)
    return invoice


def create_invoice(db, contract_id, settings, user_id, as_of_date=None):
    with database_errors(db):
        invoice, _preview_value = _create_invoice(db, contract_id, settings, user_id, initial=False, as_of_date=as_of_date)
        db.commit()
        return invoice


def list_due(db, as_of_date=None):
    with database_errors(db):
        as_of_date = as_of_date or datetime.now()
        return [{
            "contractId": int(row["ContractId"]),
            "contractRefNo": row["ContractRefNo"],
            "customerId": int(row["CustomerId"]) if row["CustomerId"] is not None else None,
            "customerName": row["CustomerName"],
            "contractType": int(row["ContractType"]),
            "paymentType": int(row["PaymentType"]),
            "billingType": row["BillingType"],
            "nextInvoiceDate": row["NextInvStDate"],
        } for row in repo.due_contracts(db, as_of_date, OPEN_CONTRACT_STATUS)]


def delete_invoice(db, contract_id, sales_master_id):
    with database_errors(db):
        contract = repo.get_contract(db, contract_id, lock=True)
        if contract is None:
            raise HTTPException(404, "Contract not found")
        invoice = sales_repo.get_invoice_header(db, sales_master_id)
        if invoice is None or int(invoice["voucherTypeId"] or 0) != repo.RENTAL_VOUCHER_TYPE_ID:
            raise HTTPException(404, "Rental Invoice draft not found")
        if int(invoice["contractId"] or 0) != contract_id:
            raise HTTPException(409, "Rental Invoice does not belong to this contract")
        if invoice["isPosted"] is True:
            raise HTTPException(409, "Posted Rental Invoices cannot be deleted")
        latest = repo.latest_rental_invoice(db, contract_id)
        if latest is None or int(latest["salesMasterId"]) != sales_master_id:
            raise HTTPException(409, "Only the latest Rental Invoice draft can be deleted")

        invoice_date = invoice["date"]
        if invoice_date is None:
            raise HTTPException(409, "Rental Invoice has no billing date")
        previous_invoice = repo.previous_rental_invoice(db, contract_id, sales_master_id)
        if previous_invoice is None and bool(contract["IsAdvanceInvoice"]):
            restored_last_date = None
        elif previous_invoice is None:
            restored_last_date = contract["ContractStartDate"]
        if previous_invoice is not None:
            restored_last_date = previous_invoice["date"]

        sales_repo.delete_draft(db, sales_master_id, invoice["voucherTypeId"], invoice["voucherNo"])
        repo.update_schedule(db, contract_id, invoice_date, restored_last_date)
        db.commit()
