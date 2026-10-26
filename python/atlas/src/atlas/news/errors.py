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


# Stage 101 Story Intelligence & Financial Event Errors
class NewsStoryNotFoundError(NewsDomainError):
    """Raised when a requested canonical Story Thread ID does not exist."""

    pass


class NewsStoryMergedError(NewsDomainError):
    """Raised when a story has been merged into another canonical thread."""

    pass


class NewsStoryWithdrawnError(NewsDomainError):
    """Raised when a story has been withdrawn from display."""

    pass


class NewsFinancialEventNotFoundError(NewsDomainError):
    """Raised when a requested Financial Event ID does not exist."""

    pass


class NewsEventEvidenceMissingError(NewsDomainError):
    """Raised when required source evidence is missing for a financial event."""

    pass


class NewsEventEvidenceRestrictedError(NewsDomainError):
    """Raised when event evidence is restricted by licensing permissions."""

    pass


class NewsStoryClusterAmbiguousError(NewsDomainError):
    """Raised when a clustering operation cannot resolve thread membership unambiguously."""

    pass


# Stage 102 Sentiment, Relevance & Market Reaction Errors
class NewsSentimentNotFoundError(NewsDomainError):
    """Raised when sentiment annotations for an article or target cannot be found."""

    pass


class NewsSentimentInsufficientEvidenceError(NewsDomainError):
    """Raised when available licensed text is inadequate for sentiment classification."""

    pass


class NewsSentimentTargetUnresolvedError(NewsDomainError):
    """Raised when requested entity target cannot be resolved for sentiment analysis."""

    pass


class NewsSentimentRestrictedError(NewsDomainError):
    """Raised when underlying article rights prevent sentiment computation or extraction."""

    pass


class NewsRelevanceNotFoundError(NewsDomainError):
    """Raised when relevance relationships for an entity cannot be resolved."""

    pass


class NewsMarketReactionPriceUnavailableError(NewsDomainError):
    """Raised when historical market prices are missing for the observation window."""

    pass


class NewsMarketReactionSecurityUnresolvedError(NewsDomainError):
    """Raised when an entity cannot be mapped to a canonical trading instrument."""

    pass


class NewsMarketReactionWindowUnsupportedError(NewsDomainError):
    """Raised when an invalid or unsupported market observation window is requested."""

    pass


