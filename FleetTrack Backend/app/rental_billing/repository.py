from sqlalchemy import and_, select

from app.generated_models.models import Base


CONTRACT = Base.metadata.tables["VT_ContractMaster"]
CONTRACT_VEHICLE = Base.metadata.tables["VT_ContractVehicleMaster"]
SALES_MASTER = Base.metadata.tables["tbl_SalesMaster"]

RENTAL_VOUCHER_TYPE_ID = 31


def get_contract(db, contract_id, lock=False):
    query = select(CONTRACT).where(CONTRACT.c.ContractId == contract_id)
    if lock:
        query = query.with_hint(CONTRACT, "UPDLOCK, HOLDLOCK", dialect_name="mssql")
    return db.execute(query).mappings().first()


def get_current_vehicle_assignment(db, contract_id):
    return db.execute(
        select(CONTRACT_VEHICLE)
        .where(CONTRACT_VEHICLE.c.ContractId == contract_id)
        .order_by(CONTRACT_VEHICLE.c.Id.desc())
        .limit(1)
    ).mappings().first()


def has_rental_invoice_for_schedule(db, contract_id, invoice_date):
    return db.execute(
        select(SALES_MASTER.c.salesMasterId).where(
            SALES_MASTER.c.contractId == contract_id,
            SALES_MASTER.c.voucherTypeId == RENTAL_VOUCHER_TYPE_ID,
            SALES_MASTER.c.date == invoice_date,
        ).limit(1)
    ).first() is not None


def latest_rental_invoice(db, contract_id):
    return db.execute(
        select(SALES_MASTER)
        .where(
            SALES_MASTER.c.contractId == contract_id,
            SALES_MASTER.c.voucherTypeId == RENTAL_VOUCHER_TYPE_ID,
        )
        .order_by(SALES_MASTER.c.date.desc(), SALES_MASTER.c.salesMasterId.desc())
        .limit(1)
    ).mappings().first()


def previous_rental_invoice(db, contract_id, sales_master_id):
    return db.execute(
        select(SALES_MASTER)
        .where(
            SALES_MASTER.c.contractId == contract_id,
            SALES_MASTER.c.voucherTypeId == RENTAL_VOUCHER_TYPE_ID,
            SALES_MASTER.c.salesMasterId != sales_master_id,
        )
        .order_by(SALES_MASTER.c.date.desc(), SALES_MASTER.c.salesMasterId.desc())
        .limit(1)
    ).mappings().first()


def update_schedule(db, contract_id, next_invoice_date, last_invoice_date):
    db.execute(
        CONTRACT.update()
        .where(CONTRACT.c.ContractId == contract_id)
        .values(NextInvStDate=next_invoice_date, LastInvoiceDate=last_invoice_date)
    )


def due_contracts(db, as_of_date, open_status):
    return db.execute(
        select(
            CONTRACT.c.ContractId,
            CONTRACT.c.ContractRefNo,
            CONTRACT.c.CustomerId,
            CONTRACT.c.CustomerName,
            CONTRACT.c.ContractType,
            CONTRACT.c.PaymentType,
            CONTRACT.c.BillingType,
            CONTRACT.c.NextInvStDate,
        )
        .where(
            CONTRACT.c.Status == open_status,
            CONTRACT.c.PaymentType.in_([2, 3]),
            CONTRACT.c.NextInvStDate.is_not(None),
            CONTRACT.c.NextInvStDate <= as_of_date,
        )
        .order_by(CONTRACT.c.NextInvStDate, CONTRACT.c.ContractId)
    ).mappings().all()
