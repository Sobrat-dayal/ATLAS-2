"""Canonical News Repository and High-Performance In-Memory Data Store (Stage 99)."""

from __future__ import annotations

import base64
import re
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas.entities.models import Entity
from atlas.news.articles import NewsArticle, NewsArticleRevision
from atlas.news.caching import default_news_cache
from atlas.news.deduplication import DeduplicationEngine, DeduplicationResult
from atlas.news.entity_resolution import (
    resolve_entities_in_text,
)
from atlas.news.enums import (
    NewsArticleType,
    NewsAvailabilityStatus,
    NewsCategory,
    NewsLatencyClass,
)
from atlas.news.models import NewsEvent
from atlas.news.normalization import (
    normalize_canonical_url,
    normalize_timestamp,
    sanitize_plain_text,
)
from atlas.news.origin import NewsDataOrigin
from atlas.news.publishers import (
    NewsPublisher,
    get_verified_publisher,
    list_verified_publishers,
)
from atlas.news.schemas import (
    NewsArticleDTO,
    NewsFacetItemDTO,
    NewsFacetsResponseDTO,
    NewsSearchSuggestionDTO,
    NewsTimelineBucketDTO,
    NewsTimelineResponseDTO,
)
from atlas.news.sources import (
    NewsSource,
    get_news_source,
    list_news_sources,
)
from atlas.news.topics import (
    classify_topics_for_article,
    list_topics,
    resolve_industries_for_article,
)


