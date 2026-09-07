from sqlalchemy import String, cast, or_, select
from app.generated_models.models import (
    TblAccountLedger,
    VTContractDriverDtls,
    VTContractMaster,
    VTContractVehicleMaster,
    VTVehVehicleMaster,
)

CONTRACT_TABLE = VTContractMaster.__table__
DRIVER_TABLE = VTContractDriverDtls.__table__
CONTRACT_VEHICLE_TABLE = VTContractVehicleMaster.__table__
CUSTOMER_TABLE = TblAccountLedger.__table__
VEHICLE_TABLE = VTVehVehicleMaster.__table__


def get_customer(db, customer_id):
    return db.execute(
        select(CUSTOMER_TABLE).where(
            CUSTOMER_TABLE.c.ledgerId == customer_id,
            CUSTOMER_TABLE.c.accountGroupId == 26,
        )
    ).mappings().first()


def get_vehicle(db, vehicle_id):
    return db.execute(
        select(VEHICLE_TABLE).where(VEHICLE_TABLE.c.VehicleId == vehicle_id)
    ).mappings().first()


def create_contract(db, contract_values, driver_values, vehicle_values):
    result = db.execute(CONTRACT_TABLE.insert().values(**contract_values))
    contract_id = result.inserted_primary_key[0]
    db.execute(DRIVER_TABLE.insert().values(**driver_values, ContractId=contract_id))
    db.execute(CONTRACT_VEHICLE_TABLE.insert().values(**vehicle_values, ContractId=contract_id))
    return contract_id


def get_contract(db, contract_id):
    return db.execute(
        select(CONTRACT_TABLE).where(CONTRACT_TABLE.c.ContractId == contract_id)
    ).mappings().first()


def get_driver(db, contract_id):
    return db.execute(
        select(DRIVER_TABLE).where(DRIVER_TABLE.c.ContractId == contract_id)
    ).mappings().first()


def get_vehicle_assignment(db, contract_id):
    return db.execute(
        select(CONTRACT_VEHICLE_TABLE).where(CONTRACT_VEHICLE_TABLE.c.ContractId == contract_id)
    ).mappings().first()


def list_contract_view(db, customer_name=None, agreement_no=None, vehicle=None, offset=0, limit=100):
    query = (
        select(
            CONTRACT_TABLE.c.ContractId,
            CONTRACT_TABLE.c.RTACode,
            CONTRACT_TABLE.c.ContractRefNo,
            CONTRACT_TABLE.c.CustomerName,
            CONTRACT_TABLE.c.ContractStartDate,
            CONTRACT_TABLE.c.ContractExpectedEndDate,
            CONTRACT_TABLE.c.Rate,
            CONTRACT_TABLE.c.SalikCharges,
            CONTRACT_TABLE.c.TrafficCharges,
            CONTRACT_TABLE.c.Advance,
            CONTRACT_TABLE.c.VehicleId.label("ContractVehicleId"),
            CONTRACT_VEHICLE_TABLE.c.VehicleId.label("AssignedVehicleId"),
            CONTRACT_VEHICLE_TABLE.c.DatetimeOut,
            CONTRACT_VEHICLE_TABLE.c.DatetimeIn,
            VEHICLE_TABLE.c.PlateNo,
            VEHICLE_TABLE.c.VHType,
        )
        .select_from(
            CONTRACT_TABLE.outerjoin(
                CONTRACT_VEHICLE_TABLE,
                CONTRACT_VEHICLE_TABLE.c.ContractId == CONTRACT_TABLE.c.ContractId,
            ).outerjoin(
                VEHICLE_TABLE,
                VEHICLE_TABLE.c.VehicleId == CONTRACT_VEHICLE_TABLE.c.VehicleId,
            )
        )
    )
    if customer_name:
        query = query.where(CONTRACT_TABLE.c.CustomerName.icontains(customer_name, autoescape=True))
    if agreement_no:
        query = query.where(
            or_(
                CONTRACT_TABLE.c.ContractRefNo.icontains(agreement_no, autoescape=True),
                CONTRACT_TABLE.c.RTACode.icontains(agreement_no, autoescape=True),
            )
        )
    if vehicle:
        query = query.where(
            or_(
                VEHICLE_TABLE.c.PlateNo.icontains(vehicle, autoescape=True),
                VEHICLE_TABLE.c.VHType.icontains(vehicle, autoescape=True),
                cast(VEHICLE_TABLE.c.VehicleId, String).icontains(vehicle, autoescape=True),
            )
        )
    return db.execute(
        query.order_by(CONTRACT_TABLE.c.ContractId.desc()).offset(offset).limit(limit)
    ).mappings().all()


def list_drivers(db, contract_id=None, q=None, offset=0, limit=100):
    query = select(DRIVER_TABLE)
    if contract_id is not None:
        query = query.where(DRIVER_TABLE.c.ContractId == contract_id)
    if q:
        query = query.where(DRIVER_TABLE.c.UserName.icontains(q, autoescape=True))
    return db.execute(
        query.order_by(DRIVER_TABLE.c.ContractDriverId).offset(offset).limit(limit)
    ).mappings().all()


def get_driver_by_id(db, driver_id):
    return db.execute(
        select(DRIVER_TABLE).where(DRIVER_TABLE.c.ContractDriverId == driver_id)
    ).mappings().first()


def create_driver(db, values):
    result = db.execute(DRIVER_TABLE.insert().values(**values))
    return result.inserted_primary_key[0]


def update_driver(db, driver_id, values):
    db.execute(DRIVER_TABLE.update().where(DRIVER_TABLE.c.ContractDriverId == driver_id).values(**values))


def delete_driver(db, driver_id):
    db.execute(DRIVER_TABLE.delete().where(DRIVER_TABLE.c.ContractDriverId == driver_id))
