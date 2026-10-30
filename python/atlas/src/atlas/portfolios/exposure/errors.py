"""ATLAS Portfolios V1 — Exposure & Allocation Domain Errors (Stage 112)."""

from typing import Optional


class PortfolioExposureError(Exception):
    """Base exception for all portfolio exposure and allocation operations."""

    def __init__(self, message: str, code: str = "PORTFOLIO_EXPOSURE_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class PortfolioExposureNotFoundError(PortfolioExposureError):
    def __init__(self, message: str = "Portfolio exposure run not found."):
        super().__init__(message, code="PORTFOLIO_EXPOSURE_NOT_FOUND", status_code=404)


class PortfolioExposureAccessDeniedError(PortfolioExposureError):
    def __init__(self, message: str = "Access to portfolio exposure run denied."):
        super().__init__(message, code="PORTFOLIO_EXPOSURE_ACCESS_DENIED", status_code=403)


class PortfolioExposureValuationUnavailableError(PortfolioExposureError):
    def __init__(self, message: str = "Portfolio valuation point is unavailable for the requested date."):
        super().__init__(message, code="PORTFOLIO_EXPOSURE_VALUATION_UNAVAILABLE", status_code=400)


class PortfolioExposureValuationIncompleteError(PortfolioExposureError):
    def __init__(self, message: str = "Portfolio valuation is incomplete; cannot compute verified weights."):
        super().__init__(message, code="PORTFOLIO_EXPOSURE_VALUATION_INCOMPLETE", status_code=400)


class PortfolioExposureNavInvalidError(PortfolioExposureError):
    def __init__(self, message: str = "Portfolio NAV denominator must be strictly positive for allocation weights."):
        super().__init__(message, code="PORTFOLIO_EXPOSURE_NAV_INVALID", status_code=400)


class PortfolioExposureTaxonomyUnsupportedError(PortfolioExposureError):
    def __init__(self, taxonomy: str):
        super().__init__(f"Taxonomy '{taxonomy}' is not supported.", code="PORTFOLIO_EXPOSURE_TAXONOMY_UNSUPPORTED", status_code=400)


class PortfolioExposureLookThroughError(PortfolioExposureError):
    def __init__(self, message: str, code: str = "PORTFOLIO_EXPOSURE_LOOKTHROUGH_ERROR", status_code: int = 400):
        super().__init__(message, code=code, status_code=status_code)


class PortfolioExposureLookThroughCycleError(PortfolioExposureLookThroughError):
    def __init__(self, fund_id: str):
        super().__init__(f"Circular reference cycle detected in nested fund look-through for {fund_id}.", code="PORTFOLIO_EXPOSURE_LOOKTHROUGH_CYCLE", status_code=400)


class PortfolioExposureLookThroughDepthExceededError(PortfolioExposureLookThroughError):
    def __init__(self, depth: int, max_depth: int):
        super().__init__(f"Look-through traversal depth {depth} exceeded max depth {max_depth}.", code="PORTFOLIO_EXPOSURE_LOOKTHROUGH_DEPTH_EXCEEDED", status_code=400)


class PortfolioExposureReconciliationFailedError(PortfolioExposureError):
    def __init__(self, message: str):
        super().__init__(message, code="PORTFOLIO_EXPOSURE_RECONCILIATION_FAILED", status_code=400)


class PortfolioExposureCurrencyMismatchError(PortfolioExposureError):
    def __init__(self, message: str):
        super().__init__(message, code="PORTFOLIO_EXPOSURE_CURRENCY_MISMATCH", status_code=400)


class PortfolioExposureDataQualityError(PortfolioExposureError):
    def __init__(self, message: str):
        super().__init__(message, code="PORTFOLIO_EXPOSURE_DATA_QUALITY_ERROR", status_code=400)


class PortfolioExposureUnknownInstrumentError(PortfolioExposureError):
    def __init__(self, instrument_id: str):
        super().__init__(f"Instrument '{instrument_id}' is unknown in classification registry.", code="PORTFOLIO_EXPOSURE_UNKNOWN_INSTRUMENT", status_code=400)
