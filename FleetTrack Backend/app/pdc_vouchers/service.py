from contextlib import contextmanager
from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException

from app.master_data import database_errors
from . import repository as repo


MONEY = Decimal("0.00001")


def money(value):
    return Decimal(value or 0).quantize(MONEY, rounding=ROUND_HALF_UP)


@contextmanager
def write_transaction(db):
    try:
        with database_errors(db):
            yield
    except HTTPException:
        db.rollback()
        raise


def _format_number(number, rule):
    if rule is None:
        return str(number)
    value = str(number)
    if rule["prefillWithZero"] and rule["widthOfNumericalPart"]:
        value = value.zfill(int(rule["widthOfNumericalPart"]))
    return f"{rule['prefix'] or ''}{value}{rule['suffix'] or ''}"


def _configuration(db, kind, value):
    voucher = repo.voucher_type(db, kind)
    if voucher is None:
        raise HTTPException(422, f"Active PDC {kind.title()} voucher type is not configured")
    year = repo.financial_year(db, value)
    if year is None:
        raise HTTPException(422, "voucherDate does not belong to a configured financial year")
    method = str(voucher["methodOfVoucherNumbering"] or "").strip()
    if method not in {"Automatic", "Manual"}:
        raise HTTPException(422, "PDC numbering must be Automatic or Manual")
    return voucher, year, method, repo.suffix_rule(db, int(voucher["voucherTypeId"]), value)


def _validate_accounts(db, kind, payload):
    control = repo.account(db, payload.controlLedgerId)
    bank = repo.account(db, payload.bankLedgerId)
    party = repo.account(db, payload.partyLedgerId)
    if control is None:
        raise HTTPException(422, "controlLedgerId does not exist")
    if bank is None or str(bank["accountGroupName"] or "").lower() not in {"bank account", "bank od a/c"}:
        raise HTTPException(422, "bankLedgerId must be an eligible bank account")
    if payload.controlLedgerId == payload.bankLedgerId:
        raise HTTPException(422, "PDC control and bank ledgers must be different")
    if party is None:
        raise HTTPException(422, "partyLedgerId does not exist")
    if payload.partyLedgerId in {payload.controlLedgerId, payload.bankLedgerId}:
        raise HTTPException(422, "Party, account ledger and bank ledgers must be different")


def _validated_allocations(db, kind, payload, voucher_type_id=None, voucher_no=None):
    _validate_accounts(db, kind, payload)
    result = []
    for item in payload.allocations:
        if item.ledgerId != payload.partyLedgerId:
            raise HTTPException(422, "Every Against reference must belong to the selected Account Ledger")
        source = repo.lock_open_reference(db, item.ledgerId, kind, item.sourceVoucherTypeId, item.sourceVoucherNo)
        if source is None:
            raise HTTPException(409, "The selected Against reference is no longer open")
        if money(item.amount) > money(source["pendingAmount"]):
            raise HTTPException(409, "Allocation amount exceeds the current pending amount")
        result.append((item, source))
    if not result:
        raise HTTPException(422, "Select at least one Against reference")
    if money(sum((item.amount for item, _ in result), Decimal("0"))) != money(payload.amount):
        raise HTTPException(422, "Allocation total must equal the PDC amount")
    return result


def _allocation_values(master, item, source, kind):
    return {
        "date": master["date"], "ledgerId": item.ledgerId,
        "voucherTypeId": int(source["sourceVoucherTypeId"]),
        "voucherNo": str(source["sourceVoucherNo"]),
        "invoiceNo": str(source["sourceInvoiceNo"] or source["sourceVoucherNo"]),
        "againstVoucherTypeId": int(master["voucherTypeId"]),
        "againstVoucherNo": str(master["voucherNo"]),
        "againstInvoiceNo": str(master["invoiceNo"]),
        "referenceType": "Against",
        "debit": money(item.amount) if kind == "payable" else Decimal("0"),
        "credit": money(item.amount) if kind == "receivable" else Decimal("0"),
        "creditPeriod": 0, "exchangeRateId": source["exchangeRateId"],
        "financialYearId": master["financialYearId"], "extraDate": None,
        "extra1": "", "extra2": "", "contractId": 0,
    }


def _save_allocations(db, master, allocations, kind):
    for item, source in allocations:
        repo.insert_allocation(db, _allocation_values(master, item, source, kind))


