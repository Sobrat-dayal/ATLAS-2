# ATLAS FX Markets V1 (Stage 59 Architecture)

## Executive Summary

Stage 59 implements **FX Markets V1: Global Foreign Exchange Intelligence, Currency Pair Discovery, Spot Exchange Rates, Bid/Ask Analytics and Currency Conversion** inside ATLAS Module 2 (`/markets`). It delivers an institutional-grade, high-density discovery, inspection, and observational analytics workspace for currency pairs, spot exchange-rate observations, bid/ask spreads, and a read-only indicative currency converter.

The canonical workspace route is:
```
/markets/fx
```
integrated directly into the existing Markets application alongside Markets Overview (`/markets`), Equities (`/markets/equities`), and ETFs & Funds (`/markets/funds`).

---

## 1. Architecture Flow

```
ATLAS MARKETS (Module 02)
       │
       ├── Overview (Stage 56)           [/markets]
       ├── Equities (Stage 57)           [/markets/equities]
       ├── ETFs & Funds (Stage 58)       [/markets/funds]
       │
       └── Foreign Exchange (Stage 59)   [/markets/fx]
               │
               ├── MarketsNavigationTabs (Overview, Equities, Funds, FX, Future St 60-65)
               ├── FxHeader (Search Ctrl+K, Charts, Economics, Refresh)
               ├── FxCoverageSummary (Configured Pairs, Base/Quote Currencies, Rates Observed, Bid/Ask Active, Spread Computed)
               ├── FxPairFilters (Search query, Base Currency filter, Quote Currency filter, Reset)
               ├── FxPairDirectoryTable (High-density tabular FX display with deterministic keyset/offset pagination)
               │     └── FxPairDirectoryRow (Pair, Rate Kind, Bid, Ask, Midpoint, Spread, 24h Change, Status, Source, Observed)
               ├── FxPairInspector (Deep inspection: Canonical UUID, Orientation explanation, Spot Quote, Base & Quote metadata, Cross-module navigation)
               └── FxCurrencyConverter (Read-only indicative currency converter with Decimal precision, swap control, and non-executable disclosure)
                       │
                       ▼
               FX REST API (FastAPI)
                       │
          ┌────────────┼────────────────────────┐
          ▼            ▼                        ▼
   FxDirectoryService  FxMarketReadService   FxConversionService
          │            │                        │
     PostgreSQL   LiveQuoteService (Stage 41)   Decimal Arithmetic Engine
                  ReferenceCloseResolver (St 39) ISO 4217 Rounding Policy
                  FreshnessClassifier (Stage 44) No Triangulation Guard
```

---

## 2. Core Identity Architecture

### A. Base and Quote Currency Semantics
For every currency pair formatted in conventional `BASE/QUOTE` notation:
- **Exchange Rate Meaning**: Units of `QUOTE` currency required for one unit of `BASE` currency.
- **Example**: `EUR/USD = 1.0850` mathematically means `1 EUR = 1.0850 USD`.
- **Directional Integrity**: `EUR/USD` and `USD/EUR` are distinct currency pair instruments with inverse mathematical orientations. ATLAS never conflates a direct pair with its reverse or silently flips symbols without preserving canonical instrument identity.

### B. Canonical Financial Instrument UUID Authority
Spot currency pairs are authoritative Financial Instruments identified by permanent UUIDs (`instrument_entity_id`) pursuant to Stage 17. The ticker text or display pair string is never used as a database primary key.

### C. Validated ISO 4217 Fiat Currency Registry
All currency codes are validated against a curated ISO 4217 reference registry (`ISO_4217_REGISTRY`). Arbitrary 3-letter strings and synthetic abbreviations are rejected.

### D. Distinction Between FX Quotation Precision and Currency Minor Units
Quotation precision in FX secondary markets (e.g., 4 decimals for EUR/USD, 2 decimals for USD/JPY) is strictly decoupled from ISO currency minor units (e.g., 0 minor units for physical JPY cash units, 2 for USD). Output money rounding for currency conversion strictly honors the destination currency's minor units.

