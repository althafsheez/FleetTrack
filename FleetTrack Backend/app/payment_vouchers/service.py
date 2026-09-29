from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException

from app.master_data import database_errors
from . import repository as repo
from .schemas import PaymentVoucherInput


MONEY = Decimal("0.00001")
FOREX_LEDGER_ID = 12
DB_REFERENCE_TYPES = {
    "against": "Against",
    "new": "New",
    "on_account": "OnAccount",
}
API_REFERENCE_TYPES = {value: key for key, value in DB_REFERENCE_TYPES.items()}


@contextmanager
def _write_transaction(db):
    try:
        with database_errors(db):
            yield
    except HTTPException:
        db.rollback()
        raise


def _decimal(value) -> Decimal:
    return Decimal(value or 0)


def _round(value) -> Decimal:
    return _decimal(value).quantize(MONEY, rounding=ROUND_HALF_UP)


def _voucher_type(db, voucher_type_id):
    voucher = repo.get_voucher_type(db, voucher_type_id)
    if voucher is None:
        raise HTTPException(422, "voucherTypeId must be an active Payment Voucher type")
    return voucher


def _numbering(db, voucher, voucher_date):
    method = str(voucher["methodOfVoucherNumbering"] or "").strip()
    if method not in {"Automatic", "Manual"}:
        raise HTTPException(422, "Payment Voucher numbering method must be Automatic or Manual")
    return method, repo.get_suffix_prefix(db, int(voucher["voucherTypeId"]), voucher_date)


def _format_invoice_no(number: int, rule) -> str:
    if rule is None:
        return str(number)
    numerical = str(number)
    if rule["prefillWithZero"] and rule["widthOfNumericalPart"]:
        numerical = numerical.zfill(int(rule["widthOfNumericalPart"]))
    return f"{rule['prefix'] or ''}{numerical}{rule['suffix'] or ''}"


def _validate_period(db, voucher_date):
    financial_year = repo.get_financial_year(db, voucher_date)
    if financial_year is None:
        raise HTTPException(422, "voucherDate does not belong to a configured financial year")
    return financial_year


