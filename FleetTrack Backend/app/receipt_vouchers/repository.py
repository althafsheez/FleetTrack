from sqlalchemy import Integer, and_, case, cast, func, not_, or_, select, text

from app.generated_models.models import Base


RECEIPT_MASTER = Base.metadata.tables["tbl_ReceiptMaster"]
RECEIPT_DETAILS = Base.metadata.tables["tbl_ReceiptDetails"]
LEDGER_POSTING = Base.metadata.tables["tbl_LedgerPosting"]
PARTY_BALANCE = Base.metadata.tables["tbl_PartyBalance"]
PARTY_BALANCE_UNPOSTED = Base.metadata.tables["tbl_PartyBalance_Unposted"]
BANK_RECONCILIATION = Base.metadata.tables["tbl_BankReconciliation"]
LEDGER = Base.metadata.tables["tbl_AccountLedger"]
ACCOUNT_GROUP = Base.metadata.tables["tbl_AccountGroup"]
EXCHANGE_RATE = Base.metadata.tables["tbl_ExchangeRate"]
CURRENCY = Base.metadata.tables["tbl_Currency"]
VOUCHER_TYPE = Base.metadata.tables["tbl_VoucherType"]
SUFFIX_PREFIX = Base.metadata.tables["tbl_SuffixPrefix"]
FINANCIAL_YEAR = Base.metadata.tables["tbl_FinancialYear"]
CONTRACT = Base.metadata.tables["VT_ContractMaster"]

RECEIVING_GROUP_NAMES = ("cash-in hand", "bank account", "bank od a/c")
PARTY_GROUP_NAMES = ("sundry creditors", "sundry debtors")
RECEIPT_TYPE_NAME = "receipt voucher"


def _group_tree(names, name):
    tree = select(ACCOUNT_GROUP.c.accountGroupId).where(
        func.lower(ACCOUNT_GROUP.c.accountGroupName).in_(names)
    ).cte(name=name, recursive=True)
    return tree.union_all(
        select(ACCOUNT_GROUP.c.accountGroupId).where(ACCOUNT_GROUP.c.groupUnder == tree.c.accountGroupId)
    )


def list_voucher_types(db):
    return db.execute(
        select(VOUCHER_TYPE).where(
            func.lower(VOUCHER_TYPE.c.typeOfVoucher) == RECEIPT_TYPE_NAME,
            or_(VOUCHER_TYPE.c.isActive == True, VOUCHER_TYPE.c.isActive.is_(None)),
        ).order_by(VOUCHER_TYPE.c.voucherTypeName, VOUCHER_TYPE.c.voucherTypeId)
    ).mappings().all()


def get_voucher_type(db, voucher_type_id):
    return db.execute(
        select(VOUCHER_TYPE).where(
            VOUCHER_TYPE.c.voucherTypeId == voucher_type_id,
            func.lower(VOUCHER_TYPE.c.typeOfVoucher) == RECEIPT_TYPE_NAME,
            or_(VOUCHER_TYPE.c.isActive == True, VOUCHER_TYPE.c.isActive.is_(None)),
        )
    ).mappings().first()


def get_financial_year(db, voucher_date):
    return db.execute(
        select(FINANCIAL_YEAR).where(
            FINANCIAL_YEAR.c.fromDate <= voucher_date,
            FINANCIAL_YEAR.c.toDate >= voucher_date,
        )
    ).mappings().first()


def get_suffix_prefix(db, voucher_type_id, voucher_date):
    return db.execute(
        select(SUFFIX_PREFIX).where(
            SUFFIX_PREFIX.c.voucherTypeId == voucher_type_id,
            SUFFIX_PREFIX.c.fromDate <= voucher_date,
            SUFFIX_PREFIX.c.toDate >= voucher_date,
        ).order_by(SUFFIX_PREFIX.c.suffixprefixId.desc())
    ).mappings().first()


