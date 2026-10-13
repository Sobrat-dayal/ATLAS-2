# ATLAS — STAGE 54: HOME TASKS AND APPROVALS
## Personal Task Management, Human Approval Inbox and Action Center

---

## 1. Executive Summary & Purpose

Stage 54 introduces the **Home Tasks and Approvals** section to the ATLAS Home operational command center. It establishes two distinct, decoupled domains:

1. **Domain A — Personal Tasks**: A human-managed work item tracking system belonging strictly to an authenticated user (`user_tasks` table). Tasks represent manual human work (e.g., reviewing filings, writing research notes, analyzing instruments) with optional deadlines, canonical ATLAS module context, and canonical Universal Entity context. Tasks do **not** trigger autonomous execution, background jobs, or scheduled alarms.
2. **Domain B — Human Approval Inbox**: A trusted backend-originated decision queue (`approval_requests` and `approval_decisions` tables). Trusted subsystems submit requests requiring explicit human confirmation. Users review immutable proposals and record binding `APPROVE` or `REJECT` decisions.

### Nonnegotiable Security Rule: Approval Is Not Execution
An approval decision is a durable audit record indicating that a specific authorized human approved or rejected an immutable proposal. **Recording an approval decision never triggers the underlying action automatically.** It does not execute broker orders, shell commands, agent runs, workflow runs, or external webhooks. Future subsystems that consume recorded approvals must independently revalidate proposal integrity, expiration, and current caller permissions at execution time.

---

## 2. Target Architecture & Flow

```text
       ATLAS AUTHENTICATED APPSHELL
                   │
                   ▼
            HOME DASHBOARD (/home)
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
     MY TASKS          PENDING APPROVALS
        │                     │
        ▼                     ▼
    Task API             Approval API
  (/api/v1/tasks)      (/api/v1/approvals)
        │                     │
        ▼                     ▼
   PersonalTaskService   ApprovalService
        │                     │
        └──────────┬──────────┘
                   │
                   ▼
         PostgreSQL / Supabase
        (Authoritative Storage)
                   │
                   ▼
      ┌─────────────────────────┐
      │ user_tasks              │
      │ approval_requests       │
      │ approval_decisions      │
      └─────────────────────────┘
                   │
                   ▼
         DURABLE AUDIT RECORD
         (NO EXECUTION DISPATCH)
```

### Trusted Producer Ingestion Flow
```text
  Future Trusted Producer (e.g. Test / Internal Service)
                   │
                   ▼ (Internal Method Only — No Public API)
        ApprovalService.create_request()
                   │
                   ▼
       Validated against Allowlist & SHA-256 Digest
                   │
                   ▼
         PostgreSQL (PENDING, Expires in ≤ 7 days)
                   │
                   ▼
         Human Decision (APPROVE / REJECT)
                   │
                   ▼
         PostgreSQL (Atomic Transaction + Immutable Decision Audit)
                   │
                   ▼
              STOPS HERE.
```

---

## 3. Domain A: Personal Tasks Specification

### Database Schema (`user_tasks`)

| Column | Type | Nullable | Description |
|---|---|---|---|
| `task_id` | UUID | No | Primary Key, server-generated canonical task identity |
| `owner_user_id` | UUID | No | Foreign Key to auth principal; strict row-level isolation |
| `title` | VARCHAR(160) | No | Non-empty plain text title (max 160 characters) |
| `description` | VARCHAR(2000) | Yes | Optional plain text notes/research context (max 2000 chars) |
| `status` | VARCHAR(20) | No | Status enum: `OPEN`, `COMPLETED`, `CANCELLED` |
| `due_at` | TIMESTAMPTZ | Yes | Optional UTC timestamp deadline |
| `module_id` | VARCHAR(50) | Yes | Optional canonical Stage 4 module ID |
| `entity_id` | UUID | Yes | Optional canonical Stage 16 Universal Entity UUID |
| `created_at` | TIMESTAMPTZ | No | Server timestamp of creation |
| `updated_at` | TIMESTAMPTZ | No | Server timestamp of last mutation |
| `completed_at` | TIMESTAMPTZ | Yes | Server timestamp when status became `COMPLETED` |
| `cancelled_at` | TIMESTAMPTZ | Yes | Server timestamp when status became `CANCELLED` |
| `version` | INTEGER | No | Optimistic concurrency control counter (default 1) |
| `idempotency_key`| VARCHAR(64) | Yes | Client-generated key for creation deduplication |

