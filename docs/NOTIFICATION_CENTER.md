# Stage 49: Persistent Notification Center

## 1. Overview & Architecture

The **ATLAS Persistent Notification Center** provides a durable, secure, user-scoped in-app notification subsystem. Backend ATLAS services generate messages persisted in PostgreSQL, while the persistent AppShell presents unread indicators and a slide-over/popover Notification Center with keyset pagination and optimistic interaction.

```text
ATLAS backend producer
        │
        ▼
NotificationService
        │
        ▼
PostgreSQL (Authoritative Durable Storage)
        │
        ├──────────────────────┐
        │                      │
        ▼                      ▼
Notification List        Unread Count
        │                      │
        └──────────┬───────────┘
                   ▼
            FastAPI Endpoints
                   │
                   ▼
         Frontend API Client / State Hook
                   │
                   ▼
         Persistent TopBar AppShell
                   │
                   ▼
           Notification Center
```

---

## 2. Source of Truth & Zero Auxiliary Storage

- **PostgreSQL / Supabase**: The authoritative and exclusive persistence layer for all notification records. Rows survive frontend reloads, browser restarts, logout/login sequences, and API restarts.
- **Zero Redis State**: Stage 49 adds 0 Redis keys, counters, streams, or pub/sub channels.
- **Zero ClickHouse Storage**: Notifications are operational transaction data, not analytical time-series.
- **Zero WebSocket Transport**: Stage 49 does not couple user notifications to the Stage 42/43 Market Event Stream. Real-time push is deferred; updates use lightweight bounded polling and event-driven refetching.

---

## 3. Update & Polling Strategy

- **Unread Count Polling Interval**: Bounded 30-second polling (`30000ms`) while authenticated and active.
- **Window Focus Refetch**: Focus listener automatically checks unread count when the user returns to the tab.
- **Document Visibility Handling**: Background polling is paused while `document.visibilityState === "hidden"` and triggers immediately upon returning to visible.
- **Center-Open Refetch**: Opening the Notification Center instantly refetches the active notification list and unread count.
- **Full-List Background Polling**: Disabled while the Notification Center is closed. Only the lightweight unread-count endpoint is polled.

---

## 4. Database Schema

The `notifications` table is defined in PostgreSQL via SQLAlchemy model `NotificationModel` and managed by Alembic migration `7e8f9012abcd_stage49_notifications.py`.

| Column | Type | Nullable | Meaning |
| :--- | :--- | :--- | :--- |
| `notification_id` | `UUID` | No | Server-generated primary key (UUIDv4) |
| `recipient_user_id` | `UUID` | No | Supabase authenticated user UUID (`auth.users.id`) |
| `category` | `VARCHAR(32)` | No | Category discriminator (`general`, `system`, `security`, `data`, `market`, `research`, `account`) |
| `severity` | `VARCHAR(16)` | No | Severity level (`info`, `success`, `warning`, `error`) |
| `title` | `VARCHAR(160)` | No | Plain-text notification headline (max 160 chars) |
| `message` | `VARCHAR(2000)` | No | Plain-text notification body (max 2000 chars) |
| `producer_key` | `VARCHAR(128)` | No | Machine-readable producer identifier (`[a-z][a-z0-9._-]{0,127}`) |
| `dedupe_key` | `VARCHAR(256)` | Yes | Optional producer idempotency key |
| `action_kind` | `VARCHAR(32)` | No | Safe navigation affordance (`none`, `internal_route`, `entity_route`) |
| `action_route` | `VARCHAR(256)` | Yes | Validated internal ATLAS route from Stage 4 allowlist |
| `action_entity_id` | `UUID` | Yes | FK → `entities.entity_id` (ON DELETE SET NULL) |
| `created_at` | `TIMESTAMPTZ` | No | Row creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | No | Last update timestamp (UTC) |
| `read_at` | `TIMESTAMPTZ` | Yes | Read timestamp (NULL if unread) |
| `archived_at` | `TIMESTAMPTZ` | Yes | Archive timestamp (NULL if active) |

### Database Constraints & Indexes

1. **Primary Pagination Index**:
   - `ix_notifications_recipient_pagination` on `(recipient_user_id, created_at DESC, notification_id DESC)`
2. **Unread Partial Index**:
   - `ix_notifications_recipient_unread` on `(recipient_user_id, created_at DESC)` WHERE `read_at IS NULL AND archived_at IS NULL`
3. **Dedupe Partial Unique Index**:
   - `uq_notifications_recipient_producer_dedupe` on `(recipient_user_id, producer_key, dedupe_key)` WHERE `dedupe_key IS NOT NULL`
