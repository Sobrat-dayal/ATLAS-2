"""Pydantic V2 Schemas and DTOs for Macroeconomic Comparisons (Stage 93)."""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import (
    ComparisonMetricKind,
    CompatibilityStatus,
    CorrelationMethod,
    GeographicCohortKind,
    PeriodAlignmentPolicy,
    RankingDirection,
    TieBreakerPolicy,
    VintagePolicy,
    WeightingPolicy,
)


class ComparableIndicatorDTO(BaseModel):
    """Macroeconomic comparison metric metadata."""
    model_config = ConfigDict(from_attributes=True)

    metric_kind: ComparisonMetricKind
    name: str
    category: str
    default_unit: str
    description: str
    higher_is_better: Optional[bool] = None
    methodology_notes: str = ""


class GeographicCohortDTO(BaseModel):
    """Geopolitical / economic group metadata."""
    model_config = ConfigDict(from_attributes=True)

    cohort_id: str
    name: str
    cohort_kind: GeographicCohortKind
    member_geography_ids: List[str]
    description: str


class CountryMetricObservationDTO(BaseModel):
    """Country observation DTO."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    country_name: str
    iso_code: str
    metric_kind: ComparisonMetricKind
    reference_period: str
    raw_value: float
    formatted_value: str
    unit: str
    source_agency: str
    source_series_id: str
    vintage_date: Optional[str] = None
    is_preliminary: bool = False
    methodology_qualifications: List[str] = Field(default_factory=list)


class ComparisonEligibilityRecordDTO(BaseModel):
    """Comparability evaluation DTO."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    metric_kind: ComparisonMetricKind
    status: CompatibilityStatus
    is_eligible: bool
    reasons: List[str] = Field(default_factory=list)
    caveats: List[str] = Field(default_factory=list)


class MatrixCellDTO(BaseModel):
    """Cell in cross-country comparison matrix."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    country_name: str
    iso_code: str
    metric_kind: ComparisonMetricKind
    raw_value: Optional[float] = None
    formatted_value: str
    unit: str
    reference_period: str
    status: CompatibilityStatus
    source_agency: str
    caveats: List[str] = Field(default_factory=list)


class ComparisonMatrixRequestDTO(BaseModel):
    """Request payload for multi-country comparison matrix."""
    geography_ids: List[str] = Field(default_factory=list)
    metric_kinds: List[ComparisonMetricKind] = Field(default_factory=list)
    period_policy: PeriodAlignmentPolicy = PeriodAlignmentPolicy.LATEST_PER_COUNTRY
    target_period: Optional[str] = None
    vintage_policy: VintagePolicy = VintagePolicy.LATEST_REVISED


class ComparisonMatrixResponseDTO(BaseModel):
    """Response payload for multi-country comparison matrix."""
    model_config = ConfigDict(from_attributes=True)

    geography_ids: List[str]
    metric_kinds: List[ComparisonMetricKind]
    period_policy: PeriodAlignmentPolicy
    cells: List[MatrixCellDTO]
    eligibility: List[ComparisonEligibilityRecordDTO]
    total_countries: int
    generated_at: str


class CountryRankingRowDTO(BaseModel):
    """Row in economic ranking table."""
    model_config = ConfigDict(from_attributes=True)

    rank: int
    geography_id: str
    country_name: str
    iso_code: str
    metric_kind: ComparisonMetricKind
    raw_value: float
    formatted_value: str
    unit: str
    reference_period: str
    is_tied: bool = False


class EconomicRankingsRequestDTO(BaseModel):
    """Request payload for ranking countries by metric."""
    metric_kind: ComparisonMetricKind
    geography_ids: Optional[List[str]] = None
    cohort_id: Optional[str] = None
    direction: RankingDirection = RankingDirection.DESCENDING
    tie_policy: TieBreakerPolicy = TieBreakerPolicy.STANDARD_COMPETITION
    period: Optional[str] = None


class EconomicRankingsResponseDTO(BaseModel):
    """Response payload for country rankings."""
    model_config = ConfigDict(from_attributes=True)

    metric_kind: ComparisonMetricKind
    direction: RankingDirection
    reference_period: str
    total_eligible: int
    total_excluded: int
    rankings: List[CountryRankingRowDTO]
    notes: List[str] = Field(default_factory=list)


class DistributionSummaryDTO(BaseModel):
    """Descriptive statistics summary DTO."""
    model_config = ConfigDict(from_attributes=True)

    metric_kind: ComparisonMetricKind
    reference_period: str
    sample_size: int
    total_eligible_geographies: int
    mean: float
    median: float
    minimum: float
    maximum: float
    q1: float
    q3: float
    standard_deviation: float
    weighting_policy: WeightingPolicy
    unit: str
    excluded_geography_ids: List[str] = Field(default_factory=list)


class DistributionStatisticsRequestDTO(BaseModel):
    """Request payload for calculating distribution stats."""
    metric_kind: ComparisonMetricKind
    geography_ids: Optional[List[str]] = None
    cohort_id: Optional[str] = None
    weighting_policy: WeightingPolicy = WeightingPolicy.EQUAL_WEIGHT
    period: Optional[str] = None


class HistoricalTrendPointDTO(BaseModel):
    """Time-series observation point for charts."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    country_name: str
    reference_period: str
    raw_value: float
    indexed_value: Optional[float] = None


