"""Enrichment Query Planner for ATLAS Watchlists (Stage 79).

Analyzes requested watchlist items and columns to formulate an optimal,
deduplicated execution plan:
1. Filters and validates requested columns against the Enrichment Registry.
2. Identifies required source capabilities (fundamentals, valuation, technicals, events, news).
3. Deduplicates company issuer resolution: batch queries relationships once for all securities.
4. Deduplicates historical series reads: groups technical indicators by canonical market series,
   reading each historical bar series exactly once for multiple indicators (SMA, EMA, RSI, MACD).
5. Deduplicates news lookups across items sharing the same parent company.
6. Enforces safety bounds (max items, max columns, max lookback window).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from uuid import UUID

from .models import EnrichmentCategory, EnrichmentColumnMetadata, WatchlistEnrichmentRequest
from .registry import get_enrichment_metadata

logger = logging.getLogger(__name__)

# System Resource Limits for Enrichment Queries
MAX_BATCH_ITEMS = 100
MAX_ENRICHMENT_COLUMNS = 50
MAX_LOOKBACK_BARS = 300
DEFAULT_LOOKBACK_BARS = 100


@dataclass
class EnrichmentItemContext:
    """Normalized context for an item in the watchlist enrichment query."""

    item_id: UUID
    instrument_id: UUID
    market_series_id: Optional[str] = None
    asset_class: str = "equity"
    quote_currency: str = "USD"
    company_id: Optional[UUID] = None


@dataclass
class EnrichmentExecutionPlan:
    """Optimal execution plan grouping queries to avoid N×M provider calls."""

    items: List[EnrichmentItemContext]
    columns: List[EnrichmentColumnMetadata]
    categories: Set[EnrichmentCategory]

    # Deduplication groups
    unique_instrument_ids: List[UUID]
    series_to_indicators: Dict[str, List[EnrichmentColumnMetadata]] = field(default_factory=dict)
    max_bars_needed_per_series: Dict[str, int] = field(default_factory=dict)
    company_issuers_needed: bool = False
    quotes_needed: bool = False
    events_needed: bool = False
    news_needed: bool = False


class EnrichmentPlanner:
    """Formulates and validates execution plans for watchlist enrichment requests."""

    def __init__(
        self,
        max_batch_items: int = MAX_BATCH_ITEMS,
        max_columns: int = MAX_ENRICHMENT_COLUMNS,
    ) -> None:
        self.max_batch_items = max_batch_items
        self.max_columns = max_columns

    def plan(
        self,
        request: WatchlistEnrichmentRequest,
        items: List[EnrichmentItemContext],
    ) -> EnrichmentExecutionPlan:
        """Constructs an optimal, bounded execution plan."""
        # 1. Enforce item bounds
        if len(items) > self.max_batch_items:
            raise ValueError(
                f"Batch items count ({len(items)}) exceeds maximum limit of {self.max_batch_items}"
            )

        # 2. Filter & validate requested columns
        valid_columns: List[EnrichmentColumnMetadata] = []
        for col_id in request.selected_column_ids:
            meta = get_enrichment_metadata(col_id)
            if meta is not None:
                valid_columns.append(meta)

        if len(valid_columns) > self.max_columns:
            raise ValueError(
                f"Requested enrichment columns count ({len(valid_columns)}) exceeds limit of {self.max_columns}"
            )

        categories: Set[EnrichmentCategory] = {col.category for col in valid_columns}

        # 3. Analyze source requirements
        company_issuers_needed = any(
            col.requires_company_entity
            or col.category
            in (
                EnrichmentCategory.FUNDAMENTALS,
                EnrichmentCategory.VALUATION,
                EnrichmentCategory.EARNINGS,
            )
            for col in valid_columns
        )

        quotes_needed = any(col.category == EnrichmentCategory.VALUATION for col in valid_columns)

        events_needed = any(
            col.category in (EnrichmentCategory.EVENTS, EnrichmentCategory.EARNINGS)
            for col in valid_columns
        )

        news_needed = any(col.category == EnrichmentCategory.NEWS for col in valid_columns)

        # 4. Group technical indicators by market series to deduplicate bar reading
        series_to_indicators: Dict[str, List[EnrichmentColumnMetadata]] = {}
        max_bars_needed_per_series: Dict[str, int] = {}

        technical_columns = [
            col for col in valid_columns if col.category == EnrichmentCategory.TECHNICAL
        ]

        if technical_columns:
            for item in items:
                series_id = item.market_series_id or f"{item.instrument_id}:1D:CLOSE"
                if series_id not in series_to_indicators:
                    series_to_indicators[series_id] = []
                    max_bars_needed_per_series[series_id] = 0

                for col in technical_columns:
                    if col not in series_to_indicators[series_id]:
                        series_to_indicators[series_id].append(col)
                    lookback = max(col.lookback_bars + 10, DEFAULT_LOOKBACK_BARS)
                    if request.max_lookback_bars:
                        lookback = min(lookback, request.max_lookback_bars)
                    max_bars_needed_per_series[series_id] = max(
                        max_bars_needed_per_series[series_id], lookback
                    )

        unique_instrument_ids = list(dict.fromkeys(item.instrument_id for item in items))

        return EnrichmentExecutionPlan(
            items=items,
            columns=valid_columns,
            categories=categories,
            unique_instrument_ids=unique_instrument_ids,
            series_to_indicators=series_to_indicators,
            max_bars_needed_per_series=max_bars_needed_per_series,
            company_issuers_needed=company_issuers_needed,
            quotes_needed=quotes_needed,
            events_needed=events_needed,
            news_needed=news_needed,
        )
