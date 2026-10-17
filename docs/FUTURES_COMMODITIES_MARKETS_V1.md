# ATLAS Stage 62 — Futures & Commodities Markets V1

## Executive Summary

Stage 62 extends the canonical **ATLAS Markets** module (Module 02) with a dedicated derivatives terminal experience at `/markets/futures`. It implements canonical economic commodity identities, standardized futures product families, multi-month listed futures contracts, contract specifications, official exchange settlement observations, volume and open interest tracking, and physical spot commodity benchmarks.

---

## 1. Core Domain Model: Four Distinct Instrument Concepts

A fundamental principle of derivatives market architecture is that physical spot benchmarks, underlying commodities, futures contract families, and specific delivery contracts are distinct financial instruments:

```
+-------------------------------------------------------------+
|                     Commodity Underlying                    |
|       (e.g., WTI Light Sweet Crude Oil, API 37°-42°)       |
+------------------------------+------------------------------+
                               |
        +----------------------+----------------------+
        |                                             |
        v                                             v
+-----------------------+                 +-----------------------+
|  Spot Benchmark       |                 |  Futures Product      |
|  (e.g., WTI Spot FOB  |                 |  (e.g., NYMEX CL,     |
|   Cushing assessment) |                 |   1,000 bbl, phys)    |
+-----------------------+                 +-----------+-----------+
                                                      |
                          +---------------------------+---------------------------+
                          |                           |                           |
                          v                           v                           v
              +-----------------------+   +-----------------------+   +-----------------------+
              | Individual Contract   |   | Individual Contract   |   | Expired Contract      |
              | CL Dec 2026 (CLZ26)   |   | CL Jan 2027 (CLF27)   |   | CL May 2020 (CLK20)   |
              | Expiry: 2026-11-20    |   | Expiry: 2026-12-21    |   | Settle: -$37.63       |
              +-----------------------+   +-----------------------+   +-----------------------+
```

1. **Commodity Underlying (`CommodityUnderlyingConfig`)**:
   Represents the physical or economic reference asset (e.g., WTI Crude Oil, Brent Crude, Henry Hub Gas, Gold, Silver, Copper, Corn, Soybeans, Wheat, Live Cattle, S&P 500 Index). Key attributes: `commodity_entity_id` (deterministic UUID5), `category`, `physical_unit`, `reference_region`, and `grade_specification`.
2. **Commodity Spot Benchmark (`CommoditySpotBenchmarkConfig`)**:
   Represents verified physical cash-market price assessments (e.g., WTI Spot FOB Cushing, Brent Dated Spot, LBMA Gold Price PM). Benchmarks represent physical transactions or index assessments, never synthesized from futures contracts.
3. **Futures Product (`FuturesProductConfig`)**:
   Represents the standardized exchange contract family (e.g., NYMEX `CL`, ICE `BZ`, COMEX `GC`, CBOT `ZC`, CME `ES`). Defines standard contract size, quotation unit, currency, tick size, verified tick value, and settlement mechanism.
4. **Individual Listed Contract (`CanonicalFuturesContractConfig`)**:
   Represents an instrument tied to a specific delivery/expiration period (e.g. `CLZ26`, `CLF27`, `GCZ26`). Preserves explicit contract month (`YYYY-MM`), expiration date, last trading day, notice days, delivery dates, and final settlement date.

---

## 2. Canonical Identifiers, Symbol Scoping, and Alias Resolution

Futures contracts are not globally identified by ticker strings alone, because root symbols can collide across venues.
- **Deterministic UUID5 Namespaces**:
  - `COMMODITY_NAMESPACE`: `33333333-3333-5333-a333-000000000001`
  - `FUTURES_PRODUCT_NAMESPACE`: `33333333-3333-5333-a333-000000000002`
  - `FUTURES_CONTRACT_NAMESPACE`: `33333333-3333-5333-a333-000000000003`
  - `SPOT_BENCHMARK_NAMESPACE`: `33333333-3333-5333-a333-000000000004`
