# ATLAS ETFs & Funds Markets V1 (Stage 58 Architecture)

## Executive Summary

Stage 58 implements **ETFs & Funds Markets V1** inside ATLAS Module 2 (`/markets`). It provides a institutional-grade, high-density discovery, inspection, and observational analytics workspace for exchange-traded funds (ETFs), open-end mutual funds, and closed-end funds (CEFs).

The canonical workspace route is:
```
/markets/funds
```
integrated directly into the existing Markets application alongside Markets Overview (`/markets`) and Equities (`/markets/equities`).

---

## 1. Architecture Flow

```
ATLAS MARKETS (Module 02)
       │
       ├── Overview (Stage 56)           [/markets]
       ├── Equities (Stage 57)           [/markets/equities]
       │
       └── ETFs & Funds (Stage 58)       [/markets/funds]
               │
               ├── MarketsNavigationTabs (Overview, Equities, ETFs & Funds, Future St 59-65)
               ├── FundsHeader (Search Ctrl+K, Charts, Research, Refresh)
               ├── FundCoverageSummary (Canonical Funds, ETFs, Mutual Funds, CEFs, Listings, Quotes, NAVs)
               ├── FundTypeSelector (All Funds, ETFs, Mutual Funds, Closed-End Funds)
               ├── FundDirectoryFilters (Country, Exchange, Domicile, Category, Currency, Reset)
               ├── FundDirectoryTable (High-density financial table with pagination & status)
               └── FundInspector (Deep inspection: Identity, Trade Quote, Official NAV, Fees, AUM, Benchmark, Sponsor)
                       │
                       ▼
               Funds REST API (FastAPI)
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   FundDirectoryService      FundMarketReadService
          │                         │
     PostgreSQL                LiveQuoteService (Stage 41 Redis)
   - Financial Instruments     ReferenceCloseResolver (Stage 39 ClickHouse)
   - FundMetadata              MarketDataFreshnessClassifier (Stage 44)
   - FundListingMetadata
   - FundNAVObservation
```

---

## 2. Core Identity Architecture

### A. Distinction of Five Financial Concepts
Stage 58 enforces strict separation between:
1. **Fund Product / Vehicle**: The legal collective investment vehicle or strategy (e.g. SPDR S&P 500 Trust, Vanguard 500 Index Fund).
2. **Fund Share Class**: Specific class of fund units with dedicated fee structure, distribution policy, minimums, and NAV (e.g. Vanguard Admiral Shares `VFIAX`, Institutional Shares).
3. **Financial Instrument**: The canonical security or share class entity identified by a permanent UUID (`instrument_entity_id`).
4. **Exchange Listing**: The specific venue trading registration with Market Identifier Code (MIC), exchange-scoped symbol, and trading currency (e.g. `XNYS:SPY`, `XNAS:QQQ`).
5. **Market Quote vs. Valuation Series**: The continuous exchange trade price stream vs. the official Net Asset Value (NAV) calculated at market close.

### B. ETF vs. ETN Classification
- **ETFs (Exchange-Traded Funds)** represent equity ownership in a pooled portfolio of securities or assets.
- **ETNs (Exchange-Traded Notes)** are senior, unsecured debt instruments issued by financial institutions and backed solely by the issuer's credit. ETNs are explicitly excluded from the equity fund catalog or classified separately.

### C. Open-End Mutual Funds
- Traditional mutual funds (e.g. `VTSAX`, `SWPPX`) are unlisted and do not trade on secondary exchange markets.
- They do **not** receive continuous bids, asks, or fake exchange trade quotes.
- They report official published Net Asset Values (NAVs) per unit, valued as of documented valuation business dates.

### D. Closed-End Funds (CEFs)
- Closed-end funds (e.g. `BST`, `UTF`) trade on exchange venues while also publishing official NAVs.
- Both market trading price and official NAV are preserved and displayed with distinct semantics without conflation.

---

## 3. The Critical Financial Data Rule: Market Price vs. Net Asset Value (NAV)

**An ETF's exchange-traded price and a fund's Net Asset Value (NAV) are fundamentally distinct financial concepts.**

| Metric | Scope | Source Authority | Frequency | Currency |
|---|---|---|---|---|
| **Market Last Price** | Traded unit on exchange venue | Stage 41 Redis latest quotes & Stage 39 ClickHouse | Continuous/Realtime during exchange hours | Trading Currency (e.g. USD) |
| **Official NAV** | Net Asset Value per share | Stage 58 FundNAVObservation / Authoritative catalog | Daily valuation points at market close | NAV / Share Class Currency |

1. **No Conflation**: An exchange quote is never substituted for NAV, and official NAV is never presented as an exchange last trade price.
2. **Realtime Isolation**: Realtime quote events (`market.quote.updated`) update exchange market prices for applicable listed ETFs. They **never** mutate official NAV.
3. **Valuation Date Integrity**: All official NAVs explicitly display their valuation date (e.g. `2026-03-30`) and publication details. Historical or end-of-day NAV is never labeled as "Live".
4. **Independent Returns**: Market price percentage changes and NAV percentage changes are separate metrics and never mixed or labeled as raw total returns.
5. **Missing States**: When an ETF lacks a quote, `Quote unavailable` is displayed while preserving valid NAV. When an unlisted fund has no exchange listing, `Not Listed` or `Unlisted` is explicitly displayed.

---

## 4. Fund Fees, AUM and Benchmark Semantics

### A. Expense Ratios
- Metric types are explicitly defined: `net_expense_ratio`, `gross_expense_ratio`, `management_fee`.
- Fees are preserved as percentages (e.g. `0.09%`, `0.03%`).
- Missing fee data is rendered as `—` or `Fee data unavailable`, **never** fabricated as `0.00%`.
- Fees reflect the specific share-class scope.

