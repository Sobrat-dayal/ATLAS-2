import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from atlas.fundamentals.concepts import FundamentalConceptKey
from atlas.fundamentals.enums import ReportingPeriodType


class FundamentalPeriodFilter(BaseModel):
    reporting_period_types: frozenset[ReportingPeriodType] = Field(default_factory=frozenset)
    fiscal_year_start: Optional[int] = Field(default=None, ge=1900, le=2200)
    fiscal_year_end: Optional[int] = Field(default=None, ge=1900, le=2200)
    period_end_start: Optional[date] = Field(default=None)
    period_end_end: Optional[date] = Field(default=None)
    limit: int = Field(default=100, gt=0, le=100)

    @model_validator(mode="after")
    def validate_ranges(self) -> "FundamentalPeriodFilter":
        if self.fiscal_year_start and self.fiscal_year_end:
            if self.fiscal_year_start > self.fiscal_year_end:
                raise ValueError("fiscal_year_start must be <= fiscal_year_end")
        if self.period_end_start and self.period_end_end:
            if self.period_end_start > self.period_end_end:
                raise ValueError("period_end_start must be <= period_end_end")
        return self

    model_config = {"frozen": True}


class IncomeStatementRequest(BaseModel):
    company_id: uuid.UUID = Field(...)
    period_filter: FundamentalPeriodFilter = Field(default_factory=FundamentalPeriodFilter)

    model_config = {"frozen": True}


class BalanceSheetRequest(BaseModel):
    company_id: uuid.UUID = Field(...)
    period_filter: FundamentalPeriodFilter = Field(default_factory=FundamentalPeriodFilter)

    model_config = {"frozen": True}


class CashFlowStatementRequest(BaseModel):
    company_id: uuid.UUID = Field(...)
    period_filter: FundamentalPeriodFilter = Field(default_factory=FundamentalPeriodFilter)

    model_config = {"frozen": True}


class FinancialFactsRequest(BaseModel):
    company_id: uuid.UUID = Field(...)
    concepts: frozenset[FundamentalConceptKey] = Field(...)
    period_filter: FundamentalPeriodFilter = Field(default_factory=FundamentalPeriodFilter)

    model_config = {"frozen": True}
