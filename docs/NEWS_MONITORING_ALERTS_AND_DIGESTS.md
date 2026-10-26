# Institutional-Grade Personalized Financial News Monitoring, Custom Feeds, Rule-Based Alerts, and News Digests

**ATLAS Platform — Stage 103 of 150**  
**Module:** News (`/news`)  
**Scope:** Personalized News Monitoring, Rule-Based Alerts, Custom Feeds, Scheduled Digests, and Final News Production Hardening  

---

## 1. Executive Summary

Stage 103 concludes the five-stage **Financial News Intelligence** sequence (Stages 99–103) of the ATLAS platform. It delivers an institutional-grade, personalized news monitoring, custom feed, rule-based alert evaluation, and scheduled digest system. 

Built directly on top of the canonical news foundation (Stage 99), source discovery and facets (Stage 100), story clustering and financial events (Stage 101), and target-aware financial sentiment and market reaction analytics (Stage 102), Stage 103 empowers quantitative researchers and institutional analysts to configure precise, user-owned, deterministic news monitoring rules and custom discovery views with zero notification flood vulnerabilities, zero retroactive alert hallucinations, and zero autonomous execution risks.

---

## 2. Core Invariants and Guardrails

1. **Non-Retroactive Preview Invariant:**
   Historical rule validation and preview evaluate candidate rules against bounded historical article/event windows to estimate matching volumes and display sample matches. **Under no circumstances are retroactive alert notifications dispatched** for historical content.
2. **Deterministic Evaluation & Strict Attribution:**
   Rule evaluations are pure, deterministic functions of article metadata, extracted financial entities, verified financial events, and licensed sentiment annotations. Every alert match records verbatim matching condition evidence (`matched_conditions`).
3. **Syndication-Aware Alert Deduplication:**
   Duplicate articles originating from identical syndication networks or identical stories across syndicated wires generate a unified SHA-256 deduplication key. Duplicate occurrences are recorded with status `SUPPRESSED_SYNDICATION` to prevent multi-outlet alert spam.
4. **Rule Cooldown Interval Suppression:**
   Each rule enforces a configurable cooldown window (default: 30 minutes, range: 5–1440 mins). Subsequent matches during active cooldown are recorded with status `SUPPRESSED_COOLDOWN`.
5. **Quiet-Hours Suppression:**
   Rules with quiet-hours enabled suppress instant notification dispatch during specified UTC hours, marking the alert as `SUPPRESSED_QUIET_HOURS` while retaining eligibility for scheduled morning digests.
6. **Durable Notification Integration:**
   When instant dispatch is triggered, the system invokes the Stage 49 durable notification service (`NotificationService.create_notification`) via the standard `/news` route action, preserving unified cross-device notification queues.
7. **Strict Non-Trading Boundary:**
   Zero automated trading, zero buy/sell signals, zero order execution, zero portfolio mutations. The News module is an analytical intelligence platform, strictly separated from capital allocation.

---

## 3. Architecture & Data Models

### 3.1 Monitoring Rule Model (`NewsMonitoringRule`)

A persistent, user-owned entity with optimistic concurrency revision tracking:

```python
@dataclass
class NewsMonitoringRule:
    rule_id: str
    owner_user_id: str
    name: str
    description: Optional[str]
    rule_type: NewsMonitoringRuleType # COMPANY, INSTRUMENT, WATCHLIST, TOPIC, PUBLISHER, EVENT_TYPE, COMPOSITE
    is_active: bool
    target_entity_ids: List[str]
    target_tickers: List[str]
    target_watchlist_id: Optional[str]
    target_topic_ids: List[str]
    target_publisher_ids: List[str]
    target_event_types: List[str]
    sentiment_condition: Optional[NewsSentimentCondition]
    priority: NewsAlertPriority # LOW, MEDIUM, HIGH, CRITICAL
    trigger_policy: NewsTriggerPolicy # ON_NEW_ARTICLE, ON_EVENT_VERIFIED, ON_SENTIMENT_CHANGE, BATCH_HOURLY, SCHEDULED_DIGEST_ONLY
    delivery_channels: List[NewsDeliveryChannel] # IN_APP, DURABLE_NOTIFICATION, EMAIL, DIGEST
    cooldown_minutes: int # e.g. 30
    quiet_hours_enabled: boolean
    quiet_hours_start_utc: Optional[str] # e.g. "22:00"
    quiet_hours_end_utc: Optional[str] # e.g. "06:00"
    rule_revision: int # Incremented on every update
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime]
    total_matches_count: int
```

