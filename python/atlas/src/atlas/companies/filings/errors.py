"""Errors for Regulatory Company Filings Intelligence (Stage 86)."""


class FilingError(Exception):
    """Base exception for all filing-related operations."""

    def __init__(self, message: str, code: str = "FILING_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class FilingNotFoundError(FilingError):
    """Raised when a requested filing or accession number cannot be located."""

    def __init__(self, message: str = "Regulatory filing not found."):
        super().__init__(message, code="FILING_NOT_FOUND")


class FilingDocumentNotFoundError(FilingError):
    """Raised when a specific filing document or attachment cannot be found."""

    def __init__(self, message: str = "Filing document or exhibit not found."):
        super().__init__(message, code="FILING_DOCUMENT_UNAVAILABLE")


class FilingSourceUnavailableError(FilingError):
    """Raised when a regulatory provider/source is offline or unconfigured."""

    def __init__(self, message: str = "Regulatory source adapter is unavailable."):
        super().__init__(message, code="FILING_SOURCE_UNAVAILABLE")


class FilingAccessRestrictedError(FilingError):
    """Raised when access to a filing document requires elevated licensing/entitlement."""

    def __init__(self, message: str = "Filing document access is restricted."):
        super().__init__(message, code="FILING_ACCESS_RESTRICTED")


class FilingExtractionFailedError(FilingError):
    """Raised when text or XBRL extraction fails or is corrupt."""

    def __init__(self, message: str = "Failed to extract structured data from filing."):
        super().__init__(message, code="FILING_EXTRACTION_FAILED")


class FilingComparisonIncompatibleError(FilingError):
    """Raised when two filings are incompatible for structured comparison."""

    def __init__(self, message: str = "Filings are incompatible for comparative diff analysis."):
        super().__init__(message, code="FILING_COMPARISON_INCOMPATIBLE")


class FilingRateLimitedError(FilingError):
    """Raised when an upstream regulator rate limit is reached."""

    def __init__(self, message: str = "Regulator request quota or rate limit exceeded."):
        super().__init__(message, code="FILING_RATE_LIMITED")


class FilingSecuritySanitizationError(FilingError):
    """Raised when a filing contains dangerous or malicious active scripts."""

    def __init__(self, message: str = "Document content failed security sanitization."):
        super().__init__(message, code="FILING_MALFORMED_DOCUMENT")


class FilingResourceLimitExceededError(FilingError):
    """Raised when document size or parser memory exceeds safety bounds."""

    def __init__(self, message: str = "Document exceeds maximum processing resource limit."):
        super().__init__(message, code="FILING_RESOURCE_LIMIT_EXCEEDED")
