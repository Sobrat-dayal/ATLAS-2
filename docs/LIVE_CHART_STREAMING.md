# ATLAS Live Chart Streaming V1 — Real-Time Financial Price Visualization & WebSocket Integration

**Canonical Roadmap Stage: 67**  
**Module Route:** `/charts`  
**Status:** Complete  
**Engine:** Lightweight Charts (`lightweight-charts@5.2.1`, Apache-2.0)  
**Read Authority:** Canonical Market Data Service / Redis/Valkey Latest Quote State (Stage 41)  
**Event Transport:** Redis Stream `market.quote.updated` (Stage 42) / Authenticated WebSocket Gateway (Stage 43)  
**Freshness Classification:** Stage 44 Market Data Freshness Service  

---

## 1. Executive Summary & Vision

Stage 67 transforms ATLAS Charts from a historical-only visualization workspace (Stage 66) into a **live-capable institutional financial charting workstation**. Inspired by Bloomberg Terminal, TradingView, and institutional execution terminals, Stage 67 integrates genuine live market observations, canonical instrument streaming subscriptions, initial state bootstrapping, chronological event ordering, and a dedicated live price overlay while enforcing strict financial market-data integrity.

Stage 67 delivers:
1. **Canonical Instrument & Market-Series Streaming:** Live subscription management using canonical `instrument_entity_id` UUIDs and market-series dimensions, preventing cross-venue or cross-listing Quote pollution.
2. **Authoritative Initial Live-State Bootstrap:** `GET /api/v1/charts/live-state` endpoint reading authorized, accepted latest Quote state from Stage 41 Redis/Valkey authority.
3. **Snapshot-to-Event Race Reconciliation:** Deterministic ordering with bounded event buffering during HTTP bootstrap; rejection of stale snapshots and chronological event progression.
4. **Dedicated Live Price Overlay:** Lightweight Charts price line and price-axis marker reflecting genuine Last-price updates without mutating canonical historical OHLC candles.
5. **Strict Financial Data Integrity:** Explicit architectural distinction between Quote snapshots, trade-print streams, and authoritative OHLC bars. No synthetic candles, no fake Volume from Quote counts, no midpoint substitution for Last, and full support for negative commodity futures prices (e.g., `CLZ26`).
6. **Dual Status Modeling:** Orthogonal transport connection state (`DISCONNECTED`, `CONNECTING`, `CONNECTED`, `RECONNECTING`, `ERROR`) and market data freshness classification (`LIVE`, `DELAYED`, `STALE`, `UNKNOWN`, `UNAVAILABLE`).
7. **Institutional Chart Controls:** Functional Pause/Resume Live Updates toggle, "Go to Latest" viewport recentering, and Follow-Live mode disabled during manual historical panning.
8. **Render Coalescing & Backpressure:** Bounded update scheduler (100ms coalesce cadence) preventing browser UI degradation under high-frequency market tick bursts.
9. **Resilient Reconnection & Degradation Handling:** Automatic resubscription on WebSocket reconnect, bounded Redis Stream gap recovery, and honest fallback states when live feeds are unavailable.
10. **Strict Security & Read-Only Guarantees:** 0 upstream Provider calls on read, 0 ClickHouse writes, 0 trading executions, 0 LLM calls, and 0 local credential exposures.

---

## 2. Roadmap Position & Strict Boundaries

Stage 67 extends Stage 66 without prematurely implementing subsequent roadmap stages:

| Roadmap Stage | Scope / Assigned Capability | Status |
| :--- | :--- | :--- |
| Stage 66 | Historical Charts V1: Candlesticks & Line, 1D Baseline, Historical Navigation | COMPLETE |
| **Stage 67** | **Live Chart Streaming V1: Last-Price Overlay, WebSocket Integration, Reconciliation** | **COMPLETE** |
| Stage 68 | Expanded Chart Intervals (1m, 5m, 1h, 1W), Resampling Engine, Alternative Chart Types | DEFERRED |
| Stage 69 | Technical Indicator Infrastructure (SMA, EMA, RSI, MACD, Bollinger Bands) | DEFERRED |
| Stage 70 | TA-Lib Integration & Advanced Quantitative Studies | DEFERRED |
| Stage 71 | Interactive Drawing Tools (Trendlines, Rays, Fibonacci, Price Channels) | DEFERRED |
| Stage 72 | Multi-Chart Layouts (Split View, 2x2, Grid Workspace) | DEFERRED |
| Stage 73 | Cross-Chart Synchronization (Linked Crosshairs, Unified Timeframes) | DEFERRED |
| Stage 74 | Saved Chart Layouts, Cloud Persistence, User Templates | DEFERRED |
| Stage 75 | Historical Chart Replay Engine | DEFERRED |
| Stage 144 | Chart Trading, Order Placement Ladders, Execution Execution Controls | DEFERRED |

