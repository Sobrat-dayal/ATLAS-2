# Stage 70 Technical Documentation: TA-Lib Integration & Production Technical Analysis Engine

## 1. Executive Architecture Summary

Stage 70 upgrades ATLAS Charts into an institutional-grade technical analysis environment. It integrates the native **TA-Lib** (Technical Analysis Library) Python bindings with the versioned, typed **Stage 69 Indicator Registry**, establishes a deterministic numerical conversion boundary (`Decimal` to `float64`), provides an allowlisted catalog of 14 production indicators across Trend, Momentum, Volatility, and Volume studies, and delivers multi-output chart overlays, independent oscillator subpanes, and accessible tabular numerical inspection.

```
+-------------------------------------------------------------------------------+
|                       ATLAS Charts Application (/charts)                      |
|                                                                               |
|  [Toolbar] Instrument (SPY) | Interval (1D) | Type (Candle) | Indicators (3)  |
|  [Active Studies] MFI (14): 57.80 | BBANDS (20,2,2): U/M/L | MACD (12,26,9)   |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|               Main Historical Chart Viewport (Lightweight Charts)             |
|                                                                               |
|   Candlestick Series (Open, High, Low, Close)                                 |
|   Volume Histogram Overlay                                                    |
|   Live Last-Price Dashed Line (Stage 67)                                      |
|   Bollinger Bands Overlay: Upper Band (dashed) / Middle Band / Lower Band     |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|             Independent Subpane 1: Money Flow Index (0-100 Oscillator)        |
|   MFI Line Series with 20/80 Reference Guidelines                             |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|             Independent Subpane 2: MACD (Momentum & Signal Pane)              |
|   MACD Line (#38bdf8) + Signal Line (#f59e0b)                                 |
|   Zero-Centered Positive (#10b981) / Negative (#ef4444) Histogram             |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|            Stage 70 Accessible Technical Indicator Numerical Table            |
|   Timestamp (UTC) | Close | MFI | BB Upper | BB Mid | BB Lower | MACD | Hist |
+-------------------------------------------------------------------------------+
                                      |
                          POST /calculate (REST API)
                                      v
+-------------------------------------------------------------------------------+
|                        FastAPI Backend Engine (apps/api)                      |
|                                                                               |
|  1. Auth & Entitlements Verification (Stages 13-14)                           |
|  2. Qualified OHLCV Historical Snapshot (Stages 33, 37, 39)                   |
|  3. Volume Qualification (Rejects OTC FX missing volume with MISSING_VOLUME)  |
|  4. Strict Decimal -> Float64 Conversion Boundary (extract_finite_float_series)|
|  5. TA-Lib Native Adapter & Calculator (TALibIndicatorCalculator)             |
|  6. Lookback & Non-Finite Warmup Mapping (NaN -> null, status: WARMUP)        |
|  7. Typed Multi-Output Series Assembly (IndicatorCalculationResponse)         |
+-------------------------------------------------------------------------------+
```

---

## 2. Dependency Management & Native Runtime

### Pinned Dependencies
- **TA-Lib Python Wrapper**: `ta-lib>=0.8.2` (installed: `0.8.2`)
- **TA-Lib Native C Library**: `0.8.1 (Oct 12 2026 17:59:54)`
- **NumPy**: `numpy>=2.0.0` (installed: `2.5.4`)
- **Python Runtime**: `3.12.x` (Windows x86_64, Linux glibc/musl x86_64 container ready)

### Capability Readiness Endpoint
- **Method & Route**: `GET /api/v1/charts/indicators/capabilities`
- **Response Contract**:
  ```json
  {
    "installed": true,
    "wrapper_version": "0.8.2",
    "native_version": "0.8.1 (Oct 12 2026 17:59:54)",
    "numpy_version": "2.5.4",
    "functions_available": 201
  }
  ```
- If the native library is uninstalled or unimportable, `installed` returns `false`, and indicator calculations fail safely with `IndicatorStatus.TALIB_UNAVAILABLE` rather than crashing the API process.

---

