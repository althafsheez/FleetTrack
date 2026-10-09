from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy import select, func
from .repository import T


def base_query():
    m, l, v, e = (T[name] for name in ('tbl_SalesMaster', 'tbl_AccountLedger', 'tbl_VoucherType', 'tbl_Employee'))
    return select(m.c.salesMasterId.label('id'), m.c.invoiceNo, m.c.date, m.c.ledgerId,
        l.c.ledgerName.label('customer'), v.c.voucherTypeName, m.c.grandTotal, m.c.taxAmount,
        m.c.lpoNo, m.c.narration, m.c.vehicleNos, m.c.isPosted, m.c.contractId,
        m.c.trafficFineNo, m.c.extra1.label('location'), e.c.employeeName.label('salesperson')
    ).select_from(m.outerjoin(l, l.c.ledgerId == m.c.ledgerId)
        .outerjoin(v, v.c.voucherTypeId == m.c.voucherTypeId)
        .outerjoin(e, e.c.employeeId == m.c.employeeId))


def register(db, start=None, end=None, invoice=None, ledger=None, voucher=None, contract=None,
             fine=None, location=None, posted=None, offset=0, limit=25, identities=None):
    m = T['tbl_SalesMaster']
    query = base_query()
    if identities:
        query = query.where(m.c.salesMasterId.in_(identities))
    if start:
        query = query.where(m.c.date >= start)
    if end:
        query = query.where(m.c.date < end + timedelta(days=1))
    for column, value in [(m.c.invoiceNo, invoice), (m.c.ledgerId, ledger), (m.c.voucherTypeId, voucher),
                          (m.c.contractId, contract), (m.c.trafficFineNo, fine), (m.c.extra1, location)]:
        if value is not None and value != '':
            query = query.where(column == value)
    if posted is not None:
        query = query.where(func.coalesce(m.c.isPosted, False) == posted)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    items = [dict(row) for row in db.execute(query.order_by(m.c.salesMasterId.desc()).offset(offset).limit(limit)).mappings()]
    return dict(items=items, total=total, offset=offset, limit=limit)


def detail(db, identity):
    m, d = T['tbl_SalesMaster'], T['tbl_SalesDetails']
    header = db.execute(base_query().where(m.c.salesMasterId == identity)).mappings().first()
    if header is None:
        raise HTTPException(404, 'Invoice not found')
    lines = db.execute(select(d).where(d.c.salesMasterId == identity).order_by(d.c.salesDetailsId)).mappings()
    return dict(header=dict(header), lines=[dict(row) for row in lines])


def salik(db, identity):
    m, d, toll = T['tbl_SalesMaster'], T['tbl_SalesDetails'], T['Salik_Toll']
    header = detail(db, identity)['header']
    invoice = header['invoiceNo']
    if not invoice:
        return []
    if db.execute(select(func.count()).select_from(m).where(m.c.invoiceNo == invoice)).scalar_one() != 1:
        raise HTTPException(409, 'Invoice number is ambiguous; Salik details cannot be assigned safely')
    rates = db.execute(select(d.c.rate).where(d.c.salesMasterId == identity, d.c.itemTypeId == 7).distinct()).scalars().all()
    if len(rates) > 1:
        raise HTTPException(409, 'Multiple Salik administration rates require review')
    admin_rate = rates[0] if rates and rates[0] else 0
    query = select(toll.c.TRANSID.label('transaction'), toll.c.DATEANDTIME.label('date'),
        toll.c.PLATENO.label('vehicle'), toll.c.LOCATION.label('location'), toll.c.DIRECTION.label('direction'),
        toll.c.AMOUNT.label('tollAmount'), (toll.c.AMOUNT + admin_rate).label('amount')
    ).where(toll.c.INVOICENO == invoice).order_by(toll.c.DATEANDTIME, toll.c.TRANSID)
    return [dict(row) for row in db.execute(query).mappings()]
