from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TariffGroupCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    TariffGroupName: str = Field(min_length=1, max_length=100)

    @field_validator("TariffGroupName")
    @classmethod
    def nonblank_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Tariff group name cannot be blank")
        return value


class TariffGroupResponse(BaseModel):
    TariffGroupId: int
    TariffGroupName: str


class TariffRatesUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    DailyRate: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    WeeklyRate: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    MonthlyRate: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    DiscountPercentPerDayDaily: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    DiscountPercent3DaysDaily: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    DiscountPercent5DaysDaily: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    DiscountPercentWeekly: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    DiscountPercentMonthly: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    FuelCharges: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    AllowedKmsPerDay: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    ExtraKmCharges: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    DailyCDW: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    WeeklyCDW: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    MonthlyCDW: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    DailyPAI: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    WeeklyPAI: Decimal | None = Field(None, max_digits=18, decimal_places=2)
    MonthlyPAI: Decimal | None = Field(None, max_digits=18, decimal_places=2)


class TariffRatesResponse(TariffRatesUpdate):
    model_config = ConfigDict(extra="ignore")
    TariffGroupId: int


class TariffGroupUpdate(TariffRatesUpdate):
    TariffGroupName: str | None = Field(None, min_length=1, max_length=100)

    @field_validator("TariffGroupName")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            raise ValueError("TariffGroupName cannot be null")
        return TariffGroupCreate.nonblank_name(value)


class TariffGroupDetail(TariffRatesResponse):
    TariffGroupName: str
