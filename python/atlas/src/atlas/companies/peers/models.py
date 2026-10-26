"""Domain Models and Dataclasses for Company Peers and Comparable Company Analysis (Stage 87)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from .enums import (
    ComparisonMetricCategory,
    IndustryTaxonomy,
    MetricObservationStatus,
    PeerRelationshipType,
)


@dataclass
class IndustryClassification:
    """Standardized multi-taxonomy industry classification metadata."""

    taxonomy: IndustryTaxonomy
    sector: str
    industry_group: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    code: Optional[str] = None
    taxonomy_version: str = "2024"


@dataclass
class CompanyPeerCandidate:
    """Discovered candidate comparable company with explainable selection reasons."""

    candidate_company_id: str
    ticker: str
    display_name: str
    relationship_type: PeerRelationshipType
    classification: IndustryClassification
    headquarters_country: str
    market_cap: Optional[Decimal] = None
    formatted_market_cap: Optional[str] = None
    revenue: Optional[Decimal] = None
    formatted_revenue: Optional[str] = None
    relevance_score: float = 0.0  # 0.0 to 1.0 deterministic score
    selection_reasons: List[str] = field(default_factory=list)
    is_competitor: bool = False


@dataclass
class UserCompanyPeerGroup:
    """User-defined saved peer group with private ownership and concurrency control."""

    id: str
    owner_user_id: str
    subject_company_id: str
    name: str
    description: Optional[str] = None
    peer_company_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    revision: int = 1


@dataclass
class ComparableMetricObservation:
    """A qualified financial or market valuation metric observation for a single company."""

    company_id: str
    company_name: str
    ticker: str
    metric_id: str
    metric_name: str
    category: ComparisonMetricCategory
    exact_value: Optional[Decimal]
    formatted_value: str
    unit: str
    currency: Optional[str] = None
    period_id: str = "FY2024"
    period_end: str = "2024-09-28"
    status: MetricObservationStatus = MetricObservationStatus.AVAILABLE
    is_subject: bool = False
    source_filing_ref: Optional[str] = None
    explanation: Optional[str] = None


@dataclass
class PeerBenchmarkStatistics:
    """Cross-sectional benchmark statistics computed over eligible peer observations."""

    metric_id: str
    metric_name: str
    category: ComparisonMetricCategory
    unit: str
    mean: Optional[Decimal] = None
    median: Optional[Decimal] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    sample_count: int = 0
    total_count: int = 0
    coverage_ratio: float = 0.0
    subject_value: Optional[Decimal] = None
    subject_diff_vs_median_pct: Optional[Decimal] = None
    subject_diff_vs_median_pp: Optional[Decimal] = None
    subject_percentile: Optional[Decimal] = None
    outliers_detected: List[str] = field(
        default_factory=list
    )  # Company IDs of statistical outliers


@dataclass
class HistoricalDataPoint:
    """Single point in a historical multi-company time series."""

    period_id: str
    period_end: str
    fiscal_year: int
    fiscal_quarter: Optional[str]
    value: Optional[Decimal]
    formatted_value: str


@dataclass
class HistoricalPeerTrendSeries:
    """Historical multi-period series for a single company and metric."""

    metric_id: str
    metric_name: str
    company_id: str
    company_name: str
    ticker: str
    is_subject: bool
    points: List[HistoricalDataPoint] = field(default_factory=list)
