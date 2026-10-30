"""ATLAS Portfolios V1 — Performance Attribution Pydantic V2 Schemas (Stage 113).

Defines serialization contracts for calculation requests, category effects,
security contributions, currency decomposition, multi-period linking, and audit.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from atlas.portfolios.attribution.enums import (
    AttributionCompleteness,
    AttributionDimension,
    AttributionMethod,
    MultiPeriodLinkingMethod,
    ReconciliationStatus,
)


class CalculateAttributionRequest(BaseModel):
    """Request payload for triggering an on-demand performance attribution calculation."""
    model_config = ConfigDict(from_attributes=True)

    portfolio_id: Optional[str] = None
    account_id: Optional[str] = None
    benchmark_id: str = Field(default="BENCHMARK_SPY", description="Canonical benchmark identifier")
    period_start: Optional[datetime] = Field(default=None, description="Start date/time of attribution period")
    period_end: Optional[datetime] = Field(default=None, description="End date/time of attribution period")
    attribution_method: AttributionMethod = Field(
        default=AttributionMethod.BRINSON_FACHLER,
        description="Methodology (BRINSON_FACHLER or BRINSON_HOOD_BEEBOWER)",
    )
    classification_dimension: AttributionDimension = Field(
        default=AttributionDimension.SECTOR,
        description="Classification dimension (SECTOR, INDUSTRY, ASSET_CLASS, GEOGRAPHY, CURRENCY)",
    )
    reporting_currency: Optional[str] = Field(default=None, description="Portfolio base reporting currency")
    linking_method: MultiPeriodLinkingMethod = Field(
        default=MultiPeriodLinkingMethod.CARINO,
        description="Multi-period linking algorithm",
    )


class AttributionCategoryResponse(BaseModel):
    """Category-level attribution effects."""
    model_config = ConfigDict(from_attributes=True)

    category_id: str
    category_label: str
    portfolio_weight: Decimal
    benchmark_weight: Decimal
    portfolio_return: Decimal
    benchmark_return: Decimal
    allocation_effect: Decimal
    selection_effect: Decimal
    interaction_effect: Decimal
    total_effect: Decimal
    sub_industries: Optional[List["AttributionCategoryResponse"]] = None


class SecurityContributionResponse(BaseModel):
    """Instrument-level return contribution."""
    model_config = ConfigDict(from_attributes=True)

    instrument_id: str
    symbol: str
    name: str
    weight: Decimal
    security_return: Decimal
    contribution: Decimal
    sector: Optional[str] = None
    industry: Optional[str] = None
    currency: str = "USD"
    is_sold: bool = False


class CurrencyEffectResponse(BaseModel):
    """Foreign currency translation return decomposition."""
    model_config = ConfigDict(from_attributes=True)

    currency: str
    weight: Decimal
    local_return: Decimal
    fx_return: Decimal
    interaction_return: Decimal
    base_currency_return: Decimal
    contribution_to_base: Decimal


class HistoricalPeriodResponse(BaseModel):
    """Discrete single-period attribution summary in a time series."""
    model_config = ConfigDict(from_attributes=True)

    period_label: str
    period_start: datetime
    period_end: datetime
    portfolio_return: Decimal
    benchmark_return: Decimal
    active_return: Decimal
    allocation_effect: Decimal
    selection_effect: Decimal
    interaction_effect: Decimal
    total_attributed: Decimal
    residual: Decimal
    category_effects: Dict[str, Decimal] = Field(default_factory=dict)


class MultiPeriodLinkedResponse(BaseModel):
    """Cumulative multi-period linked attribution results."""
    model_config = ConfigDict(from_attributes=True)

    linking_method: MultiPeriodLinkingMethod
    cumulative_portfolio_return: Decimal
    cumulative_benchmark_return: Decimal
    cumulative_active_return: Decimal
    total_allocation_effect: Decimal
    total_selection_effect: Decimal
    total_interaction_effect: Decimal
    total_attributed: Decimal
    reconciliation_residual: Decimal
    category_results: List[AttributionCategoryResponse]
    periods: List[HistoricalPeriodResponse]


class AttributionReconciliationResponse(BaseModel):
    """Mathematical audit check results and residual verification."""
    model_config = ConfigDict(from_attributes=True)

    portfolio_return: Decimal
    reconstructed_portfolio_return: Decimal
    portfolio_return_reconciled: bool
    benchmark_return: Decimal
    reconstructed_benchmark_return: Decimal
    benchmark_return_reconciled: bool
    active_return: Decimal
    total_attributed: Decimal
    attribution_reconciled: bool
    residual: Decimal
    security_contributions_sum: Decimal
    security_contributions_reconciled: bool
    status: ReconciliationStatus
    tolerance: Decimal


class AttributionDataQualityResponse(BaseModel):
    """Data completeness, taxonomy coverage, and cryptographic hash."""
    model_config = ConfigDict(from_attributes=True)

    completeness: AttributionCompleteness
    portfolio_holdings_coverage_ratio: Decimal
    benchmark_constituent_coverage_ratio: Decimal
    taxonomy_coverage_ratio: Decimal
    missing_securities_count: int
    unmapped_sector_weight: Decimal
    input_hash: str
    warnings: List[str]


class PortfolioAttributionRunResponse(BaseModel):
    """Comprehensive performance attribution run representation."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    portfolio_id: str
    account_id: Optional[str] = None
    benchmark_id: str
    benchmark_name: str
    period_start: datetime
    period_end: datetime
    reporting_currency: str
    attribution_method: AttributionMethod
    methodology_version: str
    classification_dimension: AttributionDimension
    taxonomy_id: str
    taxonomy_version: str
    portfolio_return: Decimal
    benchmark_return: Decimal
    active_return: Decimal
    total_allocation_effect: Decimal
    total_selection_effect: Decimal
    total_interaction_effect: Decimal
    total_attributed: Decimal
    reconciliation_residual: Decimal
    category_results: List[AttributionCategoryResponse]
    security_contributions: List[SecurityContributionResponse]
    top_contributors: List[SecurityContributionResponse]
    top_detractors: List[SecurityContributionResponse]
    currency_effects: List[CurrencyEffectResponse]
    reconciliation: AttributionReconciliationResponse
    data_quality: AttributionDataQualityResponse
    multi_period: Optional[MultiPeriodLinkedResponse] = None
    created_at: datetime
    completed_at: datetime


class AttributionBenchmarkSummaryResponse(BaseModel):
    """Available benchmark summary for selection."""
    model_config = ConfigDict(from_attributes=True)

    benchmark_id: str
    name: str
    symbol: str
    benchmark_type: str
    return_basis: str
    currency: str
    description: str
    has_constituent_data: bool = True


class AttributionRunsListResponse(BaseModel):
    """List of historical attribution runs."""
    model_config = ConfigDict(from_attributes=True)

    items: List[PortfolioAttributionRunResponse]
    total: int

