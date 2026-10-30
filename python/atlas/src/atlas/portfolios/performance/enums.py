"""Performance calculation enums for ATLAS Portfolio Performance (Stage 111)."""

from enum import Enum


class PerformanceMethodology(str, Enum):
    """Supported portfolio return calculation methodologies."""
    TIME_WEIGHTED_RETURN = "TIME_WEIGHTED_RETURN"
    MONEY_WEIGHTED_RETURN = "MONEY_WEIGHTED_RETURN"
    MODIFIED_DIETZ = "MODIFIED_DIETZ"
    CUMULATIVE_RETURN = "CUMULATIVE_RETURN"
    ANNUALIZED_RETURN = "ANNUALIZED_RETURN"


class MeasurementScope(str, Enum):
    """Scope of portfolio performance measurement."""
    PORTFOLIO = "PORTFOLIO"
    ACCOUNT = "ACCOUNT"


class PerformancePeriodType(str, Enum):
    """Standard portfolio reporting periods."""
    ONE_DAY = "1D"
    WEEK_TO_DATE = "WTD"
    MONTH_TO_DATE = "MTD"
    QUARTER_TO_DATE = "QTD"
    YEAR_TO_DATE = "YTD"
    TRAILING_1M = "1M"
    TRAILING_3M = "3M"
    TRAILING_6M = "6M"
    TRAILING_1Y = "1Y"
    TRAILING_3Y = "3Y"
    TRAILING_5Y = "5Y"
    SINCE_INCEPTION = "INCEPTION"
    CUSTOM = "CUSTOM"


class CashFlowClassification(str, Enum):
    """Classification of cash movements relative to the portfolio boundary."""
    EXTERNAL_CONTRIBUTION = "EXTERNAL_CONTRIBUTION"
    EXTERNAL_WITHDRAWAL = "EXTERNAL_WITHDRAWAL"
    INTERNAL_SECURITY_TRADE = "INTERNAL_SECURITY_TRADE"
    INTERNAL_INCOME = "INTERNAL_INCOME"
    INTERNAL_FEE = "INTERNAL_FEE"
    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"
    CORPORATE_ACTION_NONCASH = "CORPORATE_ACTION_NONCASH"
    UNCLASSIFIED = "UNCLASSIFIED"


class PerformanceStatus(str, Enum):
    """Execution status of a performance calculation run."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    INCOMPLETE = "INCOMPLETE"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class DataCompletenessStatus(str, Enum):
    """Data completeness classification for performance calculation inputs."""
    COMPLETE = "COMPLETE"
    COMPLETE_WITH_STALE_MARKS = "COMPLETE_WITH_STALE_MARKS"
    PARTIAL_MISSING_MARKS = "PARTIAL_MISSING_MARKS"
    PARTIAL_MISSING_FX = "PARTIAL_MISSING_FX"
    PARTIAL_APPROXIMATE_TWR = "PARTIAL_APPROXIMATE_TWR"
    UNAVAILABLE = "UNAVAILABLE"


class BenchmarkReturnBasis(str, Enum):
    """Return basis for market index benchmarks."""
    PRICE_RETURN = "PRICE_RETURN"
    TOTAL_RETURN = "TOTAL_RETURN"


class FeeTreatmentPolicy(str, Enum):
    """Policy for handling custody and trading fees in performance returns."""
    NET_OF_FEES = "NET_OF_FEES"
    GROSS_OF_FEES = "GROSS_OF_FEES"


class IncomeTreatmentPolicy(str, Enum):
    """Policy for handling dividend and interest income."""
    INCLUDE_REINVESTED_AND_CASH = "INCLUDE_REINVESTED_AND_CASH"
    EXCLUDE_DIVIDENDS = "EXCLUDE_DIVIDENDS"

