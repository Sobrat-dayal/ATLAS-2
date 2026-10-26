"""Institutional News Domain Services (Stage 99)."""

from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional

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
    NewsCustomFeedNotFoundError,
    NewsDigestNotFoundError,
    NewsEventDataInconsistentError,
    NewsEventNotFoundError,
    NewsFinancialEventNotFoundError,
    NewsMonitoringRuleInvalidError,
    NewsMonitoringRuleNotFoundError,
    NewsSearchInvalidError,
    NewsStoryNotFoundError,
)
from atlas.news.events import (
    NewsEventEvidence,
    NewsFinancialEvent,
)
from atlas.news.market_reaction import ObservedNewsMarketContext
from atlas.news.monitoring import (
    CustomNewsFeed,
    NewsAlertMatch,
    NewsDigestRun,
    NewsDigestSubscription,
    NewsMonitoringRule,
    NewsSentimentCondition,
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
    NewsDiscoveryQuery,
    NewsEventQuery,
    NewsEventRepository,
    NewsFeedQuery,
    NewsFeedResult,
    NewsRepository,
    NewsStoryQuery,
)
from atlas.news.schemas import (
    # Stage 103 DTOs
    CreateCustomNewsFeedDTO,
    CreateNewsDigestSubscriptionDTO,
    CreateNewsMonitoringRuleDTO,
    CustomNewsFeedDTO,
    EntitySentimentAggregateDTO,
    EventAmountDTO,
    EventParticipantDTO,
    EventSentimentProfileDTO,
    FinancialEventTypeDefinitionDTO,
    MarketReactionRequestDTO,
    MonitoringHealthStatusDTO,
    NewsAlertFeedResponseDTO,
    NewsAlertMatchDTO,
    NewsArticleDTO,
    NewsCoverageResponseDTO,
    NewsDigestRunDTO,
    NewsDigestSubscriptionDTO,
    NewsDiscoveryQueryDTO,
    NewsDiscoveryResponseDTO,
    NewsEntityMentionDTO,
    NewsEntityRelevanceDTO,
    NewsEventEvidenceDTO,
    NewsEventFeedResponseDTO,
    NewsEventResponse,
    NewsEventRevisionDTO,
    NewsFacetsResponseDTO,
    NewsFeedResponseDTO,
    NewsFinancialEventDTO,
    NewsFreshnessResponseDTO,
    NewsIngestionRequestDTO,
    NewsIngestionResponseDTO,
    NewsMonitoringRuleDTO,
    NewsPublisherDTO,
    NewsRulePreviewRequestDTO,
    NewsRulePreviewResponseDTO,
    NewsRuleValidationRequestDTO,
    NewsRuleValidationResponseDTO,
    NewsSearchSuggestionDTO,
    NewsSentimentAnnotationDTO,
    NewsSentimentConditionDTO,
    NewsSourceDTO,
    NewsStoryFeedResponseDTO,
    NewsStoryThreadDTO,
    NewsTimelineBucketDTO,
    NewsTimelineRequestDTO,
    NewsTimelineResponseDTO,
    NewsTopicDTO,
    ObservedNewsMarketContextDTO,
    SentimentEvaluationResultDTO,
    SentimentEvidenceReferenceDTO,
    SentimentTimelineBucketDTO,
    SentimentTimelineResponseDTO,
    StorySentimentProfileDTO,
    UpdateCustomNewsFeedDTO,
    UpdateNewsDigestSubscriptionDTO,
    UpdateNewsMonitoringRuleDTO,
)
from atlas.news.sentiment import (
    EntitySentimentAggregate,
    NewsEntityRelevance,
    NewsSentimentAnnotation,
    evaluate_golden_benchmark,
)
from atlas.news.stories import NewsStoryThread
from atlas.news.topics import get_topic, list_topics
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

    @property
    def repository(self) -> NewsRepository:
        return self._repository

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

    def discover_news(
        self,
        query: NewsDiscoveryQueryDTO,
        is_entitled: bool = True,
    ) -> NewsDiscoveryResponseDTO:
        """
        Executes institutional multi-dimensional discovery search,
        category/topic/entity filtering, and optional facet calculation.
        """
        clean_q = query.query.strip() if query.query else None
        if clean_q and len(clean_q) > 200:
            raise NewsSearchInvalidError("Search query exceeds maximum allowed length of 200 characters.")

        repo_query = NewsDiscoveryQuery(
            mode=query.mode,
            query=clean_q,
            publisher_ids=query.publisher_ids,
            source_ids=query.source_ids,
            categories=query.categories,
            topic_ids=query.topic_ids,
            company_ids=query.company_ids,
            instrument_ids=query.instrument_ids,
            country_ids=query.country_ids,
            industry_ids=query.industry_ids,
            language_codes=query.language_codes,
            article_types=query.article_types,
            date_preset=query.date_preset,
            start_date=query.start_date,
            end_date=query.end_date,
            sort_order=query.sort_order,
            limit=query.limit,
            cursor=query.cursor,
        )

        result = self._repository.discover_news(repo_query)
        article_dtos = [self._map_article_to_dto(art, is_entitled=is_entitled) for art in result.articles]
        facets = self._repository.get_facets(repo_query)

        return NewsDiscoveryResponseDTO(
            articles=article_dtos,
            total_count=result.total_count,
            next_cursor=result.next_cursor,
            has_more=result.has_more,
            as_of=datetime.datetime.now(datetime.timezone.utc),
            active_filters=query.model_dump(exclude_none=True),
            facets=facets,
        )

    def get_facets(
        self,
        query: NewsDiscoveryQueryDTO,
        is_entitled: bool = True,
    ) -> NewsFacetsResponseDTO:
        repo_query = NewsDiscoveryQuery(
            mode=query.mode,
            query=query.query,
            publisher_ids=query.publisher_ids,
            source_ids=query.source_ids,
            categories=query.categories,
            topic_ids=query.topic_ids,
            company_ids=query.company_ids,
            instrument_ids=query.instrument_ids,
            country_ids=query.country_ids,
            industry_ids=query.industry_ids,
            language_codes=query.language_codes,
            article_types=query.article_types,
            date_preset=query.date_preset,
            start_date=query.start_date,
            end_date=query.end_date,
        )
        return self._repository.get_facets(repo_query)

    def get_timeline(
        self,
        request: NewsTimelineRequestDTO,
        is_entitled: bool = True,
    ) -> NewsTimelineResponseDTO:
        repo_query = NewsDiscoveryQuery(
            mode=request.query.mode,
            query=request.query.query,
            publisher_ids=request.query.publisher_ids,
            source_ids=request.query.source_ids,
            categories=request.query.categories,
            topic_ids=request.query.topic_ids,
            company_ids=request.query.company_ids,
            instrument_ids=request.query.instrument_ids,
            country_ids=request.query.country_ids,
            industry_ids=request.query.industry_ids,
            language_codes=request.query.language_codes,
            article_types=request.query.article_types,
            date_preset=request.query.date_preset,
            start_date=request.query.start_date,
            end_date=request.query.end_date,
            sort_order=request.query.sort_order,
        )
        timeline = self._repository.get_timeline(repo_query, interval=request.interval, tz_name=request.timezone)

        masked_buckets = []
        for b in timeline.buckets:
            masked_articles = [
                self._map_article_to_dto(
                    self._repository.get_article(a.article_id) or NewsArticle.model_validate(a),
                    is_entitled=is_entitled,
                )
                for a in b.articles
            ]
            masked_buckets.append(
                NewsTimelineBucketDTO(
                    bucket_id=b.bucket_id,
                    start_time=b.start_time,
                    end_time=b.end_time,
                    label=b.label,
                    article_count=b.article_count,
                    articles=masked_articles,
                )
            )

        return NewsTimelineResponseDTO(
            interval=timeline.interval,
            timezone=timeline.timezone,
            total_articles=timeline.total_articles,
            total_buckets=len(masked_buckets),
            buckets=masked_buckets,
            as_of=datetime.datetime.now(datetime.timezone.utc),
        )

    def list_topics(self) -> List[NewsTopicDTO]:
        return [
            NewsTopicDTO(
                topic_id=t.topic_id,
                canonical_name=t.canonical_name,
                description=t.description,
                parent_topic_id=t.parent_topic_id,
                category=t.category.value,
            )
            for t in list_topics()
        ]

    def get_topic(self, topic_id: str) -> NewsTopicDTO:
        top = get_topic(topic_id)
        if not top:
            raise NewsCategoryUnsupportedError(f"Topic '{topic_id}' not found.")
        return NewsTopicDTO(
            topic_id=top.topic_id,
            canonical_name=top.canonical_name,
            description=top.description,
            parent_topic_id=top.parent_topic_id,
            category=top.category.value,
        )

    def get_suggestions(self, prefix: str, limit: int = 8) -> List[NewsSearchSuggestionDTO]:
        return self._repository.get_suggestions(prefix, limit=limit)

    def get_watchlist_news(
        self,
        user_id: str,
        watchlist_id: str,
        watched_symbols: List[str],
        limit: int = 30,
        cursor: Optional[str] = None,
        is_entitled: bool = True,
    ) -> NewsFeedResponseDTO:
        """
        Discovers news articles linked to any of the user's watched symbols.
        Preserves user watchlist privacy with 0 watchlist mutations.
        """
        if not watched_symbols:
            return NewsFeedResponseDTO(
                articles=[],
                total_count=0,
                next_cursor=None,
                has_more=False,
                as_of=datetime.datetime.now(datetime.timezone.utc),
                active_filters={"watchlist_id": watchlist_id},
            )

        discovery_query = NewsDiscoveryQuery(
            mode="WATCHLIST",
            instrument_ids=[s.lower() for s in watched_symbols],
            limit=limit,
            cursor=cursor,
        )
        result = self._repository.discover_news(discovery_query)
        article_dtos = [self._map_article_to_dto(art, is_entitled=is_entitled) for art in result.articles]

        return NewsFeedResponseDTO(
            articles=article_dtos,
            total_count=result.total_count,
            next_cursor=result.next_cursor,
            has_more=result.has_more,
            as_of=datetime.datetime.now(datetime.timezone.utc),
            active_filters={"watchlist_id": watchlist_id, "symbol_count": len(watched_symbols)},
        )


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
            topic_ids=list(art.topic_ids),
            industries=list(art.industries),
            authors=list(art.authors),
            tags=list(art.tags),
            revision=art.revision,
            is_duplicate=art.is_duplicate,
            is_corrected=art.is_corrected,
            syndicated_from_id=art.syndicated_from_id,
            correction_details=art.correction_details,
        )

    # -----------------------------------------------------------------------
    # Stage 101 Story Intelligence Methods
    # -----------------------------------------------------------------------

    def list_stories(
        self,
        status: Optional[str] = None,
        entity_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        publisher_id: Optional[str] = None,
        q: Optional[str] = None,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        limit: int = 30,
        cursor: Optional[str] = None,
    ) -> NewsStoryFeedResponseDTO:
        query = NewsStoryQuery(
            status=status,
            entity_id=entity_id,
            topic_id=topic_id,
            publisher_id=publisher_id,
            q=q,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            cursor=cursor,
        )
        res = self._repository.list_stories(query)
        dtos = [self._map_story_to_dto(s) for s in res.stories]
        return NewsStoryFeedResponseDTO(
            stories=dtos,
            total_count=res.total_count,
            next_cursor=res.next_cursor,
            has_more=res.has_more,
            as_of=datetime.datetime.now(datetime.timezone.utc),
        )

    def get_story(self, story_id: str) -> NewsStoryThreadDTO:
        story = self._repository.get_story(story_id)
        if not story:
            raise NewsStoryNotFoundError(f"Story Thread '{story_id}' not found")
        return self._map_story_to_dto(story)

    def get_story_articles(self, story_id: str, is_entitled: bool = True) -> List[NewsArticleDTO]:
        story = self._repository.get_story(story_id)
        if not story:
            raise NewsStoryNotFoundError(f"Story Thread '{story_id}' not found")
        articles = self._repository.get_story_articles(story_id)
        return [self._map_article_to_dto(a, is_entitled=is_entitled) for a in articles]

    def get_story_events(self, story_id: str) -> List[NewsFinancialEventDTO]:
        story = self._repository.get_story(story_id)
        if not story:
            raise NewsStoryNotFoundError(f"Story Thread '{story_id}' not found")
        events = self._repository.get_story_events(story_id)
        return [self._map_event_to_dto(e) for e in events]

    def merge_stories(self, target_story_id: str, source_story_id: str) -> NewsStoryThreadDTO:
        target = self._repository.get_story(target_story_id)
        if not target:
            raise NewsStoryNotFoundError(f"Target Story Thread '{target_story_id}' not found")
        source = self._repository.get_story(source_story_id)
        if not source:
            raise NewsStoryNotFoundError(f"Source Story Thread '{source_story_id}' not found")
        merged = self._repository.merge_stories(target_story_id, source_story_id)
        return self._map_story_to_dto(merged)

    def split_story(
        self, story_id: str, article_ids_to_split: list[str], new_title: str
    ) -> tuple[NewsStoryThreadDTO, NewsStoryThreadDTO]:
        story = self._repository.get_story(story_id)
        if not story:
            raise NewsStoryNotFoundError(f"Story Thread '{story_id}' not found")
        parent, child = self._repository.split_story(story_id, article_ids_to_split, new_title)
        return self._map_story_to_dto(parent), self._map_story_to_dto(child)

    # -----------------------------------------------------------------------
    # Stage 101 Financial Event Classification Methods
    # -----------------------------------------------------------------------

    def list_events(
        self,
        event_type: Optional[str] = None,
        lifecycle_status: Optional[str] = None,
        assertion_status: Optional[str] = None,
        primary_entity_id: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        story_id: Optional[str] = None,
        q: Optional[str] = None,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        limit: int = 30,
        cursor: Optional[str] = None,
    ) -> NewsEventFeedResponseDTO:
        query = NewsEventQuery(
            event_type=event_type,
            lifecycle_status=lifecycle_status,
            assertion_status=assertion_status,
            primary_entity_id=primary_entity_id,
            related_entity_id=related_entity_id,
            story_id=story_id,
            q=q,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            cursor=cursor,
        )
        res = self._repository.list_events(query)
        dtos = [self._map_event_to_dto(e) for e in res.events]
        return NewsEventFeedResponseDTO(
            events=dtos,
            total_count=res.total_count,
            next_cursor=res.next_cursor,
            has_more=res.has_more,
            as_of=datetime.datetime.now(datetime.timezone.utc),
        )

    def get_event(self, event_id: str) -> NewsFinancialEventDTO:
        ev = self._repository.get_event(event_id)
        if not ev:
            raise NewsFinancialEventNotFoundError(f"Financial Event '{event_id}' not found")
        return self._map_event_to_dto(ev)

    def get_event_evidence(self, event_id: str, is_entitled: bool = True) -> List[NewsEventEvidenceDTO]:
        ev = self._repository.get_event(event_id)
        if not ev:
            raise NewsFinancialEventNotFoundError(f"Financial Event '{event_id}' not found")
        records = self._repository.get_event_evidence(event_id)
        return [self._map_evidence_to_dto(r, is_entitled=is_entitled) for r in records]

    def list_event_types(self) -> List[FinancialEventTypeDefinitionDTO]:
        types = self._repository.list_event_types()
        return [
            FinancialEventTypeDefinitionDTO(
                event_type_id=t.event_type_id,
                canonical_label=t.canonical_label,
                event_family=t.event_family,
                description=t.description,
                supported_roles=t.supported_roles,
                supported_amount_types=t.supported_amount_types,
            )
            for t in types
        ]

    def get_entity_events(self, entity_id: str, limit: int = 20) -> List[NewsFinancialEventDTO]:
        events = self._repository.get_entity_events(entity_id, limit=limit)
        return [self._map_event_to_dto(e) for e in events]

    # -----------------------------------------------------------------------
    # Stage 101 Mapping Helpers
    # -----------------------------------------------------------------------

    def _map_story_to_dto(self, story: NewsStoryThread) -> NewsStoryThreadDTO:
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
            for e in story.related_entities
        ]

        return NewsStoryThreadDTO(
            story_id=story.story_id,
            display_title=story.display_title,
            canonical_topic_label=story.canonical_topic_label,
            topic_ids=list(story.topic_ids),
            primary_entity_id=story.primary_entity_id,
            primary_entity_name=story.primary_entity_name,
            related_entities=entity_dtos,
            first_source_published_at=story.first_source_published_at,
            latest_source_published_at=story.latest_source_published_at,
            first_seen_at=story.first_seen_at,
            latest_activity_at=story.latest_activity_at,
            story_status=story.story_status,
            article_count=story.article_count,
            independent_publisher_count=story.independent_publisher_count,
            publishers=list(story.publishers),
            article_ids=list(story.article_ids),
            representative_article_id=story.representative_article_id,
            clustering_method=story.clustering_method,
            clustering_version=story.clustering_version,
            linked_event_ids=list(story.linked_event_ids),
        )

    def _map_event_to_dto(self, ev: NewsFinancialEvent, is_entitled: bool = True) -> NewsFinancialEventDTO:
        participant_dtos = [
            EventParticipantDTO(
                entity_id=p.entity_id,
                canonical_name=p.canonical_name,
                role=p.role,
                resolution_status=p.resolution_status,
            )
            for p in ev.participants
        ]

        amount_dtos = [
            EventAmountDTO(
                amount_type=a.amount_type,
                amount_value=a.amount_value,
                currency=a.currency,
                period=a.period,
                approximation_status=a.approximation_status,
                source_text=a.source_text,
            )
            for a in ev.amounts
        ]

        evidence_dtos = [
            self._map_evidence_to_dto(r, is_entitled=is_entitled)
            for r in ev.evidence_records
        ]

        revision_dtos = [
            NewsEventRevisionDTO(
                revision_id=rev.revision_id,
                event_id=rev.event_id,
                timestamp=rev.timestamp,
                previous_lifecycle_status=rev.previous_lifecycle_status,
                new_lifecycle_status=rev.new_lifecycle_status,
                previous_assertion_status=rev.previous_assertion_status,
                new_assertion_status=rev.new_assertion_status,
                change_reason=rev.change_reason,
                evidence_id=rev.evidence_id,
            )
            for rev in ev.revisions
        ]

        return NewsFinancialEventDTO(
            event_id=ev.event_id,
            event_type=ev.event_type,
            event_title=ev.event_title,
            primary_entity_id=ev.primary_entity_id,
            primary_entity_name=ev.primary_entity_name,
            lifecycle_status=ev.lifecycle_status,
            assertion_status=ev.assertion_status,
            event_date=ev.event_date,
            event_time_precision=ev.event_time_precision,
            announcement_time=ev.announcement_time,
            first_seen_at=ev.first_seen_at,
            last_evidence_updated_at=ev.last_evidence_updated_at,
            participants=participant_dtos,
            amounts=amount_dtos,
            supporting_article_ids=list(ev.supporting_article_ids),
            evidence_records=evidence_dtos,
            linked_story_ids=list(ev.linked_story_ids),
            revisions=revision_dtos,
            is_disputed=ev.is_disputed,
            is_corrected=ev.is_corrected,
        )

    def _map_evidence_to_dto(self, r: NewsEventEvidence, is_entitled: bool = True) -> NewsEventEvidenceDTO:
        excerpt = r.permitted_excerpt if is_entitled else None
        return NewsEventEvidenceDTO(
            evidence_id=r.evidence_id,
            event_id=r.event_id,
            article_id=r.article_id,
            publisher_id=r.publisher_id,
            publisher_name=r.publisher_name,
            source_provider_id=r.source_provider_id,
            evidence_type=r.evidence_type,
            headline=r.headline,
            permitted_excerpt=excerpt,
            source_published_at=r.source_published_at,
            first_observed_at=r.first_observed_at,
            is_verified_by_filing=r.is_verified_by_filing,
            filing_id=r.filing_id,
        )

    # -----------------------------------------------------------------------
    # Stage 102 Sentiment, Relevance & Market Context Services
    # -----------------------------------------------------------------------

    def get_article_sentiment(
        self, article_id: str, is_entitled: bool = True
    ) -> List[NewsSentimentAnnotationDTO]:
        article = self.repository._dedup.get_article(article_id)
        if not article:
            raise NewsArticleNotFoundError(article_id)
        if article.availability_status == NewsAvailabilityStatus.WITHDRAWN:
            raise NewsArticleWithdrawnError(article_id)

        annotations = self.repository.get_article_sentiment(article_id)
        return [self._map_sentiment_to_dto(a, is_entitled=is_entitled) for a in annotations]

    def get_entity_sentiment_aggregate(
        self, entity_id: str, days: int = 30, sources: Optional[List[str]] = None
    ) -> EntitySentimentAggregateDTO:
        agg = self.repository.get_entity_sentiment_aggregate(
            entity_id=entity_id, days=days, sources=sources
        )
        return self._map_sentiment_aggregate_to_dto(agg)

    def get_entity_sentiment_timeline(
        self, entity_id: str, interval: str = "DAY", days: int = 30
    ) -> SentimentTimelineResponseDTO:
        raw = self.repository.get_entity_sentiment_timeline(
            entity_id=entity_id, interval=interval, days=days
        )
        bucket_dtos = [
            SentimentTimelineBucketDTO(
                bucket_start=b.bucket_start,
                bucket_end=b.bucket_end,
                label=b.label,
                eligible_count=b.eligible_count,
                positive_count=b.positive_count,
                negative_count=b.negative_count,
                neutral_count=b.neutral_count,
                mixed_count=b.mixed_count,
                net_sentiment=b.net_sentiment,
            )
            for b in raw["buckets"]
        ]
        return SentimentTimelineResponseDTO(
            target_entity_id=raw["target_entity_id"],
            interval=raw["interval"],
            buckets=bucket_dtos,
            total_articles=raw["total_articles"],
            overall_net_sentiment=raw["overall_net_sentiment"],
            as_of=raw["as_of"],
        )

    def get_story_sentiment(self, story_id: str) -> StorySentimentProfileDTO:
        profile = self.repository.get_story_sentiment(story_id)
        if not profile:
            raise NewsStoryNotFoundError(story_id)
        return StorySentimentProfileDTO(
            story_id=profile.story_id,
            target_entity_id=profile.target_entity_id,
            distribution=profile.distribution,
            net_sentiment=profile.net_sentiment,
            eligible_article_count=profile.eligible_article_count,
            independent_source_count=profile.independent_source_count,
            evaluation_time=profile.evaluation_time,
        )

    def get_event_sentiment(self, event_id: str) -> EventSentimentProfileDTO:
        profile = self.repository.get_event_sentiment(event_id)
        if not profile:
            raise NewsFinancialEventNotFoundError(event_id)
        return EventSentimentProfileDTO(
            event_id=profile.event_id,
            target_entity_id=profile.target_entity_id,
            distribution=profile.distribution,
            net_sentiment=profile.net_sentiment,
            eligible_evidence_count=profile.eligible_evidence_count,
            assertion_status=profile.assertion_status,
            evaluation_time=profile.evaluation_time,
        )

    def get_entity_relevance(self, article_id: str) -> List[NewsEntityRelevanceDTO]:
        article = self.repository._dedup.get_article(article_id)
        if not article:
            raise NewsArticleNotFoundError(article_id)
        relevances = self.repository.get_entity_relevance(article_id)
        return [self._map_relevance_to_dto(r) for r in relevances]

    def get_observed_market_reaction(
        self, req: MarketReactionRequestDTO
    ) -> ObservedNewsMarketContextDTO:
        ctx = self.repository.get_observed_market_reaction(
            article_id_or_event_id=req.article_id_or_event_id,
            instrument_id=req.instrument_id,
            ticker=req.ticker,
            window=req.window,
            exchange=req.exchange,
            currency=req.currency,
        )
        return self._map_market_reaction_to_dto(ctx)

    def get_sentiment_evaluation(self) -> SentimentEvaluationResultDTO:
        result = evaluate_golden_benchmark()
        return SentimentEvaluationResultDTO(**result)

    def _map_sentiment_to_dto(
        self, a: NewsSentimentAnnotation, is_entitled: bool = True
    ) -> NewsSentimentAnnotationDTO:
        ev_dtos = [
            SentimentEvidenceReferenceDTO(
                evidence_id=e.evidence_id,
                article_revision_id=e.article_revision_id,
                evidence_scope=e.evidence_scope,
                text_span=e.text_span if is_entitled else None,
                rationale_code=e.rationale_code,
                source_rights=e.source_rights,
            )
            for e in a.evidence
        ]
        return NewsSentimentAnnotationDTO(
            annotation_id=a.annotation_id,
            article_id=a.article_id,
            article_revision_id=a.article_revision_id,
            target_entity_id=a.target_entity_id,
            target_entity_type=a.target_entity_type,
            target_canonical_name=a.target_canonical_name,
            target_ticker=a.target_ticker,
            sentiment_label=a.sentiment_label,
            sentiment_aspect=a.sentiment_aspect,
            sentiment_score=a.sentiment_score,
            confidence_score=a.confidence_score,
            classification_status=a.classification_status,
            classification_method=a.classification_method,
            classifier_version=a.classifier_version,
            taxonomy_version=a.taxonomy_version,
            evidence=ev_dtos,
            explanation=a.explanation if is_entitled else "Explanation restricted by content license.",
            source_published_at=a.source_published_at,
            analysis_created_at=a.analysis_created_at,
            retrospective_reprocessing=a.retrospective_reprocessing,
        )

    def _map_relevance_to_dto(self, r: NewsEntityRelevance) -> NewsEntityRelevanceDTO:
        return NewsEntityRelevanceDTO(
            relevance_id=r.relevance_id,
            article_id=r.article_id,
            article_revision_id=r.article_revision_id,
            entity_id=r.entity_id,
            entity_type=r.entity_type,
            canonical_name=r.canonical_name,
            ticker=r.ticker,
            relevance_class=r.relevance_class,
            relevance_score=r.relevance_score,
            evidence_source=r.evidence_source,
            is_primary_subject=r.is_primary_subject,
            is_direct_participant=r.is_direct_participant,
            source_published_at=r.source_published_at,
        )

    def _map_sentiment_aggregate_to_dto(
        self, agg: EntitySentimentAggregate
    ) -> EntitySentimentAggregateDTO:
        return EntitySentimentAggregateDTO(
            target_entity_id=agg.target_entity_id,
            target_canonical_name=agg.target_canonical_name,
            target_ticker=agg.target_ticker,
            evaluation_window_days=agg.evaluation_window_days,
            eligible_count=agg.eligible_count,
            positive_count=agg.positive_count,
            negative_count=agg.negative_count,
            neutral_count=agg.neutral_count,
            mixed_count=agg.mixed_count,
            insufficient_evidence_count=agg.insufficient_evidence_count,
            net_sentiment=agg.net_sentiment,
            unique_story_count=agg.unique_story_count,
            independent_publisher_count=agg.independent_publisher_count,
            top_aspects=agg.top_aspects,
            coverage_completeness=agg.coverage_completeness,
            methodology_version=agg.methodology_version,
            evaluation_time=agg.evaluation_time,
        )

    def _map_market_reaction_to_dto(
        self, ctx: ObservedNewsMarketContext
    ) -> ObservedNewsMarketContextDTO:
        return ObservedNewsMarketContextDTO(
            article_id_or_event_id=ctx.article_id_or_event_id,
            instrument_id=ctx.instrument_id,
            ticker=ctx.ticker,
            company_name=ctx.company_name,
            currency=ctx.currency,
            exchange=ctx.exchange,
            publication_time=ctx.publication_time,
            publication_precision=ctx.publication_precision,
            observation_window=ctx.observation_window,
            window_start_time=ctx.window_start_time,
            window_end_time=ctx.window_end_time,
            price_start=ctx.price_start,
            price_end=ctx.price_end,
            observed_return=ctx.observed_return,
            observed_return_percent=ctx.observed_return_percent,
            benchmark_instrument_id=ctx.benchmark_instrument_id,
            benchmark_name=ctx.benchmark_name,
            benchmark_return_percent=ctx.benchmark_return_percent,
            benchmark_relative_return_percent=ctx.benchmark_relative_return_percent,
            adjustment_policy=ctx.adjustment_policy,
            noncausal_disclaimer=ctx.noncausal_disclaimer,
            limitations=ctx.limitations,
        )

    # -----------------------------------------------------------------------
    # Stage 103: Monitoring Rules, Alerts, Custom Feeds & Digests
    # -----------------------------------------------------------------------

    def _map_rule_to_dto(self, rule: NewsMonitoringRule) -> NewsMonitoringRuleDTO:
        sc_dto = None
        if rule.sentiment_condition:
            sc_dto = NewsSentimentConditionDTO(
                sentiment_label=rule.sentiment_condition.sentiment_label,
                min_score=rule.sentiment_condition.min_score,
                aspect=rule.sentiment_condition.aspect,
            )
        return NewsMonitoringRuleDTO(
            rule_id=rule.rule_id,
            owner_user_id=rule.owner_user_id,
            name=rule.name,
            description=rule.description,
            rule_type=rule.rule_type,
            target_entity_ids=rule.target_entity_ids,
            target_tickers=rule.target_tickers,
            target_watchlist_ids=rule.target_watchlist_ids,
            target_topics=rule.target_topics,
            target_event_types=rule.target_event_types,
            target_publisher_ids=rule.target_publisher_ids,
            target_story_id=rule.target_story_id,
            target_custom_feed_id=rule.target_custom_feed_id,
            sentiment_condition=sc_dto,
            priority=rule.priority,
            trigger_policy=rule.trigger_policy,
            cooldown_minutes=rule.cooldown_minutes,
            delivery_channels=rule.delivery_channels,
            quiet_hours_enabled=rule.quiet_hours_enabled,
            quiet_hours_start_utc=rule.quiet_hours_start_utc,
            quiet_hours_end_utc=rule.quiet_hours_end_utc,
            user_timezone=rule.user_timezone,
            is_active=rule.is_active,
            rule_revision=rule.rule_revision,
            last_matched_at=rule.last_matched_at,
            match_count=rule.match_count,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )

    def _map_match_to_dto(self, match: NewsAlertMatch) -> NewsAlertMatchDTO:
        return NewsAlertMatchDTO(
            match_id=match.match_id,
            rule_id=match.rule_id,
            rule_name=match.rule_name,
            rule_revision=match.rule_revision,
            owner_user_id=match.owner_user_id,
            trigger_type=match.trigger_type,
            source_object_type=match.source_object_type,
            source_object_id=match.source_object_id,
            headline_or_title=match.headline_or_title,
            publisher_name=match.publisher_name,
            target_entity_id=match.target_entity_id,
            target_ticker=match.target_ticker,
            matched_conditions=match.matched_conditions,
            evidence_snippet=match.evidence_snippet,
            source_published_at=match.source_published_at,
            evaluated_at=match.evaluated_at,
            priority=match.priority,
            delivery_channel=match.delivery_channel,
            status=match.status,
            suppression_reason=match.suppression_reason,
            deduplication_key=match.deduplication_key,
        )

    def _map_custom_feed_to_dto(self, feed: CustomNewsFeed) -> CustomNewsFeedDTO:
        return CustomNewsFeedDTO(
            feed_id=feed.feed_id,
            owner_user_id=feed.owner_user_id,
            title=feed.title,
            description=feed.description,
            query_config=feed.query_config,
            is_alert_enabled=feed.is_alert_enabled,
            linked_rule_id=feed.linked_rule_id,
            created_at=feed.created_at,
            updated_at=feed.updated_at,
        )

    _map_feed_to_dto = _map_custom_feed_to_dto

    def _map_digest_sub_to_dto(self, sub: NewsDigestSubscription) -> NewsDigestSubscriptionDTO:
        return NewsDigestSubscriptionDTO(
            digest_id=sub.digest_id,
            owner_user_id=sub.owner_user_id,
            title=sub.title,
            cadence=sub.cadence,
            preferred_time_local=sub.preferred_time_local,
            timezone=sub.timezone,
            delivery_channel=sub.delivery_channel,
            include_empty=sub.include_empty,
            max_items=sub.max_items,
            target_entity_ids=sub.target_entity_ids,
            target_watchlist_ids=sub.target_watchlist_ids,
            target_topics=sub.target_topics,
            is_active=sub.is_active,
            last_run_at=sub.last_run_at,
            created_at=sub.created_at,
            updated_at=sub.updated_at,
        )

    def _map_digest_run_to_dto(self, run: NewsDigestRun) -> NewsDigestRunDTO:
        return NewsDigestRunDTO(
            run_id=run.run_id,
            digest_id=run.digest_id,
            owner_user_id=run.owner_user_id,
            title=run.title,
            interval_start=run.interval_start,
            interval_end=run.interval_end,
            executed_at=run.executed_at,
            eligible_article_count=run.eligible_article_count,
            unique_story_count=run.unique_story_count,
            verified_event_count=run.verified_event_count,
            status=run.status,
            summary_sections=run.summary_sections,
            attribution_disclaimer=run.attribution_disclaimer,
        )

    def create_monitoring_rule(
        self,
        dto: CreateNewsMonitoringRuleDTO,
        owner_user_id: str,
    ) -> NewsMonitoringRuleDTO:
        if not dto.name or len(dto.name.strip()) < 2:
            raise NewsMonitoringRuleInvalidError("Rule name must be at least 2 characters.")

        sc = None
        if dto.sentiment_condition:
            sc = NewsSentimentCondition(
                sentiment_label=dto.sentiment_condition.sentiment_label,
                min_score=dto.sentiment_condition.min_score,
                aspect=dto.sentiment_condition.aspect,
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        rule = NewsMonitoringRule(
            rule_id=f"rule-{uuid.uuid4().hex[:8]}",
            owner_user_id=owner_user_id,
            name=dto.name.strip(),
            description=dto.description.strip() if dto.description else None,
            rule_type=dto.rule_type,
            target_entity_ids=dto.target_entity_ids,
            target_tickers=[t.upper() for t in dto.target_tickers],
            target_watchlist_ids=dto.target_watchlist_ids,
            target_topics=[top.upper() for top in dto.target_topics],
            target_event_types=[et.upper() for et in dto.target_event_types],
            target_publisher_ids=dto.target_publisher_ids,
            target_story_id=dto.target_story_id,
            target_custom_feed_id=dto.target_custom_feed_id,
            sentiment_condition=sc,
            priority=dto.priority,
            trigger_policy=dto.trigger_policy,
            cooldown_minutes=dto.cooldown_minutes,
            delivery_channels=dto.delivery_channels,
            quiet_hours_enabled=dto.quiet_hours_enabled,
            quiet_hours_start_utc=dto.quiet_hours_start_utc,
            quiet_hours_end_utc=dto.quiet_hours_end_utc,
            user_timezone=dto.user_timezone,
            is_active=dto.is_active,
            created_at=now,
            updated_at=now,
        )

        created = self._repository.create_monitoring_rule(rule)
        return self._map_rule_to_dto(created)

    def get_monitoring_rule(self, rule_id: str, owner_user_id: str) -> NewsMonitoringRuleDTO:
        rule = self._repository.get_monitoring_rule(rule_id, owner_user_id)
        if not rule:
            raise NewsMonitoringRuleNotFoundError(rule_id)
        return self._map_rule_to_dto(rule)

    def list_monitoring_rules(
        self, owner_user_id: str, active_only: bool = False
    ) -> List[NewsMonitoringRuleDTO]:
        rules = self._repository.list_monitoring_rules(owner_user_id, active_only=active_only)
        return [self._map_rule_to_dto(r) for r in rules]

    def update_monitoring_rule(
        self,
        rule_id: str,
        owner_user_id: str,
        dto: UpdateNewsMonitoringRuleDTO,
    ) -> NewsMonitoringRuleDTO:
        updates = dto.model_dump(exclude_unset=True)
        if "sentiment_condition" in updates and updates["sentiment_condition"]:
            sc_data = updates["sentiment_condition"]
            updates["sentiment_condition"] = NewsSentimentCondition(
                sentiment_label=sc_data.get("sentiment_label"),
                min_score=sc_data.get("min_score"),
                aspect=sc_data.get("aspect"),
            )
        updated = self._repository.update_monitoring_rule(rule_id, owner_user_id, updates)
        return self._map_rule_to_dto(updated)

    def delete_monitoring_rule(self, rule_id: str, owner_user_id: str) -> bool:
        return self._repository.delete_monitoring_rule(rule_id, owner_user_id)

    def validate_monitoring_rule(
        self, req: NewsRuleValidationRequestDTO
    ) -> NewsRuleValidationResponseDTO:
        rule = req.rule
        errors: List[str] = []
        warnings: List[str] = []

        if not rule.name or len(rule.name.strip()) < 2:
            errors.append("Rule name must be at least 2 characters.")

        if rule.rule_type.value == "COMPANY" and not rule.target_entity_ids and not rule.target_tickers:
            errors.append("Company monitoring rules must specify at least one target entity ID or ticker.")

        if rule.rule_type.value == "TOPIC" and not rule.target_topics:
            errors.append("Topic monitoring rules must specify at least one target topic.")

        if rule.rule_type.value == "WATCHLIST" and not rule.target_watchlist_ids:
            errors.append("Watchlist monitoring rules must specify at least one target watchlist ID.")

        if rule.cooldown_minutes < 0 or rule.cooldown_minutes > 1440:
            errors.append("Cooldown minutes must be between 0 and 1440 (24 hours).")

        if not rule.delivery_channels:
            warnings.append("No delivery channels selected; alerts will be generated but not delivered.")

        if rule.sentiment_condition and rule.sentiment_condition.min_score is not None:
            if rule.sentiment_condition.min_score < 0.0 or rule.sentiment_condition.min_score > 1.0:
                errors.append("Sentiment minimum confidence score must be between 0.0 and 1.0.")

        is_valid = len(errors) == 0
        coverage = "Comprehensive" if is_valid and not warnings else ("Degraded" if warnings else "Invalid")

        return NewsRuleValidationResponseDTO(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            estimated_coverage=f"{coverage} Coverage across verified institutional providers.",
        )

    def preview_monitoring_rule(
        self, req: NewsRulePreviewRequestDTO
    ) -> NewsRulePreviewResponseDTO:
        rule_dto = req.rule
        sc = None
        if rule_dto.sentiment_condition:
            sc = NewsSentimentCondition(
                sentiment_label=rule_dto.sentiment_condition.sentiment_label,
                min_score=rule_dto.sentiment_condition.min_score,
                aspect=rule_dto.sentiment_condition.aspect,
            )

        transient_rule = NewsMonitoringRule(
            rule_id="preview-rule",
            owner_user_id="transient-preview",
            name=rule_dto.name,
            rule_type=rule_dto.rule_type,
            target_entity_ids=rule_dto.target_entity_ids,
            target_tickers=[t.upper() for t in rule_dto.target_tickers],
            target_watchlist_ids=rule_dto.target_watchlist_ids,
            target_topics=[top.upper() for top in rule_dto.target_topics],
            target_event_types=[et.upper() for et in rule_dto.target_event_types],
            target_publisher_ids=rule_dto.target_publisher_ids,
            target_story_id=rule_dto.target_story_id,
            target_custom_feed_id=rule_dto.target_custom_feed_id,
            sentiment_condition=sc,
            priority=rule_dto.priority,
            trigger_policy=rule_dto.trigger_policy,
            cooldown_minutes=0,
            delivery_channels=rule_dto.delivery_channels,
            is_active=True,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )

        all_articles = list(self._repository._dedup._articles_by_id.values())
        matched_samples: List[Dict[str, Any]] = []

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        for article in sorted(all_articles, key=lambda a: a.published_at, reverse=True):
            sentiment_anns = self._repository._sentiment_by_article.get(article.article_id, [])
            match = self._repository._rule_matcher.match_article(
                rule=transient_rule,
                article=article,
                sentiment_annotations=sentiment_anns,
                current_time_utc=now_utc,
            )
            if match:
                matched_samples.append({
                    "article_id": article.article_id,
                    "headline": article.headline,
                    "publisher_name": article.publisher_name,
                    "published_at": article.published_at.isoformat(),
                    "matched_conditions": match.matched_conditions,
                    "evidence_snippet": match.evidence_snippet,
                })
                if len(matched_samples) >= req.limit:
                    break

        return NewsRulePreviewResponseDTO(
            matched_articles=matched_samples,
            total_potential_matches=len(matched_samples),
            sample_coverage_window_hours=72,
            disclaimer="Historical preview results reflect current news data and do not trigger retroactive notifications.",
        )

    def list_alert_matches(
        self,
        owner_user_id: str,
        limit: int = 50,
        rule_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> NewsAlertFeedResponseDTO:
        matches = self._repository.list_alert_matches(
            owner_user_id=owner_user_id,
            limit=limit,
            rule_id=rule_id,
            status=status,
        )
        dtos = [self._map_match_to_dto(m) for m in matches]
        delivered_count = sum(1 for d in dtos if d.status.value == "DELIVERED")
        suppressed_count = sum(1 for d in dtos if d.status.value != "DELIVERED")

        return NewsAlertFeedResponseDTO(
            alerts=dtos,
            total_count=len(dtos),
            delivered_count=delivered_count,
            suppressed_count=suppressed_count,
            as_of=datetime.datetime.now(datetime.timezone.utc),
        )

    def get_monitoring_health(self) -> MonitoringHealthStatusDTO:
        health = self._repository.get_monitoring_health()
        return MonitoringHealthStatusDTO(
            is_healthy=health.is_healthy,
            active_rules_count=health.active_rules_count,
            evaluated_matches_24h=health.evaluated_matches_24h,
            delivered_alerts_24h=health.delivered_alerts_24h,
            delivery_success_rate=health.delivery_success_rate,
            last_processed_ingestion_watermark=health.last_processed_ingestion_watermark,
            queue_lag_seconds=health.queue_lag_seconds,
            p95_evaluation_latency_ms=health.p95_evaluation_latency_ms,
            as_of=health.as_of,
        )

    def create_custom_feed(
        self, dto: CreateCustomNewsFeedDTO, owner_user_id: str
    ) -> CustomNewsFeedDTO:
        if not dto.title or len(dto.title.strip()) < 2:
            raise NewsMonitoringRuleInvalidError("Custom feed title must be at least 2 characters.")

        now = datetime.datetime.now(datetime.timezone.utc)
        feed = CustomNewsFeed(
            feed_id=f"feed-{uuid.uuid4().hex[:8]}",
            owner_user_id=owner_user_id,
            title=dto.title.strip(),
            description=dto.description.strip() if dto.description else None,
            query_config=dto.query_config,
            is_alert_enabled=dto.is_alert_enabled,
            created_at=now,
            updated_at=now,
        )
        created = self._repository.create_custom_feed(feed)
        return self._map_feed_to_dto(created)

    def get_custom_feed(self, feed_id: str, owner_user_id: str) -> CustomNewsFeedDTO:
        feed = self._repository.get_custom_feed(feed_id, owner_user_id)
        if not feed:
            raise NewsCustomFeedNotFoundError(feed_id)
        return self._map_feed_to_dto(feed)

    def list_custom_feeds(self, owner_user_id: str) -> List[CustomNewsFeedDTO]:
        feeds = self._repository.list_custom_feeds(owner_user_id)
        return [self._map_feed_to_dto(f) for f in feeds]

    def update_custom_feed(
        self, feed_id: str, owner_user_id: str, dto: UpdateCustomNewsFeedDTO
    ) -> CustomNewsFeedDTO:
        updates = dto.model_dump(exclude_unset=True)
        updated = self._repository.update_custom_feed(feed_id, owner_user_id, updates)
        return self._map_feed_to_dto(updated)

    def delete_custom_feed(self, feed_id: str, owner_user_id: str) -> bool:
        return self._repository.delete_custom_feed(feed_id, owner_user_id)

    def execute_custom_feed(
        self, feed_id: str, owner_user_id: str, limit: int = 30
    ) -> NewsFeedResponseDTO:
        feed = self._repository.get_custom_feed(feed_id, owner_user_id)
        if not feed:
            raise NewsCustomFeedNotFoundError(feed_id)
        qc = feed.query_config
        query = NewsFeedQuery(
            q=qc.get("q"),
            category=qc.get("category"),
            source_id=qc.get("source_id"),
            publisher_id=qc.get("publisher_id"),
            entity_id=qc.get("entity_id"),
            geography=qc.get("geography"),
            limit=limit,
        )
        return self.get_feed(query)

    def create_digest_subscription(
        self, dto: CreateNewsDigestSubscriptionDTO, owner_user_id: str
    ) -> NewsDigestSubscriptionDTO:
        if not dto.title or len(dto.title.strip()) < 2:
            raise NewsMonitoringRuleInvalidError("Digest title must be at least 2 characters.")

        now = datetime.datetime.now(datetime.timezone.utc)
        sub = NewsDigestSubscription(
            digest_id=f"digest-{uuid.uuid4().hex[:8]}",
            owner_user_id=owner_user_id,
            title=dto.title.strip(),
            cadence=dto.cadence,
            preferred_time_local=dto.preferred_time_local,
            timezone=dto.timezone,
            delivery_channel=dto.delivery_channel,
            include_empty=dto.include_empty,
            max_items=dto.max_items,
            target_entity_ids=dto.target_entity_ids,
            target_watchlist_ids=dto.target_watchlist_ids,
            target_topics=dto.target_topics,
            is_active=dto.is_active,
            created_at=now,
            updated_at=now,
        )
        created = self._repository.create_digest_subscription(sub)
        return self._map_digest_sub_to_dto(created)

    def get_digest_subscription(self, digest_id: str, owner_user_id: str) -> NewsDigestSubscriptionDTO:
        sub = self._repository.get_digest_subscription(digest_id, owner_user_id)
        if not sub:
            raise NewsDigestNotFoundError(digest_id)
        return self._map_digest_sub_to_dto(sub)

    def list_digest_subscriptions(self, owner_user_id: str) -> List[NewsDigestSubscriptionDTO]:
        subs = self._repository.list_digest_subscriptions(owner_user_id)
        return [self._map_digest_sub_to_dto(s) for s in subs]

    def update_digest_subscription(
        self, digest_id: str, owner_user_id: str, dto: UpdateNewsDigestSubscriptionDTO
    ) -> NewsDigestSubscriptionDTO:
        updates = dto.model_dump(exclude_unset=True)
        updated = self._repository.update_digest_subscription(digest_id, owner_user_id, updates)
        return self._map_digest_sub_to_dto(updated)

    def delete_digest_subscription(self, digest_id: str, owner_user_id: str) -> bool:
        return self._repository.delete_digest_subscription(digest_id, owner_user_id)

    def preview_digest(self, digest_id: str, owner_user_id: str) -> NewsDigestRunDTO:
        sub = self._repository.get_digest_subscription(digest_id, owner_user_id)
        if not sub:
            raise NewsDigestNotFoundError(digest_id)

        all_articles = list(self._repository._dedup._articles_by_id.values())
        all_stories = self._repository._stories_by_id
        all_events = self._repository._events_by_id

        run = self._repository._digest_engine.generate_digest(
            subscription=sub,
            all_articles=all_articles,
            all_stories=all_stories,
            all_events=all_events,
        )
        return self._map_digest_run_to_dto(run)

    def generate_and_dispatch_digest(
        self, digest_id: str, owner_user_id: str, session: Optional[Session] = None
    ) -> NewsDigestRunDTO:
        sub = self._repository.get_digest_subscription(digest_id, owner_user_id)
        if not sub:
            raise NewsDigestNotFoundError(digest_id)

        all_articles = list(self._repository._dedup._articles_by_id.values())
        all_stories = self._repository._stories_by_id
        all_events = self._repository._events_by_id

        run = self._repository._digest_engine.generate_digest(
            subscription=sub,
            all_articles=all_articles,
            all_stories=all_stories,
            all_events=all_events,
        )

        self._repository.record_digest_run(run)
        sub.last_run_at = run.executed_at

        # Optional Stage 49 notification dispatch if session is available
        if session is not None and run.eligible_article_count > 0:
            try:
                from atlas.notifications.enums import NotificationActionKind, NotificationCategory
                from atlas.notifications.schemas import CreateNotification
                from atlas.notifications.service import NotificationService

                try:
                    recip_uuid = uuid.UUID(owner_user_id)
                except (ValueError, AttributeError):
                    recip_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(owner_user_id))

                notif_svc = NotificationService(session)
                notif_svc.create_notification(
                    CreateNotification(
                        recipient_user_id=recip_uuid,
                        category=NotificationCategory.MARKET,
                        title=f"Digest: {sub.title[:100]}",
                        message=f"{run.eligible_article_count} articles across {run.unique_story_count} stories compiled.",
                        producer_key="news_monitoring",
                        dedupe_key=f"digest-{sub.digest_id}-{run.run_id}",
                        action_kind=NotificationActionKind.INTERNAL_ROUTE,
                        action_route="/news",
                    )
                )
            except Exception:
                pass  # Notifications service failure must not break digest generation

        return self._map_digest_run_to_dto(run)

    def list_digest_runs(
        self, owner_user_id: str, digest_id: Optional[str] = None, limit: int = 20
    ) -> List[NewsDigestRunDTO]:
        runs = self._repository.list_digest_runs(owner_user_id, digest_id=digest_id, limit=limit)
        return [self._map_digest_run_to_dto(r) for r in runs]


_news_service_singleton: Optional[NewsService] = None


def get_news_service() -> NewsService:
    global _news_service_singleton
    if _news_service_singleton is None:
        _news_service_singleton = NewsService()
    return _news_service_singleton