def _validate_payload(db, payload, existing=None, lock_references=False):
    voucher = _voucher_type(db, payload.voucherTypeId)
    financial_year = _validate_period(db, payload.voucherDate)
    method, rule = _numbering(db, voucher, payload.voucherDate)
    if method == "Automatic" and payload.manualVoucherNo is not None:
        raise HTTPException(422, "manualVoucherNo must be omitted for automatic numbering")
    if method == "Manual" and payload.manualVoucherNo is None:
        raise HTTPException(422, "manualVoucherNo is required for manual numbering")
    if existing is not None:
        if int(existing["voucherTypeId"]) != payload.voucherTypeId:
            raise HTTPException(422, "voucherTypeId cannot be changed after creation")
        if method == "Manual" and payload.manualVoucherNo != existing["invoiceNo"]:
            raise HTTPException(422, "manualVoucherNo cannot be changed after creation")
        if payload.idempotencyKey and payload.idempotencyKey != (existing["extra1"] or None):
            raise HTTPException(422, "idempotencyKey cannot be changed after creation")

    paying_account = repo.get_paying_account(db, payload.payingLedgerId)
    if paying_account is None:
        raise HTTPException(409, "payingLedgerId must be an eligible cash or bank ledger")

    source_cache = {}
    source_keys = sorted({
        (line.ledgerId, allocation.sourceVoucherTypeId, allocation.sourceVoucherNo)
        for line in payload.lines
        for allocation in line.allocations
        if allocation.referenceType == "against"
    })
    if lock_references:
        for ledger_id, source_type_id, source_no in source_keys:
            source_cache[(ledger_id, source_type_id, source_no)] = repo.lock_open_reference(
                db, ledger_id, source_type_id, source_no
            )
    else:
        for ledger_id in sorted({key[0] for key in source_keys}):
            for row in repo.list_open_references(db, ledger_id):
                source_cache[(
                    ledger_id, int(row["sourceVoucherTypeId"]), str(row["sourceVoucherNo"])
                )] = row

    validated_lines = []
    seen_references = set()
    for line in payload.lines:
        if line.ledgerId == payload.payingLedgerId:
            raise HTTPException(409, "A detail ledger cannot equal the paying ledger")
        account = repo.get_detail_account(db, line.ledgerId)
        if account is None:
            raise HTTPException(422, f"ledgerId {line.ledgerId} does not exist")
        exchange = repo.get_exchange_rate(db, line.exchangeRateId, payload.voucherDate)
        if exchange is None or _decimal(exchange["rate"]) <= 0:
            raise HTTPException(422, "exchangeRateId must be valid on voucherDate and have a positive rate")
        if line.vehicleId is not None and not repo.vehicle_exists(db, line.vehicleId):
            raise HTTPException(422, f"vehicleId {line.vehicleId} does not exist")

        is_party = bool(account["isParty"])
        if is_party and not line.allocations:
            raise HTTPException(422, "Bill-by-bill party lines require at least one allocation")
        if not is_party and line.allocations:
            raise HTTPException(422, "Allocations are allowed only for bill-by-bill party ledgers")

        validated_allocations = []
        nominal_total = Decimal("0")
        posting_base = Decimal("0")
        for allocation in line.allocations:
            reference_type = DB_REFERENCE_TYPES[allocation.referenceType]
            source = None
            allocation_rate = exchange
            if allocation.referenceType == "against":
                key = (line.ledgerId, allocation.sourceVoucherTypeId, allocation.sourceVoucherNo)
                if key in seen_references:
                    raise HTTPException(422, "An Against source reference can appear only once in a voucher")
                seen_references.add(key)
                source = source_cache.get(key)
                if source is None:
                    raise HTTPException(409, "The selected Against reference is no longer open")
                if _round(allocation.amount) > _round(source["pendingAmount"]):
                    raise HTTPException(409, "Allocation amount cannot exceed the current pending amount")
                if int(source["currencyId"] or 0) != int(exchange["currencyId"] or 0):
                    raise HTTPException(422, "All allocations on a party line must use the line currency")
                allocation_rate = source
            nominal_total += allocation.amount
            posting_base += allocation.amount * _decimal(allocation_rate["exchangeRate"] if source else exchange["rate"])
            validated_allocations.append({
                "input": allocation,
                "referenceType": reference_type,
                "source": source,
                "exchangeRateId": int(source["exchangeRateId"]) if source else line.exchangeRateId,
                "exchangeRate": _decimal(source["exchangeRate"]) if source else _decimal(exchange["rate"]),
                "contractId": int(source["contractId"] or 0) if source else 0,
            })

        if is_party and _round(nominal_total) != _round(line.amount):
            raise HTTPException(422, "Party line amount must equal the sum of its allocations")
        current_base = _round(line.amount * _decimal(exchange["rate"]))
        if current_base <= 0:
            raise HTTPException(422, "Converted line amount must be greater than zero")
        if not is_party:
            posting_base = current_base
        posting_base = _round(posting_base)
        validated_lines.append({
            "input": line,
            "account": account,
            "exchange": exchange,
            "baseAmount": current_base,
            "postingBaseAmount": posting_base,
            "forexDifference": _round(current_base - posting_base),
            "allocations": validated_allocations,
        })

    total = _round(sum((line["baseAmount"] for line in validated_lines), Decimal("0")))
    if total <= 0:
        raise HTTPException(422, "Payment Voucher total must be greater than zero")
    return voucher, financial_year, method, rule, paying_account, validated_lines, total


def _detail_values(master_id, line):
    item = line["input"]
    return {
        "paymentMasterId": master_id,
        "ledgerId": item.ledgerId,
        "amount": _round(item.amount),
        "exchangeRateId": item.exchangeRateId,
        "chequeNo": item.chequeNo,
        "chequeDate": item.chequeDate,
        "extraDate": None,
        "extra1": "",
        "extra2": "",
        "Vehicle": item.vehicleId or 0,
    }