### 3.2 Target-Aware Sentiment Condition (`NewsSentimentCondition`)

Integrates with Stage 102 polarity isolation to allow filtering rules on specific financial aspects and confidence:

```python
@dataclass
class NewsSentimentCondition:
    sentiment_label: NewsSentimentLabel # POSITIVE, NEGATIVE, NEUTRAL, MIXED
    min_score: Optional[float] # e.g. 0.50
    aspect: Optional[NewsFinancialAspect] # EARNINGS_PERFORMANCE, PROFITABILITY, REGULATORY_EXPOSURE, etc.
    require_high_confidence: bool = False
```

### 3.3 Alert Match Record (`NewsAlertMatch`)

Audit-logged matching record with suppression status and deduplication keys:

```python
@dataclass
class NewsAlertMatch:
    alert_id: str
    rule_id: str
    rule_name: str
    owner_user_id: str
    source_object_type: str # ARTICLE or EVENT
    source_object_id: str
    headline_or_title: str
    publisher_name: Optional[str]
    source_published_at: datetime
    matched_at: datetime
    priority: NewsAlertPriority
    delivery_channels: List[NewsDeliveryChannel]
    match_status: NewsAlertMatchStatus # MATCHED, DISPATCHED, SUPPRESSED_COOLDOWN, SUPPRESSED_SYNDICATION, SUPPRESSED_QUIET_HOURS, DISPATCH_FAILED
    deduplication_key: str # SHA-256 hash of (rule_id, canonical_source_id)
    matched_conditions: List[str] # ["Ticker: AAPL", "Event: DIVIDEND_DECLARATION", "Sentiment: POSITIVE"]
    evidence_summary: Optional[str]
    notification_id: Optional[str]
    error_detail: Optional[str]
    action_url: str # Canonical route e.g. /news?article=...
```

### 3.4 Custom News Feed (`CustomNewsFeed`)

Compiles user search queries into a persistent, reusable feed view:

```python
@dataclass
class CustomNewsFeed:
    feed_id: str
    owner_user_id: str
    title: str
    description: Optional[str]
    query_config: Dict[str, Any] # q, category, tickers, topics, publishers
    is_alert_enabled: bool
    priority: NewsAlertPriority
    created_at: datetime
    updated_at: datetime
    total_matching_articles_cached: Optional[int]
    last_accessed_at: Optional[datetime]
```

### 3.5 Scheduled News Digest (`NewsDigestSubscription` & `NewsDigestRun`)

Enables daily/weekly executive intelligence digests with multi-story grouping:

```python
@dataclass
class NewsDigestSubscription:
    digest_id: str
    owner_user_id: str
    title: str
    cadence: NewsDigestCadence # DAILY, WEEKLY, CUSTOM
    schedule_cron_or_time: str # e.g. "07:00"
    timezone: str # e.g. "America/New_York"
    delivery_channels: List[NewsDeliveryChannel]
    source_rule_ids: List[str]
    custom_feed_ids: List[str]
    top_stories_limit: int # Default: 10
    include_event_highlights: bool
    include_sentiment_summary: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_dispatched_at: Optional[datetime]
    next_scheduled_at: Optional[datetime]
    total_runs_count: int
```

---

## 4. Evaluation Engine State Machine

```
[ Ingested Article or Verified Event ]
                │
                ▼
     [ NewsRuleMatcher Engine ]
                │
         (Evaluate Rules)
                │
         Matches Criteria?
         ├── No  ──► [ No Alert Generated ]
         └── Yes ──► [ Generate Deduplication Key ]
                            │
               Is Syndicated Duplicate?
               ├── Yes ──► Status: SUPPRESSED_SYNDICATION (Audit Logged)
               └── No  ──► Is Cooldown Active?
                               ├── Yes ──► Status: SUPPRESSED_COOLDOWN (Audit Logged)
                               └── No  ──► Are Quiet Hours Active?
                                               ├── Yes ──► Status: SUPPRESSED_QUIET_HOURS (Digest Eligible)
                                               └── No  ──► Status: DISPATCHED
                                                                 │
                                                    Invoke Stage 49 Durable Notification
                                                    (NotificationService.create_notification)
```

---

## 5. REST API Endpoints

All endpoints are mounted under `/api/v1/news` and require authenticated `AuthPrincipal` binding:

