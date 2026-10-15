"""Pydantic DTOs and SQLAlchemy models for ATLAS Equities Markets V1 (Stage 57)."""

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database.base import Base
from atlas.home.market_summary.models import (
    MarketSummaryChangeDirection,
    MarketSummaryDataStatus,
    MarketSummaryDeliveryDelay,
)


# =============================================================================
# 1. SQLAlchemy Storage Model
# =============================================================================
class EquityListingMetadata(Base):
    """
    Authoritative database table representing exchange-scoped equity listing metadata.
    Fulfills Stage 57 Section 131.
    """

    __tablename__ = "equity_listing_metadata"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    instrument_entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("securities.entity_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exchange_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exchanges.entity_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    exchange_mic: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, index=True)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    quote_currency: Mapped[str] = mapped_column(String(16), nullable=False, default="USD")
    listing_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="ACTIVE", index=True
    )
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    metadata_provenance: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index(
            "uq_equity_listing_metadata_scoped",
            "instrument_entity_id",
            "exchange_mic",
            "symbol",
            unique=True,
        ),
    )


# =============================================================================
# 2. Pydantic DTOs for Directory & Discovery
# =============================================================================
class FilterCountryItem(BaseModel):
    """Available listing market country option with item count."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(..., description="ISO Alpha-2 country code (e.g. US, IN, GB).")
    name: str = Field(..., description="Full human-readable country name.")
    count: int = Field(ge=0, description="Number of matching equities in catalog.")


class FilterExchangeItem(BaseModel):
    """Available exchange / trading venue option with item count."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: Optional[UUID] = Field(default=None, description="Canonical Exchange entity UUID.")
    mic: Optional[str] = Field(default=None, description="Market Identifier Code (e.g. XNAS).")
    name: str = Field(..., description="Human-readable exchange display label.")
    country_code: Optional[str] = Field(default=None, description="Country code of exchange venue.")
    count: int = Field(ge=0, description="Number of matching equities listed on this venue.")


class FilterTypeItem(BaseModel):
    """Available equity subtype classification option with item count."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Subtype identifier (common_stock, preferred_stock, etc.).")
    label: str = Field(..., description="Human-readable subtype label.")
    count: int = Field(ge=0, description="Number of matching equities with this subtype.")


class FilterStatusItem(BaseModel):
    """Available listing status option with item count."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Status code (ACTIVE, INACTIVE, DELISTED, SUSPENDED).")
    label: str = Field(..., description="Human-readable status label.")
    count: int = Field(ge=0, description="Number of matching equities.")


class EquityFilterOptionsResponse(BaseModel):
    """Aggregate available filter options grounded strictly in canonical catalog contents."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    countries: List[FilterCountryItem] = Field(default_factory=list)
    exchanges: List[FilterExchangeItem] = Field(default_factory=list)
    equity_types: List[FilterTypeItem] = Field(default_factory=list)
    listing_statuses: List[FilterStatusItem] = Field(default_factory=list)


class EquityCoverageSummary(BaseModel):
    """Truthful coverage metrics for the Equities Directory."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_catalog_count: int = Field(
        ge=0, description="Total number of accessible canonical equity instruments in ATLAS."
    )
    returned_count: int = Field(
        ge=0, description="Number of equity instruments in the current response page."
    )
    exchanges_represented: int = Field(
        ge=0, description="Number of distinct exchanges represented in catalog."
    )
    countries_represented: int = Field(
        ge=0, description="Number of distinct listing market countries represented."
    )
    available_quotes_count: int = Field(
        ge=0, description="Number of equities with available live/cached quote observations."
    )
    unavailable_quotes_count: int = Field(
        ge=0, description="Number of equities without available quote observations."
    )


