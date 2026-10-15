# ATLAS Equities Markets V1 (Stage 57 Architecture)

## Executive Summary

Stage 57 establishes **Equities Markets V1** within ATLAS Module 2 (`/markets`). It delivers a high-density, professional equity security discovery, inspection, and observational analytics workspace grounded strictly in authoritative Financial Instrument records and real market quote data.

Equities Markets V1 is accessible via:
```
/markets/equities
```
while preserving the multi-asset Markets Overview at:
```
/markets
```

---

## Architecture Overview

```
ATLAS MARKETS (Module 02)
       │
       ├── Overview (Stage 56)           [/markets]
       │
       └── Equities (Stage 57)           [/markets/equities]
               │
               ├── MarketsNavigationTabs (Overview, Equities, Future placeholders)
               ├── EquitiesHeader (Search Ctrl+K, Charts, Companies, Research, Refresh)
               ├── EquityCoverageSummary (Canonical Equities, Exchanges, Countries, Quotes)
               ├── EquityDirectoryFilters (Country, Exchange, Subtype, Status, Reset)
               ├── EquityDirectoryTable (Tabular financial interface with pagination)
               └── EquityInspector (Selected entity details, verified issuer, quotes)
                       │
                       ▼
              Equities REST API (FastAPI)
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   EquityDirectoryService     EquityMarketReadService
          │                         │
     PostgreSQL                LiveQuoteService (Stage 41 Redis)
   - Financial Instruments     ReferenceCloseResolver (Stage 39 ClickHouse)
   - EquityListingMetadata     MarketDataFreshnessClassifier (Stage 44)
   - Relationship Graph (St 23)
```

---

## Core Identity Architecture

### 1. Distinction of Three Core Financial Concepts
Stage 57 strictly respects the boundaries between three fundamental concepts:
1. **Issuer Company** (Stage 18): The legal entity issuing shares (e.g. Apple Inc., Alphabet Inc., TSMC). Identified by canonical Company UUID.
2. **Equity Security** (Stage 17): The specific financial claim, share class, or receipt issued by the company (e.g. Alphabet Class A vs Class C; TSMC ADR). Identified by canonical Financial Instrument UUID.
3. **Exchange Listing**: The specific venue registration and trading representation of that security (e.g. NASDAQ: AAPL, NSE: RELIANCE). Identified by venue-scoped symbol, MIC, and trading currency.

Selecting an equity row selects its canonical **Financial Instrument UUID** (`instrument_entity_id`) into Stage 25 `useSelectedEntity()`. It **never** silently replaces it with the Company UUID. Transition to the Company module occurs exclusively when the user explicitly clicks "Open Company", which invokes `selectEntity(issuer_company.company_entity_id)` and navigates to `/companies`.

### 2. Share-Class Distinction
Different share classes (such as Alphabet Inc. Class A `GOOGL` with voting rights vs Class C `GOOG` without voting rights) are maintained as separate canonical Financial Instruments with their own distinct UUIDs, quote feeds, and venue representations. They are never merged.

### 3. Depositary Receipts & Preferred Equities
ADRs/GDRs (such as Taiwan Semiconductor Manufacturing Company ADR `TSM` traded on the NYSE in USD) are classified with `equity_subtype = "depositary_receipt"` and kept separate from ordinary foreign listings. Preferred shares are classified as `preferred_equity`. Non-equity instruments (Bonds, Futures, FX, Options, Crypto) are strictly excluded from equity directory discovery.

### 4. Exchange-Scoped Tickers & Validated MICs
Ticker symbols are not globally unique. Stage 57 uses exchange-scoped resolution with ISO 10383 Market Identifier Codes (MICs):
- `XNAS` (NASDAQ)
- `XNYS` (New York Stock Exchange)
- `XNSE` (National Stock Exchange of India)
- `XLON` (London Stock Exchange)
- `XTKS` (Tokyo Stock Exchange)

MICs and exchange labels are authoritative and never synthesized from ticker suffixes.

---

## Directory Discovery & Query Semantics

### Authoritative Directory Source
The primary source of truth is the canonical Financial Instrument repository, augmented by `equity_listing_metadata` and the Stage 23 Relationship Graph.

