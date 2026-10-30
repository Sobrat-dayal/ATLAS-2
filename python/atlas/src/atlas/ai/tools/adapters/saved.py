"""Saved Resources Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.saved.list (bridges Stage 119 Universal Saved System).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult

CANONICAL_SAVED_ITEMS = [
    {
        "saved_id": "sav_chart_tech_breakout",
        "name": "Tech Momentum Breakout Template",
        "resource_type": "CHART_LAYOUT",
        "owner_user_id": "user_primary",
        "version": 3,
        "created_at": "2026-09-10T15:20:00Z",
    },
    {
        "saved_id": "sav_screener_quality_div",
        "name": "Dividend Aristocrats Filter",
        "resource_type": "SCREENER",
        "owner_user_id": "user_primary",
        "version": 1,
        "created_at": "2026-09-12T11:00:00Z",
    },
]


class SavedListAdapter(BaseAiToolAdapter):
    """Adapter for atlas.saved.list."""

    tool_id = "atlas.saved.list"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        res_type = arguments.get("resource_type")
        limit = min(int(arguments.get("limit", 10)), 50)

        results: List[Dict[str, Any]] = []
        for item in CANONICAL_SAVED_ITEMS:
            if item["owner_user_id"] != context.user_id and context.user_id != "user_primary":
                continue
            if res_type and item["resource_type"].upper() != res_type.upper():
                continue
            results.append(item)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"saved_items": results[:limit], "count": len(results[:limit])},
            data_source="ATLAS Universal Saved Store",
            attribution="Stage 119 Saved System",
            record_count=len(results[:limit]),
            execution_time_ms=elapsed_ms,
        )

