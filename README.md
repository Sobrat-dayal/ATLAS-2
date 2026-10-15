# ATLAS

**AI-native financial intelligence, markets, research, trading, geospatial intelligence, portfolio analytics, risk, data, and autonomous-agent operating system.**

**Current implementation stage:** Stage 2 — Monorepo Foundation

**Warning:** Production implementation has not started. This repository currently contains the structural foundation and product specification. No frontend pages, backend APIs, databases, or production functionalities are active yet.

## About
ATLAS is designed as a professional, desktop-first financial operating environment combining concepts from institutional terminals, advanced geospatial platforms, and autonomous AI-agent workforces.

## Repository Structure
ATLAS uses a monorepo architecture:
- `apps/web`: Frontend application (Stage 3+)
- `apps/api`: Backend application API (Stage 11+)
- `python/atlas/`: Python domain packages (Modular Monolith)
- `packages/`: Shared frontend packages
- `agents/`, `workflows/`, `mcp/`: Configuration and definition assets
- `infrastructure/`: Infrastructure configurations
- `docs/`: Full documentation

## Setup
- **Python**: Use `uv` with python 3.12 (`python/atlas/pyproject.toml`, `apps/api/pyproject.toml`)
- **Node**: Use `pnpm` workspaces (`pnpm-workspace.yaml`, `package.json`)

## Database Architecture
- **PostgreSQL**: Authoritative source of truth for entities, relationships, configuration, and capabilities.
- **ClickHouse**: High-volume, immutable analytical data (Market Data, Event Streams).
- **Valkey**: Ephemeral low-latency state, caching, and real-time coordination.

## Run
To run the full stack locally:

```bash
# Terminal A (Frontend):
pnpm run dev:web

# Terminal B (Backend):
cd apps/api
uv run uvicorn atlas_api.main:app --reload

# Terminal C (Infrastructure):
pnpm clickhouse-up
pnpm valkey-up
```
The full product specification is located in the `docs/` directory. Check the [Documentation Index](docs/README.md) for more details.

## Global Search (Stage 45)
- Open via center search bar in AppShell TopBar.
- Backed by PostgreSQL indexed search (`entities`, `entity_aliases`, `entity_identifiers`).
- Searches canonical entities with deterministic exact, prefix, and trigram fuzzy matching.
- Selecting an entity updates global selected entity context without auto-navigating.
- Run tests: `pytest apps/api/tests/search/test_global_search.py`

## Command Palette (Stage 46)
- **Shortcut**: `Cmd + K` (macOS) / `Ctrl + K` (Windows/Linux) or click the shortcut badge in the TopBar.
- **Commands**: Discover and execute explicitly registered navigation commands across all 20 modules, global settings, section settings, search entity handoff, and entity selection clearance.
- **Execution**: 100% frontend-local deterministic filtering with 0 backend queries, 0 Provider calls, and 0 LLM calls.
- **Adding a Command**: Register in `apps/web/src/lib/commands/registry.ts` with a unique ID, human-readable label, category, optional keywords/aliases, and typed `execute` handler.
- **Run tests**: `npx.cmd tsx --test apps/web/tests/commands.test.ts`

## Command Parsing (Stage 47)
- **Syntax**: ATLAS Command Language v1 supports structured slash syntax and Bloomberg-style shorthand:
  - `/markets` — Module navigation
  - `/charts NVDA` or `/charts open NVDA` — Select NVDA security and navigate to Charts
  - `NVDA CHART` — Shorthand to select NVDA and navigate to Charts
  - `NVDA NEWS` — Shorthand to select NVDA and navigate to News
  - `MAP TSMC` — Shorthand to select TSMC entity and navigate to Maps
  - `OPTIONS NVDA` — Shorthand to select NVDA and navigate to Options
  - `NVDA FA` — Reserved recognized shorthand (unavailable in current stage)
  - `PORT RISK` — Reserved recognized shorthand (unavailable in current stage)
- **Deterministic Pipeline**: Pure Lexer -> Parser -> AST -> Binder -> Stage 22 Entity Resolver -> Authorization -> Command Preview.
- **Strict Boundaries**: 0 LLM calls, 0 vector search, 0 embeddings, 0 shell execution, 0 DB writes.
- **Testing**:
  - Backend: `pytest apps/api/tests/commands/test_command_parsing.py`
  - Frontend: `npx.cmd tsx apps/web/tests/commands-parser.test.ts`

