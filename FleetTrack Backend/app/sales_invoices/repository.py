from sqlalchemy import and_, func, or_, select, text

from app.generated_models.models import Base


SALES_MASTER = Base.metadata.tables["tbl_SalesMaster"]
SALES_DETAILS = Base.metadata.tables["tbl_SalesDetails"]
SALES_BILL_TAX = Base.metadata.tables["tbl_SalesBillTax"]
VOUCHER_TYPE = Base.metadata.tables["tbl_VoucherType"]
VOUCHER_TYPE_TAX = Base.metadata.tables["tbl_VoucherTypeTax"]
ITEM_TYPE = Base.metadata.tables["tbl_SalesDetailItemType"]
TAX = Base.metadata.tables["tbl_Tax"]
UNIT = Base.metadata.tables["tbl_Unit"]
LEDGER = Base.metadata.tables["tbl_AccountLedger"]
EMPLOYEE = Base.metadata.tables["tbl_Employee"]
EXCHANGE_RATE = Base.metadata.tables["tbl_ExchangeRate"]
CURRENCY = Base.metadata.tables["tbl_Currency"]
FINANCIAL_YEAR = Base.metadata.tables["tbl_FinancialYear"]
SUFFIX_PREFIX = Base.metadata.tables["tbl_SuffixPrefix"]
LOCATION = Base.metadata.tables["VT_Veh_LocationMaster"]
CONTRACT = Base.metadata.tables["VT_ContractMaster"]
CONTRACT_VEHICLE = Base.metadata.tables["VT_ContractVehicleMaster"]
VEHICLE = Base.metadata.tables["VT_Veh_VehicleMaster"]
PLATE_CODE = Base.metadata.tables["VT_Veh_PlateCodeMaster"]
TRAFFIC_FINE = Base.metadata.tables["Traffic_Fine"]
SALIK_TOLL = Base.metadata.tables["Salik_Toll"]


def get_voucher_type(db, name):
    return db.execute(
        select(VOUCHER_TYPE).where(VOUCHER_TYPE.c.voucherTypeName == name, VOUCHER_TYPE.c.isActive == True)
    ).mappings().first()


def get_invoice_header(db, sales_master_id):
    return db.execute(
        select(
            SALES_MASTER,
            VOUCHER_TYPE.c.voucherTypeName.label("voucherTypeName"),
            LEDGER.c.ledgerName.label("salesAccountName"),
        )
        .select_from(
            SALES_MASTER.outerjoin(VOUCHER_TYPE, VOUCHER_TYPE.c.voucherTypeId == SALES_MASTER.c.voucherTypeId)
            .outerjoin(LEDGER, LEDGER.c.ledgerId == SALES_MASTER.c.salesAccount)
        )
        .where(SALES_MASTER.c.salesMasterId == sales_master_id)
    ).mappings().first()


def list_invoice_lines(db, sales_master_id):
    return db.execute(
        select(
            SALES_DETAILS,
            ITEM_TYPE.c.ItemTypeName.label("itemTypeName"),
            UNIT.c.unitName.label("unitName"),
            TAX.c.taxName.label("taxName"),
            TAX.c.rate.label("taxRate"),
        )
        .select_from(
            SALES_DETAILS.outerjoin(ITEM_TYPE, ITEM_TYPE.c.ItemType == SALES_DETAILS.c.itemTypeId)
            .outerjoin(UNIT, UNIT.c.unitId == SALES_DETAILS.c.unitId)
            .outerjoin(TAX, TAX.c.taxId == SALES_DETAILS.c.taxId)
        )
        .where(SALES_DETAILS.c.salesMasterId == sales_master_id)
        .order_by(SALES_DETAILS.c.slNo, SALES_DETAILS.c.salesDetailsId)
    ).mappings().all()


def list_invoice_taxes(db, sales_master_id):
    return db.execute(
        select(SALES_BILL_TAX.c.taxId, TAX.c.taxName, SALES_BILL_TAX.c.taxAmount)
        .select_from(SALES_BILL_TAX.outerjoin(TAX, TAX.c.taxId == SALES_BILL_TAX.c.taxId))
        .where(SALES_BILL_TAX.c.salesMasterId == sales_master_id)
        .order_by(SALES_BILL_TAX.c.taxId)
    ).mappings().all()


