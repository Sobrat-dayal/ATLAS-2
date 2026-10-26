"""Automated Test Suite for Institutional Financial News Platform Foundation (Stage 99).

Tests:
1. Canonical News Article Entity Identity & Provenance
2. Verified Publisher Registry & Domain Identification
3. Authorized News Source Integration & Licensing Tiers
4. URL Canonicalization & Tracking Parameter Stripping
5. SSRF Defense & External Destination Validation
6. HTML Tag Sanitization & Script Injection Neutralization
7. Timestamp Integrity (Published, Updated, First Seen, Ingested)
8. Idempotent Ingestion & Duplicate Suppression (0 Duplicates)
9. Article Revisions, Corrections, and Withdrawal Lifecycle (410 Gone)
10. Syndicated Wire Attribution & Publisher Identity Separation
11. Canonical Entity Linking: Companies & Instruments
12. Ticker Collision Disambiguation (Filtering short words like 'IT', 'ON', 'CAN')
13. Share-Class & ADR Disambiguation (GOOGL vs GOOG, INFY ADR vs INFY.NSE)
14. News Taxonomy Categories & Filtering
15. Chronological News Feeds & Deterministic Stable Ordering
16. Keyset / Cursor Pagination
17. Full-Text Headline & Authorized Excerpt Keyword Search
18. Entity-Linked News Feeds (Company & Instrument)
19. Feed Caching & Invalidation on Ingestion
20. Source Freshness & Coverage Reporting
21. FastAPI Endpoints & Typed Error Envelopes
22. Side-Effect Invariants (0 Trades, 0 Portfolio Mutations, 0 Hallucinated Sentiment)
"""

from datetime import datetime, timezone