def _posting(master, ledger_id, debit, credit, cheque=False):
    return {
        "date": master["date"], "voucherTypeId": master["voucherTypeId"],
        "voucherNo": str(master["voucherNo"]), "ledgerId": ledger_id,
        "debit": money(debit), "credit": money(credit), "detailsId": 0,
        "yearId": master["financialYearId"], "invoiceNo": str(master["invoiceNo"]),
        "chequeNo": master["chequeNo"] if cheque else None,
        "chequeDate": master["chequeDate"] if cheque else None,
        "extraDate": None, "extra1": "", "extra2": "",
    }


def _save_effects(db, kind, master, party_ledger_id):
    amount = money(master["amount"])
    repo.insert_posting(db, _posting(
        master, party_ledger_id,
        amount if kind == "payable" else 0,
        amount if kind == "receivable" else 0,
    ))
    repo.insert_posting(db, _posting(
        master, master["ledgerId"], 0 if kind == "payable" else amount,
        amount if kind == "payable" else 0,
    ))
    totals = repo.posting_totals(db, int(master["voucherTypeId"]), str(master["voucherNo"]))
    if money(totals["debit"]) != money(totals["credit"]):
        raise HTTPException(409, "PDC ledger postings are not balanced")


def _allocation_response(row):
    return {
        "ledgerId": int(row["ledgerId"]), "ledgerName": row["ledgerName"],
        "sourceVoucherTypeId": int(row["voucherTypeId"]),
        "sourceVoucherTypeName": row["sourceVoucherTypeName"],
        "sourceVoucherNo": str(row["voucherNo"]),
        "sourceInvoiceNo": str(row["invoiceNo"]) if row["invoiceNo"] is not None else None,
        "amount": money(row["debit"] if money(row["debit"]) else row["credit"]),
    }


def response(db, kind, master):
    if master is None:
        raise HTTPException(404, f"PDC {kind.title()} not found")
    master_id = int(master[repo.id_column(kind).name])
    clearance = repo.clearance_for_source(db, kind, master_id)
    return {
        "id": master_id, "sourceType": kind, "voucherNo": str(master["voucherNo"]),
        "invoiceNo": str(master["invoiceNo"]), "voucherTypeId": int(master["voucherTypeId"]),
        "voucherTypeName": master["voucherTypeName"], "voucherDate": master["date"],
        "controlLedgerId": int(master["ledgerId"]), "controlLedgerName": master["controlLedgerName"],
        "partyLedgerId": int(master["partyLedgerId"]) if master["partyLedgerId"] is not None else None,
        "partyLedgerName": master["partyLedgerName"],
        "bankLedgerId": int(master["bankId"]), "bankLedgerName": master["bankLedgerName"],
        "amount": money(master["amount"]), "chequeNo": str(master["chequeNo"]),
        "chequeDate": master["chequeDate"], "narration": master["narration"],
        "status": clearance["status"] if clearance else "Pending",
        "financialYearId": int(master["financialYearId"]),
        "idempotencyKey": master["extra1"] or None,
        "allocations": [_allocation_response(row) for row in repo.allocations(
            db, int(master["voucherTypeId"]), str(master["voucherNo"])
        )],
    }


def create_voucher(db, kind, payload, user_id):
    with write_transaction(db):
        voucher, year, method, rule = _configuration(db, kind, payload.voucherDate)
        if method == "Automatic" and payload.manualVoucherNo:
            raise HTTPException(422, "manualVoucherNo must be omitted for automatic numbering")
        if method == "Manual" and not payload.manualVoucherNo:
            raise HTTPException(422, "manualVoucherNo is required for manual numbering")
        voucher_type_id = int(voucher["voucherTypeId"])
        repo.lock_numbering(db, voucher_type_id)
        retry = repo.get_master_by_key(db, kind, voucher_type_id, payload.idempotencyKey)
        if retry is not None:
            return response(db, kind, retry)
        allocations = _validated_allocations(db, kind, payload)
        if repo.cheque_exists(db, kind, payload.bankLedgerId, payload.chequeNo):
            raise HTTPException(409, "Cheque number already exists for this bank")
        number = repo.next_number(db, repo.master_table(kind), voucher_type_id)
        invoice_no = payload.manualVoucherNo if method == "Manual" else _format_number(number, rule)
        if repo.invoice_exists(db, repo.master_table(kind), voucher_type_id, invoice_no):
            raise HTTPException(409, "PDC voucher number already exists")
        master_id = repo.insert_master(db, kind, {
            "voucherNo": str(number), "invoiceNo": invoice_no,
            "suffixPrefixId": int(rule["suffixprefixId"]) if rule else 0,
            "date": payload.voucherDate, "ledgerId": payload.controlLedgerId,
            "amount": money(payload.amount), "chequeNo": payload.chequeNo,
            "chequeDate": payload.chequeDate, "narration": payload.narration,
            "userId": user_id, "bankId": payload.bankLedgerId,
            "voucherTypeId": voucher_type_id, "financialYearId": int(year["financialYearId"]),
            "extraDate": None, "extra1": payload.idempotencyKey or "", "extra2": "",
        })
        master = repo.get_master(db, kind, master_id)
        _save_effects(db, kind, master, payload.partyLedgerId)
        _save_allocations(db, master, allocations, kind)
        db.commit()
        return response(db, kind, repo.get_master(db, kind, master_id))