## Natural-Language Command Interpretation (Stage 48)
- **Natural Phrasing**: Single-turn interpretation translating human instructions into deterministic Stage 47 syntax:
  - `"take me to markets"` -> `/markets`
  - `"show me NVDA's chart"` -> `/charts "NVDA"`
  - `"open NVIDIA Corporation in companies"` -> `/companies "NVIDIA Corporation"`
  - `"open settings"` -> `/settings`
- **Safety Boundary**: The model may interpret intent, but it may **never** directly execute anything. 0 tools provided, 0 direct command IDs from model, 0 autonomous agents, no multi-step planner, no conversation memory, no DB writes.
- **Developer Configuration**:
  - `ATLAS_NL_COMMAND_ENABLED=true`: Enable natural-language interpretation.
  - `ATLAS_NL_COMMAND_MOCK_MODE=true`: Enable deterministic offline mock model client for tests & local dev.
  - `ATLAS_NL_COMMAND_MODEL_BASE_URL`: Server-side endpoint URL (default `https://api.openai.com/v1`).
  - `ATLAS_NL_COMMAND_MODEL_NAME`: Configured model identifier (default `gpt-4o-mini`).
  - `ATLAS_NL_COMMAND_MODEL_API_KEY`: Server-side model credential (never exposed to frontend).
  - `ATLAS_NL_COMMAND_TIMEOUT_SECONDS=10.0`: Model request timeout.
- **Testing**:
  - Backend: `pytest apps/api/tests/commands/test_natural_language_interpretation.py`
  - Frontend: `npx.cmd tsx --test apps/web/tests/commands-interpreter.test.ts`

## Persistent Notification Center (Stage 49)
- **Architecture**: Secure, durable user-scoped notifications backed by PostgreSQL (`notifications` table).
- **Update Strategy**: 30-second bounded unread-count polling while page is visible, focus refetch, center-open refetch. 0 WebSocket transport, 0 Redis keys, 0 ClickHouse tables.
- **TopBar Trigger**: Bell icon with real unread count badge (hidden at 0, 99+ at >= 100).
- **Notification Center**: Slide-over panel with All/Unread filter tabs, Mark all as read, and deterministic keyset pagination.
- **Database Migration**:
  ```bash
  cd apps/api
  uv run alembic upgrade head
  ```
- **Internal Service Creation**:
  ```python
  from atlas.notifications import CreateNotification, NotificationCategory, NotificationSeverity, NotificationService

  service = NotificationService(db_session)
  notif = await service.create_notification(
      CreateNotification(
          recipient_user_id=user_uuid,
          category=NotificationCategory.SYSTEM,
          severity=NotificationSeverity.INFO,
          title="System Maintenance",
          message="Scheduled upgrade completed successfully.",
          producer_key="system.ops",
      )
  )
  ```
- **APIs**:
  - `GET /api/v1/notifications` — Keyset-paginated list of owned notifications
  - `GET /api/v1/notifications/unread-count` — Lightweight unread count
  - `POST /api/v1/notifications/{id}/read` — Idempotent mark read
  - `POST /api/v1/notifications/{id}/unread` — Mark unread (rejects archived)
  - `POST /api/v1/notifications/read-all` — Mark all visible unread notifications as read
  - `POST /api/v1/notifications/{id}/archive` — Archive notification (implies read)
- **Testing**:
  - Backend: `pytest apps/api/tests/notifications -v`
  - Frontend: `npx.cmd tsx --test apps/web/tests/notifications.test.ts`

## Persistent Bottom Taskbar & Workspace Panel (Stage 50)
- **Placement**: Permanently pinned at the bottom edge of the authenticated AppShell across all 20 modules.
- **Interactions**:
  - Click any taskbar item (`Tasks`, `Agents`, `Jobs`, `Alerts`, `Downloads`, `System Health`, `Terminal`) to open or switch panels.
  - Click the active item again to toggle/close the panel.
  - Click `X` in the panel header or press `Escape` to close.