- **Venue Scoping**: Identifiers incorporate exchange MIC codes (`XNYM`, `IFEU`, `XCEC`, `XCBT`, `XCME`) to guarantee global uniqueness.
- **Alias Resolution**: Contract symbols (e.g., `CLZ26`, `CL 12/26`, `CL:NYMEX:2026-12`) resolve deterministically to canonical financial instrument UUIDs without guess work.

---

## 3. Standard Futures Month Codes and Contract Month Semantics

Standard exchange month codes map to calendar months:

| Month Code | Calendar Month | Name |
| :---: | :---: | :---: |
| **F** | 01 | January |
| **G** | 02 | February |
| **H** | 03 | March |
| **J** | 04 | April |
| **K** | 05 | May |
| **M** | 06 | June |
| **N** | 07 | July |
| **Q** | 08 | August |
| **U** | 09 | September |
| **V** | 10 | October |
| **X** | 11 | November |
| **Z** | 12 | December |

Canonical identities store the full, unambiguous `YYYY-MM` representation (e.g., `2026-12`) rather than relying on ambiguous single-digit year suffixes. A single-digit year (such as `6` in `CLZ6`) is never guessed as 2026 vs 2016 without verified metadata.

---

## 4. Contract Expiration & Lifecycle Schedule

Derivatives trading depends on precise lifecycle milestones:
- **Contract Month (`contract_month`)**: Designates the nominal delivery/settlement month (`YYYY-MM`).
- **Expiration Date (`expiration_date`)**: Date on which the contract ceases to exist and final obligations crystallize.
- **Last Trading Day (`last_trading_date`)**: The final trading day permitted by the exchange (often several business days prior to the expiration or delivery month).
- **First Notice Day (`first_notice_date`)**: First day on which a clearing firm or seller may tender notice of intention to deliver.
- **Last Notice Day (`last_notice_date`)**: Final day for delivery notice submission.
- **Delivery Start/End (`delivery_start_date` / `delivery_end_date`)**: Period during which physical transfer of underlying commodity occurs.
- **Final Settlement Date (`settlement_date`)**: Date on which final cash variation or delivery invoices are settled.
- **Lifecycle Status**:
  - `ACTIVE`: Currently listed and eligible for secondary market trading.
  - `EXPIRED`: Has reached maturity; trading terminated, but historical data and settlement preserved.
  - `DELISTED` / `SUSPENDED` / `UNKNOWN`: Verified exchange administrative states.

---

## 5. Contract Specifications, Units, and Monetary Tick Math

Contract terms dictate position sizing, margin requirements, and valuation:
- **Contract Size (`contract_size`)**: The standardized underlying quantity represented by one contract (e.g. 1,000 barrels, 100 troy ounces, 5,000 bushels, $50 \times$ index).
- **Physical Unit (`size_unit`)**: Explicit unit (barrels, troy ounces, bushels, pounds, metric tons, MMBtu, index points).
- **Price Quotation Unit (`quote_unit`)**: Currency and scale per physical unit (e.g. `USD per barrel`, `US cents per bushel`, `USD per troy oz`).
- **Tick Size (`tick_size`)**: Minimum permissible price movement allowed by the exchange matching engine.
- **Monetary Tick Value (`tick_value`)**: Dollar value of one tick movement for one contract:
  $$\text{Tick Value} = \text{Tick Size} \times \text{Contract Multiplier} \times \text{Scale Factor}$$
  - NYMEX Crude Oil: $0.01 \times 1,000 \text{ barrels} = \$10.00\text{ USD}$
  - COMEX Gold: $0.10 \times 100 \text{ troy oz} = \$10.00\text{ USD}$
  - CBOT Corn: $0.25\text{ cents} \times 5,000 \text{ bushels} = \$12.50\text{ USD}$
  - CME E-mini S&P 500: $0.25\text{ index points} \times \$50 = \$12.50\text{ USD}$
- **Settlement Type**:
  - `PHYSICAL`: Requires physical delivery at designated transfer hubs (e.g., Cushing, OK for WTI).
  - `CASH`: Financial variation settlement against a reference index (e.g., ICE Brent Index, SOFR).

---