def update_voucher(db, kind, master_id, payload, user_id):
    with write_transaction(db):
        existing = repo.get_master(db, kind, master_id, for_update=True)
        if existing is None: raise HTTPException(404, f"PDC {kind.title()} not found")
        if repo.clearance_for_source(db, kind, master_id):
            raise HTTPException(409, "A cleared or bounced PDC cannot be edited")
        if repo.has_reconciliation(db, int(existing["voucherTypeId"]), str(existing["voucherNo"])):
            raise HTTPException(409, "A reconciled PDC cannot be edited")
        voucher, year, method, rule = _configuration(db, kind, payload.voucherDate)
        if int(voucher["voucherTypeId"]) != int(existing["voucherTypeId"]):
            raise HTTPException(409, "PDC voucher type changed unexpectedly")
        if method == "Manual" and payload.manualVoucherNo != existing["invoiceNo"]:
            raise HTTPException(422, "manualVoucherNo cannot be changed after creation")
        repo.delete_postings(db, int(existing["voucherTypeId"]), str(existing["voucherNo"]))
        repo.delete_allocations(db, int(existing["voucherTypeId"]), str(existing["voucherNo"]))
        allocations = _validated_allocations(db, kind, payload)
        if repo.cheque_exists(db, kind, payload.bankLedgerId, payload.chequeNo, master_id):
            raise HTTPException(409, "Cheque number already exists for this bank")
        if repo.update_master(db, kind, master_id, {
            "suffixPrefixId": int(rule["suffixprefixId"]) if rule else 0,
            "date": payload.voucherDate, "ledgerId": payload.controlLedgerId,
            "amount": money(payload.amount), "chequeNo": payload.chequeNo,
            "chequeDate": payload.chequeDate, "narration": payload.narration,
            "userId": user_id, "bankId": payload.bankLedgerId,
            "financialYearId": int(year["financialYearId"]),
        }) != 1: raise HTTPException(409, "PDC changed during update")
        master = repo.get_master(db, kind, master_id)
        _save_effects(db, kind, master, payload.partyLedgerId)
        _save_allocations(db, master, allocations, kind)
        db.commit()
        return response(db, kind, repo.get_master(db, kind, master_id))


def delete_voucher(db, kind, master_id):
    with write_transaction(db):
        master = repo.get_master(db, kind, master_id, for_update=True)
        if master is None: raise HTTPException(404, f"PDC {kind.title()} not found")
        if repo.clearance_for_source(db, kind, master_id):
            raise HTTPException(409, "Delete the PDC clearance record before deleting this PDC")
        voucher_type_id, voucher_no = int(master["voucherTypeId"]), str(master["voucherNo"])
        if repo.has_reconciliation(db, voucher_type_id, voucher_no):
            raise HTTPException(409, "A reconciled PDC cannot be deleted")
        repo.delete_postings(db, voucher_type_id, voucher_no)
        repo.delete_allocations(db, voucher_type_id, voucher_no)
        if repo.delete_master(db, kind, master_id) != 1:
            raise HTTPException(409, "PDC changed during deletion")
        db.commit()


def get_voucher(db, kind, master_id):
    with database_errors(db): return response(db, kind, repo.get_master(db, kind, master_id))


def list_vouchers(db, kind, from_date=None, to_date=None, **kwargs):
    if from_date is not None and to_date is not None and from_date > to_date:
        raise HTTPException(422, "fromDate cannot be after toDate")
    from_bound = datetime.combine(from_date, time.min) if from_date else None
    to_bound = datetime.combine(to_date + timedelta(days=1), time.min) if to_date else None
    with database_errors(db):
        rows, total = repo.list_masters(db, kind, from_bound, to_bound, **kwargs)
        return {"items": [{**dict(row), "id": int(row["id"]), "sourceType": kind} for row in rows],
                "total": total, "offset": kwargs.get("offset", 0), "limit": kwargs.get("limit", 25)}