def list_invoices(db, q=None, invoice_type_id=None, posted=None, offset=0, limit=10):
    query = select(
        SALES_MASTER.c.salesMasterId,
        SALES_MASTER.c.voucherTypeId,
        SALES_MASTER.c.voucherNo,
        SALES_MASTER.c.invoiceNo,
        SALES_MASTER.c.date.label("invoiceDate"),
        SALES_MASTER.c.customerName,
        SALES_MASTER.c.contractRefNo,
        SALES_MASTER.c.vehicleNos,
        SALES_MASTER.c.grandTotal,
        SALES_MASTER.c.isPosted,
    ).where(SALES_MASTER.c.voucherTypeId.in_([31, 32, 33, 34, 38]))
    if q:
        query = query.where(or_(
            SALES_MASTER.c.invoiceNo.icontains(q, autoescape=True),
            SALES_MASTER.c.voucherNo.icontains(q, autoescape=True),
            SALES_MASTER.c.customerName.icontains(q, autoescape=True),
            SALES_MASTER.c.contractRefNo.icontains(q, autoescape=True),
            SALES_MASTER.c.vehicleNos.icontains(q, autoescape=True),
        ))
    if invoice_type_id is not None:
        query = query.where(SALES_MASTER.c.voucherTypeId == invoice_type_id)
    if posted is not None:
        query = query.where(SALES_MASTER.c.isPosted == posted)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    rows = db.execute(query.order_by(SALES_MASTER.c.salesMasterId.desc()).offset(offset).limit(limit)).mappings().all()
    return rows, total


def get_customer(db, customer_id):
    return db.execute(
        select(LEDGER).where(LEDGER.c.ledgerId == customer_id, LEDGER.c.accountGroupId == 26)
    ).mappings().first()


def get_contract(db, contract_id):
    return db.execute(select(CONTRACT).where(CONTRACT.c.ContractId == contract_id)).mappings().first()


def contracts_for_customer(db, customer_id):
    return db.execute(
        select(
            CONTRACT.c.ContractId,
            CONTRACT.c.ContractRefNo,
            CONTRACT.c.ContractStartDate,
            CONTRACT.c.ContractExpectedEndDate,
            CONTRACT.c.Status,
        )
        .where(CONTRACT.c.CustomerId == customer_id)
        .order_by(CONTRACT.c.ContractId.desc())
    ).mappings().all()


def vehicle_belongs_to_contract(db, contract_id, vehicle_id):
    return db.execute(
        select(CONTRACT_VEHICLE.c.Id).where(
            CONTRACT_VEHICLE.c.ContractId == contract_id,
            CONTRACT_VEHICLE.c.VehicleId == vehicle_id,
        )
    ).first() is not None


def get_vehicle(db, vehicle_id):
    return db.execute(select(VEHICLE).where(VEHICLE.c.VehicleId == vehicle_id)).mappings().first()


def contract_vehicles(db, contract_id):
    return db.execute(
        select(
            VEHICLE.c.VehicleId,
            VEHICLE.c.PlateNo,
            VEHICLE.c.StatusId,
            PLATE_CODE.c.PlateCodeName,
        )
        .select_from(
            CONTRACT_VEHICLE.join(VEHICLE, VEHICLE.c.VehicleId == CONTRACT_VEHICLE.c.VehicleId)
            .outerjoin(PLATE_CODE, PLATE_CODE.c.PlateCodeId == VEHICLE.c.PlateCodeId)
        )
        .where(CONTRACT_VEHICLE.c.ContractId == contract_id)
        .distinct()
        .order_by(VEHICLE.c.PlateNo, VEHICLE.c.VehicleId)
    ).mappings().all()


def registered_vehicles(db):
    return db.execute(
        select(
            VEHICLE.c.VehicleId,
            VEHICLE.c.PlateNo,
            VEHICLE.c.StatusId,
            PLATE_CODE.c.PlateCodeName,
        )
        .select_from(VEHICLE.outerjoin(PLATE_CODE, PLATE_CODE.c.PlateCodeId == VEHICLE.c.PlateCodeId))
        .order_by(VEHICLE.c.PlateNo, VEHICLE.c.VehicleId)
    ).mappings().all()


def get_lookup(db, table, key, value):
    return db.execute(select(table).where(table.c[key] == value)).mappings().first()


def get_financial_year(db, invoice_date):
    return db.execute(
        select(FINANCIAL_YEAR).where(
            FINANCIAL_YEAR.c.fromDate <= invoice_date,
            FINANCIAL_YEAR.c.toDate >= invoice_date,
        )
    ).mappings().first()


def get_suffix_prefix(db, voucher_type_id, invoice_date):
    return db.execute(
        select(SUFFIX_PREFIX)
        .where(
            SUFFIX_PREFIX.c.voucherTypeId == voucher_type_id,
            SUFFIX_PREFIX.c.fromDate <= invoice_date,
            SUFFIX_PREFIX.c.toDate >= invoice_date,
        )
        .order_by(SUFFIX_PREFIX.c.suffixprefixId.desc())
    ).mappings().first()


