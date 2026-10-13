# ATLAS — STAGE 52: HOME MARKET SUMMARY ARCHITECTURE
## Real-Time Market Overview and Canonical Financial Data Integration

---

## 1. Executive Summary & Purpose

The **Home Market Summary** provides a compact, truthful, data-driven financial overview on the ATLAS Home operational dashboard (`/home`, Module 1).

It answers seven core financial questions directly from Home without requiring navigation into deep analytical modules:
1. **Which markets or instruments are being followed?** A server-owned curated universe of benchmark indices, ETFs, FX pairs, crypto assets, and commodities.
2. **What is their latest available price or value?** Traded price from canonical quote/state store, preserving Decimal precision.
3. **How have they changed relative to an appropriate reference close?** Validated price movement relative to a completed prior trading session close.
4. **When was the data observed?** Truthful observation timestamps (`source_timestamp` and `received_at`).
5. **Is the displayed data current, delayed, stale, or unavailable?** Direct reuse of the Stage 44 canonical freshness engine.
6. **Which underlying financial instrument does each number represent?** Strict canonical UUID identity (`instrument_entity_id`) anchored in Stage 17 Financial Instrument architecture.
7. **Can the user navigate directly into ATLAS to investigate further?** One-click internal routing to `/markets` with Stage 25 Universal Selected Entity context activation.

### The Most Important Data Rule
**Canonical ATLAS market data is the sole source of truth.**
- 0 fabricated stock prices
- 0 simulated percentage returns
- 0 fake sparklines or mock ticker animations
- 0 direct provider calls from the browser
- 0 third-party iframe price feeds

If ATLAS does not have a verified quote, it displays **"Unavailable"** or **"No active quote"**—never zero placeholders or synthetic data.

---

## 2. Core Architecture & Component Flow

```text
                      ATLAS HOME V1 (/home)
                                │
                                ▼
                        HomeMarketSummary
                                │
                                ▼
                       useHomeMarketSummary
                    (In-memory Query Hook)
                                │
                                ▼
                   GET /api/v1/home/market-summary
                                │
                                ▼
                    HomeMarketSummaryService
                                │
       ┌────────────────────────┼────────────────────────┐
       │                        │                        │
       ▼                        ▼                        ▼
Instrument Config        Live Quote Query         Historical Ref
  & Entity Meta         (Stage 41 Valkey)       (Stage 39 ClickHouse)
       │                        │                        │
       ▼                        ▼                        ▼
   PostgreSQL              Latest State             Daily Bar
  (Entity name)         (Traded / Bid-Ask)       (Prior Completed)
       │                        │                        │
       └────────────────────────┼────────────────────────┘
                                │
                                ▼
                   Stage 44 Freshness & Delay
                                │
                                ▼
                 HomeMarketSummaryResponse (v1)
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
   MarketSummaryInstrumentCard       Stage 42/43 Realtime
   • Tabular price numerals          • market.quote.updated
   • Signed change & dir badge       • Coalesced refetch (>=2s)
   • Stage 44 freshness badge        • Monotonic timestamp race protection
   • Provider provenance
   • Internal /markets navigation
```

---

## 3. Data Authority & System Boundaries

| Concern | Authoritative System | Implementation in Stage 52 |
|---|---|---|
| **Instrument Identity** | Stage 17 Financial Instrument | Canonical UUID authority (`instrument_entity_id: UUID`) |
| **Identifier Metadata** | Stage 21 Universal Identifiers | Ticker / symbol is display metadata only |
| **Entity Resolution** | Stage 22 Entity Resolution | Curated server-side resolution; no ad-hoc string searching |
| **Selected Entity Context** | Stage 25 Universal Context | Card interaction executes `selectEntity(uuid)` |
| **Provider Provenance** | Stages 24 / 28–33 | Provenance keys and safe display names (e.g. OpenBB) |
| **Canonical Quote Model** | Stage 33 Canonical Market Data | `Quote` domain model with Decimal precision |
| **Historical Daily Bars** | Stage 39 ClickHouse Engine | Query completed daily bar (`interval = '1d'`) |
| **Latest Quote State** | Stage 41 Live Quote Service | Read ephemeral state from Valkey/Redis (`LiveQuoteService`) |
| **Realtime Event Transport**| Stages 42–43 Event Pipeline | Subscribes to `market.quote.updated`; triggers bounded refetch |
| **Freshness Classification**| Stage 44 Freshness Monitor | Statuses: `FRESH`, `AGING`, `STALE`, `UNAVAILABLE` |
| **Home Presentation** | Stage 52 Presentation Layer | `HomeMarketSummary`, `MarketSummaryInstrumentCard` |

