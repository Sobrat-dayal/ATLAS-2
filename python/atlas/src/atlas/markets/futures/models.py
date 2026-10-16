"""Pydantic Models and DTOs for ATLAS Futures & Commodities Markets V1 (Stage 62)."""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .config import (
    CommodityCategoryEnum,
    ContractLifecycleEnum,
    SettlementStatusEnum,
    SettlementTypeEnum,
    VolumeWindowEnum,
)


class CommoditySummary(BaseModel):
    """Compact summary of an underlying economic commodity or index."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    commodity_entity_id: UUID = Field(..., description="Canonical Commodity Entity UUID.")
    name: str = Field(..., min_length=2, max_length=128)
    slug: str = Field(..., min_length=2, max_length=64)
    category: CommodityCategoryEnum
    grade_specification: Optional[str] = None
    physical_unit: str = Field(..., min_length=1, max_length=64)
    reference_region: Optional[str] = None
    delivery_characteristics: Optional[str] = None


class FuturesProductSummary(BaseModel):
    """Summary of a standardized futures contract product family."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    product_entity_id: UUID = Field(..., description="Canonical Futures Product UUID.")
    underlying_entity_id: UUID = Field(..., description="Canonical Underlying Entity UUID.")
    root_symbol: str = Field(..., min_length=1, max_length=16)
    name: str = Field(..., min_length=2, max_length=128)
    exchange: str = Field(..., min_length=2, max_length=32)
    exchange_mic: str = Field(..., min_length=4, max_length=4)
    category: CommodityCategoryEnum
    contract_size: Decimal
    size_unit: str = Field(..., min_length=1, max_length=64)
    quote_currency: str = Field(..., min_length=3, max_length=3)
    quote_unit: str = Field(..., min_length=1, max_length=64)
    tick_size: Decimal
    tick_value: Optional[Decimal] = None
    settlement_type: SettlementTypeEnum
    contract_multiplier: Decimal = Decimal("1.0")


class FuturesContractSpecificationView(BaseModel):
    """Detailed verified contract specifications and schedule."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    contract_size: Decimal
    size_unit: str
    quote_currency: str
    quote_unit: str
    tick_size: Decimal
    tick_value: Optional[Decimal] = None
    settlement_type: SettlementTypeEnum
    contract_multiplier: Decimal = Decimal("1.0")
    trading_hours: str
    expiration_date: str
    last_trading_date: str
    first_notice_date: Optional[str] = None
    last_notice_date: Optional[str] = None
    delivery_start_date: Optional[str] = None
    delivery_end_date: Optional[str] = None
    settlement_date: str


class FuturesPriceObservationView(BaseModel):
    """Source-aware market price observation and bid/ask quote state."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    last: Optional[Decimal] = Field(
        default=None, description="Latest executed trade price. Distinct from official settlement."
    )
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    spread: Optional[Decimal] = Field(default=None, description="Absolute spread ask - bid.")
    quote_unit: str
    quote_currency: str
    source_timestamp: str = Field(..., description="Timestamp of observation from source.")
    received_at: str = Field(..., description="Timestamp of ingestion into ATLAS.")
    freshness_status: str = Field(default="REALTIME")
    delay_status: str = Field(default="REALTIME")
    provider: str = Field(default="OPENBB")


class FuturesSettlementObservationView(BaseModel):
    """Official daily settlement price observation determined by exchange clearing house."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    settlement_price: Optional[Decimal] = Field(
        default=None,
        description="Official daily settlement price. Distinct from latest executed trade.",
    )
    settlement_status: SettlementStatusEnum = Field(default=SettlementStatusEnum.FINAL)
    trade_date: Optional[str] = Field(
        default=None, description="Official trade date of settlement (YYYY-MM-DD)."
    )
    publication_timestamp: Optional[str] = None
    quote_unit: str
    provider: str = Field(default="OPENBB")


class FuturesPriceChangeView(BaseModel):
    """Qualified price movement relative to official previous settlement of the same contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    change_absolute: Optional[Decimal] = Field(
        default=None,
        description="Current price minus qualified reference price (in quote units).",
    )
    change_percent: Optional[Decimal] = Field(
        default=None,
        description=(
            "Percentage change. Suppressed (None) if reference price <= 0 "
            "to avoid misleading arithmetic."
        ),
    )
    reference_price: Optional[Decimal] = Field(
        default=None, description="Official reference price (typically previous settlement)."
    )
    reference_type: str = Field(default="PREVIOUS_SETTLEMENT")
    change_ticks: Optional[Decimal] = Field(
        default=None, description="Price change expressed in minimum tick increments."
    )


