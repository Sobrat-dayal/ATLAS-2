# ATLAS — Financial Screeners V1 (Stage 94)

## Executive Summary

**Stage 94** of the canonical ATLAS development roadmap delivers the **ATLAS Financial Screener Engine** and the **Screeners V1 Workspace** at `/screeners`.

The Screener is an institutional-grade security discovery and quantitative research workstation designed to filter, sort, and explore canonical financial instruments using verified market data, corporate fundamental statements, and valuation ratios. Every result row represents an authenticated financial instrument linked to its verified issuer company and exchange listing venue, adhering to strict accounting, statistical, and entitlement integrity.

---

## 1. Core Architectural Invariants

### 1.1 Strict Separation of Issuer, Security, and Listing Identity
A fundamental tenet of ATLAS is that a corporate issuer, a financial instrument, and an exchange listing are separate domain concepts:
- **Company Entity (Stage 18)**: The issuing corporation (e.g. `Alphabet Inc.`, `Infosys Limited`, `Toyota Motor Corporation`). Corporate fundamentals (Revenue, Net Income, Total Assets) belong to the Company Entity, not to an exchange listing.
- **Financial Instrument Entity (Stage 17)**: The canonical security identity (e.g. `Alphabet Inc. Class A`, `Alphabet Inc. Class C`, `Infosys Ltd. ADR`, `Infosys Ltd. Common Stock`). A single company may issue multiple share classes with distinct voting rights or par values.
- **Listing Entity (Stage 56–57)**: The exchange-scoped trading record identified by Market Identifier Code (MIC) and ticker symbol (e.g. `AAPL` on `XNAS`, `INFY` on `XNYS`, `INFYS` on `XNSE`). Ticker strings are venue-scoped and not globally unique.

### 1.2 Multiple Share Classes
Companies with multiple share classes maintain distinct Financial Instrument UUIDs while pointing to the same underlying Issuer Company Entity UUID:
- `GOOGL` (Alphabet Inc. Class A, Voting) vs `GOOG` (Alphabet Inc. Class C, Non-Voting): Both share the same issuer company entity (`company:googl`), but possess distinct instrument identities and market caps.
- `BRK.A` (Berkshire Hathaway Class A) vs `BRK.B` (Class B): Denominated under distinct share counts, share prices, and voting privileges.

### 1.3 Cross-Listings and Depositary Receipts (ADRs)
A depositary receipt represents claims on foreign shares rather than a domestic operating company:
- `TSM` (Taiwan Semiconductor ADR on NYSE): Listed in the United States (`US`) on `XNYS` in `USD`, but issuer legal domicile remains Taiwan (`TW`).
- `INFY` (Infosys ADR on NYSE in USD) vs `INFYS` (Infosys Common on NSE in INR): Both resolve to the same underlying Indian corporate issuer (`company:infosys`), but represent different instruments trading on different venues in different currencies.

### 1.4 Operating Equities vs ETFs and Funds
Exchange-Traded Funds (ETFs) such as `SPY` or `QQQ` are collective investment vehicles (funds), not operating corporations. They report Assets Under Management (AUM) rather than corporate Revenue or Net Income. By default, the `common_equity` screening universe strictly excludes ETFs, mutual funds, and closed-end funds.

### 1.5 Active vs Delisted / Suspended Status
- By default, active investment universes (`common_equity`, `all_equity`, `us_large_cap`) filter out delisted, suspended, or inactive securities to reflect tradable opportunities.
- For historical, survivorship-bias-free research, the dedicated `delisted_equity` universe allows discovering historically traded securities (e.g. Enron Corp `ENE`, Lehman Brothers `LEH`).

---

## 2. Market Data, Fundamentals, and Valuation Ratios

### 2.1 Market Capitalization
- Represents the total institutional equity market capitalization.
- Must not be fabricated by multiplying an arbitrary share-class price across total issuer shares across incompatible classes.
- Stored as exact Decimals.

### 2.2 Pricing and Quote Freshness
- Last Traded Price is verified against canonical market execution feeds (Stages 33, 41, 44).
- Prices carry explicit trading currency, exchange session timestamp, and freshness qualification (`LIVE`, `DELAYED`, `END_OF_DAY`, `STALE`).
- Stale prices are labeled accurately and never represented as verified live quotes.

