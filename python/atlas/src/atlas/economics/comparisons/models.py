"""Domain Models for Macroeconomic Comparisons & Benchmarking (Stage 93)."""

from dataclasses import dataclass, field
from typing import List, Optional

from .enums import (
    ComparisonMetricKind,
    CompatibilityStatus,
    CorrelationMethod,
    GeographicCohortKind,
    WeightingPolicy,
)


@dataclass
class GeographicCohort:
    """Predefined or custom country comparison group."""
    cohort_id: str
    name: str
    cohort_kind: GeographicCohortKind
    member_geography_ids: List[str]
    description: str


@dataclass
class ComparableIndicatorDefinition:
    """Canonical definition of a cross-country comparable macroeconomic metric."""
    metric_kind: ComparisonMetricKind
    name: str
    category: str
    default_unit: str
    description: str
    higher_is_better: Optional[bool] = None  # None if neutral, True if higher is preferable, False if lower
    methodology_notes: str = ""


@dataclass
class CountryMetricObservation:
    """Verified observation point for a specific sovereign economy and metric."""
    geography_id: str
    country_name: str
    iso_code: str
    metric_kind: ComparisonMetricKind
    reference_period: str  # e.g., "2024", "2024-Q3", "2024-10"
    raw_value: float
    formatted_value: str
    unit: str
    source_agency: str
    source_series_id: str
    vintage_date: Optional[str] = None
    is_preliminary: bool = False
    methodology_qualifications: List[str] = field(default_factory=list)


@dataclass
class ComparisonEligibilityRecord:
    """Evaluation result for whether a country and metric are statistically comparable."""
    geography_id: str
    metric_kind: ComparisonMetricKind
    status: CompatibilityStatus
    is_eligible: bool
    reasons: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)


@dataclass
class MatrixCell:
    """Single cell entry inside a multi-country comparison matrix."""
    geography_id: str
    country_name: str
    iso_code: str
    metric_kind: ComparisonMetricKind
    raw_value: Optional[float]
    formatted_value: str
    unit: str
    reference_period: str
    status: CompatibilityStatus
    source_agency: str
    caveats: List[str] = field(default_factory=list)


@dataclass
class CountryRankingRow:
    """Row in an economic ranking table."""
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


@dataclass
class DistributionSummary:
    """Descriptive statistics for a cohort of sovereign economies."""
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
    excluded_geography_ids: List[str] = field(default_factory=list)


@dataclass
class CohortAggregate:
    """Official or derived regional aggregate for a country group."""
    cohort_id: str
    metric_kind: ComparisonMetricKind
    aggregate_type: str  # e.g., "SUM", "WEIGHTED_AVG", "OFFICIAL_PUBLISHED"
    value: float
    unit: str
    is_official_source: bool
    methodology_version: str
    notes: str = ""


@dataclass
class HistoricalTrendPoint:
    """Time-series observation point for multi-country charts."""
    geography_id: str
    country_name: str
    reference_period: str
    raw_value: float
    indexed_value: Optional[float] = None  # Rebased to 100 on base_period


@dataclass
class DivergencePoint:
    """Pairwise divergence or differential observation over time."""
    reference_period: str
    country_a_value: float
    country_b_value: float
    differential_value: float
    unit: str
    ratio: Optional[float] = None


@dataclass
class CorrelationResult:
    """Pairwise correlation computation between two aligned economic series."""
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
    warnings: List[str] = field(default_factory=list)
