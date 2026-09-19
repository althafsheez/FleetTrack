from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.database.session import get_db
from . import service
from .schemas import (
    InvoiceLookup,
    InvoiceType,
    PaginatedSalesInvoices,
    SalesInvoiceDraftInput,
    SalesInvoiceResponse,
)


router = APIRouter(prefix="/sales-invoices", tags=["Sales Invoices"])


@router.get("/page", response_model=PaginatedSalesInvoices)
def list_sales_invoices(
    q: str | None = Query(None, max_length=200),
    invoice_type: InvoiceType | None = Query(None, alias="invoiceType"),
    posted: bool | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_invoices(db, q=q, invoice_type=invoice_type, posted=posted, offset=offset, limit=limit)


@router.get("/lookups/{name}", response_model=list[InvoiceLookup])
def sales_invoice_lookups(
    name: str,
    invoice_type: InvoiceType | None = Query(None, alias="invoiceType"),
    db: Session = Depends(get_db),
):
    return service.lookups(db, name, invoice_type)


@router.post("/", response_model=SalesInvoiceResponse, status_code=201)
def create_sales_invoice_draft(
    payload: SalesInvoiceDraftInput,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return service.create_draft(db, payload, current_user.userId)


@router.get("/{sales_master_id}", response_model=SalesInvoiceResponse)
def get_sales_invoice(sales_master_id: int, db: Session = Depends(get_db)):
    return service.get_invoice(db, sales_master_id)


@router.patch("/{sales_master_id}", response_model=SalesInvoiceResponse)
def update_sales_invoice_draft(
    sales_master_id: int,
    payload: SalesInvoiceDraftInput,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return service.update_draft(db, sales_master_id, payload, current_user.userId)


@router.delete("/{sales_master_id}", status_code=204)
def delete_sales_invoice_draft(sales_master_id: int, db: Session = Depends(get_db)):
    service.delete_draft(db, sales_master_id)
    return Response(status_code=204)


@router.post("/{sales_master_id}/post", response_model=SalesInvoiceResponse)
def post_sales_invoice(sales_master_id: int, db: Session = Depends(get_db)):
    return service.post_invoice(db, sales_master_id)


@router.post("/{sales_master_id}/unpost", response_model=SalesInvoiceResponse)
def unpost_sales_invoice(sales_master_id: int, db: Session = Depends(get_db)):
    return service.unpost_invoice(db, sales_master_id)
