"""Canonical Schemas and DTOs for Institutional News APIs (Stage 99)."""

import datetime
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from atlas.news.enums import (
    EventAmountApproximation,
    EventAmountType,
    EventParticipantRole,
    EventTimePrecision,
    FinancialEventType,
    NewsArticleType,
    NewsAvailabilityStatus,
    NewsClassificationMethod,
    NewsEntityRelevanceClass,
    NewsEventAssertionStatus,
    NewsEventLifecycleStatus,
    NewsEvidenceScope,
    NewsEvidenceType,
    NewsFinancialAspect,
    NewsLatencyClass,
    NewsLicensingStatus,
    NewsMarketReactionWindow,
    NewsSentimentLabel,
    NewsStoryMembershipReason,
    NewsStoryMembershipStatus,
    NewsStoryStatus,
)
from atlas.news.types import NewsEventKind, NewsEventStatus


# Preserved for Stage 20 / Stage 36 entity compatibility
class NewsEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    event_kind: Optional[NewsEventKind] = None
    event_time: Optional[datetime.datetime] = None
    event_status: Optional[NewsEventStatus] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Stage 99 News DTOs
# ---------------------------------------------------------------------------

class NewsEntityMentionDTO(BaseModel):
    entity_id: str = Field(..., description="Canonical entity ID (UUID or identifier string).")
    entity_type: str = Field(..., description="Type of entity ('COMPANY', 'INSTRUMENT', 'GEOGRAPHY', 'CENTRAL_BANK').")
    canonical_name: str = Field(..., description="Display or canonical name of the entity.")
    ticker: Optional[str] = Field(default=None, description="Primary trading symbol if equity.")
    exchange: Optional[str] = Field(default=None, description="Listing exchange code.")
    country_code: Optional[str] = Field(default=None, description="ISO country code.")
    mention_type: str = Field(default="PRIMARY_SUBJECT")
    resolution_method: str = Field(default="HIGH_CONFIDENCE_DETERMINISTIC")
    verification_status: str = Field(default="VERIFIED")

    model_config = ConfigDict(from_attributes=True)


class NewsArticleDTO(BaseModel):
    article_id: str = Field(..., description="Unique canonical article ID.")
    source_provider_id: str = Field(..., description="Provider identifier.")
    publisher_id: str = Field(..., description="Publisher identifier slug.")
    publisher_name: str = Field(..., description="Verified canonical publisher display name.")
    publisher_article_id: Optional[str] = Field(default=None, description="Source native article ID.")
    headline: str = Field(..., description="Sanitized source headline.")
    permitted_excerpt: Optional[str] = Field(default=None, description="Copyright-compliant excerpt.")
    original_url: str = Field(..., description="Verified publisher destination URL.")
    canonical_url: str = Field(..., description="Tracking-free canonical identity URL.")
    language: str = Field(default="en")
    article_type: NewsArticleType = Field(default=NewsArticleType.NEWS_REPORT)
    published_at: datetime.datetime = Field(..., description="Verified publication timestamp in UTC.")
    source_updated_at: Optional[datetime.datetime] = Field(default=None)
    first_seen_at: datetime.datetime = Field(..., description="When ATLAS first received the record.")
    ingested_at: datetime.datetime = Field(..., description="When ATLAS normalized and persisted the record.")
    availability_status: NewsAvailabilityStatus = Field(default=NewsAvailabilityStatus.AVAILABLE)
    licensing_status: NewsLicensingStatus = Field(default=NewsLicensingStatus.EXCERPT_ONLY)
    categories: List[str] = Field(default_factory=list)
    linked_entities: List[NewsEntityMentionDTO] = Field(default_factory=list)
    geographies: List[str] = Field(default_factory=list)
    topic_ids: List[str] = Field(default_factory=list, description="Canonical topic identifiers.")
    industries: List[str] = Field(default_factory=list, description="Industry sector codes.")
    authors: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    revision: int = Field(default=1)
    is_duplicate: bool = Field(default=False)
    is_corrected: bool = Field(default=False)
    syndicated_from_id: Optional[str] = Field(default=None)
    correction_details: Optional[str] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Stage 100 Discovery & Timeline DTOs
