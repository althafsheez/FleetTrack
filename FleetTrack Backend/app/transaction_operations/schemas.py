from datetime import datetime
from decimal import Decimal
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

Money = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=2)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ReconciliationLine(Input):
    ledgerPostingId: int = Field(gt=0)
    statementDate: datetime | None = None
    expectedStatementDate: datetime | None = None


class ReconciliationInput(Input):
    bankLedgerId: int = Field(gt=0)
    lines: list[ReconciliationLine] = Field(min_length=1, max_length=500)


class FineInput(Input):
    ticketNo: str = Field(min_length=1, max_length=100)
    vehicleId: int = Field(gt=0)
    trafficFile: str = Field(min_length=1, max_length=100)
    fineDate: datetime
    authority: str = Field(min_length=1, max_length=100)
    amount: Money = Field(gt=0)
    blackPoints: int = Field(default=0, ge=0, le=1000)
    description: str = Field(min_length=1, max_length=10000)
    acknowledgment: Money = Decimal(0)
