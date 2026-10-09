from datetime import date
from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import repository as r, service
from .schemas import FineInput, ReconciliationInput

router = APIRouter(tags=['Transaction Operations'])


@router.get('/bank-reconciliations/accounts')
def accounts(db: Session = Depends(get_db)):
    return r.bank_accounts(db)


@router.get('/bank-reconciliations/page')
def reconciliation_page(bankLedgerId: int = Query(gt=0), fromDate: date = Query(), toDate: date = Query(),
    status: Literal['all', 'reconciled', 'unreconciled'] = 'unreconciled', offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    return service.reconciliation_entries(db, bankLedgerId, fromDate, toDate, status, offset, limit)


@router.put('/bank-reconciliations')
def reconcile(payload: ReconciliationInput, db: Session = Depends(get_db)):
    return service.save_reconciliation(db, payload)


@router.get('/traffic-fines/page')
def fines(fromDate: date | None = None, toDate: date | None = None, q: str | None = Query(None, max_length=100),
    posted: bool | None = None, offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    return service.fines(db, fromDate, toDate, q, posted, offset, limit)


@router.get('/traffic-fines/traffic-files')
def traffic_files(db: Session = Depends(get_db)):
    t = r.T['VT_Veh_TCNoMaster']
    return [dict(row) for row in db.execute(select(t.c.TCNo.label('id'), t.c.TCNo.label('name')).order_by(t.c.TCNo)).mappings()]


@router.post('/traffic-fines', status_code=201)
def create_fine(payload: FineInput, db: Session = Depends(get_db)):
    return service.save_fine(db, payload)