### Monitoring Rules & Validation
- `GET    /api/v1/news/monitoring/rules` — List user's active/paused monitoring rules
- `POST   /api/v1/news/monitoring/rules` — Create a new monitoring rule (enforces quota: 50 rules/user)
- `GET    /api/v1/news/monitoring/rules/{rule_id}` — Get single monitoring rule detail
- `PATCH  /api/v1/news/monitoring/rules/{rule_id}` — Update rule configuration (increments `rule_revision`)
- `DELETE /api/v1/news/monitoring/rules/{rule_id}` — Soft/hard delete monitoring rule
- `POST   /api/v1/news/monitoring/rules/validate` — Validate rule parameters with error/warning feedback
- `POST   /api/v1/news/monitoring/rules/preview` — Bounded historical preview without retroactive dispatch
- `GET    /api/v1/news/monitoring/alerts` — List alert matches with filtering (status, priority, rule)
- `GET    /api/v1/news/monitoring/status` — Observability telemetry and pipeline health metrics

### Custom Feeds
- `GET    /api/v1/news/custom-feeds` — List user custom feeds
- `POST   /api/v1/news/custom-feeds` — Create a custom news feed (quota: 25 feeds/user)
- `GET    /api/v1/news/custom-feeds/{feed_id}` — Get custom feed detail
- `PATCH  /api/v1/news/custom-feeds/{feed_id}` — Update custom feed query configuration
- `DELETE /api/v1/news/custom-feeds/{feed_id}` — Delete custom feed
- `GET    /api/v1/news/custom-feeds/{feed_id}/articles` — Execute custom feed query against canonical discovery

### News Digests
- `GET    /api/v1/news/digests` — List user digest subscriptions
- `POST   /api/v1/news/digests` — Create a news digest subscription
- `GET    /api/v1/news/digests/{digest_id}` — Get digest subscription detail
- `PATCH  /api/v1/news/digests/{digest_id}` — Update digest schedule or content parameters
- `DELETE /api/v1/news/digests/{digest_id}` — Delete digest subscription
- `GET    /api/v1/news/digests/{digest_id}/preview` — Preview current digest contents without dispatch
- `POST   /api/v1/news/digests/{digest_id}/trigger` — On-demand manual digest generation and dispatch
- `GET    /api/v1/news/digests/{digest_id}/history` — List past digest execution runs

---

## 6. Frontend Workspace Architecture (`/news`)

The frontend workspace provides an integrated institutional management console under the `[Monitoring & Alerts]` view mode toggle:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [MonitoringHealthBanner]: OPERATIONAL | Engine: v103.0 | Rules: 4 | Latency: 3.2ms     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Sub-Tabs: [Monitoring Rules (4)] [Custom Feeds (2)] [Alert History] [Digests] [Health] │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [ActiveRulesTable]                                                                     │
│ • Rules listing with Active/Paused toggles, priority chips, cooldown tags, actions     │
│ • "New Rule" button opens [RuleBuilderModal] with real-time live validation & preview  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [CustomFeedsPanel]                                                                     │
│ • Left: Custom feed cards with search parameters, alert integration badges             │
│ • Right: One-click live article query execution table with canonical links             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [NewsDigestPanel]                                                                      │
│ • Configured daily/weekly digests with schedule, timezone, and story limits            │
│ • Instant "Preview" modal and "Trigger Now" manual dispatch with run history log       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Verification Summary

### 7.1 Backend Automated Tests
- **Test File:** `apps/api/tests/test_news_monitoring_alerts_v1.py` (14 comprehensive test scenarios)
- **News Regression Suite:** 108 tests passing across all News stages:
  - `test_news_v1.py` (Stage 99)
  - `test_news_discovery_v1.py` (Stage 100)
  - `test_news_story_intelligence_v1.py` (Stage 101)
  - `test_news_sentiment_analytics_v1.py` (Stage 102)
  - `test_news_monitoring_alerts_v1.py` (Stage 103)
- **Linter:** `uv run ruff check` passed with 0 errors.

### 7.2 Frontend Automated Tests
- **Test File:** `apps/web/src/lib/news/__tests__/monitoring_alerts.test.ts` (11 new unit test scenarios)
- **Web Unit Suite:** 66 tests passing with 0 failures across all web test suites.
- **Typecheck:** `cmd /c npx tsc --noEmit` passed with 0 TypeScript errors.
- **Production Build:** `cmd /c pnpm --filter web build` compiled all 38 routes cleanly with zero static generation errors.