class HistoricalTrendsRequestDTO(BaseModel):
    """Request payload for multi-country historical time series."""
    metric_kind: ComparisonMetricKind
    geography_ids: List[str]
    start_period: Optional[str] = None
    end_period: Optional[str] = None
    base_period: Optional[str] = None  # If provided, index to 100 on base_period


class HistoricalTrendsResponseDTO(BaseModel):
    """Response payload for multi-country historical trends."""
    model_config = ConfigDict(from_attributes=True)

    metric_kind: ComparisonMetricKind
    geography_ids: List[str]
    base_period: Optional[str] = None
    points: List[HistoricalTrendPointDTO]
    common_periods: List[str]


class DivergencePointDTO(BaseModel):
    """Pairwise divergence observation DTO."""
    model_config = ConfigDict(from_attributes=True)

    reference_period: str
    country_a_value: float
    country_b_value: float
    differential_value: float
    unit: str
    ratio: Optional[float] = None


class DivergenceAnalysisRequestDTO(BaseModel):
    """Request payload for pairwise convergence / divergence analysis."""
    metric_kind: ComparisonMetricKind
    geography_a_id: str
    geography_b_id: str
    start_period: Optional[str] = None
    end_period: Optional[str] = None


class DivergenceAnalysisResponseDTO(BaseModel):
    """Response payload for divergence analysis."""
    model_config = ConfigDict(from_attributes=True)

    metric_kind: ComparisonMetricKind
    geography_a_id: str
    country_a_name: str
    geography_b_id: str
    country_b_name: str
    points: List[DivergencePointDTO]
    latest_differential: float
    unit: str


class CorrelationResultDTO(BaseModel):
    """Correlation calculation DTO."""
    model_config = ConfigDict(from_attributes=True)

    metric_a: ComparisonMetricKind
    geography_a_id: str
    country_a_name: str
    metric_b: ComparisonMetricKind
    geography_b_id: str
    country_b_name: str
    method: CorrelationMethod
    sample_size: int
    coefficient: float
    is_valid: bool
    warnings: List[str] = Field(default_factory=list)


class CorrelationAnalysisRequestDTO(BaseModel):
    """Request payload for correlation analysis."""
    series_pairs: List[Dict[str, str]]  # list of {"geo_a": "geo-us", "metric_a": "...", "geo_b": "geo-ea", "metric_b": "..."}
    method: CorrelationMethod = CorrelationMethod.PEARSON


class CorrelationAnalysisResponseDTO(BaseModel):
    """Response payload for correlation analysis."""
    model_config = ConfigDict(from_attributes=True)

    results: List[CorrelationResultDTO]


class MacroCoverageSummaryDTO(BaseModel):
    """Coverage matrix across sovereign economies and indicators."""
    model_config = ConfigDict(from_attributes=True)

    supported_geographies: List[str]
    supported_metrics: List[str]
    cohorts: List[str]
    total_observations_count: int
    harmonized_sources: List[str]
    methodology_qualifications: List[str]