### E. Fiat FX vs. Cryptocurrency Separation (Stage 59 vs. Stage 60)
Cryptocurrency assets (e.g. BTC, ETH, USDT) are explicitly excluded from the fiat FX catalog. Cryptocurrency markets belong strictly to Stage 60.

### F. Spot FX vs. FX Derivatives
Stage 59 is strictly confined to spot exchange rates and basic observational analytics. FX forwards, currency swaps, NDFs, and FX options are deferred to subsequent risk, trading, and derivatives stages.

---

## 3. Market Data, Quotes, and Spreads

### A. Decentralized OTC Market Reality
Spot foreign exchange is an over-the-counter decentralized market without a single consolidated global exchange trade tape. ATLAS does not fabricate an equity-style universal consolidated Last trade. Observations are labeled with explicit rate kinds.

### B. Explicit Rate Kind Classification
Each rate observation is classified under a typed enumeration:
- `SPOT_BID_ASK`: Two-way executable or indicative dealer bid and ask quote.
- `INDICATIVE_MID`: Calculated or provider-supplied midpoint.
- `REFERENCE_RATE`: Central bank or official reference fixing rate (e.g., ECB reference rates).
- `LAST_TRADE`: Last observed OTC transaction where genuinely reported by provider.
- `CROSSED_INVALID`: Inconsistent market observation where `bid > ask`.
- `UNKNOWN`: Unverified or unclassified observation.

### C. Valid Bid/Ask and Spread Mathematics
- **Compatibility Requirement**: Bid and ask must originate from the same provider observation and compatible timestamp. ATLAS strictly prohibits mixing bid from Provider A with ask from Provider B.
- **Absolute Spread**:
  $$\text{spread\_absolute} = \text{ask} - \text{bid}$$
- **Calculated Midpoint**:
  $$\text{midpoint} = \frac{\text{bid} + \text{ask}}{2}$$
- **Normalized Basis Points**:
  $$\text{spread\_bps} = \left(\frac{\text{ask} - \text{bid}}{\text{midpoint}}\right) \times 10,000$$
- **Pip Conventions**: Pip size is pair-specific: `0.01` for JPY and INR pairs, `0.0001` for standard major pairs.
  $$\text{spread\_pips} = \frac{\text{ask} - \text{bid}}{\text{pip\_size}}$$
- **Crossed Markets Guard**: If $\text{bid} > \text{ask}$, the quote is flagged as `CROSSED_INVALID`, spread is rendered as null, and data status is marked `INCONSISTENT`. Negative spreads are never reported or silently repaired.

### D. Observation Provenance and Freshness
- Source observation timestamp (`observed_at`) and ingestion receive time (`received_at`) are explicitly preserved.
- Freshness classification (Stage 44) categorizes observations into `FRESH`, `STALE`, `DELAYED`, or `UNKNOWN`.

---

## 4. Indicative Currency Conversion Engine

### A. Read-Only Informational Scope
The currency converter in Stage 59 is strictly an informational observational tool. It does not:
- Place broker trading orders.
- Provide guaranteed execution or bank remittance rates.
- Mutate user portfolios or accounts.
- Incur transfer fees or commissions.

### B. Conversion Direction Mathematics
- **Direct Conversion** ($\text{BASE} \to \text{QUOTE}$):
  $$\text{output\_amount} = \text{input\_amount} \times \text{rate}$$
- **Reverse Conversion** ($\text{QUOTE} \to \text{BASE}$):
  $$\text{output\_amount} = \frac{\text{input\_amount}}{\text{rate}}$$
- **Quote-Side Directional Illustration**:
  - Selling BASE to buy QUOTE: uses quoting dealer **Bid** ($\text{input} \times \text{bid}$).
  - Paying QUOTE to buy BASE: uses quoting dealer **Ask** ($\text{input} / \text{ask}$).
- **Same-Currency Identity**:
  - If $\text{from\_currency} == \text{to\_currency}$, returns $1:1$ arithmetic identity without requiring a market observation.

### C. No Synthetic Cross-Rate Triangulation
Stage 59 enforces a strict no-triangulation rule: if no direct or reverse pair exists for the requested currencies, the API truthfully rejects the conversion:
```
Conversion unavailable for currency pair INR/CHF. ATLAS does not construct multi-leg synthetic cross-rates in Stage 59.
```
ATLAS never synthesizes a third currency cross without audited synchronized timestamps, compatible fixing methodologies, and explicit provenance.

