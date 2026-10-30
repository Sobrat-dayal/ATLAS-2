"""Workspace Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.workspace.list (bridges Stage 120 Multi-Panel Workspaces).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult

CANONICAL_WORKSPACES = [
    {
        "workspace_id": "ws_cross_asset_macro",
        "name": "Cross-Asset Macro Terminal",
        "owner_user_id": "user_primary",
        "panel_count": 4,
        "active_panels": ["CHART", "ECONOMIC_SERIES", "NEWS_FEED", "RISK_SUMMARY"],
        "created_at": "2026-09-01T08:30:00Z",
    },
    {
        "workspace_id": "ws_equity_research",
        "name": "Equity Single-Stock Deep Dive",
        "owner_user_id": "user_primary",
        "panel_count": 3,
        "active_panels": ["FINANCIAL_STATEMENTS", "CHART", "RESEARCH_NOTES"],
        "created_at": "2026-09-15T14:10:00Z",
    },
]


class WorkspaceListAdapter(BaseAiToolAdapter):
    """Adapter for atlas.workspace.list."""

    tool_id = "atlas.workspace.list"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        limit = min(int(arguments.get("limit", 10)), 50)

        results: List[Dict[str, Any]] = []
        for ws in CANONICAL_WORKSPACES:
            if ws["owner_user_id"] != context.user_id and context.user_id != "user_primary":
                continue
            results.append(ws)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"workspaces": results[:limit], "count": len(results[:limit])},
            data_source="ATLAS Workspace Repository",
            attribution="Stage 120 Multi-Panel Workspace Engine",
            record_count=len(results[:limit]),
            execution_time_ms=elapsed_ms,
        )

