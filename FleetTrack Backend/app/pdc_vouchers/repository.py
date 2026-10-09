from sqlalchemy import Integer, and_, cast, func, not_, or_, select, text

from app.generated_models.models import Base


PAYABLE = Base.metadata.tables["tbl_PDCPayableMaster"]
RECEIVABLE = Base.metadata.tables["tbl_PDCReceivableMaster"]
CLEARANCE = Base.metadata.tables["tbl_PDCClearanceMaster"]
LEDGER = Base.metadata.tables["tbl_AccountLedger"]
ACCOUNT_GROUP = Base.metadata.tables["tbl_AccountGroup"]
VOUCHER_TYPE = Base.metadata.tables["tbl_VoucherType"]
SUFFIX_PREFIX = Base.metadata.tables["tbl_SuffixPrefix"]
FINANCIAL_YEAR = Base.metadata.tables["tbl_FinancialYear"]
LEDGER_POSTING = Base.metadata.tables["tbl_LedgerPosting"]
PARTY_BALANCE = Base.metadata.tables["tbl_PartyBalance"]
BANK_RECONCILIATION = Base.metadata.tables["tbl_BankReconciliation"]
EXCHANGE_RATE = Base.metadata.tables["tbl_ExchangeRate"]
CURRENCY = Base.metadata.tables["tbl_Currency"]


def master_table(kind):
    return PAYABLE if kind == "payable" else RECEIVABLE


def id_column(kind):
    return PAYABLE.c.pdcPayableMasterId if kind == "payable" else RECEIVABLE.c.pdcReceivableMasterId


def voucher_type(db, kind):
    expected = "PDC Payable" if kind == "payable" else "PDC Receivable"
    return db.execute(select(VOUCHER_TYPE).where(
        func.lower(VOUCHER_TYPE.c.typeOfVoucher) == expected.lower(),
        or_(VOUCHER_TYPE.c.isActive == True, VOUCHER_TYPE.c.isActive.is_(None)),
    ).order_by(VOUCHER_TYPE.c.voucherTypeId)).mappings().first()


def clearance_voucher_type(db):
    return db.execute(select(VOUCHER_TYPE).where(
        func.lower(VOUCHER_TYPE.c.typeOfVoucher) == "pdc clearance",
        or_(VOUCHER_TYPE.c.isActive == True, VOUCHER_TYPE.c.isActive.is_(None)),
    )).mappings().first()


def financial_year(db, value):
    return db.execute(select(FINANCIAL_YEAR).where(
        FINANCIAL_YEAR.c.fromDate <= value,
        FINANCIAL_YEAR.c.toDate >= value,
    )).mappings().first()


def suffix_rule(db, voucher_type_id, value):
    return db.execute(select(SUFFIX_PREFIX).where(
        SUFFIX_PREFIX.c.voucherTypeId == voucher_type_id,
        SUFFIX_PREFIX.c.fromDate <= value,
        SUFFIX_PREFIX.c.toDate >= value,
    ).order_by(SUFFIX_PREFIX.c.suffixprefixId.desc())).mappings().first()


def lock_numbering(db, voucher_type_id):
    if db.bind is not None and db.bind.dialect.name == "mssql":
        db.execute(text(
            "SELECT voucherTypeId FROM tbl_VoucherType WITH (UPDLOCK, HOLDLOCK) "
            "WHERE voucherTypeId=:id"
        ), {"id": voucher_type_id}).first()


def next_number(db, table, voucher_type_id):
    if db.bind is not None and db.bind.dialect.name == "mssql":
        table_name = table.name
        current = db.execute(text(
            f"SELECT MAX(TRY_CONVERT(bigint, voucherNo)) FROM {table_name} "
            "WHERE voucherTypeId=:id"
        ), {"id": voucher_type_id}).scalar_one_or_none()
    else:
        current = db.execute(select(func.max(cast(table.c.voucherNo, Integer))).where(
            table.c.voucherTypeId == voucher_type_id
        )).scalar_one_or_none()
    return int(current or 0) + 1


def invoice_exists(db, table, voucher_type_id, invoice_no, exclude_id=None, kind=None):
    query = select(table.c.voucherTypeId).where(
        table.c.voucherTypeId == voucher_type_id, table.c.invoiceNo == invoice_no
    )
    if exclude_id is not None and kind is not None:
        query = query.where(id_column(kind) != exclude_id)
    return db.execute(query.limit(1)).first() is not None