def lookups(db, role, kind=None, search=None, limit=100):
    with database_errors(db):
        return [{"id": int(row["ledgerId"]), "name": row["ledgerName"], "accountGroupName": row["accountGroupName"]}
                for row in repo.list_accounts(db, role, kind, search, limit)]


def open_references(db, kind, ledger_id):
    account = repo.account(db, ledger_id)
    if account is None:
        raise HTTPException(404, "Account Ledger not found")
    with database_errors(db):
        return [{
            "ledgerId": int(row["ledgerId"]), "sourceVoucherTypeId": int(row["sourceVoucherTypeId"]),
            "sourceVoucherTypeName": row["sourceVoucherTypeName"], "sourceVoucherNo": str(row["sourceVoucherNo"]),
            "sourceInvoiceNo": str(row["sourceInvoiceNo"]) if row["sourceInvoiceNo"] is not None else None,
            "pendingAmount": money(row["pendingAmount"]), "currencySymbol": row["currencySymbol"],
        } for row in repo.open_references(db, ledger_id, kind)]


def numbering(db, kind, value):
    with database_errors(db):
        voucher, _, method, rule = _configuration(db, kind, value)
        number = repo.next_number(db, repo.master_table(kind), int(voucher["voucherTypeId"])) if method == "Automatic" else None
        return {"voucherTypeId": int(voucher["voucherTypeId"]), "numberingMethod": method,
                "automatic": method == "Automatic", "nextVoucherNo": str(number) if number else None,
                "nextInvoiceNo": _format_number(number, rule) if number else None}


def _clearance_response(db, row, source=None, kind=None):
    if row is None: raise HTTPException(404, "PDC Clearance not found")
    kind = kind or ("payable" if str(row["type"]).lower() == "pdc payable" else "receivable")
    source = source or repo.get_master(db, kind, int(row["againstId"]))
    if source is None: raise HTTPException(409, "PDC Clearance source record is missing")
    source_allocations = repo.allocations(db, int(source["voucherTypeId"]), str(source["voucherNo"]))
    party = source_allocations[0] if source_allocations else None
    return {
        "id": int(row["PDCClearanceMasterId"]), "voucherNo": str(row["voucherNo"]),
        "invoiceNo": str(row["invoiceNo"]), "voucherTypeId": int(row["voucherTypeId"]),
        "clearanceDate": row["date"], "sourceType": kind, "sourceId": int(row["againstId"]),
        "sourceInvoiceNo": str(source["invoiceNo"]), "controlLedgerId": int(source["ledgerId"]),
        "controlLedgerName": source["controlLedgerName"],
        "partyLedgerId": int(party["ledgerId"]) if party else None,
        "partyLedgerName": party["ledgerName"] if party else None,
        "bankLedgerId": int(source["bankId"]),
        "bankLedgerName": source["bankLedgerName"], "amount": money(source["amount"]),
        "chequeNo": str(source["chequeNo"]), "chequeDate": source["chequeDate"],
        "status": row["status"], "narration": row["narration"],
        "financialYearId": int(row["financialYearId"]), "idempotencyKey": row["extra1"] or None,
    }


def _save_clearance_postings(db, row, source, kind):
    if row["status"] != "Cleared": return
    master = {"date": row["date"], "voucherTypeId": row["voucherTypeId"],
              "voucherNo": row["voucherNo"], "invoiceNo": row["invoiceNo"],
              "financialYearId": row["financialYearId"], "chequeNo": source["chequeNo"],
              "chequeDate": source["chequeDate"]}
    amount = money(source["amount"])
    repo.insert_posting(db, _posting(master, source["ledgerId"], amount if kind == "payable" else 0, amount if kind == "receivable" else 0))
    repo.insert_posting(db, _posting(master, source["bankId"], amount if kind == "receivable" else 0, amount if kind == "payable" else 0, True))
    totals = repo.posting_totals(db, int(row["voucherTypeId"]), str(row["voucherNo"]))
    if int(totals["rows"]) != 2 or money(totals["debit"]) != money(totals["credit"]):
        raise HTTPException(409, "PDC Clearance postings are incomplete or unbalanced")


