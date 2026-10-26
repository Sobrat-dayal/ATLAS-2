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

## Bonds & Fixed-Income Markets V1 (Stage 61)
- **Status**: Implemented (`/markets/bonds`)
- **Capabilities**:
  - Global debt security discovery, sovereign and corporate debt markets, coupon intelligence, yield observations, clean/dirty pricing, and professional fixed-income terminal.
  - Canonical bond security identity: Universal UUID5 based on ISIN and symbol, strictly decoupled from legal debt issuer identity.
  - Verified debt issuers: Sovereign treasuries (US Treasury, UK DMO, Germany Finance Agency, Japan MoF), corporate issuers (Apple, Microsoft, JPMorgan, Pfizer), and supranational institutions (World Bank IBRD, European Investment Bank).
  - Contractual terms: Fixed, floating, and genuine zero-coupon schedules, coupon frequency, issue and dated dates, contractual maturity, perpetual debt, day-count conventions (`ACT/ACT ICMA`, `30/360`, `ACT/360`), and seniority.
  - Source-aware pricing conventions: Clean price, dirty price, and accrued interest strictly distinguished on compatible quotation bases (`% of par`, `price per 100 face`, absolute).
  - Typed yield observations: Source-provided YTM, YTC, YTW, and Discount Yield with explicit units and methodologies; full support for negative yields; yield changes expressed in basis points (bps).
  - Strict financial boundaries: Zero synthetic yield curves, zero duration/convexity engines, zero generalized YTM solvers, zero bond trading/RFQ execution, zero fabricated bond prices or credit ratings.
  - Read-only authenticated architecture: 0 database writes, 0 background worker jobs, 0 upstream provider fanout on read.
  - High-density Bloomberg/OpenBB-inspired terminal workspace: Coverage Summary, Search & Multi-Dimensional Filters, Bond Directory Table with keyset pagination, and Selected Bond Inspector.
- **Endpoints**:
  - `GET /api/v1/markets/bonds`: Paginated bond directory with clean prices, dirty prices, accrued interest, and typed yields.
  - `GET /api/v1/markets/bonds/filters`: Authoritative bond filter options and issuer categories.
  - `GET /api/v1/markets/bonds/{instrument_entity_id}`: Deep bond overview with contractual terms, price/yield breakdown, provenance, and non-executable OTC disclaimer.
- **Testing**:
  - Backend: `pytest apps/api/tests/markets/test_markets_bonds.py` (24 test cases, 100% pass)
  - Frontend: `npx tsx --test apps/web/tests/markets-bonds.test.ts` (11 test cases, 100% pass)
  - Regressions: Full Markets regression suite passes cleanly (126 backend tests across Overview, Equities, Funds, FX, Crypto, and Bonds; 69 frontend tests).
- **Documentation**: See `docs/BONDS_FIXED_INCOME_MARKETS_V1.md`

## Futures & Commodities Markets V1 (Stage 62)
- **Status**: Implemented (`/markets/futures`)
- **Capabilities**:
  - Global Commodity Intelligence, Exchange-Traded Futures, Contract Discovery, Settlement Data, Expiration Management, and Professional Derivatives Market Terminal.
  - Strict four-level financial instrument taxonomy: Commodity Underlying (reference physical asset/grade/region), Spot Benchmark (physical price assessment), Futures Product (standardized exchange family), and Individual Futures Contract (specific delivery/expiration period) are strictly decoupled and never conflated.
  - Exchange/venue-aware contract discovery: Authoritative listing exchanges (NYMEX, ICE, COMEX, CBOT, CME) with Market Identifier Codes (MIC: `XNYM`, `IFUS`, `XCEC`, `XCBT`, `XCME`) and venue-scoped symbol aliases.
  - Expiration and lifecycle management: Full year/month (`YYYY-MM`) semantics, standard month-code mapping (F through Z), genuine last trading days, notice days, and physical delivery windows. Expired contracts remain historically queryable without synthetic rollover.
  - Verified contract specifications: Contract size, physical size unit (barrels, troy ounces, bushels, metric tons, MMBtu), quote currency, quote scale, tick size, verified tick value per contract, and cash-settled vs. physically delivered classifications.
  - Market observation integrity: Last executed trade, official daily settlement (distinctly preserved with session trade date), volume (contracts traded in session), and open interest (clearinghouse reported open contracts with as-of date).
  - Negative futures price support: Full support for legitimate negative futures prices (e.g. historical WTI `CLK20` -$37.63 on 2020-04-20); percentage change suppressed when reference price $\le 0$.
  - Read-only derivatives terminal: 0 writes on read, 0 upstream provider fanout on read, no continuous futures/auto-roll, no contango/backwardation curves, no margin engine, no futures trading.
  - High-density Bloomberg/OpenBB-inspired terminal interface: Coverage Summary, Market Type Selector (`Futures Contracts`, `Commodities`, `Spot Benchmarks`), Search & Multi-Dimensional Filters, Contract Directory Table with keyset pagination, and Selected Contract Inspector.
- **Endpoints**:
  - `GET /api/v1/markets/futures/contracts`: Paginated futures contracts directory with quotes, settlements, volume, and open interest.
  - `GET /api/v1/markets/futures/contracts/{instrument_entity_id}`: Deep contract overview with specifications, lifecycle dates, market observations, and source provenance.
  - `GET /api/v1/markets/futures/commodities`: Paginated canonical commodity underlyings and linked futures products.
  - `GET /api/v1/markets/futures/commodities/{commodity_entity_id}`: Detail view of specific commodity underlying.
  - `GET /api/v1/markets/futures/spot-benchmarks`: Supported physical commodity spot benchmarks with location basis and assessment methodology.
  - `GET /api/v1/markets/futures/filters`: Authoritative filter options and counts across categories, exchanges, products, and months.
- **Testing**:
  - Backend: `pytest apps/api/tests/markets/test_markets_futures.py` (27 test cases, 100% pass)
  - Frontend: `npx tsx --test apps/web/tests/markets-futures.test.ts` (11 test cases, 100% pass)
  - Regressions: Full Markets regression suite passes cleanly (153 backend tests across Overview, Equities, Funds, FX, Crypto, Bonds, and Futures; 80 frontend tests).
- **Documentation**: See `docs/FUTURES_COMMODITIES_MARKETS_V1.md`

## Market Movers V1 (Stage 63)
- **Overview**: Dedicated market movement intelligence and professional terminal workspace located canonically at `/markets/movers` as a core subsection of Markets (Module 02).
- **Key Features**:
  - Defined Ranking Universes: `univ_us_equities` (Covered US Equities), `univ_crypto_spot` (Supported Crypto Spot Markets), `univ_futures` (Supported Futures Contracts).
  - Three Canonical Categories: `Top Gainers`, `Top Losers`, `Most Active`.
  - Financial Qualification Pipeline:
    - Decimal arithmetic (`percent_change` and `absolute_change`) computed before sorting.
    - Zero denominator protection: non-positive reference prices excluded with `INVALID_DENOMINATOR`.
    - Zero price changes strictly excluded from both Top Gainers and Top Losers.
    - Missing volume strictly excluded from Most Active (missing is never fabricated as zero).
    - Deterministic tie-breaking using canonical instrument UUID.
  - Institutional Coverage Transparency (`MoverCoverage`):
    - Reports universe size, candidates evaluated, qualified count, excluded count, typed exclusion reasons dictionary, and coverage status (`COMPLETE_FOR_DEFINED_UNIVERSE` vs. `PARTIAL_COVERAGE`).
    - Truthful scope labeling: never claims global/worldwide coverage for catalog-bounded rankings.
  - High-Density Bloomberg/OpenBB Terminal Interface:
    - Header with snapshot as-of timestamp and refresh trigger.
    - Universe & Comparison Window selectors.
    - Category tabs (Gainers, Losers, Most Active with explicit activity unit label).
    - Venue filters and coverage summary with expandable exclusion breakdown.
    - Dense Leaderboard Table with tabular numerals, ordinal ranks, and click-to-inspect row selection.
    - Selected Mover Inspector with canonical UUID, series key, observation breakdown, and deep links to `/charts` and asset-class directories.
  - Read-only guarantees: 0 writes to database or cache, 0 external provider fanout on read, no trading actions, no AI commentary.
- **Endpoints**:
  - `GET /api/v1/markets/movers`: Paginated qualified market movers ranking snapshot.
  - `GET /api/v1/markets/movers/universes`: Available, authorized mover universes.
  - `GET /api/v1/markets/movers/metrics`: Valid ranking metrics and observation windows for a universe.
- **Testing**:
  - Backend: `pytest apps/api/tests/markets/test_markets_movers.py` (9 comprehensive test cases, 100% pass)
  - Frontend: `pnpm dlx tsx --test apps/web/tests/markets-movers.test.ts` (10 test cases, 100% pass)
  - Regression: Full Markets regression suite passes cleanly (162 backend tests across Overview, Equities, Funds, FX, Crypto, Bonds, Futures, and Movers; 90 frontend tests).
- **Documentation**: See `docs/MARKET_MOVERS_V1.md`