### B. Assets Under Management (AUM)
- Reported with full numerical precision, currency, scope (e.g. `Fund Net Assets`), and as-of date.
- Formatted compactly for high-density display (e.g. `$540.20B USD`, `$31.50B USD`).
- AUM changes are never presented or inferred as investor fund flows.

### C. Benchmarks
- Verified benchmark index relationships (e.g. `S&P 500 Index`, `NASDAQ-100 Index`) are linked via canonical entity relationships with verification badges.
- Indices are never substituted with popular tracking ETF tickers.

---

## 5. Authenticated API Endpoints

All endpoints require Stage 13 authentication and Stage 14 authorization context:

### 1. `GET /api/v1/markets/funds`
Retrieve paginated canonical fund directory with applied filters:
- Parameters: `query`, `fund_type`, `market_country`, `exchange`, `domicile`, `fund_category`, `share_class_currency`, `limit` (default 25, max 100), `cursor`.
- Response: `FundDirectoryResponse` containing items, filter options, coverage summary, cursor, and total matched count.

### 2. `GET /api/v1/markets/funds/filters`
Retrieve authoritative available filter facets and counts:
- Response: `FundFilterOptionsResponse` containing fund types, countries, exchanges, domiciles, categories, and currencies.

### 3. `GET /api/v1/markets/funds/{instrument_entity_id}`
Retrieve detailed fund overview, canonical identifiers, venue details, benchmark linkages, and management metadata:
- Response: `FundOverviewDetailResponse`.

### Read-Only Invariance
All read endpoints are strictly read-only:
- `0` Entity creations
- `0` Quote or NAV writes
- `0` Upstream Provider fetches on read
- `0` Background ingestion jobs on page load

---

## 6. Frontend Components Hierarchy

```
FundsPage (apps/web/src/components/markets/funds/FundsPage.tsx)
├── MarketsNavigationTabs (Subview navigation across Markets modules)
├── FundsHeader (Search trigger, charts link, research link, manual refresh)
├── FundCoverageSummary (Canonical metrics: Total Funds, Listed, Quotes, NAVs)
├── FundTypeSelector (Tab list: All Funds, ETFs, Mutual Funds, Closed-End Funds)
├── FundDirectoryFilters (Scoped search, country, exchange, domicile, category, currency, reset)
├── FundDirectoryTable (High-density table with deterministic pagination)
│   └── FundDirectoryRow (Individual row with badge, prices, NAVs, fees, and status)
├── FundInspector (Side inspector with identity, trade quote, NAV, fees, AUM, benchmark, management)
└── FundEmptyState (Truthful empty catalog and zero-result search states)
```

---

## 7. Strict UI and Design Rules

- **Palette**: Dark, high-contrast, institutional theme utilizing curated ATLAS design tokens (`--atlas-surface-card`, `--atlas-border-subtle`, emerald-400, amber-400, rose-400).
- **Prohibitions**:
  - No purple gradients (`from-purple`, `to-purple`).
  - No emoji icons.
  - No fake prices, NAVs, AUM, expense ratios, or performance numbers.
  - No execution trading buttons (`Buy Fund`, `Sell Fund`, `Trade Now`).
  - No AI investment recommendations (`Top Pick`, `Strong Buy`).
- **Data Integrity**: Missing values are rendered as `—` or descriptive unavailable states, never false zeros.

---

## 8. Verification and Quality Gates

### Automated Backend Tests
Located in `apps/api/tests/markets/test_markets_funds.py` (19 test cases, 100% pass):
- Fund identity & UUID stability
- Product vs share class separation
- ETF, Mutual Fund, Closed-End Fund classification
- Exchange listing metadata & scoped tickers
- Price vs. NAV separation and non-conflation
- Missing quote / missing NAV handling
- Fee types, scales, and non-zero missing fee enforcement
- AUM currency and scope integrity
- Benchmark verified relationships
- Authenticated endpoints and 404 validation
- Read-only guarantees

### Automated Frontend Tests
Located in `apps/web/tests/markets-funds.test.ts` (10 test cases, 100% pass):
- Component export integrity
- Price formatting (2 decimals, explicit currency)
- NAV formatting (4 decimals, explicit currency)
- Expense ratio formatting (never 0.00% for missing fee)
- AUM formatting (compact abbreviation)
- Change formatting (signed percentage with directional colors)
- Valuation date formatting
- Route existence & Next.js static generation
- Navigation tab active status
- Strict design rule enforcement (no purple gradients, no trading buttons)

### Regression Suites
- Stage 56 Markets Overview: 15 backend tests, 10 frontend tests pass without regressions.
- Stage 57 Equities: 30 backend tests, 15 frontend tests pass without regressions.
- Ruff linter: `All checks passed!`
- Ruff formatter: `7 files already formatted`
- Next.js production build: `Compiled successfully`, 31/31 static routes generated including `/markets/funds`.

---

## 9. Stage 58 Roadmap Position & Boundaries

Stage 58 implements fund discovery and source-aware fund inspection. It explicitly does **not** implement:
- Dedicated FX markets (Stage 59)
- Dedicated Cryptocurrency markets (Stage 60)
- Bonds / Fixed income (Stage 61)
- Futures & Commodities (Stage 62)
- Advanced Charts V1 (Stage 66)
- Watchlists (Stage 76)
- Full ETF holdings ingestion or look-through risk
- Daily ETF creation / redemption flow analytics
- Intraday fair-value / iNAV trading signals
- Multi-factor fund screeners (Stage 94)
- Portfolio management & trading (Stage 110/141)
- Autonomous research agents (Stage 146)

**Next Roadmap Stage: Stage 59 — Build FX Markets Experience.**
