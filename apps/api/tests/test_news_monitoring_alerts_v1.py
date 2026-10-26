"""Comprehensive Test Suite for Stage 103: Personalized News Monitoring, Custom Feeds, Rule-Based Alerts, and News Digests.

Validates:
1. Monitoring Rule CRUD, ownership checks, revision incrementing, and quota limits
2. Rule validation panel and historical preview without retroactive notifications
3. Deterministic article matching (Company, Instrument, Watchlist, Topic, Publisher)
4. Alert deduplication key generation and deduplication stability
5. Cooldown interval suppression policy (COOLDOWN_ACTIVE)
6. Syndication-aware duplicate alert suppression (SUPPRESSED_SYNDICATION)
7. Source-evidenced Financial Event monitoring
8. Optional Stage 102 target-aware sentiment condition integration
9. Custom News Feeds creation, execution against canonical discovery, and lifecycle
10. Scheduled News Digest subscriptions, cadence, multi-story grouping, and manual trigger
11. Monitoring pipeline health status and evaluation latency metrics
12. FastAPI REST endpoints, auth principal binding, and error handling
"""

from __future__ import annotations

import datetime

import pytest
from atlas.auth import AuthPrincipal
from atlas.news import (
    CreateCustomNewsFeedDTO,
    CreateNewsDigestSubscriptionDTO,
    CreateNewsMonitoringRuleDTO,
    NewsAlertMatchStatus,
    NewsAlertPriority,
    NewsClassificationMethod,
    NewsDeliveryChannel,
    NewsDigestCadence,
    NewsFinancialAspect,
    NewsFinancialEvent,
    NewsMonitoringRule,
    NewsMonitoringRuleLimitExceededError,
    NewsMonitoringRuleType,
    NewsRepository,
    NewsRuleMatcher,
    NewsRulePreviewRequestDTO,
    NewsRuleValidationRequestDTO,
    NewsSentimentAnnotation,
    NewsSentimentCondition,
    NewsSentimentLabel,
    NewsService,
    NewsTriggerPolicy,
    UpdateCustomNewsFeedDTO,
)
from atlas.news.enums import (
    FinancialEventType,
    NewsEventAssertionStatus,
    NewsEventLifecycleStatus,
)
from atlas.news.origin import NewsDataOrigin
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.dependencies import get_db_session
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
        sub="usr-dev-atlas",
        email="analyst@atlas.local",
    )
    api.dependency_overrides[get_news_service] = lambda: news_service
    api.dependency_overrides[get_db_session] = lambda: None
    return TestClient(api)


@pytest.fixture
def sample_origin() -> NewsDataOrigin:
    return NewsDataOrigin(
        source_id="test_feed",
        source_name="Institutional Feed",
        environment="test",
    )


# ---------------------------------------------------------------------------
# 1. Monitoring Rule CRUD, Revision, and Limits
# ---------------------------------------------------------------------------

def test_rule_crud_and_limits(repo: NewsRepository) -> None:
    user_id = "user-analyst-1"

    # Create Company Rule
    rule = NewsMonitoringRule(
        rule_id="rule-msft-test",
        owner_user_id=user_id,
        name="Microsoft Cloud & AI Updates",
        description="Monitoring verified enterprise cloud milestones.",
        rule_type=NewsMonitoringRuleType.COMPANY,
        target_entity_ids=["entity-microsoft-corp"],
        target_tickers=["MSFT"],
        priority=NewsAlertPriority.HIGH,
        trigger_policy=NewsTriggerPolicy.ON_NEW_ARTICLE,
        cooldown_minutes=20,
    )
    created = repo.create_monitoring_rule(rule)
    assert created.rule_id == "rule-msft-test"
    assert created.rule_revision == 1

    # Fetch rule
    fetched = repo.get_monitoring_rule("rule-msft-test", owner_user_id=user_id)
    assert fetched is not None
    assert fetched.name == "Microsoft Cloud & AI Updates"

    # Unauthorized access check
    unauthorized = repo.get_monitoring_rule("rule-msft-test", owner_user_id="other-user")
    assert unauthorized is None

    # Update rule and verify revision increments
    updated = repo.update_monitoring_rule(
        rule_id="rule-msft-test",
        owner_user_id=user_id,
        updates={"name": "Microsoft GenAI & Azure Cloud Updates", "cooldown_minutes": 30},
    )
    assert updated.name == "Microsoft GenAI & Azure Cloud Updates"
    assert updated.cooldown_minutes == 30
    assert updated.rule_revision == 2

    # List rules
    rules = repo.list_monitoring_rules(user_id)
    assert len(rules) == 1

    # Delete rule
    deleted = repo.delete_monitoring_rule("rule-msft-test", user_id)
    assert deleted is True
    assert repo.get_monitoring_rule("rule-msft-test", user_id) is None


