"""Canonical Schemas and DTOs for Institutional News APIs (Stage 99)."""

import datetime
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from atlas.news.enums import (
    NewsArticleType,
    NewsAvailabilityStatus,
    NewsLatencyClass,
    NewsLicensingStatus,
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
    authors: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    revision: int = Field(default=1)
    is_duplicate: bool = Field(default=False)
    is_corrected: bool = Field(default=False)
    syndicated_from_id: Optional[str] = Field(default=None)
    correction_details: Optional[str] = Field(default=None)

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