### 2.3 Volume and Liquidity
- `volume_latest`: Number of shares traded during the latest completed or active trading session.
- `volume_20d_avg`: 20-trading-session average daily volume (excluding exchange holidays and market closures).
- `traded_value_latest`: Daily monetary turnover ($ traded = price × volume).

### 2.4 Fundamental Statements
Corporate fundamentals inherit verified data from multi-period annual reports (Stage 82):
- **Revenue**: Top-line revenue reported on consolidated income statements.
- **Net Income**: Consolidated net profit / loss. Can be legitimate negative numbers for loss-making corporations.
- **Operating Income (EBIT)**: Operating profit before tax and financing costs.
- **Total Assets**: Balance sheet asset base.
- **Shareholders' Equity (Book Value)**: Total equity attributable to shareholders.
- **Diluted EPS**: Diluted earnings per share for the reported period.

### 2.5 Valuation Ratios & Strict Negative Earnings Policy
- **P/E Ratio (Trailing)**: Price to diluted earnings per share.
  - **Strict Policy on Non-Positive Earnings**: If a company reports zero or negative net income (such as early-stage biotech firm `BIOX`), conventional trailing P/E is mathematically undefined and economically meaningless. The screener returns `None` / `NOT_MEANINGFUL` ("N/M"). It is **NEVER** displayed as zero or as a deceptive negative multiple.
- **P/B Ratio**: Market capitalization divided by shareholders' book equity.
- **P/S Ratio**: Market capitalization divided by total annual revenue.
- **Dividend Yield**: Trailing annual dividend payout expressed as a percentage of market price.
- **Margins & Profitability**: Gross Profit Margin, Operating Margin, Net Profit Margin, Return on Equity (ROE), and Return on Assets (ROA).

### 2.6 Strict NULL Handling: Missing is Not Zero
- Missing financial statement facts or unavailable market quotes are stored as `None` (`MISSING` / "—").
- **Critical Screener Invariant**: Under standard screening semantics, missing values **NEVER** satisfy relational comparisons (`>`, `<`, `>=`, `<=`, `BETWEEN`). A stock with missing revenue will never pass `revenue > 0`.

---

## 3. Filter Registry & Operators

### 3.1 Supported Comparison Operators
The Filter Registry enforces a strict allowlist of typed operators:
- `GTE` (`>=`): Greater than or equal to threshold.
- `LTE` (`<=`): Less than or equal to threshold.
- `GT` (`>`): Strictly greater than.
- `LT` (`<`): Strictly less than.
- `EQ` (`=`): Exact equality.
- `NE` (`≠`): Not equal.
- `BETWEEN`: Inclusive range (`min_val <= x <= max_val`). Validates that lower bound <= upper bound.
- `IN`: Set membership within an approved list of values.

### 3.2 Basic AND Composition & Complexity Guardrails
- Multiple filter criteria are combined using strict Boolean `AND` logic:
  $$\text{Predicate} = \text{Condition}_1 \land \text{Condition}_2 \land \dots \land \text{Condition}_N$$
- Arbitrary recursive Boolean tree nesting, arbitrary user SQL, and unvetted formula languages remain deferred.
- Bounded complexity limit: Maximum of 20 active filter conditions per query. Exceeding this limit immediately raises `ScreenerQueryLimitExceededError`.

---

## 4. Query Planning & High-Performance Execution

### 4.1 Server-Side Execution Flow
```
    Client Screener Query
              │
              ▼
    Query Validation (Filter Registry, Types, Operators, Ranges)
              │
              ▼
    Universe Reduction (Asset class, Security Type, Status, Venue Scopes)
              │
              ▼
    Indexed Predicate Pushdown (Market Cap, Price, Revenue, P/E)
              │
              ▼
    Deterministic Sorting (Primary column NULLS LAST + Stable UUID Tie-breaker)
              │
              ▼
    Bounded Pagination (Page size 1–100, Opaque cursor generation)
              │
              ▼
    Cell-Level Provenance & Freshness Enrichment
              │
              ▼
    ScreenerRunResponse
```

