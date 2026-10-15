# ATLAS Bonds & Fixed-Income Markets V1 (Stage 61 Architecture)

## Executive Summary

Stage 61 implements **Bonds & Fixed-Income Markets V1: Global Bond Discovery, Sovereign and Corporate Debt Markets, Coupon Intelligence, Yield Observations, Clean/Dirty Pricing and Professional Fixed-Income Terminal** inside ATLAS Module 2 (`/markets`). It delivers an institutional-grade, source-aware fixed-income discovery, inspection, and observational analytics workspace for sovereign and corporate debt securities across verified debt issuers.

The canonical workspace route is:
```
/markets/bonds
```
integrated directly into the existing Markets application alongside Markets Overview (`/markets`), Equities (`/markets/equities`), ETFs & Funds (`/markets/funds`), Foreign Exchange (`/markets/fx`), and Cryptocurrency (`/markets/crypto`).

---

## 1. Architecture Flow

```
ATLAS MARKETS (Module 02)
       │
       ├── Overview (Stage 56)           [/markets]
       ├── Equities (Stage 57)           [/markets/equities]
       ├── ETFs & Funds (Stage 58)       [/markets/funds]
       ├── Foreign Exchange (Stage 59)   [/markets/fx]
       ├── Cryptocurrency (Stage 60)     [/markets/crypto]
       │
       └── Bonds (Stage 61)              [/markets/bonds]
               │
               ├── MarketsNavigationTabs (Overview, Equities, Funds, FX, Crypto, Bonds [Active], Futures [St 62])
               ├── BondsHeader (Search Ctrl+K, Overview, Charts, Research, Refresh)
               ├── BondCoverageSummary (Total Bonds, Issuers, With Prices, With Yields, Currencies)
               ├── BondDirectoryFilters (Search query, Issuer Type, Bond Type, Currency, Coupon Type, Maturity Bucket, Reset)
               ├── BondDirectoryTable (High-density tabular bond display with deterministic keyset pagination)
               │     └── BondDirectoryRow (Bond/ISIN, Issuer, Type, Ccy, Coupon, Maturity, Clean Price, Price Basis, Yield, Freshness, Source, Updated)
               └── BondInspector (Deep inspection: Canonical Security UUID, Legal Debt Issuer, Clean/Dirty Price breakdown, Accrued Interest, Typed Yields & bps changes, Contract Terms, Day Count, Face Value, Seniority, Cross-module navigation, Non-executable OTC disclaimer)
                       │
                       ▼
               Bonds REST API (FastAPI)
                       │
          ┌────────────┼────────────────────────┐
          ▼            ▼                        ▼
   BondDirectoryService  BondMarketReadService   BondOverviewService
          │            │                        │
     PostgreSQL   LiveQuoteService (Stage 41)   Canonical Bond Securities Catalog
                  ClickHouse History (Stage 39) Debt Issuer & ISIN Resolver
                  FreshnessClassifier (Stage 44) Decimal Financial Calculation Engine
```

---

## 2. Core Fixed-Income & Security Identity Architecture

### A. Bond Security vs Issuer Identity
Bond security identity is strictly decoupled from debt issuer identity:
- **Debt Issuer Entity**: Represents the sovereign government, finance ministry, corporation, or supranational organization issuing the obligation (e.g. US Department of the Treasury, UK Debt Management Office, Federal Republic of Germany, Apple Inc., JPMorgan Chase, World Bank IBRD). Identified by deterministic UUID5 under `BOND_ISSUER_NAMESPACE`.
- **Bond Security Entity**: Represents a specific debt tranche, issue, or note with contractual maturity, coupon schedule, and ISIN (e.g. US Treasury Note 4.250% May 2034, UK Gilt 4.125% Jan 2034, Apple Inc. 3.950% Aug 2052). Identified by deterministic UUID5 under `BOND_INSTRUMENT_NAMESPACE`.
- **Tranches Distinction**: Multiple bonds issued by the same issuer with the same or different maturities, currencies, and coupon schedules are modeled as distinct financial instruments. They are never merged or collapsed into a single equity-like symbol.

### B. Fixed-Income Identifiers & Scoped Resolution
- **ISIN (International Securities Identification Number)**: Primary global 12-character alphanumeric security identifier (ISO 6166), validated against check-digit structure.
- **CUSIP**: 9-character North American security identifier, preserved where available under licensing entitlements.
- **Deterministic Namespacing**: UUID5 generated deterministically from canonical ISIN / symbol strings ensures repeatable identity across environments without synthetic sequence counters.

