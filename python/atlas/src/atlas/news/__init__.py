"""Canonical Exports for ATLAS News Module (Stage 99)."""

from atlas.news.articles import NewsArticle, NewsArticleRevision
from atlas.news.caching import NewsFeedCache, default_news_cache
from atlas.news.capabilities import NewsProviderCapabilities, NewsProviderOperation
from atlas.news.deduplication import DeduplicationEngine, DeduplicationResult
from atlas.news.entity_resolution import NewsEntityMention, resolve_entities_in_text
from atlas.news.enums import (
    NewsArticleType,
    NewsAvailabilityStatus,
    NewsCategory,
    NewsChangeType,
    NewsLatencyClass,
    NewsLicensingStatus,
    NewsProviderType,
    NewsPublisherType,
)
from atlas.news.errors import (
    InvalidNewsEventKindError,
    InvalidNewsEventStatusError,
    NewsArticleNotFoundError,
    NewsArticleRestrictedError,
    NewsArticleWithdrawnError,
    NewsCategoryUnsupportedError,
    NewsDomainError,
    NewsEventDataInconsistentError,
    NewsEventNotFoundError,
    NewsExternalUrlUnsafeError,
    NewsIngestionFailedError,
    NewsPublisherNotFoundError,
    NewsQueryInvalidError,
    NewsSearchInvalidError,
    NewsSourceNotEntitledError,
    NewsSourceUnavailableError,
)
from atlas.news.models import NewsEvent
from atlas.news.normalization import (
    normalize_canonical_url,
    normalize_timestamp,
    sanitize_plain_text,
    validate_external_url,
)
from atlas.news.origin import NewsDataOrigin
from atlas.news.protocols import NewsProvider
from atlas.news.publishers import (
    NewsPublisher,
    get_verified_publisher,
    list_verified_publishers,
)
from atlas.news.repository import (
    IngestionBatchResult,
    NewsCoverageReport,
    NewsEventRepository,
    NewsFeedQuery,
    NewsFeedResult,
    NewsFreshnessStatus,
    NewsRepository,
)
from atlas.news.requests import NewsLatestRequest, NewsSearchRequest
from atlas.news.responses import NewsResponse
from atlas.news.schemas import (
    NewsArticleDTO,
    NewsCoverageResponseDTO,
    NewsEntityMentionDTO,
    NewsEventResponse,
    NewsFeedResponseDTO,
    NewsFreshnessResponseDTO,
    NewsIngestionItemDTO,
    NewsIngestionRequestDTO,
    NewsIngestionResponseDTO,
    NewsPublisherDTO,
    NewsSourceDTO,
)
from atlas.news.service import (
    NewsEventService,
    NewsService,
    get_news_service,
)
from atlas.news.sources import (
    NewsSource,
    get_news_source,
    list_news_sources,
)
from atlas.news.types import NewsEventKind, NewsEventStatus

__all__ = [
    # Preserved Stage 20/36 items
    "NewsEvent",
    "NewsEventRepository",
    "NewsEventResponse",
    "NewsEventService",
    "NewsEventKind",
    "NewsEventStatus",
    "NewsDomainError",
    "NewsEventNotFoundError",
    "NewsEventDataInconsistentError",
    "InvalidNewsEventKindError",
    "InvalidNewsEventStatusError",
    "NewsDataOrigin",
    "NewsArticle",
    "NewsProviderCapabilities",
    "NewsProviderOperation",
    "NewsLatestRequest",
    "NewsSearchRequest",
    "NewsResponse",
    "NewsProvider",
    # Stage 99 News Platform
    "NewsArticleRevision",
    "NewsPublisher",
    "NewsSource",
    "NewsEntityMention",
    "NewsArticleType",
    "NewsAvailabilityStatus",
    "NewsLicensingStatus",
    "NewsCategory",
    "NewsProviderType",
    "NewsLatencyClass",
    "NewsPublisherType",
    "NewsChangeType",
    "NewsArticleNotFoundError",
    "NewsArticleWithdrawnError",
    "NewsArticleRestrictedError",
    "NewsSourceUnavailableError",
    "NewsSourceNotEntitledError",
    "NewsPublisherNotFoundError",
    "NewsCategoryUnsupportedError",
    "NewsQueryInvalidError",
    "NewsSearchInvalidError",
    "NewsExternalUrlUnsafeError",
    "NewsIngestionFailedError",
    "normalize_canonical_url",
    "validate_external_url",
    "sanitize_plain_text",
    "normalize_timestamp",
    "resolve_entities_in_text",
    "DeduplicationEngine",
    "DeduplicationResult",
    "NewsRepository",
    "NewsFeedQuery",
    "NewsFeedResult",
    "NewsCoverageReport",
    "NewsFreshnessStatus",
    "IngestionBatchResult",
    "NewsService",
    "get_news_service",
    "NewsFeedCache",
    "default_news_cache",
    "get_verified_publisher",
    "list_verified_publishers",
    "get_news_source",
    "list_news_sources",
    "NewsArticleDTO",
    "NewsEntityMentionDTO",
    "NewsFeedResponseDTO",
    "NewsPublisherDTO",
    "NewsSourceDTO",
    "NewsCoverageResponseDTO",
    "NewsFreshnessResponseDTO",
    "NewsIngestionItemDTO",
    "NewsIngestionRequestDTO",
    "NewsIngestionResponseDTO",
]