def _allocation_values(allocation, line, payload, voucher_no, invoice_no, financial_year_id):
    item = allocation["input"]
    common = {
        "date": payload.voucherDate,
        "ledgerId": line["input"].ledgerId,
        "referenceType": allocation["referenceType"],
        "debit": _round(item.amount),
        "credit": Decimal("0"),
        "creditPeriod": 0,
        "exchangeRateId": allocation["exchangeRateId"],
        "financialYearId": financial_year_id,
        "extraDate": None,
        "extra1": "",
        "extra2": "",
        "contractId": allocation["contractId"],
    }
    source = allocation["source"]
    if allocation["referenceType"] == "Against":
        return {
            **common,
            "voucherTypeId": int(source["sourceVoucherTypeId"]),
            "voucherNo": str(source["sourceVoucherNo"]),
            "invoiceNo": str(source["sourceInvoiceNo"] or source["sourceVoucherNo"]),
            "againstVoucherTypeId": payload.voucherTypeId,
            "againstVoucherNo": voucher_no,
            "againstInvoiceNo": invoice_no,
        }
    return {
        **common,
        "voucherTypeId": payload.voucherTypeId,
        "voucherNo": voucher_no,
        "invoiceNo": invoice_no,
        "againstVoucherTypeId": 0,
        "againstVoucherNo": "0",
        "againstInvoiceNo": "0",
    }


def _posting_values(master, ledger_id, debit, credit, details_id, cheque_no=None, cheque_date=None):
    return {
        "date": master["date"],
        "voucherTypeId": int(master["voucherTypeId"]),
        "voucherNo": str(master["voucherNo"]),
        "ledgerId": ledger_id,
        "debit": _round(debit),
        "credit": _round(credit),
        "detailsId": details_id,
        "yearId": int(master["financialYearId"]),
        "invoiceNo": str(master["invoiceNo"]),
        "chequeNo": cheque_no,
        "chequeDate": cheque_date,
        "extraDate": None,
        "extra1": "",
        "extra2": "",
    }


def _allocation_response(row):
    reference_type = API_REFERENCE_TYPES.get(row["referenceType"], "on_account")
    against = reference_type == "against"
    return {
        "partyBalanceId": int(row["partyBalanceId"]),
        "referenceType": reference_type,
        "sourceVoucherTypeId": int(row["voucherTypeId"]) if against else None,
        "sourceVoucherTypeName": row["sourceVoucherTypeName"] if against else None,
        "sourceVoucherNo": str(row["voucherNo"]) if against else None,
        "sourceInvoiceNo": str(row["invoiceNo"]) if against and row["invoiceNo"] is not None else None,
        "amount": _decimal(row["debit"]),
        "exchangeRateId": int(row["exchangeRateId"]),
        "exchangeRate": _decimal(row["exchangeRate"]),
        "currencyId": int(row["currencyId"]) if row["currencyId"] is not None else None,
        "contractId": int(row["contractId"]) if row["contractId"] not in (None, 0) else None,
    }


def _response(db, master):
    if master is None:
        raise HTTPException(404, "Payment Voucher not found")
    posted = bool(master["isPosted"])
    allocation_rows = repo.get_allocations(
        db, int(master["voucherTypeId"]), str(master["voucherNo"]), posted
    )
    allocations_by_ledger = defaultdict(list)
    for row in allocation_rows:
        allocations_by_ledger[int(row["ledgerId"])].append(_allocation_response(row))
    lines = []
    for row in repo.get_details(db, int(master["paymentMasterId"])):
        rate = _decimal(row["exchangeRate"])
        ledger_id = int(row["ledgerId"])
        lines.append({
            "paymentDetailsId": int(row["paymentDetailsId"]),
            "ledgerId": ledger_id,
            "ledgerName": row["ledgerName"],
            "amount": _decimal(row["amount"]),
            "exchangeRateId": int(row["exchangeRateId"]),
            "exchangeRate": rate,
            "currencyId": int(row["currencyId"]) if row["currencyId"] is not None else None,
            "currencyName": row["currencyName"],
            "currencySymbol": row["currencySymbol"],
            "baseAmount": _round(_decimal(row["amount"]) * rate),
            "chequeNo": row["chequeNo"] or None,
            "chequeDate": row["chequeDate"],
            "vehicleId": int(row["Vehicle"]) if row["Vehicle"] not in (None, 0) else None,
            "vehicleNo": row["vehicleNo"],
            "billByBill": bool(row["billByBill"]),
            "allocations": allocations_by_ledger[ledger_id],
        })
    return {
        "paymentMasterId": int(master["paymentMasterId"]),
        "voucherNo": str(master["voucherNo"]),
        "invoiceNo": str(master["invoiceNo"]),
        "voucherTypeId": int(master["voucherTypeId"]),
        "voucherTypeName": master["voucherTypeName"],
        "suffixPrefixId": int(master["suffixPrefixId"] or 0),
        "voucherDate": master["date"],
        "payingLedgerId": int(master["ledgerId"]),
        "payingLedgerName": master["payingLedgerName"],
        "totalAmount": _decimal(master["totalAmount"]),
        "narration": master["narration"],
        "idempotencyKey": master["extra1"] or None,
        "userId": int(master["userId"] or 0),
        "financialYearId": int(master["financialYearId"]),
        "isPosted": posted,
        "lines": lines,
    }