### C. Debt Classifications
Supported canonical debt instrument classifications:
- **Sovereign**: Government debt obligations issued by sovereign treasuries or debt management offices (e.g. US Treasuries, UK Gilts, German Bunds, JGBs).
- **Corporate**: Senior and subordinated debt obligations issued by public and private corporations.
- **Treasury Bill (T-Bill)**: Short-term discount government debt without periodic coupon payments.
- **Supranational**: Debt obligations issued by multilateral institutions (e.g. European Investment Bank, World Bank IBRD).
- **Municipal & Agency**: Supported categories for state/local government and government-sponsored enterprise issues.

---

## 3. Financial Semantics, Pricing, and Yield Engine

### A. Clean Price vs. Dirty Price vs. Accrued Interest
Bond price quotation fundamentally differs from equity share prices:
- **Clean Price**: The market quotation of the bond excluding accrued interest. This is the standard trading quotation for conventional sovereign and corporate bonds.
- **Dirty Price**: The invoice or settlement price including accrued interest:
  $$\text{Dirty Price} = \text{Clean Price} + \text{Accrued Interest}$$
  ATLAS enforces strict mathematical consistency across the three values, requiring that all three be expressed on the same quotation basis and face-value scale.
- **Accrued Interest Safeguards**: Accrued interest is sourced directly from authoritative market observations or verified contractual schedules with explicit day-count conventions and settlement dates. ATLAS never fabricates accrued interest from simple calendar heuristics.

### B. Price Quotation Units
- `PERCENTAGE_OF_PAR`: Expressed as a percentage of nominal par value (e.g. `98.500% of par`).
- `PRICE_PER_100_FACE`: Expressed per 100 units of currency face value (e.g. `100.250 / 100 USD`).
- `ABSOLUTE_AMOUNT`: Expressed as an absolute currency amount per bond note.

### C. Price Kinds
- `TRADE_PRICE`: An executed transaction on an exchange or electronic fixed-income trading venue.
- `EVALUATED_PRICE`: An evaluated pricing service matrix or model evaluation (e.g. BVAL, ICE Data, IDC).
- `INDICATIVE_QUOTE`: An indicative dealer quote or benchmark run.
- `REFERENCE_PRICE`: An official central bank or treasury fixing.

### D. Yield Semantics vs. Contractual Coupon
- **Yield is NOT Coupon**: A coupon rate is a fixed contractual term of the security. A yield is a dynamic measure derived from price, cash-flow timing, and settlement conventions. ATLAS strictly separates coupon rates from yield metrics and never displays coupon rates in yield columns.
- **Typed Yield Observations**: Supported yield measures include:
  - `YTM` (Yield to Maturity)
  - `YTC` (Yield to Call)
  - `YTW` (Yield to Worst)
  - `DISCOUNT_YIELD` (Money-market discount yield for Treasury Bills)
  - `CURRENT_YIELD` (Annual coupon divided by clean price)
- **Negative Yield Support**: Negative yields (as historically observed on European and Japanese sovereign debt) are valid mathematical quantities. ATLAS never rejects or clamps negative yields.
- **Yield Movement in Basis Points (bps)**: Yield changes are expressed in basis points ($1\text{ bps} = 0.01\%$), calculated as:
  $$\Delta y_{\text{bps}} = (y_{\text{current}} - y_{\text{previous}}) \times 100$$
  where yields are stored as percentage points. Yield changes are never conflated with percentage price returns.

### E. Bid/Ask Spread & Crossed Market Protection
When bid and ask prices are supplied on the same security, provider, and price basis:
$$\text{Spread} = \text{Ask} - \text{Bid}$$
If an erroneous or fragmented dealer quote results in $\text{Bid} > \text{Ask}$, the observation is flagged as `CROSSED_INVALID`, and the spread is suppressed (`None`) to prevent negative spreads.

---

## 4. Contractual Terms & Maturity Schedule