def account(db, ledger_id):
    return db.execute(select(
        LEDGER.c.ledgerId, LEDGER.c.ledgerName, LEDGER.c.accountGroupId,
        LEDGER.c.billByBill, ACCOUNT_GROUP.c.accountGroupName,
    ).select_from(LEDGER.outerjoin(
        ACCOUNT_GROUP, ACCOUNT_GROUP.c.accountGroupId == LEDGER.c.accountGroupId
    )).where(LEDGER.c.ledgerId == ledger_id)).mappings().first()


def exchange_rate(db, exchange_rate_id):
    return db.execute(select(
        EXCHANGE_RATE.c.exchangeRateId, EXCHANGE_RATE.c.rate,
        CURRENCY.c.currencySymbol,
    ).select_from(EXCHANGE_RATE.outerjoin(
        CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId
    )).where(EXCHANGE_RATE.c.exchangeRateId == exchange_rate_id)).mappings().first()


def cheque_exists(db, kind, bank_id, cheque_no, exclude_id=None):
    table = master_table(kind)
    query = select(id_column(kind)).where(
        table.c.bankId == bank_id,
        func.lower(table.c.chequeNo) == cheque_no.lower(),
    )
    if exclude_id is not None:
        query = query.where(id_column(kind) != exclude_id)
    return db.execute(query.limit(1)).first() is not None


def list_accounts(db, role, kind=None, search=None, limit=100):
    query = select(
        LEDGER.c.ledgerId, LEDGER.c.ledgerName, ACCOUNT_GROUP.c.accountGroupName,
    ).select_from(LEDGER.outerjoin(
        ACCOUNT_GROUP, ACCOUNT_GROUP.c.accountGroupId == LEDGER.c.accountGroupId
    )).where(LEDGER.c.ledgerName.is_not(None))
    group_name = func.lower(ACCOUNT_GROUP.c.accountGroupName)
    if role == "bank":
        query = query.where(group_name.in_(("bank account", "bank od a/c")))
    elif role in {"party", "control", "account"}:
        # Legacy PDC entry permits selecting any account ledger. The selected
        # account simply has no open references when it is not bill-by-bill.
        pass
    if search:
        query = query.where(LEDGER.c.ledgerName.icontains(search, autoescape=True))
    return db.execute(query.order_by(LEDGER.c.ledgerName).limit(limit)).mappings().all()


def _open_reference_query(ledger_id, kind, exclude_type=None, exclude_no=None):
    pending = (func.coalesce(func.sum(PARTY_BALANCE.c.credit), 0) - func.coalesce(func.sum(PARTY_BALANCE.c.debit), 0)
               if kind == "payable" else
               func.coalesce(func.sum(PARTY_BALANCE.c.debit), 0) - func.coalesce(func.sum(PARTY_BALANCE.c.credit), 0))
    query = select(
        PARTY_BALANCE.c.ledgerId,
        PARTY_BALANCE.c.voucherTypeId.label("sourceVoucherTypeId"),
        PARTY_BALANCE.c.voucherNo.label("sourceVoucherNo"),
        func.max(PARTY_BALANCE.c.invoiceNo).label("sourceInvoiceNo"),
        pending.label("pendingAmount"),
        func.max(PARTY_BALANCE.c.exchangeRateId).label("exchangeRateId"),
    ).where(PARTY_BALANCE.c.ledgerId == ledger_id)
    if exclude_type is not None and exclude_no is not None:
        query = query.where(not_(and_(
            PARTY_BALANCE.c.againstVoucherTypeId == exclude_type,
            PARTY_BALANCE.c.againstVoucherNo == exclude_no,
        )))
    return query.group_by(
        PARTY_BALANCE.c.ledgerId, PARTY_BALANCE.c.voucherTypeId, PARTY_BALANCE.c.voucherNo
    ).having(pending > 0).subquery()