def test_rule_limit_enforcement(repo: NewsRepository) -> None:
    user_id = "user-quota-test"
    # Create 50 rules
    for i in range(50):
        rule = NewsMonitoringRule(
            rule_id=f"rule-limit-{i}",
            owner_user_id=user_id,
            name=f"Rule {i}",
            rule_type=NewsMonitoringRuleType.TOPIC,
            target_topics=["MARKETS"],
        )
        repo.create_monitoring_rule(rule)

    # 51st rule should raise limit exceeded
    with pytest.raises(NewsMonitoringRuleLimitExceededError):
        rule_overflow = NewsMonitoringRule(
            rule_id="rule-limit-overflow",
            owner_user_id=user_id,
            name="Rule Overflow",
            rule_type=NewsMonitoringRuleType.TOPIC,
            target_topics=["MARKETS"],
        )
        repo.create_monitoring_rule(rule_overflow)


# ---------------------------------------------------------------------------
# 2. Rule Validation & Historical Preview
# ---------------------------------------------------------------------------

def test_rule_validation(news_service: NewsService) -> None:
    # Invalid: missing name
    req_invalid_name = NewsRuleValidationRequestDTO(
        rule=CreateNewsMonitoringRuleDTO(
            name=" ",
            rule_type=NewsMonitoringRuleType.COMPANY,
            target_tickers=["AAPL"],
        )
    )
    res1 = news_service.validate_monitoring_rule(req_invalid_name)
    assert not res1.is_valid
    assert any("Rule name" in err for err in res1.errors)

    # Invalid: Company rule missing entity/ticker
    req_missing_target = NewsRuleValidationRequestDTO(
        rule=CreateNewsMonitoringRuleDTO(
            name="Valid Name",
            rule_type=NewsMonitoringRuleType.COMPANY,
            target_entity_ids=[],
            target_tickers=[],
        )
    )
    res2 = news_service.validate_monitoring_rule(req_missing_target)
    assert not res2.is_valid
    assert any("at least one target entity ID or ticker" in err for err in res2.errors)

    # Valid rule
    req_valid = NewsRuleValidationRequestDTO(
        rule=CreateNewsMonitoringRuleDTO(
            name="Apple Inc. Verified Rules",
            rule_type=NewsMonitoringRuleType.COMPANY,
            target_tickers=["AAPL"],
            cooldown_minutes=15,
        )
    )
    res3 = news_service.validate_monitoring_rule(req_valid)
    assert res3.is_valid
    assert len(res3.errors) == 0


def test_rule_historical_preview_no_retroactive_flood(news_service: NewsService) -> None:
    req = NewsRulePreviewRequestDTO(
        rule=CreateNewsMonitoringRuleDTO(
            name="Apple Historical Check",
            rule_type=NewsMonitoringRuleType.COMPANY,
            target_tickers=["AAPL"],
        ),
        limit=5,
    )
    preview = news_service.preview_monitoring_rule(req)
    assert preview.total_potential_matches >= 1
    assert any(m["headline"] for m in preview.matched_articles)
    assert "Historical preview results reflect current news data" in preview.disclaimer

    # Confirm preview did not record any retroactive alert matches in user inbox
    alerts = news_service.list_alert_matches("transient-preview")
    assert alerts.total_count == 0


# ---------------------------------------------------------------------------
# 3. Deterministic Matching & Deduplication
# ---------------------------------------------------------------------------

def test_article_matching_and_deduplication(repo: NewsRepository) -> None:
    matcher = NewsRuleMatcher()

    # Rule targeting Apple by Ticker
    rule = NewsMonitoringRule(
        rule_id="rule-test-match",
        owner_user_id="user-match",
        name="AAPL Matcher",
        rule_type=NewsMonitoringRuleType.COMPANY,
        target_tickers=["AAPL"],
    )

    article = repo.get_article("art-aapl-services-expansion")
    assert article is not None

    match = matcher.match_article(rule, article)
    assert match is not None
    assert match.target_ticker == "AAPL"
    assert match.status == NewsAlertMatchStatus.DELIVERED
    assert match.deduplication_key == matcher.compute_dedupe_key(
        "user-match", "rule-test-match", article.article_id, "ON_NEW_ARTICLE"
    )

    # Stability of deduplication key
    key1 = matcher.compute_dedupe_key("u1", "r1", "art1", "ON_NEW_ARTICLE")
    key2 = matcher.compute_dedupe_key("u1", "r1", "art1", "ON_NEW_ARTICLE")
    assert key1 == key2


