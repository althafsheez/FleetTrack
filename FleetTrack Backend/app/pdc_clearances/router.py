from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.database.session import get_db
from app.pdc_vouchers import service
from app.pdc_vouchers.schemas import (
    PDCClearanceInput, PDCClearanceResponse, PDCRegisterRow, PDCSourceType,
    PaginatedPDCClearances,
)


router = APIRouter(prefix="/pdc-clearances", tags=["PDC Clearances"])


@router.get("/lookups/statuses", response_model=list[str])
def statuses():
    return ["Cleared", "Bounced"]


@router.get("/lookups/pending-instruments", response_model=list[PDCRegisterRow])
def pending_instruments(
    source_type: PDCSourceType = Query(..., alias="sourceType"),
    voucher_no: str | None = Query(None, alias="voucherNo"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    result = service.list_vouchers(
        db, source_type, voucher_no=voucher_no, status="Pending", offset=0, limit=limit
    )
    return result["items"]


@router.get("/page", response_model=PaginatedPDCClearances)
def page(
    from_date: date | None = Query(None, alias="fromDate"),
    to_date: date | None = Query(None, alias="toDate"),
    source_type: PDCSourceType | None = Query(None, alias="sourceType"),
    ledger_id: int | None = Query(None, alias="ledgerId", gt=0),
    bank_id: int | None = Query(None, alias="bankId", gt=0),
    status: str | None = Query(None),
    cheque_no: str | None = Query(None, alias="chequeNo"),
    offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_clearances(db, from_date, to_date, source_type=source_type,
        ledger_id=ledger_id, bank_id=bank_id, status=status, cheque_no=cheque_no,
        offset=offset, limit=limit)


@router.post("/{source_type}/{source_id}", response_model=PDCClearanceResponse, status_code=201)
def create(source_type: PDCSourceType, source_id: int, payload: PDCClearanceInput,
           db: Session = Depends(get_db), current_user: AuthenticatedUser = Depends(get_current_user)):
    return service.create_clearance(db, source_type, source_id, payload, current_user.userId)


@router.get("/{clearance_id}/print-data", response_model=PDCClearanceResponse)
def print_data(clearance_id: int, db: Session = Depends(get_db)):
    return service.get_clearance(db, clearance_id)


@router.get("/{clearance_id}", response_model=PDCClearanceResponse)
def get(clearance_id: int, db: Session = Depends(get_db)):
    return service.get_clearance(db, clearance_id)


@router.put("/{clearance_id}", response_model=PDCClearanceResponse)
def update(clearance_id: int, payload: PDCClearanceInput, db: Session = Depends(get_db),
           current_user: AuthenticatedUser = Depends(get_current_user)):
    return service.update_clearance(db, clearance_id, payload, current_user.userId)


@router.delete("/{clearance_id}", status_code=204)
def delete(clearance_id: int, db: Session = Depends(get_db)):
    service.delete_clearance(db, clearance_id)
    return Response(status_code=204)