- **Maturity Date**: Verified contractual redemption date. Matured debt is classified without speculative assumptions of default or restructuring.
- **Perpetual Bonds**: Hybrid capital and perpetual obligations (without fixed maturity) are explicitly displayed as `Perpetual`. No artificial maturity date is manufactured.
- **Time to Maturity**: Calendar approximation of remaining lifespan (e.g. `9.6 Y`, `6 mo`), clearly identified as calendar time rather than risk duration.
- **Coupon Types**:
  - `FIXED`: Fixed contractual annual coupon percentage.
  - `ZERO_COUPON`: Genuine zero-coupon instrument with 0.00% coupon (distinct from missing data).
  - `FLOATING`: Variable rate tied to a benchmark reference rate (e.g. SOFR, EURIBOR) plus margin.
  - `STEP_UP`, `INFLATION_LINKED`, `OTHER`: Supported specialized debt structures.
- **Day-Count Conventions**: Preserved contractual conventions including `ACT/ACT ICMA`, `ACT/360`, `30/360`, and `ACT/365`.
- **Seniority**: Senior Secured, Senior Unsecured, Subordinated, and Junior Subordinated claims are strictly classified.

---

## 5. REST API Reference

All endpoints are authenticated and require `ATLAS_ACCESS` permission. All read endpoints are strictly read-only:
- **0 Database Writes**: No modifications to PostgreSQL, Redis, or ClickHouse on GET requests.
- **0 External Provider Fanout**: Directory browsing does not trigger upstream API calls per row.
- **0 LLM or Agent Invocations**: No background AI jobs or token expenditures on market navigation.

### 1. `GET /api/v1/markets/bonds`
Retrieve paginated, filterable directory of canonical debt securities.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `query` | string | optional | Search query across ISIN, CUSIP, symbol, security name, and issuer |
| `issuer_type` | string | `all` | Filter by issuer category (`sovereign`, `corporate`, `supranational`, etc.) |
| `bond_type` | string | `all` | Filter by bond classification (`sovereign`, `corporate`, `treasury_bill`, etc.) |
| `currency` | string | `all` | Filter by denomination currency (`USD`, `EUR`, `GBP`, `JPY`, etc.) |
| `coupon_type` | string | `all` | Filter by coupon type (`fixed`, `zero_coupon`, `floating`, etc.) |
| `maturity_bucket` | string | `all` | Filter by maturity range (`under_1_year`, `1_to_3_years`, `3_to_5_years`, `5_to_10_years`, `over_10_years`, `perpetual`) |
| `limit` | integer | `25` | Results per page (max `100`) |
| `cursor` | string | optional | Deterministic keyset pagination cursor |

**Response DTO (`BondDirectoryResponse`):**
```json
{
  "schema_version": "1.0",
  "scope": "authorized_atlas_bond_catalog",
  "items": [
    {
      "instrument_entity_id": "908c6bfb-a9f8-580a-9bc5-408ba56ecbc8",
      "symbol": "UST-10Y",
      "name": "US Treasury Note 4.250% May 2034",
      "isin": "US91282CJZ72",
      "cusip": "91282CJZ7",
      "issuer": {
        "issuer_entity_id": "91901a8f-2875-52e6-a079-8d77ea4fe4bc",
        "name": "United States Department of the Treasury",
        "issuer_category": "sovereign",
        "country_code": "US",
        "jurisdiction": "United States"
      },
      "bond_type": "sovereign",
      "currency": "USD",
      "terms": {
        "issue_date": "2024-05-15",
        "dated_date": "2024-05-15",
        "maturity_date": "2034-05-15",
        "coupon_type": "fixed",
        "coupon_rate": "4.250",
        "coupon_frequency": "semiannual",
        "day_count_convention": "ACT/ACT ICMA",
        "face_value": "1000",
        "seniority": "senior_unsecured",
        "is_callable": false,
        "is_perpetual": false
      },
      "price": {
        "clean_price": "98.500",
        "dirty_price": "100.270",
        "accrued_interest": "1.770",
        "bid": "98.480",
        "ask": "98.520",
        "spread": "0.040",
        "price_basis": "clean",
        "quote_unit": "percentage_of_par",
        "price_kind": "evaluated_price",
        "price_change_24h": "-0.150",
        "price_change_pct_24h": "-0.152",
        "source_timestamp": "2026-10-15T12:00:00Z",
        "received_at": "2026-10-15T12:00:05Z",
        "freshness_status": "REALTIME",
        "delay_status": "REALTIME",
        "provider": "CANONICAL_BVAL"
      },
      "yield_obs": {
        "yield_value": "4.442",
        "yield_type": "ytm",
        "yield_unit": "pct_per_annum",
        "yield_change_bps_24h": "1.8",
        "as_of": "2026-10-15T12:00:00Z",
        "source": "CANONICAL_BVAL",
        "methodology": "ICMA Semi-Annual Compounding"
      },
      "freshness_status": "REALTIME",
      "provider": "CANONICAL_BVAL",
      "data_status": "AVAILABLE"
    }
  ],
  "total": 16,
  "limit": 25,
  "next_cursor": null,
  "has_more": false,
  "coverage": {
    "total_bonds": 16,
    "total_issuers": 11,
    "sovereign_bonds": 8,
    "corporate_bonds": 4,
    "other_bonds": 4,
    "bonds_with_prices": 16,
    "bonds_with_yields": 16,
    "bonds_with_accrued_interest": 16,
    "currencies": ["USD", "EUR", "GBP", "JPY"]
  }
}
```

