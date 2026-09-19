from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


InvoiceType = Literal["rental", "salik", "fine", "misc", "vehicle"]


class InvoiceLineInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itemTypeId: int = Field(..., gt=0)
    vehicleId: int | None = Field(None, gt=0)
    description: str = Field(..., min_length=1, max_length=900)
    quantity: Decimal = Field(..., gt=0, max_digits=18, decimal_places=5)
    unitId: int = Field(..., gt=0)
    rate: Decimal = Field(..., ge=0, max_digits=18, decimal_places=5)
    discount: Decimal = Field(Decimal("0"), ge=0, max_digits=18, decimal_places=5)
    taxId: int = Field(..., gt=0)

    @field_validator("description")
    @classmethod
    def trim_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("description cannot be blank")
        return value


class SalesInvoiceDraftInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invoiceType: InvoiceType
    invoiceDate: datetime
    customerId: int = Field(..., gt=0)
    contractId: int | None = Field(None, gt=0)
    creditPeriod: int = Field(..., ge=0, le=3650)
    lpoNo: str | None = Field(None, max_length=200)
    salesAccountId: int = Field(..., gt=0)
    salesPersonId: int | None = Field(None, gt=0)
    exchangeRateId: int = Field(..., gt=0)
    locationId: int = Field(..., gt=0)
    billDiscount: Decimal = Field(Decimal("0"), ge=0, max_digits=18, decimal_places=5)
    narration: str | None = Field(None, max_length=2000)
    lines: list[InvoiceLineInput] = Field(..., min_length=1, max_length=100)

    @field_validator("lpoNo", "narration")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None


class SalesInvoiceLine(BaseModel):
    salesDetailsId: int
    slNo: int
    itemTypeId: int | None = None
    itemTypeName: str | None = None
    vehicleId: int | None = None
    description: str | None = None
    quantity: Decimal
    unitId: int | None = None
    unitName: str | None = None
    rate: Decimal
    discount: Decimal
    taxId: int | None = None
    taxName: str | None = None
    taxRate: Decimal | None = None
    taxAmount: Decimal
    grossAmount: Decimal
    netAmount: Decimal
    amount: Decimal


class SalesInvoiceTax(BaseModel):
    taxId: int
    taxName: str | None = None
    taxAmount: Decimal


class SalesInvoiceResponse(BaseModel):
    salesMasterId: int
    invoiceType: InvoiceType
    voucherTypeId: int
    voucherNo: str | None = None
    invoiceNo: str | None = None
    invoiceDate: datetime | None = None
    customerId: int | None = None
    customerName: str | None = None
    contractId: int | None = None
    contractRefNo: str | None = None
    creditPeriod: int
    lpoNo: str | None = None
    salesAccountId: int | None = None
    salesAccountName: str | None = None
    salesPersonId: int | None = None
    exchangeRateId: int | None = None
    locationName: str | None = None
    taxAmount: Decimal
    billDiscount: Decimal
    totalAmount: Decimal
    grandTotal: Decimal
    narration: str | None = None
    isPosted: bool | None = None
    vehicleNos: str | None = None
    lines: list[SalesInvoiceLine] = []
    taxes: list[SalesInvoiceTax] = []


class SalesInvoiceRegisterRow(BaseModel):
    salesMasterId: int
    invoiceType: InvoiceType
    voucherTypeId: int
    voucherNo: str | None = None
    invoiceNo: str | None = None
    invoiceDate: datetime | None = None
    customerName: str | None = None
    contractRefNo: str | None = None
    vehicleNos: str | None = None
    grandTotal: Decimal
    isPosted: bool | None = None


class PaginatedSalesInvoices(BaseModel):
    items: list[SalesInvoiceRegisterRow]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)


class InvoiceLookup(BaseModel):
    id: int
    name: str
    taxId: int | None = None
    taxRate: Decimal | None = None