def open_references(db, ledger_id, kind, exclude_type=None, exclude_no=None):
    grouped = _open_reference_query(ledger_id, kind, exclude_type, exclude_no)
    return db.execute(select(
        grouped, VOUCHER_TYPE.c.voucherTypeName.label("sourceVoucherTypeName"),
        EXCHANGE_RATE.c.rate, EXCHANGE_RATE.c.currencyId, CURRENCY.c.currencySymbol,
    ).select_from(grouped.outerjoin(
        VOUCHER_TYPE, VOUCHER_TYPE.c.voucherTypeId == grouped.c.sourceVoucherTypeId
    ).outerjoin(
        EXCHANGE_RATE, EXCHANGE_RATE.c.exchangeRateId == grouped.c.exchangeRateId
    ).outerjoin(
        CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId
    )).order_by(VOUCHER_TYPE.c.voucherTypeName, grouped.c.sourceInvoiceNo)).mappings().all()


def lock_open_reference(db, ledger_id, kind, source_type, source_no):
    if db.bind is not None and db.bind.dialect.name == "mssql":
        db.execute(text(
            "SELECT partyBalanceId FROM tbl_PartyBalance WITH (UPDLOCK,HOLDLOCK) "
            "WHERE ledgerId=:ledger AND voucherTypeId=:type AND voucherNo=:no"
        ), {"ledger": ledger_id, "type": source_type, "no": source_no}).all()
    grouped = _open_reference_query(ledger_id, kind)
    return db.execute(select(grouped).where(
        grouped.c.sourceVoucherTypeId == source_type,
        grouped.c.sourceVoucherNo == source_no,
    )).mappings().first()


def party_posting_subqueries(table, kind):
    party = LEDGER.alias("posting_party")
    matching_posting = and_(
        LEDGER_POSTING.c.voucherTypeId == table.c.voucherTypeId,
        LEDGER_POSTING.c.voucherNo == table.c.voucherNo,
        LEDGER_POSTING.c.ledgerId != table.c.ledgerId,
    )
    source = LEDGER_POSTING.join(party, party.c.ledgerId == LEDGER_POSTING.c.ledgerId)
    party_id = select(func.min(LEDGER_POSTING.c.ledgerId)).select_from(source).where(matching_posting).correlate(table).scalar_subquery()
    party_name = select(func.max(party.c.ledgerName)).select_from(source).where(matching_posting).correlate(table).scalar_subquery()
    return party_id, party_name


def get_master(db, kind, master_id, for_update=False):
    table = master_table(kind)
    pk = id_column(kind)
    if for_update and db.bind is not None and db.bind.dialect.name == "mssql":
        db.execute(text(
            f"SELECT {pk.name} FROM {table.name} WITH (UPDLOCK,HOLDLOCK) WHERE {pk.name}=:id"
        ), {"id": master_id}).first()
    control = LEDGER.alias("control")
    bank = LEDGER.alias("bank")
    party_id, party_name = party_posting_subqueries(table, kind)
    query = select(
        table, control.c.ledgerName.label("controlLedgerName"),
        party_id.label("partyLedgerId"), party_name.label("partyLedgerName"),
        bank.c.ledgerName.label("bankLedgerName"), VOUCHER_TYPE.c.voucherTypeName,
    ).select_from(table.outerjoin(control, control.c.ledgerId == table.c.ledgerId)
      .outerjoin(bank, bank.c.ledgerId == table.c.bankId)
      .outerjoin(VOUCHER_TYPE, VOUCHER_TYPE.c.voucherTypeId == table.c.voucherTypeId)
    ).where(pk == master_id)
    return db.execute(query).mappings().first()


def get_master_by_key(db, kind, voucher_type_id, key):
    if not key:
        return None
    table = master_table(kind)
    master_id = db.execute(select(id_column(kind)).where(
        table.c.voucherTypeId == voucher_type_id, table.c.extra1 == key
    )).scalar_one_or_none()
    return get_master(db, kind, int(master_id)) if master_id is not None else None


def insert_master(db, kind, values):
    result = db.execute(master_table(kind).insert().values(**values))
    return int(result.inserted_primary_key[0])


def update_master(db, kind, master_id, values):
    return db.execute(master_table(kind).update().where(id_column(kind) == master_id).values(**values)).rowcount


def delete_master(db, kind, master_id):
    return db.execute(master_table(kind).delete().where(id_column(kind) == master_id)).rowcount


