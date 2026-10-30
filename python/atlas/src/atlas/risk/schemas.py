"""ATLAS Financial Risk Foundation — Pydantic Schemas (Stage 115).

Data transfer objects for risk calculations, requests, rolling volatility,
drawdown analytics, benchmark sensitivity, and covariance diagnostics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from .enums import (
    AnnualizationPolicy,
    DataCoverageStatus,
    DrawdownEpisodeStatus,
    ReturnBasis,
    RiskCalculationStatus,
    RiskMetricCode,
    RiskMetricStatus,
    RiskModelType,
    RiskReturnFrequency,
    RiskSubjectType,
)


class CalculateRiskRequest(BaseModel):
    """Request payload to initiate or recompute risk calculations."""
    subject_type: RiskSubjectType = RiskSubjectType.PORTFOLIO
    subject_id: Optional[str] = None
    account_id: Optional[str] = None
    metric_codes: Optional[List[RiskMetricCode]] = None
    model_id: Optional[str] = "COVARIANCE_BASED_PORTFOLIO_RISK"
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    return_frequency: RiskReturnFrequency = RiskReturnFrequency.DAILY
    annualization_policy: AnnualizationPolicy = AnnualizationPolicy.DAYS_252
    reporting_currency: Optional[str] = None
    benchmark_id: Optional[str] = "BENCHMARK_SPY"
    rolling_window_size: int = Field(default=20, ge=2, le=252)


class RiskMetricDefinitionDTO(BaseModel):
    metric_code: RiskMetricCode
    display_name: str
    category: str
    mathematical_formula: str
    default_frequency: RiskReturnFrequency
    annualization_policy: AnnualizationPolicy
    supported_subject_types: List[RiskSubjectType]
    units: str
    methodology_version: str


class RiskModelDefinitionDTO(BaseModel):
    model_id: str
    model_type: RiskModelType
    version: str
    display_name: str
    description: str
    allowed_metrics: List[RiskMetricCode]
    limitations: List[str]


class RollingObservationDTO(BaseModel):
    window_end: str
    metric_value: float
    observation_count: int
    is_complete: bool


class DrawdownEpisodeDTO(BaseModel):
    episode_id: str
    peak_date: str
    peak_value: float
    trough_date: str
    trough_value: float
    max_drawdown: float
    recovery_date: Optional[str] = None
    time_to_trough_days: int
    recovery_duration_days: Optional[int] = None
    status: DrawdownEpisodeStatus


class BenchmarkSensitivityDTO(BaseModel):
    benchmark_id: str
    benchmark_symbol: str
    benchmark_name: str
    beta: Optional[float] = None
    correlation: Optional[float] = None
    tracking_error_annualized: Optional[float] = None
    benchmark_volatility_annualized: Optional[float] = None
    portfolio_volatility_annualized: Optional[float] = None
    covariance: Optional[float] = None
    matched_observations: int
    status: RiskMetricStatus
    warning: Optional[str] = None


class RiskContributionItemDTO(BaseModel):
    symbol: str
    name: str
    category_label: str
    weight: float
    marginal_volatility_contribution: float
    component_volatility_contribution: float
    percentage_volatility_contribution: float
    variance_contribution: float


class CovarianceDiagnosticsDTO(BaseModel):
    model_name: str
    dimensions: int
    is_psd: bool
    condition_number: float
    min_eigenvalue: float
    regularization_applied: bool
    diversification_ratio: float
    correlation_matrix: List[List[float]]
    symbols: List[str]


class RiskDataCoverageDTO(BaseModel):
    required_observations: int
    available_observations: int
    matched_observations: int
    coverage_ratio: float
    missing_intervals: List[str]
    stale_observations: int
    unsupported_instruments: List[str]
    status: DataCoverageStatus


class RiskInputManifestDTO(BaseModel):
    portfolio_valuation_id: Optional[str] = None
    performance_run_id: Optional[str] = None
    benchmark_id: Optional[str] = None
    return_frequency: RiskReturnFrequency
    annualization_policy: AnnualizationPolicy
    reporting_currency: str
    input_hash: str


class RiskCalculationRunDTO(BaseModel):
    risk_run_id: str
    subject_id: str
    subject_type: RiskSubjectType
    model_type: RiskModelType
    model_version: str
    calculation_as_of: str
    observation_start: str
    observation_end: str
    reporting_currency: str
    frequency: RiskReturnFrequency
    annualization_factor: float
    status: RiskCalculationStatus
    historical_volatility: Optional[float] = None
    historical_variance: Optional[float] = None
    rolling_volatility_series: List[RollingObservationDTO] = Field(default_factory=list)
    wealth_index_series: List[Tuple[str, float]] = Field(default_factory=list)
    drawdown_series: List[Tuple[str, float]] = Field(default_factory=list)
    max_drawdown: Optional[float] = None
    current_drawdown: Optional[float] = None
    drawdown_episodes: List[DrawdownEpisodeDTO] = Field(default_factory=list)
    benchmark_sensitivity: Optional[BenchmarkSensitivityDTO] = None
    model_estimated_variance: Optional[float] = None
    model_estimated_volatility: Optional[float] = None
    security_contributions: List[RiskContributionItemDTO] = Field(default_factory=list)
    covariance_diagnostics: Optional[CovarianceDiagnosticsDTO] = None
    data_coverage: RiskDataCoverageDTO
    input_manifest: RiskInputManifestDTO
    warnings: List[str] = Field(default_factory=list)
    created_at: str
    completed_at: Optional[str] = None


class PortfolioRiskSummaryDTO(BaseModel):
    portfolio_id: str
    risk_run_id: str
    as_of: str
    reporting_currency: str
    historical_volatility: Optional[float] = None
    model_volatility: Optional[float] = None
    max_drawdown: Optional[float] = None
    current_drawdown: Optional[float] = None
    beta: Optional[float] = None
    correlation: Optional[float] = None
    tracking_error: Optional[float] = None
    coverage_ratio: float
    status: RiskCalculationStatus
    input_hash: str


class RiskRunsListDTO(BaseModel):
    items: List[RiskCalculationRunDTO]
    total: int


class VolatilityResponseDTO(BaseModel):
    historical_volatility_annualized: Optional[float] = None
    historical_variance: Optional[float] = None
    model_volatility_annualized: Optional[float] = None
    annualization_factor: float
    frequency: RiskReturnFrequency
    rolling_series: List[RollingObservationDTO]
    status: RiskMetricStatus


class DrawdownsResponseDTO(BaseModel):
    max_drawdown: Optional[float] = None
    current_drawdown: Optional[float] = None
    drawdown_series: List[Tuple[str, float]]
    wealth_index_series: List[Tuple[str, float]]
    episodes: List[DrawdownEpisodeDTO]
    status: RiskMetricStatus


class ContributionsResponseDTO(BaseModel):
    model_variance: Optional[float] = None
    model_volatility: Optional[float] = None
    diversification_ratio: Optional[float] = None
    contributions: List[RiskContributionItemDTO]
    covariance_diagnostics: Optional[CovarianceDiagnosticsDTO] = None
    status: RiskMetricStatus

