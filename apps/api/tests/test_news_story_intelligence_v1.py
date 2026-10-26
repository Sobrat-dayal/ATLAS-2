"""Comprehensive Automated Test Suite for Financial News Story Intelligence and Event Classification (Stage 101)."""

from datetime import datetime, timezone

import pytest
from atlas.auth import AuthPrincipal
from atlas.news.articles import NewsArticle
from atlas.news.enums import (
    EventAmountApproximation,
    EventAmountType,
    FinancialEventType,
    NewsArticleType,
    NewsCategory,
    NewsEventAssertionStatus,
    NewsEventLifecycleStatus,
    NewsEvidenceType,
    NewsStoryStatus,
)
from atlas.news.events import (
    EVENT_TYPE_CATALOG,
    EventClassificationEngine,
)
from atlas.news.origin import NewsDataOrigin
from atlas.news.repository import NewsRepository, NewsStoryQuery
from atlas.news.service import NewsService
from atlas.news.stories import StoryClusteringEngine
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.news import get_news_service
from atlas_api.routers.news import router as news_router


@pytest.fixture
def test_user():
    return AuthPrincipal(sub="test-user-101", email="senior.analyst@atlas.institution")


@pytest.fixture
def repo():
    return NewsRepository()


@pytest.fixture
def service(repo):
    return NewsService(repository=repo)


@pytest.fixture
def client(service, test_user):
    app = FastAPI()
    app.include_router(news_router)
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_news_service] = lambda: service
    return TestClient(app)


DEFAULT_ORIGIN = NewsDataOrigin(
    provider_id="test_provider",
    extracted_at=datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc),
    provider_internal_id="test-origin-id",
)


# ---------------------------------------------------------------------------
# 1. Story Clustering & False-Positive Guard Tests
# ---------------------------------------------------------------------------

def test_baseline_stories_populated(repo):
    """Verifies that baseline seed articles automatically clustered into canonical Story Threads."""
    result = repo.list_stories(NewsStoryQuery(limit=50))
    assert result.total_count >= 10
    assert len(result.stories) >= 10

    # Ensure stable story IDs starting with 'story-'
    for story in result.stories:
        assert story.story_id.startswith("story-")
        assert story.display_title
        assert story.article_count >= 1
        assert story.independent_publisher_count >= 1
        assert len(story.publishers) >= 1
        assert story.story_status == NewsStoryStatus.ACTIVE


def test_story_clustering_matching_announcement():
    """Verifies that multiple reports about the same announcement cluster into one thread."""
    engine = StoryClusteringEngine()
    existing_stories = []
    articles_by_id = {}

    art1 = NewsArticle(
        article_id="art-test-1",
        source_provider_id="corporate_press_wire",
        publisher_id="businesswire",
        publisher_name="Business Wire",
        title="Acme Corp Announces Definitive Agreement to Acquire CyberTech for $2.5 Billion",
        headline="Acme Corp Announces Definitive Agreement to Acquire CyberTech for $2.5 Billion",
        canonical_url="https://example.com/acme1",
        original_url="https://example.com/acme1",
        language="en",
        article_type=NewsArticleType.PRESS_RELEASE,
        published_at=datetime(2026, 10, 26, 10, 0, 0, tzinfo=timezone.utc),
        categories=(NewsCategory.COMPANY, NewsCategory.EQUITIES),
        topic_ids=("MERGERS_ACQUISITIONS",),
        origin=DEFAULT_ORIGIN,
    )
    articles_by_id[art1.article_id] = art1
    story1, is_new1 = engine.cluster_article(art1, existing_stories, articles_by_id)
    assert is_new1 is True
    existing_stories.append(story1)

    # Second article from Reuters covering the exact same acquisition announcement
    art2 = NewsArticle(
        article_id="art-test-2",
        source_provider_id="financial_wire_direct",
        publisher_id="reuters",
        publisher_name="Reuters",
        title="Acme Corp agrees to acquire CyberTech in $2.5 billion enterprise deal",
        headline="Acme Corp agrees to acquire CyberTech in $2.5 billion enterprise deal",
        canonical_url="https://reuters.com/acme2",
        original_url="https://reuters.com/acme2",
        language="en",
        article_type=NewsArticleType.WIRE_REPORT,
        published_at=datetime(2026, 10, 26, 10, 30, 0, tzinfo=timezone.utc),
        categories=(NewsCategory.COMPANY, NewsCategory.EQUITIES),
        topic_ids=("MERGERS_ACQUISITIONS",),
        origin=DEFAULT_ORIGIN,
    )
    articles_by_id[art2.article_id] = art2
    story2, is_new2 = engine.cluster_article(art2, existing_stories, articles_by_id)

    # Must join the existing thread!
    assert is_new2 is False
    assert story2.story_id == story1.story_id
    assert story2.article_count == 2
    assert story2.independent_publisher_count == 2
    assert "Business Wire" in story2.publishers
    assert "Reuters" in story2.publishers