### Indexes & Constraints
- `uq_user_tasks_owner_idempotency`: Unique `(owner_user_id, idempotency_key)` where `idempotency_key IS NOT NULL`.
- `ix_user_tasks_owner_status_due`: B-tree index on `(owner_user_id, status, due_at)`.
- `ix_user_tasks_owner_created`: B-tree index on `(owner_user_id, created_at, task_id)`.
- `ck_user_tasks_status`: Check constraint `status IN ('OPEN', 'COMPLETED', 'CANCELLED')`.

### Task Status Lifecycle

```text
    CREATE
      │
      ▼
    OPEN ─────────────► COMPLETED
      │                     │
      │                     ▼
      │                    OPEN (Reopen)
      │
      ▼
    CANCELLED (Terminal)
```

- **OPEN → COMPLETED**: Sets `completed_at = now()`, advances `version`.
- **COMPLETED → OPEN**: Clears `completed_at`, advances `version`.
- **OPEN → CANCELLED**: Sets `cancelled_at = now()`, advances `version`.
- Invalid transitions (e.g. `CANCELLED → OPEN`, `CANCELLED → COMPLETED`) are rejected with `InvalidTaskTransitionError (400)`.

### Due Dates, Overdue, and Due Soon
- Deadlines are stored as timezone-aware UTC timestamps.
- **Overdue** is derived: `status == "OPEN" and due_at < server_now()`. Completed or cancelled tasks are never overdue.
- **Due Soon** is derived: `status == "OPEN" and server_now() <= due_at <= server_now() + 24 hours`.
- Due dates do **not** trigger automatic push notifications, background workers, or scheduled tasks.

### Context Navigation
- Tasks can reference an internal canonical module (validated against `CANONICAL_MODULES`) and a Universal Entity UUID (validated against `entity_identifiers`).
- "Open Context" action sets the active entity context via Stage 25 `useSelectedEntity` and routes safely via Next.js router. It never executes arbitrary code or shell commands.

---

## 4. Domain B: Approval Requests & Decisions Specification

### Database Schema (`approval_requests`)

| Column | Type | Nullable | Description |
|---|---|---|---|
| `approval_id` | UUID | No | Primary Key, server-generated approval identity |
| `approver_user_id` | UUID | No | Designated human decision-maker; strict row-level isolation |
| `producer_key` | VARCHAR(64) | No | Allowlisted trusted backend originating subsystem |
| `action_kind` | VARCHAR(64) | No | Allowlisted category of requested action |
| `proposal_reference` | VARCHAR(256) | No | Opaque, immutable proposal identifier |
| `proposal_digest` | VARCHAR(64) | No | SHA-256 hex digest binding to immutable proposal contents |
| `title` | VARCHAR(160) | No | Plain text summary title |
| `summary` | VARCHAR(2000) | No | Plain text explanation of proposed action |
| `status` | VARCHAR(20) | No | Status enum: `PENDING`, `APPROVED`, `REJECTED`, `CANCELLED` |
| `requested_at` | TIMESTAMPTZ | No | Creation timestamp |
| `expires_at` | TIMESTAMPTZ | No | Hard decision deadline (default 24h, max 7d) |
| `decided_at` | TIMESTAMPTZ | Yes | Decision timestamp |
| `decided_by_user_id`| UUID | Yes | Actual authenticated actor who recorded the decision |
| `version` | INTEGER | No | Optimistic concurrency control counter (default 1) |
| `idempotency_key`| VARCHAR(64) | No | Trusted producer deduplication key |

### Database Schema (`approval_decisions`)

| Column | Type | Nullable | Description |
|---|---|---|---|
| `decision_id` | UUID | No | Primary Key, immutable audit decision record UUID |
| `approval_id` | UUID | No | Foreign Key to `approval_requests.approval_id` (Unique) |
| `approver_user_id` | UUID | No | Actual authenticated human user |
| `decision` | VARCHAR(20) | No | `APPROVE` or `REJECT` |
| `decided_at` | TIMESTAMPTZ | No | Server timestamp of decision |
| `decision_idempotency_key`| VARCHAR(64) | No | Client retry key |
| `reason` | VARCHAR(500) | Yes | Optional plain text notes/justification (max 500 chars) |

### Trusted Producer Trust Model
- **No Public Creation Endpoint**: Ordinary users cannot call `POST /api/v1/approvals`. Approval creation is strictly an internal method on `ApprovalService`.
- **Producer Allowlist**: Only registered producer keys (`"trading_system"`, `"agent_system"`, `"workflow_engine"`, `"portfolio_rebalance"`, `"test_producer"`) are accepted.
- **Action Kind Allowlist**: Only registered action kinds (`"execute_order"`, `"deploy_agent"`, `"trigger_workflow"`, `"rebalance_portfolio"`, `"test_action"`) are accepted.
- **Proposal Binding**: Each request requires an opaque `proposal_reference` and a 64-character SHA-256 `proposal_digest`.
- **Zero Fake Approvals**: In production, zero autonomous producers are connected in Stage 54. The production pending approvals count is truthfully **0**, and the inbox renders a clean empty state.