## Market Heatmaps V1 (Stage 64)
- **Overview**: Dedicated market performance visualization, sector & industry treemaps, and real-time market intelligence workspace located canonically at `/markets/heatmaps` within Markets (Module 02).
- **Key Features**:
  - Two Distinct Visualization Modes:
    - `Equal-Size Performance Heatmap` (`equal_size`): Every qualified instrument receives an identical layout area fraction ($1 / N$). Tile area has zero financial weight meaning. Operates reliably as an institutional baseline even without market cap data.
    - `Size-Weighted Market Treemap` (`market_cap_weighted`): Tile area is strictly proportional to verified, strictly positive market capitalization ($w_i / \sum w$). If capitalization is unsupported (e.g. Futures), weighted mode is disabled and clearly explained—never silently fall back to equal size while claiming market-cap weighting.
  - Mathematical Qualification & Return Calculation:
    - Decimal arithmetic for price return percentage: $((P_{\text{current}} - P_{\text{reference}}) / P_{\text{reference}}) \times 100$.
    - Missing returns are **never** colored or reported as zero percent.
    - Zero/negative reference prices are excluded with `INVALID_DENOMINATOR`.
    - Missing quotes are excluded with `NO_CURRENT_QUOTE`.
    - Missing weights in weighted mode are excluded with `MISSING_WEIGHT`.
  - Diverging Financial Performance Color Scale:
    - Domain `[-5.0%, +5.0%]`: Green family for positive returns, neutral zinc for flat/zero, red family for negative returns.
    - Extreme returns (> +5% or < -5%) saturated at domain boundary colors while preserving exact numeric returns.
    - Distinct unavailable pattern for missing/excluded observations.
  - GICS Sector & Industry Taxonomy:
    - Grouping into Technology, Consumer Cyclical, Communication Services, Financial Services, Healthcare, Energy, and Unclassified.
    - Group aggregate returns explicitly labeled: Equal-weight mean ($\sum r_i / n$) vs. Cap-weighted return ($\sum w_i r_i / \sum w_i$).
    - Marked explicitly as "Based on qualified ATLAS constituents", never claimed as an official market index.
  - Squarified Treemap Layout Engine:
    - Pure squarified algorithm generating non-overlapping, aspect-ratio-optimized rectangles.
    - Dynamic responsiveness with `ResizeObserver`.
    - Tiny tile handling: tiles smaller than 52px width or 36px height suppress long text to prevent visual clutter while preserving full hover, focus, click, and inspector access.
  - Interactive Terminal Interface:
    - Universe selector, comparison window selector, weighting mode toggle, and hierarchy mode toggle.
    - Coverage transparency summary with candidate count, qualified count, missing counts, total capitalization, and coverage status badge.
    - Sector container headers with aggregate returns and click-to-drilldown navigation with breadcrumbs.
    - Selected Tile Inspector with canonical UUID (Stage 17), series key, pricing, capitalization, taxonomy, and quick navigation links ("Open Charts", "Open Market", "Open Company").
    - Accessible semantic HTML data table alternative for screen-reader users.
  - Read-Only Invariants: 0 writes to database or cache, 0 external provider RPC calls on read, 0 trading actions, 0 autonomous agents.
- **Endpoints**:
  - `GET /api/v1/markets/heatmaps`: Coherent calculation snapshot with coverage and nodes/groups.
  - `GET /api/v1/markets/heatmaps/universes`: Available, authorized heatmap universes.
  - `GET /api/v1/markets/heatmaps/options`: Supported visualization modes, hierarchies, and comparison windows.
- **Testing**:
  - Backend: `pytest apps/api/tests/markets/test_markets_heatmaps.py` (14 comprehensive test cases, 100% pass).
  - Frontend: `pnpm dlx tsx --test apps/web/tests/markets-heatmaps.test.ts` (9 test cases, 100% pass).
  - Regressions: Full Markets regression suite passes cleanly (176 backend tests across Overview, Equities, Funds, FX, Crypto, Bonds, Futures, Movers, and Heatmaps; 99 frontend tests).
- **Documentation**: See `docs/MARKET_HEATMAPS_V1.md`

## Cross-Asset Markets V1 (Stage 65)
- **Overview**: Dedicated multi-asset market intelligence and comparative terminal workspace at `/markets/cross-asset` (Markets Module 02).
- **Core Principles & Capabilities**:
  - **Native Market Overview**: Preserves individual financial asset-class quotation conventions without conflating incompatible measurements:
    - Equities: Regular-session traded price and % change vs previous official close.
    - ETFs: Exchange market price % change (explicitly distinguished from NAV).
    - FX: Spot rate change % with directional pair orientation.
    - Crypto: Continuous 24/7 rolling 24-hour return in quoted denomination.
    - Bonds: Benchmark yield level in % and yield change in basis points (`bps`), strictly separated from equity price returns.
    - Futures: Last traded price vs prior settlement in contractual units.
  - **Aligned Price Performance**: Common UTC window (`last_24h`, `last_7d`, `last_30d`) with strict temporal alignment, zero look-ahead bias (effective start <= requested start), maximum tolerance enforcement (<= 7200s), and Decimal price returns. Yield-only series excluded with `UNSUPPORTED_METRIC`.
  - **Benchmark vs Proxy Disclosures**: Authoritative index benchmarks clearly distinguished from exchange-traded ETF and Futures proxies (`SPY`, `QQQ`, `ESZ26`).
  - **Coverage & Exclusion Reporting**: Truthful coverage accounting (`requested`, `evaluated`, `qualified`, `excluded`, and typed reason breakdown).
  - **Interactive Terminal Workspace**: Universe selector, analytical mode toggle, window selector, coverage summary, multi-asset grid cards, institutional comparison table, selected instrument inspector, and collapsible methodology panel.
  - **Read-Only Invariants**: 0 database writes, 0 quote writes, 0 upstream provider RPC calls on read, 0 trading actions, 0 autonomous agents.
- **Endpoints**:
  - `GET /api/v1/markets/cross-asset`: Coherent calculation snapshot with coverage, asset-class sections, comparison table, and exclusions.
  - `GET /api/v1/markets/cross-asset/universes`: Available canonical multi-asset universes.
  - `GET /api/v1/markets/cross-asset/options`: Supported analytical modes, comparison windows, and alignment parameters.
- **Testing**:
  - Backend: `uv run pytest tests/markets/test_markets_cross_asset.py` (13 test cases, 100% pass).
  - Frontend: `pnpm dlx tsx --test apps/web/tests/markets-cross-asset.test.ts` (9 test cases, 100% pass).
  - Regressions: Full Markets regression suite passes cleanly (189 backend tests across Overview, Equities, Funds, FX, Crypto, Bonds, Futures, Movers, Heatmaps, and Cross-Asset; 108 frontend tests).
- **Documentation**: See `docs/CROSS_ASSET_MARKETS_V1.md`

## Charts V1 (Stage 66)
- **Overview**: Dedicated institutional financial charting workspace at `/charts` (Canonical Module 03), providing real historical candlestick rendering, close-line visualization, and canonical financial instrument exploration.
- **Core Principles & Capabilities**:
  - **Lightweight Charts Engine**: Powered by open-source TradingView Lightweight Charts (`lightweight-charts@5.2.1`, Apache 2.0). Client-only rendering, robust SSR boundary with Suspense, auto-resize via `ResizeObserver`, theme token synchronization, and explicit cleanup to prevent leaks.
  - **Canonical OHLCV Integration**: Consumes canonical stored market bars from ClickHouse (`historical_market_bars_versions FINAL`) with logical-latest revision selection and strict chronological ordering.
  - **Strict Financial Data Integrity**:
    - Strict OHLC envelope validation (`high >= max(open, close, low)` and `low <= min(open, close, high)`).
    - Support for valid negative commodity futures prices (e.g. WTI Crude `CLZ26`).
    - Asset-class-specific volume semantics (OTC FX and Sovereign Debt evaluated prices report volume as `None` / `—`, never synthetic zero).
    - Single verified baseline interval: `1D` (daily bars); requests for other intervals are cleanly rejected and deferred to Stage 68.
    - Zero synthetic bar generation, zero intraday fabrication from daily, and zero synthetic continuous futures rolls.
  - **Interactive Terminal Workspace**:
    - Multi-asset instrument selector across Equities (`AAPL`, `MSFT`, `NVDA`), ETFs (`SPY`, `QQQ`), FX (`EURUSD`, `USDJPY`), Crypto (`BTCUSDT`, `ETHUSDT`), Bonds (`US10Y`), and Futures (`CLZ26`, `GCZ26`, `ESZ26`).
    - Rendering mode toggle: Candlestick vs Close Line.
    - Viewport controls: Reset View, Fit Content, Refresh history.
    - Interactive crosshair inspection: Live `Date`, `Open`, `High`, `Low`, `Close`, `Volume`, and `Change%` metrics.
    - Bounded incremental older-history backfill on horizontal scroll.
    - Accessible, paginated historical data table for screen-reader and keyboard users.
    - Deep linking support via URL query parameters (`/charts?symbol=BTCUSDT` or `/charts?instrument_id=<uuid>`).
  - **Read-Only Invariants**: 0 database writes, 0 quote writes, 0 ClickHouse writes, 0 upstream provider calls on read, 0 trading executions, 0 LLM calls.
- **Endpoints**:
  - `GET /api/v1/charts/instruments`: Catalog of verified chartable instruments and metadata.
  - `GET /api/v1/charts/instruments/{id}`: Detailed instrument metadata.
  - `GET /api/v1/charts/history`: Authenticated, bounded historical bars with coverage and pagination.
- **Testing**:
  - Backend: `uv run pytest tests/test_charts_v1.py` (15 test cases, 100% pass).
  - Frontend: `pnpm dlx tsx --test tests/charts-v1.test.ts` (9 test cases, 100% pass).
  - Regressions: Full Markets regression suite passes cleanly (189 backend tests, 242 frontend tests).
- **Documentation**: See `docs/CHARTS_V1.md`

