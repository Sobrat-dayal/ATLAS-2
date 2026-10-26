"""Pydantic V2 Schemas for Institutional Economics V1 (Stage 89).

Data transfer objects for FastAPI HTTP responses and request validation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

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


class EconomicGeographyDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    name: str
    iso_code: str
    scope_kind: GeographicScopeKind
    currency_code: str
    flag_emoji_code: str
    is_core: bool
    notes: Optional[str] = None


class EconomicIndicatorDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    is_headline: bool


class EconomicSeriesDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    is_active: bool
    vintage_supported: bool
    methodology_notes: Optional[str] = None


class EconomicObservationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observation_id: str
    series_id: str
    period: str
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


class EconomicVintageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vintage_id: str
    series_id: str
    period: str
    vintage_date: date
    value: Decimal
    status: ObservationStatus
    published_at: datetime
    notes: str


class TransformationDefinitionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transformation_type: TransformationType
    display_name: str
    formula_description: str
    supported_frequencies: List[ReportingFrequency]
    output_unit_description: str


class MajorEconomyMacroSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class GlobalMacroOverviewResponseDTO(BaseModel):
    major_economies: List[MajorEconomyMacroSummaryDTO]
    indicator_categories: List[str]
    total_indicators: int
    total_series: int
    freshness_statement: str


class EconomicSeriesObservationsResponseDTO(BaseModel):
    series: EconomicSeriesDTO
    transformation: TransformationType
    effective_unit: StatisticalUnit
    observations: List[EconomicObservationDTO]
    total_count: int
    page: int
    limit: int


class EconomicCoverageResponseDTO(BaseModel):
    supported_providers: List[str]
    covered_geographies: List[str]
    covered_categories: List[str]
    vintage_support_enabled: bool
    coverage_statement: str
    limitations: List[str]
