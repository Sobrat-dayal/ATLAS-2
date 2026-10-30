# Integrated ATLAS Terminal and Developer Console (Stage 122)

## Architectural Specification & Operator Manual

### 1. Executive Summary & Canonical Roadmap Position

The **Integrated ATLAS Terminal and Developer Console** (Stage 122 of 150) establishes a VS Code-style developer shell and Bloomberg Terminal-style financial console integrated directly into the persistent ATLAS AppShell bottom drawer. Stage 122 unifies text composition, multi-session management, dynamic console tabs, persistent user preferences, live operational diagnostics, and global context synchronization while establishing an absolute security boundary: **zero arbitrary command execution in Stage 122**.

Stage 123 owns approved sandboxed execution for Python, SQL, and ATLAS CLI commands.

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│ ATLAS                                                           Search / Settings / User │
├───────────────┬────────────────────────────────────────────────────────────────────────────┤
│               │                                                                            │
│               │                  MAIN ATLAS WORKSPACE                                      │
│ GLOBAL        │          Charts / Markets / Research / Portfolios / Risk                    │
│ SIDEBAR       │                                                                            │
│               ├────────────────────────────────────────────────────────────────────────────┤
│               │ TERMINAL [STAGE 122]        Desk: Equity Research | Context: AAPL  [-] [□] [×] │
│               ├────────────────────────────────────────────────────────────────────────────┤
│               │ [ATLAS CLI] [Python] [SQL] [Logs] [Agents] [MCP] [+]                       │
│               ├────────────────────────────────────────────────────────────────────────────┤
│               │ atlas> help                                                               │
│               │ Documented ATLAS Commands:                                                 │
│               │   markets        Navigate to Markets module or inspect asset class        │
│               │   instrument     Inspect canonical security metadata                       │
│               │   portfolio      List investment portfolios or inspect allocation          │
│               │   risk           Query multi-factor risk models and factor sensitivity     │
│               │                                                                            │
│               │ [!] Command execution is disabled in Stage 122. Sandbox in Stage 123.      │
│               │ atlas> _                                                                  │
├───────────────┴────────────────────────────────────────────────────────────────────────────┤
│ ATLAS BOTTOM TASKBAR       Tasks | Agents | Jobs | Alerts | Downloads | Health | Terminal  │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Six Principal Console Types

| Console Type | Icon | Input Editing | Real Read-Only Data | Arbitrary Execution | Stage 122 Status |
|---|---|---|---|---|---|
| **ATLAS CLI** | `Terminal` | Single-line prompt with history (Up/Down) | Static registered command help & syntax | **No** (Execution Disabled) | `INPUT_COMPOSITION_AND_HELP_READY` |
| **Python** | `Code2` | Multiline code editor, Tab/Shift-Tab indent, line numbers | Environment metadata (CPython 3.12 sandbox required) | **No** (Execution Disabled) | `MULTILINE_EDITOR_READY` |
| **SQL** | `Database` | Multiline SQL editor, line numbers | Target connection profile metadata | **No** (Direct DB blocked) | `MULTILINE_EDITOR_READY` |
| **Logs** | `ScrollText` | Read-only | Real authorized operational logs with severity & search filters | **No** (Read-only feed) | `REAL_DIAGNOSTICS_READY` |
| **Agents** | `Bot` | Read-only | Real registered agent platform records | **No** (Agent execution blocked) | `READ_ONLY_STATUS_MONITOR` |
| **MCP** | `Network` | Read-only | Real configured Model Context Protocol connections from `mcp/` | **No** (Tool invocation blocked) | `READ_ONLY_REGISTRY_INSPECTOR` |

---

### 3. Session Management & Persistence Architecture

#### 3.1 Stable Terminal Session Model
Each terminal session maintains a stable internal ID (`session_id`), owner user ID, terminal console type, display name, lifecycle state (`ACTIVE`, `MINIMIZED`, `CLOSED`), connection state (`CONNECTED`, `CONFIGURED`, `NOT_CONFIGURED`), and composite status (`READY`, `INPUT_ONLY`, `READ_ONLY`, `EXECUTION_UNAVAILABLE`).

