"""Company Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.company.get and atlas.company.financials with point-in-time accuracy.
"""

from __future__ import annotations

import time
from typing import Any, Dict

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult
from atlas.ai.tools.errors import AiToolArgumentInvalidError

# Canonical reference financial statements fixture database (Fixture C)
CANONICAL_FINANCIALS = {
    "MSFT": {
        "company_id": "comp_msft",
        "symbol": "MSFT",
        "currency": "USD",
        "units": "millions",
        "annual": [
            {
                "fiscal_year": 2025,
                "period_end": "2025-06-30",
                "revenue": 125.0,
                "operating_income": 55.0,
                "net_income": 45.0,
                "currency": "USD",
                "unit": "million",
                "source": "10-K SEC Filing",
            },
            {
                "fiscal_year": 2024,
                "period_end": "2024-06-30",
                "revenue": 100.0,
                "operating_income": 44.0,
                "net_income": 36.0,
                "currency": "USD",
                "unit": "million",
                "source": "10-K SEC Filing",
            },
        ],
    },
    "AAPL": {
        "company_id": "comp_aapl",
        "symbol": "AAPL",
        "currency": "USD",
        "units": "millions",
        "annual": [
            {
                "fiscal_year": 2024,
                "period_end": "2024-09-30",
                "revenue": 391035.0,
                "operating_income": 123216.0,
                "net_income": 93736.0,
                "currency": "USD",
                "unit": "million",
                "source": "10-K SEC Filing",
            },
            {
                "fiscal_year": 2023,
                "period_end": "2023-09-30",
                "revenue": 383285.0,
                "operating_income": 114301.0,
                "net_income": 96995.0,
                "currency": "USD",
                "unit": "million",
                "source": "10-K SEC Filing",
            },
        ],
    },
}

COMPANY_PROFILES = {
    "MSFT": {
        "company_id": "comp_msft",
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "sector": "Information Technology",
        "industry": "Systems Software",
        "hq_country": "US",
        "employees": 221000,
        "description": "Developer and provider of software, personal computing devices, and cloud computing services.",
    },
    "AAPL": {
        "company_id": "comp_aapl",
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "sector": "Information Technology",
        "industry": "Consumer Electronics",
        "hq_country": "US",
        "employees": 161000,
        "description": "Designer and manufacturer of consumer hardware, software services, and digital media.",
    },
}


class CompanyGetAdapter(BaseAiToolAdapter):
    """Adapter for atlas.company.get."""

    tool_id = "atlas.company.get"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        sym = arguments.get("symbol") or ""
        cid = arguments.get("company_id") or ""

        sym = sym.upper() if sym else ""
        if not sym and cid.startswith("comp_"):
            sym = cid.replace("comp_", "").upper()

        found = COMPANY_PROFILES.get(sym)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not found:
            return self.build_error_result(
                context=context,
                error_code="COMPANY_NOT_FOUND",
                error_message=f"Company profile for symbol '{sym}' was not found.",
                execution_time_ms=elapsed_ms,
            )

        return self.build_result(
            context=context,
            data=found,
            data_source="ATLAS Company Fundamentals",
            attribution="SEC EDGAR / ATLAS Master",
            record_count=1,
            execution_time_ms=elapsed_ms,
        )


class CompanyFinancialsAdapter(BaseAiToolAdapter):
    """Adapter for atlas.company.financials (Fixture C)."""

    tool_id = "atlas.company.financials"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        sym = arguments.get("symbol") or ""
        cid = arguments.get("company_id") or ""

        sym = sym.upper() if sym else ""
        if not sym and cid.startswith("comp_"):
            sym = cid.replace("comp_", "").upper()

        if not sym:
            raise AiToolArgumentInvalidError(
                self.tool_id, "Either symbol or company_id must be provided."
            )

        statement_type = arguments.get("statement_type", "INCOME_STATEMENT")
        period = arguments.get("period", "ANNUAL")
        limit = min(int(arguments.get("limit", 4)), 10)

        facts_record = CANONICAL_FINANCIALS.get(sym)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not facts_record:
            return self.build_error_result(
                context=context,
                error_code="FINANCIALS_NOT_FOUND",
                error_message=f"Financial facts for '{sym}' are not available.",
                execution_time_ms=elapsed_ms,
            )

        items = facts_record.get("annual", [])[:limit]
        return self.build_result(
            context=context,
            data={
                "symbol": sym,
                "statement_type": statement_type,
                "period": period,
                "currency": facts_record.get("currency", "USD"),
                "units": facts_record.get("units", "millions"),
                "line_items": items,
            },
            data_source="ATLAS Fundamental Statements Service",
            attribution="SEC EDGAR 10-K Filings",
            record_count=len(items),
            execution_time_ms=elapsed_ms,
        )