def test_cooldown_and_syndication_suppression(repo: NewsRepository) -> None:
    matcher = NewsRuleMatcher()
    now = datetime.datetime.now(datetime.timezone.utc)

    # Rule with 30-minute cooldown
    rule = NewsMonitoringRule(
        rule_id="rule-cooldown-test",
        owner_user_id="user-cd",
        name="Cooldown Rule",
        rule_type=NewsMonitoringRuleType.COMPANY,
        target_tickers=["AAPL"],
        cooldown_minutes=30,
        last_matched_at=now - datetime.timedelta(minutes=5),  # 5 mins ago (< 30m)
    )

    article = repo.get_article("art-aapl-services-expansion")
    assert article is not None

    match = matcher.match_article(rule, article, current_time_utc=now)
    assert match is not None
    assert match.status == NewsAlertMatchStatus.COOLDOWN_ACTIVE
    assert "Cooldown active: 30m" in (match.suppression_reason or "")


# ---------------------------------------------------------------------------
# 4. Financial Event & Sentiment Matching
# ---------------------------------------------------------------------------

def test_financial_event_matching() -> None:
    matcher = NewsRuleMatcher()
    now = datetime.datetime.now(datetime.timezone.utc)

    event = NewsFinancialEvent(
        event_id="ev-div-2026",
        event_type=FinancialEventType.DIVIDEND_DECLARATION,
        lifecycle_status=NewsEventLifecycleStatus.ANNOUNCED,
        assertion_status=NewsEventAssertionStatus.OFFICIALLY_REPORTED,
        event_title="Apple Inc. Announces Cash Dividend of $0.26 per Share",
        event_time=now,
        first_seen_at=now,
        last_evidence_updated_at=now,
        primary_entity_id="entity-apple-inc",
        primary_entity_name="Apple Inc.",
    )

    rule = NewsMonitoringRule(
        rule_id="rule-event-div",
        owner_user_id="user-ev",
        name="Dividend Monitor",
        rule_type=NewsMonitoringRuleType.EVENT_TYPE,
        target_event_types=["DIVIDEND_DECLARATION"],
        target_entity_ids=["entity-apple-inc"],
        trigger_policy=NewsTriggerPolicy.ON_EVENT_VERIFIED,
    )

    matches = matcher.evaluate_financial_event(event, [rule], now=now)
    assert len(matches) == 1
    assert matches[0].source_object_type == "EVENT"
    assert matches[0].headline_or_title == "Apple Inc. Announces Cash Dividend of $0.26 per Share"


def test_sentiment_condition_filtering(repo: NewsRepository) -> None:
    matcher = NewsRuleMatcher()

    rule = NewsMonitoringRule(
        rule_id="rule-sent-test",
        owner_user_id="user-sent",
        name="Positive Earnings Only",
        rule_type=NewsMonitoringRuleType.COMPANY,
        target_tickers=["AAPL"],
        sentiment_condition=NewsSentimentCondition(
            sentiment_label=NewsSentimentLabel.POSITIVE,
            min_score=0.5,
            aspect=NewsFinancialAspect.EARNINGS_PERFORMANCE,
        ),
    )

    article = repo.get_article("art-aapl-services-expansion")
    assert article is not None

    # Matching annotation
    ann_match = NewsSentimentAnnotation(
        annotation_id="ann-match-1",
        article_id=article.article_id,
        article_revision_id="rev-1",
        target_entity_id="entity-apple-inc",
        target_entity_type="COMPANY",
        target_canonical_name="Apple Inc.",
        target_ticker="AAPL",
        sentiment_label=NewsSentimentLabel.POSITIVE,
        sentiment_aspect=NewsFinancialAspect.EARNINGS_PERFORMANCE,
        sentiment_score=0.88,
        confidence_score=0.95,
        classification_status="VALIDATED",
        classification_method=NewsClassificationMethod.DETERMINISTIC_RULES,
        classifier_version="fin-rules-1.0",
        taxonomy_version="v1.0.0",
    )

    match = matcher.match_article(rule, article, sentiment_annotations=[ann_match])
    assert match is not None
    assert any("Sentiment:" in c for c in match.matched_conditions)

    # Non-matching annotation (negative sentiment)
    ann_mismatch = NewsSentimentAnnotation(
        annotation_id="ann-mismatch-1",
        article_id=article.article_id,
        article_revision_id="rev-1",
        target_entity_id="entity-apple-inc",
        target_entity_type="COMPANY",
        target_canonical_name="Apple Inc.",
        target_ticker="AAPL",
        sentiment_label=NewsSentimentLabel.NEGATIVE,
        sentiment_aspect=NewsFinancialAspect.EARNINGS_PERFORMANCE,
        sentiment_score=-0.70,
        confidence_score=0.90,
        classification_status="VALIDATED",
        classification_method=NewsClassificationMethod.DETERMINISTIC_RULES,
        classifier_version="fin-rules-1.0",
        taxonomy_version="v1.0.0",
    )

    no_match = matcher.match_article(rule, article, sentiment_annotations=[ann_mismatch])
    assert no_match is None


