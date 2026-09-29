from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.database.session import get_db
from . import service
from .schemas import (
    OpenPaymentReference,
    PaginatedPaymentVouchers,
    PaymentAccountLookup,
    PaymentDetailAccountLookup,
    PaymentExchangeRateLookup,
    PaymentNumberingRule,
    PaymentVehicleLookup,
    PaymentVoucherInput,
    PaymentVoucherResponse,
    PaymentVoucherTypeLookup,
)


router = APIRouter(prefix="/payment-vouchers", tags=["Payment Vouchers"])


@router.get("/page", response_model=PaginatedPaymentVouchers)
def list_payment_vouchers(
    from_date: datetime | None = Query(None, alias="fromDate"),
    to_date: datetime | None = Query(None, alias="toDate"),
    voucher_no: str | None = Query(None, alias="voucherNo", max_length=200),
    voucher_type_id: int | None = Query(None, alias="voucherTypeId", gt=0),
    paying_ledger_id: int | None = Query(None, alias="payingLedgerId", gt=0),
    amount: Decimal | None = Query(None, gt=0, max_digits=18, decimal_places=5),
    party_ledger_id: int | None = Query(None, alias="partyLedgerId", gt=0),
    cheque_no: str | None = Query(None, alias="chequeNo", max_length=200),
    posted: bool | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_vouchers(
        db, from_date, to_date, voucher_no, voucher_type_id,
        paying_ledger_id, amount, party_ledger_id, cheque_no,
        posted, offset, limit,
    )


@router.get("/lookups/voucher-types", response_model=list[PaymentVoucherTypeLookup])
def payment_voucher_types(db: Session = Depends(get_db)):
    return service.voucher_types(db)


@router.get("/lookups/paying-accounts", response_model=list[PaymentAccountLookup])
def payment_paying_accounts(db: Session = Depends(get_db)):
    return service.paying_accounts(db)


@router.get("/lookups/detail-accounts", response_model=list[PaymentDetailAccountLookup])
def payment_detail_accounts(
    search: str | None = Query(None, max_length=200),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return service.detail_accounts(db, search, limit)


@router.get("/lookups/party-ledgers", response_model=list[PaymentDetailAccountLookup])
def payment_party_ledgers(
    search: str | None = Query(None, max_length=200),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return service.party_ledgers(db, search, limit)


@router.get("/lookups/exchange-rates", response_model=list[PaymentExchangeRateLookup])
def payment_exchange_rates(
    voucher_date: datetime = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    return service.exchange_rates(db, voucher_date)


@router.get("/lookups/vehicles", response_model=list[PaymentVehicleLookup])
def payment_vehicles(
    search: str | None = Query(None, max_length=100),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return service.vehicles(db, search, limit)


@router.get("/lookups/numbering-rule", response_model=PaymentNumberingRule)
def payment_numbering_rule(
    voucher_type_id: int = Query(..., alias="voucherTypeId", gt=0),
    voucher_date: datetime = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    return service.numbering_rule(db, voucher_type_id, voucher_date)


@router.get(
    "/party-ledgers/{ledger_id}/open-references",
    response_model=list[OpenPaymentReference],
)
def payment_open_references(ledger_id: int, db: Session = Depends(get_db)):
    return service.open_references(db, ledger_id)


@router.post("/", response_model=PaymentVoucherResponse, status_code=201)
def create_payment_voucher(
    payload: PaymentVoucherInput,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return service.create_voucher(db, payload, current_user.userId)


@router.get("/{payment_master_id}/print-data", response_model=PaymentVoucherResponse)
def payment_voucher_print_data(payment_master_id: int, db: Session = Depends(get_db)):
    return service.get_voucher(db, payment_master_id)


@router.post("/{payment_master_id}/post", response_model=PaymentVoucherResponse)
def post_payment_voucher(payment_master_id: int, db: Session = Depends(get_db)):
    return service.post_voucher(db, payment_master_id)


@router.post("/{payment_master_id}/unpost", response_model=PaymentVoucherResponse)
def unpost_payment_voucher(payment_master_id: int, db: Session = Depends(get_db)):
    return service.unpost_voucher(db, payment_master_id)


@router.get("/{payment_master_id}", response_model=PaymentVoucherResponse)
def get_payment_voucher(payment_master_id: int, db: Session = Depends(get_db)):
    return service.get_voucher(db, payment_master_id)


@router.patch("/{payment_master_id}", response_model=PaymentVoucherResponse)
def update_payment_voucher(
    payment_master_id: int,
    payload: PaymentVoucherInput,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return service.update_voucher(db, payment_master_id, payload, current_user.userId)


@router.delete("/{payment_master_id}", status_code=204)
def delete_payment_voucher(payment_master_id: int, db: Session = Depends(get_db)):
    service.delete_voucher(db, payment_master_id)
    return Response(status_code=204)