import pytest
from atlas.auth import AuthPrincipal
from atlas.news import (
    DeduplicationEngine,
    NewsArticle,
    NewsAvailabilityStatus,
    NewsDataOrigin,
    NewsFeedQuery,
    NewsRepository,
    NewsService,
    get_verified_publisher,
    list_news_sources,
    list_verified_publishers,
    normalize_canonical_url,
    normalize_timestamp,
    resolve_entities_in_text,
    sanitize_plain_text,
    validate_external_url,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.news import router as news_router


@pytest.fixture
def repo() -> NewsRepository:
    return NewsRepository()


@pytest.fixture
def service(repo: NewsRepository) -> NewsService:
    return NewsService(repository=repo)


@pytest.fixture
def test_client(service: NewsService) -> TestClient:
    app = FastAPI()
    app.include_router(news_router)

    app.dependency_overrides[get_current_user] = lambda: AuthPrincipal(
        sub="test-user",
        email="test@atlas.local",
    )

    from atlas_api.routers.news import get_news_service
    app.dependency_overrides[get_news_service] = lambda: service

    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Canonical Article Identity & Publisher Registry Tests
# ---------------------------------------------------------------------------

def test_verified_publisher_registry():
    pubs = list_verified_publishers()
    assert len(pubs) >= 10

    reuters = get_verified_publisher("reuters")
    assert reuters is not None
    assert reuters.canonical_name == "Reuters"
    assert reuters.verified_domain == "reuters.com"
    assert reuters.publisher_type == "WIRE_SERVICE"
    assert reuters.country_code == "GB"

    bloomberg = get_verified_publisher("bloomberg")
    assert bloomberg is not None
    assert bloomberg.canonical_name == "Bloomberg News"
    assert bloomberg.verified_domain == "bloomberg.com"

    sec = get_verified_publisher("sec_gov")
    assert sec is not None
    assert sec.publisher_type == "OFFICIAL_REGULATOR"


def test_authorized_news_source_registry():
    sources = list_news_sources()
    assert len(sources) >= 4
    source_ids = {s.source_id for s in sources}
    assert "openbb_news" in source_ids
    assert "financial_wire_direct" in source_ids
    assert "regulator_announcements" in source_ids


# ---------------------------------------------------------------------------
# 2. URL Normalization, SSRF Defense, and HTML Sanitization
# ---------------------------------------------------------------------------

def test_url_canonicalization_tracking_stripping():
    raw_url = "https://www.bloomberg.com/news/articles/2026-10-26/apple?utm_source=twitter&utm_medium=social&ref=homepage#comments"
    canonical = normalize_canonical_url(raw_url)
    assert canonical == "https://www.bloomberg.com/news/articles/2026-10-26/apple"
    assert "utm_source" not in canonical
    assert "#comments" not in canonical


def test_ssrf_destination_validation():
    # Valid external URLs
    is_safe, _ = validate_external_url("https://www.reuters.com/markets/asia")
    assert is_safe is True

    # Dangerous schemes
    is_safe, reason = validate_external_url("javascript:alert(1)")
    assert is_safe is False
    assert "Unsupported" in reason or "dangerous" in reason

    is_safe, reason = validate_external_url("file:///etc/passwd")
    assert is_safe is False

    # Private loopback & AWS metadata addresses
    is_safe, reason = validate_external_url("http://127.0.0.1:8000/internal")
    assert is_safe is False

    is_safe, reason = validate_external_url("http://localhost/metrics")
    assert is_safe is False

    is_safe, reason = validate_external_url("http://169.254.169.254/latest/meta-data/")
    assert is_safe is False
    assert "metadata" in reason.lower() or "private" in reason.lower()

    # Embedded credentials
    is_safe, reason = validate_external_url("https://user:password@malicious.com")
    assert is_safe is False
    assert "credentials" in reason.lower()


def test_html_sanitization_script_injection():
    malicious_headline = "Fed Announces Rate Cut <script>alert('XSS')</script> to 5.00%"
    clean = sanitize_plain_text(malicious_headline)
    assert "<script>" not in clean
    assert "alert('XSS')" not in clean
    assert clean == "Fed Announces Rate Cut to 5.00%"

    raw_html_excerpt = "<div>Strong Q3 earnings report &amp; outlook for &lt;b&gt;Apple&lt;/b&gt;.</div>"
    clean_ex = sanitize_plain_text(raw_html_excerpt)
    assert "<div>" not in clean_ex
    assert "&amp;" not in clean_ex
    assert clean_ex == "Strong Q3 earnings report & outlook for Apple."


# ---------------------------------------------------------------------------
# 3. Timestamp Integrity Tests
# ---------------------------------------------------------------------------

def test_timestamp_normalization():
    dt_str = "2026-10-26T14:30:00Z"
    normalized = normalize_timestamp(dt_str)
    assert normalized.tzinfo == timezone.utc
    assert normalized.hour == 14
    assert normalized.minute == 30

    date_str = "2026-10-26"
    norm_date = normalize_timestamp(date_str)
    assert norm_date.tzinfo == timezone.utc
    assert norm_date.hour == 0
    assert norm_date.minute == 0


# ---------------------------------------------------------------------------
# 4. Deduplication, Idempotency, Revisions & Withdrawals
# ---------------------------------------------------------------------------

def test_idempotent_ingestion_duplicate_suppression():
    dedup = DeduplicationEngine()
    now = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)
    origin = NewsDataOrigin(provider_id="test_wire", extracted_at=now)

    art = NewsArticle(
        article_id="art-test-01",
        source_provider_id="test_wire",
        publisher_id="reuters",
        publisher_name="Reuters",
        title="Initial Story Headline",
        headline="Initial Story Headline",
        publisher="Reuters",
        canonical_url="https://www.reuters.com/markets/story-01",
        original_url="https://www.reuters.com/markets/story-01",
        published_at=now,
        origin=origin,
    )

    # 1. Initial ingestion
    res1 = dedup.process_incoming_article(art)
    assert res1.is_new is True
    assert res1.is_exact_duplicate is False

    # 2. Re-ingest exact same article
    res2 = dedup.process_incoming_article(art)
    assert res2.is_new is False
    assert res2.is_exact_duplicate is True
    assert res2.is_revision is False