class EquityDirectoryFiltersApplied(BaseModel):
    """Filters actively applied to the directory query."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    query: Optional[str] = Field(default=None)
    market_country: Optional[str] = Field(default=None)
    exchange: Optional[str] = Field(default=None)
    equity_type: Optional[str] = Field(default=None)
    listing_status: Optional[str] = Field(default=None)


class EquityDirectoryItem(BaseModel):
    """Canonical per-equity presentation DTO for directory table and list views."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority."
    )
    listing_id: Optional[UUID] = Field(
        default=None, description="Listing metadata UUID if tracked in database."
    )
    display_name: str = Field(
        ..., min_length=1, max_length=256, description="Human-readable security display name."
    )
    display_symbol: str = Field(
        ..., min_length=1, max_length=64, description="Exchange-scoped trading ticker symbol."
    )
    equity_subtype: str = Field(
        default="common_stock",
        description="Canonical classification (common_stock, preferred_stock, depositary_receipt).",
    )
    equity_subtype_label: str = Field(
        default="Common Equity", description="Human-readable subtype label."
    )
    share_class_name: Optional[str] = Field(
        default=None, max_length=128, description="Specific share class (e.g. Class A, Ordinary)."
    )

    # Exchange & Venue identification
    exchange_id: Optional[UUID] = Field(
        default=None, description="Canonical Exchange entity UUID."
    )
    exchange_mic: Optional[str] = Field(
        default=None, max_length=16, description="Market Identifier Code (e.g. XNAS, XNYS)."
    )
    exchange_display_name: Optional[str] = Field(
        default=None, max_length=128, description="Human-readable exchange venue name."
    )
    listing_market_country: Optional[str] = Field(
        default=None, max_length=128, description="Listing market country name."
    )
    listing_market_country_code: Optional[str] = Field(
        default=None, max_length=8, description="ISO Alpha-2 listing market country code."
    )
    trading_currency: Optional[str] = Field(
        default="USD", max_length=16, description="Trading and quote currency ISO code."
    )
    listing_status: str = Field(
        default="ACTIVE", description="Listing status (ACTIVE, INACTIVE, DELISTED, SUSPENDED)."
    )

    # Issuer Company (Stage 18 / 23 relationship separation)
    issuer_company_entity_id: Optional[UUID] = Field(
        default=None,
        description="Verified Company entity UUID if authoritative relationship exists.",
    )
    issuer_company_name: Optional[str] = Field(
        default=None, max_length=256, description="Issuer Company legal or display name."
    )

    # Market Data & Quote Observations (Stage 41 + 52/56 arithmetic)
    last_price: Optional[str] = Field(
        default=None, description="Latest traded price serialized as Decimal string."
    )
    bid_price: Optional[str] = Field(default=None, description="Current highest bid price.")
    ask_price: Optional[str] = Field(default=None, description="Current lowest ask price.")

    reference_close: Optional[str] = Field(
        default=None, description="Verified completed-session reference close price."
    )
    reference_session_date: Optional[date] = Field(
        default=None, description="Date of completed reference trading session."
    )
    reference_source: Optional[str] = Field(
        default=None, description="Source of reference close."
    )

    absolute_change: Optional[str] = Field(
        default=None, description="Signed price change relative to valid reference close."
    )
    percentage_change: Optional[str] = Field(
        default=None, description="Signed percentage change relative to valid reference close."
    )
    change_direction: MarketSummaryChangeDirection = Field(
        default=MarketSummaryChangeDirection.UNKNOWN,
        description="Performance direction derived from absolute change.",
    )

    source_timestamp: Optional[datetime] = Field(
        default=None, description="Observation timestamp from source feed in UTC."
    )
    received_at: Optional[datetime] = Field(
        default=None, description="Timestamp when observation entered ATLAS pipeline."
    )

    # Stage 44 freshness integration
    freshness_status: str = Field(
        default="unavailable", description="Freshness status (fresh, aging, stale, unavailable)."
    )
    delivery_delay_status: MarketSummaryDeliveryDelay = Field(
        default=MarketSummaryDeliveryDelay.UNKNOWN,
        description="Realtime vs delayed feed classification.",
    )
    delay_seconds: Optional[int] = Field(
        default=None, ge=0, description="Reported upstream feed delay duration in seconds."
    )

    # Provenance
    provider_key: Optional[str] = Field(
        default=None, description="Safe identifier of data provider."
    )
    provider_display_name: Optional[str] = Field(
        default=None, description="Human-readable data provider name."
    )

    # Availability & error handling
    data_status: MarketSummaryDataStatus = Field(
        default=MarketSummaryDataStatus.NO_QUOTE, description="Data availability classification."
    )
    unavailable_reason: Optional[str] = Field(
        default=None, description="Safe diagnostic reason when observation is unavailable."
    )


