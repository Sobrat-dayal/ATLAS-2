"""Portfolio Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.portfolio.list, atlas.portfolio.get_summary (Fixture D),
and atlas.portfolio.get_performance with strict multi-tenant ACL enforcement.
"""

from __future__ import annotations

import time
from typing import Any, Dict

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult
from atlas.ai.tools.errors import AiToolArgumentInvalidError, AiToolResourceAccessDeniedError

# Sample canonical portfolio fixture data
CANONICAL_PORTFOLIOS = {
    "port_growth_1": {
        "portfolio_id": "port_growth_1",
        "name": "US Core Growth Strategy",
        "owner_user_id": "user_primary",
        "currency": "USD",
        "total_value": 1_250_000.0,
        "cash_balance": 45_000.0,
        "asset_allocation": {
            "Equity": 0.88,
            "Fixed Income": 0.08,
            "Cash": 0.04,
        },
        "holdings": [
            {"symbol": "MSFT", "weight": 0.22, "value": 275000.0, "shares": 641},
            {"symbol": "AAPL", "weight": 0.18, "value": 225000.0, "shares": 957},
            {"symbol": "NVDA", "weight": 0.16, "value": 200000.0, "shares": 1400},
            {"symbol": "GOOGL", "weight": 0.14, "value": 175000.0, "shares": 1029},
            {"symbol": "TSLA", "weight": 0.10, "value": 125000.0, "shares": 500},
        ],
    },
    "port_macro_2": {
        "portfolio_id": "port_macro_2",
        "name": "Global Macro Hedge",
        "owner_user_id": "user_other",  # Owned by a different user for IDOR testing
        "currency": "USD",
        "total_value": 5_400_000.0,
        "cash_balance": 820_000.0,
        "asset_allocation": {
            "Equity": 0.45,
            "Fixed Income": 0.35,
            "Commodities": 0.05,
            "Cash": 0.15,
        },
        "holdings": [
            {"symbol": "SPY", "weight": 0.25, "value": 1350000.0},
            {"symbol": "TLT", "weight": 0.20, "value": 1080000.0},
        ],
    },
}


class PortfolioListAdapter(BaseAiToolAdapter):
    """Adapter for atlas.portfolio.list."""

    tool_id = "atlas.portfolio.list"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        limit = min(int(arguments.get("limit", 10)), 50)

        # Filter strictly to portfolios owned by authenticated user
        user_portfolios = [
            {
                "portfolio_id": p["portfolio_id"],
                "name": p["name"],
                "currency": p["currency"],
                "total_value": p["total_value"],
            }
            for p in CANONICAL_PORTFOLIOS.values()
            if p["owner_user_id"] == context.user_id
        ][:limit]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"portfolios": user_portfolios, "count": len(user_portfolios)},
            data_source="ATLAS Portfolio Engine",
            attribution="ATLAS Accounting Ledger",
            record_count=len(user_portfolios),
            execution_time_ms=elapsed_ms,
        )


class PortfolioGetSummaryAdapter(BaseAiToolAdapter):
    """Adapter for atlas.portfolio.get_summary (Fixture D)."""

    tool_id = "atlas.portfolio.get_summary"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        port_id = arguments.get("portfolio_id")
        if not port_id:
            raise AiToolArgumentInvalidError(self.tool_id, "portfolio_id must be provided.")

        portfolio = CANONICAL_PORTFOLIOS.get(port_id)
        if not portfolio:
            raise AiToolResourceAccessDeniedError("Portfolio", port_id)

        # Enforce strict ownership / authorization (Fixture D)
        if portfolio["owner_user_id"] != context.user_id:
            raise AiToolResourceAccessDeniedError("Portfolio", port_id)

        include_holdings = bool(arguments.get("include_holdings", False))

        data = {
            "portfolio_id": portfolio["portfolio_id"],
            "name": portfolio["name"],
            "currency": portfolio["currency"],
            "total_value": portfolio["total_value"],
            "cash_balance": portfolio["cash_balance"],
            "asset_allocation": portfolio["asset_allocation"],
            "holdings_count": len(portfolio["holdings"]),
            "holdings_redacted": not include_holdings,
        }

        if include_holdings:
            data["holdings"] = portfolio["holdings"]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data=data,
            data_source="ATLAS Portfolio Engine",
            attribution="ATLAS Custody & Position Master",
            record_count=1,
            execution_time_ms=elapsed_ms,
        )


class PortfolioGetPerformanceAdapter(BaseAiToolAdapter):
    """Adapter for atlas.portfolio.get_performance."""

    tool_id = "atlas.portfolio.get_performance"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        port_id = arguments.get("portfolio_id")
        if not port_id:
            raise AiToolArgumentInvalidError(self.tool_id, "portfolio_id must be provided.")

        portfolio = CANONICAL_PORTFOLIOS.get(port_id)
        if not portfolio or portfolio["owner_user_id"] != context.user_id:
            raise AiToolResourceAccessDeniedError("Portfolio", port_id)

        timeframe = arguments.get("timeframe", "YTD")
        benchmark = arguments.get("benchmark_id", "SPY")

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={
                "portfolio_id": port_id,
                "timeframe": timeframe,
                "benchmark_id": benchmark,
                "portfolio_return": 0.184,
                "benchmark_return": 0.152,
                "alpha": 0.032,
                "beta": 1.08,
                "sharpe_ratio": 1.74,
                "tracking_error": 0.028,
                "max_drawdown": -0.062,
            },
            data_source="ATLAS Analytics Performance Engine",
            attribution="Time-Weighted Return Standard (GIPS compliant)",
            record_count=1,
            execution_time_ms=elapsed_ms,
        )
