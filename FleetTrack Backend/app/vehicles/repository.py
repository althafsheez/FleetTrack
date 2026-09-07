from sqlalchemy import select, or_
from app.generated_models.models import VTVehVehicleMaster

TABLE = VTVehVehicleMaster.__table__


def list_vehicles(db, q=None, plate_no=None, fleet_no=None, offset=0, limit=100):
    query = select(TABLE)
    if q:
        query = query.where(or_(*(TABLE.c[name].icontains(q, autoescape=True)
                                 for name in ("PlateNo", "VHType", "ChasisNo", "EngineNo"))))
    if plate_no:
        query = query.where(TABLE.c.PlateNo.icontains(plate_no, autoescape=True))
    if fleet_no:
        query = query.where(TABLE.c.VHType.icontains(fleet_no, autoescape=True))
    return db.execute(query.order_by(TABLE.c.VehicleId).offset(offset).limit(limit)).mappings().all()


def get_vehicle(db, vehicle_id):
    return db.execute(select(TABLE).where(TABLE.c.VehicleId == vehicle_id)).mappings().first()


def create_vehicle(db, values):
    result = db.execute(TABLE.insert().values(**values))
    return result.inserted_primary_key[0]


def update_vehicle(db, vehicle_id, values):
    db.execute(TABLE.update().where(TABLE.c.VehicleId == vehicle_id).values(**values))


def delete_vehicle(db, vehicle_id):
    db.execute(TABLE.delete().where(TABLE.c.VehicleId == vehicle_id))