---

## 3. Financial Data Integrity & Semantic Distinctions

### 3.1 Three Distinct Market-Data Capabilities

Financial charting workstations must never treat market data capabilities as interchangeable:

| Capability Kind | Data Characteristics | Permitted Chart Use in Stage 67 | Prohibited Actions |
| :--- | :--- | :--- | :--- |
| **Capability A: Latest Quote Snapshot** | Bid, Ask, Last (if executed), Source Timestamp, Venue, Sizes. Sampled market state. | Real-time Last-price overlay line, price-axis marker, Quote inspector metrics. | **NEVER** construct Open, High, Low, Close or Volume from snapshot series. |
| **Capability B: Executed Trade Stream** | Every executed trade print: trade price, quantity, execution timestamp, condition codes. | Trade-derived aggregation **only if** complete coverage from period open and gap-detection exist. | **NEVER** aggregate partial trade streams into pseudo-complete session candles. |
| **Capability C: Authoritative Live OHLC Bars** | Exchange/Provider-calculated provisional or completed bars with explicit session metadata. | Active bar visualization and provisional bar overlay with explicit label. | **NEVER** finalize provisional bars solely based on local client wall-clock time. |

### 3.2 Quote Snapshot vs. Candle Integrity

1. **Quote Snapshots Do Not Establish True High/Low:** Sparse Quote samples (e.g., 100.00, 101.00, 100.50) omit unobserved trades occurring between snapshots. Fabricating an OHLC candle from Quote samples violates financial integrity.
2. **Bid/Ask Are Not Last:** In quote-driven or OTC markets (e.g., EUR/USD, US 10Y Treasury), quotes consist of indicative Bid and Ask rates. The midpoint `(bid + ask) / 2` is an indicative valuation, not an executed transaction. When genuine Last is absent, the overlay displays `Last price unavailable`; midpoint is never plotted as Last.
3. **Quote Count Is Not Volume:** Receiving 50 Quote updates during a minute indicates quotation activity, not 50 traded shares or contracts. Quote counts are never displayed as volume.
4. **Negative Price Support:** In accordance with Stage 62 derivatives semantics, commodity futures support negative prices (e.g., WTI Crude Oil `CLZ26` historical negative settlement). Negative prices are plotted accurately on the price scale and never clamped to zero.
5. **No Client-Side Historical Mutations:** Streaming Quote updates never mutate ClickHouse historical storage or overwrite authoritative daily candles.

---

## 4. System Architecture & Data Flow

```
                      UPSTREAM PROVIDER FEEDS
                                |
                                v
                Stage 41 Live Quote Ingestion Worker
                                |
                                v
                  Canonical Quote Validation &
                 Accepted-State Ordering Rules
                                |
                                v
               Stage 41 Redis/Valkey Latest Quote State
                                |
                                +------------------------------+
                                |                              |
                                v                              v
                      Stage 42 Event Bus              GET /charts/live-state
                    market.quote.updated               (Stage 67 Bootstrap)
                                |                              |
                                v                              |
                     Stage 43 WebSocket Gateway                |
                                |                              |
                                v                              |
                    Browser WebSocket Manager                  |
                                |                              |
                                +---------------+--------------+
                                                |
                                                v
                                  LiveChartController (Frontend)
                                  - Canonical UUID Subscription
                                  - Bounded Bootstrap Buffer (50)
                                  - Snapshot-to-Event Reconciliation
                                  - Source-Time Monotonic Ordering
                                  - Coalesced Scheduler (100ms)
                                                |
                     +--------------------------+--------------------------+
                     |                                                     |
                     v                                                     v
          Genuine Live Price Overlay                             Stage 66 Historical
          - Horizontal Price Line                                OHLCV Chart Engine
          - Price-Axis Badge                                     - Daily Bars (1D)
          - Provenance & Freshness                               - ClickHouse Authority
                     |                                                     |
                     +--------------------------+--------------------------+
                                                |
                                                v
                               ATLAS /charts Workspace UI
                               - Live Controls (Pause/Resume/Go to Latest)
                               - Live Market Data Status
                               - Latest Quote Details
```

---

## 5. Backend Implementation

### 5.1 DTO Schemas (`atlas.charts.models`)