## 6. Financial Derivatives Price Semantics & Safeguards

### 6.1 Legitimate Negative Futures Prices
Unlike fiat equities and spot currencies, commodity futures contracts can trade at negative prices (e.g., WTI Crude Oil May 2020 contract `CLK20` settled at `-$37.63/bbl` on 2020-04-20 due to physical storage exhaustion at Cushing).
- Negative prices are fully accepted and not coerced to zero or absolute values.
- Absolute price movement ($current - reference$) remains mathematically sound.
- **Percentage Change Suppression**: When the reference price is nonpositive ($\le 0$), ordinary percentage return is suppressed (`None`) to prevent misleading or mathematically undefined figures.
- **Negative Bid/Ask Spread**: When both bid and ask are negative, $ask \ge bid$ still holds (e.g., bid `-$38.00`, ask `-$37.50`, spread = `+$0.50`).

### 6.2 Last Trade vs Official Settlement
- **Last Trade (`latest_trade_price`)**: The most recent transaction executed on the exchange matching engine during continuous trading.
- **Official Daily Settlement (`official_settlement`)**: The official reference price determined by the exchange clearing house based on volume-weighted average price (VWAP) in the closing window.
- Both observations are distinct and displayed separately. One is never silently substituted for the other.

### 6.3 Trading Volume vs Open Interest
- **Volume (`volume`)**: Total number of contracts bought and sold during the trading session.
- **Open Interest (`open_interest`)**: Total number of active, open contracts that have not been closed out or delivered. Reported by the clearing house on a delayed schedule (typically daily with an explicit as-of date).

---

## 7. Price Change & Reference Data Semantics

- **Qualified Reference Price**: Evaluated strictly against the prior official settlement of the **same individual contract expiration**. Never compared cross-expiration (e.g., comparing Dec 2026 to Jan 2027 is strictly prohibited).
- **Absolute Change**:
  $$\Delta_{\text{abs}} = P_{\text{current}} - P_{\text{reference}}$$
- **Ticks Change**:
  $$\Delta_{\text{ticks}} = \frac{\Delta_{\text{abs}}}{\text{Tick Size}}$$
- **Percentage Change**:
  $$\Delta_{\%} = \frac{\Delta_{\text{abs}}}{P_{\text{reference}}} \times 100 \quad \text{if } P_{\text{reference}} > 0 \text{ else None}$$

---

## 8. Physical Spot Commodity Benchmarks

ATLAS supports verified cash-market commodity assessments:
- **Grade & Location**: Clearly qualified (e.g. WTI Spot FOB Cushing, Brent Dated Spot FOB Sullom Voe, LBMA Gold PM).
- **Assessment Methodology**: Sourced from official benchmarks (e.g., S&P Global Platts, LBMA, EIA, USDA).
- **Spot / Futures Separation**: Spot benchmarks are never synthesized from near-term futures contracts, and futures are never labeled as spot prices.

---

## 9. Provider Coverage & Exchange Scope

- **Exchanges**:
  - NYMEX (New York Mercantile Exchange, MIC: `XNYM`)
  - COMEX (Commodity Exchange Inc., MIC: `XCEC`)
  - CBOT (Chicago Board of Trade, MIC: `XCBT`)
  - CME (Chicago Mercantile Exchange, MIC: `XCME`)
  - ICE (Intercontinental Exchange Europe, MIC: `IFEU`)
- **Data Providers**: OpenBB, institutional exchange feeds, direct clearing notices.

---

## 10. REST API Architecture & Entitlements

