# ATLAS — Watchlist Alerts V1 Architecture (Stage 80)

## Executive Summary

Stage 80 delivers **Watchlist Alerts V1**, a production-grade, persistent financial monitoring and alerting subsystem within the `/watchlists` module of ATLAS. It enables authenticated users to establish stateful monitoring rules on financial instruments and receive verified notifications when authoritative, entitled market observations satisfy those conditions.

Crucially, **ATLAS Alerts are evaluated server-side by an authorized background process** using genuine, qualified market events from the Stage 42 Market Event Pipeline and Stage 41 Quote Ingestion engine. Evaluation continues regardless of whether the user has the browser open, subject to feed entitlements and backend operational availability.

---

## 1. Core Architectural Invariants

1. **Not a Trading Instruction:** An alert signifies that a verified financial condition occurred. It does not place orders, initiate paper trades, rebalance portfolios, or trigger autonomous trading agents.
2. **Never Fabricate Market Prices:** Conditions are evaluated exclusively against genuine, qualified canonical quotes.
3. **No False First-Snapshot Crossings:** When an alert is created or armed, if the current market price is already across the threshold, it seeds the initial baseline without triggering an artificial crossing event.
4. **Transition-Required Crossing:** Repeat crossing triggers require the price to return to the opposite side of the threshold before crossing again.
5. **Decimal-Safe Comparisons:** All numerical evaluations use exact `Decimal` arithmetic to eliminate floating-point rounding errors.
6. **No Shared Upstream Connections per Alert:** Alerts on the same financial series multiplex over the existing canonical market-data ingestion pipeline.
7. **Durable Notification Delivery:** Evaluated triggers are atomically persisted alongside a transactional notification outbox record, delivered to the Stage 49 Notification Center with deduplication guarantees.

---

## 2. Domain Data Model & Persistence

Alert definitions, evaluation states, trigger audit logs, and notification outbox items are persisted in PostgreSQL via Alembic migration `stage80_watchlist_alerts`.

### 2.1 Table Schemas

