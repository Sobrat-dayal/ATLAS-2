# ATLAS — Chart Intervals & Chart Types Architecture (Stage 68)

## 1. Overview & Roadmap Position

**Stage 68** of the canonical 150-stage ATLAS development roadmap upgrades the financial charting module (`/charts`) from the single-baseline daily configuration established in Stage 66 to an institutional, multi-timeframe financial charting interface supporting:

1. **Typed Canonical Interval Catalog**: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1D`, `1W`, `1M`.
2. **Dynamic Series-Specific Interval Discovery**: `GET /api/v1/charts/intervals` exposing native vs. derived capabilities and truthful unavailability reasons.
3. **High-Precision Decimal OHLCV Aggregation Engine**:
   - $\text{Open} = \text{first constituent bar's Open}$
   - $\text{High} = \max(\text{all constituent Highs})$
   - $\text{Low} = \min(\text{all constituent Lows})$
   - $\text{Close} = \text{last constituent bar's Close}$
   - $\text{Volume} = \sum \text{Volumes}$ strictly when all constituent bars have non-null volume; if any bar has missing volume, aggregate volume is `None` (never `0`).
4. **Calendar and Session-Aware Boundaries**: Monday-aligned ISO calendar weeks (`1W`) and calendar months (`1M`), preventing naive fixed-day or fixed-hour groupings.
5. **Preservation of Negative Futures Prices**: Legal negative settlement/close values supported for commodity energy futures (`CLZ26`).
6. **Four Foundational Financial Chart Renderers**:
   - **Candlestick**: Japanese candlesticks with High/Low wicks and Open/Close bodies.
   - **OHLC Bar**: Traditional vertical High-Low spine with left Open tick and right Close tick.
   - **Line**: Qualified Close price line series.
   - **Area**: Qualified Close price series with subtle translucent baseline gradient.
7. **Stage 67 Live Streaming Integration**:
   - Preserved real-time Last-price dashed overlay across all timeframes.
   - Strict interval isolation: 1-minute live bars never update 5-minute charts without verified aggregation.
   - Resilient against WebSocket reconnection and rapid interval switching.
8. **Strict Roadmap Scope Boundaries**:
   - No premature technical indicators (reserved for Stage 69).
   - No TA-Lib computations (reserved for Stage 70).
   - No drawing tools (reserved for Stage 71).
   - No multi-chart layouts or synchronization (Stages 72–73).
   - No persistent saved layouts (Stage 74).
   - No candle replay or order execution (Stages 75, 144).

---

## 2. Canonical Interval Model

### 2.1 Interval Identifiers & Nominal Durations

| Interval ID | Display Label | Duration Kind | Nominal Seconds | Calendar Policy |
| :--- | :--- | :--- | :--- | :--- |
| `1m` | 1m | Fixed | 60 | Intraday trading session / 24h continuous |
| `5m` | 5m | Fixed | 300 | Session-aligned 5-minute buckets |
| `15m` | 15m | Fixed | 900 | Session-aligned 15-minute buckets |
| `30m` | 30m | Fixed | 1800 | Session-aligned 30-minute buckets |
| `1h` | 1h | Fixed | 3600 | Session-aligned 60-minute buckets |
| `4h` | 4h | Fixed | 14400 | Session-aligned 4-hour buckets |
| `1d` | 1D | Calendar / Session | 86400 | Exchange-specific official trading date |
| `1w` | 1W | Calendar | None | Monday-aligned ISO calendar week |
| `1M` | 1M | Calendar | None | Calendar month (1st of month 00:00:00 UTC) |

*Critical invariant: `"1m"` represents 1 minute, while `"1M"` represents 1 calendar month. Case sensitivity is strictly enforced across APIs and parsing logic.*

### 2.2 Interval Availability by Asset Class

Availability is strictly series-specific and reflects genuine stored coverage or mathematically valid aggregation paths:

| Asset Class | Exemplars | Native Intervals | Derived Intervals | Truthful Unavailability Disclosures |
| :--- | :--- | :--- | :--- | :--- |
| **Equities** | `AAPL`, `MSFT`, `NVDA` | `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` | `1w`, `1M` (from `1d`) | Full coverage across all 9 canonical intervals. |
| **ETFs** | `SPY`, `QQQ` | `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` | `1w`, `1M` (from `1d`) | Full coverage across all 9 canonical intervals. |
| **FX** | `EURUSD`, `USDJPY` | `5m`, `15m`, `30m`, `1h`, `4h`, `1d` | `1w`, `1M` (from `1d`) | `1m` is `UNAVAILABLE` due to institutional licensing constraints. |
| **Crypto** | `BTCUSDT`, `ETHUSDT` | `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` | `1w`, `1M` (from `1d`) | 24/7 continuous trading sessions; no weekend or holiday gaps. |
| **Bonds** | `US10Y` | `1d` | `1w`, `1M` (from `1d`) | All intraday intervals (`1m`–`4h`) are `UNAVAILABLE` because OTC evaluated sovereign benchmarks are only published daily. |
| **Futures** | `CLZ26`, `GCZ26`, `ESZ26` | `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` | `1w`, `1M` (from `1d`) | Negative price support enabled for energy futures (`CLZ26`). |

---

## 3. Mathematical & Temporal OHLCV Aggregation Engine

Aggregation converts chronologically ordered constituent bars into target-interval bars using high-precision Decimal arithmetic without floating-point drift:

### 3.1 Aggregation Formulas

$$\text{Open} = B_0.\text{open}$$

$$\text{High} = \max_{i=0}^{N-1} B_i.\text{high}$$

$$\text{Low} = \min_{i=0}^{N-1} B_i.\text{low}$$

$$\text{Close} = B_{N-1}.\text{close}$$

$$\text{Volume} = \begin{cases} \sum_{i=0}^{N-1} B_i.\text{volume} & \text{if } \forall i, B_i.\text{volume} \neq \text{None} \\ \text{None} & \text{if } \exists i, B_i.\text{volume} = \text{None} \end{cases}$$

### 3.2 Volume Completeness Invariant
In OTC markets (e.g. Foreign Exchange interbank feeds or sovereign bond clean prices), trading volume is not reported. If any constituent bar has `volume is None`, the aggregate volume is strictly `None`. Treating missing volume as `0` is strictly prohibited as it fabricates false market stagnation.

### 3.3 Strict Envelope Invariant Validation
Prior to and following aggregation, every bar must satisfy:
$$\text{High} \ge \max(\text{Open}, \text{Close}, \text{Low})$$
$$\text{Low} \le \min(\text{Open}, \text{Close}, \text{High})$$
Any bar violating these geometric envelope constraints raises an explicit `ValueError` and is rejected immediately.

### 3.4 Negative Price Allowance
Commodity energy futures (e.g., WTI Crude Oil `CLZ26`) can legally settle or trade at negative prices during extreme physical delivery capacity constraints (as demonstrated in April 2020). When `allows_negative_price=True`, negative values are preserved without synthetic clamping. For all other asset classes (Equities, ETFs, FX, Crypto, Bonds), negative prices are rejected.

---

## 4. REST APIs

### 4.1 Interval Discovery (`GET /api/v1/charts/intervals`)

- **Query Parameters**:
  - `symbol` (e.g. `AAPL`, `US10Y`, `EURUSD`)
  - `instrument_id` (Canonical instrument UUID)
- **Response Schema (`ChartIntervalsResponse`)**:
```json
{
  "schema_version": "1.0.0",
  "instrument_entity_id": "c1a2b3c4-0001-4000-8000-000000000001",
  "display_symbol": "AAPL",
  "default_interval": "1d",
  "instrument": { ... },
  "intervals": [
    {
      "interval_id": "1m",
      "display_label": "1m",
      "duration_seconds": 60,
      "availability": "AVAILABLE_NATIVE",
      "native_or_derived": "NATIVE",
      "is_supported": true,
      "source_interval": null,
      "live_bar_supported": true,
      "unavailability_reason": null
    },
    {
      "interval_id": "1w",
      "display_label": "1W",
      "duration_seconds": null,
      "availability": "AVAILABLE_DERIVED",
      "native_or_derived": "DERIVED",
      "is_supported": true,
      "source_interval": "1d",
      "live_bar_supported": false,
      "unavailability_reason": null
    }
  ]
}
```

### 4.2 Multi-Interval Historical Bars (`GET /api/v1/charts/history`)

- **Query Parameters**:
  - `symbol` / `instrument_id`
  - `interval`: One of `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`, `1M`
  - `start`, `end`, `before` (pagination cursor)
  - `limit` (clamped to $[10, 2000]$)
- **Response Enhancements**:
  - `interval_source_kind`: `"NATIVE"` or `"DERIVED"`
  - `derived_source_interval`: `"1d"` or `"1m"` when derived, `null` when native.

---

## 5. Frontend Visual Architecture

### 5.1 Chart Interval Selector
Located in `ChartToolbar.tsx`:
- Rendered via `ChartIntervalSelector.tsx`.
- Displays canonical buttons: `1m  5m  15m  30m  1h  4h  1D  1W  1M`.
- Derived intervals show a subtle cyan dot indicator.
- Unsupported intervals are visibly disabled (`line-through`, dimmed) with an accessible hover tooltip explaining why the interval cannot be provided.

### 5.2 Chart Type Selector
Located in `ChartToolbar.tsx`:
- Rendered via `ChartTypeSelector.tsx`.
- Segmented buttons for:
  1. **Candles** (`candlestick` via `CandlestickSeries`)
  2. **OHLC** (`bar` via `BarSeries`)
  3. **Line** (`line` via `LineSeries`)
  4. **Area** (`area` via `AreaSeries` with Sky-400 translucent gradient)
- Switching chart type preserves the active instrument, interval, loaded bars, and viewport position without initiating unnecessary network queries.

### 5.3 Live Streaming Compatibility
- Stage 67 live Last-price overlay is preserved across all timeframes.
- Provisional candle updates are applied only when the streaming bar's interval matches the active chart interval.
- When the user switches intervals rapidly, in-flight HTTP requests are immediately aborted using `AbortController`, preventing stale responses from overwriting the active chart.

---

## 6. Verification & Quality Gates

1. **Python Lint & Formatting**:
   - `uv run ruff check` -> 0 errors.
   - `uv run ruff format --check` -> 0 unformatted files.
2. **Backend Unit & Integration Tests**:
   - `tests/test_charts_intervals_and_types.py` -> 17 passed.
   - `tests/test_charts_v1.py` -> 16 passed.
   - `tests/test_charts_live_streaming.py` -> 16 passed.
   - Total backend chart test suite: **49 passed out of 49**.
3. **Frontend TypeScript & ESLint**:
   - `npx.cmd tsc --noEmit` -> 0 type errors.
   - `npx.cmd eslint ...` -> 0 lint warnings/errors.
4. **Frontend Unit & Component Tests**:
   - `tests/charts-intervals-and-types.test.ts` -> 8 passed.
   - Total web tests across all 42 test suites: **263 passed out of 263**.
