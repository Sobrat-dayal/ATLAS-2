"""Domain errors for the Financial and Economic Exposure Engine (Stage 137).

Strict failure modes enforcing financial invariants:
- Prohibited inference (e.g. revenue from facility counts, proximity as loss)
- Non-matching accounting periods or missing denominators
- Missing point-in-time FX rates (no arbitrary substitution)
- Look-ahead bias violations
- Tenant privacy boundary violations
- Nested fund cyclic references
- Double counting of consolidated subsidiaries
- Revoked source entitlements
"""

from __future__ import annotations
from typing import Optional


class ExposureDomainError(Exception):
    """Base domain error for exposure operations."""
    def __init__(self, message: str, code: str = "EXPOSURE_ERROR", details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class InvalidDenominatorError(ExposureDomainError):
    """Raised when an exposure percentage calculation lacks a verified non-zero denominator."""
    def __init__(self, message: str = "Calculation requires a verified non-zero denominator.", details: Optional[dict] = None):
        super().__init__(message, code="INVALID_DENOMINATOR", details=details)


class IncompatiblePeriodError(ExposureDomainError):
    """Raised when attempting to calculate ratios across non-comparable accounting periods."""
    def __init__(self, message: str = "Cannot compare metrics across incompatible reporting periods.", details: Optional[dict] = None):
        super().__init__(message, code="INCOMPATIBLE_PERIOD", details=details)


class MissingCurrencyRateError(ExposureDomainError):
    """Raised when point-in-time FX rates are missing. Substituting current rates is strictly prohibited."""
    def __init__(self, from_currency: str, to_currency: str, as_of: str, details: Optional[dict] = None):
        msg = f"Historical FX rate for {from_currency}/{to_currency} as-of {as_of} is unavailable."
        super().__init__(msg, code="MISSING_FX_RATE", details=details or {"from": from_currency, "to": to_currency, "as_of": as_of})


class CurrencyMismatchError(ExposureDomainError):
    """Raised when arithmetic is attempted across distinct currencies without conversion."""
    def __init__(self, message: str = "Currencies must match or be explicitly converted.", details: Optional[dict] = None):
        super().__init__(message, code="CURRENCY_MISMATCH", details=details)


class DoubleCountingError(ExposureDomainError):
    """Raised when an operation would double-count consolidated parent and subsidiary revenues."""
    def __init__(self, message: str = "Double-counting consolidated parent and subsidiary revenue is prohibited.", details: Optional[dict] = None):
        super().__init__(message, code="DOUBLE_COUNTING_DETECTED", details=details)


class ProhibitedInferenceError(ExposureDomainError):
    """Raised when an operation attempts to fabricate financial percentages from operational counts or proximity."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, code="PROHIBITED_INFERENCE", details=details)


class LookAheadViolationError(ExposureDomainError):
    """Raised when a query as-of timestamp attempts to access data published or known after that timestamp."""
    def __init__(self, message: str = "Query violates bitemporal point-in-time integrity (look-ahead bias).", details: Optional[dict] = None):
        super().__init__(message, code="LOOK_AHEAD_VIOLATION", details=details)


class TenantExposureAccessDeniedError(ExposureDomainError):
    """Raised when accessing proprietary portfolio or exposure data across tenant boundaries."""
    def __init__(self, message: str = "Access denied: proprietary exposure data cannot cross tenant boundaries.", details: Optional[dict] = None):
        super().__init__(message, code="TENANT_ACCESS_DENIED", details=details)


class MethodNotAllowedError(ExposureDomainError):
    """Raised when an unapproved derivation method is requested for an exposure measure."""
    def __init__(self, message: str = "Requested calculation method is not authorized for this exposure measure.", details: Optional[dict] = None):
        super().__init__(message, code="METHOD_NOT_ALLOWED", details=details)


class CycleDetectedError(ExposureDomainError):
    """Raised when nested fund look-through encounters a cyclical reference."""
    def __init__(self, cycle_path: list, message: str = "Cyclical holding detected during fund look-through traversal."):
        super().__init__(message, code="CYCLE_DETECTED", details={"cycle_path": cycle_path})
        self.cycle_path = cycle_path


class SourceLicenseRevokedError(ExposureDomainError):
    """Raised when underlying source license or user entitlement has expired or been revoked."""
    def __init__(self, source_id: str, message: str = "Underlying source entitlement has been revoked or expired."):
        super().__init__(message, code="SOURCE_ENTITLEMENT_REVOKED", details={"source_id": source_id})
        self.source_id = source_id
