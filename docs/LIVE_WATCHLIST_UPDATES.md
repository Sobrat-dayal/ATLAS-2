# ATLAS — Live Watchlist Updates V1 (Stage 78)

## 1. Overview & Master Architectural Directive

**Stage 78** transforms ATLAS Watchlists into a professional, institutional-grade **live financial market monitoring interface**. It integrates the persistent multi-asset watchlists from Stage 76 and the typed configurable column registry from Stage 77 with ATLAS's canonical market-data streaming infrastructure (Stages 33, 41, 42, 43, and 44).

### Key Invariants & Principles
- **Consumer of Existing Infrastructure:** The Watchlist is a consumer of ATLAS's canonical market-data streaming system. It is **never** a second streaming pipeline.
- **Single Shared WebSocket:** Reuses the Stage 43 shared WebSocket singleton (`SharedWebSocketClient`). Never creates a separate WebSocket connection per row, per watchlist, or per provider.
- **Reference Counting:** Multi-consumer subscription sharing across watchlists and chart modules with strict reference counting.
- **Strict Financial Semantics:** Preserves canonical quotation units, base/quote FX orientation, crypto asset denominations, and exact distinctions between executed `Last`, indicative `Bid`/`Ask`, synthetic `Mid`, bond clean price vs. yield, and mutual fund `NAV`.
- **Zero Fabrication:** Never fabricates fake ticks, artificial prices, or synthetic trading volume.
- **Strict Scope Boundaries:** Strictly excludes Stage 79 (fundamentals, technical indicators, news enrichment) and Stage 80 (price and volume alerts).

---

## 2. Streaming Architecture & Shared Transport

```
   EXISTING MARKET DATA PROVIDERS (Polygon, Tiingo, FXCM, Binance, etc.)
                               |
                               v
                     Stage 41 Quote Ingestion
                               |
                               v
                     Stage 33 Canonical Quote
                               |
                               v
                   Stage 42 Market Event Pipeline
                               |
                +--------------+--------------+
                |                             |
                v                             v
          Redis Latest State        WebSocket Event Stream
                                              |
                                              v
                                  Stage 43 Shared WebSocket
                                  (/api/v1/realtime/ws)
                                              |
                                              v
                                  Entitlement Authorization
                                              |
                                              v
                                  Shared Subscription Registry
                                  (Multi-Consumer Ref Count)
                                              |
                                              v
                                   WatchlistLiveController
                                              |
                     +------------------------+------------------------+
                     |                        |                        |
                     v                        v                        v
            Viewport Planning          Event Ordering &         Startup / Reconnect
          (Visible Rows + Overscan)      Deduplication            Reconciliation
                     |                        |                        |
                     +------------------------+------------------------+
                                              |
                                              v
                                 Canonical Latest Quote State
                                              |
                                              v
                                 Stage 77 Column Registry
                                 (Typed Financial Projection)
                                              |
                                              v
                                     RenderBatcher
                                (Coalesced 80ms Frames)
                                              |
                                              v
                                 Live Financial Table UI
```

---

## 3. Subscription Identity & Shared Reference Counting

### Canonical Subscription Key
Subscriptions are keyed by canonical financial series identity, never raw ticker text:
```typescript
interface QuoteSubscriptionKeyDTO {
  instrument_entity_id: string; // Canonical UUID
  symbol?: string;              // Ticker representation
  venue?: string;               // Execution venue (NASDAQ, NYSE, FXCM, etc.)
  quote_currency?: string;      // Quotation currency (USD, EUR, etc.)
  asset_class?: string;         // Asset class (equity, crypto, fx, etc.)
}
```
Key serialization format: `quote:{instrument_entity_id}` or `quote:{symbol}:{venue}` (normalized to lowercase).

### Multi-Consumer Reference Counting
- If Instrument A appears in Watchlist 1, Watchlist 2, and an active Chart panel, exactly **one** subscription exists on the wire.
- Active references are tracked in `SeriesSubscriptionRecord.callbacksByConsumer`.
- When a consumer unsubscribes or navigates away, its reference is decremented. An unsubscription message is dispatched over the wire **only** when the reference count drops to 0.

---

## 4. Server-Side Entitlement Authorization

