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




# ---------------------------------------------------------------------------
# Stage 117: Factor, Concentration, Currency, and Sector Risk Errors
# ---------------------------------------------------------------------------


class RiskFactorNotFoundError(RiskError):
    status_code: int = 404
    code: str = "RISK_FACTOR_NOT_FOUND"


class RiskFactorModelUnsupportedError(RiskError):
    status_code: int = 400
    code: str = "RISK_FACTOR_MODEL_UNSUPPORTED"


class RiskFactorReturnHistoryInsufficientError(RiskError):
    status_code: int = 400
    code: str = "RISK_FACTOR_RETURN_HISTORY_INSUFFICIENT"


class RiskFactorRegressionRankDeficientError(RiskError):
    status_code: int = 400
    code: str = "RISK_FACTOR_REGRESSION_RANK_DEFICIENT"


class RiskFactorCollinearityDetectedError(RiskError):
    status_code: int = 400
    code: str = "RISK_FACTOR_COLLINEARITY_DETECTED"


class RiskFactorCovarianceNotPSDError(RiskError):
    status_code: int = 400
    code: str = "RISK_FACTOR_COVARIANCE_NOT_PSD"


class RiskFactorResidualCovarianceInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_FACTOR_RESIDUAL_COVARIANCE_INVALID"


class RiskFactorReconciliationFailedError(RiskError):
    status_code: int = 400
    code: str = "RISK_FACTOR_RECONCILIATION_FAILED"


class RiskConcentrationInvalidWeightsError(RiskError):
    status_code: int = 400
    code: str = "RISK_CONCENTRATION_INVALID_WEIGHTS"


class RiskConcentrationClassificationIncompleteError(RiskError):
    status_code: int = 400
    code: str = "RISK_CONCENTRATION_CLASSIFICATION_INCOMPLETE"


class RiskCurrencyFXHistoryMissingError(RiskError):
    status_code: int = 400
    code: str = "RISK_CURRENCY_FX_HISTORY_MISSING"


class RiskCurrencySensitivityUnavailableError(RiskError):
    status_code: int = 400
    code: str = "RISK_CURRENCY_SENSITIVITY_UNAVAILABLE"


class RiskSectorClassificationMissingError(RiskError):
    status_code: int = 400
    code: str = "RISK_SECTOR_CLASSIFICATION_MISSING"


class RiskSectorReturnHistoryMissingError(RiskError):
    status_code: int = 400
    code: str = "RISK_SECTOR_RETURN_HISTORY_MISSING"


class RiskSectorCovarianceInvalidError(RiskError):
    status_code: int = 400
    code: str = "RISK_SECTOR_COVARIANCE_INVALID"


class RiskSectorReconciliationFailedError(RiskError):
    status_code: int = 400
    code: str = "RISK_SECTOR_RECONCILIATION_FAILED"


class RiskCrossExposureDimensionMismatchError(RiskError):
    status_code: int = 400
    code: str = "RISK_CROSS_EXPOSURE_DIMENSION_MISMATCH"


class RiskStage117SourceRestrictedError(RiskError):
    status_code: int = 403
    code: str = "RISK_STAGE117_SOURCE_RESTRICTED"


class RiskStage117RunNotFoundError(RiskError):
    status_code: int = 404
    code: str = "RISK_STAGE117_RUN_NOT_FOUND"


# ---------------------------------------------------------------------------
# Stage 118: Options and Fixed-Income Risk Foundations Errors
# ---------------------------------------------------------------------------


class RiskOptionContractIncompleteError(RiskError):
    """Option contract specification is missing mandatory fields (strike, expiry, style, etc.)."""
    status_code: int = 400
    code: str = "RISK_OPTION_CONTRACT_INCOMPLETE"


class RiskOptionExerciseStyleUnsupportedError(RiskError):
    """Exercise style (e.g. Bermudan/American) is not supported by the requested pricing model."""
    status_code: int = 400
    code: str = "RISK_OPTION_EXERCISE_STYLE_UNSUPPORTED"


class RiskOptionExpiredError(RiskError):
    """Option contract has expired (T <= 0)."""
    status_code: int = 400
    code: str = "RISK_OPTION_EXPIRED"


class RiskOptionImpliedVolatilityMissingError(RiskError):
    """Implied volatility is required for analytical option pricing but is missing."""
    status_code: int = 400
    code: str = "RISK_OPTION_IMPLIED_VOLATILITY_MISSING"


class RiskOptionImpliedVolatilityNonPositiveError(RiskError):
    """Implied volatility must be strictly positive (sigma > 0)."""
    status_code: int = 400
    code: str = "RISK_OPTION_IMPLIED_VOLATILITY_NON_POSITIVE"