def lock_numbering_scope(db, voucher_type_id):
    if db.bind is not None and db.bind.dialect.name == "mssql":
        db.execute(text(
            "SELECT voucherTypeId FROM tbl_VoucherType WITH (UPDLOCK, HOLDLOCK) "
            "WHERE voucherTypeId = :voucher_type_id"
        ), {"voucher_type_id": voucher_type_id}).first()


def next_internal_voucher_number(db, voucher_type_id, start_index=1):
    if db.bind is not None and db.bind.dialect.name == "mssql":
        current = db.execute(text(
            "SELECT MAX(TRY_CONVERT(bigint, voucherNo)) FROM tbl_ReceiptMaster "
            "WHERE voucherTypeId = :voucher_type_id"
        ), {"voucher_type_id": voucher_type_id}).scalar_one_or_none()
    else:
        current = db.execute(
            select(func.max(cast(RECEIPT_MASTER.c.voucherNo, Integer))).where(
                RECEIPT_MASTER.c.voucherTypeId == voucher_type_id,
                RECEIPT_MASTER.c.voucherNo.is_not(None),
            )
        ).scalar_one_or_none()
    return max(int(current or 0) + 1, int(start_index or 1))


def voucher_number_exists(db, voucher_type_id, invoice_no, exclude_master_id=None):
    query = select(RECEIPT_MASTER.c.receiptMasterId).where(
        RECEIPT_MASTER.c.voucherTypeId == voucher_type_id,
        RECEIPT_MASTER.c.invoiceNo == invoice_no,
    )
    if exclude_master_id is not None:
        query = query.where(RECEIPT_MASTER.c.receiptMasterId != exclude_master_id)
    return db.execute(query.limit(1)).first() is not None


def get_master_by_idempotency_key(db, voucher_type_id, idempotency_key):
    if not idempotency_key:
        return None
    master_id = db.execute(select(RECEIPT_MASTER.c.receiptMasterId).where(
        RECEIPT_MASTER.c.voucherTypeId == voucher_type_id,
        RECEIPT_MASTER.c.extra1 == idempotency_key,
    )).scalars().first()
    return get_master(db, int(master_id)) if master_id is not None else None


def list_receiving_accounts(db):
    groups = _group_tree(RECEIVING_GROUP_NAMES, "receipt_receiving_groups")
    return db.execute(
        select(
            LEDGER.c.ledgerId, LEDGER.c.ledgerName, LEDGER.c.accountGroupId,
            ACCOUNT_GROUP.c.accountGroupName,
        ).select_from(
            LEDGER.outerjoin(ACCOUNT_GROUP, ACCOUNT_GROUP.c.accountGroupId == LEDGER.c.accountGroupId)
        ).where(
            LEDGER.c.accountGroupId.in_(select(groups.c.accountGroupId)),
            LEDGER.c.ledgerName.is_not(None),
        ).order_by(LEDGER.c.ledgerName, LEDGER.c.ledgerId)
    ).mappings().all()


def get_receiving_account(db, ledger_id):
    groups = _group_tree(RECEIVING_GROUP_NAMES, "selected_receipt_receiving_groups")
    return db.execute(
        select(
            LEDGER.c.ledgerId, LEDGER.c.ledgerName, LEDGER.c.accountGroupId,
            LEDGER.c.openingBalance, LEDGER.c.crOrDr, LEDGER.c.billByBill,
            ACCOUNT_GROUP.c.accountGroupName,
        ).select_from(
            LEDGER.outerjoin(ACCOUNT_GROUP, ACCOUNT_GROUP.c.accountGroupId == LEDGER.c.accountGroupId)
        ).where(
            LEDGER.c.ledgerId == ledger_id,
            LEDGER.c.accountGroupId.in_(select(groups.c.accountGroupId)),
        )
    ).mappings().first()


