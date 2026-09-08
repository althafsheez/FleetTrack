from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import service
from .schemas import (
    ContractCreate,
    ContractDetailResponse,
    ContractDriverCreate,
    ContractDriverResponse,
    ContractDriverUpdate,
    ContractResponse,
    ContractPrintData,
    ContractUpdate,
    ContractViewRow,
    PaginatedContractView,
)

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/", response_model=ContractResponse, status_code=201)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)):
    return service.create_contract(db, payload)


@router.get("/view", response_model=list[ContractViewRow])
def view_contracts(
    customer_name: str | None = Query(None, alias="customerName", max_length=100),
    agreement_no: str | None = Query(None, alias="agreementNo", max_length=100),
    vehicle: str | None = Query(None, max_length=100),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return service.list_contract_view(
        db,
        customer_name=customer_name,
        agreement_no=agreement_no,
        vehicle=vehicle,
        offset=offset,
        limit=limit,
    )


@router.get("/view/page", response_model=PaginatedContractView)
def view_contracts_page(
    customer_name: str | None = Query(None, alias="customerName", max_length=100),
    agreement_no: str | None = Query(None, alias="agreementNo", max_length=100),
    vehicle: str | None = Query(None, max_length=100),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_contract_view_page(
        db,
        customer_name=customer_name,
        agreement_no=agreement_no,
        vehicle=vehicle,
        offset=offset,
        limit=limit,
    )


@router.get("/drivers/", response_model=list[ContractDriverResponse])
def list_drivers(
    contract_id: int | None = Query(None, gt=0),
    q: str | None = Query(None, max_length=200),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return service.list_drivers(db, contract_id=contract_id, q=q, offset=offset, limit=limit)


@router.get("/drivers/{driver_id}", response_model=ContractDriverResponse)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    return service.get_driver_detail(db, driver_id)


@router.get("/{contract_id}/print-data", response_model=ContractPrintData)
def get_contract_print_data(
    contract_id: int,
    assignment_id: int = Query(..., alias="assignmentId", gt=0),
    db: Session = Depends(get_db),
):
    return service.get_contract_print_data(db, contract_id, assignment_id)


@router.get("/{contract_id}/print.pdf", response_class=Response)
def get_contract_print_pdf(
    contract_id: int,
    assignment_id: int = Query(..., alias="assignmentId", gt=0),
    db: Session = Depends(get_db),
):
    content, agreement_no = service.get_contract_print_pdf(db, contract_id, assignment_id)
    safe_agreement_no = "".join(character for character in agreement_no if character.isalnum() or character in "-_")
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="agreement-{safe_agreement_no or contract_id}.pdf"'},
    )


@router.post("/drivers/", response_model=ContractDriverResponse, status_code=201)
def create_driver(payload: ContractDriverCreate, db: Session = Depends(get_db)):
    return service.create_driver(db, payload)


@router.patch("/drivers/{driver_id}", response_model=ContractDriverResponse)
@router.put("/drivers/{driver_id}", response_model=ContractDriverResponse)
def update_driver(driver_id: int, payload: ContractDriverUpdate, db: Session = Depends(get_db)):
    return service.update_driver(db, driver_id, payload)


@router.delete("/drivers/{driver_id}", status_code=204)
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    service.delete_driver(db, driver_id)
    return Response(status_code=204)


@router.get("/{contract_id}", response_model=ContractDetailResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    return service.get_contract_detail(db, contract_id)


@router.patch("/{contract_id}", response_model=ContractDetailResponse)
def update_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(get_db)):
    return service.update_contract(db, contract_id, payload)
