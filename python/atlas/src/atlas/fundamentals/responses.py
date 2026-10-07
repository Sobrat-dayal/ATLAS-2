import uuid
from typing import Optional

from pydantic import BaseModel, Field

from atlas.fundamentals.facts import FinancialFact
from atlas.fundamentals.origin import FundamentalDataOrigin
from atlas.fundamentals.statements import BalanceSheet, CashFlowStatement, IncomeStatement


class IncomeStatementResponse(BaseModel):
    company_id: uuid.UUID = Field(...)
    provider_origin: Optional[FundamentalDataOrigin] = Field(default=None)
    statements: tuple[IncomeStatement, ...] = Field(...)

    model_config = {"frozen": True}


class BalanceSheetResponse(BaseModel):
    company_id: uuid.UUID = Field(...)
    provider_origin: Optional[FundamentalDataOrigin] = Field(default=None)
    statements: tuple[BalanceSheet, ...] = Field(...)

    model_config = {"frozen": True}


class CashFlowStatementResponse(BaseModel):
    company_id: uuid.UUID = Field(...)
    provider_origin: Optional[FundamentalDataOrigin] = Field(default=None)
    statements: tuple[CashFlowStatement, ...] = Field(...)

    model_config = {"frozen": True}


class FinancialFactsResponse(BaseModel):
    company_id: uuid.UUID = Field(...)
    provider_origin: Optional[FundamentalDataOrigin] = Field(default=None)
    facts: tuple[FinancialFact, ...] = Field(...)

    model_config = {"frozen": True}
