from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.database.session import get_db
from app.sales_invoices.schemas import SalesInvoiceResponse
from . import service
from .schemas import RentalInvoiceDueRow, RentalInvoicePreview, RentalInvoiceRequest


router = APIRouter(tags=["Rental Billing"])


@router.post("/contracts/{contract_id}/rental-invoices/preview", response_model=RentalInvoicePreview)
def preview_rental_invoice(
    contract_id: int,
    payload: RentalInvoiceRequest,
    db: Session = Depends(get_db),
):
    return service.preview_invoice(db, contract_id, payload, payload.asOfDate)


@router.post("/contracts/{contract_id}/rental-invoices", response_model=SalesInvoiceResponse, status_code=201)
def create_rental_invoice(
    contract_id: int,
    payload: RentalInvoiceRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return service.create_invoice(db, contract_id, payload, current_user.userId, payload.asOfDate)


@router.delete("/contracts/{contract_id}/rental-invoices/{sales_master_id}", status_code=204)
def delete_rental_invoice(contract_id: int, sales_master_id: int, db: Session = Depends(get_db)):
    service.delete_invoice(db, contract_id, sales_master_id)
    return Response(status_code=204)


@router.get("/rental-invoices/due", response_model=list[RentalInvoiceDueRow])
def due_rental_invoices(
    as_of_date: datetime | None = Query(None, alias="asOfDate"),
    db: Session = Depends(get_db),
):
    return service.list_due(db, as_of_date)
