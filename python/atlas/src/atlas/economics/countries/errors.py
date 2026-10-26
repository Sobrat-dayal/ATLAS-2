"""Domain exceptions for Country Economics Intelligence (Stage 90)."""


class CountryEconomicsError(Exception):
    """Base exception for Country Economics domain errors."""
    def __init__(self, message: str, code: str = "COUNTRY_ECONOMICS_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class CountryGeographyNotFoundError(CountryEconomicsError):
    """Raised when a requested country or economic area cannot be resolved."""
    def __init__(self, geography_id: str):
        super().__init__(
            f"Country or economic area '{geography_id}' not found in canonical geographic registry.",
            code="COUNTRY_GEOGRAPHY_NOT_FOUND",
        )
        self.geography_id = geography_id


class CountryIndicatorUnavailableError(CountryEconomicsError):
    """Raised when an indicator is unavailable for the selected country."""
    def __init__(self, geography_id: str, indicator_code: str):
        super().__init__(
            f"Indicator '{indicator_code}' is unavailable for country '{geography_id}'.",
            code="COUNTRY_INDICATOR_UNAVAILABLE",
        )
        self.geography_id = geography_id
        self.indicator_code = indicator_code


class CountryPeriodInvalidError(CountryEconomicsError):
    """Raised when a requested observation period or demographic alignment is invalid."""
    def __init__(self, message: str):
        super().__init__(message, code="COUNTRY_PERIOD_INVALID")


class CountryReconciliationError(CountryEconomicsError):
    """Raised when national accounts components or accounting identities cannot be reconciled."""
    def __init__(self, message: str):
        super().__init__(message, code="COUNTRY_RECONCILIATION_ERROR")
