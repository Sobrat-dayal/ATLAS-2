"""Pydantic schemas and DTOs for Financial Screeners V1 (Stage 94)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from atlas.screeners.enums import (
    ExportFormat,
    ExportJobStatus,
    ExportScope,
    FilterOperator,
    NLAmbiguityCategory,
    NLRequirementStatus,
    NLTranslationMode,
    NLTranslationStatus,
    PeriodPolicy,
    RankingDirection,
    RankingMethod,
    RankingMode,
    RankingTransformation,
    SavedScreenerStatus,
    SortDirection,
    SortNullOrder,
)


class FilterCriterionDTO(BaseModel):
    """Specification of a single filter predicate condition."""

    model_config = ConfigDict(extra="ignore")

    condition_id: Optional[str] = None
    filter_id: str
    operator: FilterOperator = FilterOperator.GTE
    value: Any
    secondary_value: Optional[Any] = None
    currency: Optional[str] = None
    unit: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    period_policy: Optional[str] = None


class SortCriterionDTO(BaseModel):
    """Ordering specification with typed null handling."""

    model_config = ConfigDict(extra="ignore")

    field_id: str
    direction: SortDirection = SortDirection.DESC
    null_order: SortNullOrder = SortNullOrder.NULLS_LAST


# Typed alias for multi-sort keys
ScreenerSortKeyDTO = SortCriterionDTO


class RankingFactorWeightDTO(BaseModel):
    """Individual factor configuration within a ranking specification."""

    model_config = ConfigDict(extra="ignore")

    factor_id: str
    direction: RankingDirection = RankingDirection.HIGHER_VALUE_FIRST
    transformation: RankingTransformation = RankingTransformation.PERCENTILE
    weight: float = 1.0


class ScreenerRankingSpecDTO(BaseModel):
    """Comprehensive quantitative factor ranking specification (Stage 97)."""

    model_config = ConfigDict(extra="ignore")

    mode: RankingMode = RankingMode.SINGLE_FACTOR
    cohort_policy: str = "filter_matched_securities"
    factors: List[RankingFactorWeightDTO] = Field(default_factory=list)
    method: RankingMethod = RankingMethod.DENSE_RANK
    missing_value_policy: str = "complete_case"
    minimum_coverage: float = 1.0
    methodology_version: str = "1.0.0"


class UniverseSelectionDTO(BaseModel):
    """Screener universe scoping criteria."""

    model_config = ConfigDict(extra="ignore")

    universe_id: str = "common_equity"
    security_types: Optional[List[str]] = None
    listing_statuses: Optional[List[str]] = None
    exchange_mics: Optional[List[str]] = None
    issuer_country_codes: Optional[List[str]] = None
    listing_country_codes: Optional[List[str]] = None
    sectors: Optional[List[str]] = None
    industries: Optional[List[str]] = None


class ScreenerRunRequestDTO(BaseModel):
    """Request payload for screening query execution."""

    model_config = ConfigDict(extra="ignore")

    universe: UniverseSelectionDTO = Field(default_factory=UniverseSelectionDTO)
    filters: List[FilterCriterionDTO] = Field(default_factory=list)
    sort: List[SortCriterionDTO] = Field(default_factory=list)
    multi_sort: Optional[List[SortCriterionDTO]] = None
    ranking: Optional[ScreenerRankingSpecDTO] = None
    columns: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)
    cursor: Optional[str] = None
    period_policy: PeriodPolicy = PeriodPolicy.LATEST_ANNUAL
    currency_policy: str = "USD"


class ScreenerMetricCellDTO(BaseModel):
    """Enriched value and provenance metadata for a single table cell."""

    model_config = ConfigDict(extra="ignore")

    metric_id: str
    raw_value: Optional[Any] = None
    display_value: str = "—"
    unit: Optional[str] = None
    currency: Optional[str] = None
    status: str = "AVAILABLE"  # AVAILABLE, MISSING, NOT_MEANINGFUL, RESTRICTED
    observation_period: Optional[str] = None
    freshness: Optional[str] = None
    as_of: Optional[str] = None
    provider: Optional[str] = None


class ScreenerResultRowDTO(BaseModel):
    """A single canonical security result row in screener output."""

    model_config = ConfigDict(extra="ignore")

    instrument_entity_id: UUID
    listing_id: UUID
    issuer_company_entity_id: UUID
    canonical_security_name: str
    ticker: str
    exchange_mic: str
    exchange_name: str
    listing_country_code: str
    issuer_country_code: str
    security_type: str
    share_class_name: Optional[str] = None
    listing_status: str
    currency: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    metrics: Dict[str, ScreenerMetricCellDTO] = Field(default_factory=dict)
    rank: Optional[int] = None
    composite_score: Optional[float] = None
    percentile: Optional[float] = None
    z_score: Optional[float] = None


class ScreenerRunResponseDTO(BaseModel):
    """Complete response payload for a screener run."""

    model_config = ConfigDict(extra="ignore")

    query_id: str
    universe_id: str
    evaluated_as_of: datetime
    total_matching_count: int
    count_exactness: str = "EXACT"
    page: int
    page_size: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool
    next_cursor: Optional[str] = None
    rows: List[ScreenerResultRowDTO]
    applied_filters_count: int
    source_coverage: Dict[str, int]
    execution_duration_ms: float
    warnings: List[str] = Field(default_factory=list)
    ranking_evaluation_id: Optional[UUID] = None
    ranking_summary: Optional[Dict[str, Any]] = None


class ScreenerRankingResultRowDTO(BaseModel):
    """Result row for dedicated factor ranking evaluation."""

    model_config = ConfigDict(extra="ignore")

    instrument_entity_id: UUID
    ticker: str
    canonical_security_name: str
    rank: int
    percentile: Optional[float] = None
    z_score: Optional[float] = None
    composite_score: Optional[float] = None
    factor_contributions: Dict[str, float] = Field(default_factory=dict)
    raw_factor_values: Dict[str, Optional[float]] = Field(default_factory=dict)


class ScreenerRankingResponseDTO(BaseModel):
    """Response payload for quantitative factor ranking evaluation."""

    model_config = ConfigDict(extra="ignore")

    ranking_evaluation_id: UUID
    mode: RankingMode
    method: RankingMethod
    cohort_policy: str
    methodology_version: str
    total_candidate_count: int
    eligible_count: int
    excluded_count: int
    evaluated_as_of: datetime
    results: List[ScreenerRankingResultRowDTO]


class SavedScreenerDTO(BaseModel):
    """Institutional persistent user-owned saved screener (Stage 97)."""

    model_config = ConfigDict(extra="ignore")

    saved_screen_id: UUID
    owner_user_id: UUID
    name: str
    description: Optional[str] = None
    query_schema_version: str = "1.0.0"
    universe: UniverseSelectionDTO = Field(default_factory=UniverseSelectionDTO)
    filters: List[FilterCriterionDTO] = Field(default_factory=list)
    columns: List[str] = Field(default_factory=list)
    sort: List[SortCriterionDTO] = Field(default_factory=list)
    ranking: Optional[ScreenerRankingSpecDTO] = None
    period_policy: PeriodPolicy = PeriodPolicy.LATEST_ANNUAL
    currency_policy: str = "USD"
    revision: int = 1
    status: SavedScreenerStatus = SavedScreenerStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    last_executed_at: Optional[datetime] = None


class SavedScreenerCreateRequestDTO(BaseModel):
    """Payload to create a new user-owned saved screener."""

    model_config = ConfigDict(extra="ignore")

    name: str
    description: Optional[str] = None
    universe: UniverseSelectionDTO = Field(default_factory=UniverseSelectionDTO)
    filters: List[FilterCriterionDTO] = Field(default_factory=list)
    columns: Optional[List[str]] = None
    sort: List[SortCriterionDTO] = Field(default_factory=list)
    ranking: Optional[ScreenerRankingSpecDTO] = None
    period_policy: PeriodPolicy = PeriodPolicy.LATEST_ANNUAL
    currency_policy: str = "USD"
    idempotency_key: Optional[str] = None


class SavedScreenerUpdateRequestDTO(BaseModel):
    """Payload to update an existing saved screener with revision check."""

    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = None
    description: Optional[str] = None
    universe: Optional[UniverseSelectionDTO] = None
    filters: Optional[List[FilterCriterionDTO]] = None
    columns: Optional[List[str]] = None
    sort: Optional[List[SortCriterionDTO]] = None
    ranking: Optional[ScreenerRankingSpecDTO] = None
    period_policy: Optional[PeriodPolicy] = None
    currency_policy: Optional[str] = None
    expected_revision: int


class SavedScreenerListResponseDTO(BaseModel):
    """Paginated list of user-owned saved screeners."""

    model_config = ConfigDict(extra="ignore")

    total: int
    page: int
    page_size: int
    items: List[SavedScreenerDTO]


class ScreenerExportRequestDTO(BaseModel):
    """Request payload to generate an authorized financial export."""

    model_config = ConfigDict(extra="ignore")

    query: ScreenerRunRequestDTO
    saved_screen_id: Optional[UUID] = None
    format: ExportFormat = ExportFormat.CSV
    scope: ExportScope = ExportScope.CURRENT_PAGE
    selected_columns: Optional[List[str]] = None
    include_metadata: bool = True
    idempotency_key: Optional[str] = None


class ScreenerExportJobDTO(BaseModel):
    """Lifecycle metadata and status of an export job."""

    model_config = ConfigDict(extra="ignore")

    export_job_id: UUID
    owner_user_id: UUID
    status: ExportJobStatus
    format: ExportFormat
    scope: ExportScope
    row_count: int = 0
    file_size_bytes: Optional[int] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class ScreenerExportListResponseDTO(BaseModel):
    """List of export jobs for the current user."""

    model_config = ConfigDict(extra="ignore")

    total: int
    items: List[ScreenerExportJobDTO]


class ConditionValidationIssueDTO(BaseModel):
    """Attributed validation issue for visual filter condition."""

    model_config = ConfigDict(extra="ignore")

    condition_id: Optional[str] = None
    filter_id: Optional[str] = None
    field_path: Optional[str] = None
    code: str
    severity: str = "error"  # error | warning
    message: str


class ValidationResponseDTO(BaseModel):
    """Result of validating a candidate screener query."""

    model_config = ConfigDict(extra="ignore")

    valid: bool
    accepted_filters: List[FilterCriterionDTO] = Field(default_factory=list)
    rejected_filters: List[Dict[str, Any]] = Field(default_factory=list)
    issues: List[ConditionValidationIssueDTO] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    contradictions_detected: bool = False
    eligible_universe_size: int = 0


class ExchangeOptionDTO(BaseModel):
    """Exchange option with security listing count."""

    model_config = ConfigDict(extra="ignore")

    mic: str
    name: str
    country_code: str
    count: int


class CountryOptionDTO(BaseModel):
    """Country option with security listing count."""

    model_config = ConfigDict(extra="ignore")

    code: str
    name: str
    count: int


class SectorOptionDTO(BaseModel):
    """Sector option with nested industries and count."""

    model_config = ConfigDict(extra="ignore")

    name: str
    count: int
    industries: List[str] = Field(default_factory=list)


class ScreenerCoverageResponseDTO(BaseModel):
    """Institutional data coverage audit for screeners."""

    model_config = ConfigDict(extra="ignore")

    total_instruments: int
    active_listings: int
    exchanges_count: int
    countries_count: int
    sectors_count: int
    instruments_with_quotes: int
    instruments_with_market_cap: int
    instruments_with_fundamentals: int
    instruments_with_ratios: int
    providers_represented: List[str]
    data_freshness_breakdown: Dict[str, int]


# =============================================================================
# Stage 98: Natural-Language Screener Translation DTOs
# =============================================================================


class NLRequirementResolutionDTO(BaseModel):
    """Tracking coverage and interpretation of an individual user requirement."""

    model_config = ConfigDict(extra="ignore")

    requirement_id: str
    source_text: str
    interpreted_concept: Optional[str] = None
    resolved_filter_id: Optional[str] = None
    status: NLRequirementStatus = NLRequirementStatus.RESOLVED
    explanation: str = ""
    alternatives: Optional[List[str]] = None


class NLAmbiguityQuestionDTO(BaseModel):
    """Targeted clarification question to resolve semantic ambiguity."""

    model_config = ConfigDict(extra="ignore")

    ambiguity_id: str
    category: NLAmbiguityCategory
    question: str
    source_phrase: str
    options: List[Dict[str, Any]] = Field(default_factory=list)


class NLTranslateRequestDTO(BaseModel):
    """Inbound request to translate natural-language screening instructions."""

    model_config = ConfigDict(extra="ignore")

    text: str = Field(..., max_length=1000)
    universe_context: Optional[str] = None
    current_filters: Optional[List[FilterCriterionDTO]] = None
    currency_policy: Optional[str] = "USD"
    period_policy: Optional[PeriodPolicy] = PeriodPolicy.LATEST_ANNUAL
    locale: Optional[str] = "en-US"
    mode: NLTranslationMode = NLTranslationMode.CREATE_NEW_QUERY
    request_id: Optional[str] = None


class NLClarifyRequestDTO(BaseModel):
    """User response to resolve an ambiguity in a translation proposal."""

    model_config = ConfigDict(extra="ignore")

    proposal_id: str
    original_text: str
    ambiguity_id: str
    selected_option_id: str
    additional_text: Optional[str] = None
    current_universe: Optional[UniverseSelectionDTO] = None
    current_filters: Optional[List[FilterCriterionDTO]] = None


class NLQueryModificationDiffDTO(BaseModel):
    """Structured diff when modifying an existing screener draft."""

    model_config = ConfigDict(extra="ignore")

    added_conditions: List[FilterCriterionDTO] = Field(default_factory=list)
    updated_conditions: List[FilterCriterionDTO] = Field(default_factory=list)
    removed_conditions: List[str] = Field(default_factory=list)


class NLTranslationProposalDTO(BaseModel):
    """Complete structured translation proposal ready for review and execution."""

    model_config = ConfigDict(extra="ignore")

    proposal_id: str
    status: NLTranslationStatus
    original_text: str
    universe: UniverseSelectionDTO = Field(default_factory=UniverseSelectionDTO)
    filters: List[FilterCriterionDTO] = Field(default_factory=list)
    sort: List[SortCriterionDTO] = Field(default_factory=list)
    result_limit: Optional[int] = None
    requirements: List[NLRequirementResolutionDTO] = Field(default_factory=list)
    ambiguities: List[NLAmbiguityQuestionDTO] = Field(default_factory=list)
    unsupported: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    modification_diff: Optional[NLQueryModificationDiffDTO] = None
    ready_for_review: bool = True
    translator_version: str = "1.0.0"
    registry_revision: str = "stage_98_v1"
    coverage_count: str = ""


class NLCapabilitiesResponseDTO(BaseModel):
    """Registry of supported natural language translation capabilities and examples."""

    model_config = ConfigDict(extra="ignore")

    supported_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    supported_operators: List[str] = Field(default_factory=list)
    supported_currencies: List[str] = Field(default_factory=list)
    supported_units: List[str] = Field(default_factory=list)
    supported_indicators: List[Dict[str, Any]] = Field(default_factory=list)
    supported_magnitudes: List[str] = Field(default_factory=list)
    example_queries: List[Dict[str, str]] = Field(default_factory=list)