def get_voucher(db, payment_master_id):
    with database_errors(db):
        return _response(db, repo.get_master(db, payment_master_id))


def list_vouchers(db, from_date=None, to_date=None, voucher_no=None, voucher_type_id=None,
                  paying_ledger_id=None, amount=None, party_ledger_id=None,
                  cheque_no=None, posted=None, offset=0, limit=10):
    if from_date is not None and to_date is not None and from_date > to_date:
        raise HTTPException(422, "fromDate cannot be after toDate")
    from_bound = (
        datetime.combine(from_date.date(), time.min)
        if from_date is not None else None
    )
    to_bound = (
        datetime.combine(to_date.date() + timedelta(days=1), time.min)
        if to_date is not None else None
    )
    voucher_no = voucher_no.strip() if voucher_no and voucher_no.strip() else None
    cheque_no = cheque_no.strip() if cheque_no and cheque_no.strip() else None
    with database_errors(db):
        rows, total = repo.list_vouchers(
            db, from_bound, to_bound, voucher_no, voucher_type_id,
            paying_ledger_id, amount, party_ledger_id, cheque_no,
            posted, offset, limit,
        )
        return {
            "items": [{
                "paymentMasterId": int(row["paymentMasterId"]),
                "voucherNo": str(row["voucherNo"]),
                "invoiceNo": str(row["invoiceNo"]),
                "voucherTypeId": int(row["voucherTypeId"]),
                "voucherTypeName": row["voucherTypeName"],
                "voucherDate": row["voucherDate"],
                "payingLedgerId": int(row["payingLedgerId"]),
                "payingLedgerName": row["payingLedgerName"],
                "totalAmount": _decimal(row["totalAmount"]),
                "narration": row["narration"],
                "isPosted": bool(row["isPosted"]),
                "detailAccountNames": row["detailAccountNames"],
                "lineCount": int(row["lineCount"]),
            } for row in rows],
            "total": total, "offset": offset, "limit": limit,
        }


def _save_allocations(db, payload, lines, voucher_no, invoice_no, financial_year_id,
                      existing_rows=None):
    existing_rows = existing_rows or []
    existing_by_id = {int(row["partyBalanceId"]): row for row in existing_rows}
    submitted_ids = {
        int(allocation["input"].partyBalanceId)
        for line in lines for allocation in line["allocations"]
        if allocation["input"].partyBalanceId is not None
    }
    if not submitted_ids.issubset(existing_by_id):
        raise HTTPException(404, "A partyBalanceId does not belong to this Payment Voucher draft")
    removed_ids = set(existing_by_id) - submitted_ids
    repo.delete_draft_allocations(db, payload.voucherTypeId, voucher_no, removed_ids)
    for line in lines:
        for allocation in line["allocations"]:
            values = _allocation_values(
                allocation, line, payload, voucher_no, invoice_no, financial_year_id
            )
            allocation_id = allocation["input"].partyBalanceId
            if allocation_id is None:
                repo.insert_draft_allocation(db, values)
            else:
                old = existing_by_id[int(allocation_id)]
                if int(old["ledgerId"]) != line["input"].ledgerId:
                    raise HTTPException(409, "partyBalanceId belongs to a different detail ledger")
                if repo.update_draft_allocation(db, allocation_id, values) != 1:
                    raise HTTPException(409, "Payment allocation changed during update")


