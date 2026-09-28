from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


ReceiptReferenceType = Literal["against", "on_account"]


class ReceiptAllocationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    partyBalanceId: int | None = Field(None, gt=0)
    referenceType: ReceiptReferenceType
    sourceVoucherTypeId: int | None = Field(None, gt=0)
    sourceVoucherNo: str | None = Field(None, max_length=200)
    contractId: int | None = Field(None, gt=0)
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=5)

    @field_validator("sourceVoucherNo")
    @classmethod
    def trim_source_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def reference_fields_match_type(self):
        has_source = self.sourceVoucherTypeId is not None or self.sourceVoucherNo is not None
        if self.referenceType == "against":
            if self.sourceVoucherTypeId is None or self.sourceVoucherNo is None:
                raise ValueError("Against allocations require sourceVoucherTypeId and sourceVoucherNo")
            if self.contractId is not None:
                raise ValueError("Against allocation contractId is derived from the source voucher")
        elif has_source:
            raise ValueError("On Account allocations cannot specify a source voucher")
        return self


class ReceiptVoucherLineInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receiptDetailsId: int | None = Field(None, gt=0)
    ledgerId: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=5)
    exchangeRateId: int = Field(..., gt=0)
    chequeNo: str | None = Field(None, max_length=200)
    chequeDate: datetime | None = None
    allocations: list[ReceiptAllocationInput] = Field(default_factory=list, max_length=100)

    @field_validator("chequeNo")
    @classmethod
    def trim_cheque_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def cheque_fields_are_complete(self):
        if (self.chequeNo is None) != (self.chequeDate is None):
            raise ValueError("chequeNo and chequeDate must be supplied together")
        allocation_ids = [row.partyBalanceId for row in self.allocations if row.partyBalanceId is not None]
        if len(allocation_ids) != len(set(allocation_ids)):
            raise ValueError("partyBalanceId values must be unique within a line")
        references = [
            (row.sourceVoucherTypeId, row.sourceVoucherNo)
            for row in self.allocations
            if row.referenceType == "against"
        ]
        if len(references) != len(set(references)):
            raise ValueError("An Against source reference can appear only once within a line")
        return self


class ReceiptVoucherInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    voucherTypeId: int = Field(..., gt=0)
    voucherDate: datetime
    receivingLedgerId: int = Field(..., gt=0)
    manualVoucherNo: str | None = Field(None, max_length=200)
    narration: str | None = Field(None, max_length=2000)
    idempotencyKey: str | None = Field(None, min_length=8, max_length=100)
    lines: list[ReceiptVoucherLineInput] = Field(..., min_length=1, max_length=100)

    @field_validator("manualVoucherNo", "narration", "idempotencyKey")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def line_identifiers_are_unique(self):
        detail_ids = [row.receiptDetailsId for row in self.lines if row.receiptDetailsId is not None]
        if len(detail_ids) != len(set(detail_ids)):
            raise ValueError("receiptDetailsId values must be unique")
        ledger_ids = [row.ledgerId for row in self.lines]
        if len(ledger_ids) != len(set(ledger_ids)):
            raise ValueError("A detail ledger can appear only once in a Receipt Voucher")
        allocation_ids = [
            allocation.partyBalanceId
            for row in self.lines
            for allocation in row.allocations
            if allocation.partyBalanceId is not None
        ]
        if len(allocation_ids) != len(set(allocation_ids)):
            raise ValueError("partyBalanceId values must be unique across the voucher")
        return self


class ReceiptAllocation(BaseModel):
    partyBalanceId: int
    referenceType: ReceiptReferenceType
    sourceVoucherTypeId: int | None = None
    sourceVoucherTypeName: str | None = None
    sourceVoucherNo: str | None = None
    sourceInvoiceNo: str | None = None
    amount: Decimal
    exchangeRateId: int
    exchangeRate: Decimal
    currencyId: int | None = None
    contractId: int | None = None


class ReceiptVoucherLine(BaseModel):
    receiptDetailsId: int
    ledgerId: int
    ledgerName: str | None = None
    amount: Decimal
    exchangeRateId: int
    exchangeRate: Decimal
    currencyId: int | None = None
    currencyName: str | None = None
    currencySymbol: str | None = None
    baseAmount: Decimal
    chequeNo: str | None = None
    chequeDate: datetime | None = None
    billByBill: bool
    allocations: list[ReceiptAllocation]


class ReceiptVoucherResponse(BaseModel):
    receiptMasterId: int
    voucherNo: str
    invoiceNo: str
    voucherTypeId: int
    voucherTypeName: str | None = None
    suffixPrefixId: int
    voucherDate: datetime
    receivingLedgerId: int
    receivingLedgerName: str | None = None
    totalAmount: Decimal
    narration: str | None = None
    idempotencyKey: str | None = None
    userId: int
    financialYearId: int
    isPosted: bool
    lines: list[ReceiptVoucherLine]


class ReceiptVoucherRegisterRow(BaseModel):
    receiptMasterId: int
    voucherNo: str
    invoiceNo: str
    voucherTypeId: int
    voucherTypeName: str | None = None
    voucherDate: datetime
    receivingLedgerId: int
    receivingLedgerName: str | None = None
    totalAmount: Decimal
    narration: str | None = None
    isPosted: bool
    detailAccountNames: list[str] = Field(default_factory=list)
    lineCount: int = Field(ge=0)


class PaginatedReceiptVouchers(BaseModel):
    items: list[ReceiptVoucherRegisterRow]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)


class ReceiptVoucherTypeLookup(BaseModel):
    id: int
    name: str
    numberingMethod: str | None = None


class ReceiptAccountLookup(BaseModel):
    id: int
    name: str
    accountGroupId: int | None = None
    accountGroupName: str | None = None


class ReceiptDetailAccountLookup(ReceiptAccountLookup):
    billByBill: bool


class ReceiptExchangeRateLookup(BaseModel):
    id: int
    currencyId: int
    currencyName: str | None = None
    currencySymbol: str | None = None
    rate: Decimal
    date: datetime | None = None


class ReceiptNumberingRule(BaseModel):
    voucherTypeId: int
    numberingMethod: str
    automatic: bool
    suffixPrefixId: int
    prefix: str | None = None
    suffix: str | None = None
    startIndex: int | None = None
    widthOfNumericalPart: int | None = None
    prefillWithZero: bool | None = None
    nextVoucherNo: str | None = None
    nextInvoiceNo: str | None = None
    fromDate: datetime | None = None
    toDate: datetime | None = None


class ReceiptContractLookup(BaseModel):
    id: int
    contractRefNo: str


class OpenReceiptReference(BaseModel):
    ledgerId: int
    sourceVoucherTypeId: int
    sourceVoucherTypeName: str | None = None
    sourceVoucherNo: str
    sourceInvoiceNo: str | None = None
    pendingAmount: Decimal
    exchangeRateId: int
    exchangeRate: Decimal
    currencyId: int | None = None
    currencyName: str | None = None
    currencySymbol: str | None = None
    contractId: int | None = None
