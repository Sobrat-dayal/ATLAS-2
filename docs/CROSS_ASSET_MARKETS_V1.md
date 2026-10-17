# ATLAS Cross-Asset Markets V1 (Stage 65)

## 1. Product Vision & Architecture Scope

ATLAS Cross-Asset Markets V1 introduces the first dedicated institutional multi-market intelligence workspace within ATLAS. It is located canonically at `/markets/cross-asset` as a core subsection of **Markets (Module 02)**.

The workspace delivers a high-density, multi-asset comparative terminal inspired by Bloomberg Terminal and institutional cross-market terminals, answering key financial questions with strict mathematical integrity:
1. **Which supported asset classes are represented?** Equities, ETFs, Foreign Exchange (FX), Cryptocurrency Spot, Sovereign Debt / Government Bonds, and Exchange-Traded Futures & Commodities.
2. **Which canonical benchmarks and market proxies are displayed?** Explicit attribution between authoritative benchmark indices and exchange-traded ETF/Futures proxies.
3. **Are observations from the same time window?** Explicit separation between native asset-class conventions and strict common-window UTC time alignment.
4. **How did each market move according to its native convention?** Equity price change %, ETF market price change (distinct from NAV), FX spot rate change %, crypto rolling 24h quote return %, bond yield level and basis point (bps) change, futures last price vs prior settlement.
5. **Which instruments have valid aligned-period price returns?** Only series satisfying the declared temporal alignment tolerance ($T \pm \Delta t \le 7200\text{s}$) with zero look-ahead bias and compatible quotation units participate in aligned ranking.
6. **Why is an instrument excluded from aligned comparison?** Transparent institutional exclusion reasons (`UNSUPPORTED_METRIC`, `NO_START_REFERENCE`, `WINDOW_MISALIGNED`, `INVALID_DENOMINATOR`).
7. **What is the coverage completeness?** Truthful evaluation of requested, evaluated, qualified, and excluded instruments (`COMPLETE_FOR_DEFINED_SET` vs `PARTIAL` vs `UNAVAILABLE`).

### Strict Scope Boundaries
- **No Cross-Asset Correlation / Covariance Engine**: Rolling correlation matrices, dynamic covariance, and factor models belong to future Analytics/Risk stages.
- **No Risk-On / Risk-Off Scoring**: No synthetic fear indices, risk appetite scores, or speculative macro predictions without verified empirical models.
- **No Portfolio Analytics / Optimization**: Portfolio return, asset allocation, Value at Risk, and rebalancing belong to Stages 110–118.
- **No Trading or Order Execution**: Read-only; no Buy/Sell controls, no pair trading, no automated trading agents.
- **No Stage 66 Charts**: Dedicated historical candlestick charts, drawing tools, and technical studies belong to Stage 66 (Charts V1).

---

## 2. Fundamental Cross-Asset Principle: Native Metrics vs Comparable Metrics

Stage 65 enforces a strict conceptual and mathematical separation between two analytical modes:

### Mode A: Native Market Overview (`native_overview`)
Presents each asset class according to its actual quotation conventions:
- **Equities**: Regular-session traded price and % change vs previous official close.
- **ETFs & Funds**: Exchange-traded market price % change (explicitly distinct from underlying NAV).
- **FX**: Spot exchange rate change % preserving directional pair orientation (e.g. EUR/USD vs USD/JPY).
- **Cryptocurrency**: Continuous 24/7 rolling 24-hour return in quoted denomination (e.g. USDT per BTC).
- **Government Bonds / Fixed Income**: Benchmark yield level in % and yield change in basis points (`bps`). **Never converted to equity price returns!**
- **Futures & Commodities**: Last traded contract price and change against prior official settlement in physical/contractual units (e.g. USD/barrel, index points).