def create_voucher(db, payload, user_id):
    with _write_transaction(db):
        voucher, financial_year, method, rule, _, lines, total = _validate_payload(db, payload)
        voucher_type_id = int(voucher["voucherTypeId"])
        repo.lock_numbering_scope(db, voucher_type_id)
        if payload.idempotencyKey:
            retry = repo.get_master_by_idempotency_key(db, voucher_type_id, payload.idempotencyKey)
            if retry is not None:
                return _response(db, retry)
        start_index = int(rule["startIndex"] or 1) if rule is not None else 1
        internal_number = repo.next_internal_voucher_number(db, voucher_type_id, start_index)
        voucher_no = str(internal_number)
        invoice_no = payload.manualVoucherNo if method == "Manual" else _format_invoice_no(internal_number, rule)
        if repo.voucher_number_exists(db, voucher_type_id, invoice_no):
            raise HTTPException(409, "Payment Voucher number already exists")
        financial_year_id = int(financial_year["financialYearId"])
        master_id = repo.insert_master(db, {
            "voucherNo": voucher_no,
            "invoiceNo": invoice_no,
            "suffixPrefixId": int(rule["suffixprefixId"]) if rule is not None else 0,
            "date": payload.voucherDate,
            "ledgerId": payload.payingLedgerId,
            "totalAmount": total,
            "narration": payload.narration,
            "voucherTypeId": voucher_type_id,
            "userId": user_id,
            "financialYearId": financial_year_id,
            "extraDate": None,
            "extra1": payload.idempotencyKey or "",
            "extra2": "",
            "isPosted": False,
        })
        for line in lines:
            repo.insert_detail(db, _detail_values(master_id, line))
        _save_allocations(db, payload, lines, voucher_no, invoice_no, financial_year_id)
        db.commit()
        return _response(db, repo.get_master(db, master_id))


def update_voucher(db, payment_master_id, payload, user_id):
    with _write_transaction(db):
        existing = repo.get_master(db, payment_master_id, for_update=True)
        if existing is None:
            raise HTTPException(404, "Payment Voucher not found")
        if bool(existing["isPosted"]):
            raise HTTPException(409, "Posted Payment Vouchers cannot be edited; unpost first")
        voucher_type_id = int(existing["voucherTypeId"])
        voucher_no = str(existing["voucherNo"])
        if int(repo.posting_totals(db, voucher_type_id, voucher_no)["rowCount"]) != 0:
            raise HTTPException(409, "Unposted Payment Voucher unexpectedly has ledger postings")
        if repo.get_allocations(db, voucher_type_id, voucher_no, True):
            raise HTTPException(409, "Unposted Payment Voucher unexpectedly has active allocations")
        _, financial_year, _, rule, _, lines, total = _validate_payload(db, payload, existing)
        old_details = repo.get_details(db, payment_master_id)
        old_ids = {int(row["paymentDetailsId"]) for row in old_details}
        submitted_ids = {
            int(line["input"].paymentDetailsId)
            for line in lines if line["input"].paymentDetailsId is not None
        }
        if not submitted_ids.issubset(old_ids):
            raise HTTPException(404, "A paymentDetailsId does not belong to this Payment Voucher")
        repo.delete_details(db, payment_master_id, old_ids - submitted_ids)
        for line in lines:
            detail_id = line["input"].paymentDetailsId
            if detail_id is None:
                repo.insert_detail(db, _detail_values(payment_master_id, line))
            elif repo.update_detail(
                db, detail_id, payment_master_id, _detail_values(payment_master_id, line)
            ) != 1:
                raise HTTPException(409, "Payment Voucher detail changed during update")
        invoice_no = str(existing["invoiceNo"])
        old_allocations = repo.get_allocations(db, payload.voucherTypeId, voucher_no, False)
        financial_year_id = int(financial_year["financialYearId"])
        _save_allocations(
            db, payload, lines, voucher_no, invoice_no, financial_year_id, old_allocations
        )
        if repo.update_master(db, payment_master_id, {
            "suffixPrefixId": int(rule["suffixprefixId"]) if rule is not None else 0,
            "date": payload.voucherDate,
            "ledgerId": payload.payingLedgerId,
            "totalAmount": total,
            "narration": payload.narration,
            "userId": user_id,
            "financialYearId": financial_year_id,
        }) != 1:
            raise HTTPException(409, "Payment Voucher changed during update")
        db.commit()
        return _response(db, repo.get_master(db, payment_master_id))