# ---------------------------------------------------------------------------

class NewsTopicDTO(BaseModel):
    topic_id: str
    canonical_name: str
    description: str
    parent_topic_id: Optional[str] = None
    category: str

    model_config = ConfigDict(from_attributes=True)


class NewsDiscoveryQueryDTO(BaseModel):
    mode: str = Field(default="ALL", description="NewsDiscoveryMode ('ALL', 'MARKETS', 'COMPANIES', 'SECURITIES', 'TOPICS', 'INDUSTRIES', 'WATCHLIST').")
    query: Optional[str] = Field(default=None, max_length=200, description="Headline or excerpt keyword search.")
    publisher_ids: Optional[List[str]] = Field(default=None, description="Filter by publisher IDs.")
    source_ids: Optional[List[str]] = Field(default=None, description="Filter by provider source IDs.")
    categories: Optional[List[str]] = Field(default=None, description="Filter by category slugs.")
    topic_ids: Optional[List[str]] = Field(default=None, description="Filter by canonical topic IDs.")
    company_ids: Optional[List[str]] = Field(default=None, description="Filter by canonical company UUIDs.")
    instrument_ids: Optional[List[str]] = Field(default=None, description="Filter by canonical instrument UUIDs or tickers.")
    country_ids: Optional[List[str]] = Field(default=None, description="Filter by ISO country codes.")
    industry_ids: Optional[List[str]] = Field(default=None, description="Filter by industry sectors.")
    language_codes: Optional[List[str]] = Field(default=None, description="Filter by ISO language codes.")
    article_types: Optional[List[str]] = Field(default=None, description="Filter by article types.")
    date_preset: str = Field(default="ALL_TIME", description="NewsDatePreset ('ALL_TIME', 'TODAY', 'PAST_24H', 'PAST_7D', 'PAST_30D', 'CUSTOM').")
    start_date: Optional[datetime.datetime] = Field(default=None, description="Custom range start date (UTC).")
    end_date: Optional[datetime.datetime] = Field(default=None, description="Custom range end date (UTC).")
    sort_order: str = Field(default="PUBLISHED_DESC", description="Sort order ('PUBLISHED_DESC', 'PUBLISHED_ASC', 'RELEVANCE_DESC').")
    limit: int = Field(default=30, ge=1, le=100, description="Articles per page.")
    cursor: Optional[str] = Field(default=None, description="Keyset pagination cursor.")

    model_config = ConfigDict(from_attributes=True)


class NewsFacetItemDTO(BaseModel):
    key: str
    label: str
    count: int

    model_config = ConfigDict(from_attributes=True)


class NewsFacetsResponseDTO(BaseModel):
    sources: List[NewsFacetItemDTO] = Field(default_factory=list)
    publishers: List[NewsFacetItemDTO] = Field(default_factory=list)
    categories: List[NewsFacetItemDTO] = Field(default_factory=list)
    topics: List[NewsFacetItemDTO] = Field(default_factory=list)
    countries: List[NewsFacetItemDTO] = Field(default_factory=list)
    article_types: List[NewsFacetItemDTO] = Field(default_factory=list)
    as_of: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class NewsTimelineBucketDTO(BaseModel):
    bucket_id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    label: str
    article_count: int
    articles: List[NewsArticleDTO] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class NewsTimelineRequestDTO(BaseModel):
    query: NewsDiscoveryQueryDTO = Field(default_factory=NewsDiscoveryQueryDTO)
    interval: str = Field(default="DAY", description="Interval: 'DAY', 'WEEK', 'MONTH'.")
    timezone: str = Field(default="UTC", description="IANA timezone identifier (e.g. 'UTC', 'America/New_York', 'Asia/Kolkata').")

    model_config = ConfigDict(from_attributes=True)


