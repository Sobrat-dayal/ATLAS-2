from typing import Protocol

from atlas.fundamentals.requests import (
    BalanceSheetRequest,
    CashFlowStatementRequest,
    FinancialFactsRequest,
    IncomeStatementRequest,
)
from atlas.fundamentals.responses import (
    BalanceSheetResponse,
    CashFlowStatementResponse,
    FinancialFactsResponse,
    IncomeStatementResponse,
)


class IncomeStatementFundamentalProvider(Protocol):
    async def get_income_statements(self, request: IncomeStatementRequest) -> IncomeStatementResponse:
        ...


class BalanceSheetFundamentalProvider(Protocol):
    async def get_balance_sheets(self, request: BalanceSheetRequest) -> BalanceSheetResponse:
        ...


class CashFlowFundamentalProvider(Protocol):
    async def get_cash_flow_statements(self, request: CashFlowStatementRequest) -> CashFlowStatementResponse:
        ...


class FinancialFactsFundamentalProvider(Protocol):
    async def get_financial_facts(self, request: FinancialFactsRequest) -> FinancialFactsResponse:
        ...