class FuturesVolumeOpenInterestView(BaseModel):
    """Trading volume and reported open interest observations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    volume: Optional[int] = Field(
        default=None,
        description=(
            "Number of contracts traded during the specified window. Distinct from open interest."
        ),
    )
    volume_window: VolumeWindowEnum = Field(default=VolumeWindowEnum.SESSION)
    open_interest: Optional[int] = Field(
        default=None,
        description="Total outstanding active contract positions. Reported on clearing schedule.",
    )
    open_interest_as_of: Optional[str] = Field(
        default=None, description="As-of date of the reported open interest observation."
    )
    provider: str = Field(default="OPENBB")


class FuturesContractDirectoryItem(BaseModel):
    """Item representation for the Futures Contracts Directory table."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID = Field(..., description="Canonical Financial Instrument UUID.")
    product_entity_id: UUID = Field(..., description="Canonical Futures Product UUID.")
    underlying_entity_id: UUID = Field(..., description="Canonical Underlying Entity UUID.")
    symbol: str = Field(..., min_length=2, max_length=32)
    name: str = Field(..., min_length=2, max_length=128)
    product_name: str
    underlying_name: str
    exchange: str
    exchange_mic: str
    category: CommodityCategoryEnum
    contract_year: int
    contract_month_code: str
    contract_month: str
    expiration_date: str
    last_trading_date: str
    lifecycle_status: ContractLifecycleEnum
    settlement_type: SettlementTypeEnum
    contract_size: Decimal
    size_unit: str
    tick_size: Decimal
    tick_value: Optional[Decimal] = None
    quote_currency: str
    quote_unit: str

    # Market Observations
    price_observation: FuturesPriceObservationView
    settlement_observation: FuturesSettlementObservationView
    price_change: FuturesPriceChangeView
    volume_open_interest: FuturesVolumeOpenInterestView


class FuturesContractOverviewResponse(BaseModel):
    """Comprehensive inspection view of a single selected futures contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID
    symbol: str
    name: str
    exchange: str
    exchange_mic: str
    contract_year: int
    contract_month_code: str
    contract_month: str
    lifecycle_status: ContractLifecycleEnum

    # Associated Canonical Entities
    underlying: CommoditySummary
    product: FuturesProductSummary

    # Terms & Schedule
    specifications: FuturesContractSpecificationView

    # Market Observations
    price_observation: FuturesPriceObservationView
    settlement_observation: FuturesSettlementObservationView
    price_change: FuturesPriceChangeView
    volume_open_interest: FuturesVolumeOpenInterestView

    # Source & Quality
    provider: str
    freshness_status: str
    delay_status: str
    source_timestamp: str
    received_at: str


class CommodityDirectoryItem(BaseModel):
    """Item representation for the Commodities catalog view."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    commodity_entity_id: UUID
    name: str
    slug: str
    category: CommodityCategoryEnum
    grade_specification: Optional[str] = None
    physical_unit: str
    reference_region: Optional[str] = None
    delivery_characteristics: Optional[str] = None
    associated_products_count: int = 0
    active_contracts_count: int = 0
    associated_products: List[FuturesProductSummary] = Field(default_factory=list)


class CommoditySpotBenchmarkView(BaseModel):
    """Observation representation for a physical commodity spot benchmark."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    benchmark_entity_id: UUID
    commodity_entity_id: UUID
    commodity_name: str
    name: str
    grade: str
    location: str
    currency: str
    quote_unit: str
    assessment_methodology: str
    latest_price: Optional[Decimal] = None
    previous_price: Optional[Decimal] = None
    change_absolute: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    as_of_date: str
    provider: str = "OPENBB"


class FuturesCoverageSummary(BaseModel):
    """Global coverage metrics across canonical commodities and futures contracts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_commodities: int = Field(..., description="Count of canonical underlying commodities.")
    total_products: int = Field(..., description="Count of standardized futures products.")
    total_contracts: int = Field(..., description="Count of cataloged listed futures contracts.")
    active_contracts: int = Field(..., description="Count of actively trading contracts.")
    contracts_with_last: int = Field(
        ..., description="Count of contracts with latest trade prices."
    )
    contracts_with_settlement: int = Field(
        ..., description="Count of contracts with official settlements."
    )
    contracts_with_volume: int = Field(..., description="Count of contracts with observed volume.")
    contracts_with_open_interest: int = Field(
        ..., description="Count of contracts with reported open interest."
    )
    exchanges_represented: List[str] = Field(default_factory=list)


class FuturesFilterOptionsResponse(BaseModel):
    """Available filter options for contracts directory navigation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    categories: List[str]
    exchanges: List[str]
    products: List[Dict[str, Any]]
    months: List[str]
    settlement_types: List[str]
    lifecycle_statuses: List[str]
    coverage: FuturesCoverageSummary


class FuturesContractDirectoryResponse(BaseModel):
    """Paginated response for the Futures Contract Directory."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    items: List[FuturesContractDirectoryItem]
    total: int
    limit: int
    cursor: Optional[str] = None
    next_cursor: Optional[str] = None
    has_more: bool
    coverage: FuturesCoverageSummary


class CommodityDirectoryResponse(BaseModel):
    """Response for the Commodities catalog view."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    items: List[CommodityDirectoryItem]
    total: int


class SpotBenchmarkDirectoryResponse(BaseModel):
    """Response for the Spot Benchmarks catalog view."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    items: List[CommoditySpotBenchmarkView]
    total: int