All endpoints are mounted under `/api/v1/markets/futures` and require authentication (`ATLAS_ACCESS` permission):

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/markets/futures/contracts` | List & filter futures contracts with keyset cursor pagination |
| `GET` | `/api/v1/markets/futures/contracts/{id}` | Comprehensive contract inspection view |
| `GET` | `/api/v1/markets/futures/commodities` | List canonical underlying commodities |
| `GET` | `/api/v1/markets/futures/commodities/{id}` | Single commodity overview with associated products |
| `GET` | `/api/v1/markets/futures/spot-benchmarks` | List physical commodity spot price benchmarks |
| `GET` | `/api/v1/markets/futures/filters` | Distinct filter options and catalog coverage counts |

### Read-Only Invariant
All read endpoints guarantee:
- 0 PostgreSQL writes
- 0 ClickHouse writes
- 0 Redis writes
- 0 Upstream provider requests triggered on page view
- 0 Ingestion jobs created

---

## 11. Realtime Integration & Quote Events

- **Stage 43 Global WebSocket Reuse**: Listens for standard `market.quote.updated` events.
- **Contract Matching**: Matches incoming quote events strictly by canonical Financial Instrument UUID.
- **Month Isolation**: Quotes for adjacent contract months never overwrite the displayed contract.
- **Observation Independence**: Realtime trade quotes update Last Trade only; they never overwrite official settlement, volume, or open interest.

---

## 12. User Interface Components & Terminal Design

Located in `apps/web/src/components/markets/futures/`:
- **`FuturesHeader`**: Module title, breadcrumbs, search shortcut, and cross-navigation links.
- **`FuturesCoverageSummary`**: 8 dense institutional metric cards (Commodities, Products, Listed Contracts, Tradable Active, With Trade Price, With Settlement, With Volume, With Open Interest) and venue badges.
- **`FuturesMarketTabs`**: Segmented view tabs for *Futures Contracts*, *Commodities Catalog*, and *Spot Benchmarks*.
- **`FuturesContractFilters`**: Search bar and 6 filter dropdowns (Category, Exchange, Product Family, Month, Settlement Type, Status) with Reset.
- **`FuturesContractTable`**: High-density table featuring contract symbols, months, expirations, trade prices, settlements, changes, volume, open interest, and settlement badges.
- **`FuturesContractInspector`**: Slide-in terminal panel detailing Canonical Identity, Specifications, Expiration Schedule, Volume/OI, Provenance, and non-executable disclaimer.
- **`CommodityDirectoryTable`**: Underlying commodities catalog with physical units, delivery districts, and active contract counts.
- **`SpotBenchmarkDirectoryTable`**: Verified physical spot benchmarks table with assessment methodology notices.
- **`FuturesEmptyState`**: Institutional empty, loading, and error states with truthful recovery actions.

---

## 13. Strict No-Fake-Data Policy

In adherence to ATLAS financial-integrity principles:
- **No Fictional Contracts**: Only canonical, cataloged futures products and contracts are listed.
- **No Fabricated Prices**: Missing prices display as `—`, never simulated or filled with zeros.
- **No Synthetic Continuous Series**: Contracts are never auto-rolled or stitched together without explicit user methodologies.
- **No Invented Open Interest**: Clearing figures preserve exact as-of publication dates.

---

## 14. Strict Scope Boundaries & Deferrals

Stage 62 is strictly **read-only** and derivatives-discovery focused:
- **No Continuous Futures Engine**: Individual contracts are never synthetically rolled or back-adjusted.
- **No Term-Structure Modeling**: No curve bootstrapping, calendar spread trading, or contango/backwardation calculations.
- **No Trading / Order Execution**: Buy, Sell, and margin controls are strictly prohibited.
- **No Margin Engine**: SPAN and maintenance margin calculation is deferred.
- **No Futures Options**: Options on futures are deferred to Stages 141-142.
- **Next Stage**: Stage 63 (Build Market Movers).

---

## 15. Verification & Test Summary

- **Backend Unit & Integration Tests**: 27 tests in `apps/api/tests/markets/test_markets_futures.py` passing (153/153 across all market domains).
- **Frontend Unit & Integration Tests**: 11 tests in `apps/web/tests/markets-futures.test.ts` passing (80/80 across all market web suites).
- **TypeScript Typecheck**: 0 errors on `tsc --noEmit`.
- **Ruff Code Quality**: 0 errors in futures modules, all files adhering to strict 100-character line length.
- **ESLint Code Quality**: 0 errors, 0 warnings across futures components, hooks, and tests.
- **Next.js Production Build**: Production build succeeded with `/markets/futures` pre-rendered statically.
