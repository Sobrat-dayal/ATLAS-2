# ATLAS — Stage 53: Home Personalized Activity

## 1. Overview & Purpose

ATLAS Home Personalized Activity provides an authenticated user with a privacy-conscious, recent interaction timeline to achieve **context-aware workspace continuity**. It allows users to quickly resume recently opened canonical modules and recently selected Universal Entities without navigating menus or executing search queries again.

### Core Architectural Principle
**Personalized Activity is a workspace-continuity feature, not a surveillance or analytics system.**

It exists solely to assist the user in resuming their own analytical and research work. It explicitly excludes:
- Behavioral profiling or engagement scoring
- Employee productivity monitoring or tracking
- Advertising or personalized marketing
- Clickstream analytics, mouse tracking, scroll monitoring, or keystroke logging
- Raw search query storage or natural-language command text retention
- AI/LLM profiling, embeddings, or behavioral prediction
- Third-party tracking SDKs or cross-user activity sharing

---

## 2. Target Architecture

```text
              ATLAS AUTHENTICATED APPSHELL
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
      Module Navigation           Entity Selection
      (Sidebar / QuickLaunch)    (Search / Market Summary)
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
                  Consent Check (Stage 15)
                 home.activity_history_enabled
                           │
                Enabled? ──┴── No ──► No event recorded
                  │
                 Yes
                  │
                  ▼
          Activity Recorder (Client Singleton)
          - Best-effort & nonblocking
          - Stable UUID client_event_id
          - Client debounce (2.5s)
                  │
                  ▼
          FastAPI Activity API
          POST /api/v1/home/activity/events
          - Enforces atlas.access & auth
          - Validates canonical identity
                  │
                  ▼
          UserActivityService
          - Atomic consent checks
          - Idempotency via (user_id, client_event_id)
          - Server-authoritative UTC timestamps
          - Per-user cap enforcement (max 1,000)
                  │
                  ▼
             PostgreSQL
         user_activity_events
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
   Keyset Paginated   Bounded Cleanup
   Recent Read (90d)  (Maintenance CLI)
         │
         ▼
     ATLAS HOME
   HomePersonalizedActivity
         │
         ▼
    Resume Action
    ┌────┴────┐
    ▼         ▼
  Module    Select Entity
  Route     (Stage 25)
```

---

## 3. Privacy & Consent Model

1. **Default State**: Activity history recording is **disabled by default** for all new users (`home.activity_history_enabled = false`). Existing users are never silently opted in.
2. **Explicit Opt-in**: The user must explicitly enable recording via the Home widget or account settings.
3. **Prospective Only**: Enabling recording applies prospectively. No retroactive historical activity is ever manufactured, backfilled, or inferred.
4. **Coordinated Disable & Clear**: When recording is disabled, previously recorded Stage 53 activity rows owned by the user are **atomically purged** from PostgreSQL in the same transaction.
5. **User Clear History**: Users can clear recorded activity at any time without disabling collection. This deletes only Stage 53 activity rows owned by that user, leaving canonical entities, notifications, and settings untouched.
6. **No Offline Backlog**: If recording fails (network error, offline, service outage), events are not queued in browser `localStorage` or `IndexedDB`.
7. **No Public or Shared Feeds**: Activity records are strictly user-scoped and private to the authenticated user.

---

## 4. Supported Event Types & Schemas

Stage 53 supports a deliberately minimal, typed two-event model:

| Event Type | Required Fields | Trigger Boundary | Excluded Behavior |
|---|---|---|---|
| `MODULE_OPENED` | `module_id` | Explicit click in Sidebar, Home Quick Launch, or executed navigation command | No passive render tracking, no prefetch logging, no address bar monitoring |
| `ENTITY_SELECTED` | `entity_id` | Explicit selection in Global Search or Home Market Summary instrument card | No search query text, no price snapshot, no command prompt text |

### PostgreSQL Schema (`user_activity_events`)

| Column | Type | Nullable | Description |
|---|---|---|---|
| `activity_id` | UUID | No | Primary key, generated server-side. |
| `user_id` | UUID | No | Authenticated user UUID derived from JWT `sub`. |
| `event_type` | VARCHAR(32) | No | Strict enum: `MODULE_OPENED` or `ENTITY_SELECTED`. |
| `module_id` | VARCHAR(64) | Yes | Canonical Stage 4 module ID (must be non-null for `MODULE_OPENED`). |
| `entity_id` | UUID | Yes | Universal Entity UUID referencing `entities.entity_id` (ON DELETE SET NULL). |
| `client_event_id` | UUID | No | Client-generated idempotency key. |
| `occurred_at` | TIMESTAMPTZ | No | Server-observed event acceptance time (UTC). |
| `created_at` | TIMESTAMPTZ | No | Database record insertion timestamp (UTC). |

