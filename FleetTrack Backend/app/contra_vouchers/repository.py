from decimal import Decimal

from sqlalchemy import Integer, and_, cast, func, not_, or_, select, text

from app.generated_models.models import Base


CONTRA_MASTER = Base.metadata.tables["tbl_ContraMaster"]
CONTRA_DETAILS = Base.metadata.tables["tbl_ContraDetails"]
LEDGER_POSTING = Base.metadata.tables["tbl_LedgerPosting"]
LEDGER = Base.metadata.tables["tbl_AccountLedger"]
ACCOUNT_GROUP = Base.metadata.tables["tbl_AccountGroup"]
EXCHANGE_RATE = Base.metadata.tables["tbl_ExchangeRate"]
CURRENCY = Base.metadata.tables["tbl_Currency"]
VOUCHER_TYPE = Base.metadata.tables["tbl_VoucherType"]
SUFFIX_PREFIX = Base.metadata.tables["tbl_SuffixPrefix"]
FINANCIAL_YEAR = Base.metadata.tables["tbl_FinancialYear"]
SETTINGS = Base.metadata.tables["tbl_Settings"]
CASH_BANK_GROUP_NAMES = ("cash-in hand", "bank account", "bank od a/c")


def get_contra_voucher_type(db):
    return db.execute(
        select(VOUCHER_TYPE).where(
            func.lower(VOUCHER_TYPE.c.voucherTypeName) == "contra voucher",
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
        select(SUFFIX_PREFIX)
        .where(
            SUFFIX_PREFIX.c.voucherTypeId == voucher_type_id,
            SUFFIX_PREFIX.c.fromDate <= voucher_date,
            SUFFIX_PREFIX.c.toDate >= voucher_date,
        )
        .order_by(SUFFIX_PREFIX.c.suffixprefixId.desc())
    ).mappings().first()


def lock_numbering_scope(db, voucher_type_id):
    if db.bind is not None and db.bind.dialect.name == "mssql":
        db.execute(
            text(
                "SELECT voucherTypeId FROM tbl_VoucherType WITH (UPDLOCK, HOLDLOCK) "
                "WHERE voucherTypeId = :voucher_type_id"
            ),
            {"voucher_type_id": voucher_type_id},
        ).first()


def next_internal_voucher_number(db, voucher_type_id, start_index=1):
    if db.bind is not None and db.bind.dialect.name == "mssql":
        current = db.execute(
            text(
                "SELECT MAX(TRY_CONVERT(bigint, voucherNo)) FROM tbl_ContraMaster "
                "WHERE voucherTypeId = :voucher_type_id"
            ),
            {"voucher_type_id": voucher_type_id},
        ).scalar_one_or_none()
    else:
        current = db.execute(
            select(func.max(cast(CONTRA_MASTER.c.voucherNo, Integer))).where(
                CONTRA_MASTER.c.voucherTypeId == voucher_type_id,
                CONTRA_MASTER.c.voucherNo.is_not(None),
            )
        ).scalar_one_or_none()
    return max(int(current or 0) + 1, int(start_index or 1))


def voucher_number_exists(db, voucher_type_id, invoice_no, exclude_master_id=None):
    query = select(CONTRA_MASTER.c.contraMasterId).where(
        CONTRA_MASTER.c.voucherTypeId == voucher_type_id,
        CONTRA_MASTER.c.invoiceNo == invoice_no,
    )
    if exclude_master_id is not None:
        query = query.where(CONTRA_MASTER.c.contraMasterId != exclude_master_id)
    return db.execute(query.limit(1)).first() is not None


def get_master_by_idempotency_key(db, voucher_type_id, idempotency_key):
    if not idempotency_key:
        return None
    master_id = db.execute(
        select(CONTRA_MASTER.c.contraMasterId).where(
            CONTRA_MASTER.c.voucherTypeId == voucher_type_id,
            CONTRA_MASTER.c.extra1 == idempotency_key,
        )
    ).scalars().first()
    return get_master(db, int(master_id)) if master_id is not None else None


def eligible_account(db, ledger_id):
    return db.execute(
        select(
            LEDGER.c.ledgerId,
            LEDGER.c.ledgerName,
            LEDGER.c.accountGroupId,
            LEDGER.c.openingBalance,
            LEDGER.c.crOrDr,
            ACCOUNT_GROUP.c.accountGroupName,
        )
        .select_from(LEDGER.outerjoin(ACCOUNT_GROUP, ACCOUNT_GROUP.c.accountGroupId == LEDGER.c.accountGroupId))
        .where(
            LEDGER.c.ledgerId == ledger_id,
            func.lower(ACCOUNT_GROUP.c.accountGroupName).in_(CASH_BANK_GROUP_NAMES),
        )
    ).mappings().first()


def list_eligible_accounts(db):
    return db.execute(
        select(
            LEDGER.c.ledgerId,
            LEDGER.c.ledgerName,
            LEDGER.c.accountGroupId,
            ACCOUNT_GROUP.c.accountGroupName,
        )
        .select_from(LEDGER.outerjoin(ACCOUNT_GROUP, ACCOUNT_GROUP.c.accountGroupId == LEDGER.c.accountGroupId))
        .where(
            func.lower(ACCOUNT_GROUP.c.accountGroupName).in_(CASH_BANK_GROUP_NAMES),
            LEDGER.c.ledgerName.is_not(None),
        )
        .order_by(LEDGER.c.ledgerName, LEDGER.c.ledgerId)
    ).mappings().all()


def get_exchange_rate(db, exchange_rate_id, voucher_date):
    return db.execute(
        select(
            EXCHANGE_RATE,
            CURRENCY.c.currencyName,
            CURRENCY.c.currencySymbol,
            CURRENCY.c.noOfDecimalPlaces,
        )
        .select_from(EXCHANGE_RATE.outerjoin(CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId))
        .where(
            EXCHANGE_RATE.c.exchangeRateId == exchange_rate_id,
            or_(EXCHANGE_RATE.c.date.is_(None), EXCHANGE_RATE.c.date <= voucher_date),
        )
    ).mappings().first()


def list_exchange_rates(db, voucher_date):
    latest_dates = (
        select(
            EXCHANGE_RATE.c.currencyId.label("currencyId"),
            func.max(EXCHANGE_RATE.c.date).label("rateDate"),
        )
        .where(or_(EXCHANGE_RATE.c.date.is_(None), EXCHANGE_RATE.c.date <= voucher_date))
        .group_by(EXCHANGE_RATE.c.currencyId)
        .subquery()
    )
    return db.execute(
        select(
            EXCHANGE_RATE.c.exchangeRateId,
            EXCHANGE_RATE.c.currencyId,
            EXCHANGE_RATE.c.date,
            EXCHANGE_RATE.c.rate,
            CURRENCY.c.currencyName,
            CURRENCY.c.currencySymbol,
        )
        .select_from(
            EXCHANGE_RATE.join(
                latest_dates,
                and_(
                    latest_dates.c.currencyId == EXCHANGE_RATE.c.currencyId,
                    or_(
                        latest_dates.c.rateDate == EXCHANGE_RATE.c.date,
                        and_(latest_dates.c.rateDate.is_(None), EXCHANGE_RATE.c.date.is_(None)),
                    ),
                ),
            ).outerjoin(CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId)
        )
        .order_by(CURRENCY.c.currencyName, EXCHANGE_RATE.c.exchangeRateId.desc())
    ).mappings().all()


def get_setting(db, name):
    return db.execute(
        select(SETTINGS.c.status).where(func.lower(SETTINGS.c.settingsName) == name.lower())
    ).scalar_one_or_none()


def ledger_balance(db, ledger, exclude_voucher_type_id=None, exclude_voucher_no=None):
    posting_filter = [LEDGER_POSTING.c.ledgerId == ledger["ledgerId"]]
    if exclude_voucher_type_id is not None and exclude_voucher_no is not None:
        posting_filter.append(not_(and_(
            LEDGER_POSTING.c.voucherTypeId == exclude_voucher_type_id,
            LEDGER_POSTING.c.voucherNo == exclude_voucher_no,
        )))
    posted = db.execute(
        select(
            func.coalesce(func.sum(LEDGER_POSTING.c.debit), 0)
            - func.coalesce(func.sum(LEDGER_POSTING.c.credit), 0)
        ).where(*posting_filter)
    ).scalar_one()
    opening = Decimal(ledger["openingBalance"] or 0)
    if str(ledger["crOrDr"] or "").strip().lower() == "cr":
        opening = -opening
    return opening + Decimal(posted or 0)


def get_master(db, contra_master_id, for_update=False):
    if for_update and db.bind is not None and db.bind.dialect.name == "mssql":
        db.execute(
            text(
                "SELECT contraMasterId FROM tbl_ContraMaster WITH (UPDLOCK, HOLDLOCK) "
                "WHERE contraMasterId = :contra_master_id"
            ),
            {"contra_master_id": contra_master_id},
        ).first()
    query = (
        select(
            CONTRA_MASTER,
            LEDGER.c.ledgerName.label("headerLedgerName"),
        )
        .select_from(CONTRA_MASTER.outerjoin(LEDGER, LEDGER.c.ledgerId == CONTRA_MASTER.c.ledgerId))
        .where(CONTRA_MASTER.c.contraMasterId == contra_master_id)
    )
    if for_update and (db.bind is None or db.bind.dialect.name != "mssql"):
        query = query.with_for_update()
    return db.execute(query).mappings().first()


def get_details(db, contra_master_id):
    return db.execute(
        select(
            CONTRA_DETAILS,
            LEDGER.c.ledgerName,
            EXCHANGE_RATE.c.rate.label("exchangeRate"),
            EXCHANGE_RATE.c.currencyId,
            CURRENCY.c.currencyName,
            CURRENCY.c.currencySymbol,
        )
        .select_from(
            CONTRA_DETAILS.outerjoin(LEDGER, LEDGER.c.ledgerId == CONTRA_DETAILS.c.ledgerId)
            .outerjoin(EXCHANGE_RATE, EXCHANGE_RATE.c.exchangeRateId == CONTRA_DETAILS.c.exchangeRateId)
            .outerjoin(CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId)
        )
        .where(CONTRA_DETAILS.c.contraMasterId == contra_master_id)
        .order_by(CONTRA_DETAILS.c.contraDetailsId)
    ).mappings().all()


def list_vouchers(
    db,
    from_datetime=None,
    to_datetime_exclusive=None,
    voucher_no=None,
    ledger_id=None,
    direction=None,
    offset=0,
    limit=10,
):
    query = (
        select(
            CONTRA_MASTER.c.contraMasterId,
            CONTRA_MASTER.c.voucherNo,
            CONTRA_MASTER.c.invoiceNo,
            CONTRA_MASTER.c.date.label("voucherDate"),
            CONTRA_MASTER.c.type,
            CONTRA_MASTER.c.ledgerId.label("headerLedgerId"),
            LEDGER.c.ledgerName.label("headerLedgerName"),
            CONTRA_MASTER.c.totalAmount,
            CONTRA_MASTER.c.narration,
        )
        .select_from(CONTRA_MASTER.outerjoin(LEDGER, LEDGER.c.ledgerId == CONTRA_MASTER.c.ledgerId))
    )
    if from_datetime is not None:
        query = query.where(CONTRA_MASTER.c.date >= from_datetime)
    if to_datetime_exclusive is not None:
        query = query.where(CONTRA_MASTER.c.date < to_datetime_exclusive)
    if voucher_no:
        query = query.where(or_(
            CONTRA_MASTER.c.invoiceNo.icontains(voucher_no, autoescape=True),
            CONTRA_MASTER.c.voucherNo.icontains(voucher_no, autoescape=True),
        ))
    if ledger_id is not None:
        query = query.where(CONTRA_MASTER.c.ledgerId == ledger_id)
    if direction is not None:
        query = query.where(CONTRA_MASTER.c.type == direction)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    rows = db.execute(
        query.order_by(CONTRA_MASTER.c.date.desc(), CONTRA_MASTER.c.contraMasterId.desc())
        .offset(offset)
        .limit(limit)
    ).mappings().all()
    return rows, total


def list_offset_accounts(db, contra_master_ids):
    if not contra_master_ids:
        return []
    return db.execute(
        select(
            CONTRA_DETAILS.c.contraMasterId,
            CONTRA_DETAILS.c.contraDetailsId,
            CONTRA_DETAILS.c.ledgerId,
            LEDGER.c.ledgerName,
        )
        .select_from(CONTRA_DETAILS.outerjoin(LEDGER, LEDGER.c.ledgerId == CONTRA_DETAILS.c.ledgerId))
        .where(CONTRA_DETAILS.c.contraMasterId.in_(contra_master_ids))
        .order_by(CONTRA_DETAILS.c.contraMasterId, CONTRA_DETAILS.c.contraDetailsId)
    ).mappings().all()


def insert_master(db, values):
    result = db.execute(CONTRA_MASTER.insert().values(**values))
    return int(result.inserted_primary_key[0])


def update_master(db, contra_master_id, values):
    result = db.execute(
        CONTRA_MASTER.update().where(CONTRA_MASTER.c.contraMasterId == contra_master_id).values(**values)
    )
    return result.rowcount


def insert_detail(db, values):
    result = db.execute(CONTRA_DETAILS.insert().values(**values))
    return int(result.inserted_primary_key[0])


def update_detail(db, detail_id, contra_master_id, values):
    result = db.execute(
        CONTRA_DETAILS.update().where(
            CONTRA_DETAILS.c.contraDetailsId == detail_id,
            CONTRA_DETAILS.c.contraMasterId == contra_master_id,
        ).values(**values)
    )
    return result.rowcount


def delete_details(db, contra_master_id, detail_ids=None):
    query = CONTRA_DETAILS.delete().where(CONTRA_DETAILS.c.contraMasterId == contra_master_id)
    if detail_ids is not None:
        if not detail_ids:
            return 0
        query = query.where(CONTRA_DETAILS.c.contraDetailsId.in_(detail_ids))
    return db.execute(query).rowcount


def insert_posting(db, values):
    result = db.execute(LEDGER_POSTING.insert().values(**values))
    return int(result.inserted_primary_key[0])


def update_detail_posting(db, detail_id, voucher_type_id, voucher_no, values):
    return db.execute(
        LEDGER_POSTING.update().where(
            LEDGER_POSTING.c.detailsId == detail_id,
            LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
            LEDGER_POSTING.c.voucherNo == voucher_no,
        ).values(**values)
    ).rowcount


def update_balancing_posting(db, voucher_type_id, voucher_no, values):
    return db.execute(
        LEDGER_POSTING.update().where(
            LEDGER_POSTING.c.detailsId == 0,
            LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
            LEDGER_POSTING.c.voucherNo == voucher_no,
        ).values(**values)
    ).rowcount


def delete_postings(db, voucher_type_id, voucher_no, detail_ids=None):
    query = LEDGER_POSTING.delete().where(
        LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
        LEDGER_POSTING.c.voucherNo == voucher_no,
    )
    if detail_ids is not None:
        if not detail_ids:
            return 0
        query = query.where(LEDGER_POSTING.c.detailsId.in_(detail_ids))
    return db.execute(query).rowcount


def delete_master(db, contra_master_id):
    return db.execute(
        CONTRA_MASTER.delete().where(CONTRA_MASTER.c.contraMasterId == contra_master_id)
    ).rowcount


def count_postings(db, voucher_type_id, voucher_no):
    return db.execute(
        select(func.count()).select_from(LEDGER_POSTING).where(
            LEDGER_POSTING.c.voucherTypeId == voucher_type_id,
            LEDGER_POSTING.c.voucherNo == voucher_no,
        )
    ).scalar_one()