def create_sales_master(db, values):
    # The legacy procedure owns invoice/voucher numbering and location persistence.
    result = db.execute(text("""
        EXEC dbo.SalesMasterAdd
            @voucherNo=:voucherNo, @invoiceNo=:invoiceNo, @voucherTypeId=:voucherTypeId,
            @suffixPrefixId=:suffixPrefixId, @date=:date, @creditPeriod=:creditPeriod,
            @lpoNo=:lpoNo, @ledgerId=:ledgerId, @employeeId=:employeeId,
            @salesAccount=:salesAccount, @narration=:narration, @customerName=:customerName,
            @exchangeRateId=:exchangeRateId, @taxAmount=:taxAmount,
            @additionalCost=:additionalCost, @billDiscount=:billDiscount,
            @grandTotal=:grandTotal, @totalAmount=:totalAmount, @userId=:userId,
            @POS=:POS, @counterId=:counterId, @financialYearId=:financialYearId,
            @extraDate=:extraDate, @extra1=:extra1, @extra2=:extra2,
            @contractId=:contractId, @contractRefNo=:contractRefNo, @isPosted=:isPosted
    """), values)
    return int(result.scalar_one())


def update_sales_master(db, sales_master_id, values):
    db.execute(SALES_MASTER.update().where(SALES_MASTER.c.salesMasterId == sales_master_id).values(**values))


def replace_details(db, sales_master_id, lines, taxes):
    db.execute(SALES_BILL_TAX.delete().where(SALES_BILL_TAX.c.salesMasterId == sales_master_id))
    db.execute(SALES_DETAILS.delete().where(SALES_DETAILS.c.salesMasterId == sales_master_id))
    if lines:
        db.execute(SALES_DETAILS.insert(), lines)
    if taxes:
        db.execute(SALES_BILL_TAX.insert(), taxes)


def delete_draft(db, sales_master_id, voucher_type_id, voucher_no):
    # Preserve the legacy audit behavior: copy before deleting the header/details.
    db.execute(text("""
        EXEC dbo.SalesInvoiceDelete
            @salesMasterId=:sales_master_id,
            @voucherTypeId=:voucher_type_id,
            @voucherNo=:voucher_no
    """), {
        "sales_master_id": sales_master_id,
        "voucher_type_id": voucher_type_id,
        "voucher_no": voucher_no,
    })


def invoice_types(db):
    return db.execute(
        select(VOUCHER_TYPE.c.voucherTypeId, VOUCHER_TYPE.c.voucherTypeName)
        .where(VOUCHER_TYPE.c.voucherTypeId.in_([31, 32, 33, 34, 38]), VOUCHER_TYPE.c.isActive == True)
        .order_by(VOUCHER_TYPE.c.voucherTypeId)
    ).mappings().all()


def item_types(db, voucher_type_id):
    return db.execute(
        select(ITEM_TYPE.c.ItemType, ITEM_TYPE.c.ItemTypeName, ITEM_TYPE.c.TaxId, TAX.c.rate.label("taxRate"))
        .select_from(ITEM_TYPE.outerjoin(TAX, TAX.c.taxId == ITEM_TYPE.c.TaxId))
        .where(ITEM_TYPE.c.VoucherType == voucher_type_id, ITEM_TYPE.c.IsActive == True)
        .order_by(ITEM_TYPE.c.ItemTypeName)
    ).mappings().all()


def taxes(db, voucher_type_id):
    # Voucher mappings supply the taxable options. Item defaults also expose the
    # legacy NA tax used for untaxed principal Fine/Salik lines.
    mapped_tax_ids = select(VOUCHER_TYPE_TAX.c.taxId).where(VOUCHER_TYPE_TAX.c.voucherTypeId == voucher_type_id)
    item_default_tax_ids = select(ITEM_TYPE.c.TaxId).where(
        ITEM_TYPE.c.VoucherType == voucher_type_id,
        ITEM_TYPE.c.IsActive == True,
    )
    return db.execute(
        select(TAX.c.taxId, TAX.c.taxName, TAX.c.rate)
        .where(TAX.c.isActive == True, or_(TAX.c.taxId.in_(mapped_tax_ids), TAX.c.taxId.in_(item_default_tax_ids)))
        .order_by(TAX.c.taxName)
    ).mappings().all()


def tax_is_available_for_invoice(db, voucher_type_id, item_type_id, tax_id):
    return db.execute(
        select(TAX.c.taxId)
        .where(
            TAX.c.taxId == tax_id,
            TAX.c.isActive == True,
            or_(
                TAX.c.taxId.in_(select(VOUCHER_TYPE_TAX.c.taxId).where(VOUCHER_TYPE_TAX.c.voucherTypeId == voucher_type_id)),
                and_(
                    ITEM_TYPE.c.ItemType == item_type_id,
                    ITEM_TYPE.c.VoucherType == voucher_type_id,
                    ITEM_TYPE.c.TaxId == tax_id,
                ),
            ),
        )
    ).first() is not None


