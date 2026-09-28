from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RentalInvoiceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    salesAccountId: int = Field(..., gt=0)
    exchangeRateId: int = Field(..., gt=0)
    creditPeriod: int = Field(0, ge=0, le=3650)
    lpoNo: str | None = Field(None, max_length=200)

    @field_validator("lpoNo")
    @classmethod
    def trim_lpo_no(cls, value):
        return value.strip() if value is not None else value


class RentalInvoiceRequest(RentalInvoiceSettings):
    asOfDate: datetime | None = None


class RentalInvoiceLinePreview(BaseModel):
    itemTypeId: int
    itemTypeName: str
    vehicleId: int
    description: str
    quantity: Decimal
    unitId: int
    rate: Decimal
    taxId: int
    taxAmount: Decimal
    amount: Decimal


class RentalInvoicePreview(BaseModel):
    contractId: int
    contractRefNo: str
    invoiceDate: datetime
    periodStart: datetime
    periodEnd: datetime
    nextInvoiceDate: datetime
    taxAmount: Decimal
    totalAmount: Decimal
    grandTotal: Decimal
    narration: str
    lines: list[RentalInvoiceLinePreview]


class RentalInvoiceDueRow(BaseModel):
    contractId: int
    contractRefNo: str
    customerId: int | None = None
    customerName: str | None = None
    contractType: int
    paymentType: int
    billingType: int | None = None
    nextInvoiceDate: datetime
