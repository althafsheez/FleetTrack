from fastapi import APIRouter , Depends , HTTPException 
from sqlalchemy.orm import Session
from .service import ( get_states_service , get_plate_categories_service , get_plate_codes_service
                      , get_makes_service , get_models_service , get_engine_capacities_service 
                      ,get_veh_types_service , get_fuel_types_service , get_fuel_capacity_units_service , get_transmission_types_service
                      , get_colours_service , get_insurance_policies_service , get_insurance_companies_service , get_TC_nos_service , get_tariff_groups_service ,
                        get_company_branches_service , get_locations_service , get_statuses_service, get_contract_types_service, get_customers_lookup_service,
                        get_application_users_service, get_sales_persons_service, get_payment_modes_service, get_discount_types_service,
                        get_billing_types_service, get_visa_types_service, get_license_types_service, get_nationalities_service,
                        get_fuel_levels_service, get_customer_types_service, get_confirmation_ref_types_service, get_contract_statuses_service,
                        get_customer_users_service)
from app.database.session import get_db

router = APIRouter(prefix="/lookups", tags=["Lookups"])

@router.get("/states")
def get_states(db:Session = Depends(get_db)):
    return get_states_service(db)

@router.get("/plate-categories")
def get_plate_categories(state_id:int, db:Session = Depends(get_db)):
    return get_plate_categories_service(db,state_id)

@router.get("/plate-codes")
def get_plate_codes(plate_category_id:int, db:Session = Depends(get_db)):
    return get_plate_codes_service(db,plate_category_id)

@router.get("/makes")
def get_makes(db:Session = Depends(get_db)):
    return get_makes_service(db)

@router.get("/models")
def get_models(make_id:int, db:Session = Depends(get_db)):
    return get_models_service(db,make_id)

@router.get("/engine-capacities")
def get_engine_capacities(model_id:int, db:Session = Depends(get_db)):
    return get_engine_capacities_service(db,model_id)


@router.get("/vehicle-types")
def get_vehicle_types(db: Session = Depends(get_db)):
    return get_veh_types_service(db)


@router.get("/fuel-types")
def get_fuel_types(db: Session = Depends(get_db)):
    return get_fuel_types_service(db)


@router.get("/fuel-capacity-units")
def get_fuel_capacity_units(db: Session = Depends(get_db)):
    return get_fuel_capacity_units_service(db)


@router.get("/transmission-types")
def get_transmission_types(db: Session = Depends(get_db)):
    return get_transmission_types_service(db)


@router.get("/colours")
def get_colours(db: Session = Depends(get_db)):
    return get_colours_service(db)


@router.get("/insurance-policies")
def get_insurance_policies(db: Session = Depends(get_db)):
    return get_insurance_policies_service(db)


@router.get("/insurance-companies")
def get_insurance_companies(db: Session = Depends(get_db)):
    return get_insurance_companies_service(db)


@router.get("/tc-nos")
def get_tc_nos(db: Session = Depends(get_db)):
    return get_TC_nos_service(db)


@router.get("/tariff-groups")
def get_tariff_groups(db: Session = Depends(get_db)):
    return get_tariff_groups_service(db)


@router.get("/company-branches")
def get_company_branches(db: Session = Depends(get_db)):
    return get_company_branches_service(db)


@router.get("/locations")
def get_locations(db: Session = Depends(get_db)):
    return get_locations_service(db)


@router.get("/statuses")
def get_statuses(db: Session = Depends(get_db)):
    return get_statuses_service(db)

@router.get("/insurance-types")
def get_insurance_types(db: Session = Depends(get_db)):
    from .service import get_insurance_types_service
    return get_insurance_types_service(db)

@router.get("/contract-types")
def get_contract_types(db: Session = Depends(get_db)):
    return get_contract_types_service(db)

@router.get("/customers")
def get_customers_lookup(q: str | None = None, db: Session = Depends(get_db)):
    return get_customers_lookup_service(db, q)

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return get_application_users_service(db)

@router.get("/application-users")
def get_application_users(db: Session = Depends(get_db)):
    return get_application_users_service(db)

@router.get("/customer-users")
def get_customer_users(customer_id: int, q: str | None = None, db: Session = Depends(get_db)):
    return get_customer_users_service(db, customer_id, q)

@router.get("/sales-persons")
def get_sales_persons(db: Session = Depends(get_db)):
    return get_sales_persons_service(db)

@router.get("/payment-modes")
def get_payment_modes(db: Session = Depends(get_db)):
    return get_payment_modes_service(db)

@router.get("/discount-types")
def get_discount_types(db: Session = Depends(get_db)):
    return get_discount_types_service(db)

@router.get("/billing-types")
def get_billing_types(db: Session = Depends(get_db)):
    return get_billing_types_service(db)

@router.get("/visa-types")
def get_visa_types(db: Session = Depends(get_db)):
    return get_visa_types_service(db)

@router.get("/license-types")
def get_license_types(db: Session = Depends(get_db)):
    return get_license_types_service(db)

@router.get("/nationalities")
def get_nationalities(db: Session = Depends(get_db)):
    return get_nationalities_service(db)

@router.get("/fuel-levels")
def get_fuel_levels(db: Session = Depends(get_db)):
    return get_fuel_levels_service(db)

@router.get("/customer-types")
def get_customer_types(db: Session = Depends(get_db)):
    return get_customer_types_service(db)

@router.get("/confirmation-ref-types")
def get_confirmation_ref_types(db: Session = Depends(get_db)):
    return get_confirmation_ref_types_service(db)

@router.get("/contract-statuses")
def get_contract_statuses(db: Session = Depends(get_db)):
    return get_contract_statuses_service(db)
