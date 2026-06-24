from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import EmailStr


class CustomerCreate(BaseModel):

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

    creditPeriod: Optional[int] = None
    creditLimit: Optional[Decimal] = None

    billByBill: Optional[bool] = None

    tin: Optional[str] = None

    narration: Optional[str] = None

    Nationality: Optional[str] = Field(default=None, max_length=3)


    CustomerIdNo: Optional[str] = None
    CustomerIdExpiry: Optional[datetime] = None

    routeId: Optional[int] = None

    areaId: Optional[int] = None

    isCorporate: Optional[bool] = None

class CustomerUpdate(BaseModel):
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

    creditPeriod: Optional[int] = None
    creditLimit: Optional[Decimal] = None

    billByBill: Optional[bool] = None

    tin: Optional[str] = None

    narration: Optional[str] = None

    Nationality: Optional[str] = Field(default=None, max_length=3)

    CustomerIdNo: Optional[str] = None
    CustomerIdExpiry: Optional[datetime] = None

    routeId: Optional[int] = None

    areaId: Optional[int] = None

    isCorporate: Optional[bool] = None


class CustomerResponse(BaseModel):
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

    creditPeriod: Optional[int] = None
    creditLimit: Optional[Decimal] = None

    billByBill: Optional[bool] = None

    tin: Optional[str] = None

    narration: Optional[str] = None

    Nationality: Optional[str] 

    CustomerIdNo: Optional[str] = None
    CustomerIdExpiry: Optional[datetime] = None

    routeId: Optional[int] = None

    areaId: Optional[int] = None

    isCorporate: Optional[bool] = None
