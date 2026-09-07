from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException
from app.generated_models.models import Base
from app.master_data import database_errors, require_reference
from . import repository as repo

LEGACY_DATE = datetime(1900, 1, 1)
CONTRACT_STATUS_OPEN = 8
CONTRACT_VEHICLE_STATUS_ACTIVE = 10
DRIVER_STATUS_OPEN = 16
CUSTOMER_SOURCE_REFERRAL = 2
CORPORATE_CUSTOMER_TYPE = 10
INDIVIDUAL_CUSTOMER_TYPE = 11
CORPORATE_CONFIRMATION_REF = 4
INDIVIDUAL_CONFIRMATION_REF = 9

REFERENCES = {
    "ContractType": ("tbl_VehicleContractType", "contractType"),
    "ContractLocId": ("VT_Veh_LocationMaster", "LocationId"),
    "VehicleId": ("VT_Veh_VehicleMaster", "VehicleId"),
    "PaymentMode": ("tbl_PaymentMode", "paymentMode"),
    "DiscountType": ("VT_DiscountType", "DiscountTypeId"),
    "BillingType": ("tbl_SalesInvoiceBillingType", "invoiceTypeId"),
    "VisaType": ("VT_VisaType", "Id"),
    "DrivingLicenseType": ("VT_DLTypes", "DLTypeId"),
    "Nationality": ("VT_Nationality", "NationalityId"),
    "FuelLevelIdOut": ("VT_Veh_FuelLevelMaster", "FuelLevelId"),
    "LocationOut": ("VT_Veh_LocationMaster", "LocationId"),
    "SalesPersonId": ("tbl_Employee", "employeeId"),
    "CheckedOutBy": ("VT_ApplicationUsers", "UserID"),
}

DRIVER_REFERENCES = {
    "ContractId": ("VT_ContractMaster", "ContractId"),
    "VisaType": ("VT_VisaType", "Id"),
    "DrivingLicenseType": ("VT_DLTypes", "DLTypeId"),
    "NationalityId": ("VT_Nationality", "NationalityId"),
}


def _text(value, default=""):
    if value is None:
        return default
    return str(value)


def _customer_type(customer):
    return CORPORATE_CUSTOMER_TYPE if customer["isCorporate"] is True else INDIVIDUAL_CUSTOMER_TYPE


def _confirmation_ref_type(customer_type):
    return CORPORATE_CONFIRMATION_REF if customer_type == CORPORATE_CUSTOMER_TYPE else INDIVIDUAL_CONFIRMATION_REF


def _customer_id_no(customer):
    value = _text(customer["CustomerIdNo"], "0").strip()
    return value or "0"


def _customer_id_expiry(customer):
    return customer["CustomerIdExpiry"] or LEGACY_DATE


def _validate_references(db, payload):
    for field, (table, key) in REFERENCES.items():
        value = getattr(payload, field, None)
        require_reference(db, table, key, value, field)


def _validate_customer_type_references(db, customer_type):
    require_reference(db, "VT_LookupTable", "LookupId", CUSTOMER_SOURCE_REFERRAL, "CustomerSource")
    require_reference(db, "VT_LookupTable", "LookupId", customer_type, "CustomerType")
    require_reference(db, "VT_LookupTable", "LookupId", _confirmation_ref_type(customer_type), "ConfirmationRefType")


