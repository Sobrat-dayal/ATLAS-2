"""ATLAS Portfolios V1 — Performance Attribution Errors (Stage 113).

Typed domain exceptions mapping to HTTP status codes for the Attribution platform.
"""

from typing import Optional


class PortfolioAttributionError(Exception):
    """Base exception for all portfolio attribution errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class PortfolioAttributionNotFoundError(PortfolioAttributionError):
    """Raised when an attribution run or snapshot is not found."""
    def __init__(self, message: str = "Attribution run not found"):
        super().__init__(message, status_code=404)


class PortfolioAttributionAccessDeniedError(PortfolioAttributionError):
    """Raised when a user lacks access to the target portfolio's attribution."""
    def __init__(self, message: str = "Access to portfolio attribution denied"):
        super().__init__(message, status_code=403)


class PortfolioAttributionBenchmarkNotFoundError(PortfolioAttributionError):
    """Raised when a requested benchmark does not exist in the registry."""
    def __init__(self, message: str = "Benchmark not found in registry"):
        super().__init__(message, status_code=404)


class PortfolioAttributionBenchmarkConstituentsMissingError(PortfolioAttributionError):
    """Raised when holdings-based attribution is requested but benchmark constituents are unavailable."""
    def __init__(self, message: str = "Benchmark constituent snapshots missing for requested period"):
        super().__init__(message, status_code=422)


class PortfolioAttributionPeriodInvalidError(PortfolioAttributionError):
    """Raised when the specified attribution period is invalid or inverted."""
    def __init__(self, message: str = "Invalid attribution period specified"):
        super().__init__(message, status_code=422)


class PortfolioAttributionCurrencyMismatchError(PortfolioAttributionError):
    """Raised when portfolio and benchmark reporting currencies are incompatible without FX conversion."""
    def __init__(self, message: str = "Portfolio and benchmark currencies mismatch"):
        super().__init__(message, status_code=422)


class PortfolioAttributionClassificationMissingError(PortfolioAttributionError):
    """Raised when required sector/industry classifications cannot be resolved."""
    def __init__(self, message: str = "Classification missing for one or more portfolio holdings"):
        super().__init__(message, status_code=422)


class PortfolioAttributionMethodUnsupportedError(PortfolioAttributionError):
    """Raised when an unapproved attribution methodology is requested."""
    def __init__(self, message: str = "Unsupported attribution methodology requested"):
        super().__init__(message, status_code=400)


class PortfolioAttributionReconciliationFailedError(PortfolioAttributionError):
    """Raised when mathematical reconciliation residual exceeds configured tolerance."""
    def __init__(self, message: str = "Attribution mathematical reconciliation failed"):
        super().__init__(message, status_code=422)


class PortfolioAttributionMultiPeriodLinkingError(PortfolioAttributionError):
    """Raised when logarithmic linking fails due to non-positive gross returns."""
    def __init__(self, message: str = "Multi-period linking invalid (non-positive gross returns)"):
        super().__init__(message, status_code=422)

