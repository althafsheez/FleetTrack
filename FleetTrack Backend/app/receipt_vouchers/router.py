from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.database.session import get_db
from . import service
from .schemas import (
    OpenReceiptReference,
    PaginatedReceiptVouchers,
    ReceiptAccountLookup,
    ReceiptContractLookup,
    ReceiptDetailAccountLookup,
    ReceiptExchangeRateLookup,
    ReceiptNumberingRule,
    ReceiptVoucherInput,
    ReceiptVoucherResponse,
    ReceiptVoucherTypeLookup,
)


router = APIRouter(prefix="/receipt-vouchers", tags=["Receipt Vouchers"])


@router.get("/page", response_model=PaginatedReceiptVouchers)
def list_receipt_vouchers(
    from_date: datetime | None = Query(None, alias="fromDate"),
    to_date: datetime | None = Query(None, alias="toDate"),
    voucher_no: str | None = Query(None, alias="voucherNo", max_length=200),
    voucher_type_id: int | None = Query(None, alias="voucherTypeId", gt=0),
    receiving_ledger_id: int | None = Query(None, alias="receivingLedgerId", gt=0),
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
        receiving_ledger_id, amount, party_ledger_id, cheque_no,
        posted, offset, limit,
    )


@router.get("/lookups/voucher-types", response_model=list[ReceiptVoucherTypeLookup])
def receipt_voucher_types(db: Session = Depends(get_db)):
    return service.voucher_types(db)


@router.get("/lookups/receiving-accounts", response_model=list[ReceiptAccountLookup])
def receipt_receiving_accounts(db: Session = Depends(get_db)):
    return service.receiving_accounts(db)


@router.get("/lookups/detail-accounts", response_model=list[ReceiptDetailAccountLookup])
def receipt_detail_accounts(
    search: str | None = Query(None, max_length=200),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return service.detail_accounts(db, search, limit)


@router.get("/lookups/party-ledgers", response_model=list[ReceiptDetailAccountLookup])
def receipt_party_ledgers(
    search: str | None = Query(None, max_length=200),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return service.party_ledgers(db, search, limit)


@router.get("/lookups/exchange-rates", response_model=list[ReceiptExchangeRateLookup])
def receipt_exchange_rates(
    voucher_date: datetime = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    return service.exchange_rates(db, voucher_date)


@router.get("/lookups/numbering-rule", response_model=ReceiptNumberingRule)
def receipt_numbering_rule(
    voucher_type_id: int = Query(..., alias="voucherTypeId", gt=0),
    voucher_date: datetime = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    return service.numbering_rule(db, voucher_type_id, voucher_date)


@router.get(
    "/party-ledgers/{ledger_id}/open-references",
    response_model=list[OpenReceiptReference],
)
def receipt_open_references(ledger_id: int, db: Session = Depends(get_db)):
    return service.open_references(db, ledger_id)


@router.get(
    "/party-ledgers/{ledger_id}/contracts",
    response_model=list[ReceiptContractLookup],
)
def receipt_party_contracts(ledger_id: int, db: Session = Depends(get_db)):
    return service.party_contracts(db, ledger_id)


@router.post("/", response_model=ReceiptVoucherResponse, status_code=201)
def create_receipt_voucher(
    payload: ReceiptVoucherInput,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return service.create_voucher(db, payload, current_user.userId)


@router.get("/{receipt_master_id}/print-data", response_model=ReceiptVoucherResponse)
def receipt_voucher_print_data(receipt_master_id: int, db: Session = Depends(get_db)):
    return service.get_voucher(db, receipt_master_id)


@router.post("/{receipt_master_id}/post", response_model=ReceiptVoucherResponse)
def post_receipt_voucher(receipt_master_id: int, db: Session = Depends(get_db)):
    return service.post_voucher(db, receipt_master_id)


@router.post("/{receipt_master_id}/unpost", response_model=ReceiptVoucherResponse)
def unpost_receipt_voucher(receipt_master_id: int, db: Session = Depends(get_db)):
    return service.unpost_voucher(db, receipt_master_id)


@router.get("/{receipt_master_id}", response_model=ReceiptVoucherResponse)
def get_receipt_voucher(receipt_master_id: int, db: Session = Depends(get_db)):
    return service.get_voucher(db, receipt_master_id)


@router.patch("/{receipt_master_id}", response_model=ReceiptVoucherResponse)
def update_receipt_voucher(
    receipt_master_id: int,
    payload: ReceiptVoucherInput,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return service.update_voucher(db, receipt_master_id, payload, current_user.userId)


@router.delete("/{receipt_master_id}", status_code=204)
def delete_receipt_voucher(receipt_master_id: int, db: Session = Depends(get_db)):
    service.delete_voucher(db, receipt_master_id)
    return Response(status_code=204)
