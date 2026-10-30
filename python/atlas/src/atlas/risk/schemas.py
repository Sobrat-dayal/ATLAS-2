"""ATLAS Financial Risk Foundation — Pydantic Schemas (Stage 115).

Data transfer objects for risk calculations, requests, rolling volatility,
drawdown analytics, benchmark sensitivity, and covariance diagnostics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from .enums import (
    AnnualizationPolicy,
    BondPricingModelId,
    ConcentrationDimension,
    CouponFrequency,
    CouponType,
    CurrencyExposureType,
    DataCoverageStatus,
    DayCountConvention,
    DrawdownEpisodeStatus,
    ExerciseStyle,
    ExpectedShortfallMethod,
    FactorFamily,
    FactorReturnBasis,
    KupiecTestStatus,
    ModelDiagnosticStatus,
    OptionContractStatus,
    OptionSettlementType,
    OptionsPricingModelId,
    OptionType,
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
    YieldCurveInterpolation,
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




# ---------------------------------------------------------------------------
# Stage 117: Factor, Concentration, Currency, and Sector Risk Schemas
# ---------------------------------------------------------------------------


class RiskFactorDefinitionDTO(BaseModel):
    """Specification of an economic risk factor."""
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


class SecurityFactorExposureDTO(BaseModel):
    """Estimated systematic factor loadings for a single security."""
    symbol: str
    factor_betas: Dict[str, float]
    intercept: float = 0.0
    residual_variance: float = 0.0
    r_squared: float = 0.0
    t_stats: Dict[str, float] = Field(default_factory=dict)


class FactorRiskContributionDTO(BaseModel):
    """Analytical risk contribution of a single factor to portfolio variance and volatility."""
    factor_id: str
    factor_name: str
    portfolio_exposure: float
    variance_contribution: float
    volatility_contribution: float
    percentage_of_variance: float


class FactorModelDiagnosticsDTO(BaseModel):
    """Regression health and collinearity diagnostics."""
    observation_count: int
    factor_count: int
    design_matrix_rank: int
    condition_number: float
    is_rank_deficient: bool
    is_collinear: bool
    status: ModelDiagnosticStatus = ModelDiagnosticStatus.HEALTHY
    warnings: List[str] = Field(default_factory=list)


class CalculateFactorRiskRequest(BaseModel):
    """Request payload to calculate portfolio multi-factor risk decomposition."""
    portfolio_id: str
    account_id: Optional[str] = None
    as_of: Optional[datetime] = None
    model_id: str = "FAMA_FRENCH_6"
    factor_ids: Optional[List[str]] = None
    benchmark_id: Optional[str] = None
    annualization_factor: float = Field(default=252.0, ge=1.0)


class FactorRiskRunDTO(BaseModel):
    """Full execution output of portfolio multi-factor risk decomposition."""
    run_id: str
    portfolio_id: str
    as_of: str
    model_id: str
    model_version: str
    factor_ids: List[str]
    factor_exposures: Dict[str, float]
    benchmark_exposures: Optional[Dict[str, float]] = None
    active_exposures: Optional[Dict[str, float]] = None
    systematic_variance: float
    specific_variance: float
    total_variance: float
    total_volatility: float
    factor_contributions: List[FactorRiskContributionDTO]
    specific_risk_contribution: float
    specific_variance_contribution: float
    security_exposures: List[SecurityFactorExposureDTO]
    factor_covariance_matrix: List[List[float]]
    diagnostics: FactorModelDiagnosticsDTO
    is_reconciled: bool
    reconciliation_diff: float
    created_at: str


class ConcentrationItemDTO(BaseModel):
    """Single item bucket in a concentration partition."""
    identifier: str
    name: str
    dimension: ConcentrationDimension
    weight: float
    market_value: float
    rank: int
    securities_count: int = 1
    security_symbols: List[str] = Field(default_factory=list)


class ConcentrationSnapshotDTO(BaseModel):
    """Herfindahl-Hirschman index, effective holdings, and Top-N concentration."""
    portfolio_id: str
    as_of: str
    dimension: ConcentrationDimension
    hhi: float
    effective_number_of_holdings: float
    top_1_weight: float
    top_3_weight: float
    top_5_weight: float
    top_10_weight: float
    items: List[ConcentrationItemDTO]
    total_positions_count: int
    total_issuers_count: int
    coverage_ratio: float = 1.0


class CurrencyExposureItemDTO(BaseModel):
    """Currency denomination exposure and estimated economic sensitivity."""
    currency: str
    weight: float
    market_value: float
    cash_market_value: float
    exposure_type: CurrencyExposureType
    historical_fx_volatility: Optional[float] = None
    fx_sensitivity_beta: Optional[float] = None


class CurrencyRiskSnapshotDTO(BaseModel):
    """Portfolio currency risk, FX volatility, and base/local decomposition."""
    portfolio_id: str
    as_of: str
    reporting_currency: str
    exposures: List[CurrencyExposureItemDTO]
    foreign_currency_weight: float
    foreign_currency_market_value: float
    base_local_interaction: Dict[str, float] = Field(default_factory=dict)
    cross_currency_correlations: Optional[Dict[str, Dict[str, float]]] = None


class SectorRiskItemDTO(BaseModel):
    """Sector Euler risk contribution and standalone volatility."""
    sector_name: str
    weight: float
    standalone_volatility: Optional[float] = None
    variance_contribution: float
    volatility_contribution: float
    percentage_of_variance: float
    benchmark_weight: Optional[float] = None
    active_weight: Optional[float] = None


class IndustryRiskItemDTO(BaseModel):
    """Industry drilldown Euler risk contribution."""
    sector_name: str
    industry_name: str
    weight: float
    variance_contribution: float
    volatility_contribution: float


class SectorRiskSnapshotDTO(BaseModel):
    """Portfolio sector and industry Euler risk attribution."""
    portfolio_id: str
    as_of: str
    portfolio_variance: float
    portfolio_volatility: float
    sectors: List[SectorRiskItemDTO]
    industries: List[IndustryRiskItemDTO]
    sector_correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None
    is_reconciled: bool = True
    reconciliation_diff: float = 0.0


class CrossExposureCellDTO(BaseModel):
    """Cell value in a 2D cross-exposure matrix."""
    row_key: str
    col_key: str
    value: float
    unit: str = "WEIGHT_PERCENT"


class CrossExposureMatrixDTO(BaseModel):
    """Two-dimensional cross-exposure matrix."""
    row_dimension: str
    col_dimension: str
    row_keys: List[str]
    col_keys: List[str]
    cells: List[CrossExposureCellDTO]
    unit: str = "WEIGHT_PERCENT"



# ---------------------------------------------------------------------------
# Stage 118: Options and Fixed-Income Risk Schemas / DTOs
# ---------------------------------------------------------------------------


class CalculateOptionsRiskRequest(BaseModel):
    """Standalone option pricing and Greeks calculation request."""
    instrument_id: Optional[str] = "OPT_CUSTOM"
    underlying_symbol: str = "SPY"
    option_type: OptionType = OptionType.CALL
    exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN
    strike_price: float = Field(..., gt=0.0)
    time_to_expiry_years: float = Field(..., ge=0.0)
    underlying_price: float = Field(..., gt=0.0)
    implied_volatility: float = Field(..., gt=0.0)
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0
    contract_multiplier: float = 100.0
    contracts_quantity: Optional[float] = 1.0
    model_id: OptionsPricingModelId = OptionsPricingModelId.EUROPEAN_BLACK_SCHOLES_MERTON


class OptionGreeksResultDTO(BaseModel):
    """Analytical Greeks and theoretical option price."""
    theoretical_price: float
    delta: float
    gamma: float
    vega: float
    vega_per_vol_point: float
    theta: float
    theta_per_day: float
    rho: float
    rho_per_basis_point: float
    intrinsic_value: float
    time_value: float
    implied_volatility: float
    d1: float
    d2: float
    put_call_parity_diff: Optional[float] = None
    is_pricing_valid: bool = True
    pricing_model: str


class OptionPositionRiskDTO(BaseModel):
    """Position-level options exposure and scaled Greeks."""
    position_id: str
    instrument_id: str
    underlying_symbol: str
    option_type: OptionType
    exercise_style: ExerciseStyle
    strike_price: float
    time_to_expiry_years: float
    contracts_quantity: float
    contract_multiplier: float
    position_market_value: float
    underlying_price: float
    currency: str
    base_currency: str
    fx_rate_to_base: float
    per_contract_greeks: OptionGreeksResultDTO
    position_delta_units: float
    position_delta_notional: float
    position_gamma_units: float
    position_vega_per_vol_point: float
    position_theta_per_day: float
    position_rho_per_basis_point: float
    base_currency_delta_notional: float
    base_currency_vega_per_vol_point: float
    base_currency_theta_per_day: float
    base_currency_rho_per_basis_point: float
    approximate_pnl_shock: Dict[str, float] = Field(default_factory=dict)
    full_reprice_pnl_shock: Dict[str, float] = Field(default_factory=dict)


class PortfolioOptionsRiskSummaryDTO(BaseModel):
    """Aggregated portfolio-level options risk summary."""
    portfolio_id: str
    as_of: str
    base_currency: str
    total_options_market_value: float
    options_count: int
    net_delta_notional: float
    gross_delta_notional: float
    net_vega_per_vol_point: float
    gross_vega_per_vol_point: float
    net_theta_per_day: float
    net_rho_per_basis_point: float
    underlying_exposures: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    positions: List[OptionPositionRiskDTO] = Field(default_factory=list)
    is_complete: bool = True
    warnings: List[str] = Field(default_factory=list)


class BondCashFlowItemDTO(BaseModel):
    """Projected bond coupon or principal cash flow."""
    period_index: int
    payment_date: str
    year_fraction: float
    coupon_amount: float
    principal_amount: float
    total_cash_flow: float
    discount_factor: float
    present_value: float


class BondCashFlowScheduleDTO(BaseModel):
    """Complete cash flow schedule for a bond position."""
    instrument_id: str
    face_value: float
    coupon_rate: float
    coupon_frequency: CouponFrequency
    day_count_convention: DayCountConvention
    settlement_date: str
    maturity_date: str
    cash_flows: List[BondCashFlowItemDTO]
    accrued_interest: float
    clean_price: float
    dirty_price: float


class KeyRateSensitivityItemDTO(BaseModel):
    """Key-rate duration sensitivity at a tenor bucket."""
    tenor_name: str
    tenor_years: float
    key_rate_duration: float
    key_rate_dv01: float


class BondSensitivitiesResultDTO(BaseModel):
    """Bond yield, duration, convexity, and DV01 metrics."""
    clean_price: float
    accrued_interest: float
    dirty_price: float
    yield_to_maturity: float
    macaulay_duration: float
    modified_duration: float
    convexity: float
    dv01_per_100_face: float
    effective_duration: Optional[float] = None
    effective_convexity: Optional[float] = None
    key_rate_durations: List[KeyRateSensitivityItemDTO] = Field(default_factory=list)
    pricing_model: str


class BondPositionRiskDTO(BaseModel):
    """Position-level fixed-income sensitivities and DV01."""
    position_id: str
    instrument_id: str
    issuer_name: str
    face_value: float
    quantity: float
    currency: str
    base_currency: str
    fx_rate_to_base: float
    market_value: float
    sensitivities: BondSensitivitiesResultDTO
    position_dv01: float
    base_currency_dv01: float
    cash_flow_schedule: Optional[BondCashFlowScheduleDTO] = None


class CalculateFixedIncomeRiskRequest(BaseModel):
    """Standalone fixed-income pricing and duration calculation request."""
    instrument_id: Optional[str] = "BOND_CUSTOM"
    face_value: float = Field(default=100.0, gt=0.0)
    coupon_rate: float = Field(default=0.05, ge=0.0)
    coupon_frequency: CouponFrequency = CouponFrequency.ANNUAL
    day_count_convention: DayCountConvention = DayCountConvention.ACT_ACT
    settlement_date: Optional[str] = None
    maturity_date: Optional[str] = None
    maturity_years: Optional[float] = Field(default=2.0, gt=0.0)
    market_price: Optional[float] = Field(default=100.0, gt=0.0)
    yield_to_maturity: Optional[float] = None
    pricing_model: BondPricingModelId = BondPricingModelId.DISCOUNTED_CASHFLOW


class YieldCurvePointDTO(BaseModel):
    """Point on a calibrated yield curve."""
    tenor_years: float
    rate: float
    label: str
    discount_factor: float = 1.0


class InterestRateCurveDefinitionDTO(BaseModel):
    """Yield curve term structure definition."""
    curve_id: str
    currency: str
    as_of: str
    interpolation_method: YieldCurveInterpolation
    points: List[YieldCurvePointDTO]


class PortfolioFixedIncomeRiskSummaryDTO(BaseModel):
    """Aggregated portfolio-level fixed income analytics."""
    portfolio_id: str
    as_of: str
    base_currency: str
    total_fixed_income_market_value: float
    bonds_count: int
    portfolio_weighted_modified_duration: float
    portfolio_weighted_macaulay_duration: float
    portfolio_weighted_convexity: float
    portfolio_weighted_yield: float
    portfolio_total_dv01: float
    key_rate_dv01_profile: Dict[str, float] = Field(default_factory=dict)
    positions: List[BondPositionRiskDTO] = Field(default_factory=list)
    is_complete: bool = True
    warnings: List[str] = Field(default_factory=list)


class PortfolioInstrumentSensitivitiesSummaryDTO(BaseModel):
    """Cross-asset risk synthesis across equity, options, and fixed income."""
    portfolio_id: str
    as_of: str
    base_currency: str
    total_portfolio_value: float
    options_summary: Optional[PortfolioOptionsRiskSummaryDTO] = None
    fixed_income_summary: Optional[PortfolioFixedIncomeRiskSummaryDTO] = None
    net_equity_delta_equivalent: float = 0.0
    net_fixed_income_dv01: float = 0.0
