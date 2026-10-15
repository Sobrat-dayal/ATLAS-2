"""Pydantic Models and DTOs for ATLAS Bonds & Fixed-Income Markets V1 (Stage 61)."""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .config import (
    BondTypeEnum,
    CouponFrequencyEnum,
    CouponTypeEnum,
    DayCountConventionEnum,
    IssuerCategoryEnum,
    MaturityBucketEnum,
    PriceBasisEnum,
    PriceKindEnum,
    PriceQuoteUnitEnum,
    SeniorityEnum,
    YieldTypeEnum,
)


class BondIssuerSummary(BaseModel):
    """Compact summary of a bond's legal issuer entity."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    issuer_entity_id: UUID = Field(..., description="Canonical Organization Entity UUID.")
    name: str = Field(..., min_length=2, max_length=128)
    issuer_category: IssuerCategoryEnum
    country_code: str = Field(..., min_length=2, max_length=8)
    jurisdiction: str = Field(..., min_length=2, max_length=64)


class BondContractTermsView(BaseModel):
    """Contractual terms and schedule metadata for a fixed-income security."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    issue_date: str = Field(..., description="Issue date in YYYY-MM-DD.")
    dated_date: Optional[str] = Field(default=None, description="Accrual start date.")
    maturity_date: Optional[str] = Field(default=None, description="Contractual maturity date.")
    is_perpetual: bool = Field(default=False)
    time_to_maturity_years: Optional[Decimal] = Field(
        default=None, description="Approximate calendar years to maturity (NOT duration)."
    )
    maturity_bucket: MaturityBucketEnum
    coupon_type: CouponTypeEnum
    coupon_rate: Optional[Decimal] = Field(
        default=None, description="Contractual annual coupon percentage (e.g. 4.25 for 4.25%)."
    )
    coupon_frequency: CouponFrequencyEnum
    day_count_convention: DayCountConventionEnum
    face_value: Decimal
    face_value_convention: str
    seniority: SeniorityEnum
    is_callable: bool = Field(default=False)
    is_putable: bool = Field(default=False)
    reference_index: Optional[str] = None
    floating_margin_bps: Optional[Decimal] = None


class BondPriceObservationView(BaseModel):
    """Source-aware market price observation and spread analytics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    clean_price: Optional[Decimal] = Field(
        default=None, description="Clean price excluding accrued interest."
    )
    dirty_price: Optional[Decimal] = Field(
        default=None, description="Dirty price including accrued interest."
    )
    accrued_interest: Optional[Decimal] = Field(
        default=None, description="Contractual accrued interest on stated basis."
    )
    price_basis: PriceBasisEnum = Field(default=PriceBasisEnum.CLEAN)
    quote_unit: PriceQuoteUnitEnum = Field(default=PriceQuoteUnitEnum.PERCENTAGE_OF_PAR)
    price_kind: PriceKindEnum = Field(default=PriceKindEnum.EVALUATED_PRICE)
    currency: str = Field(..., min_length=3, max_length=3)
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    spread: Optional[Decimal] = Field(default=None, description="Absolute spread ask - bid.")
    price_change_24h: Optional[Decimal] = None
    price_change_24h_percent: Optional[Decimal] = None
    source_timestamp: str = Field(..., description="Timestamp of observation from source.")
    received_at: str = Field(..., description="Timestamp of ingestion into ATLAS.")
    valuation_date: Optional[str] = None
    freshness_status: str = Field(default="REALTIME")
    delay_status: str = Field(default="REALTIME")
    provider: str = Field(default="OPENBB")


class BondYieldObservationView(BaseModel):
    """Typed yield observation and basis-point analytics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    yield_value: Optional[Decimal] = Field(
        default=None, description="Annualized percentage yield (e.g. 4.35 for 4.35%)."
    )
    yield_type: YieldTypeEnum = Field(default=YieldTypeEnum.YTM)
    yield_unit: str = Field(default="PERCENT_PER_ANNUM")
    yield_change_bps_24h: Optional[Decimal] = Field(
        default=None, description="Yield movement in basis points (1 bps = 0.01 percentage point)."
    )
    as_of: str = Field(..., description="Observation as-of timestamp or date.")
    source: str = Field(default="OPENBB")
    methodology: Optional[str] = None


class BondDirectoryItem(BaseModel):
    """Single item in the canonical bond securities directory."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID = Field(..., description="Canonical Financial Instrument UUID.")
    symbol: str
    name: str
    isin: Optional[str] = None
    cusip: Optional[str] = None
    issuer: BondIssuerSummary
    bond_type: BondTypeEnum
    currency: str
    terms: BondContractTermsView
    price: BondPriceObservationView
    yield_obs: BondYieldObservationView
    freshness_status: str = Field(default="REALTIME")
    provider: str = Field(default="OPENBB")
    data_status: str = Field(default="ACTIVE")


class BondCoverageSummary(BaseModel):
    """Summary counts and metrics for the authorized fixed-income universe."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_bonds: int = Field(..., ge=0)
    total_issuers: int = Field(..., ge=0)
    sovereign_bonds: int = Field(..., ge=0)
    corporate_bonds: int = Field(..., ge=0)
    other_bonds: int = Field(..., ge=0)
    bonds_with_prices: int = Field(..., ge=0)
    bonds_with_yields: int = Field(..., ge=0)
    bonds_with_accrued_interest: int = Field(..., ge=0)
    currencies: List[str] = Field(default_factory=list)


class BondFilterOptionsResponse(BaseModel):
    """Authoritative filter choices and catalog coverage."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    issuer_categories: List[str]
    bond_types: List[str]
    currencies: List[str]
    coupon_types: List[str]
    maturity_buckets: List[str]
    issuers: List[Dict[str, Any]]
    coverage: BondCoverageSummary


class BondDirectoryResponse(BaseModel):
    """Paginated response for the canonical bond directory."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default="1.0.0")
    scope: str = Field(default="authorized_configured_bonds_universe")
    items: List[BondDirectoryItem]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=100)
    next_cursor: Optional[str] = None
    has_more: bool = Field(default=False)
    coverage: BondCoverageSummary


class BondOverviewResponse(BaseModel):
    """Detailed overview response for a single inspected bond security."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default="1.0.0")
    instrument_entity_id: UUID
    symbol: str
    name: str
    isin: Optional[str] = None
    cusip: Optional[str] = None
    issuer: BondIssuerSummary
    bond_type: BondTypeEnum
    currency: str
    terms: BondContractTermsView
    price: BondPriceObservationView
    yield_obs: BondYieldObservationView
    provenance: Dict[str, str] = Field(default_factory=dict)
    availability: Dict[str, bool] = Field(default_factory=dict)
    non_executable_disclaimer: str = Field(
        default=(
            "Prices and yields are for research and reference only. Not executable trading quotes."
        )
    )