def test_story_clustering_false_positive_guard():
    """Verifies that mentioning the same company or topic alone does NOT cause false grouping."""
    engine = StoryClusteringEngine()
    existing_stories = []
    articles_by_id = {}

    # Article 1: Tata Motors demerger
    art1 = NewsArticle(
        article_id="art-tm-1",
        source_provider_id="corporate_press_wire",
        publisher_id="businesswire",
        publisher_name="Business Wire",
        title="Tata Motors Board Approves Demerger of Commercial and Passenger Vehicle Businesses",
        headline="Tata Motors Board Approves Demerger of Commercial and Passenger Vehicle Businesses",
        canonical_url="https://example.com/tm1",
        original_url="https://example.com/tm1",
        language="en",
        article_type=NewsArticleType.PRESS_RELEASE,
        published_at=datetime(2026, 10, 26, 11, 0, 0, tzinfo=timezone.utc),
        categories=(NewsCategory.COMPANY,),
        topic_ids=("MERGERS_ACQUISITIONS",),
        origin=DEFAULT_ORIGIN,
    )
    articles_by_id[art1.article_id] = art1
    s1, _ = engine.cluster_article(art1, existing_stories, articles_by_id)
    existing_stories.append(s1)

    # Article 2: Tata Motors new facility opening in Pune (same company, completely different development)
    art2 = NewsArticle(
        article_id="art-tm-2",
        source_provider_id="corporate_press_wire",
        publisher_id="businesswire",
        publisher_name="Business Wire",
        title="Tata Motors Inundates Solar Generation at Pune Manufacturing Facility",
        headline="Tata Motors Inundates Solar Generation at Pune Manufacturing Facility",
        canonical_url="https://example.com/tm2",
        original_url="https://example.com/tm2",
        language="en",
        article_type=NewsArticleType.PRESS_RELEASE,
        published_at=datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc),
        categories=(NewsCategory.COMPANY,),
        topic_ids=("CORPORATE_GOVERNANCE_LEADERSHIP",),
        origin=DEFAULT_ORIGIN,
    )
    articles_by_id[art2.article_id] = art2
    s2, is_new2 = engine.cluster_article(art2, existing_stories, articles_by_id)

    # Must NOT cluster together!
    assert is_new2 is True
    assert s2.story_id != s1.story_id


def test_story_merge_and_split(repo):
    """Tests administrative merge and split operations with full auditability."""
    stories = repo.list_stories(NewsStoryQuery(limit=5)).stories
    assert len(stories) >= 2
    s1 = stories[0]
    s2 = stories[1]

    # Ingest a second article into s1 so it has >= 2 articles
    new_art = NewsArticle(
        article_id="art-split-test-helper",
        source_provider_id="openbb_news",
        publisher_id="bloomberg",
        publisher_name="Bloomberg News",
        title=f"Update: {s1.display_title}",
        headline=f"Update: {s1.display_title}",
        canonical_url="https://bloomberg.com/split-test",
        original_url="https://bloomberg.com/split-test",
        language="en",
        article_type=NewsArticleType.NEWS_REPORT,
        published_at=datetime(2026, 10, 26, 13, 0, 0, tzinfo=timezone.utc),
        categories=(NewsCategory.COMPANY,),
        origin=DEFAULT_ORIGIN,
    )
    repo.ingest_articles([new_art])

    # Re-retrieve s1
    target = repo.get_story(s1.story_id)
    assert target is not None

    # Merge s2 into target
    merged = repo.merge_stories(target.story_id, s2.story_id)
    assert merged.story_id == target.story_id
    assert s2.article_ids[0] in merged.article_ids
    # Verify s2 is marked as MERGED
    updated_s2 = repo.get_story(s2.story_id)
    assert updated_s2.story_status == NewsStoryStatus.MERGED

    # Split one article into a child thread
    parent_after, child = repo.split_story(
        story_id=merged.story_id,
        article_ids_to_split=[new_art.article_id],
        new_title="Separated Analysis Branch for Story",
    )
    assert new_art.article_id not in parent_after.article_ids
    assert new_art.article_id in child.article_ids
    assert child.display_title == "Separated Analysis Branch for Story"


# ---------------------------------------------------------------------------
# 2. Financial Event Taxonomy & Classification Tests
# ---------------------------------------------------------------------------

