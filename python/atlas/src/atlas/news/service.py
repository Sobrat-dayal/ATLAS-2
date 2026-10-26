"""Institutional News Domain Services (Stage 99)."""

from __future__ import annotations

import datetime
import uuid
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from atlas.entities.repository import EntityRepository
from atlas.entities.service import EntityService
from atlas.entities.types import EntityTypeKey
from atlas.news.articles import NewsArticle, NewsArticleRevision
from atlas.news.caching import default_news_cache
from atlas.news.enums import (
    NewsArticleType,
    NewsAvailabilityStatus,
    NewsCategory,
    NewsLicensingStatus,
)
from atlas.news.errors import (
    InvalidNewsEventKindError,
    InvalidNewsEventStatusError,
    NewsArticleNotFoundError,
    NewsArticleRestrictedError,
    NewsArticleWithdrawnError,
    NewsCategoryUnsupportedError,
    NewsEventDataInconsistentError,
    NewsEventNotFoundError,
    NewsSearchInvalidError,
)
from atlas.news.normalization import (
    normalize_canonical_url,
    normalize_timestamp,
    sanitize_plain_text,
    validate_external_url,
)
from atlas.news.origin import NewsDataOrigin
from atlas.news.publishers import get_verified_publisher
from atlas.news.repository import (
    NewsEventRepository,
    NewsFeedQuery,
    NewsFeedResult,
    NewsRepository,
)
from atlas.news.schemas import (
    NewsArticleDTO,
    NewsCoverageResponseDTO,
    NewsEntityMentionDTO,
    NewsEventResponse,
    NewsFeedResponseDTO,
    NewsFreshnessResponseDTO,
    NewsIngestionRequestDTO,
    NewsIngestionResponseDTO,
    NewsPublisherDTO,
    NewsSourceDTO,
)
from atlas.news.types import NewsEventKind, NewsEventStatus


