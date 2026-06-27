from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from pydantic import EmailStr


class SupplierCreate(BaseModel):

    ledgerName: str = Field(
    min_length=1,
    max_length=200
)
    ledgerNameInArabic: Optional[str] = None
    openingBalance: Optional[Decimal] = None
    crOrDr: Optional[str] = None

    emirateId: int=Field(ge=1, le=7)

    mailingName: Optional[str] = None

    bankAccountNumber: Optional[str] = None

    branchName: Optional[str] = None
    branchCode: Optional[str] = None

    phone: Optional[str] = None
    mobile: str = Field(min_length=10)
    email: Optional[EmailStr] = None

    address: Optional[str] = None

    billByBill: Optional[bool] = None

    tin: Optional[str] = None

    narration: Optional[str] = None

    routeId: Optional[int] = None

    areaId: Optional[int] = None


class SupplierUpdate(BaseModel):
    ledgerName: str = Field(
    min_length=1,
    max_length=200
)

    ledgerNameInArabic: Optional[str] = None

    openingBalance: Optional[Decimal] = None
    crOrDr: Optional[str] = None

    emirateId: int=Field(ge=1, le=7)

    mailingName: Optional[str] = None

    bankAccountNumber: Optional[str] = None

    branchName: Optional[str] = None
    branchCode: Optional[str] = None

    phone: Optional[str] = None
    mobile: str = Field(min_length=10)
    email: Optional[EmailStr] = None

    address: Optional[str] = None


    billByBill: Optional[bool] = None

    tin: Optional[str] = None

    narration: Optional[str] = None

    routeId: Optional[int] = None

    areaId: Optional[int] = None




class SupplierResponse(BaseModel):
    ledgerId: Optional[int] = None
    ledgerName: Optional[str] = None

    ledgerNameInArabic: Optional[str] = None

    openingBalance: Optional[Decimal] = None
    crOrDr: Optional[str] = None

    emirateId: Optional[int] = None

    mailingName: Optional[str] = None

    bankAccountNumber: Optional[str] = None

    branchName: Optional[str] = None
    branchCode: Optional[str] = None

    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None

    address: Optional[str] = None

    billByBill: Optional[bool] = None

    tin: Optional[str] = None

    narration: Optional[str] = None

    routeId: Optional[int] = None

    areaId: Optional[int] = None