### D. High-Precision Decimal Arithmetic
All calculations are performed using Python `Decimal` with `ROUND_HALF_UP` quantization to the destination currency's minor units (e.g. 0 decimals for JPY, 2 for USD/EUR).

---

## 5. Authenticated API Endpoints

All endpoints require Stage 13 authentication and enforce Stage 14 `atlas.access` authorization:

### 1. `GET /api/v1/markets/fx`
Retrieve paginated canonical currency pair directory with market quotes and spreads:
- Parameters: `base_currency`, `quote_currency`, `query`, `limit` (default 25, max 100), `cursor`.
- Response: `FxPairDirectoryResponse`.

### 2. `GET /api/v1/markets/fx/currencies`
Retrieve supported fiat currencies represented in the canonical catalog:
- Response: `FxCurrenciesResponse`.

### 3. `GET /api/v1/markets/fx/{instrument_entity_id}`
Retrieve detailed overview, orientation explanation, and currency entities for a selected pair:
- Response: `FxPairOverviewDetailResponse`.

### 4. `POST /api/v1/markets/fx/convert`
Perform read-only indicative currency conversion:
- Request: `FxConversionRequest` (`amount`, `from_currency`, `to_currency`, `mode`).
- Response: `FxConversionResponse`.

### Read-Only Invariance
All FX read and conversion endpoints guarantee:
- `0` Database writes (PostgreSQL, ClickHouse, Redis).
- `0` External Provider network calls on user request.
- `0` Broker orders or financial mutations.
- `0` Agent or workflow executions.

---

## 6. Frontend Component Architecture

```
FxPage (apps/web/src/components/markets/fx/FxPage.tsx)
├── MarketsNavigationTabs (Subviews across Markets module)
├── FxHeader (Global search trigger, links to /markets, /charts, /economics, refresh)
├── FxCoverageSummary (Catalog metrics: pairs, base/quote currencies, quotes, bid/ask, spread)
├── FxPairFilters (Search query, base currency selector, quote currency selector, reset)
├── FxPairDirectoryTable (High-density financial table with deterministic pagination)
│   └── FxPairDirectoryRow (Individual row with badges, bid, ask, mid, spread, and timestamps)
├── FxPairInspector (Side inspector with canonical UUID, orientation, rate details, currency cards)
├── FxCurrencyConverter (Conversion form with amount, currency selectors, swap button, result card)
└── FxEmptyState (Truthful zero-result and empty catalog states)
```

---

## 7. Strict Financial Design Integrity

Stage 59 complies strictly with ATLAS design principles:
- **No Purple Gradients**: Pure professional Bloomberg/OpenBB terminal palette (emerald, rose, zinc, slate).
- **No Emoji Icons**: Professional Lucide icons only.
- **No Fabricated Rates**: No hardcoded rates in production code, no fake trading volumes.
- **No Broker Controls**: No "Buy Currency", "Sell Currency", or "Trade Now" buttons.
- **Accessible & Responsive**: High-contrast tabular numbers, keyboard navigation, full screen-reader ARIA labeling, responsive layouts across desktop, tablet, and mobile.

---

## 8. Verification & Quality Gates Summary

| Suite / Gate | Tests Passed | Status |
|---|---|---|
| Backend FX Market Unit & API Tests (`test_markets_fx.py`) | 20 / 20 | PASS |
| Backend Markets Regression (`test_markets_*.py`) | 84 / 84 | PASS |
| Python Linting & Formatting (`ruff check` & `ruff format`) | Clean | PASS |
| Web FX Unit & Integrity Tests (`markets-fx.test.ts`) | 12 / 12 | PASS |
| Web Markets Regression (`markets-overview`, `equities`, `funds`, `fx`) | 47 / 47 | PASS |
| Frontend Linting (`eslint`) | 0 errors, 0 warnings | PASS |
| TypeScript Typecheck (`tsc --noEmit`) | 0 errors | PASS |

Stage 59 is complete. Proceed to Stage 60 (Cryptocurrency Markets).
