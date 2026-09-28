from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException

from app.master_data import database_errors
from . import repository as repo


MONEY = Decimal("0.00001")
DB_DEPOSIT = "Deposit"
DB_WITHDRAWAL = "Withdraw"


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


def _db_direction(direction: str) -> str:
    return DB_DEPOSIT if direction == "deposit" else DB_WITHDRAWAL


def _api_direction(direction: str | None) -> str:
    return "deposit" if str(direction or "").lower() == "deposit" else "withdrawal"


def _is_bank(account) -> bool:
    return "bank" in str(account.get("accountGroupName") or "").lower()


def _voucher_type(db):
    voucher = repo.get_contra_voucher_type(db)
    if voucher is None:
        raise HTTPException(422, "Contra Voucher type is not configured")
    return voucher


def _numbering(db, voucher, voucher_date):
    method = str(voucher["methodOfVoucherNumbering"] or "").strip()
    if method not in {"Automatic", "Manual"}:
        raise HTTPException(422, "Contra Voucher numbering method must be Automatic or Manual")
    rule = repo.get_suffix_prefix(db, int(voucher["voucherTypeId"]), voucher_date)
    return method, rule


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


def _validate_payload(db, payload, existing=None):
    voucher = _voucher_type(db)
    financial_year = _validate_period(db, payload.voucherDate)
    method, rule = _numbering(db, voucher, payload.voucherDate)

    if method == "Automatic" and payload.manualVoucherNo is not None:
        raise HTTPException(422, "manualVoucherNo must be omitted for automatic numbering")
    if method == "Manual" and payload.manualVoucherNo is None:
        raise HTTPException(422, "manualVoucherNo is required for manual numbering")
    if existing is not None and method == "Manual" and payload.manualVoucherNo != existing["invoiceNo"]:
        raise HTTPException(422, "manualVoucherNo cannot be changed after creation")

    header = repo.eligible_account(db, payload.headerLedgerId)
    if header is None:
        raise HTTPException(409, "headerLedgerId must be an eligible cash or bank ledger")

    lines = []
    account_cache = {payload.headerLedgerId: header}
    for line in payload.lines:
        if line.ledgerId == payload.headerLedgerId:
            raise HTTPException(409, "A detail ledger cannot be the header ledger")
        account = account_cache.get(line.ledgerId)
        if account is None:
            account = repo.eligible_account(db, line.ledgerId)
            account_cache[line.ledgerId] = account
        if account is None:
            raise HTTPException(409, "Every detail ledger must be an eligible cash or bank ledger")
        if not _is_bank(account) and (line.chequeNo is not None or line.chequeDate is not None):
            raise HTTPException(422, "Cheque fields are allowed only for bank detail ledgers")

        exchange = repo.get_exchange_rate(db, line.exchangeRateId, payload.voucherDate)
        if exchange is None or _decimal(exchange["rate"]) <= 0:
            raise HTTPException(422, "exchangeRateId must be valid on voucherDate and have a positive rate")
        base_amount = _round(line.amount * _decimal(exchange["rate"]))
        if base_amount <= 0:
            raise HTTPException(422, "Converted line amount must be greater than zero")
        lines.append({
            "input": line,
            "account": account,
            "exchange": exchange,
            "baseAmount": base_amount,
        })

    total = _round(sum((line["baseAmount"] for line in lines), Decimal("0")))
    if total <= 0:
        raise HTTPException(422, "Contra Voucher total must be greater than zero")
    return voucher, financial_year, method, rule, header, lines, total


def _negative_balance_check(db, payload, voucher, header, lines, total, existing=None):
    status = str(repo.get_setting(db, "NegativeCashTransaction") or "Ignore").strip().lower()
    if status not in {"warn", "block"}:
        return

    exclude_voucher_type_id = int(existing["voucherTypeId"]) if existing is not None else None
    exclude_voucher_no = existing["voucherNo"] if existing is not None else None
    shortages = []
    if payload.direction == "withdrawal":
        balance = repo.ledger_balance(db, header, exclude_voucher_type_id, exclude_voucher_no)
        if _round(balance - total) < 0:
            shortages.append(header["ledgerName"] or str(header["ledgerId"]))
    else:
        outgoing = defaultdict(lambda: Decimal("0"))
        accounts = {}
        for line in lines:
            ledger_id = int(line["account"]["ledgerId"])
            outgoing[ledger_id] += line["baseAmount"]
            accounts[ledger_id] = line["account"]
        for ledger_id, amount in outgoing.items():
            balance = repo.ledger_balance(db, accounts[ledger_id], exclude_voucher_type_id, exclude_voucher_no)
            if _round(balance - amount) < 0:
                shortages.append(accounts[ledger_id]["ledgerName"] or str(ledger_id))

    if not shortages:
        return
    detail = {
        "code": "NEGATIVE_CASH_BALANCE",
        "message": "The voucher would create a negative cash/bank balance",
        "ledgers": shortages,
        "canConfirm": status == "warn",
    }
    if status == "block":
        raise HTTPException(409, detail)
    if not payload.confirmNegativeBalance:
        raise HTTPException(409, detail)


