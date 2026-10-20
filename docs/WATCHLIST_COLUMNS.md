# ATLAS — Watchlist Columns V1 (Stage 77)

## Architectural Source-of-Truth Document

---

## 1. Overview & System Mission

Stage 77 of the canonical 150-stage ATLAS development roadmap transforms ATLAS Watchlists from a fixed-layout monitoring table into a **professional customizable financial monitoring table**, matching the usability, information density, and strict correctness of Bloomberg Terminal, TradingView, and institutional workstations.

### Core Architectural Principle
> **A watchlist column describes how an authorized, canonical piece of financial information is selected, qualified, formatted and displayed. It does not create a new source of financial truth.**

The Watchlists module preserves Stage 76's authoritative membership, row ordering, and canonical financial identities while enabling:
- Central typed **Column Registry** with 14 approved operational columns.
- Dynamic **Show/Hide** with mandatory identifying symbol enforcement.
- Horizontal **drag-and-drop & keyboard reordering**.
- Responsive **column resizing** with clamped bounds ([min_width, max_width]).
- Multi-column **left pinning** with pixel-accurate sticky offset calculations.
- Financially valid **3-state sorting** with deterministic tie-breaking and missing-values-last semantics.
- Whole-watchlist dataset sorting across pagination.
- **PostgreSQL-backed preference persistence** (`watchlist_column_preferences`) with optimistic concurrency control (`revision`).
- Single-query batched data projection without upstream provider fanout.

---

## 2. Strict Roadmap Boundaries

| Stage | Capability | Ownership Status |
|---|---|---|
| **76** | Watchlists V1: Persistent Multi-Asset Lists & Membership | **Authoritative Base** |
| **77** | Advanced Watchlist Columns: Registry, Preferences, Resizing, Pinning, Sorting | **Current Stage (Completed)** |
| 78 | Live Watchlist Updates: WebSockets, Tick Streaming, Realtime Cues | *Deferred to Stage 78* |
| 79 | Watchlist Enrichment: Fundamentals, Ratios, Technicals, Events, News | *Deferred to Stage 79* |
| 80 | Watchlist Alerts: Price Thresholds, Volume Signals, Schedulers | *Deferred to Stage 80* |

### Explicit Invariants
1. **Zero Provider Fanout**: No external market data calls are triggered when adding, configuring, or reordering columns.
2. **Zero Fabricated Values**: Missing quotes, unavailable reference prices, or inapplicable assets display neutral `—` with typed status `UNAVAILABLE`, never faked zeros.
3. **Zero Formula Engines**: No user-supplied JavaScript, Python, SQL, or arbitrary formulas are executed.
4. **No Realtime Flashing / Streaming**: Live price flashing and WebSockets belong exclusively to Stage 78.
5. **No Screener Functions**: Cross-market multi-factor ranking belongs to Stages 94–98.

---

## 3. The Typed Column Registry

All available columns are defined in trusted application code with stable, immutable identifiers:

```
Watchlist Column Registry
           │
           ▼
   Column Capability Model
           │
           ▼
     Column Configuration (V1)
           │
           ▼
    Column Data Projection
           │
           ▼
    Typed Financial Values
           │
           ▼
     Column Cell Renderer
           │
           ▼
    Configurable Watchlist Table
```

### Approved Column Catalog (14 Operational Columns)

| Column ID | Label | Category | Value Type | Source Capability | Supported Assets | Default Visible | Default Width | Bounds [Min, Max] | Sort Policy | Pinnable |
|---|---|---|---|---|---|---|---|---|---|---|
| `instrument.symbol` | Symbol | identity | IDENTIFIER | canonical_instrument | All | **Yes (Required)** | 140px | [90, 260] | alpha | **Yes** |
| `instrument.name` | Instrument Name | identity | TEXT | canonical_instrument | All | Yes | 220px | [140, 400] | alpha | **Yes** |
| `instrument.asset_class` | Asset Class | identity | ENUM | canonical_instrument | All | Yes | 110px | [80, 180] | alpha | No |
| `instrument.subtype` | Subtype | identity | TEXT | canonical_instrument | All | No | 130px | [90, 200] | alpha | No |
| `instrument.identifier` | Identifier | identity | IDENTIFIER | entity_identifiers | All | No | 140px | [100, 240] | alpha | No |
| `market.venue` | Venue / Market | market | TEXT | market_series | All | Yes | 120px | [80, 200] | alpha | No |
| `market.currency` | Quote Currency | market | ENUM | market_series | All | No | 100px | [70, 150] | alpha | No |
| `market.listing_country` | Country | market | TEXT | canonical_instrument | All | No | 90px | [60, 140] | alpha | No |
| `quote.latest_measure` | Latest Measure | quote | MONETARY | latest_quote | All | Yes | 130px | [100, 200] | numeric | No |
| `quote.change` | Change | quote | PERCENTAGE | latest_quote | All | Yes | 130px | [100, 220] | numeric | No |
| `quote.kind` | Quote Kind | quote | TEXT | latest_quote | All | No | 110px | [80, 160] | alpha | No |
| `quote.as_of` | As Of | quote | TIMESTAMP | latest_quote | All | No | 120px | [90, 180] | chronological | No |
| `quality.freshness` | Freshness | quality | STATUS | freshness_monitor | All | Yes | 120px | [90, 170] | alpha | No |
| `quality.source` | Source | quality | TEXT | provenance | All | No | 120px | [90, 180] | alpha | No |