# Preserved for Stage 20 / Stage 36 entity compatibility
class NewsEventService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = NewsEventRepository(session)
        self.entity_service = EntityService(session)
        self.entity_repository = EntityRepository(session)

    def create_news_event(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        event_kind: Optional[str] = None,
        event_time: Optional[datetime.datetime] = None,
        event_status: Optional[str] = None,
    ) -> NewsEventResponse:
        if event_kind is not None:
            try:
                NewsEventKind(event_kind)
            except ValueError:
                raise InvalidNewsEventKindError(f"Invalid event_kind: {event_kind}")

        if event_status is not None:
            try:
                NewsEventStatus(event_status)
            except ValueError:
                raise InvalidNewsEventStatusError(f"Invalid event_status: {event_status}")

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.NEWS_EVENT,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            event = self.repository.create_news_event_specialization(
                entity_id=entity.entity_id,
                event_kind=event_kind,
                event_time=event_time,
                event_status=event_status,
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return NewsEventResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            event_kind=event.event_kind,
            event_time=event.event_time,
            event_status=event.event_status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def get_news_event(self, entity_id: uuid.UUID) -> NewsEventResponse:
        entity = self.entity_repository.get_entity(entity_id)
        if not entity:
            raise NewsEventNotFoundError(f"News Event {entity_id} not found.")

        if entity.entity_type != EntityTypeKey.NEWS_EVENT:
            raise NewsEventNotFoundError(f"Entity {entity_id} is not a News Event.")

        event_tuple = self.repository.get_news_event(entity_id)
        if not event_tuple:
            raise NewsEventDataInconsistentError(
                f"News Event {entity_id} missing specialization row."
            )

        _, event = event_tuple

        return NewsEventResponse.model_validate(
            {
                **entity.__dict__,
                "event_kind": event.event_kind,
                "event_time": event.event_time,
                "event_status": event.event_status,
            }
        )


class NewsService:
    """
    Primary service orchestrating Stage 99 Institutional Financial News functionality:
    Feeds, Article previews, Ingestion, Caching, and Entitlement checks.
    """

    def __init__(self, repository: Optional[NewsRepository] = None):
        self._repository = repository or NewsRepository()
        self._cache = default_news_cache

    def get_feed(
        self,
        query: NewsFeedQuery,
        is_entitled: bool = True,
    ) -> NewsFeedResponseDTO:
        # Validate category if provided
        if query.category:
            cat_upper = query.category.upper()
            valid_cats = {c.value for c in NewsCategory}
            if cat_upper not in valid_cats:
                raise NewsCategoryUnsupportedError(f"Category '{query.category}' is not supported.")

        # Check Cache
        query_dict = {
            "cat": query.category,
            "src": query.source_id,
            "pub": query.publisher_id,
            "ent": query.entity_id,
            "geo": query.geography,
            "q": query.q,
            "start": query.start_date.isoformat() if query.start_date else None,
            "end": query.end_date.isoformat() if query.end_date else None,
            "limit": query.limit,
            "cursor": query.cursor,
        }
        entitlement_scope = "full" if is_entitled else "restricted"
        cache_key = self._cache.generate_cache_key(query_dict, entitlement_scope)

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Execute Query
        result: NewsFeedResult = self._repository.get_feed(query)

        # Map to DTOs with entitlement enforcement
        article_dtos: List[NewsArticleDTO] = []
        for art in result.articles:
            dto = self._map_article_to_dto(art, is_entitled=is_entitled)
            article_dtos.append(dto)

        feed_response = NewsFeedResponseDTO(
            articles=article_dtos,
            total_count=result.total_count,
            next_cursor=result.next_cursor,
            has_more=result.has_more,
            as_of=datetime.datetime.now(datetime.timezone.utc),
            active_filters={k: v for k, v in query_dict.items() if v is not None},
        )

        self._cache.set(cache_key, feed_response)
        return feed_response

    def get_article(self, article_id: str, is_entitled: bool = True) -> NewsArticleDTO:
        art = self._repository.get_article(article_id)
        if not art:
            raise NewsArticleNotFoundError(f"News article '{article_id}' not found.")

        if art.availability_status == NewsAvailabilityStatus.WITHDRAWN:
            raise NewsArticleWithdrawnError(f"Article '{article_id}' has been withdrawn by publisher.")

        if art.availability_status == NewsAvailabilityStatus.SOURCE_RESTRICTED and not is_entitled:
            raise NewsArticleRestrictedError("Access to this article requires a higher subscription tier.")

        return self._map_article_to_dto(art, is_entitled=is_entitled)

    def get_article_revisions(self, article_id: str) -> List[NewsArticleRevision]:
        # Verify article exists
        self.get_article(article_id)
        return self._repository.get_article_revisions(article_id)

    def list_publishers(self) -> List[NewsPublisherDTO]:
        return [
            NewsPublisherDTO(
                publisher_id=p.publisher_id,
                canonical_name=p.canonical_name,
                verified_domain=p.verified_domain,
                publisher_type=p.publisher_type.value,
                country_code=p.country_code,
                official_website=p.official_website,
                attribution_required=p.attribution_required,
                status=p.status,
            )
            for p in self._repository.list_publishers()
        ]

    def list_sources(self) -> List[NewsSourceDTO]:
        return [
            NewsSourceDTO(
                source_id=s.source_id,
                provider_name=s.provider_name,
                provider_type=s.provider_type.value,
                supported_content_types=[t.value for t in s.supported_content_types],
                geographic_coverage=list(s.geographic_coverage),
                update_cadence_seconds=s.update_cadence_seconds,
                latency_class=s.latency_class,
                attribution_policy=s.attribution_policy,
                excerpt_policy=s.excerpt_policy,
                health_status=s.health_status,
                last_successful_ingestion=s.last_successful_ingestion,
            )
            for s in self._repository.list_sources()
        ]

    def list_categories(self) -> List[str]:
        return [c.value for c in NewsCategory]

    def get_coverage(self) -> NewsCoverageResponseDTO:
        cov = self._repository.get_coverage_report()
        return NewsCoverageResponseDTO(
            total_articles=cov.total_articles,
            active_sources=cov.active_sources,
            verified_publishers=cov.verified_publishers,
            supported_categories=cov.supported_categories,
            geographic_coverage=cov.geographic_coverage,
            latest_publication_time=cov.latest_publication_time,
            latest_ingestion_time=cov.latest_ingestion_time,
        )

    def get_freshness_status(self) -> NewsFreshnessResponseDTO:
        freshness = self._repository.get_freshness_status()
        return NewsFreshnessResponseDTO(
            status=freshness.status,
            latency_class=freshness.latency_class,
            last_successful_fetch=freshness.last_successful_fetch,
            latest_article_published=freshness.latest_article_published,
            latest_article_ingested=freshness.latest_article_ingested,
            staleness_seconds=freshness.staleness_seconds,
            active_source_count=freshness.active_source_count,
        )

    def get_entity_news(self, entity_id: str, limit: int = 20, is_entitled: bool = True) -> NewsFeedResponseDTO:
        query = NewsFeedQuery(entity_id=entity_id, limit=limit)
        return self.get_feed(query, is_entitled=is_entitled)

    def search_news(
        self,
        q: str,
        limit: int = 30,
        category: Optional[str] = None,
        is_entitled: bool = True,
    ) -> NewsFeedResponseDTO:
        clean_q = q.strip() if q else ""
        if len(clean_q) > 200:
            raise NewsSearchInvalidError("Search query exceeds maximum allowed length of 200 characters.")
        query = NewsFeedQuery(q=clean_q, category=category, limit=limit)
        return self.get_feed(query, is_entitled=is_entitled)

    def ingest_articles(self, request: NewsIngestionRequestDTO) -> NewsIngestionResponseDTO:
        """Processes an incoming ingestion payload."""
        articles_to_ingest: List[NewsArticle] = []
        errors: List[str] = []

        now_utc = datetime.datetime.now(datetime.timezone.utc)

        for item in request.articles:
            # Validate URL for SSRF safety
            is_safe, reason = validate_external_url(item.original_url)
            if not is_safe:
                errors.append(f"Rejected unsafe URL '{item.original_url}': {reason}")
                continue

            # Resolve publisher
            pub_obj = get_verified_publisher(item.publisher_id)
            pub_name = pub_obj.canonical_name if pub_obj else item.publisher_id

            clean_hl = sanitize_plain_text(item.headline)
            clean_ex = sanitize_plain_text(item.permitted_excerpt)
            canon_url = normalize_canonical_url(item.original_url)

            # Article type resolution
            try:
                art_type = NewsArticleType(item.article_type.upper())
            except ValueError:
                art_type = NewsArticleType.NEWS_REPORT

            # Category resolution
            categories = []
            for c_str in item.categories:
                try:
                    categories.append(NewsCategory(c_str.upper()))
                except ValueError:
                    pass

            origin = NewsDataOrigin(
                provider_id=request.source_id,
                extracted_at=now_utc,
                provider_internal_id=item.publisher_article_id,
            )

            art = NewsArticle(
                source_provider_id=request.source_id,
                publisher_id=item.publisher_id,
                publisher_name=pub_name,
                publisher_article_id=item.publisher_article_id,
                title=clean_hl,
                headline=clean_hl,
                publisher=pub_name,
                permitted_excerpt=clean_ex,
                summary=clean_ex,
                canonical_url=canon_url,
                original_url=item.original_url,
                language="en",
                article_type=art_type,
                published_at=normalize_timestamp(item.published_at),
                source_updated_at=normalize_timestamp(item.source_updated_at) if item.source_updated_at else None,
                first_seen_at=now_utc,
                ingested_at=now_utc,
                categories=tuple(categories),
                geographies=tuple(item.geographies),
                tags=tuple(item.tags),
                origin=origin,
            )
            articles_to_ingest.append(art)

        batch_result = self._repository.ingest_articles(articles_to_ingest)
        all_errors = errors + batch_result.errors

        return NewsIngestionResponseDTO(
            total_received=len(request.articles),
            new_articles=batch_result.new_articles,
            revisions=batch_result.revisions,
            duplicates_suppressed=batch_result.duplicates_suppressed,
            errors=all_errors,
        )

    def _map_article_to_dto(self, art: NewsArticle, is_entitled: bool = True) -> NewsArticleDTO:
        # If user is not entitled to excerpt, suppress excerpt text
        excerpt = art.permitted_excerpt
        if not is_entitled and art.licensing_status in (
            NewsLicensingStatus.SUBSCRIPTION_REQUIRED,
            NewsLicensingStatus.RESTRICTED,
        ):
            excerpt = None

        entity_dtos = [
            NewsEntityMentionDTO(
                entity_id=e.entity_id,
                entity_type=e.entity_type,
                canonical_name=e.canonical_name,
                ticker=e.ticker,
                exchange=e.exchange,
                country_code=e.country_code,
                mention_type=e.mention_type.value,
                resolution_method=e.resolution_method.value,
                verification_status=e.verification_status,
            )
            for e in art.linked_entities
        ]

        return NewsArticleDTO(
            article_id=art.article_id,
            source_provider_id=art.source_provider_id,
            publisher_id=art.publisher_id,
            publisher_name=art.publisher_name or art.publisher,
            publisher_article_id=art.publisher_article_id,
            headline=art.headline or art.title,
            permitted_excerpt=excerpt,
            original_url=art.original_url or str(art.url or ""),
            canonical_url=art.canonical_url,
            language=art.language,
            article_type=art.article_type,
            published_at=art.published_at,
            source_updated_at=art.source_updated_at,
            first_seen_at=art.first_seen_at or art.published_at,
            ingested_at=art.ingested_at or art.published_at,
            availability_status=art.availability_status,
            licensing_status=art.licensing_status,
            categories=[c.value for c in art.categories],
            linked_entities=entity_dtos,
            geographies=list(art.geographies),
            authors=list(art.authors),
            tags=list(art.tags),
            revision=art.revision,
            is_duplicate=art.is_duplicate,
            is_corrected=art.is_corrected,
            syndicated_from_id=art.syndicated_from_id,
            correction_details=art.correction_details,
        )


_news_service_singleton: Optional[NewsService] = None


def get_news_service() -> NewsService:
    global _news_service_singleton
    if _news_service_singleton is None:
        _news_service_singleton = NewsService()
    return _news_service_singleton