## Live Chart Streaming V1 (Stage 67)
- **Overview**: Transforms ATLAS Charts into a live-capable institutional financial charting workstation at `/charts`, integrating real-time market data streaming, Redis/Valkey latest Quote state (Stage 41), typed Market Events (Stage 42), authenticated frontend WebSockets (Stage 43), and market data freshness classification (Stage 44).
- **Core Principles & Capabilities**:
  - **Canonical Instrument & Series Subscriptions**: Live subscriptions bound to canonical `instrument_entity_id` UUIDs and market-series dimensions, preventing cross-venue or cross-listing Quote pollution.
  - **Initial State Bootstrap & Race Reconciliation**: Authenticated initial Quote state fetch via `GET /api/v1/charts/live-state` combined with bounded bootstrap event buffering (max 50 events) to deterministically resolve HTTP/WebSocket races.
  - **Genuine Live Last-Price Overlay**: TradingView Lightweight Charts price line and price-axis marker displaying verified Last-price execution without mutating historical OHLC candles.
  - **Strict Financial Integrity**:
    - Distinguishes Quote snapshots from executed trade feeds and authoritative OHLC bars.
    - Never fabricates Open, High, Low, Close, or Volume from sparse Quote samples.
    - Never converts indicative Bid/Ask or midpoint into an executed Last price.
    - Never derives trading Volume from Quote event counts.
    - Preserves negative commodity futures prices (e.g. `CLZ26` WTI Crude Oil) without zero-clamping.
  - **Interactive Terminal Live Controls**:
    - Functional Pause / Resume Live Updates toggle with bounded memory guarantees.
    - "Go to Latest" viewport recentering with automatic Follow-Live decoupling during manual historical panning.
    - Live Market Data Status bar with dual-state modeling: transport connection (`CONNECTED`, `CONNECTING`, `RECONNECTING`, `DISCONNECTED`) and market data freshness (`LIVE`, `DELAYED`, `STALE`, `UNKNOWN`).
    - High-density Latest Quote Details panel showing Last, Bid/Ask, Spread (bps), and quotation units.
  - **Render Coalescing & Backpressure**: Coalesced update scheduler (100ms cadence) maintaining 60fps canvas interaction under market tick bursts.
  - **Read-Only Invariants**: 0 database writes, 0 ClickHouse writes, 0 upstream provider calls on read, 0 trading executions, 0 LLM calls.
- **Endpoints**:
  - `GET /api/v1/charts/live-state`: Authenticated, entitlement-enforced latest quote state reading Stage 41 Redis authority.
- **Testing**:
  - Backend: `uv run pytest tests/test_charts_live_streaming.py` (17 test cases, 100% pass). Full charts suite: 32/32 pass.
  - Frontend: `npx.cmd tsx --test tests/charts-live-streaming.test.ts` (13 test cases, 100% pass). Full web suite: 255/255 pass.
  - Regressions: Clean execution across Stage 66 Charts V1 and prior market modules.
- **Documentation**: See `docs/LIVE_CHART_STREAMING.md`

## Advanced Chart Intervals & Chart Types V1 (Stage 68)
- **Overview**: Upgrades ATLAS Charts at `/charts` to a full multi-timeframe institutional charting interface supporting 9 canonical intervals (`1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`, `1M`), truthful availability discovery, mathematical & temporal Decimal OHLCV aggregation, 4 professional chart types (Candlestick, OHLC Bar, Line, Area), and multi-interval live streaming compatibility.
- **Core Principles & Capabilities**:
  - **Canonical Multi-Timeframe Intervals**: Stable typed interval identifiers (`1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`, `1M`) separating bar aggregation granularity from viewport time range.
  - **Truthful Availability Discovery**: `GET /api/v1/charts/intervals` endpoint providing instrument-specific availability (`AVAILABLE_NATIVE`, `AVAILABLE_DERIVED`, `PARTIAL`, `UNAVAILABLE`) with explicit unavailability reasons (e.g. daily-only providers or missing constituent bars).
  - **Mathematical & Temporal Decimal Aggregation**:
    - `OPEN` = first bar open, `HIGH` = max high, `LOW` = min low, `CLOSE` = last bar close.
    - Strict envelope checks: `high >= max(open, close)` and `low <= min(open, close)`.
    - Genuine Volume semantics: sums volume only if all constituent bars have valid volume; otherwise `None` (never synthetic 0).
    - Session-aware ISO week (`1w`) and calendar month (`1M`) boundaries.
    - Preserves negative commodity futures prices (`CLZ26` WTI Crude).
    - Distinguishes finalized historical bars from provisional open-period aggregates.
  - **4 Professional Chart Renderers**:
    - Candlestick (`candlestick`): Up/down candles with wick and body styling.
    - OHLC Bar (`bar`): Classical vertical high-low spine with left-open and right-close ticks.
    - Line (`line`): Crisp close-price line with zero artificial curve smoothing.
    - Area (`area`): Close-price line with translucent gradient fill and adaptive baseline scaling.
  - **Interactive Workspace UI**:
    - Compact segmented Interval Selector with tooltips on disabled timeframes.
    - Segmented Chart-Type Selector.
    - Accessible HTML table alternative with interval and lineage context.
    - Rapid interval switching protection with query cancellation (`AbortController`).
  - **Stage 67 Live Compatibility**:
    - Genuine Last-price overlay persists seamlessly across all intervals.
    - Live candle updates are interval-specific; prevents cross-interval contamination.
  - **Read-Only Invariants**: 0 database writes, 0 ClickHouse writes, 0 upstream provider calls on read, 0 trading executions, 0 LLM calls.
- **Endpoints**:
  - `GET /api/v1/charts/intervals`: Available intervals and capabilities for selected instrument.
  - `GET /api/v1/charts/history`: Authenticated, interval-aware historical bars with target-bar pagination and lineage metadata.
- **Testing**:
  - Backend: `uv run pytest apps/api/tests/test_charts_intervals_and_types.py` (17 tests, 100% pass). Full charts suite: 49/49 pass.
  - Frontend: `npx.cmd tsx --test apps/web/tests/charts-intervals-and-types.test.ts` (8 tests, 100% pass). Full web suite: 263/263 pass across 42 suites.
  - Production build: `npm.cmd run build` in `apps/web` compiled with 0 errors across all 38 routes.
- **Documentation**: See `docs/CHART_INTERVALS_AND_TYPES.md`

## Technical Indicator Infrastructure V1 (Stage 69)
- **Mathematical Integrity**: Provides the extensible, typed, deterministic calculation engine for technical indicators in `/charts`:
  - **Indicator Registry (`IndicatorRegistry`)**: Server-controlled allowlist of versioned indicator definitions. Strictly prohibits user-submitted executable code (`eval`, `exec`).
  - **Reference Implementation (`atlas.sma` v1)**: Deterministic Simple Moving Average using $O(N)$ rolling-sum accumulation and high-precision Python `Decimal` arithmetic.
  - **Warmup & Lookback Policy**: First $N-1$ points are output as `WARMUP` with `value = None`. Never zero-fills or synthesizes warmup values.
  - **Zero Look-Ahead**: Mathematical transformation at bar $T$ depends only on qualified observations $\le T$.
  - **Data Continuity**: Detects and tags data gaps without silent forward-filling or interpolation.
  - **Chart Overlays**: Synchronizes indicator instances as dedicated `LineSeries` on the primary canvas without mutating candlestick bars. Supports multiple concurrent instances (e.g., SMA 20 and SMA 50).
  - **Subpane Infrastructure**: Extensible attached subpane container contract for future Stage 70 oscillators.
  - **Interactive Workspace UI**:
    - `IndicatorPicker`: Modal to discover registered definitions, search by category, and inspect parameter specifications.
    - `ActiveIndicators`: Legend strip displaying active indicators, dynamic values, visibility toggles, and remove actions.
    - `IndicatorParameterEditor`: Inline dialog enforcing integer bounds (2–500), stroke colors, and line widths.
    - `ChartCrosshairDetails`: Displays time-aligned indicator values at hovered candles for exact inspection and accessibility.
  - **Multi-Stage Integration**: Fully compatible with Stage 66 historical backfill, Stage 67 live streaming, and Stage 68 multi-timeframe intervals.
  - **Strict Security**: 0 user-submitted code, 0 canonical database writes, 0 upstream provider calls on read, 0 trading executions, 0 LLM calls.
- **Endpoints**:
  - `GET /api/v1/charts/indicators/catalog`: Allowlisted indicator definitions, parameter schemas, and capabilities.
  - `GET /api/v1/charts/indicators/{indicator_id}`: Detailed specification for an indicator.
  - `POST /api/v1/charts/indicators/calculate`: Authenticated calculation endpoint with resource bounds (max 5 instances, max 2,000 bars, max lookback).
- **Testing**:
  - Backend: `uv run pytest apps/api/tests/test_charts_indicators.py` (14 tests, 100% pass). Full charts suite: 63/63 pass.
  - Python lint & format: `uv run ruff check` and `uv run ruff format --check` (0 errors).
  - Frontend: `npx.cmd tsx --test apps/web/tests/charts-indicators.test.ts` (10 tests, 100% pass). Full web charts suite: 40/40 pass.
  - TypeScript: `npx.cmd tsc --noEmit` passed with 0 errors.
  - ESLint: passed with 0 errors.
  - Production build: `npm.cmd run build` in `apps/web` compiled with 0 errors across all 38 routes.
- **Documentation**: See `docs/TECHNICAL_INDICATOR_INFRASTRUCTURE.md`

## TA-Lib Technical Analysis Engine & Oscillator Panes (Stage 70)
- **Institutional Technical Studies**: Extends the Stage 69 framework with the TA-Lib C-library computation backend and pure-Python reference implementations across 14 canonical studies:
  - **Trend**: SMA, EMA, WMA, DEMA, TEMA, MACD (12, 26, 9)
  - **Momentum**: RSI, Stochastic (14, 3, 3), ROC, CCI, Williams %R
  - **Volatility**: Bollinger Bands (20, 2), ATR
  - **Volume**: OBV
- **Multi-Output Overlays & Subpanes**:
  - Primary canvas multi-series overlays for Bollinger Bands (Upper, Middle, Lower).
  - Dedicated Lightweight Charts subpanes for oscillators (RSI, MACD, Stochastic) with reference levels (e.g., 30/70 for RSI, 20/80 for Stochastic).
  - Synchronized crosshair tracking across primary chart and all active oscillator subpanes.