---

## 4. Multi-Asset Financial Correctness

Columns preserve the underlying canonical domain model of different asset classes:
- **Equities**: Quotes represent executable Last traded price relative to prior official session Close.
- **Mutual Funds / ETFs**: Differentiates exchange-traded intraday Last from dated official NAV valuations.
- **FX / Currencies**: Recognizes indicative Bid, Ask, and calculated Mid quotes; never invents an exchange Last trade.
- **Cryptocurrencies**: Preserves spot pair conventions, quote token denominations (USD, USDT), and 24-hour vs exchange session boundaries.
- **Bonds**: Distinguishes Clean Price, Dirty Price, and Yield to Maturity.
- **Futures**: Preserves root contract identity, expiration month, and settlement vs last trade distinctions.

### Missing Values & Neutral Dash
A missing quote is distinct from a zero price. When market observation is unavailable:
- Status: `UNAVAILABLE`
- Formatted Text: `—`
- Accessible Reason: e.g. "Quote observation unavailable"

---

## 5. Financially Correct Sorting

### 3-State Sort Cycle
Clicking a sort-capable column header cycles through:
1. `ASC` (Ascending)
2. `DESC` (Descending)
3. `null` (Revert to Stage 76 manual membership order)

### Deterministic Tie-Breaking
Ties in parsed value are broken deterministically by:
1. `manual_position` (Stage 76 membership position ascending)
2. `item_id` (UUID string comparison)

### Missing-Values-Last Semantics
In both `ASC` and `DESC` sorting modes, rows with missing, stale, or inapplicable values always sort at the end of the table, retaining their relative manual order.

### Unit Compatibility Protection
When sorting on monetary measure (`quote.latest_measure`), if items belong to different currencies (e.g. USD vs INR), `incompatible_units_detected` is flagged and values are clustered by currency before numerical comparison to prevent false cross-currency rankings.

### Whole-Dataset Pagination Sorting
Sorting operates over the **complete authorized watchlist dataset** (up to 250 items), never misleadingly ranking only the current pagination page slice.

---

## 6. Table Layout, Pinning & Resizing

### Left Pinning & Sticky Offsets
- The required `instrument.symbol` column and optional `instrument.name` can be pinned to the left.
- Sticky offsets are computed cumulatively from actual widths:
  $$\text{Offset}_i = \text{BaseOffset} (72\text{px}) + \sum_{j < i, j \in \text{Pinned}} \text{Width}_j$$
- Pinned columns carry `position: sticky`, elevated `z-index`, and subtle border separators.

### Resizing Gestures
- Dragging the resize handle on header borders updates the width in real time without lag.
- Widths are clamped to `[col.min_width, col.max_width]`.
- Changes are committed on gesture release and debounced before persisting to PostgreSQL.

---

## 7. PostgreSQL Persistence & Concurrency

### Database Table
```sql
CREATE TABLE watchlist_column_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    configuration_schema_version INTEGER NOT NULL DEFAULT 1,
    revision INTEGER NOT NULL DEFAULT 1,
    configuration_jsonb JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_watchlist_column_preferences_watchlist UNIQUE (watchlist_id)
);
```

### Optimistic Concurrency Control
- Monotonic `revision` increments on every save.
- Supported through HTTP `If-Match: W/"{revision}"`.
- Stale updates return `HTTP 412 Precondition Failed` (or `409 Conflict`), prompting the user and reloading latest server preferences without destroying unsaved work.

---

## 8. REST API Endpoints

All endpoints require authentication and enforce watchlist ownership:
- `GET /api/v1/watchlists/columns`: List approved catalog of column definitions.
- `GET /api/v1/watchlists/{id}/columns`: Read active column preferences and revision.
- `PUT /api/v1/watchlists/{id}/columns`: Persist normalized configuration with revision check.
- `POST /api/v1/watchlists/{id}/columns/reset`: Revert watchlist columns to canonical default layout.
- `GET /api/v1/watchlists/{id}/rows`: Query projected rows with typed cell values and global sorting.

---

## 9. Roadmap Scope Boundaries

| Stage | Feature Area | Status in Stage 78 |
|---|---|---|
| **Stage 76** | Watchlists V1: Persistent Multi-Asset Watchlists, CRUD, Drag-and-Drop, Snapshots | **COMPLETE** |
| **Stage 77** | Advanced Configurable Watchlist Columns (Custom columns, presets, formulas) | **COMPLETE** |
| **Stage 78** | Live Watchlist Updates (Streaming WebSockets, per-row tick flashing, reconciliation) | **COMPLETE** |
| **Stage 79** | Fundamental, Technical, Event and News Watchlist Enrichment | **DEFERRED** |
| **Stage 80** | Watchlist Alerts (Price thresholds, volume spikes, push alerts) | **DEFERRED** |