def units(db):
    return db.execute(select(UNIT.c.unitId, UNIT.c.unitName).order_by(UNIT.c.unitName)).mappings().all()


def get_unit_by_name(db, name):
    return db.execute(select(UNIT).where(UNIT.c.unitName == name)).mappings().first()


def get_item_type_by_name(db, voucher_type_id, name):
    return db.execute(
        select(ITEM_TYPE).where(
            ITEM_TYPE.c.VoucherType == voucher_type_id,
            ITEM_TYPE.c.ItemTypeName == name,
            ITEM_TYPE.c.IsActive == True,
        )
    ).mappings().first()


def sales_accounts(db):
    return db.execute(
        select(LEDGER.c.ledgerId, LEDGER.c.ledgerName)
        .where(LEDGER.c.ledgerName.is_not(None))
        .order_by(LEDGER.c.ledgerName)
    ).mappings().all()


def locations(db):
    return db.execute(select(LOCATION.c.LocationId, LOCATION.c.LocationName).order_by(LOCATION.c.LocationName)).mappings().all()


def exchange_rates(db):
    return db.execute(select(EXCHANGE_RATE.c.exchangeRateId, EXCHANGE_RATE.c.rate).order_by(EXCHANGE_RATE.c.exchangeRateId)).mappings().all()


def exchange_rates_with_currency(db):
    return db.execute(
        select(
            EXCHANGE_RATE.c.exchangeRateId,
            EXCHANGE_RATE.c.rate,
            EXCHANGE_RATE.c.currencyId,
            CURRENCY.c.currencyName,
            CURRENCY.c.currencySymbol,
        )
        .select_from(EXCHANGE_RATE.outerjoin(CURRENCY, CURRENCY.c.currencyId == EXCHANGE_RATE.c.currencyId))
        .order_by(EXCHANGE_RATE.c.exchangeRateId)
    ).mappings().all()


def unposted_fines_for_contract(db, contract_id):
    return db.execute(
        select(
            TRAFFIC_FINE.c.TICKETNO,
            TRAFFIC_FINE.c.VEHICLEID,
            TRAFFIC_FINE.c.FINEDATETIME,
            TRAFFIC_FINE.c.AUTHORITY,
            TRAFFIC_FINE.c.FINEDESCRIPTION,
            TRAFFIC_FINE.c.AMOUNT,
        )
        .select_from(TRAFFIC_FINE.join(CONTRACT_VEHICLE, CONTRACT_VEHICLE.c.VehicleId == TRAFFIC_FINE.c.VEHICLEID))
        .where(CONTRACT_VEHICLE.c.ContractId == contract_id, TRAFFIC_FINE.c.ISPOSTED == False)
        .distinct()
        .order_by(TRAFFIC_FINE.c.FINEDATETIME, TRAFFIC_FINE.c.TICKETNO)
    ).mappings().all()


def unposted_salik_for_contract(db, contract_id, from_date, to_date):
    assigned_during_toll = and_(
        or_(CONTRACT_VEHICLE.c.DatetimeOut.is_(None), CONTRACT_VEHICLE.c.DatetimeOut <= SALIK_TOLL.c.DATEANDTIME),
        or_(CONTRACT_VEHICLE.c.DatetimeIn.is_(None), CONTRACT_VEHICLE.c.DatetimeIn >= SALIK_TOLL.c.DATEANDTIME),
    )
    return db.execute(
        select(
            SALIK_TOLL.c.TRANSID,
            SALIK_TOLL.c.DATEANDTIME,
            SALIK_TOLL.c.TAGNO,
            SALIK_TOLL.c.LOCATION,
            SALIK_TOLL.c.DIRECTION,
            SALIK_TOLL.c.AMOUNT,
            VEHICLE.c.VehicleId,
        )
        .select_from(
            SALIK_TOLL.join(VEHICLE, VEHICLE.c.SalikTag == SALIK_TOLL.c.TAGNO)
            .join(
                CONTRACT_VEHICLE,
                and_(CONTRACT_VEHICLE.c.VehicleId == VEHICLE.c.VehicleId, assigned_during_toll),
            )
        )
        .where(
            CONTRACT_VEHICLE.c.ContractId == contract_id,
            SALIK_TOLL.c.ISPOSTED == False,
            SALIK_TOLL.c.DATEANDTIME >= from_date,
            SALIK_TOLL.c.DATEANDTIME <= to_date,
        )
        .distinct()
        .order_by(SALIK_TOLL.c.DATEANDTIME, SALIK_TOLL.c.TRANSID)
    ).mappings().all()
