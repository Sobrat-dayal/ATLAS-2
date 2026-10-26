"""Typed domain errors for Company Earnings Intelligence (Stage 84)."""


class EarningsError(Exception):
    """Base exception for all earnings domain errors."""
    pass


class EarningsEventNotFoundError(EarningsError):
    """Raised when an earnings event cannot be found."""
    def __init__(self, event_id: str):
        super().__init__(f"Earnings event '{event_id}' not found.")
        self.event_id = event_id


class EarningsPeriodUnavailableError(EarningsError):
    """Raised when earnings data for a requested fiscal period is not available."""
    def __init__(self, fiscal_period: str):
        super().__init__(f"Earnings data for fiscal period '{fiscal_period}' is unavailable.")
        self.fiscal_period = fiscal_period


class IncompatibleEarningsBasisError(EarningsError):
    """Raised when attempting to compare actual and consensus with incompatible accounting or per-share bases."""
    def __init__(self, message: str):
        super().__init__(message)


class EstimateVintageUnavailableError(EarningsError):
    """Raised when pre-release analyst estimate vintage cannot be established."""
    def __init__(self, fiscal_period: str):
        super().__init__(f"Pre-release consensus estimate vintage for '{fiscal_period}' is unavailable.")
        self.fiscal_period = fiscal_period


class TranscriptNotEntitledError(EarningsError):
    """Raised when user lacks required entitlement to access full transcript text."""
    def __init__(self, document_id: str):
        super().__init__(f"User is not entitled to access transcript document '{document_id}'.")
        self.document_id = document_id
