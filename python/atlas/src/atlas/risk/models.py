"""ATLAS Financial Risk Foundation — Domain Models (Stage 115).

Domain dataclasses for institutional risk calculations, rolling volatility series,
drawdown episodes, benchmark sensitivities, and covariance-based risk contributions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .enums import (
    AnnualizationPolicy,
    ConcentrationDimension,
    CurrencyExposureType,
    DataCoverageStatus,
    DrawdownEpisodeStatus,
    ExpectedShortfallMethod,
    FactorFamily,
    FactorReturnBasis,
    KupiecTestStatus,
    ModelDiagnosticStatus,
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


@dataclass
class RiskSubject:
    """Canonical target subject of risk analysis."""
    subject_id: str
    subject_type: RiskSubjectType
    name: str
    base_currency: str
    owner_user_id: str


@dataclass
class RiskMetricDefinition:
    """Specification of a risk metric and its mathematical properties."""
    metric_code: RiskMetricCode
    display_name: str
    category: str
    mathematical_formula: str
    default_frequency: RiskReturnFrequency
    annualization_policy: AnnualizationPolicy
    supported_subject_types: List[RiskSubjectType]
    units: str
    methodology_version: str


@dataclass
class RiskModelDefinition:
    """Specification of an underlying risk calculation model."""
    model_id: str
    model_type: RiskModelType
    version: str
    display_name: str
    description: str
    allowed_metrics: List[RiskMetricCode]
    limitations: List[str]


@dataclass
class RiskReturnSeries:
    """Chronologically aligned return series for risk estimation."""
    subject_id: str
    timestamps: List[datetime]
    returns: List[float]
    reporting_currency: str
    return_basis: ReturnBasis
    sampling_frequency: RiskReturnFrequency
    observation_count: int
    completeness_status: DataCoverageStatus


@dataclass
class RollingRiskObservation:
    """Moving-window risk observation with window boundaries."""
    window_end: datetime
    metric_value: float
    observation_count: int
    is_complete: bool


@dataclass
class DrawdownEpisode:
    """Discrete historical drawdown event from peak to trough and recovery."""
    episode_id: str
    peak_date: datetime
    peak_value: float
    trough_date: datetime
    trough_value: float
    max_drawdown: float
    recovery_date: Optional[datetime]
    time_to_trough_days: int
    recovery_duration_days: Optional[int]
    status: DrawdownEpisodeStatus


@dataclass
class BenchmarkSensitivityResult:
    """Statistical co-movement metrics relative to a market benchmark."""
    benchmark_id: str
    benchmark_symbol: str
    benchmark_name: str
    beta: Optional[float]
    correlation: Optional[float]
    tracking_error_annualized: Optional[float]
    benchmark_volatility_annualized: Optional[float]
    portfolio_volatility_annualized: Optional[float]
    covariance: Optional[float]
    matched_observations: int
    status: RiskMetricStatus
    warning: Optional[str] = None


@dataclass
class ComponentRiskContribution:
    """Euler risk decomposition of portfolio volatility and variance by holding."""
    symbol: str
    name: str
    category_label: str
    weight: float
    marginal_volatility_contribution: float
    component_volatility_contribution: float
    percentage_volatility_contribution: float
    variance_contribution: float


@dataclass
class CovarianceDiagnostics:
    """Numerical health and conditioning metrics of the covariance model."""
    model_name: str
    dimensions: int
    is_psd: bool
    condition_number: float
    min_eigenvalue: float
    regularization_applied: bool
    diversification_ratio: float
    correlation_matrix: List[List[float]]
    symbols: List[str]


@dataclass
class RiskDataCoverage:
    """Data completeness and provenance audit record."""
    required_observations: int
    available_observations: int
    matched_observations: int
    coverage_ratio: float
    missing_intervals: List[str]
    stale_observations: int
    unsupported_instruments: List[str]
    status: DataCoverageStatus


@dataclass
class RiskInputManifest:
    """Cryptographic and ledger provenance watermark for auditability."""
    portfolio_valuation_id: Optional[str]
    performance_run_id: Optional[str]
    benchmark_id: Optional[str]
    return_frequency: RiskReturnFrequency
    annualization_policy: AnnualizationPolicy
    reporting_currency: str
    input_hash: str


@dataclass
class RiskCalculationRun:
    """Executed institutional risk run containing full metrics and diagnostics."""
    risk_run_id: str
    subject_id: str
    subject_type: RiskSubjectType
    model_type: RiskModelType
    model_version: str
    calculation_as_of: datetime
    observation_start: datetime
    observation_end: datetime
    reporting_currency: str
    frequency: RiskReturnFrequency
    annualization_factor: float
    status: RiskCalculationStatus
    historical_volatility: Optional[float]
    historical_variance: Optional[float]
    rolling_volatility_series: List[RollingRiskObservation]
    wealth_index_series: List[Tuple[datetime, float]]
    drawdown_series: List[Tuple[datetime, float]]
    max_drawdown: Optional[float]
    current_drawdown: Optional[float]
    drawdown_episodes: List[DrawdownEpisode]
    benchmark_sensitivity: Optional[BenchmarkSensitivityResult]
    model_estimated_variance: Optional[float]
    model_estimated_volatility: Optional[float]
    security_contributions: List[ComponentRiskContribution]
    covariance_diagnostics: Optional[CovarianceDiagnostics]
    data_coverage: RiskDataCoverage
    input_manifest: RiskInputManifest
    warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Stage 116: VaR, Expected Shortfall, Scenarios, and Model Validation Models
# ---------------------------------------------------------------------------


@dataclass
class VaRResult:
    """Estimated Value at Risk quantile."""
    model_type: VaRModelType
    confidence_level: float
    horizon_days: int
    var_fraction: float
    var_monetary: float
    status: RiskMetricStatus = RiskMetricStatus.AVAILABLE
    warning: Optional[str] = None
    effective_tail_sample_size: int = 1
    total_sample_size: int = 1
    method_notes: Optional[str] = None

    @property
    def var_return(self) -> float:
        return self.var_fraction

    @property
    def var_amount(self) -> float:
        return self.var_monetary


@dataclass
class ExpectedShortfallResult:
    """Estimated Expected Shortfall (tail conditional expectation)."""
    method: ExpectedShortfallMethod
    confidence_level: float
    horizon_days: int
    es_fraction: float
    es_monetary: float
    effective_tail_count: float
    tail_probability: float
    status: RiskMetricStatus = RiskMetricStatus.AVAILABLE
    warning: Optional[str] = None
    var_return: float = 0.0
    effective_tail_sample_size: int = 1
    total_sample_size: int = 1
    tail_weighting_scheme: str = "EXACT_FRACTIONAL_INTEGRATION"

    @property
    def es_return(self) -> float:
        return self.es_fraction

    @property
    def es_amount(self) -> float:
        return self.es_monetary


@dataclass
class LossDistribution:
    """Empirical or simulated loss distribution histogram and quantiles."""
    bins: List[float]
    counts: List[int]
    sample_count: int
    min_loss: float
    max_loss: float
    mean_loss: float
    quantiles: Dict[str, float]
    tail_losses: List[float] = field(default_factory=list)

    @property
    def total_observations(self) -> int:
        return self.sample_count


@dataclass
class TailRiskCalculationRun:
    """Complete versioned run of VaR and Expected Shortfall calculation."""
    run_id: str
    portfolio_id: str
    account_id: Optional[str]
    calculation_as_of: datetime
    model_type: VaRModelType
    confidence_level: float
    horizon_days: int
    reporting_currency: str
    portfolio_nav: float
    var_result: VaRResult
    es_result: ExpectedShortfallResult
    distribution: Optional[LossDistribution] = None
    model_comparison: Dict[str, Dict[str, float]] = field(default_factory=dict)
    sample_count: int = 0
    effective_tail_count: float = 0.0
    simulation_seed: Optional[int] = None
    simulation_count: Optional[int] = None
    data_coverage: Optional[RiskDataCoverage] = None
    input_manifest: Optional[RiskInputManifest] = None
    status: RiskCalculationStatus = RiskCalculationStatus.COMPLETED
    warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    input_hash: str = ""

    @property
    def var(self) -> VaRResult:
        return self.var_result

    @property
    def expected_shortfall(self) -> ExpectedShortfallResult:
        return self.es_result

    @property
    def loss_distribution(self) -> Optional[LossDistribution]:
        return self.distribution

    @property
    def baseline_nav(self) -> float:
        return self.portfolio_nav

    @property
    def as_of(self) -> datetime:
        return self.calculation_as_of


@dataclass
class ScenarioShock:
    """Specification of an individual market shock within a scenario."""
    shock_id: str
    shock_type: ScenarioShockType
    target_type: ShockTargetType
    target_id: str
    shock_value: float
    shock_units: str = "PERCENT"
    application_order: int = 1
    description: Optional[str] = None


@dataclass
class RiskScenario:
    """Canonical scenario definition (Historical Replay or Hypothetical Shock)."""
    scenario_id: str
    owner_user_id: str
    organization_id: Optional[str]
    name: str
    description: str
    scenario_type: ScenarioType
    historical_episode_id: Optional[str]
    shocks: List[ScenarioShock]
    reporting_currency: str = "USD"
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_system_predefined(self) -> bool:
        return self.owner_user_id == "SYSTEM"

    @property
    def user_id(self) -> Optional[str]:
        return self.owner_user_id


@dataclass
class ScenarioPositionResult:
    """Position-level P&L and revaluation under a scenario."""
    instrument_id: str
    symbol: str
    name: str
    category_label: str
    currency: str
    baseline_value: float
    weight: float
    shock_applied: float
    shock_source: str
    shocked_value: float
    pnl: float
    is_supported: bool = True
    unsupported_reason: Optional[str] = None

    @property
    def pnl_impact(self) -> float:
        return self.pnl

    @property
    def price_shock_pct(self) -> float:
        return self.shock_applied

    @property
    def fx_shock_pct(self) -> float:
        return 0.0

    @property
    def effective_total_shock_pct(self) -> float:
        return self.shock_applied

    @property
    def pre_shock_weight(self) -> float:
        return self.weight

    @property
    def pre_shock_value(self) -> float:
        return self.baseline_value

    @property
    def post_shock_value(self) -> float:
        return self.shocked_value

    @property
    def percentage_pnl_contribution(self) -> float:
        return 0.0

    @property
    def applied_rule_description(self) -> str:
        return self.shock_source

    @property
    def sector(self) -> str:
        return self.category_label


@dataclass
class RiskScenarioRun:
    """Execution run of a risk scenario against a portfolio snapshot."""
    run_id: str
    scenario_id: str
    scenario_name: str
    scenario_type: ScenarioType
    portfolio_id: str
    account_id: Optional[str]
    calculation_as_of: datetime
    baseline_nav: float
    shocked_nav: float
    portfolio_pnl: float
    scenario_return: float
    coverage_ratio: float
    eligible_value: float
    unsupported_value: float
    position_results: List[ScenarioPositionResult]
    reconciled: bool
    reconciliation_difference: float
    warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class VaRExceptionObservation:
    """Historical point-in-time VaR forecast vs realized next-period loss."""
    observation_date: datetime
    forecast_var: float
    realized_loss: float
    is_exception: bool
    exceedance_amount: float

    @property
    def date(self) -> datetime:
        return self.observation_date

    @property
    def var_forecast(self) -> float:
        return self.forecast_var

    @property
    def realized_return(self) -> float:
        return -self.realized_loss


@dataclass
class KupiecTestResult:
    """Statistical outcome and likelihood ratio of Kupiec coverage test."""
    total_observations: int
    exception_count: int
    confidence_level: float
    expected_rate: float
    observed_rate: float
    likelihood_ratio_stat: float
    critical_value_95: float
    p_value: float
    status: KupiecTestStatus
    is_sample_adequate: bool
    warnings: List[str] = field(default_factory=list)

    @property
    def test_status(self) -> KupiecTestStatus:
        return self.status

    @property
    def lr_statistic(self) -> float:
        return self.likelihood_ratio_stat

    @property
    def critical_value(self) -> float:
        return self.critical_value_95

    @property
    def sample_adequate(self) -> bool:
        return self.is_sample_adequate

    @property
    def expected_exceptions(self) -> float:
        return self.expected_rate * self.total_observations

    @property
    def observed_failure_rate(self) -> float:
        return self.observed_rate

    @property
    def expected_failure_rate(self) -> float:
        return self.expected_rate

    @property
    def decision_text(self) -> str:
        return f"Kupiec POF test: {self.status.value}"


@dataclass
class VaRBacktestRun:
    """Backtest run evaluating historical VaR exceptions and coverage."""
    backtest_id: str
    portfolio_id: str
    model_type: VaRModelType
    confidence_level: float
    horizon_days: int
    observation_start: datetime
    observation_end: datetime
    total_forecasts: int
    exceptions: List[VaRExceptionObservation]
    kupiec_test: KupiecTestResult
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    @property
    def start_date(self) -> datetime:
        return self.observation_start

    @property
    def end_date(self) -> datetime:
        return self.observation_end

    @property
    def observations(self) -> List[VaRExceptionObservation]:
        return self.exceptions


@dataclass
class PortfolioRiskSnapshot:
    """Lightweight immutable summary snapshot of key portfolio risk metrics."""
    snapshot_id: str
    portfolio_id: str
    risk_run_id: str
    as_of: datetime
    reporting_currency: str
    historical_volatility_annualized: Optional[float]
    model_volatility_annualized: Optional[float]
    max_drawdown: Optional[float]
    current_drawdown: Optional[float]
    beta: Optional[float]
    correlation: Optional[float]
    coverage_ratio: float
    status: RiskCalculationStatus
    input_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None




# ---------------------------------------------------------------------------
# Stage 117: Factor, Concentration, Currency, and Sector Risk Domain Models
# ---------------------------------------------------------------------------


@dataclass
class RiskFactorDefinition:
    """Canonical factor specification in the factor registry."""
    factor_id: str
    factor_code: str
    factor_name: str
    family: FactorFamily
    description: str
    methodology: str
    geographical_scope: str = "GLOBAL"
    currency: str = "USD"
    return_basis: FactorReturnBasis = FactorReturnBasis.EXCESS_RETURN
    version: str = "1.0.0"


@dataclass
class SecurityFactorExposure:
    """Estimated systematic factor loadings and regression diagnostics for an instrument."""
    symbol: str
    factor_betas: Dict[str, float]
    intercept: float = 0.0
    residual_variance: float = 0.0
    r_squared: float = 0.0
    t_stats: Dict[str, float] = field(default_factory=dict)


@dataclass
class FactorRiskContribution:
    """Analytical risk contribution of a single factor to portfolio variance and volatility."""
    factor_id: str
    factor_name: str
    portfolio_exposure: float
    variance_contribution: float
    volatility_contribution: float
    percentage_of_variance: float


@dataclass
class FactorModelDiagnostics:
    """Regression health and collinearity diagnostics."""
    observation_count: int
    factor_count: int
    design_matrix_rank: int
    condition_number: float
    is_rank_deficient: bool
    is_collinear: bool
    status: ModelDiagnosticStatus = ModelDiagnosticStatus.HEALTHY
    warnings: List[str] = field(default_factory=list)


@dataclass
class FactorRiskRun:
    """Executed multi-factor portfolio risk decomposition."""
    run_id: str
    portfolio_id: str
    as_of: datetime
    model_id: str
    model_version: str
    factor_ids: List[str]
    factor_exposures: Dict[str, float]
    benchmark_exposures: Optional[Dict[str, float]]
    active_exposures: Optional[Dict[str, float]]
    systematic_variance: float
    specific_variance: float
    total_variance: float
    total_volatility: float
    factor_contributions: List[FactorRiskContribution]
    specific_risk_contribution: float
    specific_variance_contribution: float
    security_exposures: List[SecurityFactorExposure]
    factor_covariance_matrix: List[List[float]]
    diagnostics: FactorModelDiagnostics
    is_reconciled: bool
    reconciliation_diff: float
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def portfolio_exposures(self) -> Dict[str, float]:
        return self.factor_exposures

    @property
    def portfolio_volatility(self) -> float:
        return self.total_volatility

    @property
    def active_factor_exposures(self) -> Optional[Dict[str, float]]:
        return self.active_exposures


@dataclass
class ConcentrationItem:
    """Individual bucket entry in a concentration partition."""
    identifier: str
    name: str
    dimension: ConcentrationDimension
    weight: float
    market_value: float
    rank: int
    securities_count: int = 1
    security_symbols: List[str] = field(default_factory=list)


@dataclass
class ConcentrationSnapshot:
    """Herfindahl-Hirschman index, effective holdings count, and Top-N concentration."""
    portfolio_id: str
    as_of: datetime
    dimension: ConcentrationDimension
    hhi: float
    effective_number_of_holdings: float
    top_1_weight: float
    top_3_weight: float
    top_5_weight: float
    top_10_weight: float
    items: List[ConcentrationItem]
    total_positions_count: int
    total_issuers_count: int
    coverage_ratio: float = 1.0


@dataclass
class CurrencyExposureItem:
    """Direct denomination and estimated economic sensitivity for a single currency."""
    currency: str
    weight: float
    market_value: float
    cash_market_value: float
    exposure_type: CurrencyExposureType
    historical_fx_volatility: Optional[float] = None
    fx_sensitivity_beta: Optional[float] = None


@dataclass
class CurrencyRiskSnapshot:
    """Consolidated portfolio currency risk, FX volatility, and base/local decomposition."""
    portfolio_id: str
    as_of: datetime
    reporting_currency: str
    exposures: List[CurrencyExposureItem]
    foreign_currency_weight: float
    foreign_currency_market_value: float
    base_local_interaction: Dict[str, float] = field(default_factory=dict)
    cross_currency_correlations: Optional[Dict[str, Dict[str, float]]] = None


@dataclass
class SectorRiskItem:
    """Euler risk contribution and standalone volatility of an individual economic sector."""
    sector_name: str
    weight: float
    standalone_volatility: Optional[float]
    variance_contribution: float
    volatility_contribution: float
    percentage_of_variance: float
    benchmark_weight: Optional[float] = None
    active_weight: Optional[float] = None


@dataclass
class IndustryRiskItem:
    """Drilldown hierarchical risk contribution for an industry within a sector."""
    sector_name: str
    industry_name: str
    weight: float
    variance_contribution: float
    volatility_contribution: float


@dataclass
class SectorRiskSnapshot:
    """Complete portfolio sector and industry Euler risk attribution."""
    portfolio_id: str
    as_of: datetime
    portfolio_variance: float
    portfolio_volatility: float
    sectors: List[SectorRiskItem]
    industries: List[IndustryRiskItem]
    sector_correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None
    is_reconciled: bool = True
    reconciliation_diff: float = 0.0


@dataclass
class CrossExposureCell:
    """Value at the intersection of two exposure dimensions."""
    row_key: str
    col_key: str
    value: float
    unit: str = "WEIGHT_PERCENT"


@dataclass
class CrossExposureMatrix:
    """Two-dimensional cross-exposure distribution (e.g. Factor x Sector, Currency x Sector)."""
    row_dimension: str
    col_dimension: str
    row_keys: List[str]
    col_keys: List[str]
    cells: List[CrossExposureCell]
    unit: str = "WEIGHT_PERCENT"
