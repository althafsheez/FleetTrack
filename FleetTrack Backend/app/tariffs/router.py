from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import service
from .schemas import TariffGroupCreate, TariffGroupResponse, TariffRatesUpdate, TariffRatesResponse, TariffGroupUpdate, TariffGroupDetail

router = APIRouter(prefix="/vehicle-tariff-groups", tags=["Tariff groups"])


@router.get("/", response_model=list[TariffGroupResponse], summary="List all tariff groups")
def list_groups(db: Session = Depends(get_db)):
    return service.list_groups(db)


@router.get("/search", response_model=list[TariffGroupResponse], summary="Search tariff groups by name")
def search_groups(q: str = Query(..., min_length=1, max_length=100),
                  db: Session = Depends(get_db)):
    return service.list_groups(db, q=q)


@router.post("/", response_model=TariffGroupResponse, status_code=201)
def create_group(payload: TariffGroupCreate, db: Session = Depends(get_db)):
    return service.create_group(db, payload)


@router.get("/{group_id}", response_model=TariffGroupDetail)
def get_group(group_id: int, db: Session = Depends(get_db)):
    return service.get_group(db, group_id)


@router.patch("/{group_id}", response_model=TariffGroupDetail)
def update_group(group_id: int, payload: TariffGroupUpdate, db: Session = Depends(get_db)):
    return service.update_group(db, group_id, payload)


@router.delete("/{group_id}", status_code=204)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    service.delete_group(db, group_id)
    return Response(status_code=204)


@router.get("/{group_id}/rates", response_model=TariffRatesResponse, summary="Get vehicle group pricing")
def get_rates(group_id: int, db: Session = Depends(get_db)):
    return service.get_group(db, group_id)


@router.patch("/{group_id}/rates", response_model=TariffRatesResponse, summary="Save vehicle group pricing")
def save_rates(group_id: int, payload: TariffRatesUpdate, db: Session = Depends(get_db)):
    # Pricing is initialized with the name; PATCH saves only supplied rate fields.
    return service.update_group(db, group_id, payload)
