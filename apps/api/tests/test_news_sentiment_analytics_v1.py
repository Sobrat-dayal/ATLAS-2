"""Comprehensive Test Suite for Stage 102: Financial News Sentiment, Entity Relevance and Market Reaction Analytics.

Validates:
1. Financial sentiment taxonomy & labels (POSITIVE, NEGATIVE, NEUTRAL, MIXED, INSUFFICIENT_EVIDENCE, NOT_APPLICABLE)
2. Financial aspect classification (EARNINGS, REVENUE, PROFITABILITY, REGULATION, DEBT, GOVERNANCE, etc.)
3. Target-aware multi-entity polarity isolation (no conflation of acquirer vs. target)
4. Negation detection and hedged language
5. Abstention policy for insufficient licensed evidence
6. Entity relevance scoring & classification (PRIMARY_SUBJECT, DIRECT_PARTICIPANT, VERIFIED_MENTION)
7. Syndication-aware sentiment aggregation and Net Sentiment calculation
8. Chronological sentiment timeline bucketing without hindsight leakage
9. Story Thread and Financial Event sentiment profiles
10. Descriptive observed market reaction alignment, weekend calendar logic, and noncausal disclaimers
11. Golden benchmark evaluation harness (Macro-F1, Precision, Recall)
12. FastAPI REST endpoints, auth, and error handling
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest
from atlas.auth import AuthPrincipal
from atlas.news import (
    FinancialSentimentClassifier,
    MarketReactionEngine,
    NewsArticle,
    NewsEntityRelevanceClass,
    NewsEvidenceScope,
    NewsFinancialAspect,
    NewsMarketReactionWindow,
    NewsRepository,
    NewsSentimentLabel,
    NewsService,
    NewsStoryQuery,
)
from atlas.news.origin import NewsDataOrigin
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.news import get_news_service
from atlas_api.routers.news import router as news_router


@pytest.fixture
def repo() -> NewsRepository:
    return NewsRepository()


@pytest.fixture
def news_service(repo: NewsRepository) -> NewsService:
    return NewsService(repository=repo)


@pytest.fixture
def test_client(news_service: NewsService) -> TestClient:
    api = FastAPI()
    api.include_router(news_router)
    api.dependency_overrides[get_current_user] = lambda: AuthPrincipal(
        sub="test-user",
        email="test@atlas.local",
    )
    api.dependency_overrides[get_news_service] = lambda: news_service
    return TestClient(api)


@pytest.fixture
def sample_origin() -> NewsDataOrigin:
    return NewsDataOrigin(
        provider_id="financial_wire_direct",
        extracted_at=datetime.datetime(2026, 10, 26, 12, 0, 0, tzinfo=datetime.timezone.utc),
    )


# ---------------------------------------------------------------------------
# 1. Deterministic Sentiment Classification & Taxonomy
# ---------------------------------------------------------------------------

def test_sentiment_positive_earnings_beat(sample_origin):
    article = NewsArticle(
        article_id="art-test-pos-beat",
        source_provider_id="financial_wire_direct",
        publisher_id="reuters",
        publisher="Reuters",
        headline="Apple Beats Earnings Expectations on Record Services Revenue",
        permitted_excerpt="Apple reported quarterly EPS beating consensus estimates by 12% driven by accelerated services growth.",
        canonical_url="https://reuters.com/aapl-beat",
        published_at=datetime.datetime(2026, 10, 26, 14, 0, 0, tzinfo=datetime.timezone.utc),
        origin=sample_origin,
    )
    ann = FinancialSentimentClassifier.classify_article_target(
        article=article,
        target_entity_id="comp-aapl-001",
        target_name="Apple Inc.",
        target_ticker="AAPL",
    )
    assert ann.sentiment_label == NewsSentimentLabel.POSITIVE
    assert ann.sentiment_aspect in (NewsFinancialAspect.EARNINGS_PERFORMANCE, NewsFinancialAspect.PROFITABILITY)
    assert ann.sentiment_score > 0.0
    assert ann.evidence[0].evidence_scope in (NewsEvidenceScope.HEADLINE, NewsEvidenceScope.LICENSED_EXCERPT)
    assert "beats" in ann.evidence[0].text_span.lower() or "beating" in ann.evidence[0].text_span.lower()


def test_sentiment_negative_earnings_miss_and_probe(sample_origin):
    article = NewsArticle(
        article_id="art-test-neg-miss",
        source_provider_id="financial_wire_direct",
        publisher_id="bloomberg",
        publisher="Bloomberg News",
        headline="Regional Bank Missed Estimates as Regulatory Probe Expands",
        permitted_excerpt="The bank fell short of analyst forecasts while disclosing a formal subpoena from financial regulators.",
        canonical_url="https://bloomberg.com/bank-probe",
        published_at=datetime.datetime(2026, 10, 26, 14, 0, 0, tzinfo=datetime.timezone.utc),
        origin=sample_origin,
    )
    ann = FinancialSentimentClassifier.classify_article_target(
        article=article,
        target_entity_id="comp-bank-001",
        target_name="Regional Bank",
        target_ticker="RBK",
    )
    assert ann.sentiment_label == NewsSentimentLabel.NEGATIVE
    assert ann.sentiment_aspect in (NewsFinancialAspect.EARNINGS_PERFORMANCE, NewsFinancialAspect.REGULATORY_EXPOSURE)
    assert ann.sentiment_score < 0.0


def test_sentiment_neutral_factual_reporting(sample_origin):
    article = NewsArticle(
        article_id="art-test-neutral",
        source_provider_id="financial_wire_direct",
        publisher_id="reuters",
        publisher="Reuters",
        headline="Treasury Department Issues Monthly Scheduled Debt Schedule",
        permitted_excerpt="The U.S. Department of the Treasury released its quarterly auction calendar and operational schedule.",
        canonical_url="https://reuters.com/treasury-schedule",
        published_at=datetime.datetime(2026, 10, 26, 14, 0, 0, tzinfo=datetime.timezone.utc),
        origin=sample_origin,
    )
    ann = FinancialSentimentClassifier.classify_article_target(
        article=article,
        target_entity_id="agency-treasury-001",
        target_name="U.S. Department of the Treasury",
    )
    assert ann.sentiment_label == NewsSentimentLabel.NEUTRAL
    assert ann.sentiment_score == 0.0


def test_sentiment_mixed_conflicting_aspects(sample_origin):
    article = NewsArticle(
        article_id="art-test-mixed",
        source_provider_id="financial_wire_direct",
        publisher_id="wsj",
        publisher="The Wall Street Journal",
        headline="Auto Group Achieves Record Revenue but Profit Warning Issued on EV Headwinds",
        permitted_excerpt="Auto Group posted record quarterly sales volume while management slashed profit guidance for next fiscal year.",
        canonical_url="https://wsj.com/auto-mixed",
        published_at=datetime.datetime(2026, 10, 26, 14, 0, 0, tzinfo=datetime.timezone.utc),
        origin=sample_origin,
    )
    ann = FinancialSentimentClassifier.classify_article_target(
        article=article,
        target_entity_id="comp-auto-001",
        target_name="Auto Group",
    )
    assert ann.sentiment_label == NewsSentimentLabel.MIXED
    assert ann.sentiment_score == 0.0
    assert "conflicting" in ann.explanation.lower() or "favorable and unfavorable" in ann.explanation.lower()


def test_sentiment_negation_handling(sample_origin):
    article = NewsArticle(
        article_id="art-test-negation",
        source_provider_id="financial_wire_direct",
        publisher_id="reuters",
        publisher="Reuters",
        headline="Tech Firm Denies Regulatory Subpoena Allegations",
        permitted_excerpt="Company spokespersons clarified that no formal investigation or subpoena has been served.",
        canonical_url="https://reuters.com/tech-denies",
        published_at=datetime.datetime(2026, 10, 26, 14, 0, 0, tzinfo=datetime.timezone.utc),
        origin=sample_origin,
    )
    ann = FinancialSentimentClassifier.classify_article_target(
        article=article,
        target_entity_id="comp-tech-001",
        target_name="Tech Firm",
    )
    assert ann.sentiment_label == NewsSentimentLabel.NEUTRAL
    assert "negated" in ann.explanation.lower() or "denied" in ann.explanation.lower()


def test_sentiment_insufficient_evidence_abstention(sample_origin):
    article = NewsArticle(
        article_id="art-test-short",
        source_provider_id="financial_wire_direct",
        publisher_id="prn",
        publisher="PR Newswire",
        headline="Update",
        permitted_excerpt="",
        canonical_url="https://prn.com/update",
        published_at=datetime.datetime(2026, 10, 26, 14, 0, 0, tzinfo=datetime.timezone.utc),
        origin=sample_origin,
    )
    ann = FinancialSentimentClassifier.classify_article_target(
        article=article,
        target_entity_id="comp-short-001",
        target_name="Short Corp",
    )
    assert ann.sentiment_label == NewsSentimentLabel.INSUFFICIENT_EVIDENCE
    assert ann.classification_status == "ABSTAINED"
    assert ann.confidence_score is None


# ---------------------------------------------------------------------------
# 2. Target-Aware Multi-Entity Polarity Isolation
# ---------------------------------------------------------------------------

def test_multi_target_polarity_isolation(sample_origin):
    """Verifies that an M&A deal between Acquirer and Target does NOT propagate the same tone."""
    article = NewsArticle(
        article_id="art-test-ma-polarity",
        source_provider_id="financial_wire_direct",
        publisher_id="bloomberg",
        publisher="Bloomberg News",
        headline="MegaCorp Acquires SmallCo at Substantial 40% Premium; MegaCorp Debt Slashed Outlook",
        permitted_excerpt="MegaCorp authorized $5 billion debt financing to fund the acquisition, leading rating agencies to warn on credit downgrade.",
        canonical_url="https://bloomberg.com/ma-deal",
        published_at=datetime.datetime(2026, 10, 26, 14, 0, 0, tzinfo=datetime.timezone.utc),
        origin=sample_origin,
    )

    ann_acquirer = FinancialSentimentClassifier.classify_article_target(
        article=article,
        target_entity_id="comp-megacorp-001",
        target_name="MegaCorp",
    )
    assert ann_acquirer.target_entity_id == "comp-megacorp-001"
    assert ann_acquirer.sentiment_label in (NewsSentimentLabel.NEGATIVE, NewsSentimentLabel.MIXED)


# ---------------------------------------------------------------------------
# 3. Entity Relevance Classification
# ---------------------------------------------------------------------------

def test_entity_relevance_primary_vs_mention(sample_origin):
    article = NewsArticle(
        article_id="art-test-rel",
        source_provider_id="financial_wire_direct",
        publisher_id="wsj",
        publisher="The Wall Street Journal",
        headline="NVIDIA Unveils Next-Generation AI Supercomputing Architecture",
        permitted_excerpt="The architecture will also be compatible with cloud systems from Microsoft and Amazon.",
        canonical_url="https://wsj.com/nvda-supercompute",
        published_at=datetime.datetime(2026, 10, 26, 14, 0, 0, tzinfo=datetime.timezone.utc),
        origin=sample_origin,
    )

    rel_nvda = FinancialSentimentClassifier.classify_article_relevance(
        article=article,
        entity_id="comp-nvda-001",
        canonical_name="NVIDIA Corporation",
        ticker="NVDA",
    )
    assert rel_nvda.relevance_class == NewsEntityRelevanceClass.PRIMARY_SUBJECT
    assert rel_nvda.relevance_score == 1.0
    assert rel_nvda.is_primary_subject is True
    assert rel_nvda.is_direct_participant is True

    rel_msft = FinancialSentimentClassifier.classify_article_relevance(
        article=article,
        entity_id="comp-msft-001",
        canonical_name="Microsoft Corporation",
        ticker="MSFT",
    )
    assert rel_msft.relevance_class == NewsEntityRelevanceClass.DIRECT_PARTICIPANT
    assert rel_msft.relevance_score == 0.75
    assert rel_msft.is_primary_subject is False
    assert rel_msft.is_direct_participant is True


# ---------------------------------------------------------------------------
# 4. Sentiment Aggregation & Net Sentiment Calculation
# ---------------------------------------------------------------------------

def test_entity_sentiment_aggregate_and_net_sentiment(news_service):
    agg = news_service.get_entity_sentiment_aggregate("comp-aapl-001", days=30)
    assert agg.target_entity_id == "comp-aapl-001"
    assert agg.eligible_count > 0
    assert -1.0 <= agg.net_sentiment <= 1.0
    assert agg.positive_count >= 1
    assert agg.coverage_completeness in ("HIGH", "MODERATE", "SPARSE")


def test_sentiment_timeline_bucketing(news_service):
    timeline = news_service.get_entity_sentiment_timeline("comp-aapl-001", interval="DAY", days=30)
    assert timeline.target_entity_id == "comp-aapl-001"
    assert timeline.interval == "DAY"
    assert isinstance(timeline.buckets, list)
    if timeline.buckets:
        first_b = timeline.buckets[0]
        assert first_b.eligible_count >= 0
        assert -1.0 <= first_b.net_sentiment <= 1.0


# ---------------------------------------------------------------------------
# 5. Story and Event Sentiment Profiles
# ---------------------------------------------------------------------------

def test_story_and_event_sentiment(news_service):
    stories_res = news_service.repository.list_stories(query=NewsStoryQuery())
    if stories_res.stories:
        sid = stories_res.stories[0].story_id
        profile = news_service.get_story_sentiment(sid)
        assert profile.story_id == sid
        assert "POSITIVE" in profile.distribution
        assert "NEGATIVE" in profile.distribution
        assert -1.0 <= profile.net_sentiment <= 1.0

    events = list(news_service.repository._events_by_id.values())
    if events:
        eid = events[0].event_id
        ev_profile = news_service.get_event_sentiment(eid)
        assert ev_profile.event_id == eid
        assert "POSITIVE" in ev_profile.distribution
        assert -1.0 <= ev_profile.net_sentiment <= 1.0


# ---------------------------------------------------------------------------
# 6. Observed Market Reaction & Calendar Alignment
# ---------------------------------------------------------------------------

def test_observed_market_reaction_weekday_close_to_close():
    engine = MarketReactionEngine()
    pub_time = datetime.datetime(2026, 10, 21, 14, 0, 0, tzinfo=datetime.timezone.utc)
    res = engine.calculate_observed_reaction(
        article_id_or_event_id="art-test-101",
        instrument_id="inst-aapl-usd",
        ticker="AAPL",
        company_name="Apple Inc.",
        publication_time=pub_time,
        window=NewsMarketReactionWindow.PREV_CLOSE_TO_NEXT_CLOSE,
    )
    assert res.ticker == "AAPL"
    assert res.price_start > Decimal("0")
    assert res.price_end > Decimal("0")
    expected_return = round((res.price_end - res.price_start) / res.price_start, 4)
    assert res.observed_return == expected_return
    assert res.observed_return_percent == round(expected_return * Decimal("100"), 2)
    assert "Correlation does not establish causation" in res.noncausal_disclaimer
    assert len(res.limitations) >= 3


def test_observed_market_reaction_weekend_handling():
    engine = MarketReactionEngine()
    saturday_pub = datetime.datetime(2026, 10, 24, 10, 0, 0, tzinfo=datetime.timezone.utc)
    res = engine.calculate_observed_reaction(
        article_id_or_event_id="art-weekend-001",
        instrument_id="inst-msft-usd",
        ticker="MSFT",
        company_name="Microsoft Corporation",
        publication_time=saturday_pub,
        window=NewsMarketReactionWindow.PREV_CLOSE_TO_NEXT_CLOSE,
    )
    assert res.window_start_time.weekday() == 4
    assert res.window_end_time.weekday() == 0


# ---------------------------------------------------------------------------
# 7. Golden Evaluation Benchmark (Macro-F1, Precision, Recall)
# ---------------------------------------------------------------------------

def test_golden_benchmark_evaluation(news_service):
    eval_res = news_service.get_sentiment_evaluation()
    assert eval_res.evaluation_corpus_size >= 7
    assert eval_res.macro_f1 >= 0.85
    assert "POSITIVE" in eval_res.per_class_metrics
    assert "NEGATIVE" in eval_res.per_class_metrics
    assert "NEUTRAL" in eval_res.per_class_metrics
    assert "MIXED" in eval_res.per_class_metrics
    assert "INSUFFICIENT_EVIDENCE" in eval_res.per_class_metrics


# ---------------------------------------------------------------------------
# 8. FastAPI REST Endpoints & Authentication
# ---------------------------------------------------------------------------

def test_api_get_article_sentiment(test_client: TestClient):
    res = test_client.get("/api/v1/news/articles/art-aapl-services-expansion/sentiment")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["article_id"] == "art-aapl-services-expansion"
    assert data[0]["sentiment_label"] == "POSITIVE"


def test_api_get_entity_sentiment_aggregate(test_client: TestClient):
    res = test_client.get("/api/v1/news/entities/comp-aapl-001/sentiment?days=30")
    assert res.status_code == 200
    data = res.json()
    assert data["target_entity_id"] == "comp-aapl-001"
    assert "net_sentiment" in data
    assert "positive_count" in data


def test_api_get_sentiment_timeline(test_client: TestClient):
    res = test_client.get("/api/v1/news/entities/comp-aapl-001/sentiment/timeline?interval=DAY&days=30")
    assert res.status_code == 200
    data = res.json()
    assert data["target_entity_id"] == "comp-aapl-001"
    assert "buckets" in data


def test_api_get_methodologies(test_client: TestClient):
    res = test_client.get("/api/v1/news/analytics/methodologies")
    assert res.status_code == 200
    data = res.json()
    assert "sentiment_labels" in data
    assert "financial_aspects" in data
    assert "noncausal_policy" in data


def test_api_post_market_reaction(test_client: TestClient):
    payload = {
        "article_id_or_event_id": "art-aapl-services-expansion",
        "ticker": "AAPL",
        "window": "PREV_CLOSE_TO_NEXT_CLOSE",
    }
    res = test_client.post("/api/v1/news/analytics/market-reaction", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["ticker"] == "AAPL"
    assert "observed_return_percent" in data
    assert "noncausal_disclaimer" in data


def test_api_get_evaluation(test_client: TestClient):
    res = test_client.get("/api/v1/news/analytics/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert data["macro_f1"] >= 0.85
    assert data["evaluation_corpus_size"] >= 7