---

## 4. Curated Instrument Configuration

The Home Market Summary uses a server-owned, statically validated instrument configuration (`python/atlas/src/atlas/home/market_summary/config.py`):

```python
class MarketSummaryInstrumentConfig(BaseModel):
    instrument_entity_id: uuid.UUID
    display_name: str
    display_symbol: str
    instrument_category: str  # market_index, etf, currency, crypto_asset, commodity, equity
    value_kind: str          # price, points, rate
    quote_currency: Optional[str]
    quote_unit: Optional[str]
    display_order: int
    enabled: bool
    is_index: bool
    provider_hint: Optional[str]
```

### Config Constraints & Invariants
- **Bounded Universe**: Strictly maximum 20 items (default: 8 curated core instruments).
- **UUID Authority**: Deterministic namespaced UUIDs (`uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, ...)`). Never uses raw tickers as keys.
- **Monotonic Ordering**: `display_order` must be unique and monotonic.
- **No Invented Entities**: Every instrument represents a real, distinct financial asset.

### Default Curated Instruments (Stage 52)
1. **S&P 500 Index** (`^GSPC`) — Category: `market_index`, Points (`pts`), `is_index: True`
2. **NASDAQ 100 Index** (`^NDX`) — Category: `market_index`, Points (`pts`), `is_index: True`
3. **Dow Jones Industrial** (`^DJI`) — Category: `market_index`, Points (`pts`), `is_index: True`
4. **SPDR S&P 500 ETF** (`SPY`) — Category: `etf`, Currency: `USD`, `is_index: False`
5. **EUR / USD** (`EUR/USD`) — Category: `currency`, Rate, Quote Unit: `USD per EUR`
6. **USD / JPY** (`USD/JPY`) — Category: `currency`, Rate, Quote Unit: `JPY per USD`
7. **Bitcoin** (`BTC/USD`) — Category: `crypto_asset`, Currency: `USD`
8. **Brent Crude** (`BZ=F`) — Category: `commodity`, Currency: `USD`, Unit: `USD/bbl`

---

## 5. Critical Domain Invariants

### 5.1 Index vs. ETF Distinction
An index benchmark and an ETF tracking that index are distinct financial entities:
- **S&P 500 Index (`^GSPC`)**: `is_index = True`, `value_kind = "points"`, `quote_unit = "pts"`. Denominated in index points; **never prefixed with `$`**.
- **SPDR S&P 500 ETF (`SPY`)**: `is_index = False`, `value_kind = "price"`, `quote_currency = "USD"`. Denominated in USD; **prefixed with `$`**.
- **Invariant**: They possess different UUIDs and are never conflated or cross-labeled.

### 5.2 Price Semantics & Traded Value Selection
- If a traded price (`last_price` or `price`) exists on the canonical quote, it is displayed.
- If only `bid_price` and `ask_price` exist, they are preserved in their respective fields.
- **Midpoint Ban**: The system **never** computes `(bid + ask) / 2` and presents it as a traded price.
- **Decimal Precision**: All numbers are stored and calculated as Python `Decimal` objects and serialized as JSON strings. Floating-point conversions in binary JavaScript numbers are avoided.

