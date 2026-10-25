"""Pydantic schemas for Watchlist Columns and Preferences (Stage 77)."""

import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WatchlistColumnDefinitionResponse(BaseModel):
    """Public API response representing an authorized column definition."""

    id: str
    version: int
    label: str
    description: str
    category: str
    value_type: str
    source_capability: str
    supported_asset_classes: List[str]
    formatter_id: str
    sort_policy: str
    default_visible: bool
    default_width: int
    min_width: int
    max_width: int
    can_hide: bool
    can_resize: bool
    can_pin: bool
    can_sort: bool


class WatchlistColumnSortConfig(BaseModel):
    """Sort state for a watchlist table."""

    column_id: Optional[str] = None
    direction: Optional[Literal["asc", "desc"]] = None


class WatchlistColumnConfigV1(BaseModel):
    """Validated version 1 presentation configuration document."""

    schema_version: int = 1
    ordered_column_ids: List[str]
    visible_column_ids: List[str]
    widths: Dict[str, int]
    pinned_left_column_ids: List[str] = Field(default_factory=list)
    sort: WatchlistColumnSortConfig = Field(default_factory=WatchlistColumnSortConfig)


class WatchlistColumnPreferencesResponse(BaseModel):
    """Response returned when reading or updating watchlist column preferences."""

    watchlist_id: UUID
    configuration_schema_version: int
    revision: int
    configuration: WatchlistColumnConfigV1
    is_default: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class WatchlistColumnPreferencesUpdateRequest(BaseModel):
    """Request payload to update column configuration for an owned watchlist."""

    configuration: WatchlistColumnConfigV1
    expected_revision: Optional[int] = None


class WatchlistRowCellValue(BaseModel):
    """Typed, qualified cell projection value."""

    # Status: AVAILABLE | UNAVAILABLE | NOT_APPLICABLE | NOT_ENTITLED | STALE
    status: str = "AVAILABLE"
    value: Optional[Any] = None
    unit: Optional[str] = None
    measure_kind: Optional[str] = None
    observed_at: Optional[datetime.datetime] = None
    source: Optional[str] = None
    freshness: Optional[str] = None
    reason: Optional[str] = None
    currency: Optional[str] = None
    fiscal_period: Optional[str] = None
    period_end_date: Optional[str] = None
    publication_time: Optional[datetime.datetime] = None
    as_of: Optional[str] = None
    methodology: Optional[str] = None
    url: Optional[str] = None
    headline: Optional[str] = None
    publisher: Optional[str] = None
    event_status: Optional[str] = None


class WatchlistRowProjection(BaseModel):
    """Projected watchlist instrument row with typed values for selected columns."""

    item_id: UUID
    instrument_entity_id: UUID
    market_series_id: str = ""
    manual_position: int
    values: Dict[str, WatchlistRowCellValue]
    has_company_page: bool = False
    issuer_id: Optional[UUID] = None


class WatchlistRowsResponse(BaseModel):
    """Response returned when querying projected rows with selected columns and sorting."""

    watchlist_id: UUID
    membership_revision: int
    selected_columns: List[str]
    total_items: int
    page: int
    page_size: int
    rows: List[WatchlistRowProjection]
    is_sorted: bool = False
    sort_column_id: Optional[str] = None
    sort_direction: Optional[str] = None
    incompatible_units_detected: bool = False