```sql
-- Alert Rule Definitions
CREATE TABLE watchlist_alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id UUID NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    watchlist_item_id UUID NOT NULL REFERENCES watchlist_items(id) ON DELETE CASCADE,
    instrument_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE RESTRICT,
    market_series_identity VARCHAR(128) NOT NULL,
    symbol VARCHAR(32) NOT NULL,
    rule_type VARCHAR(32) NOT NULL,
    rule_version INTEGER NOT NULL DEFAULT 1,
    quote_measure VARCHAR(32) NOT NULL DEFAULT 'LAST',
    comparison_operator VARCHAR(32) NOT NULL,
    threshold_decimal NUMERIC(28, 10) NOT NULL,
    threshold_unit VARCHAR(16) NOT NULL DEFAULT 'USD',
    reference_methodology VARCHAR(32),
    recurrence_policy VARCHAR(16) NOT NULL DEFAULT 'RECURRING',
    cooldown_seconds INTEGER NOT NULL DEFAULT 300,
    expires_at TIMESTAMPTZ,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    state VARCHAR(16) NOT NULL DEFAULT 'ENABLED',
    revision INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Durable Evaluation State (Indexed for Multi-Worker Event Engine)
CREATE TABLE watchlist_alert_evaluation_state (
    alert_id UUID PRIMARY KEY REFERENCES watchlist_alert_rules(id) ON DELETE CASCADE,
    rule_revision INTEGER NOT NULL DEFAULT 1,
    evaluation_status VARCHAR(32) NOT NULL DEFAULT 'WAITING_FOR_BASELINE',
    baseline_established BOOLEAN NOT NULL DEFAULT FALSE,
    armed_side VARCHAR(16),
    last_qualified_value NUMERIC(28, 10),
    last_qualified_observation_time TIMESTAMPTZ,
    last_qualified_observation_identity VARCHAR(128),
    last_trigger_at TIMESTAMPTZ,
    cooldown_until TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Immutable Trigger Audit Log
CREATE TABLE watchlist_alert_triggers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID NOT NULL REFERENCES watchlist_alert_rules(id) ON DELETE CASCADE,
    rule_revision INTEGER NOT NULL,
    owner_user_id UUID NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
    watchlist_id UUID NOT NULL,
    watchlist_item_id UUID NOT NULL,
    instrument_entity_id UUID NOT NULL,
    market_series_identity VARCHAR(128) NOT NULL,
    symbol VARCHAR(32) NOT NULL,
    event_identity VARCHAR(128) NOT NULL,
    observation_value NUMERIC(28, 10) NOT NULL,
    threshold_value NUMERIC(28, 10) NOT NULL,
    quote_measure VARCHAR(32) NOT NULL,
    rule_type VARCHAR(32) NOT NULL,
    source VARCHAR(64) NOT NULL,
    venue VARCHAR(32),
    observation_time TIMESTAMPTZ NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trigger_dedup_key VARCHAR(256) NOT NULL UNIQUE,
    notification_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Transactional Notification Outbox
CREATE TABLE watchlist_alert_notification_outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_id UUID NOT NULL REFERENCES watchlist_alert_triggers(id) ON DELETE CASCADE,
    owner_user_id UUID NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
    alert_id UUID NOT NULL REFERENCES watchlist_alert_rules(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    payload JSONB NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Financial Condition Semantics

### 3.1 Supported Rule Types

| Rule Type | Mathematical Condition | Semantics |
|---|---|---|
| `PRICE_ABOVE` | $P_t > T$ | State alert; triggers if price is strictly above threshold. |
| `PRICE_BELOW` | $P_t < T$ | State alert; triggers if price is strictly below threshold. |
| `CROSSING_ABOVE` | $P_{t-1} \le T \land P_t > T$ | Transition alert; requires verified transition from $\le T$ to $> T$. |
| `CROSSING_BELOW` | $P_{t-1} \ge T \land P_t < T$ | Transition alert; requires verified transition from $\ge T$ to $< T$. |
| `PERCENTAGE_CHANGE_ABOVE` | $\%\Delta_{t-1} \le T \land \%\Delta_t > T$ | Transition alert over qualified decimal percentage change. |
| `PERCENTAGE_CHANGE_BELOW` | $\%\Delta_{t-1} \ge T \land \%\Delta_t < T$ | Transition alert over qualified decimal percentage change. |

### 3.2 Baseline Seeding & Equality Rules

- **First Snapshot Invariant:** When an alert is created or resumed, `baseline_established` is initialized to `False`. The very first market observation sets `baseline_established = True` and records `armed_side` without triggering.
- **Strict Transition Invariant:** A crossing alert cannot trigger consecutively without observing price on the opposite side of the threshold.
- **Re-Arming:** For recurring alerts, after firing, the rule automatically re-arms once price returns to or across the threshold and cooldown has elapsed.

### 3.3 Percentage-Change Calculation & Reference Methodologies

Formula:
$$\%\Delta = \frac{P_t - P_{\text{ref}}}{|P_{\text{ref}}|} \times 100$$

- **Zero-Denominator Rejection:** If $P_{\text{ref}} = 0$ or is missing, percentage-change alerts return `triggered = False` with `reason = "INVALID_REFERENCE_PRICE_ZERO"`. Never emits `NaN` or `Infinity`.
- **Supported Reference Methodologies:**
  1. `SESSION_PREVIOUS_CLOSE`: Official session close for equities and ETFs.
  2. `ROLLING_24H`: 24-hour rolling price benchmark for continuous cryptocurrency markets.
  3. `PREVIOUS_NAV`: Official previous net asset value for mutual funds.

---

## 4. Quote Measures & Asset Class Compatibility

Alerts require an explicit, qualified quote measure compatible with the target instrument's asset class:

| Asset Class | Supported Quote Measures | Default |
|---|---|---|
| `equity` | `LAST`, `BID`, `ASK`, `MID`, `OPEN`, `HIGH`, `LOW`, `CLOSE` | `LAST` |
| `etf` | `LAST`, `BID`, `ASK`, `MID`, `OPEN`, `HIGH`, `LOW`, `CLOSE`, `NAV` | `LAST` |
| `crypto` | `LAST`, `BID`, `ASK`, `MID`, `OPEN`, `HIGH`, `LOW`, `CLOSE` | `LAST` |
| `fx` | `BID`, `ASK`, `MID` | `MID` |
| `futures` | `LAST`, `BID`, `ASK`, `MID`, `OPEN`, `HIGH`, `LOW`, `CLOSE` | `LAST` |
| `bond` | `LAST`, `BID`, `ASK`, `MID`, `YIELD`, `CLOSE` | `YIELD` |
| `mutual_fund` | `NAV`, `CLOSE` | `NAV` |

---

## 5. Event-Driven Evaluation Pipeline

```
  ATLAS Market Data Ingestion (Stage 41)
                  │
                  ▼
   Market Event Pipeline (Stage 42)
  [Event: market.quote.updated]
                  │
                  ▼
       AlertEvaluationEngine
  (Validates Freshness: Age ≤ 300s)
                  │
                  ▼
  Indexed Active Rule Retrieval
  (By market_series_identity & measure)
                  │
                  ▼
   Decimal-Safe Condition Evaluation
  (evaluate_alert_condition)
                  │
     ┌────────────┴────────────┐
     ▼                         ▼
No Trigger                 Triggered!
(Update armed_side)        (Generate trigger_dedup_key)
                               │
                               ▼
               Atomic Database Transaction
               ├── INSERT watchlist_alert_triggers
               ├── UPDATE watchlist_alert_evaluation_state
               ├── UPDATE watchlist_alert_rules (if ONE_SHOT)
               └── INSERT watchlist_alert_notification_outbox
                               │
                               ▼
               AlertNotificationDispatcher
               (Delivers to Stage 49 Notification Center)
