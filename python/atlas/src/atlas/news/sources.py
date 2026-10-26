"""Canonical News Source Registry and Provider Integration Contracts (Stage 99)."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from atlas.news.enums import (
    NewsArticleType,
    NewsLatencyClass,
    NewsProviderType,
)


class NewsSource(BaseModel):
    """
    Metadata describing an authorized news source integration.
    """

    source_id: str = Field(..., description="Unique slug for the source integration.")
    provider_name: str = Field(..., description="Provider or vendor name.")
    provider_type: NewsProviderType = Field(default=NewsProviderType.LICENSED_NEWS_API)
    supported_content_types: tuple[NewsArticleType, ...] = Field(default_factory=tuple)
    geographic_coverage: tuple[str, ...] = Field(default_factory=tuple)
    update_cadence_seconds: int = Field(default=60)
    latency_class: NewsLatencyClass = Field(default=NewsLatencyClass.NEAR_REALTIME)
    attribution_policy: str = Field(default="MANDATORY_EXPLICIT")
    excerpt_policy: str = Field(default="AUTHORIZED_SNIPPET_ONLY")
    full_text_policy: str = Field(default="NOT_PERMITTED")
    retention_policy_days: int = Field(default=365)
    health_status: str = Field(default="HEALTHY")
    last_successful_ingestion: Optional[datetime] = None

    model_config = ConfigDict(frozen=True)


# Pre-populated authorized financial news sources
_AUTHORIZED_NEWS_SOURCES: Dict[str, NewsSource] = {
    "openbb_news": NewsSource(
        source_id="openbb_news",
        provider_name="OpenBB Financial News Platform",
        provider_type=NewsProviderType.LICENSED_NEWS_API,
        supported_content_types=(
            NewsArticleType.NEWS_REPORT,
            NewsArticleType.WIRE_REPORT,
            NewsArticleType.PRESS_RELEASE,
            NewsArticleType.MARKET_COMMENTARY,
        ),
        geographic_coverage=("US", "EU", "GB", "IN", "JP", "GLOBAL"),
        update_cadence_seconds=60,
        latency_class=NewsLatencyClass.NEAR_REALTIME,
        attribution_policy="MANDATORY_EXPLICIT",
        excerpt_policy="AUTHORIZED_SNIPPET_ONLY",
        full_text_policy="NOT_PERMITTED",
        retention_policy_days=365,
        health_status="HEALTHY",
    ),
    "financial_wire_direct": NewsSource(
        source_id="financial_wire_direct",
        provider_name="Institutional Financial Wire Direct",
        provider_type=NewsProviderType.LICENSED_NEWS_API,
        supported_content_types=(
            NewsArticleType.WIRE_REPORT,
            NewsArticleType.NEWS_REPORT,
            NewsArticleType.OFFICIAL_ANNOUNCEMENT,
        ),
        geographic_coverage=("US", "GB", "EU", "GLOBAL"),
        update_cadence_seconds=30,
        latency_class=NewsLatencyClass.REALTIME,
        attribution_policy="MANDATORY_EXPLICIT",
        excerpt_policy="AUTHORIZED_SNIPPET_ONLY",
        full_text_policy="NOT_PERMITTED",
        retention_policy_days=730,
        health_status="HEALTHY",
    ),
    "regulator_announcements": NewsSource(
        source_id="regulator_announcements",
        provider_name="Official Central Bank & Regulatory Feeds",
        provider_type=NewsProviderType.OFFICIAL_PUBLIC_FEED,
        supported_content_types=(
            NewsArticleType.OFFICIAL_ANNOUNCEMENT,
            NewsArticleType.NEWS_REPORT,
        ),
        geographic_coverage=("US", "EU", "IN", "GB"),
        update_cadence_seconds=300,
        latency_class=NewsLatencyClass.NEAR_REALTIME,
        attribution_policy="MANDATORY_EXPLICIT",
        excerpt_policy="FULL_DISPLAY",
        full_text_policy="AUTHORIZED_PUBLIC_RECORD",
        retention_policy_days=1825,
        health_status="HEALTHY",
    ),
    "corporate_press_wire": NewsSource(
        source_id="corporate_press_wire",
        provider_name="Corporate Disclosures & Press Wire",
        provider_type=NewsProviderType.LICENSED_RSS_FEED,
        supported_content_types=(
            NewsArticleType.PRESS_RELEASE,
            NewsArticleType.OFFICIAL_ANNOUNCEMENT,
        ),
        geographic_coverage=("US", "IN", "EU", "GLOBAL"),
        update_cadence_seconds=120,
        latency_class=NewsLatencyClass.NEAR_REALTIME,
        attribution_policy="MANDATORY_EXPLICIT",
        excerpt_policy="AUTHORIZED_SNIPPET_ONLY",
        full_text_policy="NOT_PERMITTED",
        retention_policy_days=365,
        health_status="HEALTHY",
    ),
}


def get_news_source(source_id: str) -> Optional[NewsSource]:
    """Retrieve an authorized news source by ID."""
    return _AUTHORIZED_NEWS_SOURCES.get(source_id.lower())


def list_news_sources() -> List[NewsSource]:
    """List all authorized news sources in the registry."""
    return list(_AUTHORIZED_NEWS_SOURCES.values())
