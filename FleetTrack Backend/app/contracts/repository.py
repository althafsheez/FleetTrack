from sqlalchemy import String, and_, cast, func, or_, select
from app.generated_models.models import (
    TblAccountLedger,
    TblVehicleContractType,
    VTContractDriverDtls,
    VTContractMaster,
    VTContractVehicleMaster,
    VTVehColourMaster,
    VTVehMakeMaster,
    VTVehModelMaster,
    VTVehPlateCodeMaster,
    VTVehTariffGroupMaster,
    VTVehVehicleMaster,
    t_VT_Nationality,
)

CONTRACT_TABLE = VTContractMaster.__table__
DRIVER_TABLE = VTContractDriverDtls.__table__
CONTRACT_VEHICLE_TABLE = VTContractVehicleMaster.__table__
CUSTOMER_TABLE = TblAccountLedger.__table__
VEHICLE_TABLE = VTVehVehicleMaster.__table__
CONTRACT_TYPE_TABLE = TblVehicleContractType.__table__
MODEL_TABLE = VTVehModelMaster.__table__
MAKE_TABLE = VTVehMakeMaster.__table__
COLOUR_TABLE = VTVehColourMaster.__table__
PLATE_CODE_TABLE = VTVehPlateCodeMaster.__table__
TARIFF_TABLE = VTVehTariffGroupMaster.__table__
NATIONALITY_TABLE = t_VT_Nationality


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
        select(DRIVER_TABLE)
        .where(DRIVER_TABLE.c.ContractId == contract_id)
        .order_by(DRIVER_TABLE.c.ContractDriverId)
    ).mappings().first()


def get_vehicle_assignment(db, contract_id):
    return db.execute(
        select(CONTRACT_VEHICLE_TABLE)
        .where(CONTRACT_VEHICLE_TABLE.c.ContractId == contract_id)
        .order_by(CONTRACT_VEHICLE_TABLE.c.Id)
    ).mappings().first()


def get_vehicle_assignment_by_id(db, contract_id, assignment_id):
    return db.execute(
        select(CONTRACT_VEHICLE_TABLE).where(
            and_(
                CONTRACT_VEHICLE_TABLE.c.ContractId == contract_id,
                CONTRACT_VEHICLE_TABLE.c.Id == assignment_id,
            )
        )
    ).mappings().first()


def get_contract_print_vehicle(db, vehicle_id):
    """Return only the vehicle and tariff labels needed by the paper agreement."""
    return db.execute(
        select(
            VEHICLE_TABLE.c.VehicleId,
            VEHICLE_TABLE.c.PlateNo,
            MODEL_TABLE.c.ModelName,
            MAKE_TABLE.c.MakeName,
            COLOUR_TABLE.c.ColourName,
            PLATE_CODE_TABLE.c.PlateCodeName,
            PLATE_CODE_TABLE.c.Code.label("PlateCode"),
            TARIFF_TABLE.c.AllowedKmsPerDay,
        )
        .select_from(
            VEHICLE_TABLE.outerjoin(MODEL_TABLE, MODEL_TABLE.c.ModelId == VEHICLE_TABLE.c.ModelId)
            .outerjoin(MAKE_TABLE, MAKE_TABLE.c.MakeId == MODEL_TABLE.c.MakeId)
            .outerjoin(COLOUR_TABLE, COLOUR_TABLE.c.ColourId == VEHICLE_TABLE.c.ColourId)
            .outerjoin(PLATE_CODE_TABLE, PLATE_CODE_TABLE.c.PlateCodeId == VEHICLE_TABLE.c.PlateCodeId)
            .outerjoin(TARIFF_TABLE, TARIFF_TABLE.c.TariffGroupId == VEHICLE_TABLE.c.TariffGroupId)
        )
        .where(VEHICLE_TABLE.c.VehicleId == vehicle_id)
    ).mappings().first()


def get_contract_type_name(db, contract_type):
    return db.execute(
        select(CONTRACT_TYPE_TABLE.c.contractTypeName).where(
            CONTRACT_TYPE_TABLE.c.contractType == contract_type
        )
    ).scalar_one_or_none()


def get_nationality_name(db, nationality_id):
    return db.execute(
        select(NATIONALITY_TABLE.c.NationalityName).where(
            NATIONALITY_TABLE.c.NationalityId == nationality_id
        )
    ).scalar_one_or_none()


def update_contract(db, contract_id, values):
    db.execute(
        CONTRACT_TABLE.update()
        .where(CONTRACT_TABLE.c.ContractId == contract_id)
        .values(**values)
    )


def update_vehicle_assignment(db, assignment_id, values):
    db.execute(
        CONTRACT_VEHICLE_TABLE.update()
        .where(CONTRACT_VEHICLE_TABLE.c.Id == assignment_id)
        .values(**values)
    )


def contract_view_query(customer_name=None, agreement_no=None, vehicle=None):
    query = (
        select(
            CONTRACT_TABLE.c.ContractId,
            CONTRACT_VEHICLE_TABLE.c.Id.label("AssignmentId"),
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
                CONTRACT_TABLE.c.ContractRefNo == agreement_no,
                CONTRACT_TABLE.c.RTACode == agreement_no,
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
    return query


def list_contract_view(db, customer_name=None, agreement_no=None, vehicle=None, offset=0, limit=100):
    query = contract_view_query(customer_name, agreement_no, vehicle)
    return db.execute(
        query.order_by(CONTRACT_TABLE.c.ContractId.desc(), CONTRACT_VEHICLE_TABLE.c.Id)
        .offset(offset)
        .limit(limit)
    ).mappings().all()


def count_contract_view(db, customer_name=None, agreement_no=None, vehicle=None):
    query = contract_view_query(customer_name, agreement_no, vehicle)
    return db.execute(select(func.count()).select_from(query.subquery())).scalar_one()


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