### 2. `GET /api/v1/markets/bonds/filters`
Retrieve authoritative available filter dimensions and issuers.

### 3. `GET /api/v1/markets/bonds/{instrument_entity_id}`
Retrieve deep security overview, contractual terms, price observations, typed yields, provenance, and non-executable OTC disclaimer for a specific bond.

---

## 6. Frontend Workspace Architecture

### Components Hierarchy (`apps/web/src/components/markets/bonds/`)
1. **`BondsPage`**: Master workspace coordinating layout, selection state, and hooks.
2. **`MarketsNavigationTabs`**: Global market subviews navigation with Bonds active.
3. **`BondsHeader`**: Top bar with search trigger, module actions, and manual refresh.
4. **`BondCoverageSummary`**: High-level market metric cards (Bonds, Issuers, Pricing coverage, Yield coverage).
5. **`BondDirectoryFilters`**: Multi-dimensional search and dropdown filtering.
6. **`BondDirectoryTable`**: Financial table with dense tabular layout, sorting, and keyset pagination.
7. **`BondDirectoryRow`**: Single security row with tabular numerals, price basis tags, and freshness badges.
8. **`BondInspector`**: Right-side detail drawer presenting legal issuer, clean/dirty prices, accrued interest, typed yields, contract terms, and provenance.
9. **`BondEmptyState`**: Truthful empty and error states (`no_data`, `no_matches`, `error`).

---

## 7. Strict Financial Guardrails & Out-of-Scope Boundaries

In compliance with Stage 61 Master Implementation Directive:
1. **No Yield Curve Bootstrapping**: Zero-coupon curves, OIS curves, swap curves, and yield curve interpolation engines belong to later Quant/Economics stages.
2. **No Duration or Convexity Engines**: Macaulay duration, modified duration, DV01/PV01, and convexity belong to Stage 118 (Fixed-Income Risk).
3. **No Generalized YTM Solver**: Source-provided yields are displayed with explicit methodology. ATLAS does not invent arbitrary YTM solvers.
4. **No Advanced Bond Pricing / Option Valuation**: No callable/putable option engines, MBS prepayment models, or CDS pricing.
5. **No Credit Risk Modeling**: Default probabilities, rating migration matrices, and structural credit models belong to Risk stages.
6. **No Bond Trading Execution**: No RFQ, dealer order placement, or primary market subscription. All endpoints and UI are read-only.
7. **No Fabricated Data**: No invented prices, yields, coupons, credit ratings, or ISINs.
8. **No Purple Gradients or Emoji Icons**: Strict institutional Bloomberg/OpenBB terminal styling.

---

## 8. Verification & Test Summary

- **Backend Unit & Integration Tests**: 24 tests in `apps/api/tests/markets/test_markets_bonds.py` passing (126/126 across all market domains).
- **Frontend Unit & Integration Tests**: 11 tests in `apps/web/tests/markets-bonds.test.ts` passing (69/69 across all market web suites).
- **TypeScript Typecheck**: 0 errors on `tsc --noEmit`.
- **Ruff Code Quality**: 0 errors, all files formatted to strict 100-character line length.
- **ESLint Code Quality**: 0 errors, 0 warnings.
- **Next.js Production Build**: Production build succeeded with `/markets/bonds` pre-rendered statically.

---

## 9. Ready for Stage 62

The fixed-income market architecture is fully verified, operational, and ready for:
**Stage 62 — Build Futures & Commodities Markets V1**
- Canonical commodity and futures instrument identities
- Underlying asset and contract-month relationships
- Expiration dates, contract sizes, tick sizes, and tick values
- Physical vs. cash settlement classifications
- Professional Futures & Commodities discovery terminal.