## 3. Production Indicator Catalog (14 Approved Studies)

All 14 production indicators are registered in the authoritative `IndicatorRegistry`, validated server-side, and exposed through the catalog API (`GET /api/v1/charts/indicators/catalog`):

| Indicator Name | Indicator ID | TA-Lib Function | Category | Required Fields | Default Parameters | Parameter Bounds | Output Series | Rendering Target |
|---|---|---|---|---|---|---|---|---|
| **Simple Moving Average** | `atlas.sma` | Native / TA-Lib | TREND | `CLOSE` | `period: 20` | `2 <= period <= 500` | `sma` (Price) | `PRICE_OVERLAY` |
| **Exponential Moving Average** | `atlas.ema` | `talib.EMA` | TREND | `CLOSE` | `period: 20` | `2 <= period <= 500` | `ema` (Price) | `PRICE_OVERLAY` |
| **Weighted Moving Average** | `atlas.wma` | `talib.WMA` | TREND | `CLOSE` | `period: 20` | `2 <= period <= 500` | `wma` (Price) | `PRICE_OVERLAY` |
| **Relative Strength Index** | `atlas.rsi` | `talib.RSI` | MOMENTUM | `CLOSE` | `period: 14` | `2 <= period <= 100` | `rsi` (Points, 0-100) | `INDICATOR_PANE` |
| **MACD** | `atlas.macd` | `talib.MACD` | MOMENTUM | `CLOSE` | `fast: 12, slow: 26, signal: 9` | `fast < slow` | `macd_line`, `signal_line`, `histogram` | `INDICATOR_PANE` |
| **Bollinger Bands** | `atlas.bbands` | `talib.BBANDS` | VOLATILITY | `CLOSE` | `period: 20, nbdevup: 2, nbdevdn: 2` | `2 <= period <= 200` | `upper_band`, `middle_band`, `lower_band` | `PRICE_OVERLAY` |
| **Average True Range** | `atlas.atr` | `talib.ATR` | VOLATILITY | `HIGH, LOW, CLOSE` | `period: 14` | `1 <= period <= 100` | `atr` (Price Distance) | `INDICATOR_PANE` |
| **Stochastic Oscillator** | `atlas.stoch` | `talib.STOCH` | MOMENTUM | `HIGH, LOW, CLOSE` | `fastk: 5, slowk: 3, slowd: 3` | `1 <= periods <= 100` | `slowk`, `slowd` (0-100) | `INDICATOR_PANE` |
| **Average Directional Index** | `atlas.adx` | `talib.ADX` | TREND | `HIGH, LOW, CLOSE` | `period: 14` | `2 <= period <= 100` | `adx` (Strength 0-100) | `INDICATOR_PANE` |
| **Commodity Channel Index** | `atlas.cci` | `talib.CCI` | MOMENTUM | `HIGH, LOW, CLOSE` | `period: 14` | `2 <= period <= 100` | `cci` (Index Points) | `INDICATOR_PANE` |
| **Rate of Change** | `atlas.roc` | `talib.ROC` | MOMENTUM | `CLOSE` | `period: 10` | `1 <= period <= 200` | `roc` (Percentage %) | `INDICATOR_PANE` |
| **Momentum** | `atlas.mom` | `talib.MOM` | MOMENTUM | `CLOSE` | `period: 10` | `1 <= period <= 200` | `mom` (Price Difference) | `INDICATOR_PANE` |
| **On-Balance Volume** | `atlas.obv` | `talib.OBV` | VOLUME | `CLOSE, VOLUME` | *(None)* | *(None)* | `obv` (Cumulative Vol) | `INDICATOR_PANE` |
| **Money Flow Index** | `atlas.mfi` | `talib.MFI` | VOLUME | `HIGH, LOW, CLOSE, VOLUME` | `period: 14` | `2 <= period <= 100` | `mfi` (0-100) | `INDICATOR_PANE` |

---

## 4. Numerical Precision & Conversion Boundary

The canonical Market Data repository maintains prices and volumes as high-precision `Decimal` objects. TA-Lib functions operate on compiled C routines expecting contiguous C-order `float64` NumPy arrays.