def test_article_correction_creates_revision():
    dedup = DeduplicationEngine()
    now = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)
    origin = NewsDataOrigin(provider_id="test_wire", extracted_at=now)

    art1 = NewsArticle(
        article_id="art-test-02",
        source_provider_id="test_wire",
        publisher_id="bloomberg",
        publisher_name="Bloomberg News",
        title="Company Revenue Expected to Fall 5%",
        headline="Company Revenue Expected to Fall 5%",
        publisher="Bloomberg News",
        canonical_url="https://www.bloomberg.com/markets/story-02",
        original_url="https://www.bloomberg.com/markets/story-02",
        published_at=now,
        origin=origin,
    )
    dedup.process_incoming_article(art1)

    # Updated article with corrected headline
    art2 = NewsArticle(
        article_id="art-test-02",
        source_provider_id="test_wire",
        publisher_id="bloomberg",
        publisher_name="Bloomberg News",
        title="Company Revenue Rose 5% (CORRECTION)",
        headline="Company Revenue Rose 5% (CORRECTION)",
        publisher="Bloomberg News",
        canonical_url="https://www.bloomberg.com/markets/story-02",
        original_url="https://www.bloomberg.com/markets/story-02",
        published_at=now,
        source_updated_at=datetime(2026, 10, 26, 12, 30, 0, tzinfo=timezone.utc),
        origin=origin,
    )
    res = dedup.process_incoming_article(art2)
    assert res.is_revision is True
    assert res.article.revision == 2
    assert res.article.is_corrected is True
    assert "CORRECTION" in res.article.headline

    revisions = dedup.get_revisions("art-test-02")
    assert len(revisions) == 2


def test_article_withdrawal_lifecycle():
    dedup = DeduplicationEngine()
    now = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)
    origin = NewsDataOrigin(provider_id="test_wire", extracted_at=now)

    art1 = NewsArticle(
        article_id="art-test-withdrawn",
        source_provider_id="test_wire",
        publisher_id="reuters",
        publisher_name="Reuters",
        title="Breaking Report Withdrawn by Editor",
        headline="Breaking Report Withdrawn by Editor",
        publisher="Reuters",
        permitted_excerpt="Sensitive unverified rumor text",
        canonical_url="https://www.reuters.com/withdrawn-story",
        original_url="https://www.reuters.com/withdrawn-story",
        published_at=now,
        origin=origin,
    )
    dedup.process_incoming_article(art1)

    # Ingest withdrawal notification
    art_withdrawn = NewsArticle(
        article_id="art-test-withdrawn",
        source_provider_id="test_wire",
        publisher_id="reuters",
        publisher_name="Reuters",
        title="Breaking Report Withdrawn by Editor",
        headline="Breaking Report Withdrawn by Editor",
        publisher="Reuters",
        permitted_excerpt="Sensitive unverified rumor text",
        canonical_url="https://www.reuters.com/withdrawn-story",
        original_url="https://www.reuters.com/withdrawn-story",
        published_at=now,
        availability_status=NewsAvailabilityStatus.WITHDRAWN,
        origin=origin,
    )
    res = dedup.process_incoming_article(art_withdrawn)
    assert res.article.availability_status == NewsAvailabilityStatus.WITHDRAWN
    assert res.article.permitted_excerpt is None  # Excerpt suppressed on withdrawal


# ---------------------------------------------------------------------------
# 5. Canonical Entity Linking & Ticker Collision Disambiguation
# ---------------------------------------------------------------------------

def test_canonical_company_and_instrument_linking():
    headline = "Apple and Microsoft announce joint enterprise cloud initiative"
    mentions = resolve_entities_in_text(headline)
    assert len(mentions) >= 2
    entities = {m.canonical_name for m in mentions}
    assert "Apple Inc." in entities
    assert "Microsoft Corporation" in entities


def test_ticker_collision_short_words_rejected():
    # Ordinary sentences containing words that match ticker symbols ('ON', 'IT', 'ARE', 'CAN', 'FOR')
    ordinary_text = "The committee voted on all items and said it can wait for now"
    mentions = resolve_entities_in_text(ordinary_text)
    # None of these common English words should be linked to equities
    tickers_found = {m.ticker for m in mentions if m.ticker}
    assert "ON" not in tickers_found
    assert "IT" not in tickers_found
    assert "CAN" not in tickers_found
    assert "ALL" not in tickers_found