4. **Archived Partial Index**:
   - `ix_notifications_recipient_archived` on `(recipient_user_id, archived_at DESC)` WHERE `archived_at IS NOT NULL`
5. **Check Constraints**:
   - `ck_notifications_category`: Validates allowed category values.
   - `ck_notifications_severity`: Validates allowed severity values.
   - `ck_notifications_action_kind`: Validates allowed action kinds.
   - `ck_notifications_action_consistency`: Enforces that `none` has null route/entity, `internal_route` has route with null entity, and `entity_route` has both route and entity.

---

## 5. State Derivation & Transitions

Notification lifecycle state is derived strictly from timestamps:

| State | Derived Rule | Meaning |
| :--- | :--- | :--- |
| **UNREAD** | `read_at IS NULL AND archived_at IS NULL` | Active unread notification contributing to badge count |
| **READ** | `read_at IS NOT NULL AND archived_at IS NULL` | Read notification retained in All list |
| **ARCHIVED** | `archived_at IS NOT NULL` | Removed from default visible views |

### Transition Rules

- **UNREAD → READ**: `read_at` is stamped with current UTC time. Idempotent (subsequent calls preserve initial read timestamp).
- **READ → UNREAD**: `read_at` is set to `NULL`.
- **UNREAD → ARCHIVED**: Archiving implies read. Sets both `read_at = now` and `archived_at = now`.
- **READ → ARCHIVED**: Sets `archived_at = now`. Preserves existing `read_at`.
- **ARCHIVED → UNREAD**: Disallowed. Raises `NotificationArchivedError` (HTTP 400).
- **Hard Delete**: Not exposed in public or user APIs.

---

## 6. Producer & Dedupe Semantics

- **Producer Key Format**: `^[a-z][a-z0-9._-]{0,127}$` (e.g. `system`, `auth.security`, `market_data`, `data.worker`).
- **Dedupe Uniqueness**: Scoped strictly to `(recipient_user_id, producer_key, dedupe_key)`. The same dedupe key for different users creates independent rows.
- **Idempotent Retry**: Repeating the same creation request with identical content returns the existing notification row without creating duplicates.
- **Dedupe Conflict**: If a producer reuses an existing dedupe key for materially different payload content, `NotificationDedupeConflictError` (HTTP 409) is raised.

---

## 7. Action Model & Security Allowlists

Notifications support safe, optional internal navigation affordances:

| Action Kind | Requirements | Behavior |
| :--- | :--- | :--- |
| `none` | `action_route = NULL`, `action_entity_id = NULL` | Click marks read; no navigation occurs |
| `internal_route` | `action_route` required, `action_entity_id = NULL` | Click marks read, closes center, navigates using client router |
| `entity_route` | `action_route` required, `action_entity_id` required | Click marks read, updates Stage 25 `selectEntity(UUID)`, navigates using router |

### Security Guarantees

1. **Route Allowlist**: Only the 20 canonical Stage 4 module routes (`/home`, `/markets`, `/charts`, `/watchlists`, `/screeners`, `/companies`, `/economics`, `/news`, `/research`, `/maps`, `/intelligence`, `/options`, `/trading`, `/portfolios`, `/risk`, `/ai`, `/data`, `/saved`, `/workspaces`, `/agents`) plus `/settings` are permitted.
2. **Rejection of External Schemes**: `http://`, `https://`, `//`, `javascript:`, `data:`, `file:` are rejected server-side and client-side.
3. **No Command Execution**: Notifications cannot execute shell, SQL, natural language, or Command Palette commands.
4. **No Trade / Approval Execution**: No trading buttons, order placement, or task approvals.
5. **Universal Entity Validation**: For `entity_route`, the referenced `entity_id` must resolve to an existing entity in the Universal Entity System at creation time.
6. **Plain Text Rendering**: Title and message are rendered strictly as text nodes (no `dangerouslySetInnerHTML`), preventing XSS.

---

## 8. Backend Service & Repository Layer

- **`NotificationRepository`**:
  - `create(model)`: Adds model to current session without auto-commit (composable with caller transaction).
  - `find_by_id(notification_id, recipient_user_id)`: Recipient-scoped lookup.
  - `find_by_dedupe(recipient, producer, dedupe_key)`: Unique dedupe lookup.
  - `get_unread_count(recipient_user_id)`: Unread count query.
  - `list_notifications(recipient, filter, limit, cursor)`: Keyset pagination using `(created_at DESC, notification_id DESC)` and URL-safe base64 opaque cursors.
  - `mark_read(...)`, `mark_unread(...)`, `mark_all_read(...)`, `archive(...)`: Atomic state mutations.
