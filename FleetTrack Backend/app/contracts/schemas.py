from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ContractCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ContractRefNo: int = Field(..., ge=0)
    ContractType: int = Field(..., gt=0)
    ContractStartDate: datetime
    ContractExpectedEndDate: datetime
    ContractLocId: int = Field(..., gt=0)
    CustomerId: int = Field(..., gt=0)
    UserName: str = Field(..., min_length=1, max_length=100)
    VehicleId: int = Field(..., gt=0)
    DateOfBirth: datetime
    Nationality: str = Field(..., min_length=3, max_length=3)
    VisaType: int = Field(..., gt=0)
    VisaExpiryDate: datetime
    DrivingLicenseType: int = Field(..., gt=0)
    DrivingLicenseNo: str = Field(..., min_length=1, max_length=100)
    DLPlaceOfIssue: str = Field(..., min_length=1, max_length=100)
    DLIssueDate: datetime
    DLExpiryDate: datetime
    PaymentMode: int = Field(1, gt=0)
    Rate: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    DriverCharges: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    AddDriverCharges: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    CDW: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    PAI: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    ExcessKmCharge: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    FuelCharges: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    SalikCharges: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    ExcessInsCharges: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    TrafficCharges: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    MileageCap: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    OtherCharges: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    DiscountType: int = Field(1, gt=0)
    Discount: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    Advance: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    Subtotal: Decimal = Field(Decimal("0.00"), max_digits=18, decimal_places=2)
    BillingType: int = Field(2, gt=0)
    DatetimeOut: datetime | None = None
    KmOut: int | None = Field(None, ge=0)
    FuelLevelIdOut: int | None = Field(1, gt=0)
    CheckedOutBy: int | None = Field(None, gt=0)
    LocationOut: int | None = Field(None, gt=0)
    SalesPersonId: int | None = Field(None, gt=0)
    Phone: str | None = Field(None, max_length=50)
    Mobile: str | None = Field(None, max_length=50)
    Fax: str | None = Field(None, max_length=50)
    Email: str | None = Field(None, max_length=50)
    Address: str | None = None
    ConfirmationRefValue: str | None = Field(None, max_length=50)
    Remarks: str | None = None
    CreatedBy: int | None = Field(None, gt=0)
    IsAdvanceInvoice: bool = True

    @field_validator("UserName", "DrivingLicenseNo", "DLPlaceOfIssue")
    @classmethod
    def strip_required_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("field cannot be blank")
        return value

    @field_validator("Nationality")
    @classmethod
    def normalize_nationality(cls, value):
        return value.strip().upper()

    @model_validator(mode="after")
    def validate_dates(self):
        if self.ContractExpectedEndDate < self.ContractStartDate:
            raise ValueError("ContractExpectedEndDate cannot be before ContractStartDate")
        return self


class ContractDriverResponse(BaseModel):
    ContractDriverId: int
    ContractId: int
    UserName: str
    Address: str
    Mobile: str
    Email: str
    DateOfBirth: datetime
    NationalityId: str
    PassportNo: str
    PassportExpiryDate: datetime
    VisaType: int
    VisaExpiryDate: datetime
    DrivingLicenseType: int
    DrivingLicenseNo: str
    DLPlaceOfIssue: str
    DLIssueDate: datetime
    DLExpiryDate: datetime
    DriverStatus: int
    Phone: str | None = None
    Fax: str | None = None


class ContractDriverCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ContractId: int = Field(..., gt=0)
    UserName: str = Field(..., min_length=1, max_length=100)
    Address: str = ""
    Mobile: str = Field("", max_length=50)
    Email: str = Field("", max_length=50)
    DateOfBirth: datetime
    NationalityId: str = Field(..., min_length=3, max_length=3)
    PassportNo: str = Field(..., min_length=1, max_length=50)
    PassportExpiryDate: datetime
    VisaType: int = Field(..., gt=0)
    VisaExpiryDate: datetime
    DrivingLicenseType: int = Field(..., gt=0)
    DrivingLicenseNo: str = Field(..., min_length=1, max_length=100)
    DLPlaceOfIssue: str = Field(..., min_length=1, max_length=100)
    DLIssueDate: datetime
    DLExpiryDate: datetime
    DriverStatus: int = Field(16, gt=0)
    Phone: str | None = Field(None, max_length=50)
    Fax: str | None = Field(None, max_length=50)

    @field_validator("UserName", "PassportNo", "DrivingLicenseNo", "DLPlaceOfIssue")
    @classmethod
    def strip_required_driver_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("field cannot be blank")
        return value

    @field_validator("NationalityId")
    @classmethod
    def normalize_driver_nationality(cls, value):
        return value.strip().upper()


class ContractDriverUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    UserName: str | None = Field(None, min_length=1, max_length=100)
    Address: str | None = None
    Mobile: str | None = Field(None, max_length=50)
    Email: str | None = Field(None, max_length=50)
    DateOfBirth: datetime | None = None
    NationalityId: str | None = Field(None, min_length=3, max_length=3)
    PassportNo: str | None = Field(None, min_length=1, max_length=50)
    PassportExpiryDate: datetime | None = None
    VisaType: int | None = Field(None, gt=0)
    VisaExpiryDate: datetime | None = None
    DrivingLicenseType: int | None = Field(None, gt=0)
    DrivingLicenseNo: str | None = Field(None, min_length=1, max_length=100)
    DLPlaceOfIssue: str | None = Field(None, min_length=1, max_length=100)
    DLIssueDate: datetime | None = None
    DLExpiryDate: datetime | None = None
    DriverStatus: int | None = Field(None, gt=0)
    Phone: str | None = Field(None, max_length=50)
    Fax: str | None = Field(None, max_length=50)

    @field_validator("UserName", "PassportNo", "DrivingLicenseNo", "DLPlaceOfIssue")
    @classmethod
    def strip_optional_driver_text(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("field cannot be blank")
        return value

    @field_validator("NationalityId")
    @classmethod
    def normalize_optional_driver_nationality(cls, value):
        return value.strip().upper() if value is not None else value


class ContractVehicleResponse(BaseModel):
    Id: int
    ContractId: int
    VehicleId: int
    ContractVehicleStatus: int
    DatetimeOut: datetime | None = None
    DatetimeIn: datetime | None = None
    KmOut: int | None = None
    KmIn: int | None = None
    FuelLevelIdOut: int | None = None
    FuelLevelIdIn: int | None = None
    DTIN: datetime | None = None
    CheckedOutBy: int | None = None
    CheckedInBy: int | None = None
    LocationOut: int | None = None
    LocationIn: int | None = None


class ContractViewRow(BaseModel):
    slNo: int
    contractId: int
    agreementNo: str
    customer: str
    dateOut: datetime | None = None
    dateIn: datetime | None = None
    totalDays: int
    rate: Decimal
    vehicleId: int | None = None
    vehicle: str | None = None
    rent: Decimal
    salik: Decimal
    fine: Decimal
    received: Decimal
    pendingAmount: Decimal


class ContractResponse(BaseModel):
    ContractId: int
    RTACode: str
    ContractType: int
    ContractRefNo: str
    ContractStartDate: datetime
    ContractExpectedEndDate: datetime
    ContractActualEndDate: datetime
    ContractLocId: int
    CustomerName: str
    UserName: str
    Address: str
    Phone: str
    Mobile: str
    Fax: str
    Email: str
    DateOfBirth: datetime
    Nationality: str
    PassportNo: str
    PassportExpiryDate: datetime
    VisaType: int
    VisaExpiryDate: datetime
    DrivingLicenseType: int
    DrivingLicenseNo: str
    DLPlaceOfIssue: str
    DLIssueDate: datetime
    DLExpiryDate: datetime
    PaymentType: int
    Rate: Decimal
    DriverCharges: Decimal
    AddDriverCharges: Decimal
    CDW: Decimal
    PAI: Decimal
    ExcessKmCharge: Decimal
    FuelCharges: Decimal
    SalikCharges: Decimal
    ExcessInsCharges: Decimal
    TrafficCharges: Decimal
    MileageCap: Decimal
    OtherCharges: Decimal
    DiscountType: int
    Discount: Decimal
    Advance: Decimal
    Subtotal: Decimal
    PaymentMode: int
    CreditCardExpiryMonth: int
    CreditCardExpiryYear: int
    Status: int
    CustomerId: int | None = None
    SalesPersonId: int | None = None
    CreditCardType: int | None = None
    CreditCardNo: str | None = None
    Remarks: str | None = None
    RentalInvoiced: bool | None = None
    SalikInvoiced: bool | None = None
    FineInvoiced: bool | None = None
    RepairCharged: bool | None = None
    PenaltyCharged: bool | None = None
    ExcessKmCharged: bool | None = None
    OtherChargesCharged: bool | None = None
    VehicleId: int | None = None
    NextInvStDate: datetime | None = None
    CreatedBy: int | None = None
    CreatedDate: datetime | None = None
    UpdatedBy: int | None = None
    UpdatedDate: datetime | None = None
    CustomerSource: int | None = None
    CustomerType: int | None = None
    ConfirmationRefType: int | None = None
    ConfirmationRefValue: str | None = None
    ContactPerson: str | None = None
    ContactPersonAddress: str | None = None
    ContactPersonPhone: str | None = None
    ContactPersonMobile: str | None = None
    ContactPersonFax: str | None = None
    ContactPersonEmail: str | None = None
    LastInvoiceDate: datetime | None = None
    ContractUnder: int | None = None
    IsAdvanceInvoice: bool | None = None
    BillingType: int | None = None
    CustomerIdNo: str | None = None
    CustomerIdExpiry: datetime | None = None
    driver: ContractDriverResponse
    vehicle_assignment: ContractVehicleResponse
