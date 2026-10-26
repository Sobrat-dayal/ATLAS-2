"""Institutional News Monitoring, Rule-Based Alerts, Custom Feeds & Digests (Stage 103)."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

from atlas.news.articles import NewsArticle
from atlas.news.enums import (
    NewsAlertMatchStatus,
    NewsAlertPriority,
    NewsDeliveryChannel,
    NewsDigestCadence,
    NewsFinancialAspect,
    NewsMonitoringRuleType,
    NewsSentimentLabel,
    NewsTriggerPolicy,
)
from atlas.news.events import NewsFinancialEvent
from atlas.news.sentiment import NewsSentimentAnnotation
from atlas.news.stories import NewsStoryThread


@dataclass
class NewsSentimentCondition:
    """Optional sentiment criteria required for a monitoring rule to trigger."""

    sentiment_label: Optional[NewsSentimentLabel] = None
    min_score: Optional[float] = None
    aspect: Optional[NewsFinancialAspect] = None

    @property
    def min_sentiment_score(self) -> Optional[float]:
        return self.min_score


@dataclass
class NewsMonitoringRule:
    """Canonical user-owned monitoring subscription configuration."""

    rule_id: str
    owner_user_id: str
    name: str
    description: Optional[str] = None
    rule_type: NewsMonitoringRuleType = NewsMonitoringRuleType.COMPANY
    target_entity_ids: List[str] = field(default_factory=list)
    target_tickers: List[str] = field(default_factory=list)
    target_watchlist_ids: List[str] = field(default_factory=list)
    target_topics: List[str] = field(default_factory=list)
    target_event_types: List[str] = field(default_factory=list)
    target_publisher_ids: List[str] = field(default_factory=list)
    target_story_id: Optional[str] = None
    target_custom_feed_id: Optional[str] = None
    sentiment_condition: Optional[NewsSentimentCondition] = None
    priority: NewsAlertPriority = NewsAlertPriority.NORMAL
    trigger_policy: NewsTriggerPolicy = NewsTriggerPolicy.ON_NEW_ARTICLE
    cooldown_minutes: int = 0
    delivery_channels: List[NewsDeliveryChannel] = field(
        default_factory=lambda: [NewsDeliveryChannel.IN_APP]
    )
    quiet_hours_enabled: bool = False
    quiet_hours_start_utc: Optional[str] = None
    quiet_hours_end_utc: Optional[str] = None
    user_timezone: str = "UTC"
    is_active: bool = True
    rule_revision: int = 1
    last_matched_at: Optional[datetime] = None
    match_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Compatibility aliases
    @property
    def topic_ids(self) -> List[str]:
        return self.target_topics

    @property
    def watchlist_id(self) -> Optional[str]:
        return self.target_watchlist_ids[0] if self.target_watchlist_ids else None

    @property
    def publisher_ids(self) -> List[str]:
        return self.target_publisher_ids

    @property
    def event_types(self) -> List[str]:
        return self.target_event_types


@dataclass
class NewsAlertMatch:
    """Source-grounded record of an evaluated and matched monitoring event."""

    match_id: str
    rule_id: str
    rule_name: str
    rule_revision: int
    owner_user_id: str
    trigger_type: NewsTriggerPolicy
    source_object_type: str  # "ARTICLE", "EVENT", "STORY"
    source_object_id: str
    headline_or_title: str
    publisher_name: str
    target_entity_id: Optional[str] = None
    target_ticker: Optional[str] = None
    matched_conditions: List[str] = field(default_factory=list)
    evidence_snippet: Optional[str] = None
    source_published_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: NewsAlertPriority = NewsAlertPriority.NORMAL
    delivery_channel: NewsDeliveryChannel = NewsDeliveryChannel.IN_APP
    status: NewsAlertMatchStatus = NewsAlertMatchStatus.DELIVERED
    suppression_reason: Optional[str] = None
    deduplication_key: str = ""
    notification_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def source_title(self) -> str:
        return self.headline_or_title


@dataclass
class CustomNewsFeed:
    """User-saved discovery query configuration compiled to canonical NewsDiscoveryQuery."""

    feed_id: str
    owner_user_id: str
    title: str
    description: Optional[str] = None
    query_config: Dict[str, Any] = field(default_factory=dict)
    is_alert_enabled: bool = False
    linked_rule_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def name(self) -> str:
        return self.title


@dataclass
class NewsDigestSubscription:
    """Scheduled periodic news digest configuration."""

    digest_id: str
    owner_user_id: str
    title: str
    cadence: NewsDigestCadence = NewsDigestCadence.DAILY
    preferred_time_local: str = "08:00"
    timezone: str = "UTC"
    delivery_channel: NewsDeliveryChannel = NewsDeliveryChannel.IN_APP
    include_empty: bool = False
    max_items: int = 15
    target_entity_ids: List[str] = field(default_factory=list)
    target_watchlist_ids: List[str] = field(default_factory=list)
    target_topics: List[str] = field(default_factory=list)
    is_active: bool = True
    last_run_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def delivery_time_utc(self) -> str:
        return self.preferred_time_local

    @property
    def user_timezone(self) -> str:
        return self.timezone


@dataclass
class NewsDigestRun:
    """Execution record and generated summary content of a scheduled news digest."""

    run_id: str
    digest_id: str
    owner_user_id: str
    title: str
    interval_start: datetime
    interval_end: datetime
    executed_at: datetime
    eligible_article_count: int
    unique_story_count: int
    verified_event_count: int
    status: str
    summary_sections: List[Dict[str, Any]] = field(default_factory=list)
    attribution_disclaimer: str = (
        "Compiled from authorized institutional news feeds and verified company disclosures."
    )

    @property
    def period_start(self) -> datetime:
        return self.interval_start

    @property
    def period_end(self) -> datetime:
        return self.interval_end

    @property
    def articles_included(self) -> int:
        return self.eligible_article_count

    @property
    def stories_grouped(self) -> int:
        return self.unique_story_count

    @property
    def delivery_status(self) -> str:
        return self.status


@dataclass
class MonitoringHealthStatus:
    """System-level observability into news monitoring pipelines and evaluation lag."""

    is_healthy: bool = True
    active_rules_count: int = 0
    evaluated_matches_24h: int = 0
    delivered_alerts_24h: int = 0
    delivery_success_rate: float = 1.0
    last_processed_ingestion_watermark: Optional[datetime] = None
    queue_lag_seconds: float = 0.0
    p95_evaluation_latency_ms: float = 1.2
    as_of: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def status(self) -> str:
        return "HEALTHY" if self.is_healthy else "DEGRADED"

    @property
    def matches_24h_count(self) -> int:
        return self.evaluated_matches_24h

    @property
    def latest_ingestion_watermark(self) -> Optional[datetime]:
        return self.last_processed_ingestion_watermark

    @property
    def evaluation_latency_ms(self) -> float:
        return self.p95_evaluation_latency_ms


class NewsRuleMatcher:
    """
    Deterministic rule evaluation engine validating incoming financial news,
    story thread progressions, and financial event updates against active user rules.
    """

    @staticmethod
    def compute_dedupe_key(
        user_id: str,
        rule_id: str,
        source_object_id: str,
        trigger_type: str,
    ) -> str:
        """Derives a deterministic deduplication hash for idempotency checking."""
        content = f"{user_id}:{rule_id}:{source_object_id}:{trigger_type}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def match_article(
        cls,
        rule: NewsMonitoringRule,
        article: NewsArticle,
        sentiment_annotations: Optional[List[NewsSentimentAnnotation]] = None,
        current_time_utc: Optional[datetime] = None,
        watched_symbols: Optional[List[str]] = None,
    ) -> Optional[NewsAlertMatch]:
        """Evaluates a single article against a single rule."""
        matches = cls.evaluate_article(
            article=article,
            rules=[rule],
            sentiments=sentiment_annotations,
            watched_symbols=watched_symbols,
            now=current_time_utc,
        )
        return matches[0] if matches else None

    @classmethod
    def evaluate_article(
        cls,
        article: NewsArticle,
        rules: List[NewsMonitoringRule],
        sentiments: Optional[List[NewsSentimentAnnotation]] = None,
        watched_symbols: Optional[List[str]] = None,
        now: Optional[datetime] = None,
    ) -> List[NewsAlertMatch]:
        """
        Evaluates a newly ingested or revised article against a cohort of active monitoring rules.
        Enforces cooldown and syndication deduplication.
        """
        now_utc = now or datetime.now(timezone.utc)
        matches: List[NewsAlertMatch] = []
        sentiments = sentiments or []
        watched_symbols_set = {s.upper() for s in (watched_symbols or [])}

        # Index article entity mentions
        entity_ids = {m.entity_id.lower() for m in article.linked_entities}
        tickers = {m.ticker.upper() for m in article.linked_entities if m.ticker}
        article_topics = set(getattr(article, "topic_ids", []) or [])

        for rule in rules:
            if not rule.is_active:
                continue

            # Skip rules configured exclusively for periodic digests
            if rule.trigger_policy == NewsTriggerPolicy.DAILY_DIGEST_ONLY:
                continue

            matched_conditions: List[str] = []
            target_entity_matched: Optional[str] = None
            target_ticker_matched: Optional[str] = None

            # 1. Company / Instrument / Entity Target Matching
            if rule.target_entity_ids:
                matching_entities = [e for e in rule.target_entity_ids if e.lower() in entity_ids]
                if not matching_entities:
                    continue
                target_entity_matched = matching_entities[0]
                matched_conditions.append(f"Entity: {target_entity_matched}")

            if rule.target_tickers:
                matching_tickers = [t for t in rule.target_tickers if t.upper() in tickers]
                if not matching_tickers:
                    continue
                target_ticker_matched = matching_tickers[0]
                matched_conditions.append(f"Ticker: {target_ticker_matched}")

            # 2. Watchlist Matching
            if rule.rule_type == NewsMonitoringRuleType.WATCHLIST or rule.target_watchlist_ids:
                matching_watched = tickers.intersection(watched_symbols_set)
                if watched_symbols_set and not matching_watched:
                    continue
                if matching_watched:
                    matched_watched = list(matching_watched)[0]
                    target_ticker_matched = matched_watched
                    matched_conditions.append(f"Watchlist: {matched_watched}")

            # 3. Topic Matching
            if rule.target_topics:
                matching_topics = [t for t in rule.target_topics if t.upper() in article_topics or t.upper() in [c.value.upper() for c in article.categories if hasattr(c, "value")]]
                if not matching_topics:
                    continue
                matched_conditions.append(f"Topics: {', '.join(matching_topics)}")

            # 4. Publisher Filter
            if rule.target_publisher_ids:
                if article.publisher_id.lower() not in [p.lower() for p in rule.target_publisher_ids]:
                    continue
                matched_conditions.append(f"Publisher: {article.publisher_name}")

            # 5. Sentiment Condition Filtering
            if rule.sentiment_condition:
                cond = rule.sentiment_condition
                matching_ann = False
                for ann in sentiments:
                    # Target entity alignment if entity was matched
                    if target_entity_matched and ann.target_entity_id.lower() != target_entity_matched.lower():
                        continue
                    if cond.sentiment_label and ann.sentiment_label != cond.sentiment_label:
                        continue
                    min_s = cond.min_score if cond.min_score is not None else cond.min_sentiment_score
                    if min_s is not None and abs(ann.sentiment_score) < min_s:
                        continue
                    if cond.aspect and ann.sentiment_aspect != cond.aspect:
                        continue
                    matching_ann = True
                    break

                if not matching_ann:
                    continue
                matched_conditions.append(f"Sentiment: {cond.sentiment_label or 'Qualified'}")

            # 6. Deduplication and Cooldown Evaluation
            dedupe_key = cls.compute_dedupe_key(
                user_id=rule.owner_user_id,
                rule_id=rule.rule_id,
                source_object_id=article.article_id,
                trigger_type=rule.trigger_policy.value,
            )

            status = NewsAlertMatchStatus.DELIVERED
            suppression_reason: Optional[str] = None

            # Cooldown check
            if rule.cooldown_minutes > 0 and rule.last_matched_at:
                cooldown_delta = timedelta(minutes=rule.cooldown_minutes)
                if now_utc - rule.last_matched_at < cooldown_delta:
                    status = NewsAlertMatchStatus.COOLDOWN_ACTIVE
                    suppression_reason = (
                        f"Cooldown active: {rule.cooldown_minutes}m rule interval not yet elapsed."
                    )

            # Syndication duplicate check
            if article.is_duplicate or getattr(article, "syndicated_from_id", None):
                status = NewsAlertMatchStatus.SUPPRESSED_SYNDICATION
                suppression_reason = (
                    "Syndication duplicate suppressed; original story was previously evaluated."
                )

            evidence_snippet = article.permitted_excerpt or article.headline
            if len(evidence_snippet) > 200:
                evidence_snippet = evidence_snippet[:197] + "..."

            match = NewsAlertMatch(
                match_id=f"match-{uuid.uuid4().hex[:12]}",
                rule_id=rule.rule_id,
                rule_name=rule.name,
                rule_revision=rule.rule_revision,
                owner_user_id=rule.owner_user_id,
                trigger_type=rule.trigger_policy,
                source_object_type="ARTICLE",
                source_object_id=article.article_id,
                headline_or_title=article.headline,
                publisher_name=article.publisher_name,
                target_entity_id=target_entity_matched,
                target_ticker=target_ticker_matched,
                matched_conditions=matched_conditions or ["General News Coverage Match"],
                evidence_snippet=evidence_snippet,
                source_published_at=article.published_at,
                evaluated_at=now_utc,
                priority=rule.priority,
                delivery_channel=rule.delivery_channels[0] if rule.delivery_channels else NewsDeliveryChannel.IN_APP,
                status=status,
                suppression_reason=suppression_reason,
                deduplication_key=dedupe_key,
                created_at=now_utc,
            )
            matches.append(match)

        return matches

    @classmethod
    def evaluate_financial_event(
        cls,
        event: NewsFinancialEvent,
        rules: List[NewsMonitoringRule],
        now: Optional[datetime] = None,
    ) -> List[NewsAlertMatch]:
        """Evaluates a newly verified financial event or event status transition."""
        now_utc = now or datetime.now(timezone.utc)
        matches: List[NewsAlertMatch] = []
        event_entity_id = event.primary_entity_id.lower()

        for rule in rules:
            if not rule.is_active:
                continue

            if rule.trigger_policy not in (
                NewsTriggerPolicy.ON_EVENT_VERIFIED,
                NewsTriggerPolicy.ON_STATUS_CHANGE,
                NewsTriggerPolicy.ON_NEW_ARTICLE,
            ):
                continue

            matched_conditions: List[str] = []

            # 1. Event Type Matching
            if rule.target_event_types:
                if event.event_type.value.upper() not in [et.upper() for et in rule.target_event_types]:
                    continue
                matched_conditions.append(f"Event Type: {event.event_type.value}")

            # 2. Entity Matching
            if rule.target_entity_ids:
                if event_entity_id not in [e.lower() for e in rule.target_entity_ids]:
                    continue
                matched_conditions.append(f"Entity: {event.primary_entity_name}")

            dedupe_key = cls.compute_dedupe_key(
                user_id=rule.owner_user_id,
                rule_id=rule.rule_id,
                source_object_id=event.event_id,
                trigger_type=rule.trigger_policy.value,
            )

            match = NewsAlertMatch(
                match_id=f"match-{uuid.uuid4().hex[:12]}",
                rule_id=rule.rule_id,
                rule_name=rule.name,
                rule_revision=rule.rule_revision,
                owner_user_id=rule.owner_user_id,
                trigger_type=rule.trigger_policy,
                source_object_type="EVENT",
                source_object_id=event.event_id,
                headline_or_title=event.event_title,
                publisher_name="Canonical Verified Event",
                target_entity_id=event.primary_entity_id,
                target_ticker=None,
                matched_conditions=matched_conditions or ["Verified Financial Event"],
                evidence_snippet=f"{event.event_title} ({event.lifecycle_status.value})",
                source_published_at=event.first_seen_at,
                evaluated_at=now_utc,
                priority=rule.priority,
                delivery_channel=rule.delivery_channels[0] if rule.delivery_channels else NewsDeliveryChannel.IN_APP,
                status=NewsAlertMatchStatus.DELIVERED,
                deduplication_key=dedupe_key,
                created_at=now_utc,
            )
            matches.append(match)

        return matches


class NewsDigestEngine:
    """
    Deterministic generation engine for periodic news digests, grouping articles
    into canonical Story Threads and filtering within explicit user-configured time windows.
    """

    @classmethod
    def generate_digest(
        cls,
        subscription: NewsDigestSubscription,
        all_articles: List[NewsArticle],
        all_stories: Optional[Union[List[NewsStoryThread], Dict[str, NewsStoryThread]]] = None,
        all_events: Optional[Union[List[NewsFinancialEvent], Dict[str, NewsFinancialEvent]]] = None,
        now: Optional[datetime] = None,
    ) -> NewsDigestRun:
        """Constructs a structured, source-grounded digest run."""
        now_utc = now or datetime.now(timezone.utc)
        stories_list = list(all_stories.values()) if isinstance(all_stories, dict) else (all_stories or [])
        events_list = list(all_events.values()) if isinstance(all_events, dict) else (all_events or [])

        # Determine interval window (24 hours for daily, 7 days for weekly)
        window_hours = 168 if subscription.cadence == NewsDigestCadence.WEEKLY else 24
        period_start = now_utc - timedelta(hours=window_hours)
        period_end = now_utc

        # Filter articles in interval
        eligible_articles = [
            art
            for art in all_articles
            if period_start <= art.published_at <= period_end and not art.is_duplicate
        ]

        # Entity filtering if configured
        if subscription.target_entity_ids:
            target_ids_lower = {e.lower() for e in subscription.target_entity_ids}
            eligible_articles = [
                art
                for art in eligible_articles
                if any(m.entity_id.lower() in target_ids_lower for m in art.linked_entities)
            ]

        # Topic filtering if configured
        if subscription.target_topics:
            topics_upper = {t.upper() for t in subscription.target_topics}
            eligible_articles = [
                art
                for art in eligible_articles
                if any(t.upper() in topics_upper for t in getattr(art, "topic_ids", []))
                or any(hasattr(c, "value") and c.value.upper() in topics_upper for c in art.categories)
            ]

        # Truncate to maximum items
        eligible_articles = eligible_articles[: subscription.max_items]

        # Group into summary sections
        company_highlights: List[Dict[str, Any]] = []
        for art in eligible_articles:
            company_highlights.append(
                {
                    "article_id": art.article_id,
                    "headline": art.headline,
                    "publisher_name": art.publisher_name,
                    "published_at": art.published_at.isoformat(),
                    "excerpt": art.permitted_excerpt or art.headline,
                    "url": art.canonical_url,
                }
            )

        # Highlight verified events in window
        event_highlights: List[Dict[str, Any]] = []
        for ev in events_list:
            if period_start <= ev.first_seen_at <= period_end:
                event_highlights.append(
                    {
                        "event_id": ev.event_id,
                        "title": ev.event_title,
                        "entity_name": ev.primary_entity_name,
                        "event_type": ev.event_type.value,
                        "lifecycle_status": ev.lifecycle_status.value,
                        "assertion_status": ev.assertion_status.value,
                    }
                )

        sections = [
            {
                "section_title": "Verified News Highlights",
                "item_count": len(company_highlights),
                "items": company_highlights,
            },
            {
                "section_title": "Financial Corporate Events",
                "item_count": len(event_highlights),
                "items": event_highlights,
            },
        ]

        return NewsDigestRun(
            run_id=f"run-{uuid.uuid4().hex[:12]}",
            digest_id=subscription.digest_id,
            owner_user_id=subscription.owner_user_id,
            title=subscription.title,
            interval_start=period_start,
            interval_end=period_end,
            executed_at=now_utc,
            eligible_article_count=len(eligible_articles),
            unique_story_count=len(stories_list) if stories_list else len(company_highlights),
            verified_event_count=len(event_highlights),
            status="COMPLETED",
            summary_sections=sections,
            attribution_disclaimer="Compiled from authorized institutional news feeds and verified company disclosures.",
        )