#### 3.2 Default Onboarding Sessions
When a user opens the terminal with no active sessions, the system deterministically provisions the 4 institutional default tabs:
1. `ATLAS CLI` (order 0, active by default)
2. `Python` (order 1, quantitative scratchpad with sample Sharpe calculation)
3. `SQL` (order 2, relational query editor with sample instrument query)
4. `Logs` (order 3, operational application logs)

#### 3.3 Concurrency & Capacity Limits
- **Max Sessions**: Up to 32 concurrent tabs per user scope. Additional creation attempts reject with `TERMINAL_SESSION_LIMIT_EXCEEDED`.
- **Max Draft Size**: Up to 64 KB per draft buffer. Oversized drafts reject with `TERMINAL_DRAFT_TOO_LARGE`.
- **Optimistic Concurrency**: Monotonic `version` counter on sessions. Concurrent updates with mismatched `expected_version` reject with HTTP 409 Conflict (`TERMINAL_SESSION_VERSION_CONFLICT`).

---

### 4. Output Sanitization & Security Controls

1. **XSS Prevention**: Raw output strings pass through HTML entity escaping (`<`, `>`, `&`, `"`, `'`) before DOM insertion.
2. **Safe ANSI Rendering**: SGR escape sequences (colors 30-37, 90-97, bold) parse into structured styled spans.
3. **OSC Stripping**: Malicious OSC escape sequences (`OSC 8` hyperlinks, `OSC 52` clipboard manipulation, `OSC 0/2` window title tampering) are systematically stripped.
4. **Secret Redaction**: Real-time regex scrubber strips bearer tokens, JWT signatures, API secret keys, and passwords from log records before transmission.
5. **URL Validation**: Output links are validated against `http://` and `https://` schemes only; dangerous `javascript:` and `data:` schemes are blocked.

---

### 5. AppShell, Workspaces & Context Integration

- **AppShell Bottom Taskbar**: Trailing placement in `BottomTaskbar.tsx`. Clicking `Terminal` opens the drawer at the user's persistent height.
- **Global Keyboard Shortcut**: `Ctrl+\`` (or `Cmd+\``) toggles terminal drawer visibility across any of the 20 canonical top-level routes without displacing workspace panels.
- **Stage 120 Multi-Panel Workspace Independence**: Resizing the terminal drawer updates the persistent bottom drawer height without altering Stage 120 workspace split ratios or docking nodes.
- **Stage 121 Global Financial Context Display**: The terminal header reflects the active workspace desk name and active linked financial entities (`INSTRUMENT`, `COMPANY`, `PORTFOLIO`) without automatically injecting private financial ledgers into command drafts.
- **Command Palette Integration**: Registered `Terminal: Toggle Integrated Terminal` (`terminal.toggle`) under the `shell` category in Command Palette (`Cmd+K` / `Ctrl+K`).

---

### 6. Relational Database Schema

Stage 122 introduces 3 relational tables in PostgreSQL / Supabase:

1. **`terminal_sessions`**:
   - `session_id` (VARCHAR(64) PK): Unique session identifier.
   - `owner_user_id` (VARCHAR(64) NOT NULL): Authenticated user ID.
   - `workspace_id` (VARCHAR(64) NULL): Associated workspace scope.
   - `terminal_type` (VARCHAR(32) NOT NULL): Console type.
   - `display_name` (VARCHAR(128) NOT NULL): Tab label.
   - `lifecycle` (VARCHAR(32)): `ACTIVE`, `MINIMIZED`, `CLOSED`.
   - `connection_state` (VARCHAR(32)): `CONNECTED`, `NOT_CONFIGURED`, etc.
   - `execution_capability` (VARCHAR(32)): `DISABLED`.
   - `status` (VARCHAR(32)): `READY`, `INPUT_ONLY`, `READ_ONLY`.
   - `session_order` (INTEGER): Tab display order.
   - `version` (BIGINT): Optimistic concurrency sequence number.
   - `draft_content` (TEXT): Saved editor draft text.
   - `scrollback_limit` (INTEGER): Line buffer limit (default 2000).
   - Timestamps: `created_at`, `updated_at`, `last_active_at`, `closed_at`.

