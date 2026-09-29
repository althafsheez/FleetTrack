from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


ContraDirection = Literal["deposit", "withdrawal"]


class ContraVoucherLineInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contraDetailsId: int | None = Field(None, gt=0)
    ledgerId: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=5)
    exchangeRateId: int = Field(..., gt=0)
    chequeNo: str | None = Field(None, max_length=200)
    chequeDate: datetime | None = None

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
        return self


class ContraVoucherInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    voucherDate: datetime
    direction: ContraDirection
    headerLedgerId: int = Field(..., gt=0)
    manualVoucherNo: str | None = Field(None, max_length=200)
    narration: str | None = Field(None, max_length=2000)
    idempotencyKey: str | None = Field(None, min_length=8, max_length=100)
    confirmNegativeBalance: bool = False
    lines: list[ContraVoucherLineInput] = Field(..., min_length=1, max_length=100)

    @field_validator("manualVoucherNo", "narration", "idempotencyKey")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def line_identifiers_are_unique(self):
        ids = [line.contraDetailsId for line in self.lines if line.contraDetailsId is not None]
        if len(ids) != len(set(ids)):
            raise ValueError("contraDetailsId values must be unique")
        return self


class ContraVoucherLine(BaseModel):
    contraDetailsId: int
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


class ContraVoucherResponse(BaseModel):
    contraMasterId: int
    voucherNo: str
    invoiceNo: str
    voucherTypeId: int
    suffixPrefixId: int
    voucherDate: datetime
    direction: ContraDirection
    headerLedgerId: int
    headerLedgerName: str | None = None
    totalAmount: Decimal
    narration: str | None = None
    idempotencyKey: str | None = None
    userId: int
    financialYearId: int
    lines: list[ContraVoucherLine]


class ContraVoucherRegisterRow(BaseModel):
    contraMasterId: int
    voucherNo: str
    invoiceNo: str
    voucherDate: datetime
    direction: ContraDirection
    headerLedgerId: int
    headerLedgerName: str | None = None
    offsetAccountNames: list[str] = Field(default_factory=list)
    lineCount: int = Field(ge=0)
    totalAmount: Decimal
    narration: str | None = None


class PaginatedContraVouchers(BaseModel):
    items: list[ContraVoucherRegisterRow]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)


class ContraAccountLookup(BaseModel):
    id: int
    name: str
    accountGroupId: int | None = None
    accountGroupName: str | None = None
    isBank: bool


class ContraExchangeRateLookup(BaseModel):
    id: int
    currencyId: int
    currencyName: str | None = None
    currencySymbol: str | None = None
    rate: Decimal
    date: datetime | None = None


class ContraVoucherTypeLookup(BaseModel):
    id: int
    name: str
    numberingMethod: str | None = None


class ContraNumberingRule(BaseModel):
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