class RiskOptionUnderlyingPriceNonPositiveError(RiskError):
    """Underlying asset price must be strictly positive (S > 0)."""
    status_code: int = 400
    code: str = "RISK_OPTION_UNDERLYING_PRICE_NON_POSITIVE"


class RiskOptionStrikeNonPositiveError(RiskError):
    """Option strike price must be strictly positive (K > 0)."""
    status_code: int = 400
    code: str = "RISK_OPTION_STRIKE_NON_POSITIVE"


class RiskOptionTimeToExpiryNegativeError(RiskError):
    """Time to expiration cannot be negative."""
    status_code: int = 400
    code: str = "RISK_OPTION_TIME_TO_EXPIRY_NEGATIVE"


class RiskOptionMultiplierInvalidError(RiskError):
    """Option contract multiplier must be positive (e.g. 100)."""
    status_code: int = 400
    code: str = "RISK_OPTION_MULTIPLIER_INVALID"


class RiskOptionModelRepricingFailedError(RiskError):
    """Repricing option contract under scenario shift failed."""
    status_code: int = 400
    code: str = "RISK_OPTION_MODEL_REPRICING_FAILED"


class RiskOptionParityCheckFailedError(RiskError):
    """Put-call parity check failed beyond numerical tolerance."""
    status_code: int = 400
    code: str = "RISK_OPTION_PARITY_CHECK_FAILED"


class RiskOptionPositionQuantityZeroError(RiskError):
    """Option position quantity cannot be zero."""
    status_code: int = 400
    code: str = "RISK_OPTION_POSITION_QUANTITY_ZERO"


class RiskBondCashflowIncompleteError(RiskError):
    """Bond instrument specification lacks maturity, face value, or coupon frequency."""
    status_code: int = 400
    code: str = "RISK_BOND_CASHFLOW_INCOMPLETE"


class RiskBondYieldSolverFailedError(RiskError):
    """Yield-to-maturity numerical solver failed to converge."""
    status_code: int = 400
    code: str = "RISK_BOND_YIELD_SOLVER_FAILED"


class RiskBondCleanPriceNonPositiveError(RiskError):
    """Bond clean price must be strictly positive."""
    status_code: int = 400
    code: str = "RISK_BOND_CLEAN_PRICE_NON_POSITIVE"


class RiskBondDirtyPriceNonPositiveError(RiskError):
    """Bond dirty price must be strictly positive."""
    status_code: int = 400
    code: str = "RISK_BOND_DIRTY_PRICE_NON_POSITIVE"


class RiskBondMaturityBeforeSettlementError(RiskError):
    """Bond maturity date must be after settlement date."""
    status_code: int = 400
    code: str = "RISK_BOND_MATURITY_BEFORE_SETTLEMENT"


class RiskBondCouponFrequencyInvalidError(RiskError):
    """Bond coupon frequency must be one of ANNUAL, SEMI_ANNUAL, QUARTERLY, MONTHLY."""
    status_code: int = 400
    code: str = "RISK_BOND_COUPON_FREQUENCY_INVALID"


class RiskBondDayCountConventionUnsupportedError(RiskError):
    """Requested day count convention is not supported."""
    status_code: int = 400
    code: str = "RISK_BOND_DAY_COUNT_CONVENTION_UNSUPPORTED"


class RiskBondFaceValueNonPositiveError(RiskError):
    """Bond face value must be strictly positive."""
    status_code: int = 400
    code: str = "RISK_BOND_FACE_VALUE_NON_POSITIVE"


class RiskBondKeyRateTenorInvalidError(RiskError):
    """Key rate tenor schedule is invalid or out of bounds."""
    status_code: int = 400
    code: str = "RISK_BOND_KEY_RATE_TENOR_INVALID"


class RiskBondCurveMissingError(RiskError):
    """Required benchmark or discount yield curve was not found."""
    status_code: int = 404
    code: str = "RISK_BOND_CURVE_MISSING"


class RiskBondCurveInsufficientPointsError(RiskError):
    """Yield curve definition must contain at least 2 tenor points."""
    status_code: int = 400
    code: str = "RISK_BOND_CURVE_INSUFFICIENT_POINTS"


class RiskBondSensitivitiesUnavailableError(RiskError):
    """Bond sensitivities (duration/convexity/DV01) could not be computed."""
    status_code: int = 400
    code: str = "RISK_BOND_SENSITIVITIES_UNAVAILABLE"


class RiskStage118SourceRestrictedError(RiskError):
    """Access to proprietary derivatives or bond pricing feeds is restricted."""
    status_code: int = 403
    code: str = "RISK_STAGE118_SOURCE_RESTRICTED"