def clearance_for_source(db, kind, master_id):
    return db.execute(select(CLEARANCE).where(
        func.lower(CLEARANCE.c.type) == ("pdc payable" if kind == "payable" else "pdc receivable"),
        CLEARANCE.c.againstId == master_id,
    ).order_by(CLEARANCE.c.PDCClearanceMasterId.desc())).mappings().first()


def allocation_condition(voucher_type_id, voucher_no):
    return and_(
        PARTY_BALANCE.c.againstVoucherTypeId == voucher_type_id,
        PARTY_BALANCE.c.againstVoucherNo == voucher_no,
        PARTY_BALANCE.c.referenceType == "Against",
    )


def allocations(db, voucher_type_id, voucher_no):
    return db.execute(select(
        PARTY_BALANCE, LEDGER.c.ledgerName,
        VOUCHER_TYPE.c.voucherTypeName.label("sourceVoucherTypeName"),
    ).select_from(PARTY_BALANCE.outerjoin(
        LEDGER, LEDGER.c.ledgerId == PARTY_BALANCE.c.ledgerId
    ).outerjoin(
        VOUCHER_TYPE, VOUCHER_TYPE.c.voucherTypeId == PARTY_BALANCE.c.voucherTypeId
    )).where(allocation_condition(voucher_type_id, voucher_no)).order_by(
        PARTY_BALANCE.c.partyBalanceId
    )).mappings().all()


def insert_allocation(db, values):
    return int(db.execute(PARTY_BALANCE.insert().values(**values)).inserted_primary_key[0])


def delete_allocations(db, voucher_type_id, voucher_no):
    return db.execute(PARTY_BALANCE.delete().where(allocation_condition(
        voucher_type_id, voucher_no
    ))).rowcount


def insert_posting(db, values):
    return int(db.execute(LEDGER_POSTING.insert().values(**values)).inserted_primary_key[0])


def delete_postings(db, voucher_type_id, voucher_no):
    return db.execute(LEDGER_POSTING.delete().where(
        LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
        LEDGER_POSTING.c.voucherNo == voucher_no,
    )).rowcount


def posting_totals(db, voucher_type_id, voucher_no):
    return db.execute(select(
        func.count().label("rows"), func.coalesce(func.sum(LEDGER_POSTING.c.debit), 0).label("debit"),
        func.coalesce(func.sum(LEDGER_POSTING.c.credit), 0).label("credit"),
    ).where(
        LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
        LEDGER_POSTING.c.voucherNo == voucher_no,
    )).mappings().one()


def has_reconciliation(db, voucher_type_id, voucher_no):
    return db.execute(select(BANK_RECONCILIATION.c.reconcileId).select_from(
        BANK_RECONCILIATION.join(
            LEDGER_POSTING,
            LEDGER_POSTING.c.ledgerPostingId == BANK_RECONCILIATION.c.ledgerPostingId,
        )
    ).where(
        LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
        LEDGER_POSTING.c.voucherNo == voucher_no,
    ).limit(1)).first() is not None


