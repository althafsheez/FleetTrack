from sqlalchemy.orm import Session 
from .repository import ( get_states , get_plate_categories ,
                         get_plate_codes , get_makes , get_models
                           , get_engine_capacities , get_makes , get_models , get_engine_capacities , get_veh_types
                           , get_fuel_types , get_fuel_capacity_units , get_transmission_types , get_colours , get_insurance_policies
                           , get_insurance_companies , get_TC_nos , get_tariff_groups , get_company_branches , get_locations , get_statuses
                             )

def get_states_service(db:Session):
    return get_states(db)

def get_plate_categories_service(db:Session , state_id:int):
    return get_plate_categories(db,state_id)

def get_plate_codes_service(db:Session , plate_category_id:int):
    return get_plate_codes(db,plate_category_id)

def get_makes_service(db:Session):
    return get_makes(db)

def get_models_service(db:Session , make_id:int):
    return get_models(db,make_id)

def get_engine_capacities_service(db:Session , model_id:int):
    return get_engine_capacities(db,model_id)

def get_veh_types_service(db:Session):
    return get_veh_types(db)

def get_fuel_types_service(db:Session):
    return get_fuel_types(db)

def get_fuel_capacity_units_service(db:Session):
    return get_fuel_capacity_units(db)

def get_transmission_types_service(db:Session):
    return get_transmission_types(db)


def get_colours_service(db:Session):
    return get_colours(db)

def get_insurance_policies_service(db:Session):
    return get_insurance_policies(db)

def get_insurance_companies_service(db:Session):
    return get_insurance_companies(db)

def get_TC_nos_service(db:Session):
    return get_TC_nos(db)

def get_tariff_groups_service(db:Session):
    return get_tariff_groups(db)
   
def get_company_branches_service(db:Session):
    return get_company_branches(db)

def get_locations_service(db:Session):
    return get_locations(db)
   

def get_statuses_service(db:Session):
    return get_statuses(db)