def _ledger_query(ledger_id=None, search=None, limit=None, party_only=False):
    party_groups = _group_tree(PARTY_GROUP_NAMES, "receipt_party_groups")
    is_party = case((and_(
        LEDGER.c.billByBill == True,
        LEDGER.c.accountGroupId.in_(select(party_groups.c.accountGroupId)),
    ), True), else_=False)
    query = select(
        LEDGER.c.ledgerId, LEDGER.c.ledgerName, LEDGER.c.accountGroupId,
        LEDGER.c.billByBill, ACCOUNT_GROUP.c.accountGroupName,
        is_party.label("isParty"),
    ).select_from(
        LEDGER.outerjoin(ACCOUNT_GROUP, ACCOUNT_GROUP.c.accountGroupId == LEDGER.c.accountGroupId)
    ).where(LEDGER.c.ledgerName.is_not(None))
    if ledger_id is not None:
        query = query.where(LEDGER.c.ledgerId == ledger_id)
    if search:
        query = query.where(LEDGER.c.ledgerName.icontains(search, autoescape=True))
    if party_only:
        query = query.where(is_party == True)
    query = query.order_by(LEDGER.c.ledgerName, LEDGER.c.ledgerId)
    if limit is not None:
        query = query.limit(limit)
    return query


def get_detail_account(db, ledger_id):
    return db.execute(_ledger_query(ledger_id=ledger_id)).mappings().first()


def list_detail_accounts(db, search=None, limit=100):
    return db.execute(_ledger_query(search=search, limit=limit)).mappings().all()


def list_party_ledgers(db, search=None, limit=100):
    return db.execute(
        _ledger_query(search=search, limit=limit, party_only=True)
    ).mappings().all()


def list_party_contracts(db, ledger_id):
    return db.execute(
        select(CONTRACT.c.ContractId, CONTRACT.c.ContractRefNo).where(
            CONTRACT.c.CustomerId == ledger_id,
        ).order_by(CONTRACT.c.ContractRefNo, CONTRACT.c.ContractId)
    ).mappings().all()


def party_contract_exists(db, ledger_id, contract_id):
    return db.execute(select(CONTRACT.c.ContractId).where(
        CONTRACT.c.ContractId == contract_id,
        CONTRACT.c.CustomerId == ledger_id,
    ).limit(1)).first() is not None


def get_exchange_rate(db, exchange_rate_id, voucher_date):
    return db.execute(
        select(
            EXCHANGE_RATE, CURRENCY.c.currencyName, CURRENCY.c.currencySymbol,
            CURRENCY.c.noOfDecimalPlaces,
        ).select_from(
            EXCHANGE_RATE.outerjoin(CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId)
        ).where(
            EXCHANGE_RATE.c.exchangeRateId == exchange_rate_id,
            or_(EXCHANGE_RATE.c.date.is_(None), EXCHANGE_RATE.c.date <= voucher_date),
        )
    ).mappings().first()


def list_exchange_rates(db, voucher_date):
    latest_dates = select(
        EXCHANGE_RATE.c.currencyId.label("currencyId"),
        func.max(EXCHANGE_RATE.c.date).label("rateDate"),
    ).where(
        or_(EXCHANGE_RATE.c.date.is_(None), EXCHANGE_RATE.c.date <= voucher_date)
    ).group_by(EXCHANGE_RATE.c.currencyId).subquery()
    return db.execute(
        select(
            EXCHANGE_RATE.c.exchangeRateId, EXCHANGE_RATE.c.currencyId,
            EXCHANGE_RATE.c.date, EXCHANGE_RATE.c.rate,
            CURRENCY.c.currencyName, CURRENCY.c.currencySymbol,
        ).select_from(
            EXCHANGE_RATE.join(latest_dates, and_(
                latest_dates.c.currencyId == EXCHANGE_RATE.c.currencyId,
                or_(
                    latest_dates.c.rateDate == EXCHANGE_RATE.c.date,
                    and_(latest_dates.c.rateDate.is_(None), EXCHANGE_RATE.c.date.is_(None)),
                ),
            )).outerjoin(CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId)
        ).order_by(CURRENCY.c.currencyName, EXCHANGE_RATE.c.exchangeRateId.desc())
    ).mappings().all()


