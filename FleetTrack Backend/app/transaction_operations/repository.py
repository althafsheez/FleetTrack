from sqlalchemy import select, func, text
from app.generated_models.models import Base

T = Base.metadata.tables
POSTING = T['tbl_LedgerPosting']
RECON = T['tbl_BankReconciliation']
LEDGER = T['tbl_AccountLedger']
FINE = T['Traffic_Fine']
VEHICLE = T['VT_Veh_VehicleMaster']


def lock_query(db, query, table):
    if db.bind.dialect.name == 'mssql':
        return query.with_hint(table, 'WITH (UPDLOCK, HOLDLOCK)', dialect_name='mssql')
    return query


def bank(db, ledger_id):
    return db.execute(select(LEDGER).where(LEDGER.c.ledgerId == ledger_id, LEDGER.c.accountGroupId == 28)).mappings().first()


def bank_accounts(db):
    return [dict(r) for r in db.execute(select(LEDGER.c.ledgerId.label('id'), LEDGER.c.ledgerName.label('name')).where(LEDGER.c.accountGroupId == 28).order_by(LEDGER.c.ledgerName)).mappings()]


def entries(db, bank_id, start, end, status, offset, limit):
    vt = T['tbl_VoucherType']
    query = select(POSTING.c.ledgerPostingId, POSTING.c.date, POSTING.c.voucherNo, vt.c.voucherTypeName,
                   POSTING.c.chequeNo, POSTING.c.chequeDate, POSTING.c.debit.label('deposit'),
                   POSTING.c.credit.label('withdrawal'), RECON.c.statementDate).select_from(
        POSTING.outerjoin(RECON, RECON.c.ledgerPostingId == POSTING.c.ledgerPostingId)
        .outerjoin(vt, vt.c.voucherTypeId == POSTING.c.voucherTypeId)).where(POSTING.c.ledgerId == bank_id)
    date_column = RECON.c.statementDate if status == 'reconciled' else POSTING.c.date
    query = query.where(date_column >= start, date_column < end)
    if status == 'reconciled':
        query = query.where(RECON.c.reconcileId.is_not(None))
    if status == 'unreconciled':
        query = query.where(RECON.c.reconcileId.is_(None))
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    rows = db.execute(query.order_by(POSTING.c.date, POSTING.c.ledgerPostingId).offset(offset).limit(limit)).mappings()
    return [dict(r) for r in rows], total


def book_balance(db, account, end):
    movement = db.execute(select(func.coalesce(func.sum(POSTING.c.debit - POSTING.c.credit), 0)).where(
        POSTING.c.ledgerId == account['ledgerId'], POSTING.c.date < end)).scalar_one()
    opening = account['openingBalance'] or 0
    return movement + (-opening if str(account['crOrDr']).lower() == 'cr' else opening)


def fine_query():
    return select(FINE.c.TICKETNO.label('ticketNo'), FINE.c.VEHICLEID.label('vehicleId'),
                  VEHICLE.c.PlateNo.label('vehicle'), FINE.c.TRAFFICFILEID.label('trafficFile'),
                  FINE.c.FINEDATETIME.label('fineDate'), FINE.c.AUTHORITY.label('authority'),
                  FINE.c.AMOUNT.label('amount'), FINE.c.BLACKPOINTS.label('blackPoints'),
                  FINE.c.FINEDESCRIPTION.label('description'), FINE.c.ACKNOWLEDGMENT.label('acknowledgment'),
                  FINE.c.ISPOSTED.label('isPosted'), FINE.c.PAID.label('isPaid')).select_from(
        FINE.outerjoin(VEHICLE, VEHICLE.c.VehicleId == FINE.c.VEHICLEID))
