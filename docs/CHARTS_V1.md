# ATLAS Charts V1 — Institutional Financial Charting Workspace

**Canonical Roadmap Stage: 66**  
**Module Route:** `/charts`  
**Status:** Complete  
**Engine:** Lightweight Charts (`lightweight-charts@5.2.1`, Apache-2.0)  
**Read Authority:** Canonical Market Data Service / ClickHouse (`historical_market_bars_versions FINAL`)  

---

## 1. Executive Summary & Vision

Stage 66 delivers **Charts V1**, the foundational financial charting workspace for ATLAS. Inspired by Bloomberg Terminal and TradingView, Charts V1 establishes an institutional, information-dense workspace centered on financial data integrity, deterministic chronological ordering, and transparent data provenance.

Charts V1 provides:
1. A dedicated workspace at `/charts`.
2. Institutional candlestick and close-line price visualization.
3. Canonical financial instrument resolution across all supported asset classes (Equities, ETFs, FX, Crypto, Sovereign Debt, and Futures).
4. Strict OHLC envelope validation (`high >= max(open, close, low)` and `low <= min(open, close, high)`).
5. Support for valid negative commodity futures prices (e.g., WTI Crude `CLZ26`).
6. Truthful volume semantics (distinguishing zero volume from unavailable OTC FX or bond volume).
7. Single verified baseline interval: `1D` (daily bars).
8. Interactive pan, zoom, crosshair data inspection, and bounded historical backfill.
9. Screen-reader accessible historical data table.
10. Strict read-only guarantees: 0 database writes, 0 live quote mutations, 0 provider calls on read.

---

## 2. Roadmap Position & Strict Boundaries

To maintain software architecture integrity across the 150-stage roadmap, Stage 66 establishes the baseline rendering and read engine while strictly deferring later-stage functionality:

| Roadmap Stage | Scope / Assigned Capability | Stage 66 Status |
| :--- | :--- | :--- |
| **Stage 66** | **Charts V1: Historical OHLCV, Candlesticks & Line, 1D Baseline** | **IMPLEMENTED** |
| Stage 67 | Live Chart Streaming, Tick-to-Bar Aggregation, Active Bar Mutation | Deferred |
| Stage 68 | Multi-Timeframe Selectors (1m, 5m, 1h, 1W), Resampling, Alternate Chart Types | Deferred |
| Stage 69 | Technical Indicator Infrastructure (SMA, EMA, RSI, MACD, Bollinger Bands) | Deferred |
| Stage 70 | TA-Lib Integration & Complex Quant Studies | Deferred |
| Stage 71 | Interactive Drawing Tools (Trendlines, Rays, Fibonacci, Channels) | Deferred |
| Stage 72 | Multi-Chart Layouts (Split, 2x2, Grid Workspace) | Deferred |
| Stage 73 | Cross-Chart Synchronization (Linked Crosshairs, Unified Timeframes) | Deferred |
| Stage 74 | Saved Chart Layouts, Cloud Persistence, User Templates | Deferred |
| Stage 75 | Historical Chart Replay Engine | Deferred |
| Stage 144 | Chart Trading, Order Placement, Execution Ladders | Deferred |

---

## 3. Financial Data Integrity Principles

1. **No Fabricated History:** If 15 historical bars exist for an instrument, exactly 15 bars are rendered. No synthetic candles or artificial gaps are generated.
2. **No Intraday Observation Synthesis:** Daily bars are never sliced into artificial hourly or minute bars without genuine high-frequency source data.
3. **No Synthetic Continuous Futures:** Futures contracts are queried by explicit contract maturity (e.g., `CLZ26`, December 2026 Crude Oil). Expired or distinct contracts are never stitched into synthetic continuous series.
4. **No Cross-Provider Candle Mixing:** An OHLC candle represents a single coherent observation from a qualified provider. Open from Provider A is never combined with Close from Provider B.
5. **Negative Price Support:** In accordance with Stage 62 derivatives semantics, commodity futures support negative prices (e.g., historical WTI sub-zero settlement). Negative prices are not clamped to zero or converted to absolute values.
6. **Volume Truthfulness:** Traded volume is asset-class specific. OTC FX spot and evaluated sovereign bonds lack centralized volume feeds; their volume is reported as `None` (`—`) rather than synthetic zero.
7. **Adjustment Basis Transparency:** Equities explicitly declare their adjustment status (`RAW`, `SPLIT_ADJUSTED`, `TOTAL_RETURN_ADJUSTED`).

---

## 4. Baseline Interval Policy

Stage 66 enforces a single verified baseline interval:
```
1D (Daily Bars)
```
Historical daily bars reflect exchange-local trading sessions without accidental timezone drift. Requests for other intervals (e.g., `1m`, `5m`, `1h`) are rejected with `HTTP 400 Bad Request` citing Stage 68 roadmap deferral.

---

## 5. Architecture & Engine