### Mode B: Aligned Price Performance (`aligned_performance`)
Evaluates strictly synchronized percentage price returns across a common UTC window:
- Bounded time window: `last_24h` (24h), `last_7d` (168h), `last_30d` (720h).
- Strict common start and end instants in UTC.
- Start reference observation must occur strictly at or before requested start ($T_{\text{start, effective}} \le T_{\text{start, requested}}$)—**Zero Look-Ahead Bias Guarantee**.
- Observation offset must satisfy maximum tolerance:
  $$\Delta t_{\text{offset}} = |T_{\text{effective}} - T_{\text{requested}}| \le 7,200\text{ seconds (2 hours)}$$
- Series without compatible price observations (such as bond yields in basis points) are **excluded** with `UNSUPPORTED_METRIC`.
- Calculated Decimal price return formula:
  $$\Delta\% = \left(\frac{P_{\text{end}} - P_{\text{start}}}{P_{\text{start}}}\right) \times 100$$
- Normalized indexed level (Base 100.0):
  $$\text{Indexed} = \left(\frac{P_{\text{end}}}{P_{\text{start}}}\right) \times 100$$

---

## 3. Supported Multi-Asset Canonical Universes

| Universe ID | Display Name | Asset Classes Included | Default Member Count | Representative Canonical Symbols |
| :--- | :--- | :--- | :--- | :--- |
| `univ_cross_asset_macro` | Global Macro Cross-Asset Universe | Equities, ETFs, FX, Crypto, Bonds, Futures | 9 | `SPY`, `AAPL`, `EURUSD`, `USDJPY`, `BTCUSDT`, `ETHUSDT`, `US10Y`, `CLZ26`, `GCZ26` |
| `univ_cross_asset_us_liquidity` | US Dollar & Rates Liquidity Universe | ETFs, FX, Bonds, Futures | 6 | `SPY`, `QQQ`, `EURUSD`, `USDJPY`, `US10Y`, `GCZ26` |
| `univ_cross_asset_commodities_fx` | Commodities, FX & Inflation Universe | Futures, FX, Crypto, Bonds | 6 | `CLZ26`, `GCZ26`, `ESZ26`, `EURUSD`, `USDJPY`, `BTCUSDT` |

### Benchmark vs Proxy Distinction
- **Authoritative Index Benchmarks**: `EURUSD`, `USDJPY`, `US10Y`, `BTCUSDT` are marked `is_benchmark: true`.
- **Market Proxies**: `SPY` (ETF proxy for S&P 500 Index), `QQQ` (ETF proxy for Nasdaq-100 Index), and `ESZ26` (Futures proxy for S&P 500 Index) are explicitly marked `is_proxy: true`, with `proxy_kind: "ETF Proxy" | "Futures Proxy"` and `proxy_benchmark_target: "S&P 500 Index" | "Nasdaq-100 Index"`.
- **Anti-Conflation Rule**: Proxies are never silently presented as the cash benchmark index itself. Disclosures highlight tracking error, management expense, and contract rollover basis.

---

## 4. Institutional Coverage and Exclusion Taxonomy

Coverage reporting adheres to `CrossAssetCoverage`:
- `requested_members`: Total members requested or configured in universe.
- `authorized_members`: Entitled instruments visible to caller.
- `evaluated_members`: Count processed through qualification pipeline.
- `qualified_members`: Count eligible for common-window aligned comparison.
- `excluded_members`: Count ineligible with typed reasons.
- `completeness_status`:
  - `COMPLETE_FOR_DEFINED_SET`: 100% of defined members qualified (or native mode).
  - `PARTIAL`: Some members qualified while others excluded (e.g. bond yields in aligned mode).
  - `DEGRADED`: Provider data latency or degradation.
  - `UNAVAILABLE`: Zero members qualify.

