"""ATLAS Financial Risk Foundation — Enums (Stage 115).

Controlled vocabularies for institutional market-risk measurement,
metric types, estimation models, annualization policies, and calculation statuses.
"""

from enum import Enum


class RiskSubjectType(str, Enum):
    """Scope of the risk measurement."""
    PORTFOLIO = "PORTFOLIO"
    ACCOUNT = "ACCOUNT"
    INSTRUMENT = "INSTRUMENT"


class RiskMetricCode(str, Enum):
    """Canonical risk metric codes."""
    HISTORICAL_REALIZED_VOLATILITY = "HISTORICAL_REALIZED_VOLATILITY"
    HISTORICAL_RETURN_VARIANCE = "HISTORICAL_RETURN_VARIANCE"
    ROLLING_REALIZED_VOLATILITY = "ROLLING_REALIZED_VOLATILITY"
    HISTORICAL_MAX_DRAWDOWN = "HISTORICAL_MAX_DRAWDOWN"
    CURRENT_DRAWDOWN = "CURRENT_DRAWDOWN"
    DRAWDOWN_DURATION = "DRAWDOWN_DURATION"
    BENCHMARK_BETA = "BENCHMARK_BETA"
    BENCHMARK_CORRELATION = "BENCHMARK_CORRELATION"
    HISTORICAL_TRACKING_ERROR = "HISTORICAL_TRACKING_ERROR"
    MODEL_ESTIMATED_PORTFOLIO_VOLATILITY = "MODEL_ESTIMATED_PORTFOLIO_VOLATILITY"
    MODEL_ESTIMATED_PORTFOLIO_VARIANCE = "MODEL_ESTIMATED_PORTFOLIO_VARIANCE"
    MODEL_VOLATILITY_CONTRIBUTION = "MODEL_VOLATILITY_CONTRIBUTION"
    MODEL_VARIANCE_CONTRIBUTION = "MODEL_VARIANCE_CONTRIBUTION"
    DIVERSIFICATION_RATIO = "DIVERSIFICATION_RATIO"


class RiskModelType(str, Enum):
    """Underlying risk calculation methodologies."""
    HISTORICAL_RETURN_STATISTICS = "HISTORICAL_RETURN_STATISTICS"
    HISTORICAL_DRAWDOWN = "HISTORICAL_DRAWDOWN"
    BENCHMARK_SENSITIVITY = "BENCHMARK_SENSITIVITY"
    COVARIANCE_BASED_PORTFOLIO_RISK = "COVARIANCE_BASED_PORTFOLIO_RISK"


class RiskCalculationStatus(str, Enum):
    """Lifecycle status of a risk run."""
    QUEUED = "QUEUED"
    PREPARING = "PREPARING"
    VALIDATING = "VALIDATING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    INCOMPLETE = "INCOMPLETE"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class RiskMetricStatus(str, Enum):
    """Operational status of an individual calculated metric."""
    AVAILABLE = "AVAILABLE"
    AVAILABLE_WITH_WARNINGS = "AVAILABLE_WITH_WARNINGS"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    MISSING_PRICE_DATA = "MISSING_PRICE_DATA"
    MISSING_FX_DATA = "MISSING_FX_DATA"
    MISSING_BENCHMARK_DATA = "MISSING_BENCHMARK_DATA"
    INVALID_NUMERICAL_DOMAIN = "INVALID_NUMERICAL_DOMAIN"
    UNSUPPORTED_INSTRUMENT = "UNSUPPORTED_INSTRUMENT"
    SOURCE_RESTRICTED = "SOURCE_RESTRICTED"
    UNAVAILABLE = "UNAVAILABLE"


class RiskReturnFrequency(str, Enum):
    """Sampling frequency for return observations."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class AnnualizationPolicy(str, Enum):
    """Policy for square-root-of-time scaling convention."""
    DAYS_252 = "DAYS_252"      # sqrt(252)
    DAYS_260 = "DAYS_260"      # sqrt(260)
    WEEKS_52 = "WEEKS_52"      # sqrt(52)
    MONTHS_12 = "MONTHS_12"    # sqrt(12)
    NONE = "NONE"              # sqrt(1) = 1.0


class DataCoverageStatus(str, Enum):
    """Completeness rating for observation input data."""
    FULL_COVERAGE = "FULL_COVERAGE"
    PARTIAL_COVERAGE = "PARTIAL_COVERAGE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    MISSING_DATA = "MISSING_DATA"


class ReturnBasis(str, Enum):
    """Return computation basis."""
    TOTAL_RETURN = "TOTAL_RETURN"
    PRICE_RETURN = "PRICE_RETURN"


class DrawdownEpisodeStatus(str, Enum):
    """Drawdown episode recovery state."""
    RECOVERED = "RECOVERED"
    ONGOING = "ONGOING"

