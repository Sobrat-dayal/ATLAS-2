"""Pydantic schemas and DTOs for Watchlists V1 (Stage 76)."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WatchlistCreateRequest(BaseModel):
    """Payload to create a new watchlist."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ..., min_length=1, max_length=100, description="Display name for the watchlist."
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="Optional brief description of the watchlist."
    )


class WatchlistUpdateRequest(BaseModel):
    """Payload to update metadata (name/description) of an existing watchlist."""

    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(
        default=None, min_length=1, max_length=100, description="New display name."
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="New description (or null)."
    )


class WatchlistSummaryResponse(BaseModel):
    """Summary representation of a user's watchlist."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_user_id: UUID
    name: str
    description: Optional[str] = None
    item_count: int
    revision: int
    created_at: datetime
    updated_at: datetime


class WatchlistListResponse(BaseModel):
    """Paginated list of user watchlists."""

    model_config = ConfigDict(from_attributes=True)

    items: List[WatchlistSummaryResponse]
    total: int
    page: int
    page_size: int


class WatchlistItemResponse(BaseModel):
    """Detailed representation of a canonical financial instrument membership row in a watchlist."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    watchlist_id: UUID
    instrument_entity_id: UUID
    market_series_id: str
    position: int
    created_at: datetime

    # Display / Canonical Metadata
    symbol: str
    display_name: str
    canonical_name: str
    asset_class: str
    venue: Optional[str] = None
    quote_currency: Optional[str] = None
    quote_unit: Optional[str] = None

    # Latest Qualified Market Data Snapshot
    is_quote_available: bool = False
    quote_measure: Optional[str] = (
        None  # e.g. "Last", "Mid", "NAV", "Clean Price", "Yield", "Reference"
    )
    last_price: Optional[str] = None
    bid_price: Optional[str] = None
    ask_price: Optional[str] = None
    absolute_change: Optional[str] = None
    percentage_change: Optional[str] = None
    change_direction: str = "unknown"  # "up", "down", "flat", "unknown"
    source_timestamp: Optional[datetime] = None
    freshness_status: str = "unavailable"  # "fresh", "aging", "stale", "unavailable"
    delivery_delay_status: str = "unknown"  # "realtime", "delayed", "unknown"
    delay_seconds: Optional[int] = None
    provider: Optional[str] = None

    # Verified Issuer / Company Cross-Navigation
    issuer_entity_id: Optional[UUID] = None
    has_company_page: bool = False


class WatchlistDetailResponse(BaseModel):
    """Full representation of a watchlist including its ordered membership items."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_user_id: UUID
    name: str
    description: Optional[str] = None
    revision: int
    created_at: datetime
    updated_at: datetime
    items: List[WatchlistItemResponse]
    total_items: int
    page: int
    page_size: int


class AddWatchlistItemRequest(BaseModel):
    """Payload to add a canonical financial instrument to a watchlist."""

    model_config = ConfigDict(extra="forbid")

    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument Entity UUID."
    )
    market_series_id: Optional[str] = Field(
        default="", max_length=128, description="Optional market-series identifier or exchange MIC."
    )


class ReorderWatchlistItemsRequest(BaseModel):
    """Payload to reorder instruments in a watchlist with optimistic concurrency."""

    model_config = ConfigDict(extra="forbid")

    ordered_item_ids: List[UUID] = Field(
        ...,
        min_length=0,
        max_length=250,
        description="Full ordered array of membership item UUIDs.",
    )
    expected_revision: int = Field(
        ..., ge=1, description="Expected current watchlist revision for concurrency check."
    )


class ReorderWatchlistItemsResponse(BaseModel):
    """Confirmation response after successful atomic reorder."""

    model_config = ConfigDict(from_attributes=True)

    watchlist_id: UUID
    revision: int
    ordered_item_ids: List[UUID]