class NewsTimelineResponseDTO(BaseModel):
    interval: str
    timezone: str
    total_articles: int
    total_buckets: int
    buckets: List[NewsTimelineBucketDTO] = Field(default_factory=list)
    as_of: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class NewsSearchSuggestionDTO(BaseModel):
    suggestion_id: str
    title: str
    subtitle: str
    type: str = Field(..., description="Type: 'COMPANY', 'INSTRUMENT', 'TOPIC', 'PUBLISHER', 'CATEGORY', 'KEYWORD'")
    filter_key: str
    filter_value: str

    model_config = ConfigDict(from_attributes=True)


class NewsDiscoveryResponseDTO(BaseModel):
    articles: List[NewsArticleDTO] = Field(default_factory=list)
    total_count: int = Field(default=0)
    next_cursor: Optional[str] = Field(default=None)
    has_more: bool = Field(default=False)
    as_of: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    active_filters: Dict[str, Any] = Field(default_factory=dict)
    facets: Optional[NewsFacetsResponseDTO] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


class NewsFeedResponseDTO(BaseModel):
    articles: List[NewsArticleDTO] = Field(default_factory=list)
    total_count: int = Field(default=0)
    next_cursor: Optional[str] = Field(default=None)
    has_more: bool = Field(default=False)
    as_of: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    active_filters: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class NewsPublisherDTO(BaseModel):
    publisher_id: str
    canonical_name: str
    verified_domain: str
    publisher_type: str
    country_code: Optional[str] = None
    official_website: str
    attribution_required: bool = True
    status: str = "VERIFIED"

    model_config = ConfigDict(from_attributes=True)


class NewsSourceDTO(BaseModel):
    source_id: str
    provider_name: str
    provider_type: str
    supported_content_types: List[str] = Field(default_factory=list)
    geographic_coverage: List[str] = Field(default_factory=list)
    update_cadence_seconds: int = 60
    latency_class: NewsLatencyClass = NewsLatencyClass.NEAR_REALTIME
    attribution_policy: str = "MANDATORY_EXPLICIT"
    excerpt_policy: str = "AUTHORIZED_SNIPPET_ONLY"
    health_status: str = "HEALTHY"
    last_successful_ingestion: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NewsCoverageResponseDTO(BaseModel):
    total_articles: int
    active_sources: int
    verified_publishers: int
    supported_categories: List[str] = Field(default_factory=list)
    geographic_coverage: List[str] = Field(default_factory=list)
    latest_publication_time: Optional[datetime.datetime] = None
    latest_ingestion_time: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NewsFreshnessResponseDTO(BaseModel):
    status: str
    latency_class: NewsLatencyClass
    last_successful_fetch: Optional[datetime.datetime] = None
    latest_article_published: Optional[datetime.datetime] = None
    latest_article_ingested: Optional[datetime.datetime] = None
    staleness_seconds: int = 0
    active_source_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class NewsIngestionItemDTO(BaseModel):
    headline: str
    publisher_id: str
    original_url: str
    published_at: datetime.datetime
    permitted_excerpt: Optional[str] = None
    source_updated_at: Optional[datetime.datetime] = None
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    geographies: List[str] = Field(default_factory=list)
    article_type: str = "NEWS_REPORT"
    publisher_article_id: Optional[str] = None


class NewsIngestionRequestDTO(BaseModel):
    source_id: str = Field(default="openbb_news")
    articles: List[NewsIngestionItemDTO] = Field(default_factory=list)


class NewsIngestionResponseDTO(BaseModel):
    total_received: int
    new_articles: int
    revisions: int
    duplicates_suppressed: int
    errors: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Stage 101 Story & Financial Event DTOs
# ---------------------------------------------------------------------------