### 5.3 Reference Close & Change Calculation
Price change is calculated strictly as:
$$\text{absolute\_change} = \text{last\_price} - \text{reference\_close}$$
$$\text{percentage\_change} = \frac{\text{absolute\_change}}{\text{reference\_close}} \times 100$$

**Safeguards:**
1. **Zero Denominator Protection**: If $\text{reference\_close} = 0$, `percentage_change` is set to `None` (division by zero avoided).
2. **Prior Session Integrity**: The reference close must represent a completed historical session from Stage 39 daily bars (`interval = '1d'`) or a validated feed snapshot prior-close. It is **never guessed from "yesterday's date"** (which fails on weekends and market holidays).
3. **Incomplete Sessions Excluded**: An intraday/incomplete bar is never treated as the prior session close.
4. **Missing Reference**: If a valid reference close is unavailable, `absolute_change = None`, `percentage_change = None`, and `change_direction = UNKNOWN`. The latest price is still presented truthfully with the label **"Change unavailable"**.

### 5.4 Freshness & Delivery Delay
Reuses the Stage 44 canonical engine (`MarketDataFreshnessQueryService`):
- `FRESH`: Observation within nominal freshness window (< 5 minutes). Displayed as **Current** (emerald indicator).
- `AGING`: Observation approaching stale threshold (5–15 minutes). Displayed as **Aging** (amber indicator).
- `STALE`: Observation exceeds threshold (> 15 minutes). Displayed as **Stale** (orange indicator).
- `UNAVAILABLE`: No observation. Displayed as **No Feed** (zinc indicator).
- **Delivery Delay**: Distinguishes delayed data (e.g., 15-minute delayed exchange feeds) from stale data. Recently received delayed quotes are labeled **"15m Delayed"**, not "Live".

---

## 6. Read-Only Backend Contract

### Endpoint
```http
GET /api/v1/home/market-summary
```

### Authorization
- Authenticated user required (`get_current_user`).
- Mandatory permission: `atlas.access`.
- Headers: `Cache-Control: private, no-store`.

### Side-Effect Verification
A request to `GET /api/v1/home/market-summary` executes:
- PostgreSQL writes: **0**
- Valkey/Redis writes: **0**
- ClickHouse writes: **0**
- External Provider HTTP/stream calls: **0**
- Ingestion jobs scheduled: **0**
- Notifications or alerts triggered: **0**

### API Response Schema (Version 1)
```json
{
  "schema_version": 1,
  "generated_at": "2026-10-13T12:00:00.000000Z",
  "coverage": {
    "configured_count": 8,
    "available_count": 8,
    "unavailable_count": 0
  },
  "items": [
    {
      "instrument_entity_id": "02ddbbd5-1c31-50e5-950c-e274ee794026",
      "display_name": "S&P 500",
      "display_symbol": "^GSPC",
      "instrument_category": "market_index",
      "value_kind": "points",
      "quote_currency": "USD",
      "quote_unit": "pts",
      "last_price": "5050.50",
      "bid_price": null,
      "ask_price": null,
      "absolute_change": "50.50",
      "percentage_change": "1.01",
      "change_direction": "up",
      "source_timestamp": "2026-10-13T11:59:50Z",
      "received_at": "2026-10-13T11:59:50.050Z",
      "freshness_status": "fresh",
      "delivery_delay_status": "realtime",
      "delay_seconds": 0,
      "provider_key": "openbb",
      "provider_display_name": "OpenBB Financial Platform",
      "reference_close": "5000.00",
      "reference_session_date": "2026-10-12",
      "reference_source": "clickhouse_daily_bar",
      "data_status": "available",
      "unavailable_reason": null
    }
  ]
}
```

---

## 7. Frontend Integration & UI Architecture

