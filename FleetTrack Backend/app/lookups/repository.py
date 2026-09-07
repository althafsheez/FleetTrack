from sqlalchemy import select
from sqlalchemy.orm import Session 
from app.generated_models.models import ( TblAccountLedger, TblEmployee, TblPaymentMode, TblVehicleContractType, VTCompanyBranchMaster, VTContractDriverDtls, VTContractMaster, VTDLTypes, VTLookupTable, VTVisaType, VTVehColourMaster, VTVehFuelLevelMaster, VTVehInsuranceCompanyMaster, VTVehInsurancePolicyMaster, VTVehLocationMaster, VTVehPlateCodeMaster , VTVehStateMaster , VTVehPlateCategoryMaster
                                          , VTVehMakeMaster , VTVehModelMaster ,
                                          VTVehEngineCapacityMaster, VTVehTCNoMaster, VTVehTariffGroupMaster , VTVehTypeMaster , VTVehFuelTypeMaster 
                                          , VTVehFuelCapacityUnitMaster , VTVehTransmissionMaster ,VTStatusMaster, t_VT_ApplicationUsers, t_VT_DiscountType, t_tbl_SalesInvoiceBillingType, t_VT_Nationality )



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

def get_insurance_types(db: Session):
    from app.generated_models.models import VTVehInsuranceTypeMaster
    return db.query(VTVehInsuranceTypeMaster).all()

def get_contract_types(db: Session):
    table = TblVehicleContractType.__table__
    return db.execute(select(table).order_by(table.c.contractType)).mappings().all()

def get_customers_lookup(db: Session, q: str | None = None):
    table = TblAccountLedger.__table__
    query = select(
        table.c.ledgerId,
        table.c.ledgerName,
        table.c.mobile,
        table.c.phone,
        table.c.email,
        table.c.address,
        table.c.CustomerIdNo,
        table.c.CustomerIdExpiry,
        table.c.isCorporate,
    ).where(table.c.accountGroupId == 26)
    if q:
        query = query.where(table.c.ledgerName.icontains(q, autoescape=True))
    return db.execute(query.order_by(table.c.ledgerName)).mappings().all()

def get_application_users(db: Session):
    table = t_VT_ApplicationUsers
    return db.execute(select(
        table.c.UserID,
        table.c.UserName,
        table.c.DisplayName,
        table.c.UserCode,
        table.c.SalesPersonId,
    ).order_by(table.c.UserID)).mappings().all()

def get_customer_users(db: Session, customer_id: int, q: str | None = None):
    contract = VTContractMaster.__table__
    driver = VTContractDriverDtls.__table__
    query = select(
        driver.c.ContractDriverId,
        driver.c.ContractId,
        driver.c.UserName,
        driver.c.Phone,
        driver.c.Mobile,
        driver.c.Email,
        driver.c.DateOfBirth,
        driver.c.NationalityId,
        driver.c.PassportNo,
        driver.c.PassportExpiryDate,
        driver.c.VisaType,
        driver.c.VisaExpiryDate,
        driver.c.DrivingLicenseType,
        driver.c.DrivingLicenseNo,
        driver.c.DLPlaceOfIssue,
        driver.c.DLIssueDate,
        driver.c.DLExpiryDate,
    ).select_from(
        driver.join(contract, driver.c.ContractId == contract.c.ContractId)
    ).where(contract.c.CustomerId == customer_id)
    if q:
        query = query.where(driver.c.UserName.icontains(q, autoescape=True))
    return db.execute(query.distinct().order_by(driver.c.UserName)).mappings().all()

def get_sales_persons(db: Session):
    table = TblEmployee.__table__
    return db.execute(select(
        table.c.employeeId,
        table.c.employeeName,
        table.c.employeeCode,
        table.c.isActive,
    ).order_by(table.c.employeeId)).mappings().all()

def get_payment_modes(db: Session):
    table = TblPaymentMode.__table__
    return db.execute(select(table).order_by(table.c.paymentMode)).mappings().all()

def get_discount_types(db: Session):
    table = t_VT_DiscountType
    return db.execute(select(table).order_by(table.c.DiscountTypeId)).mappings().all()

def get_billing_types(db: Session):
    table = t_tbl_SalesInvoiceBillingType
    return db.execute(select(table).order_by(table.c.invoiceTypeId)).mappings().all()

def get_visa_types(db: Session):
    table = VTVisaType.__table__
    return db.execute(select(table).order_by(table.c.Id)).mappings().all()

def get_license_types(db: Session):
    table = VTDLTypes.__table__
    return db.execute(select(table).order_by(table.c.DLTypeId)).mappings().all()

def get_nationalities(db: Session):
    table = t_VT_Nationality
    return db.execute(select(table).order_by(table.c.NationalityName)).mappings().all()

def get_fuel_levels(db: Session):
    table = VTVehFuelLevelMaster.__table__
    return db.execute(select(table).order_by(table.c.FuelLevelId)).mappings().all()

def get_customer_types(db: Session):
    table = VTLookupTable.__table__
    return db.execute(
        select(table)
        .where(table.c.LookupType == "CustomerType")
        .order_by(table.c.LookupId)
    ).mappings().all()

def get_confirmation_ref_types(db: Session):
    table = VTLookupTable.__table__
    return db.execute(
        select(table)
        .where(table.c.LookupType.in_(["Corporate", "Individual"]))
        .order_by(table.c.LookupId)
    ).mappings().all()

def get_contract_statuses(db: Session):
    table = VTStatusMaster.__table__
    return db.execute(
        select(table)
        .where(table.c.StatusTypeId == 2)
        .order_by(table.c.StatusId)
    ).mappings().all()