### 4.2 Resource Budget & Zero Fanout Guarantee
- **Zero Client-Side Heavy Filtering**: The full equity universe is never downloaded to the browser.
- **Zero Upstream Provider Fanout on Read**: Screener queries execute against indexed database-backed read projections and memory caches. Zero external HTTP calls are made per screened security during a query.
- **Deterministic Pagination**: Sorting uses a stable tie-breaker: `(record.instrument_entity_id, record.listing_id)` in ascending order. This guarantees zero dropped or duplicated rows across pagination boundaries.

---

## 5. API Contracts (`/api/v1/screeners`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/screeners/universes` | Lists approved canonical screening universes (`common_equity`, `all_equity`, etc.). |
| `GET` | `/api/v1/screeners/filters` | Retrieves filter catalog with allowed operators, data types, and units. |
| `GET` | `/api/v1/screeners/columns` | Retrieves table column definitions and default visibility. |
| `GET` | `/api/v1/screeners/exchanges` | Lists supported exchange venues (`XNAS`, `XNYS`, `XNSE`, `XLON`, `XETR`, etc.) with security counts. |
| `GET` | `/api/v1/screeners/geographies` | Lists supported market countries with active listing counts. |
| `GET` | `/api/v1/screeners/industries` | Lists canonical classification sectors and child industry groups. |
| `POST` | `/api/v1/screeners/validate` | Validates candidate filter predicates without full screen execution. |
| `POST` | `/api/v1/screeners/run` | Executes bounded screening query with sorting and pagination. |
| `GET` | `/api/v1/screeners/coverage` | Returns institutional data coverage audit and freshness status breakdown. |

---

## 6. Frontend Workspace Architecture (`/screeners`)

The Screener UI is an institutional terminal workspace built with dense tabular typography, tabular numerals, and dark/light theme integration:
1. **ScreenerHeader**: Displays active universe badge, matching security count vs total evaluated, quick presets, and primary controls ("Run Screener", "Reset", "Columns", "Coverage").
2. **ScreenerToolbar**: Quick filter dropdowns for Exchange Venue, Market Country, and Sector with active selection badges.
3. **ScreenerFilterBuilder**: Allows choosing any approved metric, comparison operator, threshold or range inputs, and quick presets (Mega-Cap, Low P/E, High Dividend, Active Volume).
4. **ScreenerActiveFilters**: Dismissible filter chips showing active thresholds with "Clear All" capability.
5. **ScreenerResultsTable**: High-density sortable table with:
   - Sticky left column for Symbol and Share Class.
   - Column sorting with ASC/DESC toggling.
   - Right-aligned numeric data with tabular numerals.
   - Distinct badges for missing ("—") and not meaningful ("N/M") values.
   - Quick row actions: View Chart (`/charts?symbol=...`), View Company (`/companies?id=...`).
6. **ScreenerPagination**: Controls for page navigation (Next, Previous) and page size selection (25, 50, 100).
7. **ScreenerColumnManager**: Modal dialog for toggling visible columns grouped by category.
8. **ScreenerSourceInspector**: Flyout inspector drawer detailing exact canonical UUIDs, exchange venue metadata, issuer legal domicile, and cell-by-cell source provenance and observation periods.
9. **ScreenerCoveragePanel**: Audit banner providing live counts of covered equities, quotes, market caps, fundamentals, and providers.

---

## 7. Automated Test Suite Summary