### Typed Exclusion Reasons
- `UNSUPPORTED_METRIC`: Measurement kind (e.g. bond yield in bps) is not a price-return series.
- `NO_START_REFERENCE`: No historical observation found at or before requested window start.
- `WINDOW_MISALIGNED`: Observation latency exceeds tolerance (> 7200s).
- `INVALID_DENOMINATOR`: Start reference price is $\le 0$.
- `NEGATIVE_REFERENCE_UNSUPPORTED`: Non-positive price reference without valid conversion formula.
- `STALE_OBSERVATION`: Observation exceeds maximum age threshold.
- `MARKET_CLOSED`: Exchange closed without valid session observation.

---

## 5. API Endpoints

### 1. Universes Endpoint
`GET /api/v1/markets/cross-asset/universes`
- Returns: `CrossAssetUniverseResponse` containing candidate universes and metadata.
- Authentication: Requires `ATLAS_ACCESS` permission.
- Headers: `Cache-Control: no-store, max-age=0`.

### 2. Options Endpoint
`GET /api/v1/markets/cross-asset/options`
- Returns: `CrossAssetOptionsResponse` containing supported modes, windows, asset classes, max selection count (`12`), currency policy, and tolerance.

### 3. Overview Endpoint
`GET /api/v1/markets/cross-asset`
- Query parameters:
  - `universe_id` (string, default `univ_cross_asset_macro`)
  - `mode` (`native_overview` | `aligned_performance`, default `native_overview`)
  - `window` (`last_24h` | `last_7d` | `last_30d`, default `last_24h`)
  - `symbols` (optional comma-separated string, max 12 items; >12 returns HTTP 400)
- Returns: `CrossAssetOverviewResponse` containing snapshot ID, coverage audit, asset-class sections, comparison table items, and exclusion breakdowns.
- Read-Only Invariant: 0 database writes, 0 quote writes, 0 upstream provider RPC calls on read.

---

## 6. Frontend UI Architecture

- **Dedicated Route**: `/markets/cross-asset`
- **Navigation**: Integrated into `MarketsNavigationTabs` with active tab linking to `/markets/cross-asset`.
- **Components**:
  - `CrossAssetHeader`: Status badges, snapshot timestamp, methodology toggle, refresh button.
  - `CrossAssetUniverseSelector`: Dropdown switching multi-asset universes.
  - `CrossAssetModeSelector`: Tab switcher between Native Overview and Aligned Performance.
  - `CrossAssetWindowSelector`: Comparison period selector (`24H`, `7D`, `30D`).
  - `CrossAssetCoverageSummary`: Coverage metrics, completeness badge, exclusion breakdown.
  - `AssetClassOverviewGrid`: High-density cards for each financial asset class.
  - `CrossAssetComparisonTable`: Accessible financial table with sorting, tabular numerals, proxy badges, and chart links.
  - `CrossAssetInspector`: Detailed inspection drawer for selected canonical instrument.
  - `AlignmentMethodologyPanel`: Collapsible institutional disclosures.
  - `CrossAssetEmptyErrorStates`: Accessible loading skeletons, empty states, and error retry handlers.

---

## 7. Quality Gates & Test Verification

All automated tests and quality gates executed and passing:
- **Backend Tests**: `uv run pytest tests/markets/test_markets_cross_asset.py` (13 passed in 1.65s).
- **Prior Market Regressions**: `uv run pytest tests/markets` (189 passed in 3.16s).
- **Backend Lint & Format**: `uv run ruff check` & `uv run ruff format --check` (0 errors, 7 files clean).
- **Frontend Tests**: `pnpm.cmd dlx tsx --test tests/markets-cross-asset.test.ts` (9 passed in 51ms).
- **All Frontend Market Tests**: `pnpm.cmd dlx tsx --test tests/markets-*.test.ts` (108 passed in 2.3s).
- **TypeScript Typecheck**: `pnpm.cmd --filter web exec tsc --noEmit` (0 errors).
- **Frontend Lint**: `pnpm.cmd --filter web exec eslint ...` (0 errors, 0 warnings).
- **Next.js Production Build**: `pnpm.cmd --filter web build` (successful compilation, `/markets/cross-asset` prerendered).
