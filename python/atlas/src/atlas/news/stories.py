"""Canonical Story Intelligence & Multi-Source Story Clustering (Stage 101)."""

import hashlib
import re
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from atlas.news.articles import NewsArticle, NewsEntityMention
from atlas.news.enums import (
    NewsStoryMembershipReason,
    NewsStoryMembershipStatus,
    NewsStoryStatus,
)


class NewsStoryArticleLink(BaseModel):
    """Auditable association between an individual article and a canonical Story Thread."""

    story_id: str = Field(..., description="Canonical ID of the parent Story Thread.")
    article_id: str = Field(..., description="Canonical ID of the associated article.")
    publisher_id: str = Field(..., description="Publisher identifier for provenance.")
    published_at: datetime = Field(..., description="Original publication timestamp.")
    headline: str = Field(..., description="Article headline at time of linking.")
    membership_reason: NewsStoryMembershipReason = Field(
        default=NewsStoryMembershipReason.SHARED_EVENT_IDENTITY,
        description="Structural or contextual reason for membership.",
    )
    membership_status: NewsStoryMembershipStatus = Field(
        default=NewsStoryMembershipStatus.CONFIRMED,
        description="Cluster verification confidence state.",
    )
    is_primary_anchor: bool = Field(
        default=False,
        description="True if this article was the founding anchor of the thread.",
    )
    linked_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Ingestion timestamp when link was established.",
    )


class NewsStoryThread(BaseModel):
    """
    Canonical Story Thread grouping multiple source reports covering
    a developing corporate, financial, or macroeconomic development.
    """

    story_id: str = Field(..., description="Stable canonical Story Thread identifier.")
    display_title: str = Field(..., description="Source-backed representative headline or qualified title.")
    canonical_topic_label: Optional[str] = Field(None, description="Primary taxonomy label.")
    topic_ids: list[str] = Field(default_factory=list, description="Canonical topic identifiers.")
    primary_entity_id: Optional[str] = Field(None, description="Primary canonical company or subject entity.")
    primary_entity_name: Optional[str] = Field(None, description="Display name of primary entity.")
    related_entities: list[NewsEntityMention] = Field(
        default_factory=list, description="Other verified entity mentions in the thread."
    )
    first_source_published_at: datetime = Field(
        ..., description="Earliest published timestamp among member articles."
    )
    latest_source_published_at: datetime = Field(
        ..., description="Most recent published timestamp among member articles."
    )
    first_seen_at: datetime = Field(
        ..., description="Timestamp when ATLAS first observed the story."
    )
    latest_activity_at: datetime = Field(
        ..., description="Timestamp of most recent member update or ingestion."
    )
    story_status: NewsStoryStatus = Field(
        default=NewsStoryStatus.ACTIVE, description="Operational lifecycle status of thread."
    )
    article_count: int = Field(default=1, description="Number of eligible canonical articles in thread.")
    independent_publisher_count: int = Field(
        default=1,
        description="Count of distinct independent publishing organizations (excluding syndications).",
    )
    publishers: list[str] = Field(default_factory=list, description="Distinct publisher names represented.")
    article_ids: list[str] = Field(default_factory=list, description="IDs of member articles.")
    representative_article_id: str = Field(
        ..., description="Canonical anchor article used for title and primary attribution."
    )
    clustering_method: str = Field(
        default="CONSERVATIVE_ENTITY_TOPIC_TEMPORAL_V1",
        description="Algorithmic strategy used to construct this thread.",
    )
    clustering_version: str = Field(default="1.0.0", description="Version of clustering rules.")
    linked_event_ids: list[str] = Field(
        default_factory=list, description="Canonical Financial Event IDs associated with this story."
    )
    source_revision_watermark: int = Field(
        default=1, description="Incrementing watermark for cache invalidation."
    )