def _posting_values(voucher_date, voucher_type_id, voucher_no, invoice_no, financial_year_id,
                    ledger_id, debit, credit, details_id, cheque_no=None, cheque_date=None):
    return {
        "date": voucher_date,
        "voucherTypeId": voucher_type_id,
        "voucherNo": voucher_no,
        "ledgerId": ledger_id,
        "debit": _round(debit),
        "credit": _round(credit),
        "detailsId": details_id,
        "yearId": financial_year_id,
        "invoiceNo": invoice_no,
        "chequeNo": cheque_no,
        "chequeDate": cheque_date,
        "extraDate": None,
        "extra1": "",
        "extra2": "",
    }


def _detail_values(master_id, line):
    item = line["input"]
    return {
        "contraMasterId": master_id,
        "ledgerId": item.ledgerId,
        "amount": item.amount,
        "exchangeRateId": item.exchangeRateId,
        "chequeNo": item.chequeNo,
        "chequeDate": item.chequeDate,
        "extraDate": None,
        "extra1": "",
        "extra2": "",
    }


def _line_posting_values(payload, voucher_type_id, voucher_no, invoice_no, financial_year_id, line, detail_id):
    if payload.direction == "deposit":
        debit, credit = Decimal("0"), line["baseAmount"]
    else:
        debit, credit = line["baseAmount"], Decimal("0")
    item = line["input"]
    return _posting_values(
        payload.voucherDate, voucher_type_id, voucher_no, invoice_no, financial_year_id,
        item.ledgerId, debit, credit, detail_id, item.chequeNo, item.chequeDate,
    )


def _balancing_posting_values(payload, voucher_type_id, voucher_no, invoice_no, financial_year_id, total):
    if payload.direction == "deposit":
        debit, credit = total, Decimal("0")
    else:
        debit, credit = Decimal("0"), total
    return _posting_values(
        payload.voucherDate, voucher_type_id, voucher_no, invoice_no, financial_year_id,
        payload.headerLedgerId, debit, credit, 0,
    )


def _response(db, master):
    if master is None:
        raise HTTPException(404, "Contra Voucher not found")
    direction = _api_direction(master["type"])
    lines = []
    for row in repo.get_details(db, int(master["contraMasterId"])):
        rate = _decimal(row["exchangeRate"])
        lines.append({
            "contraDetailsId": int(row["contraDetailsId"]),
            "ledgerId": int(row["ledgerId"]),
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
        })
    return {
        "contraMasterId": int(master["contraMasterId"]),
        "voucherNo": str(master["voucherNo"]),
        "invoiceNo": str(master["invoiceNo"]),
        "voucherTypeId": int(master["voucherTypeId"]),
        "suffixPrefixId": int(master["suffixPrefixId"] or 0),
        "voucherDate": master["date"],
        "direction": direction,
        "headerLedgerId": int(master["ledgerId"]),
        "headerLedgerName": master["headerLedgerName"],
        "totalAmount": _decimal(master["totalAmount"]),
        "narration": master["narration"],
        "idempotencyKey": master["extra1"] or None,
        "userId": int(master["userId"]),
        "financialYearId": int(master["financialYearId"]),
        "lines": lines,
    }


def get_voucher(db, contra_master_id):
    with database_errors(db):
        return _response(db, repo.get_master(db, contra_master_id))


def list_vouchers(db, from_date=None, to_date=None, voucher_no=None, ledger_id=None,
                  direction=None, offset=0, limit=10):
    if from_date is not None and to_date is not None and from_date > to_date:
        raise HTTPException(422, "fromDate cannot be after toDate")
    from_datetime = datetime.combine(from_date, time.min) if from_date is not None else None
    to_datetime_exclusive = (
        datetime.combine(to_date + timedelta(days=1), time.min) if to_date is not None else None
    )
    normalized_voucher_no = voucher_no.strip() if voucher_no and voucher_no.strip() else None
    with database_errors(db):
        rows, total = repo.list_vouchers(
            db,
            from_datetime=from_datetime,
            to_datetime_exclusive=to_datetime_exclusive,
            voucher_no=normalized_voucher_no,
            ledger_id=ledger_id,
            direction=_db_direction(direction) if direction else None,
            offset=offset,
            limit=limit,
        )
        master_ids = [int(row["contraMasterId"]) for row in rows]
        offset_accounts = defaultdict(list)
        line_counts = defaultdict(int)
        for account in repo.list_offset_accounts(db, master_ids):
            master_id = int(account["contraMasterId"])
            line_counts[master_id] += 1
            if account["ledgerName"] is not None:
                offset_accounts[master_id].append(str(account["ledgerName"]))
        items = []
        for row in rows:
            master_id = int(row["contraMasterId"])
            items.append({
                "contraMasterId": master_id,
                "voucherNo": str(row["voucherNo"]),
                "invoiceNo": str(row["invoiceNo"]),
                "voucherDate": row["voucherDate"],
                "direction": _api_direction(row["type"]),
                "headerLedgerId": int(row["headerLedgerId"]),
                "headerLedgerName": row["headerLedgerName"],
                "offsetAccountNames": offset_accounts[master_id],
                "lineCount": line_counts[master_id],
                "totalAmount": _decimal(row["totalAmount"]),
                "narration": row["narration"],
            })
        return {
            "items": items,
            "total": total,
            "offset": offset,
            "limit": limit,
        }