def get_master(db, receipt_master_id, for_update=False):
    if for_update and db.bind is not None and db.bind.dialect.name == "mssql":
        db.execute(text(
            "SELECT receiptMasterId FROM tbl_ReceiptMaster WITH (UPDLOCK, HOLDLOCK) "
            "WHERE receiptMasterId = :receipt_master_id"
        ), {"receipt_master_id": receipt_master_id}).first()
    query = select(
        RECEIPT_MASTER,
        LEDGER.c.ledgerName.label("receivingLedgerName"),
        VOUCHER_TYPE.c.voucherTypeName,
    ).select_from(
        RECEIPT_MASTER.outerjoin(LEDGER, LEDGER.c.ledgerId == RECEIPT_MASTER.c.ledgerId)
        .outerjoin(VOUCHER_TYPE, VOUCHER_TYPE.c.voucherTypeId == RECEIPT_MASTER.c.voucherTypeId)
    ).where(RECEIPT_MASTER.c.receiptMasterId == receipt_master_id)
    if for_update and (db.bind is None or db.bind.dialect.name != "mssql"):
        query = query.with_for_update()
    return db.execute(query).mappings().first()


def get_details(db, receipt_master_id):
    return db.execute(
        select(
            RECEIPT_DETAILS,
            LEDGER.c.ledgerName, LEDGER.c.billByBill,
            EXCHANGE_RATE.c.rate.label("exchangeRate"), EXCHANGE_RATE.c.currencyId,
            CURRENCY.c.currencyName, CURRENCY.c.currencySymbol,
        ).select_from(
            RECEIPT_DETAILS.outerjoin(LEDGER, LEDGER.c.ledgerId == RECEIPT_DETAILS.c.ledgerId)
            .outerjoin(EXCHANGE_RATE, EXCHANGE_RATE.c.exchangeRateId == RECEIPT_DETAILS.c.exchangeRateId)
            .outerjoin(CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId)
        ).where(RECEIPT_DETAILS.c.receiptMasterId == receipt_master_id)
        .order_by(RECEIPT_DETAILS.c.receiptDetailsId)
    ).mappings().all()


def _voucher_allocation_condition(table, voucher_type_id, voucher_no):
    return or_(
        and_(
            table.c.againstVoucherTypeId == voucher_type_id,
            table.c.againstVoucherNo == voucher_no,
            table.c.referenceType == "Against",
        ),
        and_(
            table.c.voucherTypeId == voucher_type_id,
            table.c.voucherNo == voucher_no,
            table.c.referenceType.in_(("New", "OnAccount")),
        ),
    )


def get_allocations(db, voucher_type_id, voucher_no, posted, ledger_ids=None):
    table = PARTY_BALANCE if posted else PARTY_BALANCE_UNPOSTED
    source_type = table.c.voucherTypeId
    query = select(
        table,
        VOUCHER_TYPE.c.voucherTypeName.label("sourceVoucherTypeName"),
        EXCHANGE_RATE.c.rate.label("exchangeRate"), EXCHANGE_RATE.c.currencyId,
        CURRENCY.c.currencyName, CURRENCY.c.currencySymbol,
    ).select_from(
        table.outerjoin(VOUCHER_TYPE, VOUCHER_TYPE.c.voucherTypeId == source_type)
        .outerjoin(EXCHANGE_RATE, EXCHANGE_RATE.c.exchangeRateId == table.c.exchangeRateId)
        .outerjoin(CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId)
    ).where(_voucher_allocation_condition(table, voucher_type_id, voucher_no))
    if ledger_ids is not None:
        if not ledger_ids:
            return []
        query = query.where(table.c.ledgerId.in_(ledger_ids))
    return db.execute(query.order_by(table.c.partyBalanceId)).mappings().all()