`MarketDataEntitlementService` validates all subscription requests on the server:
- **Delayed vs. Realtime Feeds:** Users on standard tiers or free accounts receive delayed market data (`delivery_delay_status: "delayed"`). Realtime streaming is granted only to entitled enterprise/pro tiers.
- **Level 2 / Restricted Venue Protection:** Strict licensing checks prevent unauthorized access to proprietary depth or restricted venues.
- **Typed Acknowledgment:** The server replies with `subscription.ack` containing explicitly `accepted` and `rejected` series keys with rejection reasons (`unauthorized`, `capacity_exceeded`, `delayed_feed_only`).
- **No Client Tampering:** Client-side display settings cannot bypass server entitlement boundaries.

---

## 5. Viewport-Aware Subscription Management

To prevent resource exhaustion when displaying watchlists with hundreds of instruments:
1. **Visible Row Prioritization:** Desired subscriptions are calculated from the currently rendered viewport window (`startIndex` to `endIndex`).
2. **Bounded Overscan:** An overscan buffer (default: 10 rows above and below) is included to enable smooth scrolling without subscription latency.
3. **Scroll Debounce:** Fast scroll interactions are debounced (150ms) to eliminate subscription storms.
4. **Background Tab Suspension:** When the browser tab is hidden (`document.visibilityState === "hidden"`), viewport subscriptions are suspended while preserving global subscriptions required by other consumers. Subscriptions automatically re-synchronize when the user returns.

---

## 6. Canonical Market Event Validation & Ordering

### Event Validation Contract
`validateCanonicalQuoteEvent` rejects malformed or corrupted events before state application:
- **Schema Version:** Must match schema version 1.
- **Instrument Identity:** Validates canonical UUID format.
- **Finite Decimal Check:** Validates that prices are finite numbers; rejects `NaN`, `Infinity`, or string garbage.
- **Zero & Negative Price Handling:** Preserves genuine `0.00` values (e.g. expired options). Rejects negative prices on standard asset classes while permitting negative settlement prices on qualifying commodities (e.g., WTI crude futures `CLZ26`).

### Source-Scoped Ordering & Gap Detection
`EventOrderingTracker` maintains monotonic watermarks per instrument:
- **Chronological Ordering:** Uses the observation timestamp (`as_of` / `source_timestamp`). Older events arriving late are rejected (`isOutOfOrder: true`).
- **Duplicate Protection:** Bounded LRU event ID cache rejects duplicate deliveries (`isDuplicate: true`).
- **Sequence Gap Detection:** When upstream provider sequences are present, non-consecutive jumps trigger gap detection (`hasSequenceGap: true`), signaling degraded continuity and requesting canonical state reconciliation.

---

## 7. Snapshot and Stream Reconciliation

### Startup Race Resolution
When opening a watchlist, two asynchronous flows race:
1. HTTP snapshot fetch of initial quotes.
2. Realtime WebSocket subscription stream.

`SnapshotStreamReconciler` eliminates race conditions:
- While an initial snapshot is in-flight, incoming stream events are placed in a bounded buffer (capacity: 100 events).
- When the HTTP snapshot arrives, its timestamp is compared against buffered stream events.
- **Snapshot Dominance Rule:** If a buffered stream event has a newer observation timestamp than the snapshot, the stale snapshot is **rejected**, and the newer streamed event is applied.
- If the buffer overflows, oldest events are dropped, and a canonical resynchronization is requested.

---

## 8. Financial Quote Semantics & Precision

| Asset Class | Quote Measure | Semantics & Presentation |
|---|---|---|
| Equities | `Last` | Executed market trade price. |
| FX / Currencies | `Mid` | Arithmetic midpoint between executable Bid and Ask. Preserves base/quote orientation. |
| Commodities / Futures | `Last` / `Settlement` | Executed trade or daily exchange settlement. Negative prices supported where permitted. |
| Crypto | `Last` | Executed trade in exact quote denomination (e.g. USDT distinct from USD). |
| Mutual Funds | `NAV` | Net Asset Value valuation fixing; never relabeled as intraday executed trade. |
| Bonds | `Clean Price` | Quoted clean price; never conflated with yield to maturity. |

---

## 9. Table Performance & Fine-Grained Rendering

- **RenderBatcher:** Coalesces high-frequency market events into batched 80ms animation frames, eliminating UI lockup during market volatility bursts.
- **Granular Updates:** Only updated cells rerender; the entire AppShell and unaffected table rows remain untouched.
- **Directional Movement Cues:** Compares incoming price against previously displayed price for the exact same measure. Displays subtle directional arrows (`▲`, `▼`, `―`) and background highlights (`bg-emerald-500/10`, `bg-rose-500/10`).
- **Accessibility:** Honors `prefers-reduced-motion` media query by disabling pulse animations.
- **Sorting Integrity:** Retains stable manual order between explicit refreshes. A dedicated "Re-sort" control reapplies multi-column sorts against the latest live prices without disruptive row jumping.

