"""Research Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.research.list_metadata with strictly bounded metadata inspection (no broad vector RAG).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult

CANONICAL_REPORTS = [
    {
        "report_id": "rep_2026_cloud_infra",
        "symbol": "MSFT",
        "title": "Hyperscale Cloud Infrastructure: Enterprise AI Unit Economics & Capex Trajectory",
        "author": "Victoria Chen, CFA",
        "published_at": "2026-10-15T09:00:00Z",
        "rating": "OUTPERFORM",
        "price_target": 480.0,
        "access_tier": "INSTITUTIONAL",
        "summary": "Deep-dive analysis of server cluster depreciation cycles and generative AI operating margins.",
    },
    {
        "report_id": "rep_2026_semi_foundry",
        "symbol": "NVDA",
        "title": "Silicon Packaging Architecture and High-Bandwidth Memory Supply Constraints",
        "author": "Marcus Sterling, PhD",
        "published_at": "2026-10-18T11:30:00Z",
        "rating": "OVERWEIGHT",
        "price_target": 165.0,
        "access_tier": "INSTITUTIONAL",
        "summary": "Assessment of next-generation packaging capacity and wafer-level interconnect yields.",
    },
]


class ResearchListMetadataAdapter(BaseAiToolAdapter):
    """Adapter for atlas.research.list_metadata."""

    tool_id = "atlas.research.list_metadata"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        query = str(arguments.get("query", "")).lower()
        symbol = str(arguments.get("symbol", "")).upper()
        limit = min(int(arguments.get("limit", 5)), 20)

        results: List[Dict[str, Any]] = []
        for rep in CANONICAL_REPORTS:
            if symbol and rep["symbol"] != symbol:
                continue
            if query and (
                query not in rep["title"].lower() and query not in rep["summary"].lower()
            ):
                continue
            results.append(rep)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"reports": results[:limit], "count": len(results[:limit])},
            data_source="ATLAS Equity Research Repository",
            attribution="ATLAS Global Institutional Research",
            record_count=len(results[:limit]),
            execution_time_ms=elapsed_ms,
        )