def list_vouchers(db, from_date=None, to_date_exclusive=None, voucher_no=None,
                  voucher_type_id=None, receiving_ledger_id=None, amount=None,
                  party_ledger_id=None, cheque_no=None, posted=None,
                  offset=0, limit=10):
    query = select(
        RECEIPT_MASTER.c.receiptMasterId,
        RECEIPT_MASTER.c.voucherNo, RECEIPT_MASTER.c.invoiceNo,
        RECEIPT_MASTER.c.voucherTypeId, VOUCHER_TYPE.c.voucherTypeName,
        RECEIPT_MASTER.c.date.label("voucherDate"),
        RECEIPT_MASTER.c.ledgerId.label("receivingLedgerId"),
        LEDGER.c.ledgerName.label("receivingLedgerName"),
        RECEIPT_MASTER.c.totalAmount, RECEIPT_MASTER.c.narration,
        RECEIPT_MASTER.c.isPosted,
    ).select_from(
        RECEIPT_MASTER.outerjoin(LEDGER, LEDGER.c.ledgerId == RECEIPT_MASTER.c.ledgerId)
        .outerjoin(VOUCHER_TYPE, VOUCHER_TYPE.c.voucherTypeId == RECEIPT_MASTER.c.voucherTypeId)
    )
    if from_date is not None:
        query = query.where(RECEIPT_MASTER.c.date >= from_date)
    if to_date_exclusive is not None:
        query = query.where(RECEIPT_MASTER.c.date < to_date_exclusive)
    if voucher_no:
        query = query.where(or_(
            RECEIPT_MASTER.c.invoiceNo.icontains(voucher_no, autoescape=True),
            RECEIPT_MASTER.c.voucherNo.icontains(voucher_no, autoescape=True),
        ))
    if voucher_type_id is not None:
        query = query.where(RECEIPT_MASTER.c.voucherTypeId == voucher_type_id)
    if receiving_ledger_id is not None:
        query = query.where(RECEIPT_MASTER.c.ledgerId == receiving_ledger_id)
    if amount is not None:
        query = query.where(RECEIPT_MASTER.c.totalAmount == amount)
    if party_ledger_id is not None:
        query = query.where(select(RECEIPT_DETAILS.c.receiptDetailsId).where(
            RECEIPT_DETAILS.c.receiptMasterId == RECEIPT_MASTER.c.receiptMasterId,
            RECEIPT_DETAILS.c.ledgerId == party_ledger_id,
        ).exists())
    if cheque_no:
        query = query.where(select(RECEIPT_DETAILS.c.receiptDetailsId).where(
            RECEIPT_DETAILS.c.receiptMasterId == RECEIPT_MASTER.c.receiptMasterId,
            RECEIPT_DETAILS.c.chequeNo.icontains(cheque_no, autoescape=True),
        ).exists())
    if posted is not None:
        query = query.where(RECEIPT_MASTER.c.isPosted == posted)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    rows = db.execute(
        query.order_by(RECEIPT_MASTER.c.date.desc(), RECEIPT_MASTER.c.receiptMasterId.desc())
        .offset(offset).limit(limit)
    ).mappings().all()
    items = [dict(row) for row in rows]
    master_ids = [row["receiptMasterId"] for row in items]
    names_by_master = {master_id: [] for master_id in master_ids}
    if master_ids:
        detail_rows = db.execute(select(
            RECEIPT_DETAILS.c.receiptMasterId,
            LEDGER.c.ledgerName,
        ).select_from(
            RECEIPT_DETAILS.outerjoin(LEDGER, LEDGER.c.ledgerId == RECEIPT_DETAILS.c.ledgerId)
        ).where(
            RECEIPT_DETAILS.c.receiptMasterId.in_(master_ids)
        ).order_by(
            RECEIPT_DETAILS.c.receiptMasterId,
            RECEIPT_DETAILS.c.receiptDetailsId,
        )).mappings().all()
        for detail in detail_rows:
            names_by_master[detail["receiptMasterId"]].append(
                detail["ledgerName"] or "Unnamed ledger"
            )
    for item in items:
        item["detailAccountNames"] = names_by_master[item["receiptMasterId"]]
        item["lineCount"] = len(item["detailAccountNames"])
    return items, total


