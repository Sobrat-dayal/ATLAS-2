# ATLAS Market Movers V1 (Stage 63)

## 1. Product Vision & Architecture Scope

ATLAS Market Movers V1 introduces the first dedicated market movement intelligence and ranking terminal workspace within ATLAS. It is located canonically at `/markets/movers` as a core subsection of **Markets (Module 02)**.

The workspace is designed to answer critical institutional questions with strict financial-data integrity:
1. **What is the ranking universe?** Exactly defined, canonical, authorized subsets of instruments (Equities, Crypto Spot, Futures).
2. **Which asset class and venue?** Explicitly scoped to verified venues without conflating incompatible markets.
3. **What is the comparison window?** Explicitly defined observation reference intervals (Previous Regular Session Close, Rolling 24h Prior Window, Prior Session Settlement).
4. **Is the metric comparable?** Strictly Decimal percentage return, absolute price move, or session trading activity with explicit units.
5. **How comprehensive is the ranking?** Complete coverage reporting with candidate count, qualified count, excluded count, typed exclusion reasons, and truthful coverage status (`COMPLETE_FOR_DEFINED_UNIVERSE` vs. `PARTIAL_COVERAGE`).
6. **How recent is the data?** Freshness and delivery delay status (Realtime, Delayed, Stale) with observation timestamps distinct from ranking snapshot calculation timestamps.

### Strict Scope Boundaries
- **No Heatmaps**: Stage 64 owns Heatmaps (treemaps, sector tiles, market-cap weighting).
- **No Cross-Asset Analytics**: Stage 65 owns Cross-Asset correlation and risk scores.
- **No Multi-Factor Screeners**: Stages 94–98 own Screeners.
- **No Alerts**: Stage 80 owns Alerts.
- **No Trading or Signals**: Read-only; no Buy/Sell buttons, no momentum entry signals, no automated execution.
- **No AI Commentary Engine**: 0 LLM calls on load, filter, or refresh.

---

## 2. Core Architectural Principle: Three Pillars of Valid Rankings

A ranking is only valid if evaluated using:
1. **A Defined Universe**: An authorized, server-owned canonical collection of instruments (never an arbitrary page or unverified catalog scan).
2. **A Comparable Metric**: A standardized observation with identical quotation units and calculation rules.
3. **A Comparable Period**: A uniform, verified reference window (e.g. previous regular session close vs. rolling 24h).

```
Ranking = Sort(
    Qualified Metric Observations
    for Instruments in Defined Universe
    using Compatible Reference Periods
)
```

### Prohibited Anti-Patterns
- Never sort an arbitrary subset or paginated table and advertise it as global market gainers.
- Never mix rolling 24h cryptocurrency returns with previous regular session equity returns.
- Never compare equity share volume with futures contract counts as equivalent activity.
- Never treat bond yield basis point changes as price percentage returns.
- Never claim "World's Top Gainers" or "Global Most Active" when coverage is bounded to the ATLAS covered catalog.

---

## 3. Supported Ranking Universes

| Universe ID | Display Name | Asset Class | Venues | Supported Categories | Supported Windows | Activity Unit |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `univ_us_equities` | Covered US Equities | Equity | NASDAQ, NYSE, BATS | Gainers, Losers, Most Active | Prev Regular Session, Current Session | Shares Traded |
| `univ_crypto_spot` | Supported Crypto Spot Markets | Crypto | Binance, Coinbase, Kraken | Gainers, Losers, Most Active | Rolling 24h | 24h Quote Turnover (USDT) |
| `univ_futures` | Supported Futures Contracts | Futures | NYMEX, COMEX, CBOT, CME, ICE | Gainers, Losers, Most Active | Prior Settlement, Current Session | Contracts Traded |

---

## 4. Mathematical Qualification & Ranking Engine

### A. Decimal Price Percentage Return
For compatible price observations with positive reference:
$$\text{percent\_change} = \frac{\text{current\_price} - \text{reference\_price}}{\text{reference\_price}} \times 100$$

### B. Denominator and Zero-Change Qualification Rules
1. **Non-Positive Reference Denominators**: If $\text{reference\_price} \le 0$, conventional percentage return is undefined. The security is strictly excluded from percentage Gainers and Losers with typed reason `INVALID_DENOMINATOR`.
2. **Zero Price Return**: Instruments with $\text{percent\_change} = 0.00\%$ are strictly excluded from both Top Gainers and Top Losers.
3. **Missing Data**: Missing current price is excluded with `NO_CURRENT_QUOTE`; missing reference is excluded with `NO_REFERENCE`; missing volume is excluded from Most Active with `MISSING_VOLUME`. Missing data is **never** fabricated as zero.
4. **Deterministic Tie-Breaking**:
   - Gainers: `percent_change` DESC, canonical `instrument_entity_id` ASC.
   - Losers: `percent_change` ASC (most negative first), canonical `instrument_entity_id` ASC.
   - Most Active: `trading_volume` DESC, canonical `instrument_entity_id` ASC.

---

## 5. Coverage Reporting Model

Every ranking response provides complete transparency into the qualification pipeline via `MoverCoverage`:
```json
{
  "universe_size": 10,
  "candidate_count": 10,
  "evaluated_count": 10,
  "qualified_count": 8,
  "excluded_count": 2,
  "exclusion_reasons": {
    "NO_REFERENCE": 1,
    "INVALID_DENOMINATOR": 1
  },
  "coverage_status": "PARTIAL_COVERAGE",
  "ranking_as_of": "2026-10-17T15:45:00Z"
}
```

### Coverage Status Classifications:
- `COMPLETE_FOR_DEFINED_UNIVERSE`: All candidates in the defined authorized universe qualified with valid data.
- `PARTIAL_COVERAGE`: Some candidates were excluded due to data qualification rules.
- `DEGRADED`: Data source or provider feeds partially degraded.
- `UNAVAILABLE`: Zero candidates qualified.

---

## 6. HTTP API Specification

### Endpoints
1. `GET /api/v1/markets/movers`
   - **Parameters**: `universe_id` (str), `category` (gainers, losers, most_active), `window` (optional enum), `exchange` (optional venue string), `limit` (int, default 25, max 100), `cursor` (opaque keyset cursor).
   - **Guarantees**: 100% read-only, 0 writes, 0 provider fanout, Decimal precision, cache-control `no-store`.
2. `GET /api/v1/markets/movers/universes`
   - Returns all authorized mover universes with metadata, asset classes, and default ID.
3. `GET /api/v1/markets/movers/metrics`
   - Returns valid ranking metric combinations, windows, and activity units for the requested universe.

---

## 7. Professional Terminal UI Layout

The terminal layout at `/markets/movers` adheres to institutional design standards (VS Code, Bloomberg, OpenBB):
- **Header**: Canonical title, universe badge, snapshot timestamp, search trigger (Ctrl+K), manual refresh.
- **Universe & Window Selectors**: Segmented pill selectors showing asset class tags and supported comparison intervals.
- **Category Tabs**: Top Gainers (emerald), Top Losers (rose), Most Active (blue with explicit unit label).
- **Venue Filters**: Compact venue dropdown scoped to the active universe.
- **Coverage Summary**: Status badge, qualified vs. candidate counts, expandable exclusion breakdown.
- **Leaderboard Table**: Tabular numerals, ordinal ranks (`#1`, `#2`), symbol/name, venue, current, reference, change, change %, activity volume, and freshness.
- **Selected Mover Inspector**: Slide-over panel displaying canonical instrument UUID, market series identity, exact metric values, reference timestamps, provider provenance, and deep links to `/charts` and asset-class directories.
