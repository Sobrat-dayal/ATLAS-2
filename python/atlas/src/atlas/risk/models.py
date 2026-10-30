"""ATLAS Financial Risk Foundation — Domain Models (Stage 115).

Domain dataclasses for institutional risk calculations, rolling volatility series,
drawdown episodes, benchmark sensitivities, and covariance-based risk contributions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

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