def create_clearance(db, kind, source_id, payload, user_id):
    with write_transaction(db):
        source = repo.get_master(db, kind, source_id, for_update=True)
        if source is None: raise HTTPException(404, f"PDC {kind.title()} not found")
        if payload.clearanceDate.date() < source["date"].date():
            raise HTTPException(422, "clearanceDate cannot be earlier than the PDC voucher date")
        if repo.clearance_for_source(db, kind, source_id):
            raise HTTPException(409, "This PDC already has a clearance result")
        voucher = repo.clearance_voucher_type(db)
        year = repo.financial_year(db, payload.clearanceDate)
        if voucher is None or year is None: raise HTTPException(422, "PDC Clearance configuration is incomplete")
        voucher_type_id = int(voucher["voucherTypeId"])
        repo.lock_numbering(db, voucher_type_id)
        retry = repo.clearance_by_key(db, voucher_type_id, payload.idempotencyKey)
        if retry is not None: return _clearance_response(db, retry)
        number = repo.next_number(db, repo.CLEARANCE, voucher_type_id)
        clearance_id = repo.insert_clearance(db, {
            "voucherNo": str(number), "invoiceNo": str(number), "suffixPrefixId": 0,
            "date": payload.clearanceDate, "ledgerId": source["ledgerId"],
            "type": "PDC Payable" if kind == "payable" else "PDC Receivable",
            "againstId": source_id, "voucherTypeId": voucher_type_id,
            "narration": payload.narration, "status": payload.status, "userId": user_id,
            "financialYearId": int(year["financialYearId"]), "extraDate": None,
            "extra1": payload.idempotencyKey or "", "extra2": "",
        })
        row = repo.get_clearance(db, clearance_id)
        _save_clearance_postings(db, row, source, kind)
        db.commit()
        return _clearance_response(db, repo.get_clearance(db, clearance_id), source, kind)


def update_clearance(db, clearance_id, payload, user_id):
    with write_transaction(db):
        row = repo.get_clearance(db, clearance_id, for_update=True)
        if row is None: raise HTTPException(404, "PDC Clearance not found")
        if str(row["status"] or "").lower() == "cleared":
            raise HTTPException(409, "A cleared PDC Clearance is final and cannot be edited")
        kind = "payable" if str(row["type"]).lower() == "pdc payable" else "receivable"
        source = repo.get_master(db, kind, int(row["againstId"]), for_update=True)
        if repo.has_reconciliation(db, int(row["voucherTypeId"]), str(row["voucherNo"])):
            raise HTTPException(409, "A reconciled PDC Clearance cannot be edited")
        year = repo.financial_year(db, payload.clearanceDate)
        if year is None: raise HTTPException(422, "clearanceDate does not belong to a configured financial year")
        repo.delete_postings(db, int(row["voucherTypeId"]), str(row["voucherNo"]))
        repo.update_clearance(db, clearance_id, {
            "date": payload.clearanceDate, "narration": payload.narration,
            "status": payload.status, "userId": user_id,
            "financialYearId": int(year["financialYearId"]),
        })
        updated = repo.get_clearance(db, clearance_id)
        _save_clearance_postings(db, updated, source, kind)
        db.commit()
        return _clearance_response(db, repo.get_clearance(db, clearance_id), source, kind)


def delete_clearance(db, clearance_id):
    with write_transaction(db):
        row = repo.get_clearance(db, clearance_id, for_update=True)
        if row is None: raise HTTPException(404, "PDC Clearance not found")
        if str(row["status"] or "").lower() == "cleared":
            raise HTTPException(409, "A cleared PDC Clearance is final and cannot be deleted")
        voucher_type_id, voucher_no = int(row["voucherTypeId"]), str(row["voucherNo"])
        if repo.has_reconciliation(db, voucher_type_id, voucher_no):
            raise HTTPException(409, "A reconciled PDC Clearance cannot be deleted")
        repo.delete_postings(db, voucher_type_id, voucher_no)
        if repo.delete_clearance(db, clearance_id) != 1: raise HTTPException(409, "PDC Clearance changed during deletion")
        db.commit()


def get_clearance(db, clearance_id):
    with database_errors(db): return _clearance_response(db, repo.get_clearance(db, clearance_id))


def list_clearances(db, from_date=None, to_date=None, **kwargs):
    if from_date is not None and to_date is not None and from_date > to_date:
        raise HTTPException(422, "fromDate cannot be after toDate")
    from_bound = datetime.combine(from_date, time.min) if from_date else None
    to_bound = datetime.combine(to_date + timedelta(days=1), time.min) if to_date else None
    with database_errors(db):
        rows, total = repo.list_clearances(db, from_bound, to_bound, **kwargs)
        return {"items": [_clearance_response(db, row, source, kind) for row, source, kind in rows],
                "total": total, "offset": kwargs.get("offset", 0), "limit": kwargs.get("limit", 25)}
