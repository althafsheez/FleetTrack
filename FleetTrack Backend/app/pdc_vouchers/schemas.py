from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PDCSourceType = Literal["payable", "receivable"]
PDCStatus = Literal["Cleared", "Bounced"]


class PDCAllocationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ledgerId: int = Field(..., gt=0)
    sourceVoucherTypeId: int = Field(..., gt=0)
    sourceVoucherNo: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=5)

    @field_validator("sourceVoucherNo")
    @classmethod
    def trim_source_number(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("sourceVoucherNo cannot be blank")
        return value


class PDCVoucherInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    voucherDate: datetime
    controlLedgerId: int = Field(..., gt=0)
    partyLedgerId: int = Field(..., gt=0)
    bankLedgerId: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=5)
    chequeNo: str = Field(..., min_length=1, max_length=200)
    chequeDate: datetime
    manualVoucherNo: str | None = Field(None, max_length=200)
    narration: str | None = Field(None, max_length=2000)
    idempotencyKey: str | None = Field(None, min_length=8, max_length=100)
    allocations: list[PDCAllocationInput] = Field(..., min_length=1, max_length=100)

    @field_validator("chequeNo", "manualVoucherNo", "narration", "idempotencyKey")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_allocations(self):
        keys = [
            (row.ledgerId, row.sourceVoucherTypeId, row.sourceVoucherNo)
            for row in self.allocations
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("An Against reference can appear only once")
        if self.allocations and len({row.ledgerId for row in self.allocations}) != 1:
            raise ValueError("All allocations must belong to the same party ledger")
        if self.chequeDate.date() < self.voucherDate.date():
            raise ValueError("chequeDate cannot be earlier than voucherDate")
        return self


class PDCAllocation(BaseModel):
    ledgerId: int
    ledgerName: str | None = None
    sourceVoucherTypeId: int
    sourceVoucherTypeName: str | None = None
    sourceVoucherNo: str
    sourceInvoiceNo: str | None = None
    amount: Decimal


class PDCVoucherResponse(BaseModel):
    id: int
    sourceType: PDCSourceType
    voucherNo: str
    invoiceNo: str
    voucherTypeId: int
    voucherTypeName: str
    voucherDate: datetime
    controlLedgerId: int
    controlLedgerName: str | None = None
    partyLedgerId: int | None = None
    partyLedgerName: str | None = None
    bankLedgerId: int
    bankLedgerName: str | None = None
    amount: Decimal
    chequeNo: str
    chequeDate: datetime
    narration: str | None = None
    status: str
    financialYearId: int
    idempotencyKey: str | None = None
    allocations: list[PDCAllocation]


class PDCRegisterRow(BaseModel):
    id: int
    sourceType: PDCSourceType
    invoiceNo: str
    voucherTypeId: int
    voucherTypeName: str
    voucherDate: datetime
    controlLedgerId: int
    controlLedgerName: str | None = None
    partyLedgerId: int | None = None
    partyLedgerName: str | None = None
    bankLedgerId: int
    bankLedgerName: str | None = None
    amount: Decimal
    chequeNo: str
    chequeDate: datetime
    narration: str | None = None
    status: str


class PaginatedPDCVouchers(BaseModel):
    items: list[PDCRegisterRow]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)


class PDCClearanceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    clearanceDate: datetime
    status: PDCStatus
    narration: str | None = Field(None, max_length=2000)
    idempotencyKey: str | None = Field(None, min_length=8, max_length=100)

    @field_validator("narration", "idempotencyKey")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class PDCClearanceResponse(BaseModel):
    id: int
    voucherNo: str
    invoiceNo: str
    voucherTypeId: int
    clearanceDate: datetime
    sourceType: PDCSourceType
    sourceId: int
    sourceInvoiceNo: str
    controlLedgerId: int
    controlLedgerName: str | None = None
    partyLedgerId: int | None = None
    partyLedgerName: str | None = None
    bankLedgerId: int
    bankLedgerName: str | None = None
    amount: Decimal
    chequeNo: str
    chequeDate: datetime
    status: PDCStatus
    narration: str | None = None
    financialYearId: int
    idempotencyKey: str | None = None


class PaginatedPDCClearances(BaseModel):
    items: list[PDCClearanceResponse]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)


class PDCLookup(BaseModel):
    id: int
    name: str
    accountGroupName: str | None = None


class PDCVoucherTypeLookup(BaseModel):
    id: int
    name: str
    numberingMethod: str


class PDCNumberingRule(BaseModel):
    voucherTypeId: int
    numberingMethod: str
    automatic: bool
    nextVoucherNo: str | None = None
    nextInvoiceNo: str | None = None


class PDCOpenReference(BaseModel):
    ledgerId: int
    sourceVoucherTypeId: int
    sourceVoucherTypeName: str | None = None
    sourceVoucherNo: str
    sourceInvoiceNo: str | None = None
    pendingAmount: Decimal
    currencySymbol: str | None = None