- `LiveQuoteDTO`:
  - `bid_price`, `ask_price`: Indicative best bid and ask quotes.
  - `bid_size`, `ask_size`: Optional market depth quantities.
  - `last_price`: Qualified executed trade price (or `None`).
  - `last_size`: Optional trade execution volume.
  - `as_of`: ISO-8601 UTC timestamp of provider quotation.
  - `is_midpoint`: Explicit boolean flag identifying whether price is an indicative midpoint.
  - `has_genuine_last`: Verification flag confirming presence of an executed trade print.
- `ChartLiveStateResponse`:
  - `schema_version`: "1.0.0"
  - `instrument_entity_id`: Canonical instrument UUID.
  - `display_symbol`: Canonical ticker symbol.
  - `market_or_venue`: Primary exchange or execution venue.
  - `price_currency`: Currency denomination (e.g., "USD").
  - `quotation_unit`: Explicit unit (e.g., "USD/share", "USd/barrel").
  - `quote`: Qualified `LiveQuoteDTO` or `None`.
  - `source_timestamp`: Upstream quotation timestamp.
  - `received_at`: Ingestion pipeline arrival timestamp.
  - `provider`: Primary market data provider provenance.
  - `freshness_status`: Stage 44 freshness classification (`LIVE`, `DELAYED`, `STALE`, `UNKNOWN`, `UNAVAILABLE`).
  - `delay_status`: `REALTIME` vs `DELAYED_15M`.
  - `live_capability`: `LIVE_PRICE_AVAILABLE`, `HISTORICAL_ONLY`, `LIVE_BAR_AVAILABLE`, `LIVE_DATA_UNAVAILABLE`.
  - `availability`: `AVAILABLE` or `UNAVAILABLE`.
  - `is_paused`: Controller state flag.

### 5.2 Live State Service (`atlas.charts.live_service`)

The `LiveChartService` implements:
1. `get_live_state(instrument_id, symbol)`: Retrieves latest accepted Quote from Stage 41 Redis state authority. Validates against canonical instrument catalog.
2. `validate_and_reconcile_quote_event(incoming_event, current_quote, instrument_catalog)`:
   - Validates schema version, UUID match, and numeric decimal integrity (rejects `NaN` and `Infinity`).
   - Rejects stale events where `event_timestamp <= current_quote.as_of`.
   - Preserves executed Last prices; does not overwrite genuine Last with bid/ask-only snapshots.
   - Enforces negative price legality per asset class (`allow_negative_price`).
3. `apply_quote_to_historical_bars(historical_bars, live_quote)`: Strictly verifies that historical OHLC bars remain immutable upon live quote arrival.

### 5.3 REST Endpoint (`atlas.charts.router`)

- **Method / Path:** `GET /api/v1/charts/live-state`
- **Query Parameters:** `instrument_id` (UUID) or `symbol` (string).
- **Security:** Requires Stage 13 authentication and Stage 14 entitlement verification.
- **Guarantees:** 0 ClickHouse writes, 0 Provider API fetches, 0 Redis writes on read.

---

## 6. Frontend Live Controller (`apps/web/src/lib/charts/live-controller.ts`)

The `LiveChartController` coordinates live streaming state independently of React component render cycles:

### 6.1 State Machine & Lifecycles
- `subscriptionKey`: Bound to canonical `instrument_entity_id`.
- `status`:
  - `connection`: `DISCONNECTED`, `CONNECTING`, `CONNECTED`, `RECONNECTING`, `ERROR`.
  - `freshness`: `LIVE`, `DELAYED`, `STALE`, `UNKNOWN`, `UNAVAILABLE`.
  - `delay`: `REALTIME`, `DELAYED_15M`, `UNKNOWN`.
  - `capability`: `LIVE_PRICE_AVAILABLE`, `HISTORICAL_ONLY`, `LIVE_BAR_AVAILABLE`, `LIVE_DATA_UNAVAILABLE`.
- `isPaused`: Halts visual overlay emissions while maintaining connection status.
- `followingLatest`: Automatically disabled when user manually pans historical viewport; re-enabled via "Go to Latest".

### 6.2 Bootstrap & Race Resolution
1. Controller subscribes to WebSocket channel for canonical instrument UUID.
2. Incoming events during HTTP fetch are buffered into a bounded queue (`max 50 events`).
3. If buffer exceeds 50 events, buffer is purged and state is flagged for reconciliation.
4. HTTP snapshot arrives (`GET /api/v1/charts/live-state`).
5. Buffered events with `as_of > snapshot.as_of` are replayed chronologically; older events are discarded.
6. Controller transitions to `CONNECTED` and emits latest qualified Quote.

### 6.3 Backpressure & Coalesced Rendering
High-frequency market feeds may produce dozens of updates per second. The controller implements a timer-based coalescing queue (`coalesceIntervalMs = 100ms`). Intermediate price updates within the window update internal state, but emit exactly one render event per cadence, eliminating React rerender cascades and maintaining 60fps canvas interaction.

