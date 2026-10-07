import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from atlas.fundamentals.concept_registry import registry
from atlas.fundamentals.enums import (
    AccountingStandard,
    AuditStatus,
    FinancialPeriodNature,
    FinancialStatementType,
)
from atlas.fundamentals.errors import (
    concept_wrong_period_nature_error,
    concept_wrong_statement_error,
)
from atlas.fundamentals.line_items import StatementLineItem
from atlas.fundamentals.origin import FundamentalDataOrigin
from atlas.fundamentals.periods import FinancialPeriod


class FinancialReportMetadata(BaseModel):
    accounting_standard: Optional[AccountingStandard] = Field(default=None)
    audit_status: Optional[AuditStatus] = Field(default=None)
    filing_date: Optional[date] = Field(default=None)
    reported_at: Optional[datetime] = Field(default=None)
    is_restated: Optional[bool] = Field(default=None)

    model_config = {"frozen": True}


class BaseFinancialStatement(BaseModel):
    company_id: uuid.UUID = Field(...)
    statement_type: FinancialStatementType = Field(...)
    period: FinancialPeriod = Field(...)
    metadata: FinancialReportMetadata = Field(default_factory=FinancialReportMetadata)
    origin: FundamentalDataOrigin = Field(...)
    line_items: tuple[StatementLineItem, ...] = Field(...)

    @model_validator(mode="after")
    def validate_statement(self) -> "BaseFinancialStatement":
        if not self.line_items:
            raise ValueError("Financial statement must have at least one line item.")

        seen_concepts = set()
        for item in self.line_items:
            if item.concept in seen_concepts:
                raise ValueError(f"Duplicate canonical concept found in statement: {item.concept}")
            seen_concepts.add(item.concept)
            
            concept_def = registry.get(item.concept)
            if concept_def:
                if self.statement_type not in concept_def.statement_types:
                    raise concept_wrong_statement_error(item.concept, self.statement_type.value)
                if self.period.nature != concept_def.period_nature:
                    raise concept_wrong_period_nature_error(item.concept, concept_def.period_nature.value, self.period.nature.value)

        return self

    model_config = {"frozen": True}


class IncomeStatement(BaseFinancialStatement):
    statement_type: FinancialStatementType = Field(default=FinancialStatementType.INCOME_STATEMENT, frozen=True)

    @model_validator(mode="after")
    def validate_income_statement(self) -> "IncomeStatement":
        if self.period.nature != FinancialPeriodNature.DURATION:
            raise ValueError("Income statement period nature must be duration.")
        return self


class BalanceSheet(BaseFinancialStatement):
    statement_type: FinancialStatementType = Field(default=FinancialStatementType.BALANCE_SHEET, frozen=True)

    @model_validator(mode="after")
    def validate_balance_sheet(self) -> "BalanceSheet":
        if self.period.nature != FinancialPeriodNature.INSTANT:
            raise ValueError("Balance sheet period nature must be instant.")
        return self


class CashFlowStatement(BaseFinancialStatement):
    statement_type: FinancialStatementType = Field(default=FinancialStatementType.CASH_FLOW_STATEMENT, frozen=True)

    @model_validator(mode="after")
    def validate_cash_flow_statement(self) -> "CashFlowStatement":
        if self.period.nature != FinancialPeriodNature.DURATION:
            raise ValueError("Cash flow statement period nature must be duration.")
        return self
