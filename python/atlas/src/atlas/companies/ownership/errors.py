"""Typed domain errors for Company Ownership Intelligence (Stage 85)."""


class OwnershipError(Exception):
    """Base exception for all ownership domain errors."""
    pass


class OwnershipDataUnavailableError(OwnershipError):
    """Raised when ownership data for a company or security is not available."""
    def __init__(self, identifier: str, reason: str = "No verified ownership disclosures available."):
        super().__init__(f"Ownership data for '{identifier}' is unavailable: {reason}")
        self.identifier = identifier
        self.reason = reason


class OwnershipSecurityNotFoundError(OwnershipError):
    """Raised when a specific security or share class cannot be resolved for the issuer."""
    def __init__(self, security_id: str, company_id: str):
        super().__init__(f"Security '{security_id}' was not found or is not issued by company '{company_id}'.")
        self.security_id = security_id
        self.company_id = company_id


class OwnershipHolderNotFoundError(OwnershipError):
    """Raised when a holder entity cannot be found or resolved."""
    def __init__(self, holder_id: str):
        super().__init__(f"Shareholder entity '{holder_id}' not found.")
        self.holder_id = holder_id


class IncompatibleDenominatorError(OwnershipError):
    """Raised when an ownership percentage cannot be calculated due to a missing or incompatible shares denominator."""
    def __init__(self, message: str):
        super().__init__(message)


class DoubleCountingConflictError(OwnershipError):
    """Raised when aggregating overlapping positions (e.g. fund manager and underlying fund)."""
    def __init__(self, message: str):
        super().__init__(message)


class OwnershipPeriodUnavailableError(OwnershipError):
    """Raised when ownership data for a requested reporting period is not available."""
    def __init__(self, reporting_period: str):
        super().__init__(f"Ownership snapshot for reporting period '{reporting_period}' is unavailable.")
        self.reporting_period = reporting_period


class OwnershipEntitlementDeniedError(OwnershipError):
    """Raised when the user lacks required source entitlement to access ownership records."""
    def __init__(self, source_type: str):
        super().__init__(f"User lacks required entitlement to access '{source_type}' ownership data.")
        self.source_type = source_type