class NewsStoryArticleLinkDTO(BaseModel):
    story_id: str
    article_id: str
    publisher_id: str
    published_at: datetime.datetime
    headline: str
    membership_reason: NewsStoryMembershipReason
    membership_status: NewsStoryMembershipStatus
    is_primary_anchor: bool
    linked_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class NewsStoryThreadDTO(BaseModel):
    story_id: str
    display_title: str
    canonical_topic_label: Optional[str] = None
    topic_ids: List[str] = Field(default_factory=list)
    primary_entity_id: Optional[str] = None
    primary_entity_name: Optional[str] = None
    related_entities: List[NewsEntityMentionDTO] = Field(default_factory=list)
    first_source_published_at: datetime.datetime
    latest_source_published_at: datetime.datetime
    first_seen_at: datetime.datetime
    latest_activity_at: datetime.datetime
    story_status: NewsStoryStatus
    article_count: int
    independent_publisher_count: int
    publishers: List[str] = Field(default_factory=list)
    article_ids: List[str] = Field(default_factory=list)
    representative_article_id: str
    clustering_method: str
    clustering_version: str
    linked_event_ids: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class NewsStoryFeedResponseDTO(BaseModel):
    stories: List[NewsStoryThreadDTO]
    total_count: int
    next_cursor: Optional[str] = None
    has_more: bool
    as_of: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class EventParticipantDTO(BaseModel):
    entity_id: str
    canonical_name: str
    role: EventParticipantRole
    resolution_status: str

    model_config = ConfigDict(from_attributes=True)


class EventAmountDTO(BaseModel):
    amount_type: EventAmountType
    amount_value: float
    currency: str
    period: Optional[str] = None
    approximation_status: EventAmountApproximation
    source_text: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NewsEventEvidenceDTO(BaseModel):
    evidence_id: str
    event_id: str
    article_id: str
    publisher_id: str
    publisher_name: str
    source_provider_id: str
    evidence_type: NewsEvidenceType
    headline: str
    permitted_excerpt: Optional[str] = None
    source_published_at: datetime.datetime
    first_observed_at: datetime.datetime
    is_verified_by_filing: bool
    filing_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NewsEventRevisionDTO(BaseModel):
    revision_id: str
    event_id: str
    timestamp: datetime.datetime
    previous_lifecycle_status: Optional[NewsEventLifecycleStatus] = None
    new_lifecycle_status: NewsEventLifecycleStatus
    previous_assertion_status: Optional[NewsEventAssertionStatus] = None
    new_assertion_status: NewsEventAssertionStatus
    change_reason: str
    evidence_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NewsFinancialEventDTO(BaseModel):
    event_id: str
    event_type: FinancialEventType
    event_title: str
    primary_entity_id: str
    primary_entity_name: str
    lifecycle_status: NewsEventLifecycleStatus
    assertion_status: NewsEventAssertionStatus
    event_date: Optional[datetime.datetime] = None
    event_time_precision: EventTimePrecision
    announcement_time: Optional[datetime.datetime] = None
    first_seen_at: datetime.datetime
    last_evidence_updated_at: datetime.datetime
    participants: List[EventParticipantDTO] = Field(default_factory=list)
    amounts: List[EventAmountDTO] = Field(default_factory=list)
    supporting_article_ids: List[str] = Field(default_factory=list)
    evidence_records: List[NewsEventEvidenceDTO] = Field(default_factory=list)
    linked_story_ids: List[str] = Field(default_factory=list)
    revisions: List[NewsEventRevisionDTO] = Field(default_factory=list)
    is_disputed: bool
    is_corrected: bool

    model_config = ConfigDict(from_attributes=True)


class NewsEventFeedResponseDTO(BaseModel):
    events: List[NewsFinancialEventDTO]
    total_count: int
    next_cursor: Optional[str] = None
    has_more: bool
    as_of: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class FinancialEventTypeDefinitionDTO(BaseModel):
    event_type_id: FinancialEventType
    canonical_label: str
    event_family: str
    description: str
    supported_roles: List[EventParticipantRole]
    supported_amount_types: List[EventAmountType]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Stage 102: Sentiment, Relevance & Market Reaction DTOs
# ---------------------------------------------------------------------------
class SentimentEvidenceReferenceDTO(BaseModel):
    evidence_id: str
    article_revision_id: str
    evidence_scope: NewsEvidenceScope
    text_span: Optional[str] = None
    rationale_code: str
    source_rights: str

    model_config = ConfigDict(from_attributes=True)