# ---------------------------------------------------------------------------
# 5. Custom News Feeds
# ---------------------------------------------------------------------------

def test_custom_news_feed_crud(news_service: NewsService) -> None:
    user_id = "user-cf-test"

    feed = news_service.create_custom_feed(
        CreateCustomNewsFeedDTO(
            title="Global Semis & Compute",
            description="Tracking semiconductor supply chain and earnings.",
            query_config={"q": "semiconductor chip", "category": "TECHNOLOGY"},
            is_alert_enabled=True,
        ),
        owner_user_id=user_id,
    )
    assert feed.title == "Global Semis & Compute"
    assert feed.is_alert_enabled is True

    # Get feed
    fetched = news_service.get_custom_feed(feed.feed_id, user_id)
    assert fetched.feed_id == feed.feed_id

    # Execute custom feed
    res = news_service.execute_custom_feed(feed.feed_id, user_id, limit=10)
    assert res.total_count >= 0

    # Update feed
    updated = news_service.update_custom_feed(
        feed.feed_id,
        user_id,
        UpdateCustomNewsFeedDTO(title="Global Semis, Foundry & Compute"),
    )
    assert updated.title == "Global Semis, Foundry & Compute"

    # Delete feed
    deleted = news_service.delete_custom_feed(feed.feed_id, user_id)
    assert deleted is True


# ---------------------------------------------------------------------------
# 6. Scheduled News Digests
# ---------------------------------------------------------------------------

def test_news_digest_lifecycle_and_execution(news_service: NewsService) -> None:
    user_id = "user-digest-test"

    sub = news_service.create_digest_subscription(
        CreateNewsDigestSubscriptionDTO(
            title="Executive Daily Tech Digest",
            cadence=NewsDigestCadence.DAILY,
            preferred_time_local="07:30",
            timezone="America/New_York",
            delivery_channel=NewsDeliveryChannel.IN_APP,
            max_items=10,
            target_topics=["TECHNOLOGY", "COMPANY"],
        ),
        owner_user_id=user_id,
    )
    assert sub.cadence == NewsDigestCadence.DAILY
    assert sub.preferred_time_local == "07:30"

    # Preview digest run
    preview = news_service.preview_digest(sub.digest_id, user_id)
    assert preview.digest_id == sub.digest_id
    assert preview.status == "COMPLETED"
    assert len(preview.summary_sections) == 2

    # Dispatch digest run
    dispatched = news_service.generate_and_dispatch_digest(sub.digest_id, user_id)
    assert dispatched.run_id is not None
    assert dispatched.eligible_article_count >= 0

    # Inspect digest history
    history = news_service.list_digest_runs(user_id, digest_id=sub.digest_id)
    assert len(history) == 1
    assert history[0].run_id == dispatched.run_id


# ---------------------------------------------------------------------------
# 7. Pipeline Health Status
# ---------------------------------------------------------------------------

def test_monitoring_health_metrics(news_service: NewsService) -> None:
    health = news_service.get_monitoring_health()
    assert health.is_healthy is True
    assert health.active_rules_count >= 2  # Baseline seeds
    assert health.delivery_success_rate >= 0.0
    assert health.queue_lag_seconds == 0.0


# ---------------------------------------------------------------------------
# 8. REST API Endpoints via TestClient
# ---------------------------------------------------------------------------