### Database Constraints & Indexes
- **CHECK `ck_user_activity_event_type`**: `event_type IN ('MODULE_OPENED', 'ENTITY_SELECTED')`
- **CHECK `ck_user_activity_payload_consistency`**: `(event_type = 'MODULE_OPENED' AND module_id IS NOT NULL AND entity_id IS NULL) OR (event_type = 'ENTITY_SELECTED' AND entity_id IS NOT NULL)`
- **UNIQUE `uq_user_activity_events_user_client_event`**: `(user_id, client_event_id)` for duplicate retry idempotency.
- **INDEX `ix_user_activity_events_user_occurred_id`**: `(user_id, occurred_at DESC, activity_id DESC)` for high-performance keyset pagination and 90-day retention filtering.
- **INDEX `ix_user_activity_events_occurred_at`**: `(occurred_at)` for batched maintenance cleanup.

---

## 5. Storage Bounds & Retention Policy

- **Retention Cutoff**: Read queries filter out records where `occurred_at < (now - 90 days)`.
- **Per-User Event Cap**: Maximum 1,000 retained activity records per user. When a user exceeds 1,000 records, the oldest records beyond the cap are pruned.
- **Physical Cleanup**: Provided via operator routine `run_activity_retention_cleanup(session, retention_days=90, batch_size=500)` in `atlas.activity.retention`. Deletes expired records in safe batches to avoid blocking PostgreSQL table locks.
- **Inactive Users**: Unpruned records for inactive users are excluded from all read APIs by query predicates and purged during scheduled maintenance runs.

---

## 6. API Specification

All endpoints are mounted under `/api/v1/home/activity`, require authentication via Supabase JWT, and enforce `atlas.access` authorization.

### 1. `GET /api/v1/home/activity`
- **Parameters**: `limit` (int, default 10, max 50), `cursor` (opaque keyset cursor string).
- **Headers**: `Cache-Control: private, no-store`.
- **Behavior**: Returns recent user activity events. Batch resolves referenced entities from `entities` table to prevent N+1 queries. If consent is disabled, returns `enabled: false` and empty items.

### 2. `POST /api/v1/home/activity/events`
- **Payload**: `RecordActivityEventRequest` (`event_type`, `module_id`, `entity_id`, `client_event_id`). Extra fields strictly forbidden (`extra="forbid"`).
- **Behavior**:
  - If consent disabled: Returns `409 Conflict` with `detail: "ACTIVITY_HISTORY_DISABLED"`.
  - If valid: Inserts event with server UTC timestamp and returns `201 Created`.
  - If duplicate `(user_id, client_event_id)` with identical payload: Idempotently returns existing event.
  - If duplicate `(user_id, client_event_id)` with conflicting payload: Returns `409 Conflict`.

### 3. `PUT /api/v1/home/activity/consent`
- **Payload**: `ActivityConsentRequest` (`enabled: bool`).
- **Behavior**: Updates Stage 15 preference `home.activity_history_enabled`. When `enabled=false`, atomically deletes all activity records owned by the user.

### 4. `DELETE /api/v1/home/activity`
- **Behavior**: Securely deletes all Stage 53 activity records owned by the user. Leaves preferences, entities, and settings untouched. Returns `{ "deleted_count": N, "cleared": true }`.

---

## 7. Capture Coverage Matrix

| Interaction Source | Event Recorded | Status |
|---|---|---|
| Sidebar module navigation | `MODULE_OPENED` | Supported & Instrumented |
| Home Quick Launch link | `MODULE_OPENED` | Supported & Instrumented |
| Command Palette executed navigation | `MODULE_OPENED` | Supported & Instrumented |
| Global Search entity selection | `ENTITY_SELECTED` | Supported & Instrumented |
| Home Market Summary instrument click | `ENTITY_SELECTED` + `MODULE_OPENED` | Supported & Instrumented |
| Browser address bar typed URL | None | By design (avoids hydration tracking) |
| Component render / remount | None | Forbidden by design |
| Route prefetch | None | Forbidden by design |
| Market quote WebSocket event | None | Forbidden by design |
| AI interpretation preview | None | Forbidden by design |

---

## 8. Safe Resume Navigation

- **Module Resume**: Reopens the canonical internal route (e.g. `/markets`, `/charts`) via Next.js router. Checks current role permissions at resume time (`canViewModule`). If access has been revoked since the event was recorded, navigation is blocked and a restricted indicator is displayed.
- **Entity Resume**: Selects the canonical UUID via Stage 25 `selectEntity(uuid)` and navigates to the entity workspace if available. Re-evaluates entity permissions. If the entity was deleted or is inaccessible, safely renders "Unavailable Entity" and disables navigation.
- **Strict Boundary**: Resuming interactions never places a financial trade, triggers background Agent execution, launches workflows, or navigates to external URLs.
