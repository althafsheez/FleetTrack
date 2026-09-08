from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class VehicleInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("VHType", mode="before", check_fields=False)
    @classmethod
    def fleet_number_as_text(cls, value):
        return str(value) if isinstance(value, int) and not isinstance(value, bool) else value


class VehicleCreate(VehicleInput):
    ModelId: int = Field(..., gt=0)
    EngineCapacityId: int = Field(..., gt=0)
    Year: int = Field(..., ge=1, le=9999)
    PlateCodeId: int = Field(..., gt=0)
    PlateNo: str = Field(..., max_length=50, min_length=1)
    RegistrationStartDate: datetime = Field(...)
    RegistrationExpiryDate: datetime = Field(...)
    InsurancePolicyId: int = Field(..., gt=0)
    InsurancePolicyRecNo: int = Field(0, ge=0)
    InsuranceExpDate: datetime = Field(...)
    InsuranceCompanyId: int = Field(..., gt=0)
    InsuranceTypeId: int = Field(..., gt=0)
    TCNoId: int = Field(..., gt=0)
    TypeId: int = Field(..., gt=0)
    FuelCapacity: int = Field(..., ge=0)
    FuelCapacityUnitId: int = Field(..., gt=0)
    ChasisNo: str = Field(..., max_length=50, min_length=1)
    EngineNo: str = Field(..., max_length=50, min_length=1)
    TransmissionId: int = Field(..., gt=0)
    FuelTypeId: int = Field(..., gt=0)
    ColourId: int = Field(..., gt=0)
    SalikTag: str = Field(..., max_length=100, min_length=1)
    InitialKmRdg: int = Field(..., ge=0)
    LatestKmRdg: int | None = Field(None, ge=0)
    TariffGroupId: int = Field(..., gt=0)
    StatusId: int = Field(..., gt=0)
    CreatedBy: int = Field(..., gt=0)
    LocationToRemove: str | None = Field(None)
    Remarks: str | None = Field(None)
    NextDueService: int | None = Field(None)
    AlertDate: datetime | None = Field(None)
    BranchId: int | None = Field(None, gt=0)
    LocId: int | None = Field(None, gt=0)
    FuelLevel: int | None = Field(None)
    VHType: str | None = Field(None, max_length=50)


class VehicleUpdate(VehicleInput):
    ModelId: int | None = Field(None, gt=0)
    EngineCapacityId: int | None = Field(None, gt=0)
    Year: int | None = Field(None, ge=1, le=9999)
    PlateCodeId: int | None = Field(None, gt=0)
    PlateNo: str | None = Field(None, max_length=50, min_length=1)
    RegistrationStartDate: datetime | None = Field(None)
    RegistrationExpiryDate: datetime | None = Field(None)
    InsurancePolicyId: int | None = Field(None, gt=0)
    InsurancePolicyRecNo: int | None = Field(None, ge=0)
    InsuranceExpDate: datetime | None = Field(None)
    InsuranceCompanyId: int | None = Field(None, gt=0)
    InsuranceTypeId: int | None = Field(None, gt=0)
    TCNoId: int | None = Field(None, gt=0)
    TypeId: int | None = Field(None, gt=0)
    FuelCapacity: int | None = Field(None, ge=0)
    FuelCapacityUnitId: int | None = Field(None, gt=0)
    ChasisNo: str | None = Field(None, max_length=50, min_length=1)
    EngineNo: str | None = Field(None, max_length=50, min_length=1)
    TransmissionId: int | None = Field(None, gt=0)
    FuelTypeId: int | None = Field(None, gt=0)
    ColourId: int | None = Field(None, gt=0)
    SalikTag: str | None = Field(None, max_length=100, min_length=1)
    InitialKmRdg: int | None = Field(None, ge=0)
    LatestKmRdg: int | None = Field(None, ge=0)
    TariffGroupId: int | None = Field(None, gt=0)
    StatusId: int | None = Field(None, gt=0)
    LastUpdatedBy: int = Field(..., gt=0)
    LocationToRemove: str | None = Field(None)
    Remarks: str | None = Field(None)
    NextDueService: int | None = Field(None)
    AlertDate: datetime | None = Field(None)
    BranchId: int | None = Field(None, gt=0)
    LocId: int | None = Field(None, gt=0)
    FuelLevel: int | None = Field(None)
    VHType: str | None = Field(None, max_length=50)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for name in ['ModelId', 'EngineCapacityId', 'Year', 'PlateCodeId', 'PlateNo', 'RegistrationStartDate', 'RegistrationExpiryDate', 'InsurancePolicyId', 'InsurancePolicyRecNo', 'InsuranceExpDate', 'InsuranceCompanyId', 'InsuranceTypeId', 'TCNoId', 'TypeId', 'FuelCapacity', 'FuelCapacityUnitId', 'ChasisNo', 'EngineNo', 'TransmissionId', 'FuelTypeId', 'ColourId', 'SalikTag', 'InitialKmRdg', 'LatestKmRdg', 'TariffGroupId', 'StatusId', 'LastUpdatedBy']:
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    VehicleId: int
    ModelId: int
    EngineCapacityId: int
    Year: int
    PlateCodeId: int
    PlateNo: str
    RegistrationStartDate: datetime
    RegistrationExpiryDate: datetime
    InsurancePolicyId: int
    InsurancePolicyRecNo: int
    InsuranceExpDate: datetime
    InsuranceCompanyId: int
    InsuranceTypeId: int
    TCNoId: int
    TypeId: int
    FuelCapacity: int
    FuelCapacityUnitId: int
    ChasisNo: str
    EngineNo: str
    TransmissionId: int
    FuelTypeId: int
    ColourId: int
    SalikTag: str
    InitialKmRdg: int
    LatestKmRdg: int
    TariffGroupId: int
    StatusId: int
    CreatedBy: int
    CreatedDate: datetime
    LastUpdatedBy: int
    LastUpdatedDate: datetime
    LocationToRemove: str | None = None
    Remarks: str | None = None
    NextDueService: int | None = None
    AlertDate: datetime | None = None
    BranchId: int | None = None
    LocId: int | None = None
    FuelLevel: int | None = None
    VHType: str | None = None


class PaginatedVehicleResponse(BaseModel):
    items: list[VehicleResponse]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)
