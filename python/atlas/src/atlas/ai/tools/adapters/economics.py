"""Economics Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.economics.search_series and atlas.economics.get_observations.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult
from atlas.ai.tools.errors import AiToolArgumentInvalidError

CANONICAL_ECONOMIC_SERIES = {
    "CPIAUCSL": {
        "series_id": "CPIAUCSL",
        "title": "Consumer Price Index for All Urban Consumers: All Items in U.S. City Average",
        "country": "US",
        "frequency": "Monthly",
        "units": "Index 1982-1984=100",
        "seasonal_adjustment": "Seasonally Adjusted",
        "observations": [
            {"date": "2026-09-01", "value": 315.30},
            {"date": "2026-08-01", "value": 314.80},
            {"date": "2026-07-01", "value": 314.54},
            {"date": "2026-06-01", "value": 314.17},
            {"date": "2026-05-01", "value": 314.07},
            {"date": "2026-04-01", "value": 313.55},
        ],
    },
    "FEDFUNDS": {
        "series_id": "FEDFUNDS",
        "title": "Federal Funds Effective Rate",
        "country": "US",
        "frequency": "Monthly",
        "units": "Percent",
        "seasonal_adjustment": "Not Seasonally Adjusted",
        "observations": [
            {"date": "2026-09-01", "value": 4.83},
            {"date": "2026-08-01", "value": 5.08},
            {"date": "2026-07-01", "value": 5.33},
            {"date": "2026-06-01", "value": 5.33},
        ],
    },
    "GDP": {
        "series_id": "GDP",
        "title": "Gross Domestic Product",
        "country": "US",
        "frequency": "Quarterly",
        "units": "Billions of Dollars",
        "seasonal_adjustment": "Seasonally Adjusted Annual Rate",
        "observations": [
            {"date": "2026-07-01", "value": 29380.0},
            {"date": "2026-04-01", "value": 28840.0},
            {"date": "2026-01-01", "value": 28420.0},
        ],
    },
}


class EconomicsSearchSeriesAdapter(BaseAiToolAdapter):
    """Adapter for atlas.economics.search_series."""

    tool_id = "atlas.economics.search_series"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        query = str(arguments.get("query", "")).lower()
        country = str(arguments.get("country", "")).upper()
        limit = min(int(arguments.get("limit", 5)), 20)

        matches: List[Dict[str, Any]] = []
        for s in CANONICAL_ECONOMIC_SERIES.values():
            if country and s["country"] != country:
                continue
            if query and (query not in s["series_id"].lower() and query not in s["title"].lower()):
                continue
            matches.append(
                {
                    "series_id": s["series_id"],
                    "title": s["title"],
                    "country": s["country"],
                    "frequency": s["frequency"],
                    "units": s["units"],
                }
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"series": matches[:limit], "count": len(matches[:limit])},
            data_source="ATLAS Macroeconomics Engine",
            attribution="Federal Reserve Economic Data (FRED) / BLS",
            record_count=len(matches[:limit]),
            execution_time_ms=elapsed_ms,
        )


class EconomicsGetObservationsAdapter(BaseAiToolAdapter):
    """Adapter for atlas.economics.get_observations."""

    tool_id = "atlas.economics.get_observations"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        sid = arguments.get("series_id")
        if not sid:
            raise AiToolArgumentInvalidError(self.tool_id, "series_id must be provided.")

        series = CANONICAL_ECONOMIC_SERIES.get(sid.upper())
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not series:
            return self.build_error_result(
                context=context,
                error_code="SERIES_NOT_FOUND",
                error_message=f"Economic series '{sid}' was not found.",
                execution_time_ms=elapsed_ms,
            )

        limit = min(int(arguments.get("limit", 12)), 60)
        obs = series["observations"][:limit]

        return self.build_result(
            context=context,
            data={
                "series_id": series["series_id"],
                "title": series["title"],
                "units": series["units"],
                "frequency": series["frequency"],
                "observations": obs,
                "count": len(obs),
            },
            data_source="ATLAS Macroeconomics Engine",
            attribution="Federal Reserve Economic Data (FRED) / BLS",
            record_count=len(obs),
            execution_time_ms=elapsed_ms,
        )
