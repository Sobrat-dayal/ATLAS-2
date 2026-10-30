"""ATLAS Financial Risk Foundation — Errors (Stage 115).

Typed domain exceptions for portfolio risk measurement, return series validation,
covariance diagnostics, and reconciliation.
"""

from typing import Any, Optional


class RiskError(Exception):
    """Base exception for all financial risk domain errors."""

    status_code: int = 400
    code: str = "RISK_ERROR"

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RiskSubjectNotFoundError(RiskError):
    status_code: int = 404
    code: str = "RISK_SUBJECT_NOT_FOUND"


class RiskSubjectAccessDeniedError(RiskError):
    status_code: int = 403
    code: str = "RISK_SUBJECT_ACCESS_DENIED"


class RiskRunNotFoundError(RiskError):
    status_code: int = 404
    code: str = "RISK_RUN_NOT_FOUND"


class RiskModelNotFoundError(RiskError):
    status_code: int = 404
    code: str = "RISK_MODEL_NOT_FOUND"


class RiskModelUnsupportedError(RiskError):
    status_code: int = 400
    code: str = "RISK_MODEL_UNSUPPORTED"


class RiskMetricUnsupportedError(RiskError):
    status_code: int = 400
    code: str = "RISK_METRIC_UNSUPPORTED"


class RiskPeriodInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_PERIOD_INVALID"


class RiskInsufficientObservationsError(RiskError):
    status_code: int = 400
    code: str = "RISK_INSUFFICIENT_OBSERVATIONS"


class RiskReturnSeriesMissingError(RiskError):
    status_code: int = 400
    code: str = "RISK_RETURN_SERIES_MISSING"


class RiskBenchmarkNotFoundError(RiskError):
    status_code: int = 404
    code: str = "RISK_BENCHMARK_NOT_FOUND"


class RiskBenchmarkReturnSeriesMissingError(RiskError):
    status_code: int = 400
    code: str = "RISK_BENCHMARK_RETURN_SERIES_MISSING"


class RiskBenchmarkVarianceZeroError(RiskError):
    status_code: int = 400
    code: str = "RISK_BENCHMARK_VARIANCE_ZERO"


class RiskCorrelationUndefinedError(RiskError):
    status_code: int = 400
    code: str = "RISK_CORRELATION_UNDEFINED"


class RiskDrawdownIndexInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_DRAWDOWN_INDEX_INVALID"


class RiskPortfolioValuationIncompleteError(RiskError):
    status_code: int = 400
    code: str = "RISK_PORTFOLIO_VALUATION_INCOMPLETE"


class RiskCovarianceMissingError(RiskError):
    status_code: int = 400
    code: str = "RISK_COVARIANCE_MISSING"


class RiskCovarianceNotPSDError(RiskError):
    status_code: int = 400
    code: str = "RISK_COVARIANCE_NOT_PSD"


class RiskCovarianceDimensionMismatchError(RiskError):
    status_code: int = 400
    code: str = "RISK_COVARIANCE_DIMENSION_MISMATCH"


class RiskCovarianceNumericalFailureError(RiskError):
    status_code: int = 400
    code: str = "RISK_COVARIANCE_NUMERICAL_FAILURE"


class RiskContributionUnavailableError(RiskError):
    status_code: int = 400
    code: str = "RISK_RISK_CONTRIBUTION_UNAVAILABLE"


class RiskReconciliationFailedError(RiskError):
    status_code: int = 400
    code: str = "RISK_RECONCILIATION_FAILED"


class RiskSourceRestrictedError(RiskError):
    status_code: int = 403
    code: str = "RISK_SOURCE_RESTRICTED"


class RiskCalculationFailedError(RiskError):
    status_code: int = 500
    code: str = "RISK_CALCULATION_FAILED"


# ---------------------------------------------------------------------------
# Stage 116: VaR, Expected Shortfall, and Scenario Testing Typed Errors
# ---------------------------------------------------------------------------


class RiskVaRModelUnsupportedError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_MODEL_UNSUPPORTED"


class RiskVaRConfidenceInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_CONFIDENCE_INVALID"


class RiskVaRHorizonInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_HORIZON_INVALID"


class RiskVaRInsufficientHistoryError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_INSUFFICIENT_HISTORY"


class RiskVaRInsufficientTailSampleError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_INSUFFICIENT_TAIL_SAMPLE"


class RiskVaRReturnSeriesIncompleteError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_RETURN_SERIES_INCOMPLETE"


class RiskVaRPortfolioValuationIncompleteError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_PORTFOLIO_VALUATION_INCOMPLETE"


class RiskVaRCovarianceInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_COVARIANCE_INVALID"


class RiskVaRDistributionInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_DISTRIBUTION_INVALID"


class RiskVaRNumericalFailureError(RiskError):
    status_code: int = 400
    code: str = "RISK_VAR_NUMERICAL_FAILURE"


class RiskESTailEstimatorInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_ES_TAIL_ESTIMATOR_INVALID"


class RiskESInsufficientTailSampleError(RiskError):
    status_code: int = 400
    code: str = "RISK_ES_INSUFFICIENT_TAIL_SAMPLE"


class RiskMonteCarloModelUnsupportedError(RiskError):
    status_code: int = 400
    code: str = "RISK_MONTE_CARLO_MODEL_UNSUPPORTED"


class RiskMonteCarloResourceLimitError(RiskError):
    status_code: int = 400
    code: str = "RISK_MONTE_CARLO_RESOURCE_LIMIT"


class RiskMonteCarloTimeoutError(RiskError):
    status_code: int = 408
    code: str = "RISK_MONTE_CARLO_TIMEOUT"


class RiskScenarioNotFoundError(RiskError):
    status_code: int = 404
    code: str = "RISK_SCENARIO_NOT_FOUND"


class RiskScenarioAccessDeniedError(RiskError):
    status_code: int = 403
    code: str = "RISK_SCENARIO_ACCESS_DENIED"


class RiskScenarioShockInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_SCENARIO_SHOCK_INVALID"


class RiskScenarioShockConflictError(RiskError):
    status_code: int = 400
    code: str = "RISK_SCENARIO_SHOCK_CONFLICT"


class RiskScenarioUnsupportedInstrumentError(RiskError):
    status_code: int = 400
    code: str = "RISK_SCENARIO_UNSUPPORTED_INSTRUMENT"


class RiskScenarioHistoricalDataMissingError(RiskError):
    status_code: int = 400
    code: str = "RISK_SCENARIO_HISTORICAL_DATA_MISSING"


class RiskScenarioRepricingUnavailableError(RiskError):
    status_code: int = 400
    code: str = "RISK_SCENARIO_REPRICING_UNAVAILABLE"


class RiskScenarioReconciliationFailedError(RiskError):
    status_code: int = 400
    code: str = "RISK_SCENARIO_RECONCILIATION_FAILED"


class RiskTailBacktestInsufficientObservationsError(RiskError):
    status_code: int = 400
    code: str = "RISK_TAIL_BACKTEST_INSUFFICIENT_OBSERVATIONS"


class RiskTailRunNotFoundError(RiskError):
    status_code: int = 404
    code: str = "RISK_TAIL_RUN_NOT_FOUND"


class RiskTailSourceRestrictedError(RiskError):
    status_code: int = 403
    code: str = "RISK_TAIL_SOURCE_RESTRICTED"