def post_voucher(db, payment_master_id):
    with _write_transaction(db):
        master = repo.get_master(db, payment_master_id, for_update=True)
        if master is None:
            raise HTTPException(404, "Payment Voucher not found")
        voucher_type_id = int(master["voucherTypeId"])
        voucher_no = str(master["voucherNo"])
        if bool(master["isPosted"]):
            totals = repo.posting_totals(db, voucher_type_id, voucher_no)
            if int(totals["rowCount"]) > 0 and _round(totals["debit"]) == _round(totals["credit"]):
                return _response(db, master)
            raise HTTPException(409, "Payment Voucher is marked posted but its ledger postings are incomplete")
        if int(repo.posting_totals(db, voucher_type_id, voucher_no)["rowCount"]) != 0:
            raise HTTPException(409, "Unposted Payment Voucher already has ledger postings")
        if repo.get_allocations(db, voucher_type_id, voucher_no, True):
            raise HTTPException(409, "Unposted Payment Voucher already has active party allocations")

        response = _response(db, master)
        method = str(_voucher_type(db, voucher_type_id)["methodOfVoucherNumbering"] or "").strip()
        payload_data = {
            **response,
            "manualVoucherNo": response["invoiceNo"] if method == "Manual" else None,
        }
        payload = PaymentVoucherInput.model_validate({
            "voucherTypeId": payload_data["voucherTypeId"],
            "voucherDate": payload_data["voucherDate"],
            "payingLedgerId": payload_data["payingLedgerId"],
            "manualVoucherNo": payload_data["manualVoucherNo"],
            "narration": payload_data["narration"],
            "idempotencyKey": payload_data["idempotencyKey"],
            "lines": [{
                "paymentDetailsId": line["paymentDetailsId"],
                "ledgerId": line["ledgerId"],
                "amount": line["amount"],
                "exchangeRateId": line["exchangeRateId"],
                "chequeNo": line["chequeNo"],
                "chequeDate": line["chequeDate"],
                "vehicleId": line["vehicleId"],
                "allocations": [{
                    "partyBalanceId": allocation["partyBalanceId"],
                    "referenceType": allocation["referenceType"],
                    "sourceVoucherTypeId": allocation["sourceVoucherTypeId"],
                    "sourceVoucherNo": allocation["sourceVoucherNo"],
                    "amount": allocation["amount"],
                } for allocation in line["allocations"]],
            } for line in response["lines"]],
        })
        _, _, _, _, _, lines, total = _validate_payload(
            db, payload, master, lock_references=True
        )
        master_values = dict(master)
        repo.insert_posting(db, _posting_values(
            master_values, payload.payingLedgerId, Decimal("0"), total, 0
        ))
        financial_year_id = int(master["financialYearId"])
        for line in lines:
            item = line["input"]
            repo.insert_posting(db, _posting_values(
                master_values, item.ledgerId, line["postingBaseAmount"], Decimal("0"),
                item.paymentDetailsId, item.chequeNo, item.chequeDate,
            ))
            difference = line["forexDifference"]
            if difference != 0:
                if repo.get_detail_account(db, FOREX_LEDGER_ID) is None:
                    raise HTTPException(409, "Forex Gain/Loss ledger is not configured")
                repo.insert_posting(db, _posting_values(
                    master_values, FOREX_LEDGER_ID,
                    difference if difference > 0 else Decimal("0"),
                    -difference if difference < 0 else Decimal("0"),
                    item.paymentDetailsId,
                ))
            for allocation in line["allocations"]:
                repo.insert_active_allocation(db, _allocation_values(
                    allocation, line, payload, voucher_no,
                    str(master["invoiceNo"]), financial_year_id,
                ))
        totals = repo.posting_totals(db, voucher_type_id, voucher_no)
        if int(totals["rowCount"]) < len(lines) + 1 or _round(totals["debit"]) != _round(totals["credit"]):
            raise HTTPException(409, "Payment Voucher ledger postings are not balanced")
        if repo.update_master(db, payment_master_id, {"isPosted": True}) != 1:
            raise HTTPException(409, "Payment Voucher changed during posting")
        db.commit()
        return _response(db, repo.get_master(db, payment_master_id))