def _contract_values(payload, customer, now):
    ref_no = str(payload.ContractRefNo)
    customer_type = _customer_type(customer)
    phone = payload.Phone if payload.Phone is not None else _text(customer["phone"])
    mobile = payload.Mobile if payload.Mobile is not None else _text(customer["mobile"])
    address = payload.Address if payload.Address is not None else _text(customer["address"])
    email = payload.Email if payload.Email is not None else _text(customer["email"])
    fax = payload.Fax if payload.Fax is not None else "0"
    created_by = payload.CreatedBy

    return {
        "RTACode": ref_no,
        "ContractType": payload.ContractType,
        "ContractRefNo": ref_no,
        "ContractStartDate": payload.ContractStartDate,
        "ContractExpectedEndDate": payload.ContractExpectedEndDate,
        "ContractActualEndDate": payload.ContractExpectedEndDate,
        "ContractLocId": payload.ContractLocId,
        "CustomerName": _text(customer["ledgerName"]),
        "UserName": payload.UserName,
        "Address": address,
        "Phone": phone,
        "Mobile": mobile,
        "Fax": fax,
        "Email": email,
        "DateOfBirth": payload.DateOfBirth,
        "Nationality": payload.Nationality,
        "PassportNo": _customer_id_no(customer),
        "PassportExpiryDate": _customer_id_expiry(customer),
        "VisaType": payload.VisaType,
        "VisaExpiryDate": payload.VisaExpiryDate,
        "DrivingLicenseType": payload.DrivingLicenseType,
        "DrivingLicenseNo": payload.DrivingLicenseNo,
        "DLPlaceOfIssue": payload.DLPlaceOfIssue,
        "DLIssueDate": payload.DLIssueDate,
        "DLExpiryDate": payload.DLExpiryDate,
        "PaymentType": payload.ContractType,
        "Rate": payload.Rate,
        "DriverCharges": payload.DriverCharges,
        "AddDriverCharges": payload.AddDriverCharges,
        "CDW": payload.CDW,
        "PAI": payload.PAI,
        "ExcessKmCharge": payload.ExcessKmCharge,
        "FuelCharges": payload.FuelCharges,
        "SalikCharges": payload.SalikCharges,
        "ExcessInsCharges": payload.ExcessInsCharges,
        "TrafficCharges": payload.TrafficCharges,
        "MileageCap": payload.MileageCap,
        "OtherCharges": payload.OtherCharges,
        "DiscountType": payload.DiscountType,
        "Discount": payload.Discount,
        "Advance": payload.Advance,
        "Subtotal": payload.Subtotal,
        "PaymentMode": payload.PaymentMode,
        "CreditCardExpiryMonth": 0,
        "CreditCardExpiryYear": 0,
        "Status": CONTRACT_STATUS_OPEN,
        "CustomerId": payload.CustomerId,
        "SalesPersonId": payload.SalesPersonId,
        "Remarks": payload.Remarks,
        "RentalInvoiced": False,
        "SalikInvoiced": False,
        "FineInvoiced": False,
        "RepairCharged": False,
        "PenaltyCharged": False,
        "ExcessKmCharged": False,
        "OtherChargesCharged": False,
        "VehicleId": payload.VehicleId,
        "CreatedBy": created_by,
        "CreatedDate": now,
        "UpdatedBy": created_by,
        "UpdatedDate": now,
        "CustomerSource": CUSTOMER_SOURCE_REFERRAL,
        "CustomerType": customer_type,
        "ConfirmationRefType": _confirmation_ref_type(customer_type),
        "ConfirmationRefValue": payload.ConfirmationRefValue,
        "IsAdvanceInvoice": payload.IsAdvanceInvoice,
        "BillingType": payload.BillingType,
    }


def _driver_values(payload, customer):
    return {
        "UserName": payload.UserName,
        "Address": payload.Address if payload.Address is not None else _text(customer["address"]),
        "Mobile": payload.Mobile if payload.Mobile is not None else _text(customer["mobile"]),
        "Email": payload.Email if payload.Email is not None else _text(customer["email"]),
        "DateOfBirth": payload.DateOfBirth,
        "NationalityId": payload.Nationality,
        "PassportNo": _customer_id_no(customer),
        "PassportExpiryDate": _customer_id_expiry(customer),
        "VisaType": payload.VisaType,
        "VisaExpiryDate": payload.VisaExpiryDate,
        "DrivingLicenseType": payload.DrivingLicenseType,
        "DrivingLicenseNo": payload.DrivingLicenseNo,
        "DLPlaceOfIssue": payload.DLPlaceOfIssue,
        "DLIssueDate": payload.DLIssueDate,
        "DLExpiryDate": payload.DLExpiryDate,
        "DriverStatus": DRIVER_STATUS_OPEN,
        "Phone": payload.Phone if payload.Phone is not None else _text(customer["phone"]),
        "Fax": payload.Fax if payload.Fax is not None else "0",
    }


def _vehicle_values(payload):
    return {
        "VehicleId": payload.VehicleId,
        "ContractVehicleStatus": CONTRACT_VEHICLE_STATUS_ACTIVE,
        "DatetimeOut": payload.DatetimeOut or payload.ContractStartDate,
        "KmOut": payload.KmOut,
        "FuelLevelIdOut": payload.FuelLevelIdOut,
        "CheckedOutBy": payload.CheckedOutBy,
        "LocationOut": payload.LocationOut or payload.ContractLocId,
    }