def create_voucher(db, payload, user_id):
    with _write_transaction(db):
        voucher, financial_year, method, rule, header, lines, total = _validate_payload(db, payload)
        voucher_type_id = int(voucher["voucherTypeId"])

        repo.lock_numbering_scope(db, voucher_type_id)
        if payload.idempotencyKey:
            retry = repo.get_master_by_idempotency_key(db, voucher_type_id, payload.idempotencyKey)
            if retry is not None:
                return _response(db, retry)

        _negative_balance_check(db, payload, voucher, header, lines, total)
        start_index = int(rule["startIndex"] or 1) if rule is not None else 1
        internal_number = repo.next_internal_voucher_number(db, voucher_type_id, start_index)
        voucher_no = str(internal_number)
        invoice_no = payload.manualVoucherNo if method == "Manual" else _format_invoice_no(internal_number, rule)
        if repo.voucher_number_exists(db, voucher_type_id, invoice_no):
            raise HTTPException(409, "Contra Voucher number already exists")

        financial_year_id = int(financial_year["financialYearId"])
        suffix_prefix_id = int(rule["suffixprefixId"]) if rule is not None else 0
        master_id = repo.insert_master(db, {
            "voucherNo": voucher_no,
            "invoiceNo": invoice_no,
            "suffixPrefixId": suffix_prefix_id,
            "date": payload.voucherDate,
            "ledgerId": payload.headerLedgerId,
            "type": _db_direction(payload.direction),
            "totalAmount": total,
            "narration": payload.narration,
            "userId": user_id,
            "voucherTypeId": voucher_type_id,
            "financialYearId": financial_year_id,
            "extraDate": None,
            "extra1": payload.idempotencyKey or "",
            "extra2": "",
        })
        for line in lines:
            detail_id = repo.insert_detail(db, _detail_values(master_id, line))
            repo.insert_posting(db, _line_posting_values(
                payload, voucher_type_id, voucher_no, invoice_no, financial_year_id, line, detail_id
            ))
        repo.insert_posting(db, _balancing_posting_values(
            payload, voucher_type_id, voucher_no, invoice_no, financial_year_id, total
        ))
        if repo.count_postings(db, voucher_type_id, voucher_no) != len(lines) + 1:
            raise HTTPException(409, "Contra Voucher posting set is incomplete")
        db.commit()
        return _response(db, repo.get_master(db, master_id))


