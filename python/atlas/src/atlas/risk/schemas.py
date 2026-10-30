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
    ExpectedShortfallMethod,
    KupiecTestStatus,
    ReturnBasis,
    RiskCalculationStatus,
    RiskMetricCode,
    RiskMetricStatus,
    RiskModelType,
    RiskReturnFrequency,
    RiskSubjectType,
    ScenarioShockType,
    ScenarioType,
    ShockTargetType,
    VaRModelType,
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


# ============================================================================
# STAGE 116: VALUE AT RISK, EXPECTED SHORTFALL, SCENARIOS & DIAGNOSTICS DTOs
# ============================================================================

class VaRResultDTO(BaseModel):
    """Value at Risk result contract."""
    model_type: VaRModelType
    confidence_level: float
    horizon_days: int
    var_return: float
    var_amount: float
    effective_tail_sample_size: int
    total_sample_size: int
    method_notes: Optional[str] = None


class ExpectedShortfallResultDTO(BaseModel):
    """Expected Shortfall / CVaR result contract."""
    method: ExpectedShortfallMethod
    confidence_level: float
    horizon_days: int
    es_return: float
    es_amount: float
    var_return: float
    effective_tail_sample_size: int
    total_sample_size: int
    tail_weighting_scheme: str


class LossDistributionBinDTO(BaseModel):
    """Single histogram bin for loss distribution."""
    bin_start: float
    bin_end: float
    frequency: int
    relative_frequency: float


class LossDistributionDTO(BaseModel):
    """Empirical or simulated loss distribution metrics and histogram."""
    total_observations: int
    min_loss: float
    max_loss: float
    mean_loss: float
    quantiles: Dict[str, float]
    bins: List[LossDistributionBinDTO]
    tail_losses: List[float]


class CalculateTailRiskRequest(BaseModel):
    """Request payload for on-demand VaR and Expected Shortfall calculation."""
    portfolio_id: Optional[str] = None
    account_id: Optional[str] = None
    model_type: VaRModelType = VaRModelType.HISTORICAL_SIMULATION
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1.0)
    horizon_days: int = Field(default=1, ge=1, le=252)
    es_method: Optional[ExpectedShortfallMethod] = None
    mc_simulations: int = Field(default=2500, ge=100, le=10000)
    mc_seed: Optional[int] = 42
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    reporting_currency: Optional[str] = None


class TailRiskCalculationRunDTO(BaseModel):
    """Complete record of a tail-loss risk calculation run."""
    run_id: str
    portfolio_id: str
    account_id: Optional[str] = None
    as_of: str
    reporting_currency: str
    baseline_nav: float
    model_type: VaRModelType
    confidence_level: float
    horizon_days: int
    var: VaRResultDTO
    expected_shortfall: ExpectedShortfallResultDTO
    loss_distribution: Optional[LossDistributionDTO] = None
    status: RiskCalculationStatus
    input_hash: str
    warnings: List[str] = Field(default_factory=list)
    created_at: str


class ScenarioShockDTO(BaseModel):
    """Specification of an individual shock parameter within a scenario."""
    shock_type: ScenarioShockType
    target_type: ShockTargetType
    target_id: Optional[str] = None
    shock_percentage: float = Field(..., ge=-1.0, le=10.0, description="-1.0 (-100%) to +10.0 (+1000%)")
    currency_pair: Optional[str] = None
    description: Optional[str] = None


class CreateScenarioRequest(BaseModel):
    """Payload to create a new user-defined risk scenario."""
    name: str = Field(..., min_length=2, max_length=100)
    scenario_type: ScenarioType = ScenarioType.HYPOTHETICAL_USER_DEFINED
    description: Optional[str] = None
    shocks: List[ScenarioShockDTO] = Field(..., min_length=1)
    is_public: bool = False


class RiskScenarioDTO(BaseModel):
    """Scenario definition in library."""
    scenario_id: str
    name: str
    scenario_type: ScenarioType
    description: Optional[str] = None
    shocks: List[ScenarioShockDTO]
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    is_system_predefined: bool = False
    created_at: str
    updated_at: str


class ScenarioPositionResultDTO(BaseModel):
    """Position-level impact of a risk scenario."""
    instrument_id: str
    symbol: str
    security_name: str
    sector: Optional[str] = None
    currency: str
    baseline_weight: float
    baseline_market_value: float
    applied_price_shock_pct: float
    applied_fx_shock_pct: float
    compounded_return_pct: float
    shocked_market_value: float
    position_pnl: float
    contribution_to_portfolio_pnl_pct: float
    shock_source_rule: str


class ExecuteScenarioRequest(BaseModel):
    """Request payload to execute a scenario on a portfolio."""
    account_id: Optional[str] = None
    as_of: Optional[datetime] = None


class RiskScenarioRunDTO(BaseModel):
    """Complete execution record of a scenario against a portfolio."""
    run_id: str
    portfolio_id: str
    account_id: Optional[str] = None
    scenario_id: str
    scenario_name: str
    scenario_type: ScenarioType
    as_of: str
    reporting_currency: str
    baseline_nav: float
    shocked_nav: float
    portfolio_pnl: float
    portfolio_scenario_return_pct: float
    position_results: List[ScenarioPositionResultDTO]
    reconciliation_residual: float
    is_reconciled: bool
    warnings: List[str] = Field(default_factory=list)
    created_at: str


class ScenarioComparisonRequest(BaseModel):
    """Request payload to compare multiple scenarios for a portfolio."""
    portfolio_id: str
    scenario_ids: List[str] = Field(..., min_length=1)
    account_id: Optional[str] = None


class ScenarioComparisonItemDTO(BaseModel):
    """Single scenario summary in a multi-scenario comparison."""
    scenario_id: str
    scenario_name: str
    scenario_type: ScenarioType
    baseline_nav: float
    shocked_nav: float
    portfolio_pnl: float
    portfolio_scenario_return_pct: float
    run_id: str


class ScenarioComparisonResponseDTO(BaseModel):
    """Comparative impact analysis across multiple scenarios."""
    portfolio_id: str
    reporting_currency: str
    baseline_nav: float
    items: List[ScenarioComparisonItemDTO]


class VaRExceptionObservationDTO(BaseModel):
    """Single historical observation in a VaR exception backtest."""
    date: str
    realized_portfolio_return: float
    realized_portfolio_loss: float
    var_forecast_return: float
    is_exception: bool
    exceedance_amount: float


class KupiecTestResultDTO(BaseModel):
    """Kupiec POF likelihood ratio test result."""
    total_observations: int
    exception_count: int
    expected_exception_count: float
    observed_exception_rate: float
    expected_exception_rate: float
    likelihood_ratio_stat: float
    critical_value_95: float
    p_value: float
    status: KupiecTestStatus
    sample_adequate: bool
    decision_text: str


class RunVaRBacktestRequest(BaseModel):
    """Request payload to perform a VaR exception backtest."""
    portfolio_id: str
    account_id: Optional[str] = None
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1.0)
    horizon_days: int = Field(default=1, ge=1, le=252)
    model_type: VaRModelType = VaRModelType.HISTORICAL_SIMULATION
    window_size: int = Field(default=252, ge=30, le=1000)


class VaRBacktestRunDTO(BaseModel):
    """Complete record of a VaR backtest run with Kupiec diagnostic test."""
    backtest_id: str
    portfolio_id: str
    confidence_level: float
    horizon_days: int
    model_type: VaRModelType
    start_date: str
    end_date: str
    observations: List[VaRExceptionObservationDTO]
    kupiec_test: KupiecTestResultDTO
    created_at: str