def _response(contract, driver, vehicle_assignment, customer):
    values = dict(contract)
    values["driver"] = dict(driver)
    values["vehicle_assignment"] = dict(vehicle_assignment)
    values["CustomerIdNo"] = customer["CustomerIdNo"]
    values["CustomerIdExpiry"] = customer["CustomerIdExpiry"]
    return values


def create_contract(db, payload):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with database_errors(db):
        customer = repo.get_customer(db, payload.CustomerId)
        if customer is None:
            raise HTTPException(422, "CustomerId: selected customer does not exist")
        vehicle = repo.get_vehicle(db, payload.VehicleId)
        if vehicle is None:
            raise HTTPException(422, "VehicleId: selected vehicle does not exist")
        _validate_references(db, payload)
        _validate_customer_type_references(db, _customer_type(customer))

        contract_id = repo.create_contract(
            db,
            _contract_values(payload, customer, now),
            _driver_values(payload, customer),
            _vehicle_values(payload),
        )
        contract = repo.get_contract(db, contract_id)
        driver = repo.get_driver(db, contract_id)
        vehicle_assignment = repo.get_vehicle_assignment(db, contract_id)
        db.commit()
        return _response(contract, driver, vehicle_assignment, customer)


def _money(value):
    if value is None:
        return Decimal("0.00")
    return Decimal(value).quantize(Decimal("0.01"))


def _total_days(date_out, date_in):
    if date_out is None or date_in is None:
        return 0
    days = (date_in.date() - date_out.date()).days
    return max(days, 1)


def _vehicle_label(row):
    if row["PlateNo"]:
        return row["PlateNo"]
    if row["VHType"]:
        return row["VHType"]
    vehicle_id = row["AssignedVehicleId"] or row["ContractVehicleId"]
    return str(vehicle_id) if vehicle_id is not None else None


def list_contract_view(db, customer_name=None, agreement_no=None, vehicle=None, offset=0, limit=100):
    with database_errors(db):
        rows = repo.list_contract_view(
            db,
            customer_name=customer_name,
            agreement_no=agreement_no,
            vehicle=vehicle,
            offset=offset,
            limit=limit,
        )
        view = []
        for index, row in enumerate(rows, start=offset + 1):
            date_out = row["DatetimeOut"] or row["ContractStartDate"]
            date_in = row["DatetimeIn"] or row["ContractExpectedEndDate"]
            total_days = _total_days(date_out, date_in)
            rate = _money(row["Rate"])
            rent = (rate * Decimal(total_days)).quantize(Decimal("0.01"))
            salik = _money(row["SalikCharges"])
            fine = _money(row["TrafficCharges"])
            received = _money(row["Advance"])
            view.append(
                {
                    "slNo": index,
                    "contractId": row["ContractId"],
                    "agreementNo": row["ContractRefNo"] or row["RTACode"],
                    "customer": row["CustomerName"],
                    "dateOut": date_out,
                    "dateIn": date_in,
                    "totalDays": total_days,
                    "rate": rate,
                    "vehicleId": row["AssignedVehicleId"] or row["ContractVehicleId"],
                    "vehicle": _vehicle_label(row),
                    "rent": rent,
                    "salik": salik,
                    "fine": fine,
                    "received": received,
                    "pendingAmount": (rent + salik + fine - received).quantize(Decimal("0.01")),
                }
            )
        return view


def _validate_driver_references(db, values):
    for field, (table, key) in DRIVER_REFERENCES.items():
        if field in values:
            require_reference(db, table, key, values[field], field)


def list_drivers(db, **filters):
    with database_errors(db):
        return repo.list_drivers(db, **filters)


def get_driver_detail(db, driver_id):
    with database_errors(db):
        driver = repo.get_driver_by_id(db, driver_id)
        if driver is None:
            raise HTTPException(404, "Contract driver not found")
        return driver


def create_driver(db, payload):
    values = payload.model_dump()
    with database_errors(db):
        _validate_driver_references(db, values)
        driver_id = repo.create_driver(db, values)
        driver = repo.get_driver_by_id(db, driver_id)
        db.commit()
        return driver


def update_driver(db, driver_id, payload):
    with database_errors(db):
        get_driver_detail(db, driver_id)
        values = payload.model_dump(exclude_unset=True)
        _validate_driver_references(db, values)
        if values:
            repo.update_driver(db, driver_id, values)
        driver = repo.get_driver_by_id(db, driver_id)
        db.commit()
        return driver


def delete_driver(db, driver_id):
    with database_errors(db):
        get_driver_detail(db, driver_id)
        repo.delete_driver(db, driver_id)
        db.commit()
