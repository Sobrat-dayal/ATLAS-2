# Markets Overview V1 Architecture (Stage 56)

**ATLAS Module 02 — Multi-Asset Market Intelligence Dashboard, Live Market Data and Professional Financial Terminal Interface**

---

## 1. Executive Summary

Stage 56 establishes **ATLAS Markets Overview V1**, transforming the canonical `/markets` route (Module 2) from a placeholder into an operational, information-dense multi-asset financial market dashboard.

Markets Overview answers key financial questions:
1. Which market instruments are configured and covered in ATLAS?
2. What are their latest canonical traded values?
3. How have they changed relative to verified completed-session reference closes?
4. Which asset classes are represented (Benchmarks, Equities, ETFs, FX, Crypto, Commodities, Bonds)?
5. Which observations are current (fresh), aging, stale, delayed, or unavailable?
6. What is the verifiable provenance and source observation time of each price?
7. How can users seamlessly select canonical entities and navigate to other analytical workspaces (Charts, Screeners, Watchlists)?

### Core Product Principle
**Financial market data must be evidence-based, mathematically accurate, and transparent.**
ATLAS never fabricates stock prices, return percentages, volume numbers, market capitalizations, or provider coverage. Missing or unconfigured data is displayed truthfully as unavailable (`—`), never masked by decorative mock data or false zero values.

---

## 2. Architecture & Data Flow

```
                      ATLAS AUTHENTICATED APPSHELL
                                    │
                                    ▼
                         /markets (Module 02)
                                    │
      ┌─────────────────────────────┼─────────────────────────────┐
      │                             │                             │
      ▼                             ▼                             ▼
MarketsHeader             MarketsCoverageSummary        MarketsGroupSelector
(Search, Charts,             (Configured, Available,       (Asset Group Tabs &
 Screeners, Watchlists)       Unavailable, Scope)           Count Badges)
      │                             │                             │
      └─────────────────────────────┼─────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
       FeaturedMarketInstruments        MarketsInstrumentTable
       (Top 7 Benchmarks & Markets)     (Density Table, Sort, Paging)
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                          useMarketsOverview Hook
                         (In-Memory Cache, Coalesced
                          Invalidation, Race Protection)
                                    │
                                    ▼ HTTP GET
                       /api/v1/markets/overview
                                    │
                                    ▼
                         MarketsOverviewService
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
PostgreSQL                      Redis / Valkey                ClickHouse
(Canonical Entity Names &       (Latest Traded Quotes via      (Verified Daily Bars via
 Instrument UUID Authority)      LiveQuoteService)              ReferenceCloseResolver)
     │                              │                              │
     └──────────────────────────────┼──────────────────────────────┘
                                    │
                                    ▼
                       Stage 44 Freshness & Delay
                       + Decimal Change Calculations
                                    │
                                    ▼
                        MarketsOverviewResponse
                                    │
                                    ▲ Realtime Event
                     Stage 43 WebSocket Subscription
                     ("atlas:market.quote.updated")
```

---

## 3. Scope & Universe Definition

### Bounded Universe Guarantee
Markets Overview V1 operates over a **deliberate, server-owned, bounded catalog** of configured canonical Financial Instruments. It does **not** claim to be an unrestricted scanner of every global exchange or listed security.

- **Scope Metadata**: Authoritatively labeled in responses as:
  ```json
  "scope": "configured_overview_universe"
  ```
- **Capacity**: Maximum catalog capacity is bounded at 100 instruments (initial active universe: 29 curated instruments across 7 asset groups).
- **Featured Instruments**: Exactly 7 high-visibility instruments (within the required 6–8 range) displayed above the table: S&P 500, NASDAQ 100, Dow Jones, SPY ETF, EUR/USD, BTC/USD, Brent Crude.

### Canonical Asset Groups
1. `benchmarks`: S&P 500 (`^GSPC`), NASDAQ 100 (`^NDX`), Dow Jones Industrial (`^DJI`), Russell 2000 (`^RUT`), FTSE 100 (`^FTSE`), Nikkei 225 (`^N225`).
2. `equities`: Apple (`AAPL`), Microsoft (`MSFT`), NVIDIA (`NVDA`), Amazon (`AMZN`), Alphabet (`GOOGL`), Tesla (`TSLA`).
3. `etfs`: SPDR S&P 500 ETF (`SPY`), Invesco QQQ (`QQQ`), iShares Russell 2000 (`IWM`), Vanguard Total Stock Market (`VTI`).
4. `fx`: EUR/USD, USD/JPY, GBP/USD, USD/CHF.
5. `crypto`: Bitcoin (`BTC/USD`), Ethereum (`ETH/USD`), Solana (`SOL/USD`).
6. `commodities`: Brent Crude (`BZ=F`), WTI Crude (`CL=F`), Gold (`GC=F`), Silver (`SI=F`).
7. `bonds`: US 10-Year Benchmark Yield (`^TNX`), US 2-Year Benchmark Yield (`^IRX`).

### Invariant: Index vs ETF Distinction
Benchmark indices and their tracking ETFs remain strictly distinct entities:
- S&P 500 Index (`^GSPC`, `is_index: true`, value in points `pts`, group `benchmarks`).
- SPDR S&P 500 ETF (`SPY`, `is_index: false`, value in price `USD`, group `etfs`).
An ETF price is never mislabeled as an index level.

