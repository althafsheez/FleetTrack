from sqlalchemy.orm import Session 
from app.generated_models.models import ( VTCompanyBranchMaster, VTVehColourMaster, VTVehInsuranceCompanyMaster, VTVehInsurancePolicyMaster, VTVehLocationMaster, VTVehPlateCodeMaster , VTVehStateMaster , VTVehPlateCategoryMaster
                                          , VTVehMakeMaster , VTVehModelMaster ,
                                          VTVehEngineCapacityMaster, VTVehTCNoMaster, VTVehTariffGroupMaster , VTVehTypeMaster , VTVehFuelTypeMaster 
                                          , VTVehFuelCapacityUnitMaster , VTVehTransmissionMaster ,VTStatusMaster )



def get_states(db:Session):
    return (
        db.query(VTVehStateMaster )
        .all()
    )

def get_plate_categories(db:Session , state_id:int):
    return (
        db.query(VTVehPlateCategoryMaster)
        .filter(VTVehPlateCategoryMaster.StateId==state_id)
        .all()
    )

def get_plate_codes(db:Session , plate_category_id:int):
    return (
        db.query(VTVehPlateCodeMaster)
        .filter(VTVehPlateCodeMaster.PlateCategoryId==plate_category_id)
        .all()
    )
        
def get_makes(db:Session):
    return (
        db.query(VTVehMakeMaster)
        .all()
    )

def get_models(db:Session , make_id:int):
    return (
        db.query(VTVehModelMaster)
        .filter(VTVehModelMaster.MakeId==make_id)
        .all()
    )

def get_engine_capacities(db:Session , model_id:int):
    return (
        db.query(VTVehEngineCapacityMaster)
        .filter(VTVehEngineCapacityMaster.ModelId==model_id)
        .all()
    )

def get_veh_types(db:Session):
    return (
        db.query(VTVehTypeMaster)
        .all()
    )

def get_fuel_types(db:Session):
    return (
        db.query(VTVehFuelTypeMaster)
        .all()
    )

def get_fuel_capacity_units(db:Session):
    return (
        db.query(VTVehFuelCapacityUnitMaster)
        .all()
    )

def get_transmission_types(db:Session):
    return (
        db.query(VTVehTransmissionMaster)
        .all()
    )

def get_colours(db:Session):
    return (
        db.query(VTVehColourMaster)
        .all()
    )

def get_insurance_policies(db:Session):
    return (
        db.query(VTVehInsurancePolicyMaster)
        .all()
    )

def get_insurance_companies(db:Session):
    return (
        db.query(VTVehInsuranceCompanyMaster)
        .distinct()
        .all()
    )

def get_TC_nos(db:Session):
    return (
        db.query(VTVehTCNoMaster)
        .distinct()
        .all()
    )

def get_tariff_groups(db:Session):
    return (
        db.query(VTVehTariffGroupMaster)
        .distinct()
        .all()
    )

def get_company_branches(db:Session):
    return (
        db.query(VTCompanyBranchMaster)
        .distinct()
        .all()
    )

def get_locations(db:Session):
    return (
        db.query(VTVehLocationMaster)
        .distinct()
        .all()
    )

def get_statuses(db:Session):
    return (
        db.query(VTStatusMaster)
        .distinct()
        .all()
    )