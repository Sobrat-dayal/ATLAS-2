"""Typed Domain Exceptions for Financial Screeners V1 (Stage 94)."""

from typing import Optional


class ScreenerError(Exception):
    """Base exception for all financial screener errors."""

    def __init__(self, message: str, code: str = "SCREENER_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class ScreenerUniverseNotFoundError(ScreenerError):
    def __init__(self, universe_id: str):
        super().__init__(
            f"Screener universe '{universe_id}' was not found in catalog.",
            code="SCREENER_UNIVERSE_NOT_FOUND",
            status_code=404,
        )


class ScreenerUniverseUnsupportedError(ScreenerError):
    def __init__(self, reason: str):
        super().__init__(
            f"Universe selection is unsupported: {reason}",
            code="SCREENER_UNIVERSE_UNSUPPORTED",
            status_code=400,
        )


class ScreenerFilterNotFoundError(ScreenerError):
    def __init__(self, filter_id: str):
        super().__init__(
            f"Filter '{filter_id}' is not recognized in the approved filter registry.",
            code="SCREENER_FILTER_NOT_FOUND",
            status_code=400,
        )


class ScreenerOperatorNotSupportedError(ScreenerError):
    def __init__(self, filter_id: str, operator: str):
        super().__init__(
            f"Operator '{operator}' is not supported for filter '{filter_id}'.",
            code="SCREENER_OPERATOR_NOT_SUPPORTED",
            status_code=400,
        )


class ScreenerValueTypeInvalidError(ScreenerError):
    def __init__(self, filter_id: str, message: str):
        super().__init__(
            f"Invalid value type for filter '{filter_id}': {message}",
            code="SCREENER_VALUE_TYPE_INVALID",
            status_code=400,
        )


class ScreenerRangeInvalidError(ScreenerError):
    def __init__(self, filter_id: str, min_val: Optional[str] = None, max_val: Optional[str] = None):
        super().__init__(
            f"Invalid range for filter '{filter_id}': lower bound ({min_val}) must be <= upper bound ({max_val}).",
            code="SCREENER_RANGE_INVALID",
            status_code=400,
        )


class ScreenerUnitIncompatibleError(ScreenerError):
    def __init__(self, filter_id: str, expected: str, actual: str):
        super().__init__(
            f"Incompatible unit for filter '{filter_id}': expected '{expected}', got '{actual}'.",
            code="SCREENER_UNIT_INCOMPATIBLE",
            status_code=400,
        )


class ScreenerCurrencyPolicyUnavailableError(ScreenerError):
    def __init__(self, message: str):
        super().__init__(
            f"Currency normalization or policy is unavailable: {message}",
            code="SCREENER_CURRENCY_POLICY_UNAVAILABLE",
            status_code=400,
        )


class ScreenerMetricUnavailableError(ScreenerError):
    def __init__(self, metric_id: str):
        super().__init__(
            f"Financial metric '{metric_id}' is unavailable for the selected universe.",
            code="SCREENER_METRIC_UNAVAILABLE",
            status_code=400,
        )


class ScreenerMetricInapplicableError(ScreenerError):
    def __init__(self, metric_id: str, instrument_type: str):
        super().__init__(
            f"Financial metric '{metric_id}' is inapplicable to security type '{instrument_type}'.",
            code="SCREENER_METRIC_INAPPLICABLE",
            status_code=400,
        )


class ScreenerFinancialPeriodInvalidError(ScreenerError):
    def __init__(self, period: str):
        super().__init__(
            f"Requested financial reporting period '{period}' is invalid or unsupported.",
            code="SCREENER_FINANCIAL_PERIOD_INVALID",
            status_code=400,
        )


class ScreenerSourceUnavailableError(ScreenerError):
    def __init__(self, source_name: str):
        super().__init__(
            f"Financial data provider '{source_name}' is currently unavailable.",
            code="SCREENER_SOURCE_UNAVAILABLE",
            status_code=503,
        )


class ScreenerQuoteStaleError(ScreenerError):
    def __init__(self, symbol: str, quote_age_seconds: int):
        super().__init__(
            f"Quote for '{symbol}' is stale ({quote_age_seconds}s old) and does not meet strict freshness requirements.",
            code="SCREENER_QUOTE_STALE",
            status_code=400,
        )


class ScreenerFilterNotEntitledError(ScreenerError):
    def __init__(self, filter_id: str):
        super().__init__(
            f"Current user session is not entitled to filter on metric '{filter_id}'.",
            code="SCREENER_FILTER_NOT_ENTITLED",
            status_code=403,
        )


class ScreenerColumnNotEntitledError(ScreenerError):
    def __init__(self, column_id: str):
        super().__init__(
            f"Current user session is not entitled to display column '{column_id}'.",
            code="SCREENER_COLUMN_NOT_ENTITLED",
            status_code=403,
        )


class ScreenerQueryTooComplexError(ScreenerError):
    def __init__(self, message: str):
        super().__init__(
            f"Screener query exceeds complexity budget: {message}",
            code="SCREENER_QUERY_TOO_COMPLEX",
            status_code=400,
        )


class ScreenerQueryLimitExceededError(ScreenerError):
    def __init__(self, limit: int, actual: int):
        super().__init__(
            f"Active filter count ({actual}) exceeds maximum allowed limit ({limit}).",
            code="SCREENER_QUERY_LIMIT_EXCEEDED",
            status_code=400,
        )


class ScreenerSortUnsupportedError(ScreenerError):
    def __init__(self, field_id: str):
        super().__init__(
            f"Field '{field_id}' cannot be used for sorting.",
            code="SCREENER_SORT_UNSUPPORTED",
            status_code=400,
        )


class ScreenerCursorInvalidError(ScreenerError):
    def __init__(self, message: str = "Invalid or expired pagination cursor."):
        super().__init__(
            message,
            code="SCREENER_CURSOR_INVALID",
            status_code=400,
        )