- **`NotificationService`**:
  - `create_notification(...)`: Internal creation method with entity validation, bounds checking, and dedupe conflict detection.
  - `list_notifications(...)`, `get_unread_count(...)`, `mark_read(...)`, `mark_unread(...)`, `mark_all_read(...)`, `archive(...)`.

---

## 9. FastAPI Public API Endpoints

All public notification endpoints require authenticated session and `atlas.access` permission. Recipient identity is derived from the verified token (`principal.user_id`) and is never accepted from the request body or query string.

| Method | Endpoint | Query / Path Params | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/notifications` | `filter=all\|unread\|archived`, `limit=1..100`, `cursor` | Keyset-paginated list of owned notifications |
| `GET` | `/api/v1/notifications/unread-count` | None | Lightweight unread count for badge persistence |
| `POST` | `/api/v1/notifications/{id}/read` | `id: UUID` | Idempotently marks notification as read |
| `POST` | `/api/v1/notifications/{id}/unread` | `id: UUID` | Marks notification as unread (fails on archived) |
| `POST` | `/api/v1/notifications/read-all` | None | Marks all active unread notifications as read |
| `POST` | `/api/v1/notifications/{id}/archive` | `id: UUID` | Archives notification (implies read) |

- **No Public Create Endpoint**: Notifications are created only via backend service calls.
- **No Hard Delete Endpoint**: Hard deletion is disabled.
- **Cross-User Protection**: Mutating or querying a notification belonging to another user returns HTTP 404 (does not leak existence).
- **HTTP Cache**: Responses return `Cache-Control: private, no-store`.

---

## 10. Frontend Architecture & Notification Center UI

### Component Structure

```text
TopBar
  └── NotificationTrigger
        ├── Bell icon (lucide-react)
        └── Unread Badge (hidden at 0, 1-99, 99+ at >= 100)
  └── NotificationCenter (Popover dialog, max-h-[580px], w-[380px])
        ├── Header (Title, Unread badge, Mark all read, Close button)
        ├── Filter Tabs (All, Unread)
        └── List Body
              ├── Loading Skeleton / Error Retry
              ├── Empty State ("No notifications" / "No unread notifications")
              ├── NotificationRow (Severity icon, Title, Plain text, Time, Action, Overflow buttons)
              └── Load More (Keyset pagination)
```

### State Management & Privacy

- **Memory-Only State**: Query and unread states are held in React Context (`NotificationsProvider`). No notification titles, messages, or counters are written to `localStorage` or `sessionStorage`.
- **Principal Switch Isolation**: When `session.user.id` changes or user logs out, the notification list, unread count, and cursor are reset to initial state.
- **Optimistic Updates**: Mark read, mark unread, mark all read, and archive update client state immediately and reconcile with server, rolling back if the request fails. Unread count is bound to `Math.max(0, count)`.
- **Selected Entity Context**: Entity routes invoke Stage 25 `selectEntity(action_entity_id)` before navigating, preserving selection for non-entity routes.

---

## 11. Explicitly Deferred Subsystems

Stage 49 establishes persistent notification infrastructure only. The following producer systems and channels are intentionally not implemented:
- Realtime WebSocket notification messaging (Market WebSocket untouched)
- Redis notification pub/sub or streams
- Alert rule engines (Market price alerts, Watchlist alerts, Portfolio/Risk thresholds)
- News and Economic release alert triggers
- Agent / Workflow automated completion notifications
- Task approvals / Broker trade execution buttons
- Email, SMS, Telegram, WhatsApp, Mobile Push
- Browser Notification API (`Notification.requestPermission`)
- Notification sound effects
- User notification preferences / quiet hours / Do Not Disturb
- Full standalone `/notifications` page or history export
- Global Search integration for notifications

---

## 12. Notification Center vs. Stage 50 Bottom Taskbar Alerts

It is critical to distinguish between Notifications and Alerts:
- **Notifications (Stage 49)**: Durable, delivered messages presented to the authenticated user in the TopBar Notification Center. Backed by PostgreSQL (`notifications` table).
- **Alerts (Stage 50 Bottom Taskbar)**: Future operational monitoring workspace for configuring condition rules and inspecting threshold triggers (price, risk, watchlist).
- The Stage 50 Bottom Taskbar includes a reserved `Alerts` panel shell. Opening or interacting with the Alerts panel does not duplicate, modify, or query Notification Center data.
