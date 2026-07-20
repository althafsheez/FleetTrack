from sqlacademy import Session
from .schemas import VehicleCreate, VehicleUpdate 
from app.generated_models.models import VT_Veh_VehicleMaster

def get_all_vehicles(db: Session):
    return db.query(VT_Veh_VehicleMaster).all()

def get_vehicle_by_id(db:Session , vehicleId:int):
    return db.query(VT_Veh_VehicleMaster).filter(VT_Veh_VehicleMaster.VehicleId == vehicleId).first()

def create_vehicle(db: Session, vehicle: VehicleCreate):
    vehicle_data=vehicle.model_dump()
    db_vehicle=VT_Veh_VehicleMaster(**vehicle_data)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def update_vehicle(db: Session, vehicleId: int, vehicle: VehicleUpdate):
    db_vehicle = get_vehicle_by_id(db, vehicleId)
    if not db_vehicle:
        return None

    vehicle_data = vehicle.model_dump()
    for key, value in vehicle_data.items():
        setattr(db_vehicle, key, value)

    db.commit()
    db.refresh(db_vehicle)

    return db_vehicle

def delete_vehicle(db: Session, vehicleId: int):
    db_vehicle = get_vehicle_by_id(db, vehicleId)
    if not db_vehicle:
        return None

    db.delete(db_vehicle)
    db.commit()

    return True

def search_vehicle(db:Session , )