import test from "node:test";
import assert from "node:assert/strict";

import {
  NewsMonitoringRuleType,
  NewsAlertPriority,
  NewsTriggerPolicy,
  NewsDeliveryChannel,
  NewsAlertMatchStatus,
  NewsDigestCadence,
  NewsMonitoringRuleDTO,
  CreateNewsMonitoringRuleDTO,
  NewsRuleValidationResponseDTO,
  NewsRulePreviewResponseDTO,
  NewsAlertMatchDTO,
  NewsAlertFeedResponseDTO,
  CustomNewsFeedDTO,
  CreateCustomNewsFeedDTO,
  NewsDigestSubscriptionDTO,
  NewsDigestRunDTO,
  MonitoringHealthStatusDTO,
} from "../types";

test("Stage 103: NewsMonitoringRuleType covers all institutional target scopes", () => {
  const ruleTypes: NewsMonitoringRuleType[] = [
    "COMPANY",
    "INSTRUMENT",
    "WATCHLIST",
    "TOPIC",
    "PUBLISHER",
    "EVENT_TYPE",
    "COMPOSITE",
  ];
  assert.equal(ruleTypes.length, 7);
  assert.ok(ruleTypes.includes("COMPANY"));
  assert.ok(ruleTypes.includes("EVENT_TYPE"));
  assert.ok(ruleTypes.includes("COMPOSITE"));
});