def update_voucher(db, contra_master_id, payload, user_id):
    with _write_transaction(db):
        existing = repo.get_master(db, contra_master_id, for_update=True)
        if existing is None:
            raise HTTPException(404, "Contra Voucher not found")
        voucher, financial_year, method, rule, header, lines, total = _validate_payload(db, payload, existing)
        voucher_type_id = int(existing["voucherTypeId"])
        if voucher_type_id != int(voucher["voucherTypeId"]):
            raise HTTPException(409, "Contra Voucher type configuration changed")
        _negative_balance_check(db, payload, voucher, header, lines, total, existing)

        voucher_no = str(existing["voucherNo"])
        invoice_no = str(existing["invoiceNo"])
        financial_year_id = int(financial_year["financialYearId"])
        suffix_prefix_id = int(rule["suffixprefixId"]) if rule is not None else 0
        old_rows = repo.get_details(db, contra_master_id)
        old_ids = {int(row["contraDetailsId"]) for row in old_rows}
        submitted_ids = {
            int(line["input"].contraDetailsId)
            for line in lines
            if line["input"].contraDetailsId is not None
        }
        if not submitted_ids.issubset(old_ids):
            raise HTTPException(404, "A contraDetailsId does not belong to this Contra Voucher")

        removed_ids = old_ids - submitted_ids
        repo.delete_postings(db, voucher_type_id, voucher_no, removed_ids)
        repo.delete_details(db, contra_master_id, removed_ids)

        for line in lines:
            detail_id = line["input"].contraDetailsId
            if detail_id is None:
                detail_id = repo.insert_detail(db, _detail_values(contra_master_id, line))
                repo.insert_posting(db, _line_posting_values(
                    payload, voucher_type_id, voucher_no, invoice_no, financial_year_id, line, detail_id
                ))
            else:
                if repo.update_detail(db, detail_id, contra_master_id, _detail_values(contra_master_id, line)) != 1:
                    raise HTTPException(409, "Contra Voucher detail changed during update")
                if repo.update_detail_posting(
                    db, detail_id, voucher_type_id, voucher_no,
                    _line_posting_values(payload, voucher_type_id, voucher_no, invoice_no, financial_year_id, line, detail_id),
                ) != 1:
                    raise HTTPException(409, "Contra Voucher detail posting is missing or duplicated")

        if repo.update_balancing_posting(
            db, voucher_type_id, voucher_no,
            _balancing_posting_values(payload, voucher_type_id, voucher_no, invoice_no, financial_year_id, total),
        ) != 1:
            raise HTTPException(409, "Contra Voucher balancing posting is missing or duplicated")
        if repo.update_master(db, contra_master_id, {
            "suffixPrefixId": suffix_prefix_id,
            "date": payload.voucherDate,
            "ledgerId": payload.headerLedgerId,
            "type": _db_direction(payload.direction),
            "totalAmount": total,
            "narration": payload.narration,
            "userId": user_id,
            "financialYearId": financial_year_id,
        }) != 1:
            raise HTTPException(409, "Contra Voucher changed during update")
        if repo.count_postings(db, voucher_type_id, voucher_no) != len(lines) + 1:
            raise HTTPException(409, "Contra Voucher posting set is incomplete")
        db.commit()
        return _response(db, repo.get_master(db, contra_master_id))


def delete_voucher(db, contra_master_id):
    with _write_transaction(db):
        existing = repo.get_master(db, contra_master_id, for_update=True)
        if existing is None:
            raise HTTPException(404, "Contra Voucher not found")
        voucher_type_id = int(existing["voucherTypeId"])
        voucher_no = str(existing["voucherNo"])
        repo.delete_postings(db, voucher_type_id, voucher_no)
        repo.delete_details(db, contra_master_id)
        if repo.delete_master(db, contra_master_id) != 1:
            raise HTTPException(409, "Contra Voucher changed during deletion")
        db.commit()


def accounts(db):
    with database_errors(db):
        return [{
            "id": int(row["ledgerId"]),
            "name": row["ledgerName"],
            "accountGroupId": int(row["accountGroupId"]) if row["accountGroupId"] is not None else None,
            "accountGroupName": row["accountGroupName"],
            "isBank": _is_bank(row),
        } for row in repo.list_eligible_accounts(db)]


def exchange_rates(db, voucher_date):
    with database_errors(db):
        return [{
            "id": int(row["exchangeRateId"]),
            "currencyId": int(row["currencyId"]),
            "currencyName": row["currencyName"],
            "currencySymbol": row["currencySymbol"],
            "rate": _decimal(row["rate"]),
            "date": row["date"],
        } for row in repo.list_exchange_rates(db, voucher_date)]


def voucher_types(db):
    with database_errors(db):
        voucher = _voucher_type(db)
        return [{
            "id": int(voucher["voucherTypeId"]),
            "name": voucher["voucherTypeName"],
            "numberingMethod": voucher["methodOfVoucherNumbering"],
        }]


def numbering_rule(db, voucher_date):
    with database_errors(db):
        voucher = _voucher_type(db)
        method, rule = _numbering(db, voucher, voucher_date)
        next_voucher_no = None
        next_invoice_no = None
        if method == "Automatic":
            number = repo.next_internal_voucher_number(
                db,
                int(voucher["voucherTypeId"]),
                int(rule["startIndex"] or 1) if rule is not None else 1,
            )
            next_voucher_no = str(number)
            next_invoice_no = _format_invoice_no(number, rule)
        return {
            "voucherTypeId": int(voucher["voucherTypeId"]),
            "numberingMethod": method,
            "automatic": method == "Automatic",
            "suffixPrefixId": int(rule["suffixprefixId"]) if rule is not None else 0,
            "prefix": rule["prefix"] if rule is not None else None,
            "suffix": rule["suffix"] if rule is not None else None,
            "startIndex": int(rule["startIndex"]) if rule is not None and rule["startIndex"] is not None else None,
            "widthOfNumericalPart": rule["widthOfNumericalPart"] if rule is not None else None,
            "prefillWithZero": rule["prefillWithZero"] if rule is not None else None,
            "nextVoucherNo": next_voucher_no,
            "nextInvoiceNo": next_invoice_no,
            "fromDate": rule["fromDate"] if rule is not None else None,
            "toDate": rule["toDate"] if rule is not None else None,
        }