2. **`terminal_user_preferences`**:
   - `user_id` (VARCHAR(64) PK): User reference.
   - `font_size` (INTEGER): Editor font size (default 12px).
   - `font_family` (VARCHAR(256)): Permitted monospaced font family.
   - `line_height` (FLOAT): Line spacing (default 1.45).
   - `scrollback_limit` (INTEGER): Buffer size (default 2000).
   - `cursor_style` (VARCHAR(32)): `BLOCK`, `LINE`, `UNDERLINE`.
   - `word_wrap` (BOOLEAN): Soft wrap toggle.
   - `terminal_height` (INTEGER): Drawer height in pixels (default 320px).
   - `default_tab_type` (VARCHAR(32)): Initial console type.

3. **`terminal_audit_events`**:
   - `event_id` (VARCHAR(64) PK): Event audit ID.
   - `user_id` (VARCHAR(64) NOT NULL): User identity.
   - `session_id` (VARCHAR(64) NULL): Target session.
   - `event_type` (VARCHAR(64) NOT NULL): Event action (`SESSION_CREATED`, `SESSION_CLOSED`, `SESSIONS_REORDERED`).
   - `payload` (JSONB): Structured audit metadata.
   - `created_at` (TIMESTAMP WITH TIME ZONE): Event timestamp.

---

### 7. REST API Endpoints (`/api/v1/terminal`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/terminal/capabilities` | Retrieve capability catalog, console profiles, and Stage 123 contracts. |
| `GET` | `/api/v1/terminal/cli/help` | Retrieve documented CLI syntax and static registered commands. |
| `GET` | `/api/v1/terminal/sessions` | List all active sessions for the authenticated user. |
| `POST` | `/api/v1/terminal/sessions` | Create a new session of a specified console type. |
| `GET` | `/api/v1/terminal/sessions/{session_id}` | Retrieve details and draft for a specific session. |
| `PATCH` | `/api/v1/terminal/sessions/{session_id}` | Update title, draft content, or scrollback limit with version checking. |
| `DELETE` | `/api/v1/terminal/sessions/{session_id}` | Close a terminal session. |
| `PATCH` | `/api/v1/terminal/sessions/order` | Reorder tabs for the user. |
| `GET` | `/api/v1/terminal/preferences` | Load user's persistent terminal preferences. |
| `PUT` | `/api/v1/terminal/preferences` | Save updated terminal preferences. |
| `GET` | `/api/v1/terminal/logs` | Retrieve sanitized, authorized operational logs for the Logs console. |
| `GET` | `/api/v1/terminal/agents/status` | Retrieve truthful operational status of registered agents. |
| `GET` | `/api/v1/terminal/mcp/connections` | Retrieve truthful connection metadata for configured MCP servers. |
| `POST` | `/api/v1/terminal/execute` | **Strictly Disabled (HTTP 501)**. Blocks all execution attempts. |

---

### 8. Stage 123 Execution Handoff Specifications

Stage 122 prepares typed schema contracts for Stage 123 (Sandboxed Terminal Execution):

1. **`ExecutionCapabilityDefinition`**: Contract defining execution permission gates (`terminal.python.execute`, `terminal.sql.execute`), sandbox policy references, and API versions.
2. **`ExecutionRequestSchemaContract`**: Contract defining `request_id`, `session_id`, `terminal_type`, `payload`, `workspace_context_reference`, and `idempotency_key`.
3. **`ExecutionStatusContract`**: Contract defining execution lifecycle (`QUEUED`, `STARTING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`, `TIMED_OUT`), exit codes, and resource metrics (CPU ms, peak memory bytes).
4. **`ExecutionOutputStreamingContract`**: Contract defining stdout/stderr streaming chunks, sequence numbers, and timestamps.
5. **`CancellationContract`**: Contract for out-of-band cancellation of running sandbox processes.

---

### 9. Verification & Quality Gates

- **Backend Pytest**: 13 integration tests passing (`apps/api/tests/test_terminal_stage122_v1.py`).
- **Backend Lint**: 100% clean `ruff check` and `ruff format` on all terminal files.
- **Frontend Unit Tests**: 9 unit tests passing (`apps/web/src/lib/terminal/__tests__/terminal_stage122_v1.test.ts`).
- **Regression Tests**: Stage 120 multi-panel workspaces (11 tests) and Stage 121 global context linking (9 tests) passing with 0 regressions.
- **TypeScript Check**: `tsc --noEmit` clean across web workspace (0 errors).
- **Next.js Production Build**: 100% successful build across all 38 application routes.