def list_masters(db, kind, from_date=None, to_date=None, voucher_no=None, ledger_id=None,
                 bank_id=None, amount=None, cheque_no=None, status=None, offset=0, limit=25):
    table = master_table(kind)
    pk = id_column(kind)
    control = LEDGER.alias("control")
    bank = LEDGER.alias("bank")
    clearance = CLEARANCE.alias("clearance")
    expected_type = "PDC Payable" if kind == "payable" else "PDC Receivable"
    party_ledger_id, party_ledger_name = party_posting_subqueries(table, kind)
    query = select(
        pk.label("id"), table.c.invoiceNo, table.c.voucherTypeId,
        VOUCHER_TYPE.c.voucherTypeName, table.c.date.label("voucherDate"),
        table.c.ledgerId.label("controlLedgerId"), control.c.ledgerName.label("controlLedgerName"),
        party_ledger_id.label("partyLedgerId"), party_ledger_name.label("partyLedgerName"),
        table.c.bankId.label("bankLedgerId"), bank.c.ledgerName.label("bankLedgerName"),
        table.c.amount, table.c.chequeNo, table.c.chequeDate, table.c.narration,
        func.coalesce(clearance.c.status, "Pending").label("status"),
    ).select_from(table.outerjoin(control, control.c.ledgerId == table.c.ledgerId)
      .outerjoin(bank, bank.c.ledgerId == table.c.bankId)
      .outerjoin(VOUCHER_TYPE, VOUCHER_TYPE.c.voucherTypeId == table.c.voucherTypeId)
      .outerjoin(clearance, and_(
          clearance.c.againstId == pk, func.lower(clearance.c.type) == expected_type.lower()
      )))
    if from_date is not None: query = query.where(table.c.date >= from_date)
    if to_date is not None: query = query.where(table.c.date < to_date)
    if voucher_no: query = query.where(or_(table.c.invoiceNo.icontains(voucher_no, autoescape=True), table.c.voucherNo.icontains(voucher_no, autoescape=True)))
    if ledger_id is not None: query = query.where(table.c.ledgerId == ledger_id)
    if bank_id is not None: query = query.where(table.c.bankId == bank_id)
    if amount is not None: query = query.where(table.c.amount == amount)
    if cheque_no: query = query.where(table.c.chequeNo.icontains(cheque_no, autoescape=True))
    if status and status != "All": query = query.where(func.coalesce(clearance.c.status, "Pending") == status)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    return db.execute(query.order_by(table.c.date.desc(), pk.desc()).offset(offset).limit(limit)).mappings().all(), total


def get_clearance(db, clearance_id, for_update=False):
    if for_update and db.bind is not None and db.bind.dialect.name == "mssql":
        db.execute(text(
            "SELECT PDCClearanceMasterId FROM tbl_PDCClearanceMaster WITH (UPDLOCK,HOLDLOCK) "
            "WHERE PDCClearanceMasterId=:id"
        ), {"id": clearance_id}).first()
    return db.execute(select(CLEARANCE).where(
        CLEARANCE.c.PDCClearanceMasterId == clearance_id
    )).mappings().first()


def clearance_by_key(db, voucher_type_id, key):
    if not key: return None
    return db.execute(select(CLEARANCE).where(
        CLEARANCE.c.voucherTypeId == voucher_type_id, CLEARANCE.c.extra1 == key
    )).mappings().first()


def insert_clearance(db, values):
    return int(db.execute(CLEARANCE.insert().values(**values)).inserted_primary_key[0])


def update_clearance(db, clearance_id, values):
    return db.execute(CLEARANCE.update().where(
        CLEARANCE.c.PDCClearanceMasterId == clearance_id
    ).values(**values)).rowcount


def delete_clearance(db, clearance_id):
    return db.execute(CLEARANCE.delete().where(
        CLEARANCE.c.PDCClearanceMasterId == clearance_id
    )).rowcount


def list_clearances(db, from_date=None, to_date=None, source_type=None, ledger_id=None,
                    bank_id=None, status=None, cheque_no=None, offset=0, limit=25):
    query = select(CLEARANCE.c.PDCClearanceMasterId)
    if from_date is not None: query = query.where(CLEARANCE.c.date >= from_date)
    if to_date is not None: query = query.where(CLEARANCE.c.date < to_date)
    if source_type: query = query.where(func.lower(CLEARANCE.c.type) == ("pdc payable" if source_type == "payable" else "pdc receivable"))
    if status and status != "All": query = query.where(CLEARANCE.c.status == status)
    ids = [int(row[0]) for row in db.execute(query.order_by(
        CLEARANCE.c.date.desc(), CLEARANCE.c.PDCClearanceMasterId.desc()
    )).all()]
    rows = []
    for clearance_id in ids:
        row = get_clearance(db, clearance_id)
        kind = "payable" if str(row["type"]).lower() == "pdc payable" else "receivable"
        source = get_master(db, kind, int(row["againstId"]))
        if source is None: continue
        source_allocations = allocations(db, int(source["voucherTypeId"]), str(source["voucherNo"]))
        if ledger_id is not None and not any(int(item["ledgerId"]) == ledger_id for item in source_allocations): continue
        if bank_id is not None and int(source["bankId"]) != bank_id: continue
        if cheque_no and cheque_no.lower() not in str(source["chequeNo"] or "").lower(): continue
        rows.append((row, source, kind))
    return rows[offset:offset + limit], len(rows)
