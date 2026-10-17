# ATLAS Market Heatmaps V1 (Stage 64)

## 1. Product Vision & Architecture Scope

ATLAS Market Heatmaps V1 introduces the first dedicated market performance visualization and treemap workspace within ATLAS. It is located canonically at `/markets/heatmaps` as a core subsection of **Markets (Module 02)**.

The workspace delivers institutional-quality visual market intelligence comparable to Bloomberg Terminal and OpenBB systems, answering critical financial questions with strict mathematical integrity:
1. **What is the visualized universe?** Exactly defined, canonical, authorized subsets of instruments (Equities, Crypto Spot, Futures).
2. **What determines tile area?** Explicitly declared: equal-size baseline or verified market-capitalization weighting.
3. **What determines tile color?** Qualified percentage return over an explicit comparison window (Previous Regular Session Close, Rolling 24h Prior Window, Previous Session Settlement).
4. **How are assets grouped?** Authoritative GICS sector and industry classifications (never name-based heuristics).
5. **How comprehensive is the heatmap?** Complete coverage reporting with candidate count, qualified count, missing returns, missing weights, unclassified count, and truthful coverage status (`COMPLETE_FOR_DEFINED_UNIVERSE` vs. `PARTIAL_COVERAGE`).
6. **How recent is the data?** Freshness and delivery delay status (Realtime, Delayed, Stale) with observation timestamps distinct from heatmap calculation timestamps.

### Strict Scope Boundaries
- **No Stage 65 Cross-Asset Analytics**: Stage 65 owns multi-asset correlation matrices, cross-market contagion scores, and normalized risk heatmaps.
- **No Stage 66 Charts**: Stage 66 owns full candlestick charting engines and technical drawing tools.
- **No Multi-Factor Screeners**: Stages 94–98 own Screeners.
- **No Portfolio Exposure Heatmaps**: Stage 110+ owns Portfolio analytics.
- **No Geographic Maps**: Geospatial choropleths belong to the Maps module.
- **No Trading or Order Execution**: Read-only; no Buy/Sell actions, no auto-rebalancing.
- **No Predictive AI Scores**: 0 synthetic momentum ratings or AI forecast signals.

---

## 2. Core Architectural Principle: Two Distinct Visualization Modes

Stage 64 enforces a strict mathematical and visual separation between two presentation modes:

### Mode A: Equal-Size Performance Heatmap (`equal_size`)
- Every qualified instrument receives an identical layout area fraction ($1 / N$).
- Tile area has **zero financial weight meaning**.
- Tile color represents qualified price return percentage.
- Operates reliably as an institutional baseline even when market capitalization data is missing or incomplete.

### Mode B: Size-Weighted Market Treemap (`market_cap_weighted`)
- Each instrument's tile area represents verified, strictly positive market capitalization ($w_i$).
- Normalized area fraction:
  $$\text{normalized\_weight}_i = \frac{w_i}{\sum_{j \in \text{qualified}} w_j}$$
- Area and color encode independent quantities: Area = Capitalization, Color = Return.
- **Anti-Fallback Rule**: If market capitalization is unsupported or unavailable for a universe (e.g. Futures), weighted mode is disabled and clearly explained—never silently fall back to equal size while claiming market-cap weighting!
- Invalid, negative, or zero weights are rejected.

---

## 3. Supported Heatmap Universes

| Universe ID | Display Name | Asset Class | Supported Modes | Supported Hierarchies | Supported Windows | Weight Metric | Taxonomy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `univ_us_equities` | Covered US Equities | Equity | Equal-Size, Market-Cap Weighted | Flat, Sector, Industry | Prev Regular Session | Market Capitalization (USD) | GICS |
| `univ_crypto_spot` | Covered Cryptocurrency Spot | Crypto | Equal-Size, Market-Cap Weighted | Flat | Rolling 24h | Circulating Market Cap (USDT) | None |
| `univ_futures` | Exchange-Traded Futures | Futures | Equal-Size | Flat, Sector | Prev Session Settlement | None (No equity market cap) | Commodity Class |

---

## 4. Mathematical Qualification & Return Calculation

### Price Return Percentage
For an active candidate security with verified traded price ($P_{\text{current}}$) and positive prior reference ($P_{\text{reference}} > 0$):
$$\Delta\% = \left(\frac{P_{\text{current}} - P_{\text{reference}}}{P_{\text{reference}}}\right) \times 100$$
Calculated strictly using Python `Decimal` with `ROUND_HALF_UP` precision to 4 decimal places.

### Missing Data Invariants
- Missing price observations are **never** colored or reported as 0.00% return.
- If $P_{\text{current}}$ is missing $\rightarrow$ Excluded (`NO_CURRENT_QUOTE`), counted in `missing_returns`.
- If $P_{\text{reference}}$ is missing $\rightarrow$ Excluded (`NO_REFERENCE`), counted in `missing_returns`.
- If $P_{\text{reference}} \le 0$ $\rightarrow$ Excluded (`INVALID_DENOMINATOR`), counted in `missing_returns`.
- In `market_cap_weighted` mode, if weight is missing $\rightarrow$ Excluded (`MISSING_WEIGHT`), counted in `missing_weights`.
- Excluded instruments receive a distinct unavailable visual styling (muted dark neutral with dashed border and "N/A" label).

---

## 5. Performance Diverging Color Scale