def _open_reference_query(ledger_id, voucher_type_id=None, voucher_no=None):
    balance = (func.coalesce(func.sum(PARTY_BALANCE.c.debit), 0)
               - func.coalesce(func.sum(PARTY_BALANCE.c.credit), 0))
    grouped = select(
        PARTY_BALANCE.c.ledgerId,
        PARTY_BALANCE.c.voucherTypeId.label("sourceVoucherTypeId"),
        PARTY_BALANCE.c.voucherNo.label("sourceVoucherNo"),
        func.max(PARTY_BALANCE.c.invoiceNo).label("sourceInvoiceNo"),
        balance.label("pendingAmount"),
        func.max(PARTY_BALANCE.c.exchangeRateId).label("exchangeRateId"),
        func.max(PARTY_BALANCE.c.contractId).label("contractId"),
    ).where(PARTY_BALANCE.c.ledgerId == ledger_id)
    if voucher_type_id is not None and voucher_no is not None:
        grouped = grouped.where(not_(and_(
            func.coalesce(PARTY_BALANCE.c.againstVoucherTypeId, -1) == voucher_type_id,
            func.coalesce(PARTY_BALANCE.c.againstVoucherNo, "") == voucher_no,
        )))
    grouped = grouped.group_by(
        PARTY_BALANCE.c.ledgerId, PARTY_BALANCE.c.voucherTypeId, PARTY_BALANCE.c.voucherNo,
    ).having(balance > 0).subquery()
    return select(
        grouped,
        VOUCHER_TYPE.c.voucherTypeName.label("sourceVoucherTypeName"),
        EXCHANGE_RATE.c.rate.label("exchangeRate"), EXCHANGE_RATE.c.currencyId,
        CURRENCY.c.currencyName, CURRENCY.c.currencySymbol,
    ).select_from(
        grouped.outerjoin(VOUCHER_TYPE, VOUCHER_TYPE.c.voucherTypeId == grouped.c.sourceVoucherTypeId)
        .outerjoin(EXCHANGE_RATE, EXCHANGE_RATE.c.exchangeRateId == grouped.c.exchangeRateId)
        .outerjoin(CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId)
    )


def list_open_references(db, ledger_id, voucher_type_id=None, voucher_no=None):
    return db.execute(
        _open_reference_query(ledger_id, voucher_type_id, voucher_no)
        .order_by(VOUCHER_TYPE.c.voucherTypeName, text("sourceInvoiceNo"))
    ).mappings().all()


def lock_open_reference(db, ledger_id, source_voucher_type_id, source_voucher_no):
    if db.bind is not None and db.bind.dialect.name == "mssql":
        db.execute(text(
            "SELECT partyBalanceId FROM tbl_PartyBalance WITH (UPDLOCK, HOLDLOCK) "
            "WHERE ledgerId=:ledger_id AND voucherTypeId=:voucher_type_id AND voucherNo=:voucher_no"
        ), {
            "ledger_id": ledger_id,
            "voucher_type_id": source_voucher_type_id,
            "voucher_no": source_voucher_no,
        }).all()
    query = _open_reference_query(ledger_id).where(
        text("sourceVoucherTypeId = :source_voucher_type_id"),
        text("sourceVoucherNo = :source_voucher_no"),
    )
    return db.execute(query, {
        "source_voucher_type_id": source_voucher_type_id,
        "source_voucher_no": source_voucher_no,
    }).mappings().first()


def insert_master(db, values):
    result = db.execute(RECEIPT_MASTER.insert().values(**values))
    return int(result.inserted_primary_key[0])


def update_master(db, receipt_master_id, values):
    return db.execute(RECEIPT_MASTER.update().where(
        RECEIPT_MASTER.c.receiptMasterId == receipt_master_id
    ).values(**values)).rowcount


def insert_detail(db, values):
    result = db.execute(RECEIPT_DETAILS.insert().values(**values))
    return int(result.inserted_primary_key[0])


def update_detail(db, detail_id, receipt_master_id, values):
    return db.execute(RECEIPT_DETAILS.update().where(
        RECEIPT_DETAILS.c.receiptDetailsId == detail_id,
        RECEIPT_DETAILS.c.receiptMasterId == receipt_master_id,
    ).values(**values)).rowcount


