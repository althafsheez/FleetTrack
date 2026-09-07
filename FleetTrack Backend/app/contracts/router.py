from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import service
from .schemas import (
    ContractCreate,
    ContractDriverCreate,
    ContractDriverResponse,
    ContractDriverUpdate,
    ContractResponse,
    ContractViewRow,
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