test("Stage 103: NewsAlertPriority specifies four institutional severity tiers", () => {
  const priorities: NewsAlertPriority[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
  assert.equal(priorities.length, 4);
  assert.ok(priorities.includes("CRITICAL"));
  assert.ok(priorities.includes("HIGH"));
});

test("Stage 103: NewsTriggerPolicy supports synchronous and batched evaluation policies", () => {
  const policies: NewsTriggerPolicy[] = [
    "ON_NEW_ARTICLE",
    "ON_EVENT_VERIFIED",
    "ON_SENTIMENT_CHANGE",
    "BATCH_HOURLY",
    "SCHEDULED_DIGEST_ONLY",
  ];
  assert.equal(policies.length, 5);
  assert.ok(policies.includes("ON_NEW_ARTICLE"));
  assert.ok(policies.includes("ON_EVENT_VERIFIED"));
  assert.ok(policies.includes("SCHEDULED_DIGEST_ONLY"));
});

test("Stage 103: NewsDeliveryChannel covers in-app, durable notifications, email, and digests", () => {
  const channels: NewsDeliveryChannel[] = [
    "IN_APP",
    "DURABLE_NOTIFICATION",
    "EMAIL",
    "DIGEST",
  ];
  assert.equal(channels.length, 4);
  assert.ok(channels.includes("DURABLE_NOTIFICATION"));
  assert.ok(channels.includes("DIGEST"));
});

test("Stage 103: NewsAlertMatchStatus tracks dispatch and suppression reasons", () => {
  const statuses: NewsAlertMatchStatus[] = [
    "MATCHED",
    "DISPATCHED",
    "SUPPRESSED_COOLDOWN",
    "SUPPRESSED_SYNDICATION",
    "SUPPRESSED_QUIET_HOURS",
    "SUPPRESSED_MUTED",
    "DISPATCH_FAILED",
  ];
  assert.equal(statuses.length, 7);
  assert.ok(statuses.includes("SUPPRESSED_COOLDOWN"));
  assert.ok(statuses.includes("SUPPRESSED_SYNDICATION"));
  assert.ok(statuses.includes("SUPPRESSED_QUIET_HOURS"));
});

test("Stage 103: NewsMonitoringRuleDTO contract validation with sentiment condition", () => {
  const rule: NewsMonitoringRuleDTO = {
    rule_id: "rule-nvda-ai",
    owner_user_id: "usr-dev-atlas",
    name: "NVIDIA AI & Data Center Alerts",
    description: "Tracks generative compute announcements and earnings beats.",
    rule_type: "COMPANY",
    is_active: true,
    target_entity_ids: ["entity-nvidia-corp"],
    target_tickers: ["NVDA"],
    target_watchlist_id: null,
    target_topic_ids: ["artificial-intelligence", "semiconductors"],
    target_publisher_ids: ["reuters", "bloomberg_wire"],
    target_event_types: ["EARNINGS_RELEASE"],
    sentiment_condition: {
      sentiment_label: "POSITIVE",
      min_score: 0.6,
      aspect: "EARNINGS_PERFORMANCE",
      require_high_confidence: true,
    },
    priority: "HIGH",
    trigger_policy: "ON_NEW_ARTICLE",
    delivery_channels: ["IN_APP", "DURABLE_NOTIFICATION"],
    cooldown_minutes: 30,
    quiet_hours_enabled: true,
    quiet_hours_start_utc: "22:00",
    quiet_hours_end_utc: "06:00",
    rule_revision: 2,
    created_at: "2026-10-26T12:00:00Z",
    updated_at: "2026-10-26T12:30:00Z",
    last_triggered_at: "2026-10-26T13:00:00Z",
    total_matches_count: 5,
  };

  assert.equal(rule.rule_id, "rule-nvda-ai");
  assert.equal(rule.rule_revision, 2);
  assert.equal(rule.sentiment_condition?.sentiment_label, "POSITIVE");
  assert.equal(rule.cooldown_minutes, 30);
  assert.ok(rule.delivery_channels.includes("DURABLE_NOTIFICATION"));
});

test("Stage 103: NewsRuleValidationResponseDTO and NewsRulePreviewResponseDTO contracts", () => {
  const validation: NewsRuleValidationResponseDTO = {
    is_valid: true,
    validation_errors: [],
    validation_warnings: ["Rule has broad keywords; consider adding a target ticker."],
    normalized_summary: "COMPANY rule targeting $AAPL with HIGH priority",
    rule_id: null,
  };
  assert.ok(validation.is_valid);
  assert.equal(validation.validation_errors.length, 0);

  const preview: NewsRulePreviewResponseDTO = {
    preview_sample_articles: [],
    preview_sample_events: [],
    estimated_matching_volume_per_week: 14,
    is_rule_valid: true,
    warnings: [],
    disclaimer:
      "Historical rule preview is bounded and non-retroactive; no retroactive alert notifications are generated.",
  };
  assert.ok(preview.is_rule_valid);
  assert.equal(preview.estimated_matching_volume_per_week, 14);
  assert.ok(preview.disclaimer.includes("non-retroactive"));
});

test("Stage 103: NewsAlertMatchDTO enforces deduplication key and evidence conditions", () => {
  const alert: NewsAlertMatchDTO = {
    alert_id: "alt-2026-001",
    rule_id: "rule-nvda-ai",
    rule_name: "NVIDIA AI & Data Center Alerts",
    owner_user_id: "usr-dev-atlas",
    source_object_type: "ARTICLE",
    source_object_id: "art-nvda-blackwell-2026",
    headline_or_title: "NVIDIA Announces Next-Gen Ultra AI Systems",
    publisher_name: "Reuters",
    source_published_at: "2026-10-26T14:00:00Z",
    matched_at: "2026-10-26T14:00:05Z",
    priority: "HIGH",
    delivery_channels: ["IN_APP", "DURABLE_NOTIFICATION"],
    match_status: "DISPATCHED",
    deduplication_key: "dedup-sha256-nvda-rule-art",
    matched_conditions: ["Ticker: NVDA", "Topic: artificial-intelligence", "Sentiment: POSITIVE (0.85)"],
    evidence_summary: "Explicitly matches verified ticker NVDA and positive earnings performance.",
    notification_id: "notif-stage49-001",
    error_detail: null,
    action_url: "/news?article=art-nvda-blackwell-2026",
  };

  assert.equal(alert.alert_id, "alt-2026-001");
  assert.equal(alert.match_status, "DISPATCHED");
  assert.equal(alert.matched_conditions.length, 3);
  assert.ok(alert.action_url.startsWith("/news"));
});

test("Stage 103: CustomNewsFeedDTO compiles query configuration into canonical discovery", () => {
  const feed: CustomNewsFeedDTO = {
    feed_id: "cf-semis-global",
    owner_user_id: "usr-dev-atlas",
    title: "Global Semiconductor Supply Chain",
    description: "Tracks foundries, lithography, and memory supply.",
    query_config: {
      q: "semiconductor lithography foundry",
      category: "TECHNOLOGY",
      countries: ["US", "TW", "NL"],
    },
    is_alert_enabled: true,
    priority: "HIGH",
    created_at: "2026-10-26T10:00:00Z",
    updated_at: "2026-10-26T10:00:00Z",
    total_matching_articles_cached: 42,
    last_accessed_at: "2026-10-26T15:00:00Z",
  };

  assert.equal(feed.feed_id, "cf-semis-global");
  assert.ok(feed.is_alert_enabled);
  assert.equal(feed.total_matching_articles_cached, 42);
  const qConfig = feed.query_config as Record<string, unknown>;
  assert.equal(qConfig.category, "TECHNOLOGY");
});

test("Stage 103: NewsDigestSubscriptionDTO and NewsDigestRunDTO enforce idempotent execution", () => {
  const digest: NewsDigestSubscriptionDTO = {
    digest_id: "dig-morning-briefing",
    owner_user_id: "usr-dev-atlas",
    title: "Executive Morning Intelligence Digest",
    cadence: "DAILY",
    schedule_cron_or_time: "07:00",
    timezone: "America/New_York",
    delivery_channels: ["IN_APP", "DURABLE_NOTIFICATION", "EMAIL"],
    source_rule_ids: ["rule-nvda-ai", "rule-msft-test"],
    custom_feed_ids: ["cf-semis-global"],
    top_stories_limit: 10,
    include_event_highlights: true,
    include_sentiment_summary: true,
    is_active: true,
    created_at: "2026-10-26T08:00:00Z",
    updated_at: "2026-10-26T08:00:00Z",
    last_dispatched_at: "2026-10-26T11:00:00Z",
    next_scheduled_at: "2026-10-27T11:00:00Z",
    total_runs_count: 14,
  };

  assert.equal(digest.cadence, "DAILY");
  assert.equal(digest.top_stories_limit, 10);
  assert.ok(digest.include_event_highlights);
  assert.ok(digest.include_sentiment_summary);

  const run: NewsDigestRunDTO = {
    run_id: "run-2026-10-26-001",
    digest_id: "dig-morning-briefing",
    owner_user_id: "usr-dev-atlas",
    cadence: "DAILY",
    started_at: "2026-10-26T11:00:00Z",
    completed_at: "2026-10-26T11:00:02Z",
    status: "DISPATCHED",
    total_articles_included: 8,
    top_stories_included: [{ story_id: "st-apple-services", title: "Apple Expands Services" }],
    event_highlights: [{ event_id: "ev-div-2026", title: "Apple Cash Dividend Declaration" }],
    delivery_channels: ["IN_APP", "DURABLE_NOTIFICATION"],
    notification_id: "notif-digest-2026-001",
    error_message: null,
    idempotency_token: "idemp-digest-dig-morning-briefing-20261026",
  };

  assert.equal(run.status, "DISPATCHED");
  assert.equal(run.total_articles_included, 8);
  assert.ok(run.idempotency_token.startsWith("idemp-digest-"));
});

test("Stage 103: MonitoringHealthStatusDTO tracks observability and evaluation latency", () => {
  const health: MonitoringHealthStatusDTO = {
    is_healthy: true,
    active_rules_count: 8,
    active_custom_feeds_count: 4,
    active_digests_count: 2,
    alerts_last_24h: 35,
    deduplicated_last_24h: 12,
    average_eval_latency_ms: 3.45,
    last_evaluation_timestamp: "2026-10-26T15:30:00Z",
    engine_version: "v103.0-institutional",
    watermark_timestamp: "2026-10-26T15:29:55Z",
  };

  assert.ok(health.is_healthy);
  assert.equal(health.active_rules_count, 8);
  assert.equal(health.engine_version, "v103.0-institutional");
  assert.ok(health.average_eval_latency_ms < 5.0);
});
