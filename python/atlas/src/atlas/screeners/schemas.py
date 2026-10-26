"""Pydantic schemas and DTOs for Financial Screeners V1 (Stage 94)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from atlas.screeners.enums import (
    FilterOperator,
    PeriodPolicy,
    SortDirection,
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



class SortCriterionDTO(BaseModel):
    """Ordering specification."""

    model_config = ConfigDict(extra="ignore")

    field_id: str
    direction: SortDirection = SortDirection.DESC


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
