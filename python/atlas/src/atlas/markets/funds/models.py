"""Pydantic DTOs and SQLAlchemy models for ATLAS ETFs & Funds Markets V1 (Stage 58)."""

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
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
# 1. SQLAlchemy Storage Models
# =============================================================================
class FundMetadata(Base):
    """
    Authoritative database table representing core fund product metadata.
    Fulfills Stage 58 Sections 132-134.
    """

    __tablename__ = "fund_metadata"

    instrument_entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("securities.entity_id", ondelete="CASCADE"),
        primary_key=True,
    )
    fund_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    product_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="SET NULL"),
        nullable=True,
    )
    domicile: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    inception_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    investment_category: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, index=True
    )
    distribution_policy: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    base_currency: Mapped[str] = mapped_column(String(16), nullable=False, default="USD")
    share_class_currency: Mapped[str] = mapped_column(String(16), nullable=False, default="USD")
    benchmark_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="SET NULL"),
        nullable=True,
    )
    benchmark_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    manager_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="SET NULL"),
        nullable=True,
    )
    manager_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    sponsor_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    fund_objective: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    net_expense_ratio: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    gross_expense_ratio: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    fee_metric_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    fee_effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    total_aum: Mapped[Optional[float]] = mapped_column(Numeric(38, 2), nullable=True)
    aum_currency: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    aum_as_of_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    aum_scope: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    metadata_provenance: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class FundListingMetadata(Base):
    """
    Authoritative table representing exchange listing metadata for listed funds (ETFs, CEFs).
    Fulfills Stage 58 Section 131.
    """

    __tablename__ = "fund_listing_metadata"

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
    )
    exchange_mic: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, index=True)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    trading_currency: Mapped[str] = mapped_column(String(16), nullable=False, default="USD")
    listing_status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    is_primary_listing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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
            "uq_fund_listing_metadata_scoped",
            "instrument_entity_id",
            "exchange_mic",
            "symbol",
            unique=True,
        ),
    )


class FundNAVObservation(Base):
    """
    Authoritative table representing official Net Asset Value (NAV) observations.
    Fulfills Stage 58 Section 135.
    """

    __tablename__ = "fund_nav_observations"

    nav_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    instrument_entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("securities.entity_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nav_per_unit: Mapped[float] = mapped_column(Numeric(38, 6), nullable=False)
    nav_currency: Mapped[str] = mapped_column(String(16), nullable=False)
    valuation_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valuation_method: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, default="OFFICIAL_CLOSE_NAV"
    )
    provider_key: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    provenance: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index(
            "uq_fund_nav_observations_scoped",
            "instrument_entity_id",
            "valuation_date",
            "nav_currency",
            unique=True,
        ),
    )


# =============================================================================
# 2. Pydantic DTOs for Presentation & Read Models
# =============================================================================
class FundMarketQuoteView(BaseModel):
    """
    Exchange-traded market price observation.
    Only applicable to exchange-listed funds (ETFs, CEFs).
    """

    model_config = ConfigDict(from_attributes=True)

    last_price: Optional[str] = None
    bid_price: Optional[str] = None
    ask_price: Optional[str] = None
    reference_close: Optional[str] = None
    reference_source: Optional[str] = None
    absolute_change: Optional[str] = None
    percentage_change: Optional[str] = None
    change_direction: MarketSummaryChangeDirection = MarketSummaryChangeDirection.UNKNOWN

    source_timestamp: Optional[datetime] = None
    received_at: Optional[datetime] = None

    freshness_status: str = "unknown"
    delivery_delay_status: MarketSummaryDeliveryDelay = MarketSummaryDeliveryDelay.UNKNOWN

    provider_key: Optional[str] = None
    provider_display_name: Optional[str] = None

    data_status: MarketSummaryDataStatus = MarketSummaryDataStatus.NOT_CONFIGURED
    unavailable_reason: Optional[str] = None


class FundNAVView(BaseModel):
    """
    Official published Net Asset Value observation.
    Must never be conflated with exchange market price.
    """

    model_config = ConfigDict(from_attributes=True)

    nav_per_unit: Optional[str] = None
    nav_currency: Optional[str] = None
    valuation_date: Optional[date] = None
    published_at: Optional[datetime] = None
    valuation_method: Optional[str] = None
    provider_key: Optional[str] = None
    provenance: Optional[str] = None
    is_available: bool = False