### 5.1 Charting Engine Selection
- **Library:** `lightweight-charts` (Version `5.2.1`)
- **License:** Apache License 2.0 (open-source TradingView library)
- **Attribution:** TradingView Lightweight Charts™
- **SSR Strategy:** Client-only rendering via dynamic imports and Next.js `"use client"` component boundary with `<Suspense>` fallback.
- **Lifecycle Management:** Clean instantiation, window `ResizeObserver` subscription, theme synchronization (dark/light tokens), and explicit `chart.remove()` on component unmount to eliminate memory leaks.

### 5.2 Backend Service & Storage
- **Read Path:** `HistoricalChartService` -> `HistoricalChartRepository` -> ClickHouse `historical_market_bars_versions FINAL`.
- **Revision Handling:** Uses `FINAL` and deterministic latest revision tie-breaking on `(instrument_entity_id, bar_timestamp, interval)`.
- **Decimal Safety:** Authoritative OHLC values are processed and validated as `Decimal` instances before conversion to JSON-serializable floating point or decimal strings.

---

## 6. API Specification

### 6.1 Instruments Catalog
```http
GET /api/v1/charts/instruments
```
**Response:**
```json
{
  "total": 13,
  "results": [
    {
      "entity_id": "a0000000-0000-0000-0000-000000000001",
      "display_symbol": "SPY",
      "display_name": "SPDR S&P 500 ETF Trust",
      "asset_class": "etfs",
      "primary_venue": "ARCA",
      "currency": "USD",
      "quotation_unit": "USD/share",
      "source_provider": "canonical_feed",
      "supported_intervals": ["1d"]
    }
  ]
}
```

### 6.2 Historical Chart Bars
```http
GET /api/v1/charts/history?symbol=SPY&interval=1d&limit=250
```
**Parameters:**
- `symbol` (optional): Display ticker (e.g. `SPY`, `BTCUSDT`, `CLZ26`).
- `instrument_entity_id` (optional): Authoritative instrument UUID.
- `interval` (required): Must be `1d` for Stage 66.
- `start` (optional): Inclusive ISO 8601 UTC start datetime.
- `end` (optional): Exclusive ISO 8601 UTC end datetime.
- `limit` (optional): Integer between 10 and 2000 (default: 250).
- `before` (optional): Cursor timestamp for older-history pagination.

**Response Structure:**
```json
{
  "schema_version": "1.0",
  "instrument": {
    "entity_id": "a0000000-0000-0000-0000-000000000001",
    "display_symbol": "SPY",
    "display_name": "SPDR S&P 500 ETF Trust",
    "asset_class": "etfs",
    "primary_venue": "ARCA",
    "currency": "USD",
    "quotation_unit": "USD/share",
    "source_provider": "canonical_feed"
  },
  "interval": "1d",
  "price_basis": "CLOSE",
  "adjustment_basis": "SPLIT_ADJUSTED",
  "bars": [
    {
      "time_unix": 1792195200,
      "timestamp": "2026-10-16T00:00:00Z",
      "open": 585.10,
      "high": 587.40,
      "low": 584.20,
      "close": 586.30,
      "volume": 48200000,
      "source_provider": "canonical_feed"
    }
  ],
  "coverage": {
    "requested_start": null,
    "requested_end": null,
    "earliest_available_bar": "2026-09-01T00:00:00Z",
    "latest_available_bar": "2026-10-16T00:00:00Z",
    "total_bars_returned": 34,
    "is_complete": true
  },
  "pagination": {
    "has_more": false,
    "next_cursor": null,
    "limit": 250
  }
}
```

---

## 7. Supported Multi-Asset Coverage

Charts V1 provides validated historical chart data across 6 financial asset classes:

| Asset Class | Symbols Available | Quote Unit | Adjustment / Price Basis | Volume Semantics |
| :--- | :--- | :--- | :--- | :--- |
| **Equities** | `AAPL`, `MSFT`, `NVDA` | USD/share | Split Adjusted | Real shares traded |
| **ETFs** | `SPY`, `QQQ` | USD/share | Market Price (not NAV) | Real shares traded |
| **FX Spot** | `EURUSD`, `USDJPY` | Rate ratio | Midpoint rate | None (`—`, OTC market) |
| **Crypto** | `BTCUSDT`, `ETHUSDT` | USDT/coin | Spot Trade | Real base units |
| **Bonds** | `US10Y` | % yield / face | Clean Price | None (`—`, OTC benchmark) |
| **Futures** | `CLZ26`, `GCZ26`, `ESZ26` | USD/bbl, USD/oz, Index pts | Settlement price (Negative valid) | Contracts traded |

---

## 8. Verification & Test Evidence

### Quality Gates Run & Passed:
1. **Backend Tests:** `apps/api/tests/test_charts_v1.py` (15/15 passed).
   - Invariants: OHLC envelope verification, negative commodity price support, volume type safety, interval validation, pagination cursors.
2. **Prior-Stage Regressions:** `apps/api/tests/markets` (189/189 passed).
3. **Backend Linter:** `uv run ruff check` (0 errors).
4. **Frontend Unit Tests:** `apps/web/tests/charts-v1.test.ts` (9/9 passed).
5. **Full Frontend Suite:** `apps/web/tests/*.test.ts` (242/242 passed across 21 test files).
6. **Production Build:** `next build` completed with all 38 static and dynamic routes compiled without errors.