class EquityDirectoryResponse(BaseModel):
    """Root presentation response for GET /api/v1/markets/equities."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = Field(default=1, description="Presentation schema version.")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response assembly UTC timestamp.",
    )
    scope: str = Field(
        default="authorized_canonical_equity_directory",
        description="Authoritative scope declaration.",
    )
    filters: EquityDirectoryFiltersApplied = Field(..., description="Applied filters.")
    coverage: EquityCoverageSummary = Field(..., description="Coverage statistics.")
    available_filters: EquityFilterOptionsResponse = Field(
        ..., description="Available filter options."
    )
    items: List[EquityDirectoryItem] = Field(
        default_factory=list, description="Paginated canonical equity records."
    )
    next_cursor: Optional[str] = Field(
        default=None, description="Cursor for the next page of results."
    )
    has_more: bool = Field(
        default=False, description="True if additional configured equities remain."
    )


# =============================================================================
# 3. Pydantic DTOs for Security Overview Inspector
# =============================================================================
class EquityIdentifierItem(BaseModel):
    """Universal identifier associated with the equity security (Stage 21)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scheme_key: str = Field(..., description="Scheme key (e.g. ticker, isin, figi, cusip).")
    value: str = Field(..., description="Identifier value.")
    is_current: bool = Field(default=True, description="Whether identifier is currently effective.")


class EquityIssuerCompanyDetails(BaseModel):
    """Verified issuer company details linked via Stage 23 relationship."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    company_entity_id: UUID = Field(..., description="Canonical Company UUID authority.")
    legal_name: Optional[str] = Field(default=None, description="Official legal corporate name.")
    short_name: Optional[str] = Field(default=None, description="Common or brand name.")
    organization_type: Optional[str] = Field(default=None, description="e.g. public_company.")
    status: Optional[str] = Field(default=None, description="e.g. active.")
    website_url: Optional[str] = Field(default=None, description="Official website URL.")
    primary_country: Optional[str] = Field(
        default=None, description="Incorporation or HQ country."
    )


class EquityVenueDetails(BaseModel):
    """Listing venue details grounded in canonical Exchange entity."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    exchange_id: Optional[UUID] = Field(default=None, description="Exchange entity UUID.")
    name: Optional[str] = Field(default=None, description="Exchange display name.")
    mic: Optional[str] = Field(default=None, description="Market Identifier Code.")
    timezone_name: Optional[str] = Field(
        default=None, description="Exchange operating timezone."
    )
    exchange_kind: Optional[str] = Field(default=None, description="e.g. stock_exchange.")
    country_name: Optional[str] = Field(default=None, description="Exchange market country.")
    country_code: Optional[str] = Field(default=None, description="ISO country code.")


class EquityOverviewDetailResponse(BaseModel):
    """Detailed Security Overview for GET /api/v1/markets/equities/{instrument_entity_id}."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Inherits full item presentation
    item: EquityDirectoryItem = Field(..., description="Core equity listing and quote item.")

    # Extended inspector details
    identifiers: List[EquityIdentifierItem] = Field(
        default_factory=list, description="Associated universal identifiers."
    )
    issuer_company: Optional[EquityIssuerCompanyDetails] = Field(
        default=None, description="Verified issuer company details if relationship exists."
    )
    venue_details: Optional[EquityVenueDetails] = Field(
        default=None, description="Authoritative venue details."
    )
    disclaimer: str = Field(
        default=(
            "ATLAS canonical equities discovery. Advanced fundamentals, ratios, "
            "screeners, and charts are scheduled for roadmap Stages 66-98."
        ),
        description="Coverage boundary notice.",
    )
