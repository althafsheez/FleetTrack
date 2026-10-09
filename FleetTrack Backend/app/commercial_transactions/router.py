from datetime import date, datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.database.session import get_db
from app.payment_vouchers.service import exchange_rates
from . import repository as r, service as s, sales_register, exports
from .schemas import DocumentInput, Kind

router = APIRouter(prefix='/transaction-documents', tags=['Commercial Transactions'])


class VersionInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expectedVersion: str


class SalesExportInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    format: Literal['excel', 'pdf']
    fromDate: date | None = None
    toDate: date | None = None
    invoiceNo: str | None = Field(None, max_length=200)
    ledgerId: int | None = Field(None, gt=0)
    voucherTypeId: int | None = Field(None, gt=0)
    contractId: int | None = Field(None, gt=0)
    fineNo: str | None = Field(None, max_length=200)
    location: str | None = Field(None, max_length=200)
    posted: bool | None = None
    identities: list[int] = Field(default_factory=list, max_length=100)


@router.post('/sales-register/export')
def sales_export(payload: SalesExportInput, db: Session = Depends(get_db)):
    if payload.fromDate and payload.toDate and payload.toDate < payload.fromDate:
        raise HTTPException(422, 'To date must not precede from date')
    result = sales_register.register(db, payload.fromDate, payload.toDate, payload.invoiceNo, payload.ledgerId,
        payload.voucherTypeId, payload.contractId, payload.fineNo, payload.location, payload.posted,
        limit=10000, identities=payload.identities)
    if result['total'] > 10000:
        raise HTTPException(422, 'Narrow the filters to at most 10,000 invoices for export')
    is_pdf = payload.format == 'pdf'
    content = exports.pdf(result['items']) if is_pdf else exports.excel(result['items'])
    extension = 'pdf' if is_pdf else 'xml'
    return Response(content, media_type='application/pdf' if is_pdf else 'application/vnd.ms-excel',
        headers={'Content-Disposition': f'attachment; filename="sales-invoices.{extension}"'})


@router.get('/lookups/exchange-rates')
def rates(date: datetime = Query(), db: Session = Depends(get_db)):
    return exchange_rates(db, date)


@router.get('/lookups/{name}')
def lookups(name: str, q: str = Query('', max_length=200), selected: int | None = Query(None, ge=0), db: Session = Depends(get_db)):
    return r.lookups(db, name, q, selected)


@router.get('/references')
def references(ledgerId: int = Query(gt=0), direction: Literal['Dr', 'Cr'] = 'Dr', db: Session = Depends(get_db)):
    return s.references(db, ledgerId, direction)


@router.get('/sales-register/page')
def sales_page(fromDate: date | None = None, toDate: date | None = None,
    invoiceNo: str | None = Query(None, max_length=200), ledgerId: int | None = Query(None, gt=0),
    voucherTypeId: int | None = Query(None, gt=0), contractId: int | None = Query(None, gt=0),
    fineNo: str | None = Query(None, max_length=200), location: str | None = Query(None, max_length=200),
    posted: bool | None = None, offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)):
    if fromDate and toDate and toDate < fromDate:
        raise HTTPException(422, 'To date must not precede from date')
    return sales_register.register(db, fromDate, toDate, invoiceNo, ledgerId, voucherTypeId,
        contractId, fineNo, location, posted, offset, limit)


@router.get('/sales-register/{identity}/salik')
def sales_salik(identity: int, db: Session = Depends(get_db)):
    return sales_register.salik(db, identity)


@router.get('/sales-register/{identity}')
def sales_detail(identity: int, db: Session = Depends(get_db)):
    return sales_register.detail(db, identity)


@router.get('/sources/{kind}/{identity}')
def sources(kind: Literal['purchase-orders', 'purchases', 'sales'], identity: int, db: Session = Depends(get_db)):
    return s.source_lines(db, kind, identity)


@router.post('/vehicle-finance/preview')
def finance_preview(payload: DocumentInput):
    return s.finance_schedule(payload)


@router.get('/{kind}/page')
def register(kind: Kind, fromDate: date | None = None, toDate: date | None = None,
    q: str | None = Query(None, max_length=200), ledgerId: int | None = Query(None, gt=0),
    status: Literal['posted', 'draft', 'approved', 'pending', 'cancelled', 'overdue'] | None = None,
    mode: Literal['misc', 'asset', 'inventory'] | None = None, dateBasis: Literal['voucher', 'invoice'] = 'voucher',
    offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    if fromDate and toDate and toDate < fromDate:
        raise HTTPException(422, 'To date must not precede from date')
    items, total = r.register(db, kind, fromDate, toDate, q, ledgerId, status, mode, dateBasis, offset, limit)
    cfg = r.config(kind)
    for item in items:
        item['id'] = int(item[cfg.key])
        item['number'] = item[cfg.number_key]
        item['documentDate'] = item[cfg.date_key]
    return dict(items=items, total=total, offset=offset, limit=limit)


@router.post('/{kind}', status_code=201)
def create(kind: Kind, payload: DocumentInput, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    return s.save_document(db, kind, payload, user.userId)


@router.get('/{kind}/{identity}')
def detail(kind: Kind, identity: int, db: Session = Depends(get_db)):
    return s.get_document(db, kind, identity)


@router.patch('/{kind}/{identity}')
def update(kind: Kind, identity: int, payload: DocumentInput, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    return s.save_document(db, kind, payload, user.userId, identity)


@router.delete('/{kind}/{identity}', status_code=204)
def delete(kind: Kind, identity: int, expectedVersion: str = Query(), db: Session = Depends(get_db)):
    s.delete_document(db, kind, identity, expectedVersion)
    return Response(status_code=204)


@router.post('/{kind}/{identity}/post')
def post(kind: Kind, identity: int, payload: VersionInput, db: Session = Depends(get_db)):
    return s.change_posting(db, kind, identity, True, payload.expectedVersion)


@router.post('/{kind}/{identity}/unpost')
def unpost(kind: Kind, identity: int, payload: VersionInput, db: Session = Depends(get_db)):
    return s.change_posting(db, kind, identity, False, payload.expectedVersion)