### Supported Parameters:
- `query` (optional string): Bounded substring search across canonical security name, exchange-scoped symbol, and venue.
- `market_country` (optional string): Listing market jurisdiction filter (e.g., `United States`, `India`, `United Kingdom`, `Japan`).
- `exchange` (optional string): Validated venue MIC (e.g., `XNAS`, `XNSE`, `XLON`).
- `equity_type` (optional string): Subtype filter (`common_equity`, `preferred_equity`, `depositary_receipt`).
- `listing_status` (optional string): Canonical status (`active`, `inactive`, `suspended`, `delisted`).
- `limit` (integer): Page size (default: 25, maximum: 100).
- `cursor` (string): Stable offset-based or keyset cursor for deterministic pagination.

### Filter Reset Policy
"Reset Filters" restores all parameters to default (`query=""`, `market_country="all"`, `exchange="all"`, `equity_type="all"`, `listing_status="all"`), resets the pagination cursor, but preserves the currently selected entity in the Inspector.

---

## Market Data & Financial Math Integrity

### 1. Latest Quote Retrieval
Quotes are retrieved in batch from Stage 41 `LiveQuoteService` backed by Valkey/Redis. If a Quote is missing, it is truthfully marked `data_status = "no_quote"` with `last_price = null`. It is **never** faked as `0.00`.

### 2. Qualified Reference Close & Price Change
- Price changes are calculated strictly against qualified completed session reference closes resolved via Stage 39/52 `ReferenceCloseResolver`:
  $$\text{absolute\_change} = \text{last\_price} - \text{reference\_close}$$
  $$\text{percentage\_change} = \left(\frac{\text{last\_price} - \text{reference\_close}}{\text{reference\_close}}\right) \times 100$$
- If the reference close is missing or zero, the valid latest price is displayed while `absolute_change = null` and `percentage_change = null`. Division-by-zero is mathematically guarded.

### 3. High-Precision Decimals
All financial values are calculated in Python using `Decimal` and serialized as JSON decimal strings to preserve mathematical fidelity and prevent IEEE 754 binary floating-point distortions.

### 4. Quote Freshness Classification (Stage 44)
- Fresh: Observed within active threshold.
- Stale: Cache or observation age exceeds threshold.
- Delayed: Feed provides delayed quotes (e.g. 15-minute delay).
- No Quote / Unavailable: Not yet received or unconfigured.

---

## API Endpoints

All endpoints require Stage 13 authentication and enforce Stage 14 `atlas.access` authorization:

### 1. `GET /api/v1/markets/equities`
Returns a paginated, filterable directory of canonical equity instruments enriched with latest quote observations and coverage metrics.
Headers returned: `Cache-Control: private, no-store`.

### 2. `GET /api/v1/markets/equities/filters`
Returns authoritative available filter options (countries, exchanges, subtypes, listing statuses) extracted dynamically from canonical catalog coverage.

### 3. `GET /api/v1/markets/equities/{instrument_entity_id}`
Returns a detailed inspector read model for a single equity security, including canonical identifiers, verified issuer company relationship, venue metadata, latest quote, and data limitation disclosures.

---

## Realtime Integration

Equities reuses the Stage 43 WebSocket infrastructure:
- Listens to Stage 42 canonical accepted quote event: `atlas:market.quote.updated`.
- When an update event occurs, coalesces refetch requests (maximum 1 refetch per 2 seconds).
- Protects against snapshot races via `lastAcceptedGeneratedAtRef`, ensuring older HTTP responses or stale packets never overwrite newer state.
- Automatically refetches on window focus and network reconnect.
- Subscriptions clean up on unmount or filter navigation.
- No separate WebSocket transport or unverified client streams are created.

---

## Strict Scope Boundaries

In accordance with the 150-stage ATLAS development roadmap:
- **No ETF/Fund workspaces** (Deferred to Stage 58).
- **No FX, Crypto, Bonds, or Futures workspaces** (Deferred to Stages 59–62).
- **No Market Movers** (Deferred to Stage 63).
- **No Heatmaps** (Deferred to Stage 64).
- **No Candlestick Chart Workspace or Indicators** (Deferred to Stages 66+).
- **No Watchlists** (Deferred to Stage 76).
- **No Price Alerts** (Deferred to Stage 80).
- **No Company Financial Statements or Ownership** (Deferred to Stages 81–88).
- **No Fundamental or Technical Screeners** (Deferred to Stages 94–98).
- **No Buy/Sell Trading Execution, Broker Connects, or Order Books** (Stage 57 is strictly read-only analytical discovery).
- **Zero fabricated stocks, volume, market cap, or prices**.
