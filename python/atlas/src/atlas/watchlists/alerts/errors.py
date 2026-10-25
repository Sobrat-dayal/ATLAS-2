"""Typed exceptions for Watchlist Alerts V1 (Stage 80)."""


class WatchlistAlertError(Exception):
    """Base exception for all Watchlist Alert errors."""

    def __init__(self, message: str, code: str = "ALERT_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class AlertNotFoundError(WatchlistAlertError):
    """Raised when an alert rule is not found or not owned by user."""

    def __init__(self, message: str = "Alert rule not found.") -> None:
        super().__init__(message, code="ALERT_NOT_FOUND")


class AlertLimitExceededError(WatchlistAlertError):
    """Raised when user exceeds active alert quotas."""

    def __init__(self, message: str = "Maximum active alerts quota exceeded.") -> None:
        super().__init__(message, code="ALERT_LIMIT_EXCEEDED")


class InvalidAlertConditionError(WatchlistAlertError):
    """Raised when condition or comparator is invalid."""

    def __init__(self, message: str = "Invalid alert condition.") -> None:
        super().__init__(message, code="INVALID_ALERT_CONDITION")


class InvalidThresholdUnitError(WatchlistAlertError):
    """Raised when threshold unit or currency does not match instrument."""

    def __init__(self, message: str = "Invalid threshold unit or currency.") -> None:
        super().__init__(message, code="INVALID_THRESHOLD_UNIT")


class IncompatibleQuoteMeasureError(WatchlistAlertError):
    """Raised when selected quote measure is incompatible with instrument asset class."""

    def __init__(self, message: str = "Incompatible quote measure for instrument.") -> None:
        super().__init__(message, code="INCOMPATIBLE_QUOTE_MEASURE")


class IncompatibleReferenceMethodError(WatchlistAlertError):
    """Raised when reference methodology is invalid or missing."""

    def __init__(self, message: str = "Incompatible reference price methodology.") -> None:
        super().__init__(message, code="INCOMPATIBLE_REFERENCE_METHOD")


class AlertDataUnavailableError(WatchlistAlertError):
    """Raised when required market observation data is unavailable."""

    def __init__(self, message: str = "Market data currently unavailable for evaluation.") -> None:
        super().__init__(message, code="ALERT_DATA_UNAVAILABLE")


class AlertNotEntitledError(WatchlistAlertError):
    """Raised when user lacks subscription entitlement for the feed."""

    def __init__(self, message: str = "User is not entitled to market data for this alert.") -> None:
        super().__init__(message, code="ALERT_NOT_ENTITLED")


class InvalidExpirationError(WatchlistAlertError):
    """Raised when expiration date is invalid or in the past."""

    def __init__(self, message: str = "Expiration timestamp must be in the future.") -> None:
        super().__init__(message, code="INVALID_EXPIRATION")


class InvalidCooldownError(WatchlistAlertError):
    """Raised when cooldown interval is invalid."""

    def __init__(self, message: str = "Invalid cooldown interval.") -> None:
        super().__init__(message, code="INVALID_COOLDOWN")


class AlertRevisionConflictError(WatchlistAlertError):
    """Raised when optimistic concurrency revision conflict occurs."""

    def __init__(self, message: str = "Alert rule revision conflict. Please reload.") -> None:
        super().__init__(message, code="ALERT_REVISION_CONFLICT")


class AlertEvaluationUnavailableError(WatchlistAlertError):
    """Raised when evaluation worker is offline or degraded."""

    def __init__(self, message: str = "Server-side alert evaluation is temporarily unavailable.") -> None:
        super().__init__(message, code="ALERT_EVALUATION_UNAVAILABLE")


class UnsupportedAlertTypeError(WatchlistAlertError):
    """Raised when rule type is unsupported."""

    def __init__(self, message: str = "Unsupported alert condition type.") -> None:
        super().__init__(message, code="UNSUPPORTED_ALERT_TYPE")


class WatchlistItemNotFoundError(WatchlistAlertError):
    """Raised when referenced watchlist item does not exist or belong to user."""

    def __init__(self, message: str = "Watchlist item not found.") -> None:
        super().__init__(message, code="WATCHLIST_ITEM_NOT_FOUND")
