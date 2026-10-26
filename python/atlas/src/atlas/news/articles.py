"""Canonical News Article Entities, Provenance, and Revision Lifecycle (Stage 99)."""

import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from atlas.news.entity_resolution import NewsEntityMention
from atlas.news.enums import (
    NewsArticleType,
    NewsAvailabilityStatus,
    NewsCategory,
    NewsChangeType,
    NewsLicensingStatus,
)
from atlas.news.origin import NewsDataOrigin


class NewsArticle(BaseModel):
    """
    Canonical, immutable representation of a financial news article.
    Preserves publisher attribution, publication & update timestamps,
    canonical URL identity, entity mentions, copyright licensing,
    and revision tracking.
    """

    article_id: str = Field(default="", description="Unique canonical article ID (e.g., 'art-uuid' or deterministic hash).")
    source_provider_id: str = Field(default="openbb", description="Provider ID that ingested the record.")
    publisher_id: str = Field(default="generic_publisher", description="Slug of the verified publisher.")
    publisher_name: str = Field(default="", description="Canonical display name of the publisher.")
    publisher_article_id: Optional[str] = Field(default=None, description="Native identifier assigned by upstream source/publisher.")

    title: str = Field(..., description="The headline or title of the news article.")
    headline: str = Field(default="", description="Sanitized headline string.")
    publisher: str = Field(..., description="Publisher name (preserved for Stage 36/79 compatibility).")

    permitted_excerpt: Optional[str] = Field(default=None, description="Copyright-compliant excerpt snippet.")
    summary: Optional[str] = Field(default=None, description="Summary (preserved for Stage 36/79 compatibility).")

    url: Optional[HttpUrl] = Field(default=None, description="The URL to the original article.")
    canonical_url: str = Field(default="", description="Normalized tracking-free canonical URL.")
    original_url: str = Field(default="", description="Verified original publisher destination URL.")

    language: str = Field(default="en", description="ISO 639-1 language code.")
    article_type: NewsArticleType = Field(default=NewsArticleType.NEWS_REPORT, description="Classification of the article content.")

    published_at: datetime.datetime = Field(..., description="Verified timestamp when originally published.")
    source_updated_at: Optional[datetime.datetime] = Field(default=None, description="When publisher updated or corrected story.")
    first_seen_at: Optional[datetime.datetime] = Field(default=None, description="When ATLAS first observed the article.")
    ingested_at: Optional[datetime.datetime] = Field(default=None, description="When ATLAS normalized and stored the record.")

    availability_status: NewsAvailabilityStatus = Field(default=NewsAvailabilityStatus.AVAILABLE)
    licensing_status: NewsLicensingStatus = Field(default=NewsLicensingStatus.EXCERPT_ONLY)

    categories: tuple[NewsCategory, ...] = Field(default_factory=tuple, description="Financial taxonomy categories.")
    linked_entities: tuple[NewsEntityMention, ...] = Field(default_factory=tuple, description="Canonical entity links.")
    geographies: tuple[str, ...] = Field(default_factory=tuple, description="Geographic regions (ISO country codes).")

    authors: tuple[str, ...] = Field(default_factory=tuple, description="Authors or bylines.")
    tags: tuple[str, ...] = Field(default_factory=tuple, description="Tags, keywords, or topics.")

    revision: int = Field(default=1, description="Sequential revision number of this article.")
    is_duplicate: bool = Field(default=False, description="Whether this article is a duplicate of a canonical record.")
    duplicate_of_id: Optional[str] = Field(default=None, description="Canonical article ID if marked duplicate.")
    syndicated_from_id: Optional[str] = Field(default=None, description="Original source ID if syndicated.")
    is_corrected: bool = Field(default=False, description="Whether article contains a published correction.")
    correction_details: Optional[str] = Field(default=None, description="Details of correction.")

    origin: NewsDataOrigin = Field(..., description="The provenance information of the article data.")

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="before")
    @classmethod
    def _synchronize_fields(cls, data: dict) -> dict:
        if isinstance(data, dict):
            # Synchronize title and headline
            if "headline" in data and data["headline"] and not data.get("title"):
                data["title"] = data["headline"]
            elif "title" in data and data["title"] and not data.get("headline"):
                data["headline"] = data["title"]

            # Synchronize publisher and publisher_name
            if "publisher_name" in data and data["publisher_name"] and not data.get("publisher"):
                data["publisher"] = data["publisher_name"]
            elif "publisher" in data and data["publisher"] and not data.get("publisher_name"):
                data["publisher_name"] = data["publisher"]

            # Synchronize summary and permitted_excerpt
            if "permitted_excerpt" in data and data["permitted_excerpt"] and not data.get("summary"):
                data["summary"] = data["permitted_excerpt"]
            elif "summary" in data and data["summary"] and not data.get("permitted_excerpt"):
                data["permitted_excerpt"] = data["summary"]

            # Synchronize original_url and url
            if "url" in data and data["url"] and not data.get("original_url"):
                data["original_url"] = str(data["url"])
            elif "original_url" in data and data["original_url"] and not data.get("url"):
                try:
                    data["url"] = data["original_url"]
                except Exception:
                    pass

            # Default canonical_url if absent
            if not data.get("canonical_url") and data.get("original_url"):
                data["canonical_url"] = str(data["original_url"])

            # Default timestamps if absent
            now = datetime.datetime.now(datetime.timezone.utc)
            if not data.get("first_seen_at"):
                data["first_seen_at"] = now
            if not data.get("ingested_at"):
                data["ingested_at"] = now

        return data


class NewsArticleRevision(BaseModel):
    """
    Immutable audit record representing an observed revision or correction
    to a canonical News Article.
    """

    revision_id: str = Field(..., description="Unique ID for this revision record.")
    article_id: str = Field(..., description="Target canonical article ID.")
    revision_number: int = Field(..., description="1-based sequential revision index.")
    observed_at: datetime.datetime = Field(..., description="When the revision was ingested.")
    source_updated_at: Optional[datetime.datetime] = Field(default=None, description="When source modified the story.")
    change_type: NewsChangeType = Field(default=NewsChangeType.INITIAL_INGESTION)
    headline: str = Field(..., description="Headline at this revision.")
    permitted_excerpt: Optional[str] = Field(default=None, description="Excerpt at this revision.")
    change_summary: Optional[str] = Field(default=None, description="Description of changes.")

    model_config = ConfigDict(frozen=True)
