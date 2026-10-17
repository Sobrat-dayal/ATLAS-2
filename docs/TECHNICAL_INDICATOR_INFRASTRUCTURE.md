# TECHNICAL INDICATOR INFRASTRUCTURE V1 (STAGE 69)

## 1. Overview & Architectural Directive

The **Technical Indicator Infrastructure V1** establishes the formal mathematical study framework for the ATLAS Charts module (`/charts`). It provides a secure, versioned, typed, deterministic calculation engine that applies approved mathematical transformations to qualified canonical financial market time series.

An indicator in ATLAS is strictly defined as:
> **A deterministic mathematical transformation of qualified financial observations. It is not an independent source of market truth, a prediction, or a trading recommendation.**

### Strict Scope Boundaries & Principles
1. **Never fabricate missing OHLCV observations** to produce indicator values.
2. **Never silently interpolate** missing price data or forward-fill gaps.
3. **Never treat provisional market data as finalized history.**
4. **Never calculate indicators using incompatible source intervals** or mix providers, venues, price bases, or adjustment policies.
5. **Never look ahead into future bars.** Every calculation at timestamp $T$ uses only observations $\le T$.
6. **Never display mathematically invalid warmup values as genuine indicator values.** Warmup bars are explicitly marked `WARMUP` with `value = None`.
7. **Never return NaN or Infinity as valid outputs.**
8. **Server-controlled allowlisted registry only.** Never accept user-submitted arbitrary Python, JavaScript, SQL, or executable formulas (`eval`, `exec`).
9. **No TA-Lib integration in Stage 69.** TA-Lib integration and the broader indicator catalog (RSI, MACD, Bollinger Bands, ATR, Stochastic, etc.) are formally deferred to **Stage 70**.
10. **No Trading signals, backtesting, drawings, or multi-chart layouts.**

---

## 2. Technical Indicator Architecture

The engine architecture follows a strictly layered, unidirectional pipeline:

```
Canonical Historical OHLCV (ClickHouse / Stored Bars)
                     │
                     ▼
       Historical Data Qualification
 (Instrument Entity UUID, Price Basis, Adjustment Basis)
                     │
                     ▼
          Indicator Input Resolver
   (Calculates lookback budget = output bars + lookback)
                     │
                     ▼
          Indicator Registry (Allowlist)
         (atlas.sma v1 registered calculator)
                     │
                     ▼
           Parameter Validator
 (Authoritative backend bounds: Period integer 2-500)
                     │
                     ▼
      Deterministic Calculation Engine
    (O(N) rolling arithmetic, Decimal precision)
                     │
                     ▼
        Typed Time-Aligned Output
 (WARMUP / READY / DATA_GAP status per point, LineData)
                     │
                     ▼
      Chart Overlay / Subpane Container
   (TradingView Lightweight Charts LineSeries adapter)
                     │
                     ▼
           ATLAS Charts Module UI
```

---

## 3. Indicator Definition vs. Instance

- **Indicator Definition (`IndicatorDefinition`):** The immutable, versioned blueprint describing an algorithm, its parameter schemas, input field requirements, minimum history policy, category, and rendering target.
- **Indicator Instance (`IndicatorInstanceConfig`):** The user's active configuration of that definition in the active chart session (e.g., `instance_id: "sma_20"`, `parameters: { period: 20 }`, `color: "#38bdf8"`, `visible: true`).
- A user can attach multiple instances of the same indicator with different parameters simultaneously (e.g., fast SMA 20 and slow SMA 50).
- Session state is kept client-side during the chart session; persistent layout storage is reserved for Stage 74.

---

## 4. Secure Versioned Registry (`IndicatorRegistry`)

- Registry implementations reside in `atlas.charts.indicators.registry`.
- Registration is strictly static and allowlisted.
- Rejects duplicate `(indicator_id, version)` registrations.
- Rejects requests for unknown indicators (`UNKNOWN_INDICATOR`) or unsupported versions (`UNSUPPORTED_VERSION`).
- Rejects arbitrary user-supplied formulas or code.

### Registered Catalog in Stage 69
- **`atlas.sma` (Version 1):** Simple Moving Average.
  - Category: `TREND`
  - Rendering Target: `PRICE_OVERLAY`
  - Required Inputs: `["close"]`
  - Parameters: `period` (Integer, default `20`, minimum `2`, maximum `500`).
  - Supported Intervals: `1m`, `5m`, `15m`, `1h`, `4h`, `1D`, `1W`, `1M`.

---

## 5. Reference Implementation: Simple Moving Average (SMA)

