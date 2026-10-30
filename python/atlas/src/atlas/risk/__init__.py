"""ATLAS Financial Risk Foundation (Stage 115).

Institutional market-risk measurement, historical realized volatility,
rolling volatility series, drawdown analytics, benchmark sensitivity (beta, correlation),
and covariance-based Euler risk decomposition.
"""

from .benchmark import BenchmarkSensitivityEngine
from .covariance_risk import ModelRiskEngine
from .drawdown import DrawdownEngine
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
from .errors import (
    RiskBenchmarkNotFoundError,
    RiskBenchmarkReturnSeriesMissingError,
    RiskBenchmarkVarianceZeroError,
    RiskCalculationFailedError,
    RiskContributionUnavailableError,
    RiskCorrelationUndefinedError,
    RiskCovarianceDimensionMismatchError,
    RiskCovarianceMissingError,
    RiskCovarianceNotPSDError,
    RiskCovarianceNumericalFailureError,
    RiskDrawdownIndexInvalidError,
    RiskError,
    RiskInsufficientObservationsError,
    RiskModelNotFoundError,
    RiskModelUnsupportedError,
    RiskPeriodInvalidError,
    RiskPortfolioValuationIncompleteError,
    RiskReconciliationFailedError,
    RiskReturnSeriesMissingError,
    RiskRunNotFoundError,
    RiskSourceRestrictedError,
    RiskSubjectAccessDeniedError,
    RiskSubjectNotFoundError,
)
from .models import (
    BenchmarkSensitivityResult,
    ComponentRiskContribution,
    CovarianceDiagnostics,
    DrawdownEpisode,
    PortfolioRiskSnapshot,
    RiskCalculationRun,
    RiskDataCoverage,
    RiskInputManifest,
    RiskMetricDefinition,
    RiskModelDefinition,
    RiskReturnSeries,
    RiskSubject,
    RollingRiskObservation,
)
from .multi_currency import MultiCurrencyRiskEngine
from .quality import RiskDataQualityEngine
from .reconciliation import RiskReconciliationEngine
from .service import RiskService
from .volatility import HistoricalVolatilityEngine

__all__ = [
    # Engines
    "HistoricalVolatilityEngine",
    "DrawdownEngine",
    "BenchmarkSensitivityEngine",
    "ModelRiskEngine",
    "MultiCurrencyRiskEngine",
    "RiskDataQualityEngine",
    "RiskReconciliationEngine",
    "RiskService",
    # Enums
    "RiskSubjectType",
    "RiskMetricCode",
    "RiskModelType",
    "RiskCalculationStatus",
    "RiskMetricStatus",
    "RiskReturnFrequency",
    "AnnualizationPolicy",
    "DataCoverageStatus",
    "ReturnBasis",
    "DrawdownEpisodeStatus",
    # Models
    "RiskSubject",
    "RiskMetricDefinition",
    "RiskModelDefinition",
    "RiskReturnSeries",
    "RollingRiskObservation",
    "DrawdownEpisode",
    "BenchmarkSensitivityResult",
    "ComponentRiskContribution",
    "CovarianceDiagnostics",
    "RiskDataCoverage",
    "RiskInputManifest",
    "RiskCalculationRun",
    "PortfolioRiskSnapshot",
    # Errors
    "RiskError",
    "RiskSubjectNotFoundError",
    "RiskSubjectAccessDeniedError",
    "RiskRunNotFoundError",
    "RiskModelNotFoundError",
    "RiskModelUnsupportedError",
    "RiskPeriodInvalidError",
    "RiskInsufficientObservationsError",
    "RiskReturnSeriesMissingError",
    "RiskBenchmarkNotFoundError",
    "RiskBenchmarkReturnSeriesMissingError",
    "RiskBenchmarkVarianceZeroError",
    "RiskCorrelationUndefinedError",
    "RiskDrawdownIndexInvalidError",
    "RiskPortfolioValuationIncompleteError",
    "RiskCovarianceMissingError",
    "RiskCovarianceNotPSDError",
    "RiskCovarianceDimensionMismatchError",
    "RiskCovarianceNumericalFailureError",
    "RiskContributionUnavailableError",
    "RiskReconciliationFailedError",
    "RiskSourceRestrictedError",
    "RiskCalculationFailedError",
]