Stage 70 establishes a tested conversion boundary via `extract_finite_float_series(bars, field)`:
1. Every Decimal value is converted explicitly to float64: `float(raw_val)`.
2. Every float is validated with `np.isfinite()`. Non-finite numbers (`NaN`, `+Inf`, `-Inf`) are rejected.
3. If non-finite values are encountered in historical bars, calculation stops and returns `IndicatorStatus.INCOMPATIBLE_INPUT` or `IndicatorStatus.DATA_GAP`.
4. Outputs from TA-Lib are validated:
   - Initial lookback warmup entries (represented as `NaN` by TA-Lib) are mapped to `value: null` with `status: IndicatorStatus.WARMUP`.
   - Never serialized as `NaN` or `Infinity` in JSON payloads.
   - Never substituted with artificial zeroes or fifties.

---

## 5. Volume Qualification & Anti-Fabrication Policy

Technical indicators that rely on volume (`atlas.obv`, `atlas.mfi`) are strictly conditional on genuine, consolidated traded volume:
- If an instrument does not have volume observations (e.g. OTC FX like `EURUSD` or fixed income), the service rejects the calculation with `IndicatorStatus.MISSING_VOLUME`.
- Traded volume is never fabricated or replaced with artificial zeroes.
- The UI displays an amber badge: `Traded Volume Required: Incompatible with OTC FX feeds`.

---

## 6. Multi-Output Indicators & Chart Overlays

### Price Overlays (Bollinger Bands, Moving Averages)
- In `HistoricalChart.tsx`, all output series with `rendering_target === "PRICE_OVERLAY"` are synchronized directly onto the primary price scale.
- Bollinger Bands renders 3 distinct series:
  - `upper_band`: Translucent dashed line with upper volatility boundary.
  - `middle_band`: Solid baseline moving average.
  - `lower_band`: Translucent dashed line with lower volatility boundary.

### Oscillator Panes (RSI, MACD, Stochastic, ATR, etc.)
- In `IndicatorSubpane.tsx`, all output series with `rendering_target === "INDICATOR_PANE"` mount independent HTML5 canvas instances via Lightweight Charts below the primary chart.
- **RSI Subpane**: Displays 0–100 scale with horizontal dashed reference lines at 30 (oversold guide) and 70 (overbought guide).
- **MACD Subpane**: Renders MACD Line (`#38bdf8`), Signal Line (`#f59e0b`), and zero-centered Histogram (`#10b981` when positive, `#ef4444` when negative).
- **Stochastic Subpane**: Displays %K and %D lines with 20/80 reference lines.
- **MFI Subpane**: Displays Money Flow Index oscillator with 20/80 reference lines.

---

## 7. Operational & Resource Caps

- **Maximum Active Indicator Instances**: 12 simultaneous instances per chart request (increased from Stage 69's limit of 5).
- **Maximum Output Bars**: 2,000 bars per indicator calculation.
- **Error Isolation**: Each indicator instance calculates independently within the batch; failure or warmup in one indicator never prevents other valid indicators from calculating and rendering.
- **Zero Market Data Writes**: Normal calculation reads perform **0** writes to canonical PostgreSQL or ClickHouse tables, **0** upstream market data provider fetches, and **0** trading/order side effects.

---

## 8. Verification Results

All automated quality gates have been executed and verified:
1. **Backend Tests**: 70/70 pytest tests passing (`apps/api/tests/test_talib_indicators.py`, `test_charts_*.py`).
2. **Backend Ruff Lint**: 0 errors across `python/atlas/src/atlas/charts/indicators`.
3. **Frontend Tests**: 50/50 test runner tests passing (`apps/web/tests/charts-*.test.ts`).
4. **Frontend TypeScript**: `cmd /c npx tsc --noEmit` exited with code 0 (zero type errors).
5. **Browser Verification**: Real-time browser tests verified live rendering of Bollinger Bands on SPY, independent RSI and MACD subpanes with zero-centered histogram, and numerical inspection table.