def delete_details(db, receipt_master_id, detail_ids=None):
    query = RECEIPT_DETAILS.delete().where(RECEIPT_DETAILS.c.receiptMasterId == receipt_master_id)
    if detail_ids is not None:
        if not detail_ids:
            return 0
        query = query.where(RECEIPT_DETAILS.c.receiptDetailsId.in_(detail_ids))
    return db.execute(query).rowcount


def insert_draft_allocation(db, values):
    return int(db.execute(
        PARTY_BALANCE_UNPOSTED.insert().values(**values).returning(PARTY_BALANCE_UNPOSTED.c.partyBalanceId)
    ).scalar_one())


def update_draft_allocation(db, party_balance_id, values):
    return db.execute(PARTY_BALANCE_UNPOSTED.update().where(
        PARTY_BALANCE_UNPOSTED.c.partyBalanceId == party_balance_id
    ).values(**values)).rowcount


def delete_draft_allocations(db, voucher_type_id, voucher_no, allocation_ids=None):
    query = PARTY_BALANCE_UNPOSTED.delete().where(
        _voucher_allocation_condition(PARTY_BALANCE_UNPOSTED, voucher_type_id, voucher_no)
    )
    if allocation_ids is not None:
        if not allocation_ids:
            return 0
        query = query.where(PARTY_BALANCE_UNPOSTED.c.partyBalanceId.in_(allocation_ids))
    return db.execute(query).rowcount


def insert_active_allocation(db, values):
    result = db.execute(PARTY_BALANCE.insert().values(**values))
    return int(result.inserted_primary_key[0])


def delete_active_allocations(db, voucher_type_id, voucher_no):
    return db.execute(PARTY_BALANCE.delete().where(
        _voucher_allocation_condition(PARTY_BALANCE, voucher_type_id, voucher_no)
    )).rowcount


def has_external_party_reference(db, voucher_type_id, voucher_no):
    for table in (PARTY_BALANCE, PARTY_BALANCE_UNPOSTED):
        if db.execute(select(table.c.partyBalanceId).where(
            table.c.voucherTypeId == voucher_type_id,
            table.c.voucherNo == voucher_no,
            table.c.againstVoucherTypeId.is_not(None),
            table.c.againstVoucherTypeId != 0,
            table.c.againstVoucherNo.is_not(None),
            table.c.againstVoucherNo != "0",
        ).limit(1)).first() is not None:
            return True
    return False


def insert_posting(db, values):
    result = db.execute(LEDGER_POSTING.insert().values(**values))
    return int(result.inserted_primary_key[0])


def delete_postings(db, voucher_type_id, voucher_no):
    return db.execute(LEDGER_POSTING.delete().where(
        LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
        LEDGER_POSTING.c.voucherNo == voucher_no,
    )).rowcount


def posting_totals(db, voucher_type_id, voucher_no):
    return db.execute(select(
        func.count().label("rowCount"),
        func.coalesce(func.sum(LEDGER_POSTING.c.debit), 0).label("debit"),
        func.coalesce(func.sum(LEDGER_POSTING.c.credit), 0).label("credit"),
    ).where(
        LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
        LEDGER_POSTING.c.voucherNo == voucher_no,
    )).mappings().one()


def has_bank_reconciliation(db, voucher_type_id, voucher_no):
    return db.execute(select(BANK_RECONCILIATION.c.reconcileId).select_from(
        BANK_RECONCILIATION.join(
            LEDGER_POSTING,
            LEDGER_POSTING.c.ledgerPostingId == BANK_RECONCILIATION.c.ledgerPostingId,
        )
    ).where(
        LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
        LEDGER_POSTING.c.voucherNo == voucher_no,
    ).limit(1)).first() is not None


def delete_master(db, receipt_master_id):
    return db.execute(RECEIPT_MASTER.delete().where(
        RECEIPT_MASTER.c.receiptMasterId == receipt_master_id
    )).rowcount
