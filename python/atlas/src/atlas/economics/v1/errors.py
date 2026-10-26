"""Domain Exceptions for Institutional Economics V1 (Stage 89)."""


class EconomicsV1Error(Exception):
    """Base exception for Economics V1 domain operations."""

    def __init__(self, message: str, code: str = "ECONOMICS_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class EconomicIndicatorNotFoundError(EconomicsV1Error):
    """Raised when an economic indicator cannot be resolved."""

    def __init__(self, indicator_id: str):
        super().__init__(
            f"Economic indicator '{indicator_id}' not found in canonical catalog.",
            code="ECONOMIC_INDICATOR_NOT_FOUND",
        )


class EconomicSeriesNotFoundError(EconomicsV1Error):
    """Raised when an economic series cannot be resolved."""

    def __init__(self, series_id: str):
        super().__init__(
            f"Economic series '{series_id}' not found.",
            code="ECONOMIC_SERIES_NOT_FOUND",
        )


class EconomicGeographyNotFoundError(EconomicsV1Error):
    """Raised when a country or economic area is not supported."""

    def __init__(self, geography_id: str):
        super().__init__(
            f"Geographic entity '{geography_id}' not supported in economics coverage.",
            code="ECONOMIC_GEOGRAPHY_NOT_SUPPORTED",
        )


class EconomicTransformationUnsupportedError(EconomicsV1Error):
    """Raised when a statistical transformation is invalid for a series frequency or unit."""

    def __init__(self, message: str):
        super().__init__(message, code="ECONOMIC_TRANSFORMATION_UNSUPPORTED")


class EconomicPeriodInvalidError(EconomicsV1Error):
    """Raised when a date range or period alignment is mathematically invalid."""

    def __init__(self, message: str):
        super().__init__(message, code="ECONOMIC_PERIOD_INVALID")


class EconomicCalculationError(EconomicsV1Error):
    """Raised when a statistical calculation fails (e.g., zero denominator)."""

    def __init__(self, message: str):
        super().__init__(message, code="ECONOMIC_CALCULATION_ERROR")