def unpost_voucher(db, payment_master_id):
    with _write_transaction(db):
        master = repo.get_master(db, payment_master_id, for_update=True)
        if master is None:
            raise HTTPException(404, "Payment Voucher not found")
        if not bool(master["isPosted"]):
            return _response(db, master)
        voucher_type_id = int(master["voucherTypeId"])
        voucher_no = str(master["voucherNo"])
        if repo.has_external_party_reference(db, voucher_type_id, voucher_no):
            raise HTTPException(409, "Payment Voucher is referenced by a later party allocation")
        if repo.has_bank_reconciliation(db, voucher_type_id, voucher_no):
            raise HTTPException(409, "A reconciled Payment Voucher cannot be unposted")
        draft_rows = repo.get_allocations(db, voucher_type_id, voucher_no, False)
        active_rows = repo.get_allocations(db, voucher_type_id, voucher_no, True)
        if active_rows and not draft_rows:
            allowed = {
                "date", "ledgerId", "voucherTypeId", "voucherNo", "againstVoucherTypeId",
                "againstVoucherNo", "invoiceNo", "againstInvoiceNo", "referenceType",
                "debit", "credit", "creditPeriod", "exchangeRateId", "financialYearId",
                "extraDate", "extra1", "extra2", "contractId",
            }
            for row in active_rows:
                repo.insert_draft_allocation(db, {key: row[key] for key in allowed})
        repo.delete_active_allocations(db, voucher_type_id, voucher_no)
        repo.delete_postings(db, voucher_type_id, voucher_no)
        if repo.update_master(db, payment_master_id, {"isPosted": False}) != 1:
            raise HTTPException(409, "Payment Voucher changed during unposting")
        db.commit()
        return _response(db, repo.get_master(db, payment_master_id))


def delete_voucher(db, payment_master_id):
    with _write_transaction(db):
        master = repo.get_master(db, payment_master_id, for_update=True)
        if master is None:
            raise HTTPException(404, "Payment Voucher not found")
        if bool(master["isPosted"]):
            raise HTTPException(409, "Posted Payment Vouchers cannot be deleted; unpost first")
        voucher_type_id = int(master["voucherTypeId"])
        voucher_no = str(master["voucherNo"])
        if int(repo.posting_totals(db, voucher_type_id, voucher_no)["rowCount"]) != 0:
            raise HTTPException(409, "Unposted Payment Voucher unexpectedly has ledger postings")
        if repo.get_allocations(db, voucher_type_id, voucher_no, True):
            raise HTTPException(409, "Unposted Payment Voucher unexpectedly has active allocations")
        if repo.has_external_party_reference(db, voucher_type_id, voucher_no):
            raise HTTPException(409, "Payment Voucher is referenced by a later party allocation")
        if repo.has_bank_reconciliation(db, voucher_type_id, voucher_no):
            raise HTTPException(409, "A reconciled Payment Voucher cannot be deleted")
        repo.delete_draft_allocations(db, voucher_type_id, voucher_no)
        repo.delete_details(db, payment_master_id)
        if repo.delete_master(db, payment_master_id) != 1:
            raise HTTPException(409, "Payment Voucher changed during deletion")
        db.commit()


def voucher_types(db):
    with database_errors(db):
        return [{
            "id": int(row["voucherTypeId"]), "name": row["voucherTypeName"],
            "numberingMethod": row["methodOfVoucherNumbering"],
        } for row in repo.list_voucher_types(db)]


def paying_accounts(db):
    with database_errors(db):
        return [{
            "id": int(row["ledgerId"]), "name": row["ledgerName"],
            "accountGroupId": int(row["accountGroupId"]) if row["accountGroupId"] is not None else None,
            "accountGroupName": row["accountGroupName"],
        } for row in repo.list_paying_accounts(db)]


