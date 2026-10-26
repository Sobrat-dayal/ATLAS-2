"""Comprehensive Automated Test Suite for News Discovery, Facets, and Timelines (Stage 100)."""

import pytest
from atlas.auth import AuthPrincipal
from atlas.news.enums import (
    NewsCategory,
)
from atlas.news.repository import NewsDiscoveryQuery, NewsRepository
from atlas.news.service import NewsService
from atlas.news.topics import (
    classify_topics_for_article,
    get_topic,
    list_topics,
    resolve_industries_for_article,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.news import get_news_service
from atlas_api.routers.news import router as news_router


@pytest.fixture
def test_user():
    return AuthPrincipal(sub="test-user-100", email="analyst@atlas.institution")


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


# ---------------------------------------------------------------------------
# Topic Taxonomy & Classification Tests
# ---------------------------------------------------------------------------

def test_topics_catalog():
    topics = list_topics()
    assert len(topics) >= 12
    topic_ids = {t.topic_id for t in topics}
    assert "EARNINGS_RELEASES" in topic_ids
    assert "INTEREST_RATES_MONETARY_POLICY" in topic_ids
    assert "INFLATION_PRICES" in topic_ids
    assert "TECHNOLOGY_AI_INNOVATION" in topic_ids

    # Lookup by ID
    fed_topic = get_topic("INTEREST_RATES_MONETARY_POLICY")
    assert fed_topic is not None
    assert fed_topic.category == NewsCategory.CENTRAL_BANKS
    assert "fed funds" in fed_topic.keywords


def test_classify_topics_deterministic():
    # Earnings keywords
    t1 = classify_topics_for_article("Apple quarterly profit and revenue rise above expectations")
    assert "EARNINGS_RELEASES" in t1

    # Monetary policy keywords
    t2 = classify_topics_for_article("Federal Reserve maintains federal funds rate target steady")
    assert "INTEREST_RATES_MONETARY_POLICY" in t2

    # Semiconductor keywords
    t3 = classify_topics_for_article("ASML ships High-NA EUV lithography systems for 2nm semiconductor fabs")
    assert "TECHNOLOGY_AI_INNOVATION" in t3


def test_resolve_industries_deterministic():
    ind_tech = resolve_industries_for_article("NVIDIA Blackwell GPU accelerators deployed in AI data centers")
    assert "TECHNOLOGY" in ind_tech

    ind_energy = resolve_industries_for_article("BP outlines offshore wind and deepwater oil exploration capex")
    assert "ENERGY" in ind_energy

    ind_auto = resolve_industries_for_article("Toyota Motor achieves record vehicle output with hybrid powertrain")
    assert "CONSUMER_DISCRETIONARY" in ind_auto


# ---------------------------------------------------------------------------
# Repository Discovery & Filtering Tests
# ---------------------------------------------------------------------------

def test_discovery_default_all(repo):
    q = NewsDiscoveryQuery(mode="ALL", limit=20)
    res = repo.discover_news(q)
    assert res.total_count >= 10
    assert len(res.articles) > 0
    # Strict chronological ordering
    for i in range(len(res.articles) - 1):
        assert res.articles[i].published_at >= res.articles[i + 1].published_at


def test_discovery_mode_markets(repo):
    q = NewsDiscoveryQuery(mode="MARKETS", limit=20)
    res = repo.discover_news(q)
    market_cats = {"MARKETS", "EQUITIES", "FIXED_INCOME", "FOREIGN_EXCHANGE", "COMMODITIES"}
    for a in res.articles:
        assert any(c.value in market_cats for c in a.categories)


def test_discovery_mode_companies(repo):
    q = NewsDiscoveryQuery(mode="COMPANIES", limit=20)
    res = repo.discover_news(q)
    for a in res.articles:
        assert any(e.entity_type == "COMPANY" for e in a.linked_entities)


def test_discovery_publisher_filter(repo):
    q = NewsDiscoveryQuery(publisher_ids=["bloomberg", "reuters"], limit=20)
    res = repo.discover_news(q)
    assert res.total_count > 0
    for a in res.articles:
        assert a.publisher_id in ("bloomberg", "reuters")


def test_discovery_country_filter(repo):
    q = NewsDiscoveryQuery(country_ids=["IN"], limit=20)
    res = repo.discover_news(q)
    assert res.total_count > 0
    for a in res.articles:
        assert "IN" in a.geographies


def test_discovery_topic_filter(repo):
    q = NewsDiscoveryQuery(topic_ids=["INTEREST_RATES_MONETARY_POLICY"], limit=20)
    res = repo.discover_news(q)
    assert res.total_count > 0
    for a in res.articles:
        assert "INTEREST_RATES_MONETARY_POLICY" in a.topic_ids


def test_discovery_company_filter(repo):
    q = NewsDiscoveryQuery(company_ids=["US0378331005", "Apple Inc."], limit=10)
    res = repo.discover_news(q)
    assert res.total_count >= 1
    assert "Apple" in res.articles[0].headline


def test_discovery_instrument_filter(repo):
    q = NewsDiscoveryQuery(instrument_ids=["NVDA"], limit=10)
    res = repo.discover_news(q)
    assert res.total_count >= 1
    assert "NVIDIA" in res.articles[0].headline


# ---------------------------------------------------------------------------
# Search Phrases, Relevance & Highlighting Tests
# ---------------------------------------------------------------------------

def test_discovery_search_quoted_phrase(repo):
    # Quoted phrase must match exactly
    q = NewsDiscoveryQuery(query='"Blackwell Ultra"', limit=10)
    res = repo.discover_news(q)
    assert res.total_count == 1
    assert "NVIDIA" in res.articles[0].headline


def test_discovery_search_multiple_tokens(repo):
    q = NewsDiscoveryQuery(query='Federal Reserve interest rate', limit=10)
    res = repo.discover_news(q)
    assert res.total_count >= 1
    assert any("Federal Reserve" in a.headline for a in res.articles)


def test_discovery_search_relevance_sort(repo):
    # Query with relevance sort
    q = NewsDiscoveryQuery(query="semiconductor fabs", sort_order="RELEVANCE_DESC", limit=10)
    res = repo.discover_news(q)
    assert res.total_count >= 1
    # Top result should mention semiconductor in headline
    top_headline = res.articles[0].headline.lower()
    assert "asml" in top_headline or "semiconductor" in top_headline or "fabs" in top_headline


def test_discovery_search_injection_safety(repo):
    # Search containing SQL injection pattern and script tags
    nasty_query = "'; DROP TABLE articles; -- <script>alert(1)</script>"
    q = NewsDiscoveryQuery(query=nasty_query, limit=10)
    res = repo.discover_news(q)
    # Should safely return 0 matches without crashing or executing
    assert res.total_count == 0


# ---------------------------------------------------------------------------
# Keyset Pagination Tests
# ---------------------------------------------------------------------------

def test_discovery_keyset_pagination_published_desc(repo):
    q1 = NewsDiscoveryQuery(limit=3, sort_order="PUBLISHED_DESC")
    res1 = repo.discover_news(q1)
    assert len(res1.articles) == 3
    assert res1.has_more is True
    assert res1.next_cursor is not None

    q2 = NewsDiscoveryQuery(limit=3, cursor=res1.next_cursor, sort_order="PUBLISHED_DESC")
    res2 = repo.discover_news(q2)
    assert len(res2.articles) == 3

    # Ensure sets of article IDs are completely disjoint
    ids1 = {a.article_id for a in res1.articles}
    ids2 = {a.article_id for a in res2.articles}
    assert ids1.isdisjoint(ids2)


def test_discovery_keyset_pagination_published_asc(repo):
    q1 = NewsDiscoveryQuery(limit=3, sort_order="PUBLISHED_ASC")
    res1 = repo.discover_news(q1)
    assert len(res1.articles) == 3
    assert res1.has_more is True

    # Check ascending order
    for i in range(len(res1.articles) - 1):
        assert res1.articles[i].published_at <= res1.articles[i + 1].published_at


# ---------------------------------------------------------------------------
# Faceted Search Tests
# ---------------------------------------------------------------------------

def test_facets_computation(repo):
    q = NewsDiscoveryQuery(mode="ALL")
    facets = repo.get_facets(q)
    assert len(facets.sources) > 0
    assert len(facets.publishers) > 0
    assert len(facets.categories) > 0
    assert len(facets.topics) > 0
    assert len(facets.countries) > 0

    # Verify counts sum matches articles with that facet
    src_total = sum(f.count for f in facets.sources)
    assert src_total == repo.discover_news(q).total_count


# ---------------------------------------------------------------------------
# Timeline Grouping & Timezone Tests
# ---------------------------------------------------------------------------

def test_timeline_daily_grouping_utc(repo):
    q = NewsDiscoveryQuery(mode="ALL")
    timeline = repo.get_timeline(q, interval="DAY", tz_name="UTC")
    assert timeline.interval == "DAY"
    assert timeline.timezone == "UTC"
    assert timeline.total_buckets >= 1
    for b in timeline.buckets:
        assert b.article_count == len(b.articles)
        assert b.article_count > 0


def test_timeline_timezone_conversion(repo):
    q = NewsDiscoveryQuery(mode="ALL")
    # New York timezone (EDT / UTC-4)
    tl_ny = repo.get_timeline(q, interval="DAY", tz_name="America/New_York")
    assert tl_ny.timezone == "America/New_York"
    assert len(tl_ny.buckets) >= 1

    # Kolkata timezone (IST / UTC+5:30)
    tl_ist = repo.get_timeline(q, interval="DAY", tz_name="Asia/Kolkata")
    assert tl_ist.timezone == "Asia/Kolkata"
    assert len(tl_ist.buckets) >= 1


# ---------------------------------------------------------------------------
# Autocomplete Search Suggestions Tests
# ---------------------------------------------------------------------------

def test_suggestions_matching(repo):
    # Match company prefix
    s_aapl = repo.get_suggestions("app", limit=5)
    assert len(s_aapl) > 0
    assert any("Apple" in s.title for s in s_aapl)
    assert any(s.type == "COMPANY" for s in s_aapl)

    # Match topic prefix
    s_earn = repo.get_suggestions("earn", limit=5)
    assert any(s.type == "TOPIC" for s in s_earn)

    # Match publisher prefix
    s_reuters = repo.get_suggestions("reut", limit=5)
    assert any("Reuters" in s.title for s in s_reuters)
    assert any(s.type == "PUBLISHER" for s in s_reuters)


# ---------------------------------------------------------------------------
# Watchlist-Scoped News Tests
# ---------------------------------------------------------------------------

def test_watchlist_news_scoped(service):
    # User watching AAPL and MSFT
    res = service.get_watchlist_news(
        user_id="user-123",
        watchlist_id="wl-tech-leaders",
        watched_symbols=["AAPL", "MSFT"],
        limit=10,
    )
    assert res.total_count >= 2
    tickers_in_feed = {
        m.ticker
        for a in res.articles
        for m in a.linked_entities
        if m.ticker
    }
    assert "AAPL" in tickers_in_feed or "MSFT" in tickers_in_feed


def test_watchlist_news_empty_symbols(service):
    res = service.get_watchlist_news(
        user_id="user-123",
        watchlist_id="wl-empty",
        watched_symbols=[],
    )
    assert res.total_count == 0
    assert len(res.articles) == 0


# ---------------------------------------------------------------------------
# FastAPI Endpoints Integration Tests (Stage 100)
# ---------------------------------------------------------------------------

def test_api_discover_endpoint(client):
    payload = {
        "mode": "ALL",
        "query": "infrastructure",
        "limit": 10,
        "sort_order": "PUBLISHED_DESC",
    }
    resp = client.post("/api/v1/news/discover", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "articles" in data
    assert "total_count" in data
    assert "facets" in data
    assert data["total_count"] >= 1


def test_api_facets_endpoint(client):
    payload = {
        "mode": "ALL",
    }
    resp = client.post("/api/v1/news/facets", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "sources" in data
    assert "publishers" in data
    assert "categories" in data
    assert "topics" in data


def test_api_timeline_endpoint(client):
    payload = {
        "query": {"mode": "ALL"},
        "interval": "DAY",
        "timezone": "UTC",
    }
    resp = client.post("/api/v1/news/timeline", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["interval"] == "DAY"
    assert "buckets" in data
    assert len(data["buckets"]) >= 1


def test_api_topics_endpoints(client):
    resp = client.get("/api/v1/news/topics")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 12

    # Single topic lookup
    resp2 = client.get("/api/v1/news/topics/EARNINGS_RELEASES")
    assert resp2.status_code == 200
    top = resp2.json()
    assert top["topic_id"] == "EARNINGS_RELEASES"
    assert top["canonical_name"] == "Earnings & Financial Results"

    # Non-existent topic
    resp3 = client.get("/api/v1/news/topics/INVALID_TOPIC_SLUG")
    assert resp3.status_code == 404


def test_api_suggestions_endpoint(client):
    resp = client.get("/api/v1/news/suggestions?q=aapl&limit=5")
    assert resp.status_code == 200
    suggestions = resp.json()
    assert len(suggestions) >= 1
    assert suggestions[0]["type"] == "COMPANY"
    assert "AAPL" in suggestions[0]["title"]
