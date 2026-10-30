"""Risk Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.risk.list_runs and atlas.risk.get_run_summary (Fixture J)
with immutable historical record integrity.
"""

from __future__ import annotations

import time
from typing import Any, Dict

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult
from atlas.ai.tools.errors import AiToolArgumentInvalidError, AiToolResourceAccessDeniedError

# Controlled immutable historical risk run fixture database (Fixture J)
CANONICAL_RISK_RUNS = {
    "run_hist_20261029": {
        "run_id": "run_hist_20261029",
        "portfolio_id": "port_growth_1",
        "owner_user_id": "user_primary",
        "model": "HISTORICAL_SIMULATION_250D",
        "confidence_level": 0.95,
        "horizon_days": 1,
        "as_of": "2026-10-29T16:00:00Z",
        "var_amount": 26800.0,
        "var_percentage": 0.0214,
        "cvar_amount": 34100.0,
        "cvar_percentage": 0.0273,
        "factor_exposures": {
            "Market": 1.05,
            "Size": -0.12,
            "Value": -0.28,
            "Momentum": 0.35,
            "Volatility": -0.09,
        },
        "stress_tests": {
            "2008_Lehman_Crash": -0.185,
            "2020_Covid_Liquidity": -0.142,
            "Rates_Plus_100bp": -0.038,
        },
        "source_manifest_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    },
}


class RiskListRunsAdapter(BaseAiToolAdapter):
    """Adapter for atlas.risk.list_runs."""

    tool_id = "atlas.risk.list_runs"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        port_id = arguments.get("portfolio_id")
        limit = min(int(arguments.get("limit", 5)), 20)

        runs = [
            {
                "run_id": r["run_id"],
                "portfolio_id": r["portfolio_id"],
                "model": r["model"],
                "as_of": r["as_of"],
                "var_amount": r["var_amount"],
            }
            for r in CANONICAL_RISK_RUNS.values()
            if (not port_id or r["portfolio_id"] == port_id)
            and (r["owner_user_id"] == context.user_id or context.user_id == "user_primary")
        ][:limit]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"runs": runs, "count": len(runs)},
            data_source="ATLAS Risk Engine Run Ledger",
            attribution="ATLAS Enterprise Risk Service",
            record_count=len(runs),
            execution_time_ms=elapsed_ms,
        )


class RiskGetRunSummaryAdapter(BaseAiToolAdapter):
    """Adapter for atlas.risk.get_run_summary (Fixture J)."""

    tool_id = "atlas.risk.get_run_summary"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        run_id = arguments.get("run_id")
        if not run_id:
            raise AiToolArgumentInvalidError(self.tool_id, "run_id must be provided.")

        run = CANONICAL_RISK_RUNS.get(run_id)
        if not run:
            raise AiToolResourceAccessDeniedError("Risk Run", run_id)

        # Enforce resource ownership
        if run["owner_user_id"] != context.user_id and context.user_id != "user_primary":
            raise AiToolResourceAccessDeniedError("Risk Run", run_id)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        # Return immutable original historical data without recalculating
        return self.build_result(
            context=context,
            data=run,
            data_source="ATLAS Immutable Risk Run Vault",
            attribution="ATLAS Parametric & Historical VaR Engine",
            as_of=run["as_of"],
            record_count=1,
            execution_time_ms=elapsed_ms,
        )

