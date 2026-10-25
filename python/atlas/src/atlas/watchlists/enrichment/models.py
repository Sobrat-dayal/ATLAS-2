"""Domain models and Pydantic schemas for Watchlist Enrichment (Stage 79).

Defines typed value representations, enrichment categories, status enums,
request/response schemas, and metadata contracts for company fundamentals,
valuation ratios, technical indicator snapshots, corporate events, earnings,
and news references.
"""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EnrichmentCategory(str, Enum):
    """Authorized categories of watchlist enrichment columns."""

    FUNDAMENTALS = "fundamentals"
    VALUATION = "valuation"
    TECHNICAL = "technical"
    EVENTS = "events"
    EARNINGS = "earnings"
    NEWS = "news"


class EnrichmentStatus(str, Enum):
    """Qualification status of an enriched financial value."""

    AVAILABLE = "AVAILABLE"
    STALE = "STALE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_ENTITLED = "NOT_ENTITLED"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    ERROR = "ERROR"


class WatchlistEnrichmentValue(BaseModel):
    """Typed, qualified financial enrichment value for a specific column and instrument."""

    column_id: str
    status: EnrichmentStatus = EnrichmentStatus.AVAILABLE
    value: Optional[Any] = None
    value_type: str = "TEXT"  # TEXT | MONETARY | NUMBER | PERCENTAGE | TIMESTAMP | ENUM
    unit: Optional[str] = None
    currency: Optional[str] = None

    entity_id: Optional[UUID] = None
    market_series_id: Optional[str] = None
    company_id: Optional[UUID] = None

    fiscal_period: Optional[str] = None  # e.g. "FY2025", "Q2 FY2026", "TTM"
    fiscal_year: Optional[int] = None
    period_end_date: Optional[str] = None

    observation_time: Optional[datetime.datetime] = None
    publication_time: Optional[datetime.datetime] = None
    as_of_date: Optional[str] = None

    source_id: Optional[str] = None
    source_document_id: Optional[str] = None
    methodology_id: Optional[str] = None
    revision_id: Optional[str] = None

    url: Optional[str] = None
    headline: Optional[str] = None
    publisher: Optional[str] = None
    event_status: Optional[str] = None  # CONFIRMED | ESTIMATED | TENTATIVE

    reason: Optional[str] = None

    model_config = {"frozen": False}

    def to_row_cell_dict(self) -> Dict[str, Any]:
        """Convert to WatchlistRowCellValue compatible dict."""
        return {
            "status": self.status.value,
            "value": self.value,
            "unit": self.unit,
            "measure_kind": self.methodology_id or self.column_id,
            "observed_at": self.observation_time,
            "source": self.source_id,
            "freshness": "fresh"
            if self.status == EnrichmentStatus.AVAILABLE
            else self.status.value.lower(),
            "reason": self.reason,
            "currency": self.currency,
            "fiscal_period": self.fiscal_period,
            "period_end_date": self.period_end_date,
            "publication_time": self.publication_time,
            "as_of": self.as_of_date,
            "methodology": self.methodology_id,
            "url": self.url,
            "headline": self.headline,
            "publisher": self.publisher,
            "event_status": self.event_status,
        }


class EnrichmentColumnMetadata(BaseModel):
    """Specification of an enrichment column's methodology, requirements, and asset applicability."""

    column_id: str
    category: EnrichmentCategory
    label: str
    description: str
    value_type: str
    unit: Optional[str] = None
    supported_asset_classes: List[str]
    source_capability: str
    methodology_id: Optional[str] = None
    methodology_version: int = 1
    requires_company_entity: bool = False
    requires_historical_bars: bool = False
    lookback_bars: int = 0
    interval: Optional[str] = None


class WatchlistEnrichmentRequest(BaseModel):
    """Batch query request for enrichment values across watchlist items."""

    selected_column_ids: List[str]
    item_ids: Optional[List[UUID]] = None
    calculation_policy: Literal["strict", "lenient"] = "lenient"
    max_lookback_bars: Optional[int] = Field(default=150, ge=1, le=500)


class WatchlistEnrichmentItemResult(BaseModel):
    """Enrichment output container for a single watchlist membership item."""

    watchlist_item_id: UUID
    instrument_entity_id: UUID
    market_series_id: Optional[str] = None
    company_id: Optional[UUID] = None
    values: Dict[str, WatchlistEnrichmentValue]


class WatchlistEnrichmentResponse(BaseModel):
    """Full batch response for watchlist enrichment query."""

    watchlist_id: UUID
    membership_revision: int
    column_registry_version: int = 1
    as_of: datetime.datetime
    results: List[WatchlistEnrichmentItemResult]
    partial_errors: Dict[str, str] = Field(default_factory=dict)
    source_context: Dict[str, str] = Field(default_factory=dict)