### Mathematical Formula
For period $N$ and qualified Close observations $C_t$:
$$SMA_t = \frac{1}{N} \sum_{i=0}^{N-1} C_{t-i}$$

### Warmup and Lookback Policy
- For an SMA with period $N$, the first $N-1$ points do not have sufficient historical lookback.
- They are output with `status = "WARMUP"` and `value = None`.
- **Zero-filling or synthetic prices are strictly forbidden.**
- If the available qualified bars count is $< N$, the result returns status `INSUFFICIENT_HISTORY`.

### Gap and Continuity Policy
- A bar missing required Close values is classified as a `DATA_GAP`.
- Rolling accumulators discard corrupted windows and reset until $N$ consecutive qualified observations are available.

### Decimal Arithmetic and Numerical Integrity
- Authoritative financial arithmetic is performed using Python's `Decimal` type to prevent IEEE 754 floating-point drift.
- Complexity is $O(N)$ through a bounded rolling-sum window accumulator.
- Output points align exactly to canonical bar timestamps ($T_{point} = T_{bar}$). Zero forward or backward time shifting is applied.

---

## 6. Authenticated REST API Endpoints

Mounted under `/api/v1/charts/indicators`:

### 1. Catalog Endpoint
- **`GET /api/v1/charts/indicators/catalog`**
- Returns all allowlisted indicator definitions, their parameter schemas, defaults, and capabilities.

### 2. Definition Endpoint
- **`GET /api/v1/charts/indicators/{indicator_id}`**
- Returns detailed schema for a specific indicator.

### 3. Calculation Endpoint
- **`POST /api/v1/charts/indicators/calculate`**
- Request Payload (`IndicatorCalculationRequest`):
  ```json
  {
    "instrument_id": "019488a0-0000-7000-8000-000000000001",
    "interval": "1D",
    "instances": [
      {
        "instance_id": "sma_20",
        "indicator_id": "atlas.sma",
        "version": 1,
        "parameters": { "period": 20 }
      }
    ]
  }
  ```
- Response Payload (`IndicatorCalculationResponse`):
  - Returns calculated time-aligned points for each instance, coverage metadata, and execution status (`READY`, `WARMUP`, `INSUFFICIENT_HISTORY`).
  - Enforces resource limits: max 5 instances per request, max 2,000 bars per series, max period 500.

---

## 7. Frontend Architecture & Rendering

### Component Topology
- **`IndicatorPicker`:** Modal dialog displaying registered definitions, searching by category, inspecting requirements, and adding to chart.
- **`ActiveIndicators`:** Horizontal legend strip above the chart displaying active studies, parameter summaries, crosshair values, visibility toggle, settings trigger, and removal.
- **`IndicatorParameterEditor`:** Parameter configuration modal with inline validation (enforcing integer bounds 2–500), color selection swatches, and line width sliders.
- **`HistoricalChart` Overlay Adapter:** Synchronizes active indicator instances as dedicated `LineSeries` attached to the primary price canvas, supporting multi-instance overlay without modifying the main OHLCV candlestick series.
- **`IndicatorSubpane`:** Attached subpane container adapter providing isolated vertical scaling for future Stage 70 oscillators.
- **`ChartCrosshairDetails`:** Displays real-time hovered indicator values numerically for exact inspection and screen-reader accessibility.

---

## 8. Integration with Prior Stages

- **Stage 66 (Historical Charts):** Indicators calculate directly from canonical OHLCV bars. Historical backfill panning fetches older lookback and recalculates automatically.
- **Stage 67 (Live Streaming):** Latest Quotes update live Last-price overlays but **never fabricate finalized indicator points**. Indicators recalculate when an authoritative finalized bar is accepted.
- **Stage 68 (Intervals & Types):** Calculations are interval-aware. Switching intervals (e.g., 1D to 1h) recalculates on that interval's bars. Switching chart types (Candlestick, Bar, Line, Area) preserves indicator overlays cleanly.

---

## 9. Verification & Quality Gates

- **Backend Pytest:** 14/14 tests in `apps/api/tests/test_charts_indicators.py` passed; 63/63 tests across all chart suites passed.
- **Python Ruff:** 0 errors, 100% compliant formatting.
- **Frontend Node Test:** 10/10 tests in `apps/web/tests/charts-indicators.test.ts` passed; 40/40 tests across all web charts suites passed.
- **TypeScript:** `npx tsc --noEmit` passed with 0 errors.
- **ESLint:** passed with 0 errors.
- **Next.js Production Build:** compiled and generated all 38 routes cleanly.
