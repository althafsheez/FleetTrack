from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.database.session import get_db
from app.pdc_vouchers import service
from app.pdc_vouchers.schemas import (
    PDCLookup, PDCNumberingRule, PDCOpenReference, PDCVoucherInput,
    PDCVoucherResponse, PaginatedPDCVouchers,
)


router = APIRouter(prefix="/pdc-payables", tags=["PDC Payables"])


@router.get("/page", response_model=PaginatedPDCVouchers)
def page(
    from_date: date | None = Query(None, alias="fromDate"),
    to_date: date | None = Query(None, alias="toDate"),
    voucher_no: str | None = Query(None, alias="voucherNo"),
    ledger_id: int | None = Query(None, alias="ledgerId", gt=0),
    bank_id: int | None = Query(None, alias="bankId", gt=0),
    amount: Decimal | None = Query(None, gt=0),
    cheque_no: str | None = Query(None, alias="chequeNo"),
    status: str | None = Query(None),
    offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_vouchers(db, "payable", from_date, to_date, voucher_no=voucher_no,
        ledger_id=ledger_id, bank_id=bank_id, amount=amount, cheque_no=cheque_no,
        status=status, offset=offset, limit=limit)


@router.get("/lookups/control-accounts", response_model=list[PDCLookup])
def control_accounts(search: str | None = None, limit: int = Query(100, ge=1, le=200), db: Session = Depends(get_db)):
    return service.lookups(db, "control", "payable", search, limit)


@router.get("/lookups/banks", response_model=list[PDCLookup])
def banks(search: str | None = None, limit: int = Query(100, ge=1, le=200), db: Session = Depends(get_db)):
    return service.lookups(db, "bank", "payable", search, limit)


@router.get("/lookups/party-ledgers", response_model=list[PDCLookup])
def parties(search: str | None = None, limit: int = Query(100, ge=1, le=200), db: Session = Depends(get_db)):
    return service.lookups(db, "party", "payable", search, limit)


@router.get("/lookups/accounts", response_model=list[PDCLookup])
def accounts(search: str | None = None, limit: int = Query(100, ge=1, le=200), db: Session = Depends(get_db)):
    return service.lookups(db, "account", "payable", search, limit)


@router.get("/lookups/open-references", response_model=list[PDCOpenReference])
def open_references(ledger_id: int = Query(..., alias="ledgerId", gt=0), db: Session = Depends(get_db)):
    return service.open_references(db, "payable", ledger_id)


@router.get("/lookups/numbering-rule", response_model=PDCNumberingRule)
def numbering(value: datetime = Query(..., alias="date"), db: Session = Depends(get_db)):
    return service.numbering(db, "payable", value)


@router.post("/", response_model=PDCVoucherResponse, status_code=201)
def create(payload: PDCVoucherInput, db: Session = Depends(get_db), current_user: AuthenticatedUser = Depends(get_current_user)):
    return service.create_voucher(db, "payable", payload, current_user.userId)


@router.get("/{master_id}/print-data", response_model=PDCVoucherResponse)
def print_data(master_id: int, db: Session = Depends(get_db)):
    return service.get_voucher(db, "payable", master_id)


@router.get("/{master_id}", response_model=PDCVoucherResponse)
def get(master_id: int, db: Session = Depends(get_db)):
    return service.get_voucher(db, "payable", master_id)


@router.put("/{master_id}", response_model=PDCVoucherResponse)
def update(master_id: int, payload: PDCVoucherInput, db: Session = Depends(get_db), current_user: AuthenticatedUser = Depends(get_current_user)):
    return service.update_voucher(db, "payable", master_id, payload, current_user.userId)


@router.delete("/{master_id}", status_code=204)
def delete(master_id: int, db: Session = Depends(get_db)):
    service.delete_voucher(db, "payable", master_id)
    return Response(status_code=204)