---

## 10. Security & Entitlement Architecture

- **Authenticated Subscriptions:** Subscriptions reuse Stage 13 authentication tokens exchanged for ephemeral connection tickets (`/api/v1/realtime/websocket-ticket`).
- **Server-Side Entitlement Checks:** Every requested series key is checked against the user's licensing profile (`MarketDataEntitlementService`). Guessed topics or unauthorized Level 2 instruments return typed rejection records.
- **Realtime vs. Delayed Licensing:** Users on standard tiers receive delayed market data (`delivery_delay_status: "delayed"`). Realtime feeds are only streamed to entitled professional accounts.
- **Zero Client Credential Leakage:** Upstream provider API keys and authorization headers remain exclusively server-side.
- **Resource Limits:** Connection budgets (max 10 series per subscribe message, max 25-50 series per connection) prevent subscription flood abuse.
- **Zero Financial Side-Effects:** Live quote delivery never places trading orders, creates portfolio transactions, triggers background workflows, or initiates LLM calls.

---

## 11. Freshness & Data Quality Classification

ATLAS keeps WebSocket connection state and market-data freshness strictly orthogonal:
- **Connected Socket $\neq$ Realtime Data:** A green WebSocket connection indicator reflects active network transport, not fresh exchange prints.
- **Observation Time vs. Receipt Time:** The observation timestamp (`source_timestamp` / `as_of`) records when the trade/quote occurred at the exchange/venue. Ingestion receipt time (`received_at`) is logged independently and never replaces market observation time.
- **Duplicate Ticks:** Duplicate deliveries do not refresh observation timestamps or transform stale observations into fresh data.
- **Verified Market Closure:** Markets are marked Closed only using verified exchange calendar sessions, never guessed from event silence.
- **Mixed-Quality Watchlists:** When a watchlist contains both realtime and delayed series, the aggregate status reflects `Mixed Quality`, while individual row badges display exact per-series freshness.

---

## 12. Accessibility, Responsiveness & Visual Restraint

- **Keyboard Usability:** All table headers, sort toggles, row actions, dialogs, and reconnect buttons remain completely accessible via keyboard navigation.
- **Screen-Reader Throttling:** Screen-reader live regions (`aria-live="polite"`) announce intentional user actions (e.g., row reordering, sort changes) while suppressing high-frequency price tick announcements.
- **Reduced Motion Support:** Respects `prefers-reduced-motion: reduce` by disabling row background highlight pulses and animation transitions.
- **Responsive Layout:** Compatible with screen viewports from 320px mobile devices to 1920px+ institutional widescreen workstations, coexisting cleanly with the Agent Dock and Bottom Taskbar.
- **Institutional Visual Language:** Reuses ATLAS design tokens with zero purple gradients, zero cartoon emojis, zero fake stock tickers, and zero artificial price animations.

---

## 13. Roadmap Scope Boundaries

| Stage | Feature Area | Status in Stage 78 |
|---|---|---|
| **Stage 76** | Watchlists V1: Persistent Multi-Asset Watchlists, Membership, CRUD, Snapshots | **COMPLETE** |
| **Stage 77** | Advanced Watchlist Columns: Column Registry, Width Resizing, Pinning, Multi-Column Sort | **COMPLETE** |
| **Stage 78** | Live Watchlist Updates: Realtime Streaming, Reference Counting, Reconciliation, Freshness | **COMPLETE** |
| **Stage 79** | Fundamental, Technical, Event and News Watchlist Enrichment | **DEFERRED** |
| **Stage 80** | Watchlist Alerts (Price thresholds, volume spikes, push notifications) | **DEFERRED** |

---

## 14. Verification & Quality Gates

All automated quality gates pass cleanly:
- **Backend Tests:** 57 passing pytest suites (`test_watchlists.py`, `test_watchlist_columns.py`, `test_watchlist_live.py`).
- **Frontend Tests:** 25 passing Node.js/tsx tests (`watchlist-live.test.ts`, `watchlists.test.ts`, `watchlist-columns.test.ts`).
- **Type Checking:** TypeScript typecheck (`tsc --noEmit`) passes with 0 errors.
- **Lint & Format:** Python Ruff check and format pass cleanly with 0 errors; ESLint on target watchlist/realtime modules passes with 0 errors and 0 warnings.
- **Production Build:** Next.js production build (`next build`) passes cleanly with all 38 application routes statically/dynamically generated.
