"""Instrument Tool Adapters for Stage 126: ATLAS AI Tool Gateway.

Implements atlas.instrument.search and atlas.instrument.get with canonical entity resolution.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult
from atlas.ai.tools.errors import AiToolArgumentInvalidError

# Canonical reference instrument fixture database
CANONICAL_INSTRUMENTS = [
    {
        "instrument_id": "inst_msft_us",
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "exchange": "NASDAQ",
        "asset_class": "EQUITY",
        "currency": "USD",
        "figi": "BBG000BPH459",
        "isin": "US5949181045",
        "country": "US",
        "sector": "Information Technology",
    },
    {
        "instrument_id": "inst_aapl_us",
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "asset_class": "EQUITY",
        "currency": "USD",
        "figi": "BBG000B9XRY4",
        "isin": "US0378331005",
        "country": "US",
        "sector": "Information Technology",
    },
    {
        "instrument_id": "inst_nvda_us",
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "exchange": "NASDAQ",
        "asset_class": "EQUITY",
        "currency": "USD",
        "figi": "BBG000BBJQV0",
        "isin": "US67066G1040",
        "country": "US",
        "sector": "Semiconductors",
    },
    {
        "instrument_id": "inst_googl_us",
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "exchange": "NASDAQ",
        "asset_class": "EQUITY",
        "currency": "USD",
        "figi": "BBG009S39JX6",
        "isin": "US02079K3059",
        "country": "US",
        "sector": "Communication Services",
    },
    {
        "instrument_id": "inst_tsla_us",
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "exchange": "NASDAQ",
        "asset_class": "EQUITY",
        "currency": "USD",
        "figi": "BBG000N9MNX3",
        "isin": "US88160R1014",
        "country": "US",
        "sector": "Consumer Discretionary",
    },
]


class InstrumentSearchAdapter(BaseAiToolAdapter):
    """Adapter for atlas.instrument.search (Fixture A)."""

    tool_id = "atlas.instrument.search"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        query = str(arguments.get("query", "")).strip().lower()
        if not query:
            raise AiToolArgumentInvalidError(self.tool_id, "Query cannot be empty.")

        exchange_filter = arguments.get("exchange")
        asset_class_filter = arguments.get("asset_class")
        limit = min(int(arguments.get("limit", 5)), 20)

        matches: List[Dict[str, Any]] = []
        for inst in CANONICAL_INSTRUMENTS:
            if (
                query in inst["symbol"].lower()
                or query in inst["name"].lower()
                or query in inst["instrument_id"].lower()
            ):
                if exchange_filter and inst["exchange"].upper() != exchange_filter.upper():
                    continue
                if asset_class_filter and inst["asset_class"].upper() != asset_class_filter.upper():
                    continue
                matches.append(inst)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"results": matches[:limit], "total_matches": len(matches)},
            data_source="ATLAS Canonical Instrument Registry",
            attribution="ATLAS Security Master",
            record_count=len(matches[:limit]),
            execution_time_ms=elapsed_ms,
        )


class InstrumentGetAdapter(BaseAiToolAdapter):
    """Adapter for atlas.instrument.get."""

    tool_id = "atlas.instrument.get"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        instrument_id = str(arguments.get("instrument_id", "")).strip()
        if not instrument_id:
            raise AiToolArgumentInvalidError(self.tool_id, "instrument_id must be provided.")

        # Look up by ID or symbol
        found = None
        for inst in CANONICAL_INSTRUMENTS:
            if (
                inst["instrument_id"].lower() == instrument_id.lower()
                or inst["symbol"].lower() == instrument_id.lower()
            ):
                found = inst
                break

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        if not found:
            return self.build_error_result(
                context=context,
                error_code="INSTRUMENT_NOT_FOUND",
                error_message=f"Canonical instrument '{instrument_id}' was not found.",
                execution_time_ms=elapsed_ms,
            )

        return self.build_result(
            context=context,
            data=found,
            data_source="ATLAS Canonical Instrument Registry",
            attribution="ATLAS Security Master",
            record_count=1,
            execution_time_ms=elapsed_ms,
        )