- **Resizing**: Drag the top resize handle upward or downward (default 280px, clamped between 160px and 45% of viewport height). Double-click the handle to reset to 280px. Keyboard resizing supported via `ArrowUp` / `ArrowDown`.
- **Future Panel Extension**: Statically registered in `PANEL_DEFINITIONS` within `apps/web/src/lib/bottom-taskbar/registry.ts`. Future roadmap stages (Stage 54, Stage 122, Stage 146+) can connect domain components directly to this shell.
- **Testing**:
  - Run tests: `npx.cmd tsx --test apps/web/tests/bottom-taskbar.test.ts`

## Home Market Summary (Stage 52)
- **Placement**: Integrated into the primary column of the ATLAS Home operational dashboard (`/home`, Module 1).
- **Core Functionality**:
  - Truthful, real-time observation cards for server-owned curated benchmark instruments (S&P 500, NASDAQ 100, Dow Jones, SPY ETF, EUR/USD, USD/JPY, Bitcoin, Brent Crude).
  - Traded prices derived strictly from canonical quote state (Stage 41) with full Decimal precision preserved.
  - Performance changes calculated only when a verified completed prior session reference close exists from ClickHouse (Stage 39). Zero guessing of trading calendars or missing references.
  - Data freshness, delivery delay, and provenance classification powered directly by the Stage 44 canonical freshness engine.
  - Snapshot race protection and live quote invalidation integration (`atlas:market.quote.updated`).
  - One-click navigation to `/markets` with Stage 25 Universal Selected Entity context activation.
- **Strict Data Guarantee**: Zero synthetic stock prices, zero mock percentage returns, zero provider calls on page load, and zero database writes.
- **Testing**:
  - Backend: `uv run --directory apps/api pytest tests/home/test_market_summary.py`
  - Frontend: `npx tsx --tsconfig apps/web/tsconfig.json --test apps/web/tests/home-market-summary.test.ts`
- **Documentation**: See `docs/HOME_MARKET_SUMMARY.md`

## Home Personalized Activity (Stage 53)
- **Placement**: Integrated into the primary column of the ATLAS Home operational dashboard (`/home`, Module 1) directly below Market Summary.
- **Core Functionality**:
  - Workspace continuity helping authenticated users resume recently opened modules and selected canonical entities.
  - Strict privacy-first design: user activity recording is **disabled by default** (`home.activity_history_enabled = false`). Explicit user opt-in required.
  - User-scoped PostgreSQL storage with server-authoritative UTC timestamps (`occurred_at`, `created_at`).
  - Idempotency guaranteed via `(user_id, client_event_id)` uniqueness.
  - Capture limited strictly to explicit user actions: `MODULE_OPENED` (canonical module ID) and `ENTITY_SELECTED` (canonical entity UUID).
  - Keyset pagination (`occurred_at DESC, activity_id DESC`), default page size 10, max 50.
  - Safe resume navigation: reopening canonical module route and selecting canonical entity via Stage 25 `selectEntity(uuid)` with permission rechecks.
  - Atomically coordinated disable-and-clear: disabling consent purges all user Stage 53 activity rows immediately.
  - User-initiated Clear History with confirmation dialog.
  - Bounded retention: 90-day retention query cutoff, per-user cap (max 1,000 events), and operator maintenance cleanup routine (`run_activity_retention_cleanup`).
- **Strict Privacy & Scope Guarantees**:
  - Zero surveillance, zero clickstream tracking, zero keystroke/mouse/scroll tracking, zero passive route/render logging.
  - Zero raw search query or command text storage.
  - Zero AI/LLM profiling, embeddings, RAG, or behavioral scoring.
  - Zero Redis streams, ClickHouse activity warehouse, or message brokers.
  - Zero third-party analytics SDKs, device fingerprinting, or IP logging.
- **Testing**:
  - Backend: `uv run --directory apps/api pytest tests/home/test_user_activity.py`
  - Frontend: `npx tsx --tsconfig apps/web/tsconfig.json --test apps/web/tests/home-personalized-activity.test.ts`
- **Documentation**: See `docs/HOME_PERSONALIZED_ACTIVITY.md`