def detail_accounts(db, search=None, limit=100):
    with database_errors(db):
        return [{
            "id": int(row["ledgerId"]), "name": row["ledgerName"],
            "accountGroupId": int(row["accountGroupId"]) if row["accountGroupId"] is not None else None,
            "accountGroupName": row["accountGroupName"],
            "billByBill": bool(row["isParty"]),
        } for row in repo.list_detail_accounts(db, search, limit)]


def party_ledgers(db, search=None, limit=100):
    with database_errors(db):
        return [{
            "id": int(row["ledgerId"]), "name": row["ledgerName"],
            "accountGroupId": int(row["accountGroupId"]) if row["accountGroupId"] is not None else None,
            "accountGroupName": row["accountGroupName"],
            "billByBill": True,
        } for row in repo.list_party_ledgers(db, search, limit)]


def exchange_rates(db, voucher_date):
    with database_errors(db):
        return [{
            "id": int(row["exchangeRateId"]), "currencyId": int(row["currencyId"]),
            "currencyName": row["currencyName"], "currencySymbol": row["currencySymbol"],
            "rate": _decimal(row["rate"]), "date": row["date"],
        } for row in repo.list_exchange_rates(db, voucher_date)]


def vehicles(db, search=None, limit=100):
    with database_errors(db):
        return [{"id": int(row["VehicleId"]), "plateNo": row["PlateNo"]}
                for row in repo.list_vehicles(db, search, limit)]


def open_references(db, ledger_id):
    with database_errors(db):
        account = repo.get_detail_account(db, ledger_id)
        if account is None or not bool(account["isParty"]):
            raise HTTPException(422, "ledgerId must be a bill-by-bill party ledger")
        return [{
            "ledgerId": int(row["ledgerId"]),
            "sourceVoucherTypeId": int(row["sourceVoucherTypeId"]),
            "sourceVoucherTypeName": row["sourceVoucherTypeName"],
            "sourceVoucherNo": str(row["sourceVoucherNo"]),
            "sourceInvoiceNo": str(row["sourceInvoiceNo"]) if row["sourceInvoiceNo"] is not None else None,
            "pendingAmount": _decimal(row["pendingAmount"]),
            "exchangeRateId": int(row["exchangeRateId"]),
            "exchangeRate": _decimal(row["exchangeRate"]),
            "currencyId": int(row["currencyId"]) if row["currencyId"] is not None else None,
            "currencyName": row["currencyName"], "currencySymbol": row["currencySymbol"],
            "contractId": int(row["contractId"]) if row["contractId"] not in (None, 0) else None,
        } for row in repo.list_open_references(db, ledger_id)]


def numbering_rule(db, voucher_type_id, voucher_date):
    with database_errors(db):
        voucher = _voucher_type(db, voucher_type_id)
        method, rule = _numbering(db, voucher, voucher_date)
        next_voucher_no = next_invoice_no = None
        if method == "Automatic":
            number = repo.next_internal_voucher_number(
                db, voucher_type_id, int(rule["startIndex"] or 1) if rule is not None else 1
            )
            next_voucher_no = str(number)
            next_invoice_no = _format_invoice_no(number, rule)
        return {
            "voucherTypeId": voucher_type_id, "numberingMethod": method,
            "automatic": method == "Automatic",
            "suffixPrefixId": int(rule["suffixprefixId"]) if rule is not None else 0,
            "prefix": rule["prefix"] if rule is not None else None,
            "suffix": rule["suffix"] if rule is not None else None,
            "startIndex": int(rule["startIndex"]) if rule is not None and rule["startIndex"] is not None else None,
            "widthOfNumericalPart": rule["widthOfNumericalPart"] if rule is not None else None,
            "prefillWithZero": rule["prefillWithZero"] if rule is not None else None,
            "nextVoucherNo": next_voucher_no, "nextInvoiceNo": next_invoice_no,
            "fromDate": rule["fromDate"] if rule is not None else None,
            "toDate": rule["toDate"] if rule is not None else None,
        }