class FundFeeView(BaseModel):
    """
    Reported expense and fee metrics.
    """

    model_config = ConfigDict(from_attributes=True)

    net_expense_ratio: Optional[str] = None
    gross_expense_ratio: Optional[str] = None
    fee_metric_type: Optional[str] = None
    fee_effective_date: Optional[date] = None
    is_available: bool = False


class FundAUMView(BaseModel):
    """
    Reported assets under management metric.
    """

    model_config = ConfigDict(from_attributes=True)

    total_aum: Optional[str] = None
    aum_currency: Optional[str] = None
    aum_as_of_date: Optional[date] = None
    aum_scope: Optional[str] = None
    is_available: bool = False


class FundDirectoryItem(BaseModel):
    """
    Unified directory item representing an investment fund or ETF share class.
    """

    model_config = ConfigDict(from_attributes=True)

    instrument_entity_id: UUID
    listing_id: Optional[UUID] = None
    fund_name: str
    display_symbol: str
    fund_type: str  # ETF, OPEN_END_MUTUAL_FUND, CLOSED_END_FUND, etc.

    # Listing context (null for unlisted open-end mutual funds)
    is_exchange_traded: bool = True
    exchange_mic: Optional[str] = None
    exchange_display_name: Optional[str] = None
    listing_market_country: Optional[str] = None
    trading_currency: Optional[str] = None
    listing_status: Optional[str] = "ACTIVE"

    # Fund characteristics
    domicile: Optional[str] = None
    investment_category: Optional[str] = None
    distribution_policy: Optional[str] = None
    base_currency: str = "USD"
    share_class_currency: str = "USD"

    # Parties & Benchmarks
    manager_name: Optional[str] = None
    sponsor_name: Optional[str] = None
    benchmark_name: Optional[str] = None

    # Market Price vs NAV (Crucial Stage 58 Separation)
    market_quote: Optional[FundMarketQuoteView] = None
    official_nav: Optional[FundNAVView] = None

    # Financial Attributes
    fees: FundFeeView = Field(default_factory=FundFeeView)
    aum: FundAUMView = Field(default_factory=FundAUMView)


class FundCoverageSummary(BaseModel):
    """
    Truthful coverage facts for the ATLAS fund catalog.
    """

    configured_funds_count: int
    etf_count: int
    mutual_fund_count: int
    closed_end_fund_count: int
    exchange_listed_count: int
    returned_count: int
    available_quotes_count: int
    available_navs_count: int
    unavailable_quotes_count: int
    unavailable_navs_count: int


class FundFilterOption(BaseModel):
    id: str
    label: str
    count: int


class FundExchangeFilterOption(BaseModel):
    mic: str
    name: str
    country: str
    count: int


class FundFilterOptionsResponse(BaseModel):
    fund_types: List[FundFilterOption] = Field(default_factory=list)
    countries: List[FundFilterOption] = Field(default_factory=list)
    exchanges: List[FundExchangeFilterOption] = Field(default_factory=list)
    categories: List[FundFilterOption] = Field(default_factory=list)
    currencies: List[FundFilterOption] = Field(default_factory=list)


class FundDirectoryFilters(BaseModel):
    fund_type: Optional[str] = None
    market_country: Optional[str] = None
    exchange: Optional[str] = None
    domicile: Optional[str] = None
    fund_category: Optional[str] = None
    share_class_currency: Optional[str] = None
    query: Optional[str] = None


class FundDirectoryResponse(BaseModel):
    schema_version: int = 1
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scope: str = "authorized_canonical_fund_directory"
    items: List[FundDirectoryItem]
    filters: FundDirectoryFilters
    coverage: FundCoverageSummary
    available_filters: FundFilterOptionsResponse
    next_cursor: Optional[str] = None
    has_more: bool = False


class FundIdentifierItem(BaseModel):
    scheme: str
    value: str
    is_primary: bool = False


class FundRelationshipsView(BaseModel):
    manager_company_id: Optional[UUID] = None
    manager_name: Optional[str] = None
    sponsor_name: Optional[str] = None
    benchmark_entity_id: Optional[UUID] = None
    benchmark_name: Optional[str] = None


class FundOverviewDetailResponse(BaseModel):
    schema_version: int = 1
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    item: FundDirectoryItem
    fund_objective: Optional[str] = None
    inception_date: Optional[date] = None
    identifiers: List[FundIdentifierItem] = Field(default_factory=list)
    relationships: FundRelationshipsView = Field(default_factory=FundRelationshipsView)
    coverage_limitations: List[str] = Field(default_factory=list)
