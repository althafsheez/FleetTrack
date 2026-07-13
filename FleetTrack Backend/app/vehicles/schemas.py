from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date, datetime

class Vehicle(BaseModel):
    VehicleId: int
    ModelID: int
    EngineCapacityID: int
    Year:int 
    PlateCodeId:int
    PlateNo:str
    VHType:int
    RegistrationStartDate:datetime
    RegistrationExpiryDate:datetime
    InsurancePolicyId:int
    InsurancePolicyRecNo:int
    InsuranceExpDate:datetime
    InsuranceCompanyId:int
    InsuranceTypeId:int             
    TCNoId:int
    TypeId:int
    FuelCapacity:int
    FuelCapacityUnitId:int
    ChasisNo:str
    EngineNo:str
    TransmissionId:int
    FuelTypeId:int
    ColourId:int
    SalikTag:str
    InitialKmRdg:int
    LatestKmRdg:int
    TariffGroupId:int
    StatusId:int
    CreatedBy:int
    CreatedDate:datetime
    LastUpdatedBy:int
    LastUpdatedDate:datetime
    LocationToRemove:Optional[str]
    Remarks:Optional[str]
    NextDueService:Optional[int]
    AlertDate:Optional[datetime]
    BranchId:Optional[int]
    LocId:Optional[int]
    FuelLevel:Optional[int]