"""Domain Exceptions for Global Economic Calendar (Stage 92)."""

from typing import Optional


class EconomicCalendarError(Exception):
    """Base exception for economic calendar domain."""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.code = code or "ECONOMIC_CALENDAR_ERROR"


class EconomicEventNotFoundError(EconomicCalendarError):
    """Raised when an economic calendar event cannot be resolved."""
    def __init__(self, event_id: str):
        super().__init__(
            f"Economic calendar event with identifier '{event_id}' not found.",
            code="ECONOMIC_EVENT_NOT_FOUND",
        )
        self.event_id = event_id


class EconomicEventScheduleUnavailableError(EconomicCalendarError):
    """Raised when an official release schedule is unavailable or unverified."""
    def __init__(self, message: str):
        super().__init__(message, code="ECONOMIC_EVENT_SCHEDULE_UNAVAILABLE")


class EconomicEventForecastUnavailableError(EconomicCalendarError):
    """Raised when an authorized consensus forecast snapshot does not exist."""
    def __init__(self, message: str):
        super().__init__(message, code="ECONOMIC_EVENT_FORECAST_UNAVAILABLE")


class EconomicEventIncompatibleForecastError(EconomicCalendarError):
    """Raised when forecast and actual observations have incompatible units or adjustments."""
    def __init__(self, message: str):
        super().__init__(message, code="ECONOMIC_EVENT_FORECAST_INCOMPATIBLE")


class EconomicEventAlertNotFoundError(EconomicCalendarError):
    """Raised when an event alert cannot be found or is not owned by user."""
    def __init__(self, alert_id: str):
        super().__init__(
            f"Economic event alert with identifier '{alert_id}' not found.",
            code="ECONOMIC_EVENT_ALERT_NOT_FOUND",
        )
        self.alert_id = alert_id


class EconomicEventAlertQuotaExceededError(EconomicCalendarError):
    """Raised when user exceeds active alert limits."""
    def __init__(self, max_quota: int):
        super().__init__(
            f"User active alert quota of {max_quota} exceeded.",
            code="ECONOMIC_EVENT_ALERT_QUOTA_EXCEEDED",
        )


class EconomicEventTimezoneInvalidError(EconomicCalendarError):
    """Raised when an unrecognized IANA timezone is requested."""
    def __init__(self, tz_name: str):
        super().__init__(
            f"Timezone '{tz_name}' is not a valid IANA timezone.",
            code="ECONOMIC_EVENT_TIMEZONE_INVALID",
        )
        self.tz_name = tz_name


class EconomicEventDateRangeInvalidError(EconomicCalendarError):
    """Raised when date window range parameters are invalid."""
    def __init__(self, message: str):
        super().__init__(message, code="ECONOMIC_EVENT_DATE_RANGE_INVALID")