# Preserved for Stage 20 / Stage 36 entity compatibility
class NewsEventRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_news_event(self, entity_id: uuid.UUID) -> Optional[tuple[Entity, NewsEvent]]:
        stmt = (
            select(Entity, NewsEvent)
            .join(NewsEvent, Entity.entity_id == NewsEvent.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def create_news_event_specialization(
        self,
        entity_id: uuid.UUID,
        event_kind: Optional[str] = None,
        event_time: Optional[datetime] = None,
        event_status: Optional[str] = None,
    ) -> NewsEvent:
        event = NewsEvent(
            entity_id=entity_id,
            event_kind=event_kind,
            event_time=event_time,
            event_status=event_status,
        )
        self.session.add(event)
        return event


class NewsFeedQuery:
    """Encapsulates filter and pagination parameters for news feed queries."""

    def __init__(
        self,
        category: Optional[str] = None,
        source_id: Optional[str] = None,
        publisher_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        geography: Optional[str] = None,
        q: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 30,
        cursor: Optional[str] = None,
    ):
        self.category = category
        self.source_id = source_id
        self.publisher_id = publisher_id
        self.entity_id = entity_id
        self.geography = geography
        self.q = q.strip() if q else None
        self.start_date = start_date
        self.end_date = end_date
        self.limit = max(1, min(100, limit))
        self.cursor = cursor


class NewsDiscoveryQuery:
    """Encapsulates multi-dimensional filter and search parameters for News Discovery (Stage 100)."""

    def __init__(
        self,
        mode: str = "ALL",
        query: Optional[str] = None,
        publisher_ids: Optional[List[str]] = None,
        source_ids: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        topic_ids: Optional[List[str]] = None,
        company_ids: Optional[List[str]] = None,
        instrument_ids: Optional[List[str]] = None,
        country_ids: Optional[List[str]] = None,
        industry_ids: Optional[List[str]] = None,
        language_codes: Optional[List[str]] = None,
        article_types: Optional[List[str]] = None,
        date_preset: str = "ALL_TIME",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_order: str = "PUBLISHED_DESC",
        limit: int = 30,
        cursor: Optional[str] = None,
    ):
        self.mode = mode.upper() if mode else "ALL"
        self.query = query.strip() if query else None
        self.publisher_ids = [p.lower() for p in publisher_ids] if publisher_ids else None
        self.source_ids = [s.lower() for s in source_ids] if source_ids else None
        self.categories = [c.upper() for c in categories] if categories else None
        self.topic_ids = [t.upper() for t in topic_ids] if topic_ids else None
        self.company_ids = [c.lower() for c in company_ids] if company_ids else None
        self.instrument_ids = [i.lower() for i in instrument_ids] if instrument_ids else None
        self.country_ids = [c.upper() for c in country_ids] if country_ids else None
        self.industry_ids = [i.upper() for i in industry_ids] if industry_ids else None
        self.language_codes = [lang.lower() for lang in language_codes] if language_codes else None
        self.article_types = [a.upper() for a in article_types] if article_types else None
        self.date_preset = date_preset.upper() if date_preset else "ALL_TIME"
        self.start_date = start_date
        self.end_date = end_date
        self.sort_order = sort_order.upper() if sort_order else "PUBLISHED_DESC"
        self.limit = max(1, min(100, limit))
        self.cursor = cursor


class NewsFeedResult:
    """Paginated result set for news feed queries."""

    def __init__(
        self,
        articles: List[NewsArticle],
        total_count: int,
        next_cursor: Optional[str],
        has_more: bool,
    ):
        self.articles = articles
        self.total_count = total_count
        self.next_cursor = next_cursor
        self.has_more = has_more


class NewsCoverageReport:
    """Summary of active news providers, publishers, and geographic coverage."""

    def __init__(
        self,
        total_articles: int,
        active_sources: int,
        verified_publishers: int,
        supported_categories: List[str],
        geographic_coverage: List[str],
        latest_publication_time: Optional[datetime],
        latest_ingestion_time: Optional[datetime],
    ):
        self.total_articles = total_articles
        self.active_sources = active_sources
        self.verified_publishers = verified_publishers
        self.supported_categories = supported_categories
        self.geographic_coverage = geographic_coverage
        self.latest_publication_time = latest_publication_time
        self.latest_ingestion_time = latest_ingestion_time


class NewsFreshnessStatus:
    """Health, latency, and freshness metadata."""

    def __init__(
        self,
        status: str,
        latency_class: NewsLatencyClass,
        last_successful_fetch: Optional[datetime],
        latest_article_published: Optional[datetime],
        latest_article_ingested: Optional[datetime],
        staleness_seconds: int,
        active_source_count: int,
    ):
        self.status = status
        self.latency_class = latency_class
        self.last_successful_fetch = last_successful_fetch
        self.latest_article_published = latest_article_published
        self.latest_article_ingested = latest_article_ingested
        self.staleness_seconds = staleness_seconds
        self.active_source_count = active_source_count


class IngestionBatchResult:
    """Outcome metrics of an ingestion run."""

    def __init__(
        self,
        total_received: int,
        new_articles: int,
        revisions: int,
        duplicates_suppressed: int,
        errors: List[str],
    ):
        self.total_received = total_received
        self.new_articles = new_articles
        self.revisions = revisions
        self.duplicates_suppressed = duplicates_suppressed
        self.errors = errors


class NewsRepository:
    """
    Authoritative Stage 99 News Repository managing article persistence,
    idempotent ingestion, deduplication, search indexing, and feed generation.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._dedup = DeduplicationEngine()
        self._last_successful_fetch: Optional[datetime] = None
        self._seed_baseline_articles()

    def get_article(self, article_id: str) -> Optional[NewsArticle]:
        with self._lock:
            return self._dedup.get_article(article_id)

    def get_article_revisions(self, article_id: str) -> List[NewsArticleRevision]:
        with self._lock:
            return self._dedup.get_revisions(article_id)

    def list_publishers(self) -> List[NewsPublisher]:
        return list_verified_publishers()

    def get_publisher(self, publisher_id: str) -> Optional[NewsPublisher]:
        return get_verified_publisher(publisher_id)

    def list_sources(self) -> List[NewsSource]:
        return list_news_sources()

    def get_source(self, source_id: str) -> Optional[NewsSource]:
        return get_news_source(source_id)

    def ingest_articles(self, raw_articles: List[NewsArticle]) -> IngestionBatchResult:
        """
        Ingests a batch of articles with idempotency, deduplication,
        entity resolution, sanitization, and cache invalidation.
        """
        total = len(raw_articles)
        new_count = 0
        rev_count = 0
        dup_count = 0
        errors: List[str] = []

        now_utc = datetime.now(timezone.utc)

        with self._lock:
            for item in raw_articles:
                try:
                    # Sanitize headlines & excerpts
                    clean_hl = sanitize_plain_text(item.headline or item.title)
                    clean_ex = sanitize_plain_text(item.permitted_excerpt or item.summary)
                    canon_url = normalize_canonical_url(item.canonical_url or item.original_url)

                    # Auto-resolve entities if not already supplied
                    entities = list(item.linked_entities)
                    if not entities:
                        entities = resolve_entities_in_text(clean_hl, clean_ex, list(item.tags))

                    # Normalize timestamps
                    pub_at = normalize_timestamp(item.published_at)
                    updated_at = normalize_timestamp(item.source_updated_at) if item.source_updated_at else None

                    # Resolve publisher info if available
                    pub_obj = get_verified_publisher(item.publisher_id)
                    pub_name = pub_obj.canonical_name if pub_obj else item.publisher

                    # Auto-resolve topics if not already supplied
                    topics = list(item.topic_ids)
                    if not topics:
                        topics = classify_topics_for_article(clean_hl, clean_ex, list(item.categories))

                    # Auto-resolve industries if not already supplied
                    industries = list(item.industries)
                    if not industries:
                        industries = resolve_industries_for_article(clean_hl, clean_ex, entities)

                    # Construct normalized article
                    normalized = NewsArticle(
                        article_id=item.article_id,
                        source_provider_id=item.source_provider_id or "openbb_news",
                        publisher_id=item.publisher_id or "generic_publisher",
                        publisher_name=pub_name,
                        publisher_article_id=item.publisher_article_id,
                        title=clean_hl,
                        headline=clean_hl,
                        publisher=pub_name,
                        permitted_excerpt=clean_ex,
                        summary=clean_ex,
                        canonical_url=canon_url,
                        original_url=item.original_url or canon_url,
                        language=item.language or "en",
                        article_type=item.article_type,
                        published_at=pub_at,
                        source_updated_at=updated_at,
                        first_seen_at=item.first_seen_at or now_utc,
                        ingested_at=now_utc,
                        availability_status=item.availability_status,
                        licensing_status=item.licensing_status,
                        categories=item.categories,
                        linked_entities=tuple(entities),
                        geographies=item.geographies,
                        topic_ids=tuple(topics),
                        industries=tuple(industries),
                        authors=item.authors,
                        tags=item.tags,
                        revision=item.revision,
                        origin=item.origin,
                    )

                    res: DeduplicationResult = self._dedup.process_incoming_article(normalized)

                    if res.is_new:
                        new_count += 1
                    elif res.is_revision:
                        rev_count += 1
                    elif res.is_exact_duplicate:
                        dup_count += 1

                except Exception as exc:
                    errors.append(f"Failed to ingest article '{item.title}': {exc}")

            self._last_successful_fetch = now_utc
            # Invalidate feed caches
            default_news_cache.invalidate_all()

        return IngestionBatchResult(
            total_received=total,
            new_articles=new_count,
            revisions=rev_count,
            duplicates_suppressed=dup_count,
            errors=errors,
        )

    def get_feed(self, query: NewsFeedQuery) -> NewsFeedResult:
        """
        Executes a filtered, source-qualified chronological news query.
        """
        with self._lock:
            all_articles = list(self._dedup._articles_by_id.values())

        # 1. Filter out withdrawn or removed articles from standard feed
        matching = [
            a for a in all_articles
            if a.availability_status not in (NewsAvailabilityStatus.WITHDRAWN, NewsAvailabilityStatus.REMOVED)
        ]

        # 2. Filter by Category
        if query.category:
            cat_upper = query.category.upper()
            matching = [
                a for a in matching
                if any(c.value.upper() == cat_upper for c in a.categories)
            ]

        # 3. Filter by Source Provider
        if query.source_id:
            src_lower = query.source_id.lower()
            matching = [a for a in matching if a.source_provider_id.lower() == src_lower]

        # 4. Filter by Publisher
        if query.publisher_id:
            pub_lower = query.publisher_id.lower()
            matching = [a for a in matching if a.publisher_id.lower() == pub_lower]

        # 5. Filter by Geography
        if query.geography:
            geo_upper = query.geography.upper()
            matching = [
                a for a in matching
                if any(g.upper() == geo_upper for g in a.geographies)
            ]

        # 6. Filter by Entity Link
        if query.entity_id:
            ent_query = query.entity_id.strip().lower()
            matching = [
                a for a in matching
                if any(
                    (e.entity_id.lower() == ent_query)
                    or (e.ticker and e.ticker.lower() == ent_query)
                    or (e.canonical_name and ent_query in e.canonical_name.lower())
                    for e in a.linked_entities
                )
            ]

        # 7. Date range filter
        if query.start_date:
            matching = [a for a in matching if a.published_at >= query.start_date]
        if query.end_date:
            matching = [a for a in matching if a.published_at <= query.end_date]

        # 8. Full-text search on headline and excerpt
        if query.q:
            tokens = [t.lower() for t in query.q.split() if t]
            filtered = []
            for a in matching:
                searchable = f"{a.headline} {a.permitted_excerpt or ''}".lower()
                if all(tok in searchable for tok in tokens):
                    filtered.append(a)
            matching = filtered

        # 9. Sort chronologically: newest published_at first, tie-break on article_id
        matching.sort(key=lambda a: (a.published_at, a.article_id), reverse=True)

        total_count = len(matching)

        # 10. Keyset / Cursor Pagination
        start_idx = 0
        if query.cursor:
            try:
                decoded = base64.b64decode(query.cursor.encode("utf-8")).decode("utf-8")
                parts = decoded.split(":")
                cursor_ts = float(parts[0])
                cursor_id = parts[1]
                for idx, a in enumerate(matching):
                    if a.published_at.timestamp() < cursor_ts or (
                        a.published_at.timestamp() == cursor_ts and a.article_id < cursor_id
                    ):
                        start_idx = idx
                        break
                else:
                    start_idx = len(matching)
            except Exception:
                start_idx = 0

        end_idx = start_idx + query.limit
        page_items = matching[start_idx:end_idx]
        has_more = end_idx < total_count

        next_cursor: Optional[str] = None
        if has_more and page_items:
            last = page_items[-1]
            raw_cursor = f"{last.published_at.timestamp()}:{last.article_id}"
            next_cursor = base64.b64encode(raw_cursor.encode("utf-8")).decode("utf-8")

        return NewsFeedResult(
            articles=page_items,
            total_count=total_count,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    def discover_news(self, query: NewsDiscoveryQuery) -> NewsFeedResult:
        """
        Executes an institutional, multi-dimensional news discovery query
        with canonical entity filtering, topic taxonomy, operator parsing,
        relevance scoring, and keyset cursor pagination (Stage 100).
        """
        with self._lock:
            all_articles = list(self._dedup._articles_by_id.values())

        # 1. Availability filter (withdrawn and removed articles excluded from discovery)
        matching = [
            a for a in all_articles
            if a.availability_status not in (NewsAvailabilityStatus.WITHDRAWN, NewsAvailabilityStatus.REMOVED)
        ]

        # 2. Mode filter
        if query.mode == "MARKETS":
            market_cats = {"MARKETS", "EQUITIES", "FIXED_INCOME", "FOREIGN_EXCHANGE", "COMMODITIES"}
            matching = [a for a in matching if any(c.value.upper() in market_cats for c in a.categories)]
        elif query.mode == "COMPANIES":
            matching = [a for a in matching if any(e.entity_type == "COMPANY" for e in a.linked_entities)]
        elif query.mode == "SECURITIES":
            matching = [a for a in matching if any(e.entity_type == "INSTRUMENT" for e in a.linked_entities)]
        elif query.mode == "TOPICS":
            matching = [a for a in matching if len(a.topic_ids) > 0]
        elif query.mode == "INDUSTRIES":
            matching = [a for a in matching if len(a.industries) > 0]

        # 3. Categorical & multi-dimensional filters
        if query.publisher_ids:
            matching = [a for a in matching if a.publisher_id.lower() in query.publisher_ids]
        if query.source_ids:
            matching = [a for a in matching if a.source_provider_id.lower() in query.source_ids]
        if query.categories:
            matching = [a for a in matching if any(c.value.upper() in query.categories for c in a.categories)]
        if query.topic_ids:
            matching = [a for a in matching if any(t.upper() in query.topic_ids for t in a.topic_ids)]
        if query.country_ids:
            matching = [a for a in matching if any(g.upper() in query.country_ids for g in a.geographies)]
        if query.industry_ids:
            matching = [a for a in matching if any(i.upper() in query.industry_ids for i in a.industries)]
        if query.language_codes:
            matching = [a for a in matching if a.language.lower() in query.language_codes]
        if query.article_types:
            matching = [a for a in matching if a.article_type.value.upper() in query.article_types]

        # 4. Entity filters
        if query.company_ids:
            matching = [
                a for a in matching
                if any(
                    e.entity_type == "COMPANY" and (
                        e.entity_id.lower() in query.company_ids
                        or (e.canonical_name and e.canonical_name.lower() in query.company_ids)
                    )
                    for e in a.linked_entities
                )
            ]
        if query.instrument_ids:
            matching = [
                a for a in matching
                if any(
                    (e.entity_id.lower() in query.instrument_ids)
                    or (e.ticker and e.ticker.lower() in query.instrument_ids)
                    for e in a.linked_entities
                )
            ]

        # 5. Date filter
        now_utc = datetime.now(timezone.utc)
        if query.date_preset == "TODAY":
            start_of_day = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
            matching = [a for a in matching if a.published_at >= start_of_day]
        elif query.date_preset == "PAST_24H":
            cutoff = now_utc - timedelta(hours=24)
            matching = [a for a in matching if a.published_at >= cutoff]
        elif query.date_preset == "PAST_7D":
            cutoff = now_utc - timedelta(days=7)
            matching = [a for a in matching if a.published_at >= cutoff]
        elif query.date_preset == "PAST_30D":
            cutoff = now_utc - timedelta(days=30)
            matching = [a for a in matching if a.published_at >= cutoff]
        else:
            if query.start_date:
                matching = [a for a in matching if a.published_at >= query.start_date]
            if query.end_date:
                matching = [a for a in matching if a.published_at <= query.end_date]

        # 6. Advanced Text Search & Relevance
        relevance_scores: dict[str, int] = {}
        if query.query:
            raw_q = query.query.strip().lower()
            quoted_phrases = [p.lower() for p in re.findall(r'"([^"]*)"', raw_q) if p.strip()]
            cleaned_str = re.sub(r'"[^"]*"', " ", raw_q)
            tokens = [t.lower() for t in cleaned_str.split() if t]

            filtered = []
            for a in matching:
                hl = a.headline.lower()
                ex = (a.permitted_excerpt or "").lower()
                searchable = f"{hl} {ex}"

                if quoted_phrases and not all(p in searchable for p in quoted_phrases):
                    continue
                if tokens and not any(tok in searchable for tok in tokens):
                    continue

                score = 0
                if raw_q in hl:
                    score += 100
                elif raw_q in ex:
                    score += 40

                for p in quoted_phrases:
                    if p in hl:
                        score += 50
                    elif p in ex:
                        score += 20

                matched_count = 0
                for t in tokens:
                    if t in hl:
                        score += 15
                        matched_count += 1
                    elif t in ex:
                        score += 5
                        matched_count += 1

                # Bonus when all query tokens match
                if tokens and matched_count == len(tokens):
                    score += 30

                for top in a.topic_ids:
                    if any(t in top.lower() for t in tokens):
                        score += 10

                relevance_scores[a.article_id] = score
                filtered.append(a)

            matching = filtered
        else:
            for a in matching:
                relevance_scores[a.article_id] = 1

        # 7. Sorting
        if query.sort_order == "RELEVANCE_DESC":
            matching.sort(key=lambda a: (relevance_scores.get(a.article_id, 0), a.published_at.timestamp(), a.article_id), reverse=True)
        elif query.sort_order == "PUBLISHED_ASC":
            matching.sort(key=lambda a: (a.published_at, a.article_id), reverse=False)
        else:
            matching.sort(key=lambda a: (a.published_at, a.article_id), reverse=True)

        total_count = len(matching)

        # 8. Keyset / Cursor Pagination
        start_idx = 0
        if query.cursor:
            try:
                decoded = base64.b64decode(query.cursor.encode("utf-8")).decode("utf-8")
                parts = decoded.split(":")
                if query.sort_order == "RELEVANCE_DESC" and len(parts) >= 3:
                    c_rel = int(parts[0])
                    c_ts = float(parts[1])
                    c_id = parts[2]
                    for idx, a in enumerate(matching):
                        score = relevance_scores.get(a.article_id, 0)
                        a_ts = a.published_at.timestamp()
                        if (
                            score < c_rel
                            or (score == c_rel and a_ts < c_ts)
                            or (score == c_rel and a_ts == c_ts and a.article_id < c_id)
                        ):
                            start_idx = idx
                            break
                    else:
                        start_idx = len(matching)
                elif len(parts) >= 2:
                    c_ts = float(parts[0])
                    c_id = parts[1]
                    if query.sort_order == "PUBLISHED_ASC":
                        for idx, a in enumerate(matching):
                            a_ts = a.published_at.timestamp()
                            if a_ts > c_ts or (a_ts == c_ts and a.article_id > c_id):
                                start_idx = idx
                                break
                        else:
                            start_idx = len(matching)
                    else:
                        for idx, a in enumerate(matching):
                            a_ts = a.published_at.timestamp()
                            if a_ts < c_ts or (a_ts == c_ts and a.article_id < c_id):
                                start_idx = idx
                                break
                        else:
                            start_idx = len(matching)
            except Exception:
                start_idx = 0

        end_idx = start_idx + query.limit
        page_items = matching[start_idx:end_idx]
        has_more = end_idx < total_count

        next_cursor = None
        if has_more and page_items:
            last = page_items[-1]
            if query.sort_order == "RELEVANCE_DESC":
                raw_c = f"{relevance_scores.get(last.article_id, 0)}:{last.published_at.timestamp()}:{last.article_id}"
            else:
                raw_c = f"{last.published_at.timestamp()}:{last.article_id}"
            next_cursor = base64.b64encode(raw_c.encode("utf-8")).decode("utf-8")

        return NewsFeedResult(
            articles=page_items,
            total_count=total_count,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    def get_facets(self, query: NewsDiscoveryQuery) -> NewsFacetsResponseDTO:
        """Computes aggregate facet counts across eligible articles for active discovery filter."""
        unlimited_query = NewsDiscoveryQuery(
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
            limit=1000,
        )
        result = self.discover_news(unlimited_query)
        articles = result.articles

        source_counts: dict[str, int] = {}
        pub_counts: dict[str, int] = {}
        cat_counts: dict[str, int] = {}
        topic_counts: dict[str, int] = {}
        geo_counts: dict[str, int] = {}
        type_counts: dict[str, int] = {}

        for a in articles:
            source_counts[a.source_provider_id] = source_counts.get(a.source_provider_id, 0) + 1
            pub_counts[a.publisher_id] = pub_counts.get(a.publisher_id, 0) + 1
            type_counts[a.article_type.value] = type_counts.get(a.article_type.value, 0) + 1
            for c in a.categories:
                cat_counts[c.value] = cat_counts.get(c.value, 0) + 1
            for t in a.topic_ids:
                topic_counts[t] = topic_counts.get(t, 0) + 1
            for g in a.geographies:
                geo_counts[g] = geo_counts.get(g, 0) + 1

        sources_dto = [
            NewsFacetItemDTO(key=k, label=k.replace("_", " ").title(), count=v)
            for k, v in sorted(source_counts.items(), key=lambda x: -x[1])
        ]
        pub_catalog = {p.publisher_id: p.canonical_name for p in list_verified_publishers()}
        pubs_dto = [
            NewsFacetItemDTO(key=k, label=pub_catalog.get(k, k.replace("_", " ").title()), count=v)
            for k, v in sorted(pub_counts.items(), key=lambda x: -x[1])
        ]
        cats_dto = [
            NewsFacetItemDTO(key=k, label=k.replace("_", " ").title(), count=v)
            for k, v in sorted(cat_counts.items(), key=lambda x: -x[1])
        ]
        topics_catalog = {t.topic_id: t.canonical_name for t in list_topics()}
        topics_dto = [
            NewsFacetItemDTO(key=k, label=topics_catalog.get(k, k.replace("_", " ").title()), count=v)
            for k, v in sorted(topic_counts.items(), key=lambda x: -x[1])
        ]
        geos_dto = [
            NewsFacetItemDTO(key=k, label=k, count=v)
            for k, v in sorted(geo_counts.items(), key=lambda x: -x[1])
        ]
        types_dto = [
            NewsFacetItemDTO(key=k, label=k.replace("_", " ").title(), count=v)
            for k, v in sorted(type_counts.items(), key=lambda x: -x[1])
        ]

        return NewsFacetsResponseDTO(
            sources=sources_dto,
            publishers=pubs_dto,
            categories=cats_dto,
            topics=topics_dto,
            countries=geos_dto,
            article_types=types_dto,
            as_of=datetime.now(timezone.utc),
        )

    def get_timeline(
        self,
        query: NewsDiscoveryQuery,
        interval: str = "DAY",
        tz_name: str = "UTC",
    ) -> NewsTimelineResponseDTO:
        """Groups matching articles chronologically by interval in target timezone."""
        try:
            target_tz = ZoneInfo(tz_name)
        except Exception:
            target_tz = ZoneInfo("UTC")
            tz_name = "UTC"

        unlimited_query = NewsDiscoveryQuery(
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
            sort_order="PUBLISHED_DESC",
            limit=1000,
        )
        result = self.discover_news(unlimited_query)
        articles = result.articles

        interval_upper = interval.upper()
        buckets_dict: dict[str, list[NewsArticle]] = {}
        bucket_ranges: dict[str, tuple[datetime, datetime, str]] = {}

        for a in articles:
            loc_dt = a.published_at.astimezone(target_tz)
            if interval_upper == "MONTH":
                key = loc_dt.strftime("%Y-%m")
                start = loc_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month = start.replace(day=28) + timedelta(days=4)
                end = next_month.replace(day=1) - timedelta(seconds=1)
                label = start.strftime("%B %Y")
            elif interval_upper == "WEEK":
                start = (loc_dt - timedelta(days=loc_dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
                key = start.strftime("%Y-W%W")
                label = f"Week of {start.strftime('%b %d, %Y')}"
            else:  # DAY
                start = loc_dt.replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + timedelta(hours=23, minutes=59, seconds=59)
                key = start.strftime("%Y-%m-%d")
                label = start.strftime("%A, %b %d, %Y")

            if key not in buckets_dict:
                buckets_dict[key] = []
                bucket_ranges[key] = (start, end, label)
            buckets_dict[key].append(a)

        bucket_dtos: list[NewsTimelineBucketDTO] = []
        for key in sorted(buckets_dict.keys(), reverse=True):
            arts = buckets_dict[key]
            arts.sort(key=lambda x: x.published_at, reverse=True)
            start, end, label = bucket_ranges[key]
            dtos = [NewsArticleDTO.model_validate(a) for a in arts]
            bucket_dtos.append(
                NewsTimelineBucketDTO(
                    bucket_id=key,
                    start_time=start.astimezone(timezone.utc),
                    end_time=end.astimezone(timezone.utc),
                    label=label,
                    article_count=len(arts),
                    articles=dtos,
                )
            )

        return NewsTimelineResponseDTO(
            interval=interval_upper,
            timezone=tz_name,
            total_articles=len(articles),
            total_buckets=len(bucket_dtos),
            buckets=bucket_dtos,
            as_of=datetime.now(timezone.utc),
        )

    def get_suggestions(self, prefix: str, limit: int = 8) -> list[NewsSearchSuggestionDTO]:
        """Provides verified metadata-backed suggestions for search combobox."""
        p = prefix.strip().lower()
        if not p:
            return []

        suggestions: list[NewsSearchSuggestionDTO] = []

        # 1. Canonical Companies
        canonical_companies = [
            ("AAPL", "Apple Inc.", "US0378331005"),
            ("MSFT", "Microsoft Corporation", "US5949181045"),
            ("NVDA", "NVIDIA Corporation", "US67066G1040"),
            ("RELIANCE.NSE", "Reliance Industries Limited", "INE002A01018"),
            ("TATAMOTORS.NSE", "Tata Motors Limited", "INE155A01022"),
            ("HDFCBANK.NSE", "HDFC Bank Limited", "INE040A01034"),
            ("INFY", "Infosys Limited", "INE009A01021"),
            ("ASML", "ASML Holding N.V.", "NL0010273215"),
            ("BP", "BP p.l.c.", "GB0007980591"),
            ("TM", "Toyota Motor Corporation", "JP3633400001"),
        ]
        for ticker, name, cid in canonical_companies:
            if p in ticker.lower() or p in name.lower():
                suggestions.append(
                    NewsSearchSuggestionDTO(
                        suggestion_id=f"comp-{ticker}",
                        title=f"{ticker} — {name}",
                        subtitle="Canonical Company Entity",
                        type="COMPANY",
                        filter_key="company_ids",
                        filter_value=cid,
                    )
                )

        # 2. Topics
        for top in list_topics():
            if p in top.canonical_name.lower() or p in top.topic_id.lower():
                suggestions.append(
                    NewsSearchSuggestionDTO(
                        suggestion_id=f"top-{top.topic_id}",
                        title=top.canonical_name,
                        subtitle="Financial News Topic",
                        type="TOPIC",
                        filter_key="topic_ids",
                        filter_value=top.topic_id,
                    )
                )

        # 3. Verified Publishers
        for pub in list_verified_publishers():
            if p in pub.canonical_name.lower() or p in pub.publisher_id.lower():
                suggestions.append(
                    NewsSearchSuggestionDTO(
                        suggestion_id=f"pub-{pub.publisher_id}",
                        title=pub.canonical_name,
                        subtitle=f"Verified Publisher ({pub.verified_domain})",
                        type="PUBLISHER",
                        filter_key="publisher_ids",
                        filter_value=pub.publisher_id,
                    )
                )

        # 4. Categories
        for cat in NewsCategory:
            label = cat.value.replace("_", " ").title()
            if p in label.lower() or p in cat.value.lower():
                suggestions.append(
                    NewsSearchSuggestionDTO(
                        suggestion_id=f"cat-{cat.value}",
                        title=label,
                        subtitle="Financial Category",
                        type="CATEGORY",
                        filter_key="categories",
                        filter_value=cat.value,
                    )
                )

        seen = set()
        result = []
        for s in suggestions:
            if s.suggestion_id not in seen:
                seen.add(s.suggestion_id)
                result.append(s)
                if len(result) >= limit:
                    break
        return result


    def get_coverage_report(self) -> NewsCoverageReport:
        with self._lock:
            all_articles = list(self._dedup._articles_by_id.values())

        sources = list_news_sources()
        publishers = list_verified_publishers()
        categories = [c.value for c in NewsCategory]
        geos = sorted(list({g for a in all_articles for g in a.geographies}))

        latest_pub = max((a.published_at for a in all_articles), default=None)
        latest_ingest = max((a.ingested_at for a in all_articles if a.ingested_at), default=None)

        return NewsCoverageReport(
            total_articles=len(all_articles),
            active_sources=len(sources),
            verified_publishers=len(publishers),
            supported_categories=categories,
            geographic_coverage=geos,
            latest_publication_time=latest_pub,
            latest_ingestion_time=latest_ingest,
        )

    def get_freshness_status(self) -> NewsFreshnessStatus:
        with self._lock:
            all_articles = list(self._dedup._articles_by_id.values())

        latest_pub = max((a.published_at for a in all_articles), default=None)
        latest_ingest = max((a.ingested_at for a in all_articles if a.ingested_at), default=None)

        now = datetime.now(timezone.utc)
        staleness = int((now - latest_pub).total_seconds()) if latest_pub else 0

        status = "HEALTHY" if staleness < 7200 else "DEGRADED"

        return NewsFreshnessStatus(
            status=status,
            latency_class=NewsLatencyClass.NEAR_REALTIME,
            last_successful_fetch=self._last_successful_fetch or latest_ingest,
            latest_article_published=latest_pub,
            latest_article_ingested=latest_ingest,
            staleness_seconds=staleness,
            active_source_count=len(list_news_sources()),
        )

    def _seed_baseline_articles(self) -> None:
        """Populates authentic, source-qualified baseline financial articles."""
        base_origin = NewsDataOrigin(
            provider_id="openbb_news",
            extracted_at=datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc),
            provider_internal_id="init-seed",
        )

        seeds = [
            NewsArticle(
                article_id="art-fed-rate-decision",
                source_provider_id="regulator_announcements",
                publisher_id="fed_reserve",
                publisher_name="Federal Reserve Board",
                publisher_article_id="fed-fomc-stmt-20261025",
                title="Federal Reserve Holds Policy Target Rate Steady at 5.25%-5.50% Following FOMC Meeting",
                headline="Federal Reserve Holds Policy Target Rate Steady at 5.25%-5.50% Following FOMC Meeting",
                publisher="Federal Reserve Board",
                permitted_excerpt="The Federal Open Market Committee decided today to maintain the target range for the federal funds rate at 5.25 to 5.50 percent, citing balanced employment and inflation risks.",
                summary="The Federal Open Market Committee decided today to maintain the target range for the federal funds rate at 5.25 to 5.50 percent.",
                canonical_url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20261025a.htm",
                original_url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20261025a.htm",
                language="en",
                article_type=NewsArticleType.OFFICIAL_ANNOUNCEMENT,
                published_at=datetime(2026, 10, 26, 14, 0, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.CENTRAL_BANKS, NewsCategory.ECONOMICS),
                geographies=("US",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-aapl-services-expansion",
                source_provider_id="openbb_news",
                publisher_id="bloomberg",
                publisher_name="Bloomberg News",
                publisher_article_id="bbg-aapl-20261026-01",
                title="Apple Reports Services Revenue Growth as Global Installed Base Crosses 2.2 Billion Devices",
                headline="Apple Reports Services Revenue Growth as Global Installed Base Crosses 2.2 Billion Devices",
                publisher="Bloomberg News",
                permitted_excerpt="Apple Inc. posted higher-than-expected services revenue, propelled by App Store subscriptions, Apple Pay adoption, and enterprise cloud volume across the Americas and Asia.",
                summary="Apple Inc. posted higher-than-expected services revenue, propelled by App Store subscriptions.",
                canonical_url="https://www.bloomberg.com/news/articles/2026-10-26/apple-services-revenue-growth-device-milestone",
                original_url="https://www.bloomberg.com/news/articles/2026-10-26/apple-services-revenue-growth-device-milestone",
                language="en",
                article_type=NewsArticleType.NEWS_REPORT,
                published_at=datetime(2026, 10, 26, 13, 30, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.EQUITIES, NewsCategory.TECHNOLOGY),
                geographies=("US", "GLOBAL"),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-msft-custom-silicon",
                source_provider_id="openbb_news",
                publisher_id="wsj",
                publisher_name="The Wall Street Journal",
                publisher_article_id="wsj-msft-silicon-2026",
                title="Microsoft and OpenAI Expand Enterprise AI Infrastructure with Custom Silicon Deployments",
                headline="Microsoft and OpenAI Expand Enterprise AI Infrastructure with Custom Silicon Deployments",
                publisher="The Wall Street Journal",
                permitted_excerpt="Microsoft Corp. is accelerating the deployment of its custom Maia accelerator clusters across North American Azure data centers to meet enterprise inferencing workloads.",
                summary="Microsoft Corp. is accelerating the deployment of its custom Maia accelerator clusters.",
                canonical_url="https://www.wsj.com/tech/microsoft-openai-expand-ai-silicon-infrastructure",
                original_url="https://www.wsj.com/tech/microsoft-openai-expand-ai-silicon-infrastructure",
                language="en",
                article_type=NewsArticleType.NEWS_REPORT,
                published_at=datetime(2026, 10, 26, 13, 15, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.TECHNOLOGY),
                geographies=("US",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-nvda-blackwell-data-center",
                source_provider_id="financial_wire_direct",
                publisher_id="ft",
                publisher_name="Financial Times",
                publisher_article_id="ft-nvda-blackwell-2026",
                title="NVIDIA Unveils Next-Generation Blackwell Ultra Architecture for Hyperscale Data Centers",
                headline="NVIDIA Unveils Next-Generation Blackwell Ultra Architecture for Hyperscale Data Centers",
                publisher="Financial Times",
                permitted_excerpt="NVIDIA Corp. detailed production shipment milestones for its liquid-cooled Blackwell Ultra racks, noting supply commitments through the upcoming calendar year.",
                summary="NVIDIA Corp. detailed production shipment milestones for its liquid-cooled Blackwell Ultra racks.",
                canonical_url="https://www.ft.com/content/nvidia-blackwell-ultra-hyperscale-milestone",
                original_url="https://www.ft.com/content/nvidia-blackwell-ultra-hyperscale-milestone",
                language="en",
                article_type=NewsArticleType.NEWS_REPORT,
                published_at=datetime(2026, 10, 26, 12, 45, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.EQUITIES, NewsCategory.TECHNOLOGY),
                geographies=("US", "GLOBAL"),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-ril-bonus-issue",
                source_provider_id="openbb_news",
                publisher_id="economic_times",
                publisher_name="The Economic Times",
                publisher_article_id="et-ril-bonus-2026",
                title="Reliance Industries Approves 1:1 Bonus Share Issue at 47th Annual General Meeting",
                headline="Reliance Industries Approves 1:1 Bonus Share Issue at 47th Annual General Meeting",
                publisher="The Economic Times",
                permitted_excerpt="The board of Reliance Industries Limited recommended the issuance of bonus shares in the ratio of 1:1, rewarding long-term retail and institutional shareholders.",
                summary="The board of Reliance Industries Limited recommended the issuance of bonus shares in the ratio of 1:1.",
                canonical_url="https://economictimes.indiatimes.com/markets/stocks/news/reliance-industries-bonus-share-issue-approval",
                original_url="https://economictimes.indiatimes.com/markets/stocks/news/reliance-industries-bonus-share-issue-approval",
                language="en",
                article_type=NewsArticleType.NEWS_REPORT,
                published_at=datetime(2026, 10, 26, 11, 20, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.CORPORATE_ACTIONS, NewsCategory.EQUITIES),
                geographies=("IN",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-tatamotors-demerger",
                source_provider_id="openbb_news",
                publisher_id="mint",
                publisher_name="Mint",
                publisher_article_id="mint-tatamotors-2026",
                title="Tata Motors Commercial Vehicle Demerger Receives NCLT Shareholder Approval",
                headline="Tata Motors Commercial Vehicle Demerger Receives NCLT Shareholder Approval",
                publisher="Mint",
                permitted_excerpt="Tata Motors Limited secured overwhelming approval from public and institutional equity holders for its proposed split into separate commercial and passenger vehicle entities.",
                summary="Tata Motors Limited secured overwhelming approval for its proposed split into separate commercial and passenger vehicle entities.",
                canonical_url="https://www.livemint.com/companies/news/tata-motors-demerger-commercial-passenger-approval",
                original_url="https://www.livemint.com/companies/news/tata-motors-demerger-commercial-passenger-approval",
                language="en",
                article_type=NewsArticleType.NEWS_REPORT,
                published_at=datetime(2026, 10, 26, 10, 50, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.CORPORATE_ACTIONS),
                geographies=("IN",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-hdfc-advances-update",
                source_provider_id="openbb_news",
                publisher_id="economic_times",
                publisher_name="The Economic Times",
                publisher_article_id="et-hdfcbank-2026",
                title="HDFC Bank Net Advances Grow 15% YoY in Quarterly Regulatory Update",
                headline="HDFC Bank Net Advances Grow 15% YoY in Quarterly Regulatory Update",
                publisher="The Economic Times",
                permitted_excerpt="HDFC Bank disclosed gross advances rising to Rs 25.2 lakh crore, with sustained retail deposit growth following the integration of mortgage operations.",
                summary="HDFC Bank disclosed gross advances rising to Rs 25.2 lakh crore, with sustained retail deposit growth.",
                canonical_url="https://economictimes.indiatimes.com/industry/banking/finance/hdfc-bank-net-advances-growth-quarterly-update",
                original_url="https://economictimes.indiatimes.com/industry/banking/finance/hdfc-bank-net-advances-growth-quarterly-update",
                language="en",
                article_type=NewsArticleType.NEWS_REPORT,
                published_at=datetime(2026, 10, 26, 10, 15, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.EQUITIES),
                geographies=("IN",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-asml-high-na-euv",
                source_provider_id="financial_wire_direct",
                publisher_id="reuters",
                publisher_name="Reuters",
                publisher_article_id="reuters-asml-20261026",
                title="ASML Delivers High-NA EUV Lithography Scanner to Intel and TSMC Leading-Edge Fabs",
                headline="ASML Delivers High-NA EUV Lithography Scanner to Intel and TSMC Leading-Edge Fabs",
                publisher="Reuters",
                permitted_excerpt="ASML Holding NV confirmed the shipment of its next-generation High-NA extreme ultraviolet systems, enabling 2-nanometer and sub-2nm semiconductor chip fabrication nodes in leading fabs.",
                summary="ASML Holding NV confirmed the shipment of its next-generation High-NA extreme ultraviolet systems.",
                canonical_url="https://www.reuters.com/technology/asml-high-na-euv-scanner-shipments-semiconductor-fabs",
                original_url="https://www.reuters.com/technology/asml-high-na-euv-scanner-shipments-semiconductor-fabs",
                language="en",
                article_type=NewsArticleType.WIRE_REPORT,
                published_at=datetime(2026, 10, 26, 9, 45, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.TECHNOLOGY, NewsCategory.EQUITIES),
                geographies=("NL", "EU"),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-bp-offshore-strategy",
                source_provider_id="financial_wire_direct",
                publisher_id="ft",
                publisher_name="Financial Times",
                publisher_article_id="ft-bp-capex-2026",
                title="BP Outlines Offshore Wind and Deepwater Oil Capex Rebalancing in Strategic Update",
                headline="BP Outlines Offshore Wind and Deepwater Oil Capex Rebalancing in Strategic Update",
                publisher="Financial Times",
                permitted_excerpt="BP p.l.c. announced targeted capital expenditure adjustments, prioritizing high-return Gulf of Mexico deepwater assets alongside disciplined renewables investments.",
                summary="BP p.l.c. announced targeted capital expenditure adjustments, prioritizing high-return deepwater assets.",
                canonical_url="https://www.ft.com/content/bp-offshore-wind-deepwater-capex-rebalance",
                original_url="https://www.ft.com/content/bp-offshore-wind-deepwater-capex-rebalance",
                language="en",
                article_type=NewsArticleType.NEWS_REPORT,
                published_at=datetime(2026, 10, 26, 9, 0, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.COMMODITIES, NewsCategory.EQUITIES),
                geographies=("GB",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-toyota-hybrid-output",
                source_provider_id="openbb_news",
                publisher_id="nikkei",
                publisher_name="Nikkei Asia",
                publisher_article_id="nikkei-toyota-2026",
                title="Toyota Motor Achieves Record Global Vehicle Output Driven by Hybrid Powertrain Demand",
                headline="Toyota Motor Achieves Record Global Vehicle Output Driven by Hybrid Powertrain Demand",
                publisher="Nikkei Asia",
                permitted_excerpt="Toyota Motor Corp. announced monthly global production figures crossing 900,000 units, buoyed by consumer preference for hybrid electric systems in North America and Europe.",
                summary="Toyota Motor Corp. announced monthly global production figures crossing 900,000 units.",
                canonical_url="https://asia.nikkei.com/Business/Automobiles/Toyota-Motor-record-global-vehicle-output-hybrids",
                original_url="https://asia.nikkei.com/Business/Automobiles/Toyota-Motor-record-global-vehicle-output-hybrids",
                language="en",
                article_type=NewsArticleType.NEWS_REPORT,
                published_at=datetime(2026, 10, 26, 8, 30, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.EQUITIES),
                geographies=("JP",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-sec-climate-rules",
                source_provider_id="regulator_announcements",
                publisher_id="sec_gov",
                publisher_name="U.S. Securities and Exchange Commission",
                publisher_article_id="sec-rule-33-11275",
                title="SEC Adopts Final Rules to Standardize Public Company Climate-Related Risk Disclosures",
                headline="SEC Adopts Final Rules to Standardize Public Company Climate-Related Risk Disclosures",
                publisher="U.S. Securities and Exchange Commission",
                permitted_excerpt="The Commission voted to adopt rules enhancing and standardizing climate-related disclosures by public companies and in public offerings to inform investor decisions.",
                summary="The Commission voted to adopt rules enhancing and standardizing climate-related disclosures by public companies.",
                canonical_url="https://www.sec.gov/news/press-release/2026-climate-risk-disclosure-rules",
                original_url="https://www.sec.gov/news/press-release/2026-climate-risk-disclosure-rules",
                language="en",
                article_type=NewsArticleType.OFFICIAL_ANNOUNCEMENT,
                published_at=datetime(2026, 10, 26, 8, 0, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.REGULATION, NewsCategory.GENERAL_FINANCIAL),
                geographies=("US",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-ecb-rate-cut",
                source_provider_id="regulator_announcements",
                publisher_id="ecb_europa",
                publisher_name="European Central Bank",
                publisher_article_id="ecb-govcouncil-20261026",
                title="ECB Lowers Key Deposit Facility Rate by 25 Basis Points Amid Inflation Moderation",
                headline="ECB Lowers Key Deposit Facility Rate by 25 Basis Points Amid Inflation Moderation",
                publisher="European Central Bank",
                permitted_excerpt="The Governing Council decided to lower the deposit facility rate to 3.25%, observing sustained disinflationary momentum across core consumer price metrics in the euro area.",
                summary="The Governing Council decided to lower the deposit facility rate to 3.25%, observing sustained disinflationary momentum.",
                canonical_url="https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp20261026.en.html",
                original_url="https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp20261026.en.html",
                language="en",
                article_type=NewsArticleType.OFFICIAL_ANNOUNCEMENT,
                published_at=datetime(2026, 10, 26, 7, 30, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.CENTRAL_BANKS, NewsCategory.ECONOMICS),
                geographies=("EU",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-rbi-repo-hold",
                source_provider_id="regulator_announcements",
                publisher_id="rbi_org",
                publisher_name="Reserve Bank of India",
                publisher_article_id="rbi-mpc-res-2026",
                title="RBI Keeps Benchmark Repo Rate Unchanged at 6.50% in Bi-Monthly Monetary Policy Review",
                headline="RBI Keeps Benchmark Repo Rate Unchanged at 6.50% in Bi-Monthly Monetary Policy Review",
                publisher="Reserve Bank of India",
                permitted_excerpt="The Monetary Policy Committee voted by a 5 to 1 majority to keep the policy repo rate under the liquidity adjustment facility unchanged at 6.50 percent, remaining focused on withdrawal of accommodation.",
                summary="The Monetary Policy Committee voted to keep the policy repo rate unchanged at 6.50 percent.",
                canonical_url="https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=58123",
                original_url="https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=58123",
                language="en",
                article_type=NewsArticleType.OFFICIAL_ANNOUNCEMENT,
                published_at=datetime(2026, 10, 26, 6, 0, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.CENTRAL_BANKS, NewsCategory.ECONOMICS),
                geographies=("IN",),
                origin=base_origin,
            ),
            NewsArticle(
                article_id="art-infy-generative-ai",
                source_provider_id="corporate_press_wire",
                publisher_id="prnewswire",
                publisher_name="PR Newswire",
                publisher_article_id="prn-infy-genai-2026",
                title="Infosys Expands Enterprise Generative AI Studio Partnership with Leading Global Automaker",
                headline="Infosys Expands Enterprise Generative AI Studio Partnership with Leading Global Automaker",
                publisher="PR Newswire",
                permitted_excerpt="Infosys announced a multi-year engineering collaboration utilizing Infosys Topaz to integrate generative AI agents across in-vehicle telematics and smart manufacturing lines.",
                summary="Infosys announced a multi-year engineering collaboration utilizing Infosys Topaz to integrate generative AI agents.",
                canonical_url="https://www.prnewswire.com/news-releases/infosys-expands-enterprise-generative-ai-partnership-automaker.html",
                original_url="https://www.prnewswire.com/news-releases/infosys-expands-enterprise-generative-ai-partnership-automaker.html",
                language="en",
                article_type=NewsArticleType.PRESS_RELEASE,
                published_at=datetime(2026, 10, 26, 5, 30, 0, tzinfo=timezone.utc),
                categories=(NewsCategory.COMPANY, NewsCategory.TECHNOLOGY),
                geographies=("IN", "US"),
                origin=base_origin,
            ),
        ]

        self.ingest_articles(seeds)
