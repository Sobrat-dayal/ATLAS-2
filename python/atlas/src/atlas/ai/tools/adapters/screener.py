"""Screener Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.screener.get_definition (read-only inspection, no mutations or execution jobs).
"""

from __future__ import annotations

import time
from typing import Any, Dict

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult
from atlas.ai.tools.errors import AiToolArgumentInvalidError, AiToolResourceAccessDeniedError

CANONICAL_SCREENERS = {
    "scr_quality_growth": {
        "screener_id": "scr_quality_growth",
        "name": "Quality Large-Cap Growth Screen",
        "owner_user_id": "user_primary",
        "universe": "US_LARGE_CAP",
        "filter_criteria": [
            {"dimension": "market_cap", "operator": ">=", "value": 50_000_000_000, "unit": "USD"},
            {"dimension": "revenue_growth_yoy", "operator": ">=", "value": 0.15, "unit": "ratio"},
            {"dimension": "return_on_equity", "operator": ">=", "value": 0.20, "unit": "ratio"},
            {"dimension": "net_debt_to_ebitda", "operator": "<=", "value": 2.5, "unit": "ratio"},
        ],
        "sorting": [{"dimension": "revenue_growth_yoy", "direction": "DESC"}],
        "created_at": "2026-08-01T10:00:00Z",
    },
}


class ScreenerGetDefinitionAdapter(BaseAiToolAdapter):
    """Adapter for atlas.screener.get_definition."""

    tool_id = "atlas.screener.get_definition"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        scr_id = arguments.get("screener_id")
        if not scr_id:
            raise AiToolArgumentInvalidError(self.tool_id, "screener_id must be provided.")

        screener = CANONICAL_SCREENERS.get(scr_id)
        if not screener:
            raise AiToolResourceAccessDeniedError("Screener", scr_id)

        # Ownership / ACL check
        if screener["owner_user_id"] != context.user_id and context.user_id != "user_primary":
            raise AiToolResourceAccessDeniedError("Screener", scr_id)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data=screener,
            data_source="ATLAS Screener Configuration Vault",
            attribution="ATLAS Quantitative Screening Engine",
            record_count=1,
            execution_time_ms=elapsed_ms,
        )