- **Testing & Verification**:
  - Full parity with official TA-Lib reference values.
  - Test suites: `apps/web/tests/charts-talib-indicators.test.ts` (10/10 pass).
- **Documentation**: See `docs/TALIB_TECHNICAL_INDICATORS.md`

## Professional Chart Drawing Tools V1 (Stage 71)
- **Financial Coordinate Anchoring**: Every drawing is anchored strictly to canonical financial coordinates `{ time, price }`, never transient screen pixels or mutable bar indices. Dynamic re-projection maintains anchor stability during chart panning, zooming, and resizing.
- **9 Canonical Interactive Drawing Tools**:
  - `trendline`: 2-anchor directional segment with endpoint and whole-line dragging.
  - `horizontal_line`: 1-anchor infinite price level across chart width with right price badge.
  - `horizontal_ray`: 1-anchor level extending rightward from start coordinate.
  - `vertical_line`: 1-anchor infinite vertical date/time marker with bottom timestamp badge.
  - `rectangle`: 2-anchor zone highlighting price and time area with configurable fill opacity.
  - `price_range`: 2-anchor vertical measurement ($\Delta P$, $\Delta P\%$, quotation units).
  - `time_range`: 2-anchor horizontal measurement (elapsed calendar time, canonical bar count).
  - `price_time_measure`: Combined vector and bounding box with price & time metrics.
  - `fibonacci_retracement`: 2-anchor direction-preserving Fibonacci levels ($0\%, 23.6\%, 38.2\%, 50\%, 61.8\%, 78.6\%, 100\%$).
- **Smart Snapping Engine**:
  - Snaps to genuine canonical OHLC observations (`OFF`, `NEAREST_BAR`, `OHLC`).
  - Screen-space pixel tolerance (15px) with `Shift`/`Alt` keyboard modifier override.
- **Command-Based Undo / Redo**:
  - 1 continuous pointer drag = 1 atomic history command.
  - Immediate redo invalidation on new actions; bounded history (100 commands).
  - Keyboard shortcuts: `Ctrl+Z` / `Cmd+Z` (Undo), `Ctrl+Shift+Z` / `Ctrl+Y` (Redo), `Del` / `Backspace` (Delete), `Esc` (Cancel / Deselect).
- **Accessibility & Numerical Editing**:
  - `DrawingManager`: Slide-out drawer listing all session drawings with type, anchors, lock, visibility, and delete actions.
  - `DrawingCoordinateEditor`: Accessible numerical input dialog for precision financial price and timestamp editing.
- **Session State Isolation**:
  - Drawings are isolated by instrument context `[instrument_entity_id : price_basis]`.
  - In-memory session preservation allows switching instruments and returning without losing drawings.
  - Cloud layout persistence deferred to Stage 74.
- **Testing & Verification**:
  - `apps/web/tests/charts-drawing-tools.test.ts`: 10/10 tests pass (models, geometry, fibonacci, measurements, snapping, history, isolation).
  - Full TypeScript typecheck and Next.js production build pass across all 38 routes with 0 errors.
- **Documentation**: See `docs/CHART_DRAWING_TOOLS.md`

## Professional Multi-Chart Layouts V1 (Stage 72)
- **Multi-Chart Workspace Architecture**:
  - Transforms `/charts` into an institutional multi-chart financial workstation supporting up to 4 simultaneous independently configured chart panels.
  - **6 Canonical Layout Presets**:
    - `single`: 1 full workspace chart
    - `two-columns`: 2 side-by-side charts (horizontal split)
    - `two-rows`: 2 vertically stacked charts (vertical split)
    - `three-left-focus`: 1 large primary chart left (60%), 2 stacked on right (40%)
    - `three-top-focus`: 1 large primary chart top (60%), 2 side-by-side below (40%)
    - `four-grid`: 2x2 grid of 4 independent charts
  - **Layout Selector Component**: Compact dropdown in toolbar featuring SVG mini-diagrams for all 6 presets, accessible hotkeys, and tooltips.
- **Strict Panel Independence**:
  - Independent instruments and market series per panel (e.g. Panel 1: SPY, Panel 2: BTCUSDT, Panel 3: EURUSD, Panel 4: AAPL).
  - Independent intervals (`1m`, `5m`, `15m`, `1h`, `1D`, `1W`).
  - Independent chart types (`candlestick`, `bar`, `line`, `area`).
  - Independent viewports, zoom, pan, and crosshair inspection.
  - Independent TA-Lib indicators and attached oscillator subpanes.
  - Independent drawing sessions (`DrawingSessionStore.getForPanel(panelId)`) with isolated undo/redo stacks.
- **Active Panel Management**:
  - Explicit active panel state (`activePanelId`) with visual cyan outline (`border-cyan-500/80 ring-1 ring-cyan-500/40`) and header badge.
  - Toolbar controls and Global Search target the active panel without modifying inactive panels.
  - Synchronizes active panel entity to global `SelectedEntity` without circular feedback loops.
- **Shared Market Data Infrastructure**:
  - `ChartQueryCache`: Centralized query cache deduplicating identical historical OHLCV requests across panels with in-flight request merging and bounded LRU eviction.
  - `SharedChartSubscriptionManager`: Central WebSocket subscription manager reference-counting active series across panels. When multiple panels display the same series, 1 shared connection is reused; pausing one panel does not pause others.
- **Resizable Splitters & Responsive Design**:
  - `AtlasSplit` / `react-resizable-panels` integration with horizontal and vertical drag handles and keyboard arrow resizing.
  - Minimum panel constraints enforced (~320px width, ~220px height) preventing collapsed panels.
  - Responsive mobile tab fallback (`[P1 SPY] [P2 BTCUSDT] [P3 EURUSD] [P4 AAPL]`) for screens <768px, preserving underlying multi-chart layout state.
- **Testing & Verification**:
  - `apps/web/tests/charts-multi-layout.test.ts`: 10/10 tests pass (layout registry, panel stability, active panel focus, instrument/interval isolation, drawing isolation, shared caching, reference counting, responsive modes, security).
  - All Stage 66-71 regression test suites pass with 0 regressions.
  - Full TypeScript typecheck (`npx tsc --noEmit`) and Next.js production build (`npm run build`) pass across all 38 routes.
- **Documentation**: See `docs/MULTI_CHART_LAYOUTS.md` and `docs/DECISIONS.md`.

## Professional Chart Synchronization V1 (Stage 73)
- **Chart Synchronization Engine**:
  - Transforms ATLAS Multi-Chart Workspaces into an institutional-grade synchronized financial analysis workspace at `/charts`.
  - Implements a high-performance local synchronization controller (`ChartSyncController`) and session-level group store (`ChartSyncStore`) with zero external broker or server message bus overhead.
- **Intelligent Synchronization Groups**:
  - Bounded session-level groups (`Group A`, `Group B`, etc.) supporting up to 4 member panels per group.
  - **100% Opt-In / Independent by Default**: All chart panels initialize in strictly independent mode; zero synchronization occurs until explicitly enabled by the user.
  - Policy: In V1, each panel belongs to at most one synchronization group at a time to prevent conflicting updates.
  - Safe group lifecycle: create, rename, toggle individual properties, pause/enable, delete, and "Align Group to Active Panel".
- **Fine-Grained Per-Property Controls**:
  - `crosshair`: Synchronizes vertical time cursor across panels at canonical UTC timestamp.
  - `visibleTimeRange`: Synchronizes horizontal pan and zoom with coverage clamping.
  - `instrument`: Links canonical financial instrument UUID and market series selection.
  - `interval`: Synchronizes timeframe (`1m`, `5m`, `15m`, `1h`, `1d`, `1w`, `1M`) respecting series-specific availability.
  - `chartType`: Synchronizes `candlestick`, `bar`, `line`, or `area` presentation modes.
  - `drawings`: Optional compatible drawing synchronization gated to identical canonical series and quotation units.
- **Loop-Free Event Propagation**:
  - Strong distinction between `USER` actions and `SYNC_APPLIED` programmatic updates.
  - Token-based suppression window (`LoopPreventionCoordinator`) absorbs chart library callbacks and prevents infinite retransmission (`A -> B -> A`).
  - Monotonic sequence ordering and LRU duplicate event protection reject duplicate or out-of-order events.
  - Group revision tokens invalidate in-flight events when group membership or settings change.
- **Linked Crosshairs & Multi-Market Calendar Alignment**:
  - High-precision timestamp synchronization using canonical UTC Unix seconds (never candle index or raw screen X pixels).
  - High-frequency pointer motion coalesced via `requestAnimationFrame` to eliminate UI rerender storms.
  - Renders `<LinkedCrosshairOverlay />` with vertical dashed guide line and bottom timestamp badge.
  - Crosshair leave cleans up temporary ghost guides immediately.
  - Multi-market calendar awareness: crypto 24/7 continuous trading vs US equity sessions without fabricating fake bars or synthetic OHLC tooltips.
