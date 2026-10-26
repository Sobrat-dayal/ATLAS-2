"""Domain models and entity definitions for Financial Screeners V1 (Stage 94)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from atlas.screeners.enums import (
    ConsolidationScope,
    EditorType,
    FilterCategory,
    FilterOperator,
    FreshnessStatus,
    ListingStatus,
    SecurityType,
    UnitKind,
    ValueType,
)


class ScreenerUniverseDefinition(BaseModel):
    """Canonical definition of an investment screening universe."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    universe_id: str
    name: str
    description: str
    asset_class: str = "EQUITY"
    eligible_security_types: List[SecurityType]
    eligible_listing_statuses: List[ListingStatus]
    geographic_scope: Optional[List[str]] = None
    exchange_scope: Optional[List[str]] = None
    is_default: bool = False


class ScreenerFilterDefinition(BaseModel):
    """Canonical typed filter definition in the Screener Filter Registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    filter_id: str
    display_name: str
    description: str
    category: FilterCategory
    value_type: ValueType
    unit_kind: UnitKind
    allowed_operators: List[FilterOperator]
    eligible_security_types: List[SecurityType] = Field(default_factory=list)
    eligible_industries: List[str] = Field(default_factory=list)
    default_operator: FilterOperator = FilterOperator.GTE
    is_range_supported: bool = True
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    editor_type: EditorType = EditorType.DECIMAL_INPUT
    currency_options: Optional[List[str]] = None
    magnitude_options: Optional[List[str]] = None
    aliases: List[str] = Field(default_factory=list)
    methodology_reference: Optional[str] = None
    decimal_precision: Optional[int] = 2
    entitlement_state: str = "PUBLIC"
    source_coverage_summary: Optional[str] = None



class ScreenerColumnDefinition(BaseModel):
    """Presentation column specification for screener tables."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    column_id: str
    display_label: str
    category: FilterCategory
    data_type: ValueType
    unit_kind: UnitKind
    sortable: bool = True
    default_visible: bool = False
    description: str = ""
    alignment: str = "left"


class ScreenerObservationRecord(BaseModel):
    """
    Authoritative candidate observation joining canonical security identity,
    exchange listing, issuer company, market metrics, fundamentals, and ratios.
    """

    model_config = ConfigDict(extra="ignore")

    instrument_entity_id: UUID
    listing_id: UUID = Field(default_factory=uuid.uuid4)
    issuer_company_entity_id: UUID

    canonical_security_name: str
    ticker: str
    exchange_mic: str
    exchange_name: str

    listing_country: str
    listing_country_code: str
    issuer_country: str
    issuer_country_code: str

    trading_currency: str = "USD"
    reporting_currency: str = "USD"

    security_type: SecurityType = SecurityType.COMMON_STOCK
    share_class_name: Optional[str] = None
    listing_status: ListingStatus = ListingStatus.ACTIVE

    sector: Optional[str] = None
    industry: Optional[str] = None

    # Market metrics
    last_price: Optional[Decimal] = None
    price_change_pct: Optional[Decimal] = None
    price_timestamp: Optional[datetime] = None
    price_freshness: FreshnessStatus = FreshnessStatus.LIVE
    market_cap: Optional[Decimal] = None
    volume_latest: Optional[Decimal] = None
    volume_20d_avg: Optional[Decimal] = None
    traded_value_latest: Optional[Decimal] = None

    # Fundamental metrics
    revenue: Optional[Decimal] = None
    net_income: Optional[Decimal] = None
    operating_income: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    book_equity: Optional[Decimal] = None
    eps: Optional[Decimal] = None

    # Valuation & Profitability Ratios
    pe_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    ps_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    gross_margin: Optional[Decimal] = None
    operating_margin: Optional[Decimal] = None
    net_margin: Optional[Decimal] = None
    roe: Optional[Decimal] = None
    roa: Optional[Decimal] = None

    # Reporting metadata
    fiscal_period: Optional[str] = "FY2025"
    fiscal_period_type: Optional[str] = "ANNUAL"
    consolidation_scope: ConsolidationScope = ConsolidationScope.CONSOLIDATED
    is_restated: bool = False

    provider: str = "openbb"
    provenance: str = "CANONICAL_EXCHANGE_FEED"