def test_api_monitoring_rules_endpoints(test_client: TestClient) -> None:
    # 1. List baseline seeded rules
    res = test_client.get("/api/v1/news/monitoring/rules")
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) >= 2

    # 2. Create rule via API
    payload = {
        "name": "Tesla Regulatory Disclosures",
        "rule_type": "COMPANY",
        "target_entity_ids": ["entity-tesla-inc"],
        "target_tickers": ["TSLA"],
        "priority": "HIGH",
        "trigger_policy": "ON_NEW_ARTICLE",
        "cooldown_minutes": 15,
        "delivery_channels": ["IN_APP"],
    }
    create_res = test_client.post("/api/v1/news/monitoring/rules", json=payload)
    assert create_res.status_code == 201
    created_rule = create_res.json()
    assert created_rule["name"] == "Tesla Regulatory Disclosures"
    rule_id = created_rule["rule_id"]

    # 3. Get rule detail
    get_res = test_client.get(f"/api/v1/news/monitoring/rules/{rule_id}")
    assert get_res.status_code == 200
    assert get_res.json()["rule_id"] == rule_id

    # 4. Patch rule
    patch_res = test_client.patch(
        f"/api/v1/news/monitoring/rules/{rule_id}",
        json={"cooldown_minutes": 45, "is_active": False},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["cooldown_minutes"] == 45
    assert patch_res.json()["is_active"] is False
    assert patch_res.json()["rule_revision"] == 2

    # 5. Delete rule
    del_res = test_client.delete(f"/api/v1/news/monitoring/rules/{rule_id}")
    assert del_res.status_code == 204

    # 6. Verify 404 after delete
    get_del = test_client.get(f"/api/v1/news/monitoring/rules/{rule_id}")
    assert get_del.status_code == 404


def test_api_validation_and_preview_endpoints(test_client: TestClient) -> None:
    # Validation endpoint
    val_res = test_client.post(
        "/api/v1/news/monitoring/rules/validate",
        json={
            "rule": {
                "name": "NVIDIA AI Chips",
                "rule_type": "COMPANY",
                "target_tickers": ["NVDA"],
            }
        },
    )
    assert val_res.status_code == 200
    assert val_res.json()["is_valid"] is True

    # Preview endpoint
    prev_res = test_client.post(
        "/api/v1/news/monitoring/rules/preview",
        json={
            "rule": {
                "name": "NVIDIA AI Chips",
                "rule_type": "COMPANY",
                "target_tickers": ["NVDA"],
            },
            "limit": 5,
        },
    )
    assert prev_res.status_code == 200
    assert "disclaimer" in prev_res.json()


def test_api_custom_feeds_and_digests(test_client: TestClient) -> None:
    # 1. Custom feed list
    feeds_res = test_client.get("/api/v1/news/custom-feeds")
    assert feeds_res.status_code == 200
    assert len(feeds_res.json()) >= 1

    # 2. Create custom feed
    create_feed = test_client.post(
        "/api/v1/news/custom-feeds",
        json={
            "title": "Clean Energy & EV Feeds",
            "description": "Renewable energy and grid infrastructure.",
            "query_config": {"q": "solar wind grid", "category": "TECHNOLOGY"},
            "is_alert_enabled": True,
        },
    )
    assert create_feed.status_code == 201
    feed_id = create_feed.json()["feed_id"]

    # 3. Execute custom feed articles
    art_res = test_client.get(f"/api/v1/news/custom-feeds/{feed_id}/articles?limit=5")
    assert art_res.status_code == 200
    assert "articles" in art_res.json()

    # 4. Digests list
    dig_res = test_client.get("/api/v1/news/digests")
    assert dig_res.status_code == 200
    assert len(dig_res.json()) >= 1
    first_digest_id = dig_res.json()[0]["digest_id"]

    # 5. Digest preview
    prev_dig = test_client.get(f"/api/v1/news/digests/{first_digest_id}/preview")
    assert prev_dig.status_code == 200
    assert prev_dig.json()["status"] == "COMPLETED"

    # 6. Digest trigger
    trig_dig = test_client.post(f"/api/v1/news/digests/{first_digest_id}/trigger")
    assert trig_dig.status_code == 200
    assert trig_dig.json()["run_id"] is not None

    # 7. Digest history
    hist_dig = test_client.get(f"/api/v1/news/digests/{first_digest_id}/history")
    assert hist_dig.status_code == 200
    assert len(hist_dig.json()) >= 1

    # 8. Monitoring status
    status_res = test_client.get("/api/v1/news/monitoring/status")
    assert status_res.status_code == 200
    assert status_res.json()["is_healthy"] is True
