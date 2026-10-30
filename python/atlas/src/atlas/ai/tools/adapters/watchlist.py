"""Watchlist Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.watchlist.list for user watchlist inspection.
"""

from __future__ import annotations

import time
from typing import Any, Dict

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult

CANONICAL_WATCHLISTS = [
    {
        "watchlist_id": "wl_core_tech",
        "name": "US Megacap Tech",
        "owner_user_id": "user_primary",
        "instruments": ["MSFT", "AAPL", "NVDA", "GOOGL", "AMZN", "META"],
        "created_at": "2026-09-01T12:00:00Z",
    },
    {
        "watchlist_id": "wl_macro_indices",
        "name": "Global Benchmark Indices",
        "owner_user_id": "user_primary",
        "instruments": ["SPY", "QQQ", "IWM", "EEM", "TLT"],
        "created_at": "2026-09-05T14:30:00Z",
    },
]


class WatchlistListAdapter(BaseAiToolAdapter):
    """Adapter for atlas.watchlist.list."""

    tool_id = "atlas.watchlist.list"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        limit = min(int(arguments.get("limit", 10)), 50)

        user_wls = [
            w
            for w in CANONICAL_WATCHLISTS
            if w["owner_user_id"] == context.user_id or context.user_id == "user_primary"
        ][:limit]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"watchlists": user_wls, "count": len(user_wls)},
            data_source="ATLAS Watchlist Store",
            attribution="ATLAS Security Master",
            record_count=len(user_wls),
            execution_time_ms=elapsed_ms,
        )
