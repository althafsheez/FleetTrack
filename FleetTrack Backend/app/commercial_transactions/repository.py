from dataclasses import dataclass
from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy import select, func, text, or_
from app.generated_models.models import Base
from app.transaction_operations.repository import lock_query

T = Base.metadata.tables


@dataclass(frozen=True)
class Document:
    master: str
    detail: str
    key: str
    detail_key: str
    voucher_name: str | None
    tax: str | None = None
    date_key: str = 'date'
    number_key: str = 'invoiceNo'


DOCUMENTS = {
    'purchase-orders': Document('tbl_PurchaseOrderMaster', 'tbl_PurchaseOrderDetails', 'purchaseOrderMasterId', 'purchaseOrderDetailsId', 'Purchase Order'),
    'sales-quotations': Document('tbl_SalesQuotationMaster', 'tbl_SalesQuotationDetails', 'quotationMasterId', 'quotationDetailsId', 'Sales Quotation'),
    'purchase-invoices': Document('tbl_PurchaseMaster', 'tbl_PurchaseDetails', 'purchaseMasterId', 'purchaseDetailsId', 'Purchase Invoice', 'tbl_PurchaseBillTax'),
    'credit-notes': Document('tbl_SalesReturnMaster', 'tbl_SalesReturnDetails', 'salesReturnMasterId', 'salesReturnDetailsId', 'Credit Note (Invoice)', 'tbl_SalesReturnBillTax'),
    'debit-notes': Document('tbl_DebitNoteMaster', 'tbl_DebitNoteDetails', 'debitNoteMasterId', 'debitNoteDetailsId', 'Debit Note'),
    'vehicle-finance': Document('tbl_FinanceHeader', 'tbl_FinanceDetail', 'financeHeaderId', 'financeDetailId', None, date_key='docDate', number_key='financeNo'),
}


def config(kind):
    if kind not in DOCUMENTS:
        raise HTTPException(404, 'Unknown transaction')
    return DOCUMENTS[kind]


def row(db, table, key, value, lock=False):
    table = T[table] if isinstance(table, str) else table
    query = select(table).where(table.c[key] == value)
    return db.execute(lock_query(db, query, table) if lock else query).mappings().first()


def children(db, cfg, identity):
    d = T[cfg.detail]
    return [dict(r) for r in db.execute(select(d).where(d.c[cfg.key] == identity).order_by(d.c[cfg.detail_key])).mappings()]


def insert(db, table, values):
    result = db.execute(T[table].insert().values(**values))
    return int(result.inserted_primary_key[0])


def register(db, kind, start=None, end=None, q=None, ledger_id=None, status=None, mode=None, date_basis='voucher', offset=0, limit=25):
    cfg = config(kind)
    m, ledger = T[cfg.master], T['tbl_AccountLedger']
    query = select(m, ledger.c.ledgerName.label('partyName')).select_from(m.outerjoin(ledger, ledger.c.ledgerId == m.c.ledgerId)) if 'ledgerId' in m.c else select(m)
    date_col = m.c.vendorInvoiceDate if kind == 'purchase-invoices' and date_basis == 'invoice' else m.c[cfg.date_key]
    if start:
        query = query.where(date_col >= start)
    if end:
        query = query.where(date_col < end + timedelta(days=1))
    if q:
        query = query.where(m.c[cfg.number_key].contains(q, autoescape=True))
    if ledger_id and 'ledgerId' in m.c:
        query = query.where(m.c.ledgerId == ledger_id)
    if status in ('posted', 'draft') and 'isPosted' in m.c:
        query = query.where(func.coalesce(m.c.isPosted, False) == (status == 'posted'))
    if kind == 'sales-quotations' and status in ('approved', 'pending'):
        query = query.where(func.coalesce(m.c.approved, False) == (status == 'approved'))
    if kind == 'purchase-orders':
        if status == 'cancelled':
            query = query.where(m.c.cancelled == True)
        if status in ('pending', 'overdue'):
            d, pd = T[cfg.detail], T['tbl_PurchaseDetails']
            used = select(func.coalesce(func.sum(pd.c.qty), 0)).where(pd.c.orderDetailsId == d.c.purchaseOrderDetailsId).scalar_subquery()
            remaining = select(d.c.purchaseOrderDetailsId).where(d.c.purchaseOrderMasterId == m.c.purchaseOrderMasterId, d.c.qty > used).exists()
            query = query.where(func.coalesce(m.c.cancelled, False) == False, remaining)
            if status == 'overdue':
                query = query.where(m.c.dueDate < func.current_date())
    if kind == 'purchase-invoices' and mode:
        key = {'misc': 'isMiscPurchase', 'asset': 'isFaPurchase', 'inventory': 'isInvPurchase'}[mode]
        query = query.where(m.c[key] == True)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    items = [dict(r) for r in db.execute(query.order_by(m.c[cfg.date_key].desc(), m.c[cfg.key].desc()).offset(offset).limit(limit)).mappings()]
    return items, total


LOOKUPS = {
    'accounts': ('tbl_AccountLedger', 'ledgerId', 'ledgerName'),
    'vehicles': ('VT_Veh_VehicleMaster', 'VehicleId', 'PlateNo'),
    'units': ('tbl_Unit', 'unitId', 'unitName'),
    'taxes': ('tbl_Tax', 'taxId', 'taxName'),
    'employees': ('tbl_Employee', 'employeeId', 'employeeName'),
    'pricing': ('tbl_PricingLevel', 'pricinglevelId', 'pricinglevelName'),
    'products': ('tbl_Product', 'productId', 'productName'),
    'assets': ('tbl_FixedAssetMaster', 'fixedAssetId', 'fixedAssetDescription'),
    'item-types': ('tbl_SalesDetailItemType', 'ItemType', 'ItemTypeName'),
    'orders': ('tbl_PurchaseOrderMaster', 'purchaseOrderMasterId', 'invoiceNo'),
    'purchases': ('tbl_PurchaseMaster', 'purchaseMasterId', 'invoiceNo'),
    'sales': ('tbl_SalesMaster', 'salesMasterId', 'invoiceNo'),
    'sales-voucher-types': ('tbl_VoucherType', 'voucherTypeId', 'voucherTypeName'),
    'contracts': ('VT_ContractMaster', 'ContractId', 'ContractRefNo'),
}


def lookups(db, name, q='', selected=None):
    if name not in LOOKUPS:
        raise HTTPException(404, 'Unknown lookup')
    table_name, key, label = LOOKUPS[name]
    t = T[table_name]
    columns = [t.c[key].label('id'), t.c[label].label('name')]
    if name == 'taxes':
        columns.append(t.c.rate)
    if name == 'accounts':
        columns.append(t.c.accountGroupId)
    query = select(*columns)
    if name == 'sales-voucher-types':
        query = query.where(t.c.typeOfVoucher == 'Sales Invoice')
    if q:
        query = query.where(t.c[label].contains(q, autoescape=True))
    if selected is not None:
        query = select(*columns).where(t.c[key] == selected)
    if name == 'orders':
        query = query.where(func.coalesce(t.c.cancelled, False) == False)
    if name in ('purchases', 'sales'):
        query = query.where(t.c.isPosted == True)
    return [dict(r) for r in db.execute(query.order_by(t.c[label], t.c[key]).limit(100)).mappings()]