ATLAS uses a high-contrast financial diverging color scale configured across the domain `[-5.0%, +5.0%]`:
- **Positive returns (> 0%)**: Green family (rich subtle emerald `rgba(6, 78, 59, 0.45)` to saturated forest emerald `rgba(16, 185, 129, 0.95)`).
- **Zero return (0.00%)**: Neutral zinc/slate `rgba(39, 39, 42, 0.85)` with light gray text.
- **Negative returns (< 0%)**: Red family (rich subtle ruby `rgba(127, 29, 29, 0.45)` to saturated crimson `rgba(220, 38, 38, 0.95)`).
- **Extreme returns (> +5% or < -5%)**: Saturated at the domain boundary color while preserving the exact numeric percentage in labels, popovers, and inspector.
- **Accessible & Screen-Reader Compatibility**: Explicit `+` sign for positive values (`+2.35%`), `-` sign for negatives (`-1.80%`), and a dedicated accessible data table alternative.

---

## 6. GICS Sector & Industry Taxonomy & Group Aggregates

Where authoritative classifications exist, constituents are grouped into GICS sectors:
- `Technology` (e.g. AAPL, MSFT, NVDA)
- `Consumer Cyclical` (e.g. AMZN, TSLA)
- `Communication Services` (e.g. GOOGL, META)
- `Financial Services` (e.g. JPM)
- `Healthcare` (e.g. UNH)
- `Energy` (e.g. XOM)
- `Unclassified`: Fallback group for securities lacking an authoritative sector (never guess sectors from company names).

### Sector Aggregate Return Methodology
Group nodes disclose their exact calculation methodology:
- In `equal_size` mode: **Equal-Weight Mean**:
  $$\text{aggregate\_return}_{\text{group}} = \frac{\sum_{i=1}^n r_i}{n}$$
  Labeled: "Equal-weight mean (qualified constituents)".
- In `market_cap_weighted` mode: **Cap-Weighted Return**:
  $$\text{aggregate\_return}_{\text{group}} = \frac{\sum_{i=1}^n w_i \cdot r_i}{\sum_{i=1}^n w_i}$$
  Labeled: "Cap-weighted return (qualified constituents)".
- Marked explicitly as "Based on qualified ATLAS constituents", never claimed as an official market index.

---

## 7. Squarified Treemap Layout Engine

The frontend layout engine (`apps/web/src/lib/markets/heatmaps/treemap.ts`) implements the pure squarified treemap algorithm:
- Generates non-overlapping rectangles fitted within bounded width and height.
- Optimizes aspect ratios to be as close to 1:1 (square) as possible.
- Deterministic layout for identical snapshots.
- Responsive reflow via `ResizeObserver` without flickering or shifting tile colors.
- Tiny tile classification: tiles smaller than 52px width or 36px height suppress long labels to prevent text overflow while maintaining full hover, focus, click, and inspector access.

---

## 8. Coverage Transparency Model

Every response includes an institutional coverage report:
```json
{
  "universe_size": 12,
  "candidate_count": 12,
  "qualified_count": 12,
  "missing_returns": 0,
  "missing_weights": 0,
  "unclassified_count": 0,
  "coverage_status": "COMPLETE_FOR_DEFINED_UNIVERSE",
  "total_qualified_weight": "19955000000000",
  "exclusion_breakdown": {}
}
```

Coverage statuses:
- `COMPLETE_FOR_DEFINED_UNIVERSE`: 100% of defined universe candidates are qualified and visualized.
- `PARTIAL_COVERAGE`: Some candidates were excluded due to missing quotes, references, or weights.
- `DEGRADED`: Provider latency or partial data streams.
- `UNAVAILABLE`: Zero qualified observations.

---

## 9. Authenticated Read-Only APIs

### Endpoints
- `GET /api/v1/markets/heatmaps/universes`: Lists supported canonical universes.
- `GET /api/v1/markets/heatmaps/options`: Lists supported modes, hierarchies, and comparison windows.
- `GET /api/v1/markets/heatmaps`: Computes a coherent calculation snapshot.

### Query Parameters
- `universe_id` (string, default: `univ_us_equities`)
- `visualization_mode` (string: `equal_size`, `market_cap_weighted`)
- `hierarchy_mode` (string: `none`, `sector`, `industry`)
- `comparison_window` (string)
- `sector` (optional string filter)
- `max_nodes` (optional integer limit)

### Read-Only Invariants
Normal heatmap requests perform:
- 0 Canonical Entity writes
- 0 Quote writes
- 0 Historical price writes
- 0 Fundamental weight writes
- 0 External provider RPC calls
- 0 Live ingestion targets
- 0 Trading orders
- 0 Autonomous agent executions

---

## 10. User Interface Specification

Located at `/markets/heatmaps`:
- **Header**: Title, universe badge, asset class, snapshot timestamp, data table toggle, and refresh button.
- **Control Toolbar**: Universe selector, comparison window selector, weighting mode toggle (Equal-Size vs Market-Cap Weighted), hierarchy mode toggle (Sector vs Flat).
- **Coverage Summary**: Transparency metrics detailing candidates, qualified items, missing data counts, total capitalization, and coverage status badge.
- **Legend**: Diverging performance color scale (-5.0% to +5.0%) with explicit missing data indicator.
- **Treemap Workspace**: Squarified treemap with sector container headers, aggregate returns, breadcrumb drilldown navigation, and interactive tiles.
- **Inspector Panel**: Detailed inspection of selected tile with canonical instrument UUID (Stage 17), series key, pricing, capitalization, taxonomy, and quick navigation links ("Open Charts", "Open Market", "Open Company").
- **Accessible Data Table**: Nonvisual accessible semantic HTML table with full keyboard and screen-reader support.