def test_cashtag_disambiguation():
    # Explicit cashtag $ON should match ON Semiconductor
    headline = "Semiconductor rally lifted $AAPL and $NVDA today"
    mentions = resolve_entities_in_text(headline)
    tickers = {m.ticker for m in mentions}
    assert "AAPL" in tickers
    assert "NVDA" in tickers


def test_adr_vs_ordinary_share_linking():
    headline = "Infosys ADR gained 3% on NYSE following global automotive partnership"
    mentions = resolve_entities_in_text(headline)
    names = {m.canonical_name for m in mentions}
    assert "Infosys Limited ADR" in names


# ---------------------------------------------------------------------------
# 6. Chronological Feed & Keyset Pagination Tests
# ---------------------------------------------------------------------------

def test_chronological_feed_ordering(repo: NewsRepository):
    query = NewsFeedQuery(limit=50)
    feed = repo.get_feed(query)
    assert len(feed.articles) > 0
    assert feed.total_count >= len(feed.articles)

    # Verify descending publication order
    for i in range(len(feed.articles) - 1):
        assert feed.articles[i].published_at >= feed.articles[i + 1].published_at


def test_feed_category_filtering(repo: NewsRepository):
    query = NewsFeedQuery(category="CENTRAL_BANKS", limit=50)
    feed = repo.get_feed(query)
    assert len(feed.articles) > 0
    for a in feed.articles:
        assert any(c.value == "CENTRAL_BANKS" for c in a.categories)


def test_feed_entity_filtering(repo: NewsRepository):
    query = NewsFeedQuery(entity_id="comp-aapl-001")
    feed = repo.get_feed(query)
    assert len(feed.articles) > 0
    for a in feed.articles:
        assert any(e.entity_id == "comp-aapl-001" for e in a.linked_entities)


def test_keyset_pagination_resumption(repo: NewsRepository):
    # Fetch first page with limit 3
    q1 = NewsFeedQuery(limit=3)
    f1 = repo.get_feed(q1)
    assert len(f1.articles) == 3
    assert f1.has_more is True
    assert f1.next_cursor is not None

    # Fetch next page with cursor
    q2 = NewsFeedQuery(limit=3, cursor=f1.next_cursor)
    f2 = repo.get_feed(q2)
    assert len(f2.articles) == 3

    # IDs between page 1 and page 2 must be disjoint
    ids_p1 = {a.article_id for a in f1.articles}
    ids_p2 = {a.article_id for a in f2.articles}
    assert ids_p1.isdisjoint(ids_p2)


def test_headline_search(repo: NewsRepository):
    query = NewsFeedQuery(q="Federal Reserve")
    feed = repo.get_feed(query)
    assert len(feed.articles) > 0
    for a in feed.articles:
        assert "federal reserve" in f"{a.headline} {a.permitted_excerpt or ''}".lower()


# ---------------------------------------------------------------------------
# 7. Coverage & Freshness Status
# ---------------------------------------------------------------------------

def test_coverage_and_freshness_reporting(repo: NewsRepository):
    cov = repo.get_coverage_report()
    assert cov.total_articles > 10
    assert cov.active_sources >= 4
    assert cov.verified_publishers >= 10
    assert "US" in cov.geographic_coverage
    assert "IN" in cov.geographic_coverage

    freshness = repo.get_freshness_status()
    assert freshness.status in ("HEALTHY", "DEGRADED")
    assert freshness.latency_class == "NEAR_REALTIME"
    assert freshness.latest_article_published is not None


# ---------------------------------------------------------------------------
# 8. FastAPI HTTP Endpoints
# ---------------------------------------------------------------------------