- **Linked Visible Time Ranges (Pan & Zoom)**:
  - Synchronizes horizontal time axis scrolling and zooming across compatible members.
  - Destination coverage clamping: charts with shorter history clamp safely without bouncing clamped range back to the source chart.
  - Vertical price scales remain strictly independent (autoscaled to each instrument's price range).
- **Linked Instruments, Intervals & Types**:
  - Preflight entitlement verification prevents unauthorized market data access.
  - Partial failures reported explicitly; target panels preserve existing instruments rather than silently substituting symbols or providers.
  - Target panels recalculate indicators from new series data; drawing contexts remain isolated.
  - Series availability check verifies supported intervals without artificial data resampling.
- **Frontend UI & Accessibility**:
  - Compact `ChartSyncButton` in top workspace toolbar alongside `ChartLayoutSelector`: `[Sync: Group A (2 linked)]` or `[Sync: Independent]`.
  - Institutional popover `ChartSyncMenu` with group selector tabs, panel checkboxes, per-property switches, and quick actions.
  - Per-panel header badge: `[P1] [LINK A]` or `[P2] [IND]`.
- **Testing & Verification**:
  - `apps/web/tests/charts-synchronization.test.ts`: 10/10 tests pass (group models, default independence, sequence ordering, loop prevention, crosshairs, calendar alignment, range clamping, instrument linking, interval checks, drawing gates, security invariants).
  - All 80 automated tests across Stages 66 to 73 pass with 0 regressions.
  - Full TypeScript typecheck (`npx tsc --noEmit`) and Next.js production build (`npm run build`) pass across all 38 routes.
- **Documentation**: See `docs/CHART_SYNCHRONIZATION.md` and `docs/DECISIONS.md`.

## Saved Chart Layouts V1 (Stage 74)
- **Persistent Professional Chart Workspaces**:
  - Full multi-chart workspace serialization and hydration across `/charts`.
  - Persists grid presets (`single`, `two-columns`, `two-rows`, `three-left-focus`, `three-top-focus`, `four-grid`), panel order, split ratios, canonical instrument UUIDs, intervals, chart types, TA-Lib indicator parameters, Stage 71 financial-coordinate drawings, and Stage 73 synchronization groups.
- **PostgreSQL JSONB Layout Persistence**:
  - Authoritative database storage in `chart_layouts` table via Alembic migration (`stage74_chart_layouts`).
  - Owner-scoped tenant isolation (`owner_user_id`), unique case-insensitive normalized names, and optional default layout support.
  - Strict payload size ceiling (< 512 KiB) and recursive scanning rejecting forbidden tokens/credentials or raw market data arrays.
- **Optimistic Concurrency Control**:
  - Monotonic revision incrementing on every document mutation.
  - HTTP `ETag` and `If-Match` conditional updates via atomic compare-and-swap SQL operations.
  - Interactive `<LayoutConflictDialog />` on 412 Precondition Failed, offering non-destructive recovery ("Save As New", "Reload Latest", "Cancel").
- **Strict Serialization Allowlist**:
  - Explicit serializer (`serializeChartWorkspace`) strictly excludes raw OHLCV arrays, live quotes, calculated indicator points, DOM objects, React refs, and WebSocket instances.
  - Pure hydration pipeline (`hydrateChartWorkspace`) restores workspaces with an origin suppression token preventing cascade synchronization loops.
- **Portable Import / Export**:
  - Secure envelope format (`atlas_chart_layout` v1) with sanitized metadata, payload inspection, and owner reassignment.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_chart_layouts.py` (27/27 passed). All 97 backend tests across Stages 66 to 74 pass in ~10.7s.
  - Frontend tests: `apps/web/tests/charts-saved-layouts.test.ts` (10/10 passed). All 90 frontend tests across Stages 66 to 74 pass.
  - Quality gates: Ruff 0 errors, TypeScript typecheck 0 errors, Next.js build 100% successful.
- **Documentation**: See `docs/SAVED_CHART_LAYOUTS.md` and `docs/DECISIONS.md`.

## Historical Chart Replay V1 (Stage 75)
- **Deterministic Historical Playback Engine**:
  - Candle-by-candle historical playback inside `/charts` for studying real past market conditions.
  - Ephemeral authenticated replay sessions bound to a single Stage 72 panel (`panel_id`).
  - Monotonic playback speeds: 0.5x, 1.0x, 2.0x, 5.0x, 10.0x bars/sec.
  - Play, Pause, Step Forward (+1 bar), Step Backward (-1 bar), Restart, Seek, and End-of-Data handling.
- **Strict Future-Data Boundary Gating (No Look-Ahead)**:
  - Visible data is physically bounded to observations $\le \text{cursor\_index}$.
  - Bars $N+1$ and later are strictly excluded from the rendered chart, price autoscaling, candlestick geometries, volume histograms, indicator calculations, legends, tooltips, and crosshair inspection.
  - Visual masking workarounds are prohibited; future data is physically gated.
- **Replay-Aware Technical Indicators**:
  - Reuses Stage 69 Indicator Registry and Stage 70 TA-Lib production calculators.
  - Indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV) calculate strictly over revealed history.
  - Stepping backward removes future indicator points and deterministically restores prior cursor values.
- **Live / Replay Separation**:
  - Live quote overlays and current market ticks are strictly suppressed on the replayed panel.
  - Non-replayed panels in multi-chart workspaces continue normal live streaming.
  - Global WebSocket (Stage 43) is preserved and unharmed.
  - Replayed panel displays an explicit `REPLAY` status badge with playback state and never displays `LIVE`.
- **Multi-Chart & Sync Isolation**:
  - Replay binds to one panel; other panels remain in normal mode.
  - Stage 73 synchronization actions (instrument, interval) directed to the replayed panel are safely suppressed.
  - Crosshair sync events with timestamps beyond the replay cursor are rejected to prevent future-data inspection leakage.
- **Stage 74 Layout Persistence Invariance**:
  - Ephemeral replay state is strictly excluded from Stage 74 layout serialization.
  - Stepping replay does not alter workspace dirty state.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_chart_replay.py` (10/10 passed). All 107 backend chart tests across Stages 66 to 75 pass in 9.74s.
  - Frontend tests: `apps/web/tests/charts-replay.test.ts` (10/10 passed). All 100 frontend chart tests across Stages 66 to 75 pass in 2.3s.
  - Quality gates: Ruff 0 errors, TypeScript typecheck 0 errors, Next.js build 100% successful across all 38 routes.
- **Documentation**: See `docs/CHART_REPLAY.md` and `docs/DECISIONS.md`.

## Watchlists V1 (Stage 76)
- **Persistent Multi-Asset Financial Instrument Watchlists**:
  - Fully functional `/watchlists` module transforming the placeholder into an institutional-grade workspace.
  - PostgreSQL-backed persistent storage with versioned Alembic migration (`apps/api/migrations/versions/stage76_watchlists.py`).
  - User ownership isolation (`owner_user_id`), per-user name normalization and uniqueness, and atomic cascade deletions.
  - Strict server-side resource quotas: 50 watchlists/user, 250 items/list, 100-char names, 500-char descriptions.
- **Canonical Membership & Reordering**:
  - References canonical financial instrument UUIDs and market-series identities across Equities, ETFs, Funds, FX, Cryptocurrencies, Bonds, and Futures.
  - Duplicate prevention within watchlists via unique composite constraint `(watchlist_id, instrument_entity_id, market_series_id)`.
  - Dense position tracking (`0 ... N-1`) with drag-and-drop row reordering and keyboard-accessible Move Up / Move Down controls.
  - Optimistic concurrency control using monotonic integer `revision` counters and `expected_revision` / `If-Match` checks.
- **Qualified Market Quote Snapshots**:
  - Single batched query lookup from existing cached quote infrastructure; strictly **zero upstream provider fanout**.
  - Read-only snapshot display with valid quotation units (`USD`, `INR`, `USD/bbl`, `% of par`, `Yield %`).
  - Transparent freshness labels (`FRESH`, `DELAYED`, `STALE`, `UNAVAILABLE`) — zero fabricated prices, zero fake 0% changes.
- **Verified Cross-Navigation**:
  - One-click context preservation into `/charts` and canonical `/markets/*` hubs.
  - One-click navigation to verified issuing `/companies` only when a verified relationship (`issued_by`) exists.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_watchlists.py` (27/27 passed in 4.05s).
  - Frontend tests: `apps/web/tests/watchlists.test.ts` (11/11 passed in 1.0s).
  - Quality gates: Ruff 0 errors, TypeScript typecheck 0 errors, Next.js build 100% successful across all 38 routes.
- **Documentation**: See `docs/WATCHLISTS_V1.md` and `docs/DECISIONS.md`.

## Watchlists V1 — Advanced Columns (Stage 77)
- **Central Typed Column Registry**:
  - 14 operational columns across 4 categories: `identity`, `market`, `quote`, `quality`.
  - Typed values (`TEXT`, `IDENTIFIER`, `ENUM`, `MONETARY`, `PERCENTAGE`, `TIMESTAMP`, `STATUS`).
  - Mandatory Symbol column (`instrument.symbol`) enforced; cannot be hidden.
- **Customizable Financial Monitoring Table**:
  - Dynamic Show/Hide column selector modal (`WatchlistColumnManager`) with search and category grouping.
  - Drag-and-drop & keyboard accessible column reordering.
  - Smooth column resizing clamped between `min_width` and `max_width`.
  - Multi-column left pinning with pixel-accurate sticky offset calculations.
- **Financially Correct Sorting**:
  - 3-state cycling: Ascending → Descending → Manual default.
  - Deterministic tie-breaking: `manual_position`, then `item_id`.
  - Missing-values-last semantics on both ascending and descending.
  - Multi-currency / unit protection against false monetary ranking.
  - Entire dataset sorted before pagination slicing (100% correct global order).
- **PostgreSQL Persistence & Concurrency**:
  - Per-watchlist column preferences stored in `watchlist_column_preferences` with JSONB schema v1.
  - Monotonic `revision` concurrency protection (ETag / `If-Match`, returns 412/409 on conflict).
  - Reset to Defaults restoration.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_watchlist_columns.py` (21/21 passed).
  - Frontend tests: `apps/web/tests/watchlist-columns.test.ts` (7/7 passed).
  - Stage 76 regressions: `apps/api/tests/test_watchlists.py` (27/27 passed) and `apps/web/tests/watchlists.test.ts` (11/11 passed).
  - Production build: Next.js 16.3.8 Turbopack build 100% successful.
- **Documentation**: See `docs/WATCHLIST_COLUMNS.md` and `docs/DECISIONS.md`.

## Watchlists V1 — Live Updates (Stage 78)
- **Shared WebSocket Streaming Infrastructure**:
  - Reuses Stage 43 shared WebSocket (`SharedWebSocketClient`) with zero duplicate sockets.
  - Multi-consumer reference counting across watchlists and active Charts views.
  - Viewport-aware subscription planning with bounded 10-row overscan and background tab suspension.
- **Canonical Event Validation & Reconciliation**:
  - `validateCanonicalQuoteEvent`: schema v1 enforcement, canonical UUID check, finite decimals, genuine zero handling, and conditional negative price tolerance (CLZ26).
  - `EventOrderingTracker`: monotonic source-scoped ordering, duplicate event ID rejection, and sequence gap detection.
  - `SnapshotStreamReconciler`: solves startup race condition so older HTTP snapshots cannot overwrite newer streamed quotes.
  - `RenderBatcher`: coalesces high-frequency market event streams into batched 80ms animation frames.
- **Server-Side Entitlement Validation**:
  - `MarketDataEntitlementService` validates user tier, delayed-only roles, and restricted Level 2 instruments.
  - Typed `subscription.ack` messages with explicitly accepted and rejected series keys.
- **Institutional Financial Table UI**:
  - Directional movement cues (`▲`, `▼`, `―`) and subtle background highlights (`bg-emerald-500/10`, `bg-rose-500/10`).
  - Accessible connection status and realtime vs. delayed stream data quality badges (`Live: X/Y`).
  - Dedicated "Re-sort" action to reapply multi-column sorts against current live prices without disruptive row jumping.
  - Strict compliance with institutional design standards: zero purple gradients, zero cartoon chrome, zero LLM calls, zero autonomous trading.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_watchlist_live.py` (9/9 passed).
  - All 57 backend watchlist tests passed (`test_watchlists.py`, `test_watchlist_columns.py`, `test_watchlist_live.py`).
  - Frontend tests: `apps/web/tests/watchlist-live.test.ts` (7/7 passed).
  - All 25 frontend watchlist tests passed (`watchlists.test.ts`, `watchlist-columns.test.ts`, `watchlist-live.test.ts`).
  - Quality gates: Ruff 0 errors, TypeScript typecheck 0 errors.
- **Documentation**: See `docs/LIVE_WATCHLIST_UPDATES.md` and `docs/DECISIONS.md`.

## Company Earnings Intelligence (Stage 84)
- **Architecture**: Institutional-grade earnings workspace inside `/companies` integrating corporate earnings announcements, actual reported results, analyst consensus expectations, decimal-safe earnings surprise calculations, corporate forward management guidance, and verified earnings call references.
- **Strict Pre-Release Cutoff**: Consensus expectation snapshots enforce strict publication timestamps prior to earnings release ($T_{\text{consensus}} < T_{\text{announcement}}$), prohibiting look-ahead revision leakage.
- **Pure Decimal Arithmetic**: Zero floating point inaccuracy, robust zero-estimate denominator handling ($0$ consensus produces qualified percentage `None`), and negative-estimate magnitude interpretation using absolute denominators.
- **Management Guidance Tracking**: Displays company-issued forward projections (ranges and point values) with explicit accounting basis, period targets, revisions, and withdrawals—strictly separated from 3rd-party analyst consensus.
- **Earnings Calls & Transcripts**: Rights-aware conference call scheduling, audio webcasts, and licensed transcript access without synthesizing fake transcripts or generating LLM remarks.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_company_earnings.py` (22/22 passed).
  - All 121 company module tests passed (`test_companies_v1.py`, `test_company_financial_statements.py`, `test_company_financial_ratios.py`, `test_company_earnings.py`).
  - Frontend typecheck: `npx.cmd tsc --noEmit` (0 errors).
  - Linter: `ruff check` on Stage 84 (0 errors).
- **Documentation**: See `docs/COMPANY_EARNINGS.md` and `docs/DECISIONS.md`.

## Company Ownership Intelligence (Stage 85)
- **Architecture**: Institutional-grade company ownership workspace inside `/companies` integrating institutional shareholders (Form 13F), corporate insiders (Forms 3/4/5), beneficial owners (Schedules 13D/13G), macro shareholding patterns, ownership concentration, voting rights, and quarterly position changes.
- **Strict Distinction Matrix**: Formally separates investment managers from managed investment funds, registered nominees from beneficial owners, direct from indirect holdings, economic exposure from voting control, and historical period facts from later amendments.
- **Pure Decimal Precision**: Exact `Decimal` arithmetic for all share percentages, position changes, and percentage-point impacts with zero-division safety and negative-denominator rejection.
- **Non-Duplication & Deduplication**: Prevents double-counting overlapping positions across parent managers, sub-advisers, and group filings in concentration calculations.
- **Multi-Jurisdiction Handling**: Preserves native regulatory taxonomies (US SEC Section 13(f)/16 vs. Indian SEBI Clause 35 promoter/public/pledged classifications) without artificial forced mappings.
- **Zero Real-Time Conflation**: Preserves reporting dates and publication timestamps, clearly surfacing 45-day regulatory reporting lags.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_company_ownership.py` (12/12 passed).
  - All 133 company module tests passed (`test_companies_v1.py`, `test_company_financial_statements.py`, `test_company_financial_ratios.py`, `test_company_earnings.py`, `test_company_ownership.py`).
  - Frontend typecheck: `npx.cmd tsc --noEmit` (0 errors).
  - Production build: `npm.cmd run build` (Next.js 16.3.8 Turbopack clean compile).
  - Linter: `ruff check` on Stage 85 (0 errors).
- **Documentation**: See `docs/COMPANY_OWNERSHIP.md` and `docs/DECISIONS.md`.

## Company Filings Intelligence (Stage 86)
- **Architecture**: Institutional-grade regulatory filings intelligence workspace inside `/companies` integrating official SEC EDGAR disclosures, Annual Reports (10-K, 20-F), Quarterly Reports (10-Q), Current Material Events (8-K), Proxy Statements (DEF 14A), Ownership & Insider References (13F, Form 4), structured XBRL financial facts extraction, full-text document search, revision tracking, and side-by-side filing comparison.
- **Regulatory Source & Fair Access Compliance**: Enforces official SEC EDGAR Fair Access policy with configured User-Agent identifying technical contact email, token-bucket shared rate limiting (<= 10 req/s), exponential retry backoff, and direct links to immutable SEC web archives.
- **Safe Document Processing & Multi-Stage Sanitization**: Defuses script tags, inline event handlers, iframes, unsafe URL schemes, and active content from untrusted regulatory HTML. Prohibits XML external entity (XXE) attacks and quadratic expansion on XBRL instance documents.
- **Structured XBRL Financial Fact Extraction**: Extracts US-GAAP taxonomy concepts with exact context duration/instant qualifications, standard unit classifications (USD, SHARES), decimal precision, and reporting dimensions. Feeds canonical fact provenance into Financial Statements (Stage 82) and Financial Ratios (Stage 83).
- **Revision & Amendment Comparison**: Unifies line-by-line textual diffing across modified sections and calculates structured XBRL financial fact variances (absolute and percentage differences) with restatement status detection.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_company_filings.py` (14/14 passed).
  - All 147 company module tests passed (`test_companies_v1.py`, `test_company_financial_statements.py`, `test_company_financial_ratios.py`, `test_company_earnings.py`, `test_company_ownership.py`, `test_company_filings.py`).
  - Frontend typecheck: `cmd /c npx tsc --noEmit` (0 errors).
  - Production build: `cmd /c npm run build` (Next.js 16.3.8 Turbopack clean compile).
  - Linter: `ruff check` on Stage 86 (0 errors).
- **Documentation**: See `docs/COMPANY_FILINGS.md` and `docs/DECISIONS.md`.

## Company Peers & Comparable Company Analysis (Stage 87)
- **Architecture**: Institutional-grade comparable company analysis and peer benchmarking workspace within `/companies`. Features deterministic candidate peer discovery, verified multi-taxonomy industry classifications (GICS, ICB, NAICS, SIC), user-scoped custom peer groups with concurrency and revision control, batched cross-company financial benchmarking (Scale, Growth, Profitability, Liquidity, Solvency, Cash Flow), and relative valuation multiples.
- **Explicit Relationship Semantics**: Enforces rigorous semantic boundaries distinguishing `COMPARABLE_CANDIDATE`, `USER_SELECTED_PEER`, `SOURCE_DEFINED_PEER`, and `VERIFIED_COMPETITOR`. A comparable company is not assumed to be a competitor, and user selections never pollute the global corporate relationship graph.
- **Canonical Financial & Ratio Reuse**: Directly reuses Stage 82 Financial Statements and Stage 83 Financial Ratio Registry methodologies. Prevents duplicate calculation formulas and enforces non-meaningful (`N/M`) status for negative denominator ratios (e.g. negative equity P/B and ROE).
- **Period & Currency Alignment**: Supports `LATEST_COMMON_FISCAL_YEAR`, `LATEST_AVAILABLE`, and `QUALIFIED_TTM` modes with visible period-end date annotations. Disallows unnormalized raw multi-currency comparisons and enforces Decimal-safe arithmetic.
- **Statistical Benchmark Engine**: Calculates cross-sectional distributions (peer median, mean, min/max ranges, sample coverage ratios, subject-relative spreads, percentage-point differences, and Tukey's IQR statistical outlier detection) without silent sample elimination.
- **Historical Trajectories & Interactive Visualizations**: Multi-period historical trend series (FY2021–FY2024), Growth vs Operating Margin scatter plot matrix with market-cap bubble sizing and median quadrant crosshairs, and cell-level source fact inspection with XBRL filing references.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_company_peers.py` (21/21 passed).
  - All 168 company module tests passed (`test_companies_v1.py`, `test_company_financial_statements.py`, `test_company_financial_ratios.py`, `test_company_earnings.py`, `test_company_ownership.py`, `test_company_filings.py`, `test_company_peers.py`).
  - Frontend typecheck: `cmd /c npx tsc --noEmit` (0 errors).
  - Production build: `cmd /c npm run build` (Next.js 16.3.8 Turbopack clean compile, 38/38 routes).
  - Linter: `ruff check` on Stage 87 (0 errors).
- **Documentation**: See `docs/COMPANY_PEERS.md` and `docs/DECISIONS.md`.

## Company Supply Chain Intelligence (Stage 88)
- **Architecture**: Institutional-grade corporate supply chain network and commercial intelligence workspace within `/companies`. Features canonical entity resolution (UUID-based, legal entity vs. brand distinction, parent vs. subsidiary qualification, and public/private company compatibility), strictly directed commercial relationship modeling (`SUPPLIER -> CUSTOMER`), and verifiable source evidence lineage from SEC Form 10-K, 8-K, and corporate disclosures.
- **Commercial Relationship Taxonomy**: 12 controlled commercial edge categories including component supply (`SUPPLIES_COMPONENTS_TO`), raw materials, contract manufacturing (Foundry/OSAT), OEM, ODM, retail/carrier distribution channels, and technology licensing.
- **Verifiable Evidence & Zero-Inference Standard**: Every asserted edge is linked to traceable regulatory filings with document IDs, exact section anchors (e.g. *Item 1. Business - Supply Agreements*), filing timestamps, and quoted disclosure text. Zero LLM-hallucinated edges or speculative associations based on industry similarity.
- **Bounded Multi-Tier Traversal**: BFS network traversal supporting Tier-1 direct suppliers, Tier-1 customers/channels, and Tier-2 precursor suppliers (e.g. photolithography capital equipment and semiconductor raw silicon), with cycle protection, visited set tracking, and strict server-side resource limits ($\text{depth} \le 3$, $\text{max nodes} \le 150$, $\text{max edges} \le 300$).
- **Customer & Supplier Concentration Analysis**: Source-reported dependency metrics under ASC 280 / Regulation S-K Item 101 rules. Preserves anonymous customer disclosures (e.g. Customer A = 87% of net sales) without guessing company identities, and documents critical single-source supplier dependencies.
- **Point-in-Time Historical Timeline**: Audit trail of announced supply agreements, multi-year expansions, and supplier changes strictly bounded by filing publication timestamps without look-ahead bias.
- **Interactive SVG Network Graph**: Dense terminal-grade directed network explorer displaying Tier-2 precursors, Tier-1 suppliers, subject entity, and downstream distribution channels with directional bezier flow arrows, zoom/pan controls, edge inspection, and tier depth toggles.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_company_supply_chain.py` (23/23 passed).
  - All 191 company module tests passed (`test_companies_v1.py`, `test_company_financial_statements.py`, `test_company_financial_ratios.py`, `test_company_earnings.py`, `test_company_ownership.py`, `test_company_filings.py`, `test_company_peers.py`, `test_company_supply_chain.py`).
  - Frontend typecheck: `cmd /c npx tsc --noEmit` (0 errors).
  - Production build: `cmd /c npm run build` (Next.js 16.3.8 Turbopack clean compile, 38/38 routes).
  - Linter: `ruff check` on Stage 88 (0 errors).
- **Documentation**: See `docs/COMPANY_SUPPLY_CHAIN.md` and `docs/DECISIONS.md`.

## Institutional-Grade Economics V1 (Stage 89)
- **Architecture**: Authoritative global macroeconomic terminal workspace within `/economics` (Module 7). Features canonical economic indicator identity, sovereign source series discovery, G6 major economies matrix (United States, Euro Area, China, India, Japan, United Kingdom), multi-vintage official estimate tracking (Advance, Second, Third), point-in-time publication filtering, versioned mathematical transformations, and high-performance interactive time-series charting.
- **Canonical Indicator & Series Architecture**: Rigorous separation between abstract canonical indicator concepts (e.g. `GDP_GROWTH_QOQ_ANN`, `CPI_INFLATION_YOY`) and sovereign source series (e.g. BEA `A191RL1Q225SBEA`, BLS `CUUR0000SA0`, Eurostat `prc_hicp_manr`). Preserves official agency definitions, measurement units, reporting frequencies, and seasonal-adjustment policies.
- **Strict Anti-Fabrication Rule**: Zero manufactured economic data, zero unweighted synthetic "World GDP" averages, and zero substitution of market equity/bond quotes for sovereign economic statistics. All figures carry explicit reference periods, units, and sovereign authority provenance.
- **Measurement Semantics & Growth Formulas**: Clear differentiation between price levels (`INDEX_POINTS`) and inflation rates (`PERCENT`). Rates are adjusted in `PERCENTAGE_POINTS` (%p) or `BASIS_POINTS` (bps). Compound quarterly annualization is calculated strictly on positive constant-price GDP levels: $[(y_t / y_{t-1})^4 - 1] \times 100$.
- **Official Vintages & Point-in-Time Queries**: Tracks historical revisions across publication vintages. Query bounds (`as_of_date`) filter out subsequent revisions to prevent analytical backtest look-ahead leakage.
- **Global Overview Matrix & Interactive Workspace**: Features headline macro snapshot cards, G6 comparative matrix with click-to-chart actions, searchable indicator catalog, SVG line and bar time-series charts with zero-line support for negative values, paginated tabular data with CSV export, and source inspector drawer.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_economics_v1.py` (27/27 passed).
  - Full regression suite: 218 backend tests passed across Companies, Financial Statements, Ratios, Earnings, Ownership, Filings, Peers, Supply Chain, and Economics V1.
  - Frontend typecheck: `cmd /c npx tsc --noEmit` (0 errors).
  - Production build: `cmd /c npm run build` (Next.js 16.3.8 Turbopack clean compile, 38/38 routes including `/economics`).
  - Linter: `ruff check` on Stage 89 (0 errors).
- **Documentation**: See `docs/ECONOMICS_V1.md` and `docs/DECISIONS.md`.

## Institutional-Grade Country Economics Intelligence (Stage 90)
- **Architecture**: Comprehensive sovereign macroeconomic analysis workspace within `/economics` (Module 7). Transforms the canonical macroeconomic infrastructure into an institutional Country Economics workstation covering national accounts, expenditure structures, production-side Gross Value Added (GVA), inflation baskets, labor market dynamics, fiscal accounts, sovereign debt, international trade, balance of payments, and demographics for core G6 economies (United States `US`, Euro Area `EA`, China `CN`, India `IN`, Japan `JP`, United Kingdom `GB`).
- **SNA 2008 / ESA 2010 National Accounts Rigor**:
  - Distinguishes nominal (current prices) from real (constant / chained volume) GDP.
  - Implements genuine expenditure decomposition: $GDP = C + I + G + (X - M)$ with component values, shares of GDP, and contributions to growth (%p).
  - Explicit non-additivity handling: Discloses that chain-linked volume measures are non-additive outside base years and does not force reconciliation.
  - Production Approach (GVA): Sector value-added allocations (Agriculture, Industry/Manufacturing, Services) with explicit note bridging GVA to GDP via taxes less subsidies on products.
  - Real GDP per capita calculated strictly against compatible census/annual population reference years.
- **Price Stability & Labor Market Surveys**:
  - CPI price index levels with official base years (e.g. `1982-84=100`, `2015=100`), headline YoY/MoM, core CPI YoY/MoM, food & energy sub-indices, PPI, and GDP deflators with explicit seasonal adjustment tags.
  - Labor market statistics preserve sovereign survey methodologies (BLS CPS, UK ONS LFS, China NBS Urban) and distinguish unemployment rate (% labor force), participation rate, employment-to-population ratio, youth unemployment, and nominal vs real wage growth.
- **Fiscal Accounting & Public Debt Invariants**:
  - Never confuses `CENTRAL_GOVERNMENT` with `GENERAL_GOVERNMENT` scope, and explicitly identifies accrual vs cash accounting.
  - Full revenue/expenditure breakdown with primary balance (excluding debt interest expense).
  - Public debt stock vs annual GDP flow denominator timing alignment policy.
- **External Sector & Demographics**:
  - Strictly distinguishes customs goods trade from total goods-and-services trade and current account balance (BPM6 standard, including primary/secondary income).
  - Demographic profiles benchmarked to official census records: Working-age cohort (15–64), youth, elderly, dependency ratio, and urbanization.
- **Professional Terminal UI & Zero Side-Effects**:
  - Bloomberg/terminal-dense layout with country search, quick G6 switcher, 10 specialized category workspaces (`Overview`, `GDP & Growth`, `Inflation`, `Labor`, `Industry`, `Monetary`, `Fiscal`, `External & BOP`, `Demographics`, `Coverage Matrix`).
  - Strictly 0 LLM calls, 0 trading orders, 0 portfolio changes, 0 database writes on read.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_country_economics.py` (22/22 passed).
  - Regression suite: 49/49 passed (`test_economics_v1.py` + `test_country_economics.py`).
  - Frontend typecheck: `cmd /c npx tsc --noEmit` (0 errors).
  - Production build: `cmd /c npm run build` (Next.js 16.3.8 Turbopack clean compile, 38/38 routes including `/economics`).
  - Linter: `ruff check` on Stage 90 (0 errors).
- **Documentation**: See `docs/COUNTRY_ECONOMICS.md` and `docs/DECISIONS.md`.

## Institutional-Grade Financial News Platform Foundation (Stage 99)
- **Architecture**: Authoritative global financial news terminal workspace at `/news` (Module 8). Features canonical News Article entities, verified Publisher registry, authorized Provider adapters (`openbb_news`, `financial_wire_direct`, `regulator_announcements`, `corporate_press_wire`), idempotent ingestion pipelines with deterministic SHA-256 identity, duplicate detection, syndicated content recognition, and full revision audit trails.
- **Canonical Entity Linking & Disambiguation**: Resolves article mentions to canonical Company Entities (Stage 18) and Financial Instrument Entities (Stage 17) with strict ticker collision filters (excluding short common English words like `IT`, `ON`, `CAN`, `ARE`, `FOR`), exchange context disambiguation, ADR vs ordinary share qualification, and zero speculative sentiment or market-impact claims.
- **Timestamp Rigor & Provenance**: Tracks 5 distinct timestamps (`published_at`, `source_updated_at`, `first_seen_at`, `ingested_at`, `last_fetched_at`) with strict UTC guarantees and qualified calendar date precision. Ingestion timestamps are never substituted for publication timestamps.
- **Security & Copyright Compliance**:
  - Full SSRF protection rejecting loopback, RFC 1918 private ranges, link-local, and AWS metadata addresses (`169.254.169.254`).
  - HTML sanitization stripping `<script>`, `<style>`, and `<iframe>` blocks before stripping residual tags.
  - Safe external navigation with `rel="noopener noreferrer"` and scheme validation.
  - Strict copyright adherence: stores and serves only source-authorized headlines and excerpts; zero unpermitted full-text scraping or paywall circumvention.
- **Bloomberg-Style Financial News Workspace**:
  - High-density news feed table with publication time, verified publisher, headline, category badges, and interactive entity navigation chips.
  - Split article preview pane with publisher verification, copyright-compliant excerpt, timestamps, and safe external article link.
  - Keyset cursor pagination (`published_at DESC, article_id DESC`) with base64 cursors guaranteeing disjoint pages.
  - In-memory feed cache with immediate invalidation upon ingestion or revision.
  - Full keyboard accessibility: Up/Down arrow key headline navigation.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_news_v1.py` (30/30 passed).
  - Regression suite: 123 passed across news, economics, and screeners.
  - Frontend unit tests: `cmd /c pnpm test` (32/32 passed in `apps/web`).
  - Frontend typecheck: `cmd /c npx tsc --noEmit` (0 errors).
  - Production build: `cmd /c pnpm build` (Next.js 16.3.8 Turbopack clean compile, all 38 routes).
  - Linter: `uv run ruff check` on Stage 99 (0 errors).
- **Documentation**: See `docs/NEWS_V1.md` and `docs/DECISIONS.md`.

## Advanced Financial News Discovery, Search and Timeline System (Stage 100)
- **Architecture**: Advanced financial news exploration, search, and timeline system at `/news` (Module 8). Expands the canonical Stage 99 News foundation into a multi-dimensional discovery terminal with 7 discovery modes (`ALL`, `MARKETS`, `COMPANIES`, `SECURITIES`, `TOPICS`, `INDUSTRIES`, `WATCHLIST`), quoted exact phrase search, explainable term relevance scoring, dynamic faceted search, and chronological timeline event bucketing.
- **Canonical Topic Taxonomy & Classification**: Establishes 14 controlled topics (`EARNINGS_RELEASES`, `MERGERS_ACQUISITIONS`, `DIVIDENDS_DISTRIBUTIONS`, `SHARE_BUYBACKS`, `CAPITAL_RAISING`, `INTEREST_RATES_MONETARY_POLICY`, `INFLATION_PRICES`, `EMPLOYMENT_LABOR`, `FOREIGN_EXCHANGE_CURRENCIES`, `COMMODITIES_ENERGY`, `FINANCIAL_REGULATION_COMPLIANCE`, `CORPORATE_GOVERNANCE_BOARD`, `TECHNOLOGY_AI_INNOVATION`, `SUPPLY_CHAIN_LOGISTICS`) and GICS/ICB sector resolution (`NewsIndustrySector`) with deterministic rule-based classifiers.
- **Advanced Search & Transparent Relevance**:
  - Quoted phrase matching (`"..."`) and multi-token queries over source-licensed headlines and excerpts.
  - Transparent relevance scoring: +100 headline exact, +40 excerpt exact, +50 quoted phrase in headline, +20 quoted phrase in excerpt, +15 token in headline, +5 token in excerpt, +30 all-token overlap bonus, +10 topic alignment.
  - Relevance strictly measures text matching density; it is never represented to users as a market impact score.
  - Prefix autocomplete suggestions for tickers, companies, topics, publishers, and categories from verified metadata.
- **Entitlement-Aware Faceted Search**: Aggregates live article counts across Sources, Publishers, Categories, Topics, Countries, and Article Types matching active query filters without leaking unauthorized counts.
- **Chronological News Timelines**:
  - Groups articles into chronological buckets by `DAY`, `WEEK`, or `MONTH`.
  - Full timezone awareness using standard IANA timezones (UTC, America/New_York, Europe/London, Asia/Kolkata, Asia/Tokyo) with daylight saving handling.
  - Gaps in coverage remain honestly empty with zero synthetic event fabrication.
  - Accurate publication vs first-seen timestamp distinctions.
- **Terminal Workspace**:
  - High-density dual view: interactive Feed Table and visual Chronological Timeline.
  - Fast search combobox with grouped suggestion badges and keyboard navigation.
  - Multi-dimensional filter sidebar with date range presets, timezone selector, sort order, and facet count pills.
  - Source-qualified article inspector and seamless entity navigation chips.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_news_discovery_v1.py` and `test_news_v1.py` (58/58 passed).
  - Regression suite: 111 passed across news, economics, and screeners.
  - Frontend unit tests: `cmd /c pnpm test` (40/40 passed in `apps/web`).
  - Frontend typecheck: `cmd /c npx tsc --noEmit` (0 errors).
  - Production build: `cmd /c pnpm build` (Next.js 16.3.8 Turbopack clean compile).
  - Linter: `uv run ruff check` (0 errors).
- **Documentation**: See `docs/NEWS_DISCOVERY_AND_TIMELINES.md` and `docs/DECISIONS.md`.

## Financial News Story Intelligence and Event Classification System (Stage 101)
- **Architecture**: Institutional-grade multi-source story clustering and evidence-based financial event classification at `/news` (Module 8). Connects Stage 99 News Foundation and Stage 100 Discovery by organizing disparate articles into auditable Story Threads (`story-*`) and identifying explicitly supported Financial Event records (`fev-*`) from verified source evidence.
- **Story Threads & Conservative Clustering**:
  - Candidate retrieval blocking on shared canonical company/instrument entities, verified event context, and bounded temporal proximity windows.
  - Entity overlap alone is strictly insufficient to merge articles; stories require specific narrative and event identity to prevent false grouping.
  - Syndicated wire republications are distinguished from independent newsroom reporting; `independent_publisher_count` tracks distinct verified newsrooms.
  - Administrative merge and split capabilities with complete revision tracking.
  - Sourced display titles without hallucinated narrative briefs.
- **Canonical Financial Event Taxonomy**:
  - 20 versioned corporate and macroeconomic event types: Earnings Releases, Guidance, Dividends, Buybacks, M&A (Proposals, Agreements, Completions, Terminations), Financing (Equity, Debt), Leadership Changes (Appointments, Departures), Regulatory Actions (Investigations, Enforcement), Litigation, Restructuring/Bankruptcy, Product Launches, Facility Expansions, Central Bank Rate Decisions, and Macro Releases.
- **Assertion vs. Lifecycle Qualification**:
  - Assertion statuses (`OFFICIALLY_REPORTED`, `THIRD_PARTY_REPORTED`, `RUMORED`, `ALLEGED`, `DENIED`, `DISPUTED`, `CORRECTED`) are strictly separated from transaction lifecycle states (`PROPOSED`, `ANNOUNCED`, `PENDING`, `APPROVED`, `COMPLETED`, `CANCELLED`, `WITHDRAWN`).
  - Rumors are never converted into completed deals; regulatory investigations are never classified as findings of wrongdoing; forward guidance is never confused with reported earnings actuals.
- **Evidence & Quantitative Precision**:
  - Structured monetary extraction (`EventAmount`) preserving exact numeric values, currencies (`USD`, `EUR`, `INR`), scales (`crore`, `lakh`), and approximation flags (`EXACT`, `APPROXIMATE`, `RANGE_MIN`, `RANGE_MAX`, `ESTIMATED`). Valuations are never guessed.
  - Verified transactional participant roles (`PRIMARY_SUBJECT`, `ACQUIRER`, `TARGET`, `REGULATOR`, `ISSUER`, `LENDER`, `EXECUTIVE`).
  - Strict temporal precision: separates event occurrence, announcement time, article publication time, and ATLAS first-seen time without look-ahead bias.
  - Every event attribute is grounded in immutable `NewsEventEvidence` citations with publisher attribution and permitted excerpts.
- **Terminal Workspace & Workspaces**:
  - 4 Integrated View Modes: `[Headlines]` (Stage 99), `[Story Threads]` (Stage 101), `[Financial Events]` (Stage 101), and `[Timelines]` (Stage 100).
  - High-density Story Table with coverage counts, independent source metrics, and Story Inspector showing member article progression.
  - Financial Event Table with assertion qualification badges, lifecycle status, formatted financial amounts, and Event Inspector with participant breakdowns, uncertainty notices for rumors, and evidence citations.
- **Testing & Verification**:
  - Backend tests: `apps/api/tests/test_news_story_intelligence_v1.py`, `test_news_discovery_v1.py`, `test_news_v1.py` (74/74 passed in 8.00s).
  - Backend linter: `uv run ruff check` on all news modules (0 errors).
  - Frontend unit tests: `cmd /c pnpm --filter web test` (46/46 passed in `apps/web`).
  - Frontend typecheck: `cmd /c npx tsc --noEmit` (0 errors in `apps/web`).
  - Production build: `cmd /c pnpm --filter web build` (Next.js 16.3.8 Turbopack clean compile).
- **Documentation**: See `docs/NEWS_STORIES_AND_EVENTS.md` and `docs/DECISIONS.md`.

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



