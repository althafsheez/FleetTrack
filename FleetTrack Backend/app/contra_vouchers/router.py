from datetime import date, datetime

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.database.session import get_db
from . import service
from .schemas import (
    ContraAccountLookup,
    ContraDirection,
    ContraExchangeRateLookup,
    ContraNumberingRule,
    ContraVoucherInput,
    ContraVoucherResponse,
    ContraVoucherTypeLookup,
    PaginatedContraVouchers,
)


router = APIRouter(prefix="/contra-vouchers", tags=["Contra Vouchers"])


@router.get("/page", response_model=PaginatedContraVouchers)
def list_contra_vouchers(
    from_date: date | None = Query(None, alias="fromDate"),
    to_date: date | None = Query(None, alias="toDate"),
    voucher_no: str | None = Query(None, alias="voucherNo", max_length=200),
    ledger_id: int | None = Query(None, alias="ledgerId", gt=0),
    direction: ContraDirection | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_vouchers(
        db,
        from_date=from_date,
        to_date=to_date,
        voucher_no=voucher_no,
        ledger_id=ledger_id,
        direction=direction,
        offset=offset,
        limit=limit,
    )


@router.get("/lookups/voucher-types", response_model=list[ContraVoucherTypeLookup])
def contra_voucher_types(db: Session = Depends(get_db)):
    return service.voucher_types(db)


@router.get("/lookups/accounts", response_model=list[ContraAccountLookup])
def contra_accounts(db: Session = Depends(get_db)):
    return service.accounts(db)


@router.get("/lookups/exchange-rates", response_model=list[ContraExchangeRateLookup])
def contra_exchange_rates(
    voucher_date: datetime = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    return service.exchange_rates(db, voucher_date)


@router.get("/lookups/numbering-rule", response_model=ContraNumberingRule)
def contra_numbering_rule(
    voucher_date: datetime = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    return service.numbering_rule(db, voucher_date)


@router.post("/", response_model=ContraVoucherResponse, status_code=201)
def create_contra_voucher(
    payload: ContraVoucherInput,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return service.create_voucher(db, payload, current_user.userId)


@router.get("/{contra_master_id}/print-data", response_model=ContraVoucherResponse)
def contra_voucher_print_data(contra_master_id: int, db: Session = Depends(get_db)):
    return service.get_voucher(db, contra_master_id)


@router.get("/{contra_master_id}", response_model=ContraVoucherResponse)
def get_contra_voucher(contra_master_id: int, db: Session = Depends(get_db)):
    return service.get_voucher(db, contra_master_id)


@router.patch("/{contra_master_id}", response_model=ContraVoucherResponse)
def update_contra_voucher(
    contra_master_id: int,
    payload: ContraVoucherInput,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return service.update_voucher(db, contra_master_id, payload, current_user.userId)


@router.delete("/{contra_master_id}", status_code=204)
def delete_contra_voucher(contra_master_id: int, db: Session = Depends(get_db)):
    service.delete_voucher(db, contra_master_id)
    return Response(status_code=204)