### 7.1 Component Structure
```text
HomeMarketSummary
   ├── Surface Header
   │     ├── Title: "Market Summary"
   │     ├── Subtitle: "Latest observations from connected market infrastructure"
   │     ├── Coverage Badge: "X/Y Available"
   │     ├── Refresh Button (Manual Refetch with spin animation)
   │     └── "Open Markets" Link (/markets)
   │
   ├── Loading Skeleton (8 pulsing card placeholders)
   ├── Empty State (No instruments configured)
   ├── Error State (Connection failure with retry button)
   │
   └── Grid of MarketSummaryInstrumentCard
         ├── Card Header: Display Name, Symbol Badge, Category Uppercase
         ├── Price Body: Tabular numeral, unit label, directional change badge
         └── Card Footer: Freshness dot & label, delay badge, safe provider name
```

### 7.2 Data Synchronization & Snapshot Race Protection
- **Stale Time**: 15 seconds in-memory cache.
- **Refetch Triggers**: Window focus, network reconnect, manual button click.
- **Live Event Coalesced Refetch**: When `atlas:market.quote.updated` fires, the hook triggers a rate-limited refetch (coalesced to maximum once every 2 seconds).
- **Monotonic Snapshot Ordering**: If an HTTP snapshot response returns with a `generated_at` earlier than the currently accepted state, it is safely discarded. Older network responses cannot overwrite newer accepted observations.

### 7.3 Accessibility & Terminal Design Tokens
- Strict alignment to ATLAS design system tokens (`--atlas-bg-0`, `--atlas-surface-1`, `--atlas-border-default`, `--atlas-text-primary`).
- Cards implement `role="button"`, `tabIndex={0}`, and handle keyboard interaction (`Enter` and `Space`).
- Accessible ARIA label: `"Open [Display Name] in Markets"`.
- Tabular numerals (`tabular-nums font-mono`) prevent digit jitter during price updates.
- Color is not the sole indicator of movement: signed plus/minus characters and directional arrows (`ArrowUpRight`, `ArrowDownRight`) accompany color badges.

---

## 8. Stage Boundaries & Deferred Features

| Feature | Assigned Roadmap Stage | Stage 52 Status |
|---|---|---|
| **Home Market Summary** | **Stage 52** | **Implemented** |
| Home Personalized Activity | Stage 53 | Deferred (Slot reserved) |
| Home Tasks & Approvals | Stage 54 | Deferred (Slot reserved) |
| Home Intelligence Feed | Stage 55 | Deferred (Slot reserved) |
| Markets Overview (Full Module) | Stage 56 | Deferred |
| Equities / ETF / FX / Crypto Modules | Stages 57–62 | Deferred |
| Market Movers (Top Gainers/Losers) | Stage 63 | Banned in Stage 52 |
| Market Heatmaps | Stage 64 | Banned in Stage 52 |
| Cross-Asset Analytics | Stage 65 | Banned in Stage 52 |
| Interactive Chart Engine | Stage 66 | Banned in Stage 52 |
| Technical Indicators (RSI, MACD) | Stages 69–70 | Banned in Stage 52 |
| User Watchlists & Price Alerts | Stages 76–80 | Deferred |
| AI / LLM Market Commentary | Stage 124+ | Banned in Stage 52 |

---

## 9. Verification & Quality Gates Summary

- **Backend Unit & Integration Tests**: 25 passed in `apps/api/tests/home/test_market_summary.py` (config validation, Decimal math, read-only guarantees, partial availability, Redis/ClickHouse/PostgreSQL failure handling, endpoint auth/authz).
- **Frontend Formatting & Static Tests**: 16 passed in `apps/web/tests/home-market-summary.test.ts` (currency symbols, crypto precision, index points, signed changes, snapshot race condition ordering, no-fake-data static verification).
- **TypeScript Typecheck**: Clean (0 errors via `tsc --noEmit`).
- **ESLint**: Clean (0 errors, 0 warnings on Stage 52 files via `eslint`).
- **Python Ruff**: Clean (`ruff check` and `ruff format --check` passed).
- **Next.js Production Build**: Turbopack build passed cleanly with 29 optimized routes.