## Home Tasks and Approvals (Stage 54)
- **Placement**: Integrated into the secondary column of the ATLAS Home operational dashboard (`/home`, Module 1) alongside Quick Launch, and powering the Stage 50 Bottom Taskbar Tasks panel.
- **Core Functionality**:
  - **Domain A — Personal Tasks**: User-managed manual work items (`user_tasks` table in PostgreSQL). Support for task creation, editing, completion, reopening, and cancellation with optimistic concurrency control (`version`). Optional UTC deadlines with derived `is_overdue` and `is_due_soon` presentation flags. Optional canonical module context and Universal Entity UUID context with safe "Open Context" navigation.
  - **Domain B — Human Approval Inbox**: Trusted backend decision queue (`approval_requests` and `approval_decisions` tables in PostgreSQL). Internal-only request creation with strict allowlists for producer keys and action kinds, binding to an opaque proposal reference and SHA-256 proposal digest. Finite request lifetime (default 24h, max 7d) with server-time expiration enforcement. Explicit `APPROVE` or `REJECT` decision recording into an immutable audit trail with row-level concurrency protection (`SELECT ... FOR UPDATE`).
  - **Bottom Taskbar Integration**: Upgrades the reserved Stage 50 Tasks panel to a live personal task management surface consuming the shared `usePersonalTasks` hook.
- **Strict Security & Scope Guarantees**:
  - **APPROVAL IS NOT EXECUTION**: Recording an approval decision stores human intent in PostgreSQL only. It **never** triggers broker orders, shell execution, agent runs, workflow runs, or external webhooks.
  - **Zero Public Approval Creation**: Public users cannot create approval requests. No public `POST /api/v1/approvals` creation endpoint exists.
  - **Zero Fake Approvals**: In production, 0 unintegrated producers are simulated. The pending approvals inbox truthfully displays 0 pending requests and an honest empty state.
  - **Zero Autonomous Execution**: Tasks and due dates do not trigger background jobs, push notifications, or scheduled execution.
  - **Zero LocalStorage Persistence**: Private task descriptions and approval details are never cached in browser localStorage or IndexedDB.
- **Testing**:
  - Backend: `uv run pytest tests/home/test_tasks_approvals.py -v` (inside `apps/api`)
  - Frontend: `npx tsx --test apps/web/tests/home-tasks-approvals.test.ts`
- **Documentation**: See `docs/HOME_TASKS_APPROVALS.md`

## Home Intelligence Feed Placeholder (Stage 55)
- **Placement**: Integrated into the secondary column of the ATLAS Home operational dashboard (`/home`, Module 1) directly below Tasks & Approvals.
- **Core Purpose & Presentation Foundation**:
  - Compact, professional intelligence feed presentation foundation establishing a truthful reserved state and extension point for future stages.
  - Truthful, non-misleading service state: explicitly presented as **"Reserved" / "Not Connected"** ("Intelligence feed not connected: Verified intelligence updates will appear here when the ATLAS Intelligence service becomes available.").
  - Clear semantic distinction between states: **Reserved** (service not yet implemented/connected), **Loading** (real backend request in flight), **Ready** (authenticated service connected), **Empty** (connected service returned 0 items), **Unavailable** (service temporarily unreachable), and **Error** (real request failed).
  - Unknown counts are represented honestly: zero fake counters (no "0 threats", "0 events", "0 risks").
  - Accessible, permission-aware navigation to the canonical Intelligence workspace at `/intelligence` (`ATLAS_MODULES.intelligence.route`) respecting Stage 14 route authorization and preserving Stage 25 Selected Entity Context.
  - Minimal presentation-only TypeScript contract (`IntelligenceFeedViewState`, `IntelligenceFeedViewItem`) without premature Universal Event domain schema definitions.
- **Roadmap Integration**:
  - Real intelligence events and services will be supplied by future roadmap stages:
    - Stage 135: Universal Event model
    - Stage 136: Event–Entity Graph
    - Stage 137: Exposure Analysis
    - Stage 138: Intelligence Service V1 & Read API
    - Stage 139: Intelligence Scoring & methodology
    - Stage 140: God's Eye Intelligence