### Expiration Semantics
- Every request has a finite `expires_at` (1 minute to 7 days, default 24 hours).
- A request is decision-eligible only if `status == "PENDING" and expires_at > server_now()`.
- Expired requests cannot be approved or rejected. Attempted decisions on expired requests are rejected with `ApprovalExpiredError (400)`.

### Atomic Decision Recording
Decisions use `SELECT ... FOR UPDATE` row locking inside an atomic SQLAlchemy transaction:
1. Verify designated approver matches authenticated principal.
2. Verify status is `PENDING`.
3. Verify `expires_at > now()`.
4. Check version matches `expected_version` (if provided).
5. Update `approval_requests` (`status = APPROVED|REJECTED`, `decided_at = now()`, `decided_by_user_id = principal.sub`, `version += 1`).
6. Insert immutable `approval_decisions` audit row.
7. Commit transaction.
8. **ZERO execution dispatch occurs.**

---

## 5. API Reference

### Personal Tasks API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/tasks` | Keyset-paginated list of tasks filtered by `status` (`OPEN`, `COMPLETED`, `CANCELLED`, `ALL`). Default limit 10, max 50. |
| `POST` | `/api/v1/tasks` | Create personal task (201 Created). Derives owner from principal. Supports `idempotency_key`. |
| `GET` | `/api/v1/tasks/counts` | Returns authoritative `open_count` and `overdue_count`. |
| `PATCH` | `/api/v1/tasks/{task_id}` | Edit title, description, due date, module, or entity. Enforces optimistic `expected_version`. |
| `POST` | `/api/v1/tasks/{task_id}/complete`| Mark task complete. |
| `POST` | `/api/v1/tasks/{task_id}/reopen` | Reopen completed task. |
| `POST` | `/api/v1/tasks/{task_id}/cancel` | Cancel task (terminal). |

### Approvals API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/approvals` | Keyset-paginated list of approvals assigned to authenticated user. Default limit 10, max 50. |
| `GET` | `/api/v1/approvals/counts` | Returns authoritative `pending_count` (excluding expired requests). |
| `GET` | `/api/v1/approvals/{approval_id}` | Get full approval details, including proposal digest and recorded decision record. |
| `POST` | `/api/v1/approvals/{approval_id}/decision` | Record human `APPROVE` or `REJECT` decision. Atomic, race-safe, idempotent. |

---

## 6. Frontend Architecture & Home Integration

### Component Tree
```text
HomeTasksApprovals
   ├── Header (Tabs: My Tasks [count] | Approvals [count], Add Task button)
   ├── PersonalTaskList
   │      ├── Filter Tabs (Open | Completed | Cancelled | All)
   │      ├── PersonalTaskRow (Completion checkbox, badges, due date, Open Context, actions menu)
   │      ├── Empty State (No open tasks + Add Task launcher)
   │      └── Loading / Error Skeletons
   ├── PendingApprovalList
   │      ├── Filter Tabs (Pending | Approved | Rejected | Expired | All)
   │      ├── PendingApprovalRow (Producer, action kind, title, summary, expiration, Review button)
   │      ├── Truthful Empty State (No pending approvals)
   │      └── Loading / Error Skeletons
   ├── TaskEditorDialog (Accessible modal for Add / Edit task)
   └── ApprovalReviewDialog (Accessible review modal with security warning and Approve/Reject controls)
```

### Bottom Taskbar Integration (`TasksPanel.tsx`)
The Stage 50 reserved Tasks panel is upgraded to consume `usePersonalTasks`:
- Shares the same authoritative `PersonalTaskService` backend APIs.
- Offers full task filtering, completion, reopening, and creation.
- Preserves all other taskbar panels (Terminal, Alerts, Jobs, Agents, Downloads, System Health) and the Agent Dock.

---

## 7. Security, Privacy & Invariants

1. **Authentication & Authorization**: All endpoints require active bearer authentication and enforce `atlas.access`.
2. **Owner-Scoped Isolation**: Users can only see and mutate their own tasks and approvals. Cross-user access returns `404 Not Found`.
3. **No Executive Side-Effects**: Approving an approval request does not invoke commands, broker APIs, agents, or workflows.
4. **No Sensitive Payloads in Summaries**: Summaries and reasons are bounded plain text.
5. **No Local Storage of Private Content**: Tasks and approvals are strictly in-memory TanStack Query caches, cleared on principal logout.
6. **No Fake Data**: When no approvals exist, pending count is `0`.