def test_event_type_catalog():
    """Verifies that the canonical event taxonomy has at least 15 comprehensive event types."""
    assert len(EVENT_TYPE_CATALOG) >= 15
    type_ids = {t.event_type_id for t in EVENT_TYPE_CATALOG}
    assert FinancialEventType.EARNINGS_RELEASE in type_ids
    assert FinancialEventType.EARNINGS_GUIDANCE in type_ids
    assert FinancialEventType.DIVIDEND_DECLARATION in type_ids
    assert FinancialEventType.SHARE_REPURCHASE in type_ids
    assert FinancialEventType.MERGER_ACQUISITION_AGREEMENT in type_ids
    assert FinancialEventType.MERGER_ACQUISITION_PROPOSAL in type_ids
    assert FinancialEventType.CENTRAL_BANK_POLICY_DECISION in type_ids
    assert FinancialEventType.REGULATORY_ACTION in type_ids
    assert FinancialEventType.EQUITY_FINANCING in type_ids
    assert FinancialEventType.PRODUCT_LAUNCH in type_ids


def test_event_classification_central_bank():
    """Tests deterministic extraction of Central Bank rate hold event."""
    engine = EventClassificationEngine()
    art = NewsArticle(
        article_id="art-test-fomc",
        source_provider_id="regulator_announcements",
        publisher_id="fed_reserve",
        publisher_name="Federal Reserve Board",
        title="Federal Reserve Holds Policy Target Rate Steady at 5.25%-5.50% Following FOMC Meeting",
        headline="Federal Reserve Holds Policy Target Rate Steady at 5.25%-5.50% Following FOMC Meeting",
        canonical_url="https://federalreserve.gov/fomc",
        original_url="https://federalreserve.gov/fomc",
        language="en",
        article_type=NewsArticleType.OFFICIAL_ANNOUNCEMENT,
        published_at=datetime(2026, 10, 26, 18, 0, 0, tzinfo=timezone.utc),
        categories=(NewsCategory.CENTRAL_BANKS, NewsCategory.ECONOMICS),
        topic_ids=("INTEREST_RATES_MONETARY_POLICY",),
        origin=DEFAULT_ORIGIN,
    )

    events = engine.classify_article(art, linked_story_id="story-fed")
    assert len(events) == 1
    ev = events[0]

    assert ev.event_type == FinancialEventType.CENTRAL_BANK_POLICY_DECISION
    assert ev.lifecycle_status == NewsEventLifecycleStatus.ANNOUNCED
    assert ev.assertion_status == NewsEventAssertionStatus.OFFICIALLY_REPORTED
    assert len(ev.evidence_records) == 1
    assert ev.evidence_records[0].evidence_type == NewsEvidenceType.CENTRAL_BANK_RELEASE
    assert ev.linked_story_ids == ["story-fed"]

    # Verify interest rate amount extraction
    assert len(ev.amounts) >= 1
    amt = ev.amounts[0]
    assert amt.amount_type == EventAmountType.INTEREST_RATE_TARGET
    assert amt.amount_value in (5.25, 5.5)
    assert amt.currency == "PERCENT"


def test_event_classification_rumor_vs_official():
    """Verifies that rumors are classified with RUMORED assertion status and PROPOSED lifecycle."""
    engine = EventClassificationEngine()

    rumor_art = NewsArticle(
        article_id="art-test-rumor",
        source_provider_id="openbb_news",
        publisher_id="bloomberg",
        publisher_name="Bloomberg News",
        title="Acme Corp is considering a buyout of BetaTech for $500 million, people familiar say",
        headline="Acme Corp is considering a buyout of BetaTech for $500 million, people familiar say",
        canonical_url="https://bloomberg.com/rumor",
        original_url="https://bloomberg.com/rumor",
        language="en",
        article_type=NewsArticleType.NEWS_REPORT,
        published_at=datetime(2026, 10, 26, 14, 0, 0, tzinfo=timezone.utc),
        categories=(NewsCategory.COMPANY,),
        topic_ids=("MERGERS_ACQUISITIONS",),
        origin=DEFAULT_ORIGIN,
    )

    events = engine.classify_article(rumor_art)
    assert len(events) == 1
    ev = events[0]

    # Must be categorized as rumor and proposed — NEVER announced agreement!
    assert ev.event_type == FinancialEventType.MERGER_ACQUISITION_PROPOSAL
    assert ev.assertion_status == NewsEventAssertionStatus.RUMORED
    assert ev.lifecycle_status == NewsEventLifecycleStatus.PROPOSED
    assert len(ev.amounts) == 1
    assert ev.amounts[0].amount_value == 500_000_000.0