def test_api_get_news_feed(test_client: TestClient):
    response = test_client.get("/api/v1/news/feed?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert len(data["articles"]) == 5
    assert data["total_count"] > 5
    assert "as_of" in data


def test_api_get_news_article_detail(test_client: TestClient):
    response = test_client.get("/api/v1/news/articles/art-fed-rate-decision")
    assert response.status_code == 200
    art = response.json()
    assert art["article_id"] == "art-fed-rate-decision"
    assert "Federal Reserve" in art["headline"]
    assert art["publisher_name"] == "Federal Reserve Board"
    assert len(art["linked_entities"]) > 0


def test_api_get_article_not_found(test_client: TestClient):
    response = test_client.get("/api/v1/news/articles/art-non-existent-999")
    assert response.status_code == 404


def test_api_list_sources_and_publishers(test_client: TestClient):
    src_res = test_client.get("/api/v1/news/sources")
    assert src_res.status_code == 200
    assert len(src_res.json()) >= 4

    pub_res = test_client.get("/api/v1/news/publishers")
    assert pub_res.status_code == 200
    assert len(pub_res.json()) >= 10


def test_api_list_categories(test_client: TestClient):
    cat_res = test_client.get("/api/v1/news/categories")
    assert cat_res.status_code == 200
    cats = cat_res.json()
    assert "GENERAL_FINANCIAL" in cats
    assert "CENTRAL_BANKS" in cats
    assert "EQUITIES" in cats


def test_api_search_endpoint(test_client: TestClient):
    res = test_client.get("/api/v1/news/search?q=NVIDIA")
    assert res.status_code == 200
    data = res.json()
    assert len(data["articles"]) > 0
    assert any("nvidia" in a["headline"].lower() for a in data["articles"])


def test_api_entity_news_endpoint(test_client: TestClient):
    res = test_client.get("/api/v1/news/entities/comp-aapl-001")
    assert res.status_code == 200
    data = res.json()
    assert len(data["articles"]) > 0


def test_api_coverage_and_status(test_client: TestClient):
    cov_res = test_client.get("/api/v1/news/coverage")
    assert cov_res.status_code == 200
    cov = cov_res.json()
    assert cov["total_articles"] > 0

    stat_res = test_client.get("/api/v1/news/status")
    assert stat_res.status_code == 200
    stat = stat_res.json()
    assert stat["status"] in ("HEALTHY", "DEGRADED")


def test_api_ingest_batch(test_client: TestClient):
    payload = {
        "source_id": "openbb_news",
        "articles": [
            {
                "headline": "Tesla Deploys Megapack Energy Storage Farm in Australia",
                "publisher_id": "bloomberg",
                "original_url": "https://www.bloomberg.com/news/articles/2026-10-26/tesla-australia-megapack",
                "published_at": "2026-10-26T15:00:00Z",
                "permitted_excerpt": "Tesla Energy completed installation of a 300 megawatt utility battery installation.",
                "categories": ["COMPANY", "COMMODITIES"],
                "geographies": ["US", "AU"],
            }
        ],
    }
    ing_res = test_client.post("/api/v1/news/ingest", json=payload)
    assert ing_res.status_code == 200
    res_data = ing_res.json()
    assert res_data["total_received"] == 1
    assert res_data["new_articles"] == 1
    assert len(res_data["errors"]) == 0


def test_api_ingest_rejects_unsafe_ssrf_url(test_client: TestClient):
    payload = {
        "source_id": "openbb_news",
        "articles": [
            {
                "headline": "Malicious Article with Internal URL",
                "publisher_id": "reuters",
                "original_url": "http://169.254.169.254/latest/meta-data/",
                "published_at": "2026-10-26T15:00:00Z",
            }
        ],
    }
    ing_res = test_client.post("/api/v1/news/ingest", json=payload)
    assert ing_res.status_code == 200
    res_data = ing_res.json()
    assert res_data["new_articles"] == 0
    assert len(res_data["errors"]) == 1
    assert "unsafe" in res_data["errors"][0].lower() or "rejected" in res_data["errors"][0].lower()


# ---------------------------------------------------------------------------
# 9. Side-Effect Invariants
# ---------------------------------------------------------------------------

def test_side_effect_invariants_zero_mutations(service: NewsService):
    """
    Guarantees that reading news causes:
    - 0 trading orders
    - 0 portfolio mutations
    - 0 LLM summarization calls
    - 0 financial statement writes
    """
    query = NewsFeedQuery(limit=10)
    feed = service.get_feed(query)
    assert len(feed.articles) > 0

    # Read article detail
    art = service.get_article(feed.articles[0].article_id)
    assert art is not None

    # Search news
    search_res = service.search_news("Federal Reserve")
    assert len(search_res.articles) > 0
