"""Canonical News Reference Adapter for Watchlist Enrichment (Stage 79).

Projects verified news article references:
- news.latest_headline
- news.latest_publication_time
- news.publisher

Guarantees:
- Strict entity association: News is linked through canonical entity relationships or direct entity ID.
- Attribution & Provenance: Preserves publisher, original publication timestamp, and authorized article URL.
- No synthetic headlines or artificial sentiment: Returns UNAVAILABLE when genuine records are absent.
- Entitlement checks: Enforces user access to article references.
- Caching: Efficiently cached with short TTL (15m) without every-tick invalidation.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.news.articles import NewsArticle

from .caching import default_enrichment_cache
from .models import EnrichmentCategory, EnrichmentStatus, WatchlistEnrichmentValue

logger = logging.getLogger(__name__)

# Authoritative in-memory registry of verified canonical news articles linked to entities.
# Keyed by entity_id (instrument_id or company_id) -> list of NewsArticle sorted descending by published_at
_ENTITY_NEWS_STORE: Dict[UUID, List[NewsArticle]] = {}


def register_verified_articles_for_entity(
    entity_id: UUID,
    articles: List[NewsArticle],
) -> None:
    """Helper used by tests and background adapters to register verified canonical news articles."""
    _ENTITY_NEWS_STORE[entity_id] = sorted(articles, key=lambda a: a.published_at, reverse=True)


def clear_verified_news_store() -> None:
    """Clear registered news items (for test isolation)."""
    _ENTITY_NEWS_STORE.clear()


class NewsReferenceAdapter:
    """Adapter projecting canonical news references into typed WatchlistEnrichmentValues."""

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        self.session = session
        self.cache = default_enrichment_cache

    def get_news_metric(
        self,
        column_id: str,
        instrument_id: UUID,
        company_id: Optional[UUID] = None,
        is_entitled: bool = True,
    ) -> WatchlistEnrichmentValue:
        """Projects a news column value for a given instrument and/or company entity."""
        # 1. Entitlement check
        if not is_entitled:
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.NOT_ENTITLED,
                entity_id=instrument_id,
                company_id=company_id,
                reason="User is not entitled to canonical news feed references",
            )

        # 2. Check Cache
        cache_key = f"{instrument_id}:{company_id or 'none'}:{column_id}"
        cached = self.cache.get(EnrichmentCategory.NEWS, cache_key)
        if cached is not None:
            return cached

        # 3. Resolve latest article: check instrument first, then issuer company
        articles = _ENTITY_NEWS_STORE.get(instrument_id)
        entity_resolved_id = instrument_id

        if not articles and company_id is not None:
            articles = _ENTITY_NEWS_STORE.get(company_id)
            if articles:
                entity_resolved_id = company_id

        if not articles:
            val = WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.UNAVAILABLE,
                entity_id=instrument_id,
                company_id=company_id,
                reason="No verified canonical news articles found for entity",
            )
            self.cache.set(EnrichmentCategory.NEWS, cache_key, val)
            return val

        latest = articles[0]
        origin_provider = getattr(
            latest.origin, "provider_id", getattr(latest.origin, "provider", "CANONICAL")
        )

        # Extract values
        if column_id == "news.latest_headline":
            val = WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=latest.title,
                value_type="TEXT",
                entity_id=entity_resolved_id,
                company_id=company_id,
                observation_time=latest.published_at,
                publication_time=latest.published_at,
                source_id=origin_provider,
                source_document_id=getattr(latest.origin, "article_id", None) or latest.title,
                methodology_id="verified_article_reference",
                headline=latest.title,
                publisher=latest.publisher,
                url=str(latest.url) if latest.url else None,
            )
        elif column_id == "news.latest_publication_time":
            val = WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=latest.published_at.isoformat(),
                value_type="TIMESTAMP",
                entity_id=entity_resolved_id,
                company_id=company_id,
                observation_time=latest.published_at,
                publication_time=latest.published_at,
                source_id=origin_provider,
                methodology_id="article_publication_timestamp",
                headline=latest.title,
                publisher=latest.publisher,
                url=str(latest.url) if latest.url else None,
            )
        elif column_id == "news.publisher":
            val = WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=latest.publisher,
                value_type="TEXT",
                entity_id=entity_resolved_id,
                company_id=company_id,
                observation_time=latest.published_at,
                publication_time=latest.published_at,
                source_id=origin_provider,
                methodology_id="article_publisher_attribution",
                headline=latest.title,
                publisher=latest.publisher,
                url=str(latest.url) if latest.url else None,
            )
        else:
            val = WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.ERROR,
                entity_id=instrument_id,
                reason=f"Unsupported news column ID '{column_id}'",
            )

        self.cache.set(EnrichmentCategory.NEWS, cache_key, val)
        return val