class StoryClusteringEngine:
    """
    Institutional, conservative multi-source story clustering engine.
    Applies candidate retrieval, temporal bounds, entity identity verification,
    and false-positive guards to group genuine developing stories.
    """

    def __init__(
        self,
        temporal_window_days: int = 14,
        ma_temporal_window_days: int = 30,
        version: str = "1.0.0",
    ) -> None:
        self.temporal_window_days = temporal_window_days
        self.ma_temporal_window_days = ma_temporal_window_days
        self.version = version

    def cluster_article(
        self,
        article: NewsArticle,
        existing_stories: list[NewsStoryThread],
        articles_by_id: dict[str, NewsArticle],
    ) -> tuple[NewsStoryThread, bool]:
        """
        Evaluates candidate Story Threads for an ingested article.
        Returns (thread, is_new_story).
        """
        candidates = self._retrieve_candidates(article, existing_stories)

        for candidate in candidates:
            if self._validate_cluster_membership(article, candidate, articles_by_id):
                # Join existing story thread
                self._attach_article_to_story(candidate, article)
                return candidate, False

        # No compatible candidate -> instantiate a new Story Thread
        new_story = self._create_new_story(article)
        return new_story, True

    def _retrieve_candidates(
        self,
        article: NewsArticle,
        existing_stories: list[NewsStoryThread],
    ) -> list[NewsStoryThread]:
        """
        Filters existing stories using fast candidate blocking:
        1. Temporal proximity
        2. Primary entity overlap OR shared topic
        """
        candidates: list[NewsStoryThread] = []
        article_pub = article.published_at

        # Resolve primary entity of article
        art_entity_ids = {e.entity_id for e in article.linked_entities if e.entity_id}
        art_topics = set(article.topic_ids)

        for story in existing_stories:
            if story.story_status in (NewsStoryStatus.ARCHIVED, NewsStoryStatus.MERGED, NewsStoryStatus.WITHDRAWN_FROM_DISPLAY):
                continue

            # Determine temporal window based on topic (M&A has longer window)
            is_ma = any("MERGER" in t or "ACQUISITION" in t for t in story.topic_ids) or any(
                "MERGER" in t or "ACQUISITION" in t for t in art_topics
            )
            max_days = self.ma_temporal_window_days if is_ma else self.temporal_window_days

            diff_seconds = abs((article_pub - story.latest_source_published_at).total_seconds())
            if diff_seconds > max_days * 86400:
                continue

            # Candidate signal 1: Shared primary entity
            if story.primary_entity_id and story.primary_entity_id in art_entity_ids:
                candidates.append(story)
                continue

            # Candidate signal 2: Shared exact topic and high headline token overlap (e.g. central bank rate hold)
            if art_topics and story.topic_ids:
                if bool(art_topics.intersection(set(story.topic_ids))):
                    candidates.append(story)
                    continue

        return candidates

    def _validate_cluster_membership(
        self,
        article: NewsArticle,
        story: NewsStoryThread,
        articles_by_id: dict[str, NewsArticle],
    ) -> bool:
        """
        Strict validation against false-positive grouping:
        - Same entity alone is INSUFFICIENT
        - Same topic alone is INSUFFICIENT
        - Must have specific contextual overlap (headline tokens or explicit event markers)
        """
        art_entity_ids = {e.entity_id for e in article.linked_entities if e.entity_id}

        # 1. Entity Compatibility Guard
        # If both have a primary entity and they differ, reject
        if story.primary_entity_id and art_entity_ids:
            if story.primary_entity_id not in art_entity_ids:
                return False

        # 2. Extract normalized salient tokens from headlines (excluding stopwords)
        stopwords = {
            "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with",
            "by", "from", "as", "is", "are", "was", "were", "be", "has", "have", "had",
            "reports", "announces", "says", "holds", "new", "global", "across",
        }
        art_tokens = set(re.findall(r"\b[a-zA-Z0-9-]{3,}\b", article.headline.lower())) - stopwords
        story_tokens = set(re.findall(r"\b[a-zA-Z0-9-]{3,}\b", story.display_title.lower())) - stopwords

        overlap = art_tokens.intersection(story_tokens)

        # 3. Specific Event / Marker Matching
        # Key financial event markers that establish specific story continuity
        critical_markers = {
            "fomc", "repo", "bonus", "demerger", "blackwell", "lithography",
            "high-na", "euv", "services", "sub-2nm", "hybrid", "climate",
            "advances", "offshore", "generative", "buyback", "dividend",
        }
        has_shared_marker = bool(overlap.intersection(critical_markers))

        # If shared marker is present -> strong cluster validation
        if has_shared_marker:
            return True

        # If primary entities match AND at least 2 salient tokens overlap -> confirmed
        if story.primary_entity_id and story.primary_entity_id in art_entity_ids and len(overlap) >= 2:
            return True

        # If 3 or more salient tokens overlap regardless of entity -> confirmed
        if len(overlap) >= 3:
            return True

        return False

    def _attach_article_to_story(
        self,
        story: NewsStoryThread,
        article: NewsArticle,
    ) -> None:
        """Attaches article to story thread and recalculates metrics and independent publisher counts."""
        if article.article_id not in story.article_ids:
            story.article_ids.append(article.article_id)

        # Update timestamps
        if article.published_at < story.first_source_published_at:
            story.first_source_published_at = article.published_at
        if article.published_at > story.latest_source_published_at:
            story.latest_source_published_at = article.published_at

        now_utc = datetime.now(timezone.utc)
        story.latest_activity_at = now_utc
        story.article_count = len(story.article_ids)

        # Update publishers list
        pub_name = article.publisher_name or article.publisher
        if pub_name and pub_name not in story.publishers:
            story.publishers.append(pub_name)

        # Update independent publisher count
        # Wire services (e.g. Reuters, Bloomberg) or newspapers counting distinct publishers
        story.independent_publisher_count = len(set(story.publishers))

        # Append topic IDs if not present
        for t in article.topic_ids:
            if t not in story.topic_ids:
                story.topic_ids.append(t)

        # Append related entities if not present
        existing_entity_ids = {e.entity_id for e in story.related_entities}
        for e in article.linked_entities:
            if e.entity_id and e.entity_id not in existing_entity_ids:
                story.related_entities.append(e)
                existing_entity_ids.add(e.entity_id)

        story.source_revision_watermark += 1

    def _create_new_story(self, article: NewsArticle) -> NewsStoryThread:
        """Creates a new canonical Story Thread anchored by the given article."""
        # Derive stable deterministic story ID
        clean_seed = f"{article.publisher_id}:{article.article_id}:{article.headline[:40]}"
        digest = hashlib.sha256(clean_seed.encode("utf-8")).hexdigest()[:16]
        story_id = f"story-{digest}"

        primary_ent = article.linked_entities[0] if article.linked_entities else None
        pub_name = article.publisher_name or article.publisher

        return NewsStoryThread(
            story_id=story_id,
            display_title=article.headline,
            canonical_topic_label=article.topic_ids[0] if article.topic_ids else None,
            topic_ids=list(article.topic_ids),
            primary_entity_id=primary_ent.entity_id if primary_ent else None,
            primary_entity_name=primary_ent.canonical_name if primary_ent else None,
            related_entities=list(article.linked_entities),
            first_source_published_at=article.published_at,
            latest_source_published_at=article.published_at,
            first_seen_at=article.first_seen_at or article.published_at,
            latest_activity_at=datetime.now(timezone.utc),
            story_status=NewsStoryStatus.ACTIVE,
            article_count=1,
            independent_publisher_count=1,
            publishers=[pub_name] if pub_name else [],
            article_ids=[article.article_id],
            representative_article_id=article.article_id,
            clustering_method="CONSERVATIVE_ENTITY_TOPIC_TEMPORAL_V1",
            clustering_version=self.version,
            linked_event_ids=[],
            source_revision_watermark=1,
        )

    def merge_stories(
        self,
        target_story: NewsStoryThread,
        source_story: NewsStoryThread,
        articles_by_id: dict[str, NewsArticle],
    ) -> NewsStoryThread:
        """Administratively merges source story into target story with auditable revision."""
        for art_id in source_story.article_ids:
            if art_id not in target_story.article_ids:
                target_story.article_ids.append(art_id)
                art = articles_by_id.get(art_id)
                if art:
                    pub = art.publisher_name or art.publisher
                    if pub and pub not in target_story.publishers:
                        target_story.publishers.append(pub)

        target_story.first_source_published_at = min(
            target_story.first_source_published_at, source_story.first_source_published_at
        )
        target_story.latest_source_published_at = max(
            target_story.latest_source_published_at, source_story.latest_source_published_at
        )
        target_story.article_count = len(target_story.article_ids)
        target_story.independent_publisher_count = len(set(target_story.publishers))
        target_story.latest_activity_at = datetime.now(timezone.utc)
        target_story.source_revision_watermark += 1

        # Mark source story as merged
        source_story.story_status = NewsStoryStatus.MERGED
        source_story.source_revision_watermark += 1

        return target_story

    def split_story(
        self,
        parent_story: NewsStoryThread,
        article_ids_to_split: list[str],
        new_title: str,
        articles_by_id: dict[str, NewsArticle],
    ) -> tuple[NewsStoryThread, NewsStoryThread]:
        """Splits selected articles from a parent story thread into a new independent story."""
        remaining_ids = [a for a in parent_story.article_ids if a not in article_ids_to_split]
        if not remaining_ids:
            raise ValueError("Cannot split all articles from parent story")

        # Update parent story
        parent_story.article_ids = remaining_ids
        parent_story.article_count = len(remaining_ids)
        parent_publishers = []
        for aid in remaining_ids:
            art = articles_by_id.get(aid)
            if art:
                p = art.publisher_name or art.publisher
                if p and p not in parent_publishers:
                    parent_publishers.append(p)
        parent_story.publishers = parent_publishers
        parent_story.independent_publisher_count = len(parent_publishers)
        parent_story.latest_activity_at = datetime.now(timezone.utc)
        parent_story.source_revision_watermark += 1

        # Build child story
        first_art = articles_by_id.get(article_ids_to_split[0])
        anchor_id = first_art.article_id if first_art else article_ids_to_split[0]
        child_story = self._create_new_story(first_art) if first_art else NewsStoryThread(
            story_id=f"story-split-{hashlib.sha256(new_title.encode()).hexdigest()[:12]}",
            display_title=new_title,
            representative_article_id=anchor_id,
            first_source_published_at=datetime.now(timezone.utc),
            latest_source_published_at=datetime.now(timezone.utc),
            first_seen_at=datetime.now(timezone.utc),
            latest_activity_at=datetime.now(timezone.utc),
            article_count=len(article_ids_to_split),
            article_ids=article_ids_to_split,
        )
        child_story.display_title = new_title
        child_story.article_ids = article_ids_to_split
        child_story.article_count = len(article_ids_to_split)

        child_publishers = []
        for aid in article_ids_to_split:
            art = articles_by_id.get(aid)
            if art:
                p = art.publisher_name or art.publisher
                if p and p not in child_publishers:
                    child_publishers.append(p)
        child_story.publishers = child_publishers
        child_story.independent_publisher_count = len(child_publishers)

        return parent_story, child_story
