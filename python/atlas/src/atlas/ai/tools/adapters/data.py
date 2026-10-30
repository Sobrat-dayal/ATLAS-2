"""Data Catalog Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.data.list_sources for discovery of authorized financial data resources.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult

CANONICAL_DATA_SOURCES = [
    {
        "source_id": "src_sec_edgar",
        "name": "SEC EDGAR Form 10-K & 10-Q Financial Disclosures",
        "category": "FUNDAMENTALS",
        "vendor": "U.S. Securities and Exchange Commission",
        "coverage": "US Public Companies (1994-Present)",
        "frequency": "Quarterly / Annual",
        "entitled": True,
    },
    {
        "source_id": "src_fred_macro",
        "name": "Federal Reserve Economic Data (FRED)",
        "category": "MACROECONOMICS",
        "vendor": "Federal Reserve Bank of St. Louis",
        "coverage": "Global & US Macro Indicators",
        "frequency": "Daily / Monthly / Quarterly",
        "entitled": True,
    },
    {
        "source_id": "src_sip_equities",
        "name": "Consolidated Tape Association / UTP SIP Equities",
        "category": "MARKET_DATA",
        "vendor": "Consolidated SIP",
        "coverage": "All US Listed Equities & ETFs",
        "frequency": "Tick-Level Real-Time / End of Day",
        "entitled": True,
    },
]


class DataListSourcesAdapter(BaseAiToolAdapter):
    """Adapter for atlas.data.list_sources."""

    tool_id = "atlas.data.list_sources"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        category = arguments.get("category")
        limit = min(int(arguments.get("limit", 10)), 50)

        results: List[Dict[str, Any]] = []
        for src in CANONICAL_DATA_SOURCES:
            if category and src["category"].upper() != category.upper():
                continue
            results.append(src)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"sources": results[:limit], "count": len(results[:limit])},
            data_source="ATLAS Global Data Catalog",
            attribution="ATLAS Enterprise Master Data Service",
            record_count=len(results[:limit]),
            execution_time_ms=elapsed_ms,
        )