The test suite in `apps/api/tests/test_screeners.py` runs 30 comprehensive automated tests:
1. `test_canonical_security_identity`: Confirms all candidates have verified instrument, listing, and company UUIDs.
2. `test_multiple_share_classes_have_distinct_instrument_ids`: Verifies GOOGL (Class A) vs GOOG (Class C) have distinct instrument UUIDs sharing `company:googl`.
3. `test_cross_listed_adr_and_domestic_equity_distinction`: Verifies INFY ADR (NYSE in USD) vs INFYS Common (NSE in INR) share the same issuer with distinct instrument IDs.
4. `test_etf_exclusion_from_common_equity_universe`: Confirms ETFs (SPY) are excluded from `common_equity`.
5. `test_delisted_security_exclusion_from_active_universe`: Confirms delisted equities (Enron) are excluded from active screens, but accessible in `delisted_equity`.
6. `test_exchange_filter_pushdown`: Verifies venue filtering (`XNAS`).
7. `test_country_filters_distinguish_listing_and_issuer_domicile`: Verifies Taiwan domicile for TSM listed in the US.
8. `test_sector_and_industry_filters`: Verifies classification filters.
9. `test_market_cap_gte_filter`: Tests `>= $1T` market cap filter.
10. `test_price_range_between_filter`: Tests `BETWEEN 200 AND 500` price filter.
11. `test_average_volume_filter`: Tests 20-day average volume filter.
12. `test_revenue_and_net_income_filters`: Tests combined fundamental filters.
13. `test_pe_ratio_lte_filter_excludes_negative_earnings`: Confirms loss-making stocks (`BIOX`) are excluded from `P/E <= 40`.
14. `test_strict_null_handling_missing_metric_does_not_satisfy_comparisons`: Confirms missing metrics never satisfy `>= 0`.
15. `test_dividend_yield_filter`: Tests dividend yield filtering.
16. `test_deterministic_sorting_with_stable_tie_breaker`: Tests stable sorting and reproducibility.
17. `test_bounded_pagination_and_cursor`: Tests cursor-based pagination and disjoint row pages.
18. `test_unknown_universe_raises_error`: Validates universe not found error.
19. `test_unknown_filter_raises_error`: Validates filter not found error.
20. `test_invalid_range_raises_error`: Validates min > max range error.
21. `test_filter_complexity_limit_exceeded`: Validates 20-filter limit.
22. `test_api_list_universes`: Tests `/screeners/universes`.
23. `test_api_list_filters`: Tests `/screeners/filters`.
24. `test_api_list_columns`: Tests `/screeners/columns`.
25. `test_api_list_exchanges`: Tests `/screeners/exchanges`.
26. `test_api_list_geographies`: Tests `/screeners/geographies`.
27. `test_api_list_industries`: Tests `/screeners/industries`.
28. `test_api_validate_endpoint`: Tests `/screeners/validate`.
29. `test_api_run_screener`: Tests `/screeners/run`.
30. `test_api_coverage_endpoint`: Tests `/screeners/coverage`.

**Result**: 30 passed in 2.79 seconds.

---

## 8. Roadmap Boundaries

- **Stage 94 owns**: Canonical Universes, Basic Fundamental & Market Data Filtering, Server-Side Query Planning, Deterministic Sorting, Bounded Pagination, and Screeners V1 Workspace.
- **Stage 95 owns**: Institutional-Grade Visual Screener Filter Builder (Advanced Visual Query Construction, Interactive Financial Filter Controls, Dynamic Metric Discovery, Intelligent Validation, Filter Dependency Management, Query Transparency, and Terminal UX). Documented in [VISUAL_SCREENER_FILTERS.md](file:///e:/proooo/Atlas/docs/VISUAL_SCREENER_FILTERS.md).
- **Stage 96 owns**: Fundamental, Technical, and Multi-Factor Screening Expansion. Documented in [ADVANCED_SCREENER_FACTORS.md](file:///e:/proooo/Atlas/docs/ADVANCED_SCREENER_FACTORS.md).
- **Stage 97 owns**: Saved Screens, Advanced Sorting, Factor Ranking, and Professional Financial Data Exports. Documented in [SAVED_SCREENERS_RANKING_EXPORTS.md](file:///e:/proooo/Atlas/docs/SAVED_SCREENERS_RANKING_EXPORTS.md).
- **Stage 98 owns**: Institutional-Grade Natural-Language Screener Translation Engine, Semantic Mapping, Multi-Factor Query Construction, and Interactive Ambiguity Resolution. Documented in [NATURAL_LANGUAGE_SCREENER.md](file:///e:/proooo/Atlas/docs/NATURAL_LANGUAGE_SCREENER.md).
- **Stage 98 completes the 5-stage Screener series (Stages 94–98).**
- **Stage 99 (News Module) is the next canonical roadmap stage.**