```

### 5.1 Freshness & Staleness Rules
- Realtime observations older than 300 seconds are rejected with a log warning to prevent stale movements from triggering false alerts.
- Delayed feeds are honored when authorized, and the notification explicitly includes `[Delayed]` provenance disclosure.

### 5.2 Deduplication & Concurrency Protection
- **Trigger Uniqueness:** Enforced by PostgreSQL unique index on `trigger_dedup_key`:
  `trig:{rule.id}:{rule.revision}:{event_id}:{observation_time}`
- **Multi-Worker Safety:** Multiple evaluation workers can consume market events concurrently; duplicate evaluations fail gracefully on database constraint collision with automatic transaction rollback.
- **Optimistic Concurrency:** Rule updates require matching `expected_revision` to prevent concurrent edits from silently overwriting rule state.

---

## 6. Durable Notification Delivery (Stage 49 Integration)

- Evaluated triggers enqueue a pending item into `watchlist_alert_notification_outbox`.
- `AlertNotificationDispatcher` polls pending outbox entries with bounded batching.
- Constructs formatted financial notifications conforming to Stage 49 `CreateNotification`:
  - `category`: `NotificationCategory.MARKET`
  - `producer_key`: `"alerts.watchlist_evaluator"`
  - `dedupe_key`: `"alert_trigger:{trigger_id}"`
  - `action_kind`: `NotificationActionKind.INTERNAL_ROUTE`
  - `action_route`: `"/watchlists"`
- Atomically transitions outbox records to `DELIVERED` upon acknowledgment.

---

## 7. Resource Quotas & Operational Limits

- **Active Alerts per User:** Maximum 100 active alerts (`MAX_ACTIVE_ALERTS_PER_USER`).
- **Active Alerts per Instrument:** Maximum 20 active alerts per instrument per user (`MAX_ALERTS_PER_INSTRUMENT`).
- **Cooldown Presets:** 0s (None), 60s (1m), 300s (5m), 900s (15m), 3600s (1h), 86400s (1d).
- **Trigger History Page Size:** Default 50, maximum 100 per page.

---

## 8. Lifecycle Hooks & Cascade Handling

- **Watchlist Item Removed:** Disables associated active alerts atomically and updates rule revision; trigger history is preserved.
- **Watchlist Deleted:** Disables all associated active alerts atomically; historical trigger records are preserved.

---

## 9. REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/watchlists/alert-capabilities` | Supported rule types, measures, quotas, and cooldowns. |
| `GET` | `/api/v1/watchlists/alert-health` | Operational health and active indexed series count. |
| `GET` | `/api/v1/watchlists/{watchlist_id}/alerts` | List alert rules with pagination and state filtering. |
| `POST` | `/api/v1/watchlists/{watchlist_id}/alerts` | Create and arm a new alert rule. |
| `GET` | `/api/v1/watchlists/{watchlist_id}/alerts/{alert_id}` | Retrieve alert rule definition and evaluation state. |
| `PATCH` | `/api/v1/watchlists/{watchlist_id}/alerts/{alert_id}` | Update alert rule with optimistic revision check. |
| `DELETE` | `/api/v1/watchlists/{watchlist_id}/alerts/{alert_id}` | Soft-delete alert rule and terminate monitoring. |
| `POST` | `/api/v1/watchlists/{watchlist_id}/alerts/{alert_id}/pause` | Pause alert evaluation. |
| `POST` | `/api/v1/watchlists/{watchlist_id}/alerts/{alert_id}/resume` | Resume alert evaluation (re-baselines crossing). |
| `GET` | `/api/v1/watchlists/{watchlist_id}/alerts/{alert_id}/history` | Paginated trigger audit log for an alert. |

---

## 10. Frontend User Interface

Integrated directly into `/watchlists`:
- **Row Alert Indicators (`AlertBadge`):** Shows a subtle badge with the `Bell` icon and active alert count next to the instrument symbol.
- **Row Action Button:** Quick-action `Bell` button in `WatchlistRowActions` to configure an alert directly for that row's instrument.
- **Create Alert Dialog (`CreateAlertDialog`):** Terminal-density dialog with measure selection, condition type, threshold validation, recurrence, cooldown options, and live quote snapshot preview.
- **Edit Alert Dialog (`EditAlertDialog`):** Allows updating threshold, measure, and cooldown with baseline reset disclosure.
- **Delete Confirmation (`DeleteAlertDialog`):** Explicit modal confirmation before removing rules.
- **Trigger History Dialog (`AlertHistoryDialog`):** Audit table displaying trigger time, market observation time, observed value, threshold, source venue, and delivery status.
- **Watchlist Alerts Panel (`WatchlistAlertsPanel`):** Collapsible bottom workspace panel with tabs for Active, Paused, and All alerts, live evaluator health badge, and quick creation button.