---

## 4. Financial Calculations & Data Precision

1. **Decimal Precision**:
   - All backend calculations utilize Python's `Decimal` type to avoid binary floating-point rounding errors.
   - Price and change values are serialized as string representations to preserve full precision over JSON.
2. **Absolute Change Formula**:
   $$\text{absolute\_change} = \text{last\_price} - \text{reference\_close}$$
3. **Percentage Change Formula**:
   $$\text{percentage\_change} = \left(\frac{\text{last\_price} - \text{reference\_close}}{\text{reference\_close}}\right) \times 100$$
4. **Zero-Denominator Safety**:
   - If $\text{reference\_close} = 0$, percentage change is set to `None`. No division-by-zero, `NaN`, or `Infinity` is ever produced.
5. **Reference Close Source**:
   - Priority 1: Verified previous close embedded in the feed snapshot.
   - Priority 2: Completed daily session close from ClickHouse (`interval = '1d'`).
   - If no valid completed session reference close is verified, change is returned as `None` (presented as `—`), while the valid latest price remains displayed.

---

## 5. Freshness, Delivery Delay & Provenance

Reuses Stage 44 Market Data Freshness Engine:
- **Observation Freshness**:
  - `fresh`: Under 5 minutes old (Current).
  - `aging`: 5 to 15 minutes old (Aging).
  - `stale`: Over 15 minutes old (Stale).
  - `unavailable`: No source timestamp or no observation.
- **Delivery Delay**:
  - `realtime`: Live feed delivery.
  - `delayed`: Upstream provider delay (e.g., `15m Delayed`).
- **Safe Provenance**:
  - Exposes `provider_key`, `provider_display_name` (e.g., OpenBB, Financial Modeling Prep), `source_timestamp`, and `received_at`.
  - Zero internal credentials, API keys, or Redis connection strings are ever exposed to the client.

---

## 6. Read-Only Backend API Specification

### Endpoint: `GET /api/v1/markets/overview`
- **Authentication**: Requires authenticated session (`get_current_user`).
- **Authorization**: Requires `atlas.access` permission.
- **Cache-Control**: `private, no-store`.

#### Query Parameters:
| Parameter | Type | Default | Description |
|---|---|---|---|
| `group` | string | `None` | Filter by asset group (`benchmarks`, `equities`, `etfs`, `fx`, `crypto`, `commodities`, `bonds`). |
| `limit` | integer | `25` | Page limit (min: 1, max: 100). |
| `cursor` | string | `None` | Keyset/offset pagination cursor. |
| `featured_only` | boolean | `false` | Return only featured instruments. |

#### Read-Only Guarantees:
- PostgreSQL writes: `0`
- Redis writes: `0`
- ClickHouse writes: `0`
- Provider HTTP/Stream requests: `0`
- Ingestion target modifications: `0`
- Background jobs spawned: `0`

---

## 7. Realtime Synchronization & Event Ordering

Reuses Stage 42 live market event pipeline and Stage 43 frontend WebSockets:
- **Initial State**: Fetched via authoritative HTTP snapshot (`GET /api/v1/markets/overview`).
- **Realtime Trigger**: Listens for window event `atlas:market.quote.updated`.
- **Coalesced Invalidation**: Rate-limited to at most one refetch every 2,000ms, preventing request storms during high-frequency market activity.
- **Snapshot Race Protection**: `lastAcceptedGeneratedAtRef` ensures out-of-order HTTP responses older than the currently displayed state are discarded.
- **Reconnection Recovery**: Network reconnect and window focus events trigger automatic background verification if data is older than `STALE_TIME_MS` (15s).

---

## 8. Cross-Module Navigation & Context

- **Stage 25 Universal Selected Entity**:
  - Clicking any featured card or table row invokes `selectEntity(instrument_entity_id)` with canonical UUID authority.
  - Global entity context is preserved across module transitions without auto-navigating away from Markets.
- **Module Navigation**:
  - `Search Instruments`: Triggers Stage 45 Global Search.
  - `Open Charts`: Links to `/charts` preserving selected entity context.
  - `Open Screeners`: Links to `/screeners`.
  - `Open Watchlists`: Links to `/watchlists`.

---

## 9. Verification & Quality Gates

- **Backend Unit & Integration Tests**: 15 passed in `apps/api/tests/markets/test_markets_overview.py` (catalog validation, Decimal math, group filtering, pagination, missing quote transparency, read-only guarantees, auth/authz contracts).
- **Backend Regression Tests**: 104 passed across `tests/home/` and `tests/markets/`.
- **Frontend Component Tests**: 10 passed in `apps/web/tests/markets-overview.test.ts` (export integrity, point/currency/rate/yield formatting, missing data handling, direction styling, freshness badges, no fake data static checks).
- **Frontend Regression Tests**: 81 passed across 16 test suites in `apps/web/tests/`.
- **Typecheck**: `tsc --noEmit` exited with code 0.
- **Lint**: Ruff and ESLint exited with code 0.
- **Production Build**: Next.js production build succeeded with 29/29 static pages generated.
