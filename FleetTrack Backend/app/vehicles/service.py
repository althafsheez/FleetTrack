from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select
from app.generated_models.models import Base
from app.master_data import database_errors, require_reference, require_unused
from . import repository as repo

# UI lookup associations; validate changed values only to retain legacy missing IDs.
REFERENCES = {
    "ModelId": ("VT_Veh_ModelMaster", "ModelId"),
    "EngineCapacityId": ("VT_Veh_EngineCapacityMaster", "EngineCapacityId"),
    "PlateCodeId": ("VT_Veh_PlateCodeMaster", "PlateCodeId"),
    "InsurancePolicyId": ("VT_Veh_InsurancePolicyMaster", "InsurancePolicyId"),
    "InsuranceCompanyId": ("VT_Veh_InsuranceCompanyMaster", "InsuranceCompanyId"),
    "InsuranceTypeId": ("VT_Veh_InsuranceTypeMaster", "InsuranceTypeId"),
    "TCNoId": ("VT_Veh_TCNoMaster", "TCNoId"),
    "TypeId": ("VT_Veh_TypeMaster", "TypeId"),
    "FuelCapacityUnitId": ("VT_Veh_FuelCapacityUnitMaster", "FuelCapUnitId"),
    "TransmissionId": ("VT_Veh_TransmissionMaster", "TransmissionId"),
    "FuelTypeId": ("VT_Veh_FuelTypeMaster", "FuelTypeId"),
    "ColourId": ("VT_Veh_ColourMaster", "ColourId"),
    "TariffGroupId": ("VT_Veh_TariffGroupMaster", "TariffGroupId"),
    "StatusId": ("VT_StatusMaster", "StatusId"),
    "BranchId": ("VT_Company_BranchMaster", "BranchId"),
    "LocId": ("VT_Veh_LocationMaster", "LocationId"),
    "FuelLevel": ("VT_Veh_FuelLevelMaster", "FuelLevelId"),
}


def validate_references(db, values, existing=None):
    changed = {k: v for k, v in values.items() if existing is None or existing[k] != v}
    for field, (table, key) in REFERENCES.items():
        if field in changed:
            require_reference(db, table, key, changed[field], field)
    # Respect the unusual generated FK instead of changing the MSSQL schema.
    if "FuelCapacityUnitId" in changed:
        require_reference(db, "VT_Veh_FleetTypeMaster", "FleetTypeId",
                          changed["FuelCapacityUnitId"], "FuelCapacityUnitId (legacy fleet-type constraint)")
    if "ModelId" in changed or "EngineCapacityId" in changed:
        merged = dict(existing or {}) | values
        table = Base.metadata.tables["VT_Veh_EngineCapacityMaster"]
        model_id = db.execute(select(table.c.ModelId).where(
            table.c.EngineCapacityId == merged["EngineCapacityId"])).scalar_one_or_none()
        if model_id != merged["ModelId"]:
            raise HTTPException(422, "EngineCapacityId does not belong to ModelId")


def get_vehicle(db, vehicle_id):
    with database_errors(db):
        result = repo.get_vehicle(db, vehicle_id)
        if result is None:
            raise HTTPException(404, "Vehicle not found")
        return result


def list_vehicles(db, **filters):
    with database_errors(db):
        return repo.list_vehicles(db, **filters)


def get_vehicles_page(db, **filters):
    with database_errors(db):
        items, total = repo.get_vehicles_page(db, **filters)
        return {"items": items, "total": total, "offset": filters["offset"], "limit": filters["limit"]}


def create_vehicle(db, payload):
    values = payload.model_dump()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    values.update(CreatedDate=now, LastUpdatedDate=now, LastUpdatedBy=values["CreatedBy"])
    if values["LatestKmRdg"] is None:
        values["LatestKmRdg"] = values["InitialKmRdg"]
    with database_errors(db):
        validate_references(db, values)
        vehicle_id = repo.create_vehicle(db, values)
        result = repo.get_vehicle(db, vehicle_id)
        db.commit()
        return result


def update_vehicle(db, vehicle_id, payload):
    with database_errors(db):
        current = get_vehicle(db, vehicle_id)
        values = payload.model_dump(exclude_unset=True)
        validate_references(db, values, current)
        values["LastUpdatedDate"] = datetime.now(timezone.utc).replace(tzinfo=None)
        repo.update_vehicle(db, vehicle_id, values)
        result = repo.get_vehicle(db, vehicle_id)
        db.commit()
        return result


def delete_vehicle(db, vehicle_id):
    with database_errors(db):
        get_vehicle(db, vehicle_id)
        # These names are candidate vehicle references, not inferred database FKs.
        # Conservative checks include legacy Core/history tables and replacement IDs.
        candidates = [(t, c) for t in Base.metadata.tables.values() if t is not repo.TABLE
                      for c in t.c if c.name.lower() in
                      {"vehicleid", "vehicle", "sid_vehicle_id", "takingvehicleid", "givingvehicleid"}]
        require_unused(db, candidates, vehicle_id)
        repo.delete_vehicle(db, vehicle_id)
        db.commit()
