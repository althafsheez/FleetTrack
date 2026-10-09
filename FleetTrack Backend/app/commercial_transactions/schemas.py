from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Kind = Literal['purchase-orders', 'purchase-invoices', 'sales-quotations', 'credit-notes', 'debit-notes', 'vehicle-finance']
Amount = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=5)]


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class Allocation(Input):
    voucherTypeId: int = Field(gt=0)
    voucherNo: str = Field(min_length=1, max_length=200)
    amount: Amount = Field(gt=0)


class Line(Input):
    id: int | None = Field(None, gt=0)
    description: str = Field(default='', max_length=4000)
    vehicleId: int | None = Field(None, gt=0)
    unitId: int | None = Field(None, gt=0)
    qty: Amount = Decimal(1)
    rate: Amount = Decimal(0)
    taxId: int | None = Field(None, gt=0)
    productId: int | None = Field(None, gt=0)
    itemTypeId: int | None = Field(None, gt=0)
    sourceLineId: int | None = Field(None, gt=0)
    ledgerId: int | None = Field(None, gt=0)
    direction: Literal['Dr', 'Cr'] = 'Dr'
    amount: Amount = Decimal(0)
    exchangeRateId: int | None = Field(None, gt=0)
    chequeNo: str = Field(default='', max_length=50)
    chequeDate: datetime | None = None
    allocations: list[Allocation] = Field(default_factory=list, max_length=100)


class DocumentInput(Input):
    date: datetime
    manualNumber: str = Field(default='', max_length=200)
    ledgerId: int | None = Field(None, gt=0)
    exchangeRateId: int | None = Field(None, gt=0)
    accountId: int | None = Field(None, gt=0)
    employeeId: int | None = Field(None, ge=0)
    pricingLevelId: int | None = Field(None, ge=0)
    dueDate: datetime | None = None
    vendorInvoiceNo: str = Field(default='', max_length=200)
    invoiceDate: datetime | None = None
    creditPeriod: int = Field(default=0, ge=0, le=3650)
    sourceId: int | None = Field(None, gt=0)
    purchaseMode: Literal['misc', 'asset', 'inventory'] = 'misc'
    narration: str = Field(default='', max_length=10000)
    discount: Amount = Decimal(0)
    transportationCompany: str = Field(default='', max_length=200)
    lrNo: str = Field(default='', max_length=200)
    approved: bool = False
    cancelled: bool = False
    loanAmount: Amount = Decimal(0)
    monthlyAmount: Amount = Decimal(0)
    installments: int = Field(default=1, ge=1, le=360)
    bankId: int | None = Field(None, gt=0)
    assetId: int | None = Field(None, gt=0)
    purchaseDetailId: int | None = Field(None, gt=0)
    chequeNoFrom: str = Field(default='', max_length=50)
    chequeDateFrom: datetime | None = None
    lines: list[Line] = Field(default_factory=list, max_length=200)
    idempotencyKey: str = Field(min_length=16, max_length=100)
    expectedVersion: str | None = None

    @model_validator(mode='after')
    def unique_lines(self):
        ids = [line.id for line in self.lines if line.id is not None]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate line identity')
        return self
