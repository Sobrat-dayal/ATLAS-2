"""Domain Models for Institutional Economics V1 (Stage 89).

Dataclasses representing canonical indicators, source-qualified series,
geographies, observation points, vintages, and macroeconomic summaries.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from .enums import (
    GeographicScopeKind,
    IndicatorCategory,
    ObservationStatus,
    PriceBasisKind,
    ReportingFrequency,
    SeasonalAdjustmentKind,
    StatisticalUnit,
    TransformationType,
)


@dataclass
class EconomicGeography:
    """Canonical country or regional economic area."""
    geography_id: str
    name: str
    iso_code: str
    scope_kind: GeographicScopeKind
    currency_code: str
    flag_emoji_code: str
    is_core: bool = True
    notes: Optional[str] = None


@dataclass
class EconomicIndicator:
    """Conceptual macroeconomic indicator definition (e.g., Real GDP Growth, CPI)."""
    indicator_id: str
    code: str
    name: str
    description: str
    category: IndicatorCategory
    default_unit: StatisticalUnit
    frequency: ReportingFrequency
    seasonal_adjustment: SeasonalAdjustmentKind
    price_basis: PriceBasisKind
    methodology_summary: str
    is_headline: bool = False


@dataclass
class EconomicSeries:
    """A specific statistical time-series for an indicator in a geography from an official provider."""
    series_id: str
    indicator_id: str
    indicator_code: str
    indicator_name: str
    geography_id: str
    geography_name: str
    provider_id: str
    source_series_code: str
    unit: StatisticalUnit
    frequency: ReportingFrequency
    seasonal_adjustment: SeasonalAdjustmentKind
    price_basis: PriceBasisKind
    first_period: str
    latest_period: str
    observation_count: int
    source_definition: str
    source_url: str
    is_active: bool = True
    vintage_supported: bool = True
    methodology_notes: Optional[str] = None


@dataclass
class EconomicObservationRecord:
    """A single canonical economic data observation point."""
    observation_id: str
    series_id: str
    period: str                     # e.g., "2024-Q3" or "2024-09"
    period_start: date
    period_end: date
    reference_date: date
    value: Decimal
    unit: StatisticalUnit
    status: ObservationStatus
    published_at: Optional[datetime] = None
    ingested_at: Optional[datetime] = None
    revision_number: int = 0
    vintage_id: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class EconomicVintageRecord:
    """Historical data vintage record reflecting point-in-time publication."""
    vintage_id: str
    series_id: str
    period: str
    vintage_date: date
    value: Decimal
    status: ObservationStatus
    published_at: datetime
    notes: str


@dataclass
class TransformationDefinition:
    """Mathematical specification of a supported statistical transformation."""
    transformation_type: TransformationType
    display_name: str
    formula_description: str
    supported_frequencies: List[ReportingFrequency]
    output_unit_description: str


@dataclass
class MajorEconomyMacroSummary:
    """Cross-indicator headline macroeconomic snapshot for a major economy."""
    geography_id: str
    geography_name: str
    iso_code: str
    currency_code: str
    gdp_growth_yoy: Optional[Decimal] = None
    gdp_growth_period: Optional[str] = None
    gdp_source: Optional[str] = None
    cpi_inflation_yoy: Optional[Decimal] = None
    cpi_period: Optional[str] = None
    cpi_source: Optional[str] = None
    unemployment_rate: Optional[Decimal] = None
    unemployment_period: Optional[str] = None
    unemployment_source: Optional[str] = None
    policy_interest_rate: Optional[Decimal] = None
    policy_rate_period: Optional[str] = None
    policy_rate_source: Optional[str] = None
    latest_observation_date: Optional[str] = None
    source_freshness: str = "PUBLISHED_CURRENT"