- **Strict Data Integrity & Boundary Guarantees**:
  - **Zero Fabricated Content**: Zero invented geopolitical events, financial crises, cyber incidents, supply-chain disruptions, or market-moving headlines.
  - **Zero Fabricated Scores**: Zero fake confidence scores ("97%"), risk percentages, sentiment classifications ("Bullish"), or severity levels.
  - **Zero Fabricated Provenance**: Zero fake source citations ("Reuters") or fabricated source counts.
  - **Zero Backend Changes**: Zero new FastAPI endpoints, zero PostgreSQL migrations, zero ClickHouse tables, zero Redis keys/streams, zero WebSockets.
  - **Zero AI/Agent Execution**: Zero LLM calls, zero autonomous research workers, zero OSINT scraping, and zero background jobs.
- **Testing**:
  - Run component & contract tests: `npx tsx --tsconfig apps/web/tsconfig.json --test apps/web/tests/home-intelligence-feed.test.ts`
- **Documentation**: See `docs/HOME_INTELLIGENCE_FEED.md`

## Markets Overview V1 (Stage 56)
- **Placement**: Mounted on the canonical route `/markets` (`ATLAS_MODULES.markets.route`), Module 2 of the 20 canonical ATLAS modules.
- **Core Terminal Architecture**:
  - Professional, data-dense financial market intelligence workspace inspired by Bloomberg Terminal and OpenBB.
  - Header with quick navigation to `/charts`, `/screeners`, `/watchlists`, and Search (Stage 45) scoping.
  - Scoped Coverage Summary metrics (`configured_instruments`, `available_quotes`, `unavailable_quotes`) with truthful data scopes.
  - Accessible Market Group tabs (`All`, `Benchmarks`, `Equities`, `ETFs`, `FX`, `Crypto`, `Commodities`, `Bonds`) with live count badges.
  - Top Featured Instruments grid (7 canonical benchmark instruments) with Stage 25 `selectEntity` integration.
  - High-density tabular overview with sortable columns, tabular figures, signed change treatments, freshness indicators, and cursor pagination.
- **Curated Multi-Asset Catalog**:
  - Bounded universe of 29 canonical financial instruments across 7 asset classes configured via deterministic UUID5 identifiers (`ATLAS_INSTRUMENT_NAMESPACE`).
  - Strict separation of benchmark indices and tracking ETFs (e.g., S&P 500 Index `^GSPC` points vs. SPDR S&P 500 ETF `SPY` dollars).
- **Read-Only Backend & Financial Data Integrity**:
  - `GET /api/v1/markets/overview`: Authenticated read endpoint enforcing `atlas.access` authorization and financial-data entitlements.
  - Zero side-effects: 0 database writes, 0 Redis writes, 0 ClickHouse writes, 0 background jobs, 0 direct provider fetches on page load.
  - Reuses Stage 52 shared financial read logic (`ReferenceCloseResolver`, `calculate_market_changes`, Decimal precision, zero-denominator safety).
  - Reuses Stage 44 freshness and delay classification; independent connection vs. observation freshness indicators.
- **Realtime Updates & Snapshot Consistency**:
  - Reuses Stage 43 WebSocket infrastructure, listening to Stage 42 `atlas:market.quote.updated` events.
  - Safe coalesced refetching with snapshot race protection (`lastAcceptedGeneratedAtRef`), focus refetch, and reconnect recovery.
- **Strict No Fake Data Policy**:
  - Missing quotes are truthfully displayed as unavailable (`—`, `no_quote`); zero synthetic stock prices, zero fake market caps, zero fake volumes.
- **Testing**:
  - Backend: `uv run pytest tests/markets/test_markets_overview.py -v` (inside `apps/api`)
  - Frontend: `npx tsx --tsconfig apps/web/tsconfig.json --test apps/web/tests/markets-overview.test.ts`
- **Documentation**: See `docs/MARKETS_OVERVIEW_V1.md`