class NewsSentimentAnnotationDTO(BaseModel):
    annotation_id: str
    article_id: str
    article_revision_id: str
    target_entity_id: str
    target_entity_type: str
    target_canonical_name: Optional[str] = None
    target_ticker: Optional[str] = None
    sentiment_label: NewsSentimentLabel
    sentiment_aspect: NewsFinancialAspect
    sentiment_score: float
    confidence_score: Optional[float] = None
    classification_status: str
    classification_method: NewsClassificationMethod
    classifier_version: str
    taxonomy_version: str
    evidence: List[SentimentEvidenceReferenceDTO] = Field(default_factory=list)
    explanation: Optional[str] = None
    source_published_at: datetime.datetime
    analysis_created_at: datetime.datetime
    retrospective_reprocessing: bool = False

    model_config = ConfigDict(from_attributes=True)


class NewsEntityRelevanceDTO(BaseModel):
    relevance_id: str
    article_id: str
    article_revision_id: str
    entity_id: str
    entity_type: str
    canonical_name: str
    ticker: Optional[str] = None
    relevance_class: NewsEntityRelevanceClass
    relevance_score: float
    evidence_source: NewsEvidenceScope
    is_primary_subject: bool
    is_direct_participant: bool
    source_published_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class EntitySentimentAggregateDTO(BaseModel):
    target_entity_id: str
    target_canonical_name: Optional[str] = None
    target_ticker: Optional[str] = None
    evaluation_window_days: int
    eligible_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    mixed_count: int
    insufficient_evidence_count: int
    net_sentiment: float
    unique_story_count: int
    independent_publisher_count: int
    top_aspects: List[Dict[str, Any]] = Field(default_factory=list)
    coverage_completeness: str
    methodology_version: str
    evaluation_time: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class SentimentTimelineBucketDTO(BaseModel):
    bucket_start: datetime.datetime
    bucket_end: datetime.datetime
    label: str
    eligible_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    mixed_count: int
    net_sentiment: float

    model_config = ConfigDict(from_attributes=True)


class SentimentTimelineResponseDTO(BaseModel):
    target_entity_id: str
    interval: str
    buckets: List[SentimentTimelineBucketDTO]
    total_articles: int
    overall_net_sentiment: float
    as_of: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class StorySentimentProfileDTO(BaseModel):
    story_id: str
    target_entity_id: str
    distribution: Dict[str, int]
    net_sentiment: float
    eligible_article_count: int
    independent_source_count: int
    evaluation_time: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class EventSentimentProfileDTO(BaseModel):
    event_id: str
    target_entity_id: str
    distribution: Dict[str, int]
    net_sentiment: float
    eligible_evidence_count: int
    assertion_status: str
    evaluation_time: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ObservedNewsMarketContextDTO(BaseModel):
    article_id_or_event_id: str
    instrument_id: str
    ticker: str
    company_name: str
    currency: str
    exchange: str
    publication_time: datetime.datetime
    publication_precision: str
    observation_window: NewsMarketReactionWindow
    window_start_time: datetime.datetime
    window_end_time: datetime.datetime
    price_start: Decimal
    price_end: Decimal
    observed_return: Decimal
    observed_return_percent: Decimal
    benchmark_instrument_id: Optional[str] = None
    benchmark_name: Optional[str] = None
    benchmark_return_percent: Optional[Decimal] = None
    benchmark_relative_return_percent: Optional[Decimal] = None
    adjustment_policy: str
    noncausal_disclaimer: str
    limitations: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class MarketReactionRequestDTO(BaseModel):
    article_id_or_event_id: str
    instrument_id: Optional[str] = None
    ticker: Optional[str] = None
    window: NewsMarketReactionWindow = NewsMarketReactionWindow.PREV_CLOSE_TO_NEXT_CLOSE
    exchange: str = "NASDAQ"
    currency: str = "USD"


class SentimentEvaluationResultDTO(BaseModel):
    evaluation_corpus_size: int
    macro_f1: float
    classifier_version: str
    taxonomy_version: str
    per_class_metrics: Dict[str, Any]
    evaluation_timestamp: str

    model_config = ConfigDict(from_attributes=True)


