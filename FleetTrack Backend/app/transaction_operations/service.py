from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError
from . import repository as r


def period(start, end):
    if end < start:
        raise HTTPException(422, 'To date must not precede from date')
    return datetime.combine(start, datetime.min.time()), datetime.combine(end + timedelta(days=1), datetime.min.time())


def reconciliation_entries(db, bank_id, start, end, status, offset, limit):
    account = r.bank(db, bank_id)
    if account is None:
        raise HTTPException(422, 'Select a bank account')
    start, end = period(start, end)
    rows, total = r.entries(db, bank_id, start, end, status, offset, limit)
    return dict(items=rows, total=total, offset=offset, limit=limit, bookBalance=r.book_balance(db, account, end))


def save_reconciliation(db, payload):
    if len({line.ledgerPostingId for line in payload.lines}) != len(payload.lines):
        raise HTTPException(422, 'A bank entry may occur only once')
    try:
        if r.bank(db, payload.bankLedgerId) is None:
            raise HTTPException(422, 'Select a bank account')
        # The legacy key is MAX+1, not an identity. Serialize all marker allocations.
        if db.bind.dialect.name == 'mssql':
            db.execute(text('SELECT reconcileId FROM tbl_BankReconciliation WITH (TABLOCKX, HOLDLOCK)')).all()
        next_id = int(db.execute(select(func.coalesce(func.max(r.RECON.c.reconcileId), 0))).scalar_one()) + 1
        for line in sorted(payload.lines, key=lambda item: item.ledgerPostingId):
            posting = db.execute(r.lock_query(db, select(r.POSTING).where(r.POSTING.c.ledgerPostingId == line.ledgerPostingId), r.POSTING)).mappings().first()
            if posting is None or int(posting['ledgerId']) != payload.bankLedgerId:
                raise HTTPException(422, 'Entry does not belong to the selected bank')
            markers = db.execute(select(r.RECON).where(r.RECON.c.ledgerPostingId == line.ledgerPostingId)).mappings().all()
            if len(markers) > 1:
                raise HTTPException(409, 'Duplicate legacy reconciliation markers require review')
            marker = markers[0] if markers else None
            old_date = marker['statementDate'] if marker else None
            if old_date != line.expectedStatementDate:
                raise HTTPException(409, 'Reconciliation changed. Refresh before saving')
            if line.statementDate and line.statementDate.date() < posting['date'].date():
                raise HTTPException(422, 'Statement date must not precede transaction date')
            if marker:
                query = r.RECON.update().values(statementDate=line.statementDate) if line.statementDate else r.RECON.delete()
                db.execute(query.where(r.RECON.c.reconcileId == marker['reconcileId']))
            elif line.statementDate:
                db.execute(r.RECON.insert().values(reconcileId=next_id, ledgerPostingId=line.ledgerPostingId, statementDate=line.statementDate, extraDate=datetime.now()))
                next_id += 1
        db.commit()
        return {'saved': len(payload.lines)}
    except Exception:
        db.rollback()
        raise


def fines(db, start=None, end=None, q=None, posted=None, offset=0, limit=25):
    query = r.fine_query()
    if start and end:
        start, end = period(start, end)
        query = query.where(r.FINE.c.FINEDATETIME >= start, r.FINE.c.FINEDATETIME < end)
    elif start:
        query = query.where(r.FINE.c.FINEDATETIME >= start)
    elif end:
        query = query.where(r.FINE.c.FINEDATETIME < end + timedelta(days=1))
    if q:
        query = query.where(r.FINE.c.TICKETNO.contains(q, autoescape=True))
    if posted is not None:
        query = query.where(func.coalesce(r.FINE.c.ISPOSTED, False) == posted)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    rows = db.execute(query.order_by(r.FINE.c.FINEDATETIME.desc(), r.FINE.c.TICKETNO).offset(offset).limit(limit)).mappings()
    return dict(items=[dict(row) for row in rows], total=total, offset=offset, limit=limit)


def save_fine(db, payload):
    try:
        vehicle = db.execute(select(r.VEHICLE).where(r.VEHICLE.c.VehicleId == payload.vehicleId)).mappings().first()
        if vehicle is None:
            raise HTTPException(422, 'Vehicle does not exist')
        tc = r.T['VT_Veh_TCNoMaster']
        traffic_file = db.execute(select(tc.c.TCNo).where(tc.c.TCNo == payload.trafficFile)).scalar_one_or_none()
        if traffic_file is None:
            raise HTTPException(422, 'Traffic file does not exist')
        if db.execute(select(r.FINE.c.TICKETNO).where(r.FINE.c.TICKETNO == payload.ticketNo)).first():
            raise HTTPException(409, 'Ticket number already exists')
        db.execute(r.FINE.insert().values(TICKETNO=payload.ticketNo, VEHICLEID=payload.vehicleId,
            TRAFFICFILEID=payload.trafficFile, FINEDATETIME=payload.fineDate, AUTHORITY=payload.authority,
            PLATEDETAILS=vehicle['PlateNo'], AMOUNT=payload.amount, BLACKPOINTS=payload.blackPoints,
            FINEDESCRIPTION=payload.description, ACKNOWLEDGMENT=payload.acknowledgment,
            DOWNLOADDATE=datetime.now(), PAID=False, ISPOSTED=False, VOUCHERNO=''))
        result = dict(db.execute(r.fine_query().where(r.FINE.c.TICKETNO == payload.ticketNo)).mappings().one())
        db.commit()
        return result
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Ticket number already exists')
    except Exception:
        db.rollback()
        raise