def test_event_classification_amount_extraction():
    """Verifies source-reported amount extraction without arbitrary FX or hallucination."""
    engine = EventClassificationEngine()

    art = NewsArticle(
        article_id="art-test-buyback",
        source_provider_id="corporate_press_wire",
        publisher_id="prnewswire",
        publisher_name="PR Newswire",
        title="Global Corp Authorizes $10 billion Share Repurchase Program",
        headline="Global Corp Authorizes $10 billion Share Repurchase Program",
        canonical_url="https://prnewswire.com/buyback",
        original_url="https://prnewswire.com/buyback",
        language="en",
        article_type=NewsArticleType.PRESS_RELEASE,
        published_at=datetime(2026, 10, 26, 15, 0, 0, tzinfo=timezone.utc),
        categories=(NewsCategory.COMPANY,),
        topic_ids=("SHARE_BUYBACKS",),
        origin=DEFAULT_ORIGIN,
    )

    events = engine.classify_article(art)
    assert len(events) == 1
    ev = events[0]

    assert ev.event_type == FinancialEventType.SHARE_REPURCHASE
    assert len(ev.amounts) == 1
    assert ev.amounts[0].amount_type == EventAmountType.BUYBACK_AUTHORIZATION
    assert ev.amounts[0].amount_value == 10_000_000_000.0
    assert ev.amounts[0].currency == "USD"
    assert ev.amounts[0].approximation_status == EventAmountApproximation.EXACT


# ---------------------------------------------------------------------------
# 3. REST API Integration Tests
# ---------------------------------------------------------------------------

def test_api_get_stories(client):
    """GET /api/v1/news/stories"""
    res = client.get("/api/v1/news/stories?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "stories" in data
    assert "total_count" in data
    assert len(data["stories"]) >= 5

    story = data["stories"][0]
    assert story["story_id"].startswith("story-")
    assert "display_title" in story
    assert "article_count" in story
    assert "publishers" in story


def test_api_get_story_details(client):
    """GET /api/v1/news/stories/{story_id} and member articles"""
    feed_res = client.get("/api/v1/news/stories?limit=1")
    story_id = feed_res.json()["stories"][0]["story_id"]

    res = client.get(f"/api/v1/news/stories/{story_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["story_id"] == story_id

    # Member articles endpoint
    art_res = client.get(f"/api/v1/news/stories/{story_id}/articles")
    assert art_res.status_code == 200
    articles = art_res.json()
    assert len(articles) >= 1
    assert articles[0]["article_id"] in data["article_ids"]

    # Linked events endpoint
    ev_res = client.get(f"/api/v1/news/stories/{story_id}/events")
    assert ev_res.status_code == 200
    assert isinstance(ev_res.json(), list)


def test_api_get_story_not_found(client):
    """GET /api/v1/news/stories/{story_id} with invalid ID returns 404."""
    res = client.get("/api/v1/news/stories/story-nonexistent-12345")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_api_get_event_types(client):
    """GET /api/v1/news/events/types"""
    res = client.get("/api/v1/news/events/types")
    assert res.status_code == 200
    types = res.json()
    assert len(types) >= 15
    type_labels = {t["canonical_label"] for t in types}
    assert "Earnings Release" in type_labels
    assert "Central Bank Policy Decision" in type_labels


def test_api_get_events(client):
    """GET /api/v1/news/events"""
    res = client.get("/api/v1/news/events?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "events" in data
    assert "total_count" in data
    assert len(data["events"]) >= 5

    ev = data["events"][0]
    assert ev["event_id"].startswith("fev-")
    assert "event_type" in ev
    assert "lifecycle_status" in ev
    assert "assertion_status" in ev
    assert "participants" in ev
    assert "evidence_records" in ev


def test_api_get_event_details_and_evidence(client):
    """GET /api/v1/news/events/{event_id} and /evidence"""
    feed_res = client.get("/api/v1/news/events?limit=1")
    event_id = feed_res.json()["events"][0]["event_id"]

    res = client.get(f"/api/v1/news/events/{event_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["event_id"] == event_id

    # Evidence endpoint
    evd_res = client.get(f"/api/v1/news/events/{event_id}/evidence")
    assert evd_res.status_code == 200
    records = evd_res.json()
    assert len(records) >= 1
    assert records[0]["event_id"] == event_id
    assert "headline" in records[0]
    assert "publisher_name" in records[0]


def test_api_get_event_not_found(client):
    """GET /api/v1/news/events/{event_id} with invalid ID returns 404."""
    res = client.get("/api/v1/news/events/fev-nonexistent-12345")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_api_get_entity_events(client):
    """GET /api/v1/news/entities/{entity_id}/events"""
    feed_res = client.get("/api/v1/news/events?limit=1")
    primary_entity = feed_res.json()["events"][0]["primary_entity_id"]

    res = client.get(f"/api/v1/news/entities/{primary_entity}/events")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 1
    assert any(e["primary_entity_id"] == primary_entity for e in events)