---

## 7. Interactive Canvas Integration (`HistoricalChart.tsx`)

### 7.1 Lightweight Charts Price Line
When a qualified Last-price exists on `currentQuote`:
- Controller updates or creates an `IPriceLine` on the candlestick series.
- Color: High-contrast cyan/sky blue (`#38bdf8`) with dashed line style.
- Title: Formatted with quotation unit (e.g. `LAST 586.25 USD/share`).
- Price Axis Marker: Displays exact qualified execution price.
- Inactive/Bid-Ask Only Mode: When Last is unavailable, the price line is cleanly removed.

### 7.2 Viewport Navigation & Follow-Live
- **Manual Pan Detection:** Subscribes to Lightweight Charts `visibleLogicalRangeChange`. When user pans older history, `followingLatest` transitions to `false`.
- **Go to Latest:** Invokes `chart.timeScale().scrollToRealTime()` and restores `followingLatest = true`.
- **Zero Viewport Jumps:** Incoming live quotes do not reset zoom level or disrupt active crosshair examination.

---

## 8. User Interface & Controls

### 8.1 Toolbar & Controls
- **Live Updates Toggle:** Functional button toggling between `LIVE UPDATES ACTIVE` (green pulse) and `UPDATES PAUSED` (amber border).
- **Go to Latest Button:** Jump directly to newest bar/price overlay with follow indicator (`FOLLOWING` vs `FREE PAN`).

### 8.2 Live Market Data Status Bar (`LiveMarketDataStatus.tsx`)
- High-density status chips:
  - Transport Connection (`CONNECTED`, `CONNECTING`, `RECONNECTING`, `DISCONNECTED`).
  - Data Freshness (`LIVE`, `DELAYED`, `STALE`, `UNKNOWN`).
  - Feed Latency (`REALTIME` vs `DELAYED 15M`).
  - Source Provenance (`VENUE: NYSE Arca`, `SOURCE: OPENBB_POLYGON`).
  - Upstream Timestamp (`SRC TIME: 2026-10-18 10:00:00 UTC`).

### 8.3 Latest Quote Details (`LatestQuoteDetails.tsx`)
- Metric readouts with tabular typography:
  - `LAST PRICE`: Qualified executed price (or `—` when unavailable).
  - `BID / ASK`: Current top-of-book prices and sizes.
  - `SPREAD`: Absolute spread and basis points.
  - `QUOTATION UNIT`: Precise quotation unit (`USD/share`, `USd/barrel`, `USD/token`).

---

## 9. Verification & Quality Gates

### 9.1 Backend Tests (`apps/api/tests/test_charts_live_streaming.py`)
- 17 test cases verifying:
  - Equities, ETFs, and Crypto live state retrieval with genuine Last prices.
  - Bid/Ask-only OTC FX and bond rates with `has_genuine_last=False` and `None` Last price.
  - Support for valid negative commodity futures prices (`CLZ26` at -12.50 USD/barrel).
  - Immutability of historical OHLC bars upon live quote arrival.
  - Rejection of stale/older timestamps and duplicate events.
  - Malformed decimal and NaN/Infinity injection rejection.
  - Zero Provider fetches and zero ClickHouse writes on read.
- **Result:** 17/17 passed; full charts suite 32/32 passed.

### 9.2 Frontend Tests (`apps/web/tests/charts-live-streaming.test.ts`)
- 13 test cases verifying:
  - Initial bootstrap and state population.
  - Rejection of stale and duplicate events based on source timestamp ordering.
  - Preservation of historical OHLC candles without client-side mutation.
  - Bid/Ask-only handling without midpoint-to-Last conflation.
  - Negative futures price handling without zero-clamping.
  - Snapshot-to-event race reconciliation with bounded buffering.
  - Pause and Resume controls without unbounded queues.
  - Safe instrument switching without cross-entity state bleeding.
  - High-frequency event coalescing.
  - Disconnect and reconnect state transitions.
  - Strict design compliance: 0 purple gradients, 0 emoji icons, 0 buy/sell trading actions.
- **Result:** 13/13 passed; full web suite 255/255 passed.

### 9.3 Code Quality & Compilation
- Python: `uv run ruff check` passed with 0 errors; `uv run ruff format` clean.
- TypeScript: `tsc --noEmit` passed with 0 errors across all monorepo packages.
- ESLint: `eslint src/components/charts src/hooks/charts src/lib/charts` passed with 0 errors.
- Production Build: Next.js Turbopack production build (`next build`) compiled successfully with static route generation for `/charts`.
