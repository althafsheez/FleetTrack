from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.database.session import get_db
from . import service
from .schemas import PaginatedVehicleResponse, VehicleCreate, VehicleUpdate, VehicleResponse

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("/page", response_model=PaginatedVehicleResponse)
def get_vehicles_page(
    q: str | None = Query(None, max_length=200),
    plate_no: str | None = Query(None, max_length=50),
    fleet_no: str | None = Query(None, max_length=50),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.get_vehicles_page(
        db, q=q, plate_no=plate_no, fleet_no=fleet_no, offset=offset, limit=limit
    )


@router.get("/", response_model=list[VehicleResponse])
@router.get("/search", response_model=list[VehicleResponse])
def list_vehicles(q: str | None = Query(None, max_length=200),
                  plate_no: str | None = Query(None, max_length=50),
                  fleet_no: str | None = Query(None, max_length=50),
                  offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
                  db: Session = Depends(get_db)):
    return service.list_vehicles(db, q=q, plate_no=plate_no, fleet_no=fleet_no, offset=offset, limit=limit)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return service.get_vehicle(db, vehicle_id)


@router.post("/", response_model=VehicleResponse, status_code=201)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    return service.create_vehicle(db, payload)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, payload: VehicleUpdate, db: Session = Depends(get_db)):
    return service.update_vehicle(db, vehicle_id, payload)


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    service.delete_vehicle(db, vehicle_id)
    return Response(status_code=204)
