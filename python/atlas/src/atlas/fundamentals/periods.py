from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from atlas.fundamentals.enums import FinancialPeriodNature, FiscalPeriod, ReportingPeriodType


class FinancialPeriod(BaseModel):
    """
    Represents the period for a financial statement or fact.
    """

    nature: FinancialPeriodNature = Field(...)
    period_start: Optional[date] = Field(default=None)
    period_end: date = Field(...)
    fiscal_year: Optional[int] = Field(default=None, ge=1900, le=2200)
    fiscal_period: Optional[FiscalPeriod] = Field(default=None)
    reporting_period_type: Optional[ReportingPeriodType] = Field(default=None)

    @model_validator(mode="after")
    def validate_period_nature(self) -> "FinancialPeriod":
        if self.nature == FinancialPeriodNature.INSTANT:
            if self.period_start is not None:
                raise ValueError("period_start must be None when nature is instant.")
        elif self.nature == FinancialPeriodNature.DURATION:
            if self.period_start is None:
                raise ValueError("period_start is required when nature is duration.")
            if self.period_start >= self.period_end:
                raise ValueError("period_start must be strictly before period_end.")
        return self

    @model_validator(mode="after")
    def validate_fiscal_period_consistency(self) -> "FinancialPeriod":
        if self.fiscal_period and self.reporting_period_type:
            # Check for obvious contradictions
            if self.reporting_period_type == ReportingPeriodType.QUARTERLY:
                if self.fiscal_period not in (FiscalPeriod.Q1, FiscalPeriod.Q2, FiscalPeriod.Q3, FiscalPeriod.Q4):
                    raise ValueError(f"Incompatible fiscal_period {self.fiscal_period.value} for quarterly reporting.")
            elif self.reporting_period_type == ReportingPeriodType.ANNUAL:
                if self.fiscal_period != FiscalPeriod.FY:
                    raise ValueError(f"Incompatible fiscal_period {self.fiscal_period.value} for annual reporting.")
            elif self.reporting_period_type == ReportingPeriodType.SEMIANNUAL:
                if self.fiscal_period not in (FiscalPeriod.H1, FiscalPeriod.H2):
                    raise ValueError(f"Incompatible fiscal_period {self.fiscal_period.value} for semiannual reporting.")
            elif self.reporting_period_type == ReportingPeriodType.NINE_MONTH:
                if self.fiscal_period != FiscalPeriod.NINE_MONTHS:
                    raise ValueError(f"Incompatible fiscal_period {self.fiscal_period.value} for nine-month reporting.")
        return self

    model_config = {"frozen": True}