## Equities Markets V1 (Stage 57)
- **Placement**: Mounted on `/markets/equities`, extending Module 2 (`/markets`).
- **Core Architecture**:
  - Global equity security discovery and inspection workspace grounded in canonical Financial Instrument records.
  - Strict distinction between Issuer Company (Stage 18), Equity Security (Stage 17), and Exchange Listing.
  - Multi-market listing support with Market Identifier Codes (MIC: `XNAS`, `XNYS`, `XNSE`, `XLON`, `XTKS`).
  - Read-only endpoints: `GET /api/v1/markets/equities`, `GET /api/v1/markets/equities/filters`, `GET /api/v1/markets/equities/{id}`.
  - High-density tabular layout with sorting, deterministic keyset pagination, and side Inspector panel.
- **Testing**:
  - Backend: `pytest apps/api/tests/markets/test_markets_equities.py`
  - Frontend: `npx.cmd tsx --tsconfig apps/web/tsconfig.json --test apps/web/tests/markets-equities.test.ts`
- **Documentation**: See `docs/EQUITIES_MARKETS_V1.md`

## ETFs & Funds Markets V1 (Stage 58)
- **Placement**: Mounted on the canonical route `/markets/funds`, extending Module 2 (`/markets`).
- **Core Architecture**:
  - Global fund vehicle discovery, ETF intelligence, and NAV-aware market data explorer.
  - Strict classification: ETFs, Open-End Mutual Funds, Closed-End Funds (CEFs), with explicit ETN separation.
  - **The Prime Data Rule: Exchange Last Price vs Official Net Asset Value (NAV)**:
    - Traded market price and Net Asset Value (NAV) are separate financial concepts and never conflated or substituted.
    - Listed ETFs report continuous exchange quotes via Stage 41 Redis + Stage 39 ClickHouse.
    - Unlisted Open-End Mutual Funds report dated valuation close NAVs per unit without synthetic realtime trade quotes.
    - Realtime quote events (`market.quote.updated`) update trade prices for applicable ETFs without mutating official NAV.
  - Typed expense ratios (net vs gross, percentage scale) and reported AUM with explicit scope and as-of dates.
  - Verified benchmark relationships and management/sponsor links with verification badges.
  - High-density Bloomberg/OpenBB-inspired terminal interface with Fund Type Selector (`All`, `ETFs`, `Mutual Funds`, `CEFs`), filters, pagination, and detailed Fund Inspector.
  - Strict security and design policies: zero purple gradients, zero execution trading buttons, zero fake fund ratings or returns.
- **Endpoints**:
  - `GET /api/v1/markets/funds`: Paginated directory with typed filters.
  - `GET /api/v1/markets/funds/filters`: Authoritative filter options and counts.
  - `GET /api/v1/markets/funds/{instrument_entity_id}`: Deep fund overview with identifiers, venue, benchmark, and sponsor metadata.
- **Testing**:
  - Backend: `pytest apps/api/tests/markets/test_markets_funds.py` (19 test cases, 100% pass)
  - Frontend: `npx.cmd tsx --tsconfig apps/web/tsconfig.json --test apps/web/tests/markets-funds.test.ts` (10 test cases, 100% pass)
  - Regressions: Stage 56 (35 tests) and Stage 57 (45 tests) pass cleanly without regressions.
- **Documentation**: See `docs/ETF_FUNDS_MARKETS_V1.md`

## Foreign Exchange (FX) Markets V1 (Stage 59)
- **Status**: Implemented (`/markets/fx`)
- **Capabilities**:
  - Global Foreign Exchange intelligence, currency pair discovery, spot exchange rates, bid/ask analytics, and indicative currency conversion.
  - Base and quote currency semantics strictly enforced (`BASE/QUOTE` = units of quote per 1 unit of base).
  - Validated ISO 4217 fiat currency metadata registry.
  - Canonical Financial Instrument UUID authority (`instrument_entity_id`) and alias resolution.
  - Rate Kind classification: `SPOT_BID_ASK`, `INDICATIVE_MID`, `REFERENCE_RATE`, `LAST_TRADE`, `CROSSED_INVALID`.
  - Absolute spread, normalized basis points, and pair-specific pip conventions (0.01 for JPY & INR, 0.0001 for non-JPY).
  - Crossed market guards (`bid > ask` flagged as `CROSSED_INVALID`, spread null, midpoint null).
  - Indicative Currency Converter: Direct, Reverse, and Same-Currency (1:1) arithmetic with Python Decimal precision and destination minor unit rounding.
  - Strict no-triangulation guard: Unsupported cross-rates are rejected honestly without synthetic triangulation.
  - High-density Bloomberg/OpenBB-inspired terminal interface with Pair Directory Table, Pair Inspector, Currency Converter, and Coverage Summary.
