"""ATLAS Maps Live Physical-World Exceptions and Error Hierarchy (Stage 134)."""

from typing import Optional


class LiveDomainError(Exception):
    """Base error for all live physical-world geospatial operations."""
    def __init__(self, message: str, code: str = "LIVE_DOMAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class LiveProviderNotConfiguredError(LiveDomainError):
    """Raised when an authorized data provider is requested but lacks required configuration or API keys."""
    def __init__(self, provider_id: str, reason: str = "Provider API keys or credentials not configured"):
        super().__init__(f"Provider '{provider_id}' is not configured: {reason}", code="PROVIDER_NOT_CONFIGURED")
        self.provider_id = provider_id
        self.reason = reason


class LiveProviderAccessDeniedError(LiveDomainError):
    """Raised when user or client lacks entitlement to the requested provider feed."""
    def __init__(self, provider_id: str, required_tier: str = "INSTITUTIONAL"):
        super().__init__(
            f"Access denied for provider '{provider_id}'. Requires {required_tier} license tier.",
            code="PROVIDER_ACCESS_DENIED"
        )
        self.provider_id = provider_id
        self.required_tier = required_tier


class LiveProviderUnavailableError(LiveDomainError):
    """Raised when an upstream live provider is offline or unreachable."""
    def __init__(self, provider_id: str, details: str = "Upstream service unreachable"):
        super().__init__(f"Provider '{provider_id}' is currently unavailable: {details}", code="PROVIDER_UNAVAILABLE")
        self.provider_id = provider_id
        self.details = details


class LiveObservationTooOldError(LiveDomainError):
    """Raised when an observation exceeds expiration thresholds."""
    def __init__(self, observation_id: str, age_seconds: float, max_age_seconds: float):
        super().__init__(
            f"Observation '{observation_id}' age ({age_seconds:.1f}s) exceeds max threshold ({max_age_seconds:.1f}s)",
            code="OBSERVATION_EXPIRED"
        )
        self.observation_id = observation_id
        self.age_seconds = age_seconds
        self.max_age_seconds = max_age_seconds


class LiveEventNotFoundError(LiveDomainError):
    """Raised when a specific event or observation cannot be found."""
    def __init__(self, entity_id: str):
        super().__init__(f"Live physical event or entity '{entity_id}' not found", code="EVENT_NOT_FOUND")
        self.entity_id = entity_id


class LiveOrbitPropagationFailedError(LiveDomainError):
    """Raised when SGP4 orbital propagation fails mathematically."""
    def __init__(self, norad_id: int, reason: str):
        super().__init__(f"Orbital propagation failed for satellite {norad_id}: {reason}", code="ORBIT_PROPAGATION_FAILED")
        self.norad_id = norad_id
        self.reason = reason


class LiveStaleOrbitElementsError(LiveDomainError):
    """Raised when satellite TLE / OMM orbital epoch is older than allowed threshold (>14-30 days)."""
    def __init__(self, norad_id: int, epoch_age_days: float, max_days: float = 14.0):
        super().__init__(
            f"Satellite {norad_id} orbital elements epoch is {epoch_age_days:.1f} days old (exceeds {max_days:.1f} days). "
            "Orbital position error degrades by tens of kilometers per day; fresh ephemeris required.",
            code="STALE_ORBITAL_EPOCH"
        )
        self.norad_id = norad_id
        self.epoch_age_days = epoch_age_days
        self.max_days = max_days


class LiveHistoryNotLicensedError(LiveDomainError):
    """Raised when historical temporal playback exceeds authorized licensed retention window."""
    def __init__(self, requested_date: str, retention_days: int):
        super().__init__(
            f"Historical playback for date '{requested_date}' exceeds your account's {retention_days}-day live history window.",
            code="HISTORY_NOT_LICENSED"
        )
        self.requested_date = requested_date
        self.retention_days = retention_days


class LiveRateLimitExceededError(LiveDomainError):
    """Raised when downstream requests exceed provider rate limits."""
    def __init__(self, provider_id: str, retry_after_seconds: int = 60):
        super().__init__(
            f"Rate limit exceeded for provider '{provider_id}'. Retry after {retry_after_seconds}s.",
            code="RATE_LIMIT_EXCEEDED"
        )
        self.provider_id = provider_id
        self.retry_after_seconds = retry_after_seconds


class LiveCoordinatesInvalidError(LiveDomainError):
    """Raised when latitude or longitude are outside valid WGS84 bounds."""
    def __init__(self, lat: float, lon: float):
        super().__init__(f"Invalid coordinates: lat={lat}, lon={lon}. Lat must be [-90, 90], Lon must be [-180, 180].", code="INVALID_COORDINATES")
        self.lat = lat
        self.lon = lon


class LiveViewportTooLargeError(LiveDomainError):
    """Raised when a live observation bounding box query exceeds maximum allowed spatial area."""
    def __init__(self, area_deg2: float, max_area_deg2: float):
        super().__init__(
            f"Viewport query bounding box ({area_deg2:.2f} deg^2) exceeds maximum allowed ({max_area_deg2:.2f} deg^2). "
            "Please zoom in to inspect live observations.",
            code="VIEWPORT_TOO_LARGE"
        )
        self.area_deg2 = area_deg2
        self.max_area_deg2 = max_area_deg2
