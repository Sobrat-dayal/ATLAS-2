"""Canonical Typed Domain Errors for Institutional News Platform (Stage 99)."""


class NewsDomainError(Exception):
    """Base exception for all news domain errors."""

    pass


# Preserved for Stage 20 / Stage 36 entity compatibility
class NewsEventNotFoundError(NewsDomainError):
    pass


class NewsEventDataInconsistentError(NewsDomainError):
    pass


class InvalidNewsEventKindError(NewsDomainError):
    pass


class InvalidNewsEventStatusError(NewsDomainError):
    pass


# Stage 99 News Platform Errors
class NewsArticleNotFoundError(NewsDomainError):
    """Raised when an article ID does not exist."""

    pass


class NewsArticleWithdrawnError(NewsDomainError):
    """Raised when an article has been officially withdrawn by its source."""

    pass


class NewsArticleRestrictedError(NewsDomainError):
    """Raised when the requesting principal lacks the necessary publisher entitlement."""

    pass


class NewsSourceUnavailableError(NewsDomainError):
    """Raised when an upstream provider or news source is currently offline or degraded."""

    pass


class NewsSourceNotEntitledError(NewsDomainError):
    """Raised when access to a premium source feed is forbidden."""

    pass


class NewsPublisherNotFoundError(NewsDomainError):
    """Raised when a publisher slug cannot be found."""

    pass


class NewsCategoryUnsupportedError(NewsDomainError):
    """Raised when an invalid or unsupported news category is requested."""

    pass


class NewsQueryInvalidError(NewsDomainError):
    """Raised when news feed parameters violate validation constraints."""

    pass


class NewsSearchInvalidError(NewsDomainError):
    """Raised when news search query contains invalid syntax or exceeds maximum limits."""

    pass


class NewsExternalUrlUnsafeError(NewsDomainError):
    """Raised when an external news URL violates SSRF safety rules."""

    pass


class NewsIngestionFailedError(NewsDomainError):
    """Raised when an ingestion batch fails critical validation."""

    pass