- **Endpoints**:
  - `GET /api/v1/markets/fx`: Paginated FX pair directory with quotes and spreads.
  - `GET /api/v1/markets/fx/currencies`: Supported fiat currencies in the canonical catalog.
  - `GET /api/v1/markets/fx/{instrument_entity_id}`: Deep pair overview, orientation explanation, and currency metadata.
  - `POST /api/v1/markets/fx/convert`: Read-only indicative currency conversion.
- **Testing**:
  - Backend: `pytest apps/api/tests/markets/test_markets_fx.py` (20 test cases, 100% pass)
  - Frontend: `npx tsx --test apps/web/tests/markets-fx.test.ts` (12 test cases, 100% pass)
  - Regressions: Stage 56, 57, and 58 pass cleanly without regressions (47 web tests, 84 backend tests).
- **Documentation**: See `docs/FX_MARKETS_V1.md`

## Cryptocurrency Markets V1 (Stage 60)
- **Status**: Implemented (`/markets/crypto`)
- **Capabilities**:
  - Global cryptocurrency asset discovery, exchange-aware spot markets, digital asset intelligence, and professional market terminal.
  - Strict asset identity distinctions: Native currencies vs contract tokens, network identities, token standards, wrapped assets, and bridged tokens.
  - Base asset and quote asset semantics strictly enforced (`BASE/QUOTE` = units of quote per 1 unit of base).
  - Quote asset classification: Fiat currency vs cryptocurrency/stablecoin (never treating stablecoins as ISO USD or hardcoding 1:1 parity).
  - Exchange/venue-aware market isolation: Venue identity (Coinbase, Binance, Kraken, Bitstamp) preserved without cross-venue quote contamination or arbitrary multi-exchange volume aggregation.
  - Spot vs derivative boundaries: Strict exclusion of perpetual futures, dated futures, options, margin/leverage, and order-book ladders.
  - Authoritative quote metrics: Last trade, separate bid and ask, Decimal absolute spread, midpoint, basis points, and crossed market (`CROSSED_INVALID`) detection.
  - Rolling 24-hour change and volume with verified windows and explicit units (distinguishing base volume from quote volume).
  - Stage 44 freshness tracking and delay status (`REALTIME`, `DELAYED`, `STALE`, `UNKNOWN`, `OFFLINE`).
  - Read-only authenticated architecture: 0 writes, 0 background worker jobs, 0 upstream provider fanout on read.
  - High-density Bloomberg/OpenBB-inspired terminal workspace: Coverage Summary, Search & Filters, Spot Markets Directory Table, and Selected Market Inspector.
- **Endpoints**:
  - `GET /api/v1/markets/crypto`: Paginated crypto spot market directory with quotes, spreads, 24h change, and volume.
  - `GET /api/v1/markets/crypto/assets`: Supported canonical digital asset entities and classifications.
  - `GET /api/v1/markets/crypto/filters`: Authoritative filter options and counts.
  - `GET /api/v1/markets/crypto/{instrument_entity_id}`: Deep spot market overview with asset identity, venue variant, and source provenance.
- **Testing**:
  - Backend: `pytest apps/api/tests/markets/test_markets_crypto.py` (18 test cases, 100% pass)
  - Frontend: `npx tsx --test apps/web/tests/markets-crypto.test.ts` (11 test cases, 100% pass)
  - Regressions: Full Markets regression suite passes cleanly (102 backend tests across Overview, Equities, Funds, FX, and Crypto; 48 frontend tests).
- **Documentation**: See `docs/CRYPTOCURRENCY_MARKETS_V1.md`

## The 20 Modules
1. Home
2. Markets
3. Charts
4. Watchlists
5. Screeners
6. Companies
7. Economics
8. News
9. Research
10. Maps
11. Intelligence
12. Options
13. Trading
14. Portfolios
15. Risk
16. AI Assistant
17. Data
18. Saved
19. Workspaces
20. Agents



