"""Pydantic Request and Response Schemas for Company Peers API (Stage 87)."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import (
    ComparisonMetricCategory,
    IndustryTaxonomy,
    MetricObservationStatus,
    OutlierPolicy,
    PeerRelationshipType,
    PeriodAlignmentMode,
    SubjectInclusionPolicy,
)


class IndustryClassificationDTO(BaseModel):
    taxonomy: IndustryTaxonomy
    sector: str
    industry_group: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    code: Optional[str] = None
    taxonomy_version: str = "2024"


class CompanyPeerCandidateDTO(BaseModel):
    candidate_company_id: str
    ticker: str
    display_name: str
    relationship_type: PeerRelationshipType
    classification: IndustryClassificationDTO
    headquarters_country: str
    market_cap: Optional[Decimal] = None
    formatted_market_cap: Optional[str] = None
    revenue: Optional[Decimal] = None
    formatted_revenue: Optional[str] = None
    relevance_score: float = 0.0
    selection_reasons: List[str] = Field(default_factory=list)
    is_competitor: bool = False


class CandidatesResponseDTO(BaseModel):
    subject_company_id: str
    total_candidates: int
    items: List[CompanyPeerCandidateDTO]


class UserPeerGroupDTO(BaseModel):
    id: str
    owner_user_id: str
    subject_company_id: str
    name: str
    description: Optional[str] = None
    peer_company_ids: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    revision: int = 1


class CreatePeerGroupRequestDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    peer_company_ids: List[str] = Field(..., min_length=1, max_length=25)


class UpdatePeerGroupRequestDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    peer_company_ids: Optional[List[str]] = Field(None, min_length=1, max_length=25)
    expected_revision: Optional[int] = None


class PeerMetricDefinitionDTO(BaseModel):
    metric_id: str
    name: str
    category: ComparisonMetricCategory
    unit: str
    formula_display: str
    description: str


class MetricCatalogResponseDTO(BaseModel):
    total_metrics: int
    items: List[PeerMetricDefinitionDTO]


class ComparableObservationDTO(BaseModel):
    company_id: str
    company_name: str
    ticker: str
    metric_id: str
    metric_name: str
    category: ComparisonMetricCategory
    exact_value: Optional[Decimal] = None
    formatted_value: str
    unit: str
    currency: Optional[str] = None
    period_id: str
    period_end: str
    status: MetricObservationStatus
    is_subject: bool = False
    source_filing_ref: Optional[str] = None
    explanation: Optional[str] = None


class PeerBenchmarkStatisticsDTO(BaseModel):
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
    outliers_detected: List[str] = Field(default_factory=list)


class PeerCompanySummaryDTO(BaseModel):
    company_id: str
    ticker: str
    display_name: str
    relationship_type: PeerRelationshipType
    sector: str
    industry: str
    country: str
    is_subject: bool = False


class PeerComparisonRequestDTO(BaseModel):
    peer_company_ids: Optional[List[str]] = None
    peer_group_id: Optional[str] = None
    metric_ids: Optional[List[str]] = None
    period_alignment_mode: PeriodAlignmentMode = PeriodAlignmentMode.LATEST_COMMON_FISCAL_YEAR
    fiscal_period: Optional[str] = "FY2024"
    outlier_policy: OutlierPolicy = OutlierPolicy.ALL_VALID_VALUES
    subject_inclusion_policy: SubjectInclusionPolicy = SubjectInclusionPolicy.EXCLUDE_SUBJECT


class PeerComparisonResponseDTO(BaseModel):
    subject_company_id: str
    subject_company_name: str
    period_alignment_mode: PeriodAlignmentMode
    fiscal_period: str
    companies: List[PeerCompanySummaryDTO]
    observations: Dict[
        str, Dict[str, ComparableObservationDTO]
    ]  # metric_id -> company_id -> observation
    statistics: Dict[str, PeerBenchmarkStatisticsDTO]  # metric_id -> stats


class HistoricalDataPointDTO(BaseModel):
    period_id: str
    period_end: str
    fiscal_year: int
    fiscal_quarter: Optional[str] = None
    value: Optional[Decimal] = None
    formatted_value: str


class HistoricalPeerTrendSeriesDTO(BaseModel):
    metric_id: str
    metric_name: str
    company_id: str
    company_name: str
    ticker: str
    is_subject: bool
    points: List[HistoricalDataPointDTO]


class HistoricalComparisonRequestDTO(BaseModel):
    peer_company_ids: Optional[List[str]] = None
    peer_group_id: Optional[str] = None
    metric_ids: List[str]
    max_periods: int = 5


class HistoricalComparisonResponseDTO(BaseModel):
    subject_company_id: str
    series: List[HistoricalPeerTrendSeriesDTO]


class PeersOverviewResponseDTO(BaseModel):
    subject_company_id: str
    subject_company_name: str
    classification: IndustryClassificationDTO
    default_peer_group: Optional[UserPeerGroupDTO] = None
    total_candidates: int
    available_metrics_count: int
    key_highlights: Dict[str, Any] = Field(default_factory=dict)


class PeerMethodologyResponseDTO(BaseModel):
    version: str = "Stage87.v1"
    candidate_discovery: Dict[str, Any]
    period_alignment_rules: Dict[str, str]
    valuation_definitions: Dict[str, str]
    statistical_methodology: Dict[str, str]
