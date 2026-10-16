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

## 2. Standard Futures Month Codes

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

Canonical identities store the full, unambiguous `YYYY-MM` representation (e.g., `2026-12`) rather than relying on ambiguous single-digit year suffixes.

---

## 3. Financial Derivatives Semantics & Safeguards

### 3.1 Legitimate Negative Futures Prices
Unlike fiat equities and spot currencies, commodity futures contracts can trade at negative prices (e.g., WTI Crude Oil May 2020 contract `CLK20` settled at `-$37.63/bbl` on 2020-04-20 due to physical storage exhaustion at Cushing).
- Negative prices are fully accepted and not coerced to zero or absolute values.
- Absolute price movement ($current - reference$) remains mathematically sound.
- **Percentage Change Suppression**: When the reference price is nonpositive ($\le 0$), ordinary percentage return is suppressed (`None`) to prevent misleading or mathematically undefined figures.
- **Negative Bid/Ask Spread**: When both bid and ask are negative, $ask \ge bid$ still holds (e.g., bid `-$38.00`, ask `-$37.50`, spread = `+$0.50`).

### 3.2 Last Trade vs Official Settlement
- **Last Trade (`latest_trade_price`)**: The most recent transaction executed on the exchange matching engine during continuous trading.
- **Official Daily Settlement (`official_settlement`)**: The official reference price determined by the exchange clearing house based on volume-weighted average price (VWAP) in the closing window.
- Both observations are distinct and displayed separately. One is never silently substituted for the other.

### 3.3 Trading Volume vs Open Interest
- **Volume (`volume`)**: Total number of contracts bought and sold during the trading session.
- **Open Interest (`open_interest`)**: Total number of active, open contracts that have not been closed out or delivered. Reported by the clearing house on a delayed schedule (typically daily with an explicit as-of date).

### 3.4 Tick Size and Monetary Tick Value
Tick value measures the exact currency movement per contract for a minimum price fluctuation:
$$\text{Tick Value} = \text{Tick Size} \times \text{Contract Multiplier} \times \text{Scale Factor}$$
- NYMEX Crude Oil: $0.01 \times 1,000 \text{ barrels} = \$10.00\text{ USD}$
- COMEX Gold: $0.10 \times 100 \text{ troy oz} = \$10.00\text{ USD}$
- CBOT Corn: $0.25\text{ cents} \times 5,000 \text{ bushels} = \$12.50\text{ USD}$
- CME E-mini S&P 500: $0.25\text{ index points} \times \$50 = \$12.50\text{ USD}$

---

## 4. REST API Endpoints

All endpoints are mounted under `/api/v1/markets/futures` and require authentication (`ATLAS_ACCESS` permission):

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/markets/futures/contracts` | List & filter futures contracts with cursor pagination |
| `GET` | `/api/v1/markets/futures/contracts/{id}` | Comprehensive contract inspection view |
| `GET` | `/api/v1/markets/futures/commodities` | List canonical underlying commodities |
| `GET` | `/api/v1/markets/futures/commodities/{id}` | Single commodity overview with associated products |
| `GET` | `/api/v1/markets/futures/spot-benchmarks` | List physical commodity spot price benchmarks |
| `GET` | `/api/v1/markets/futures/filters` | Distinct filter options and catalog coverage counts |

---

## 5. User Interface Components

Located in `apps/web/src/components/markets/futures/`:
- **`FuturesHeader`**: Module title, breadcrumbs, search shortcut, and cross-navigation links.
- **`FuturesCoverageSummary`**: 8 dense institutional metric cards (Commodities, Products, Listed Contracts, Tradable Active, With Trade Price, With Settlement, With Volume, With Open Interest) and venue badges.
- **`FuturesMarketTabs`**: Segmented view tabs for *Futures Contracts*, *Commodities Catalog*, and *Spot Benchmarks*.
- **`FuturesContractFilters`**: Search bar and 6 filter dropdowns (Category, Exchange, Product Family, Month, Settlement Type, Status) with Reset.
- **`FuturesContractTable`**: High-density table featuring contract symbols, months, expirations, trade prices, settlements, changes, volume, open interest, and settlement badges.
- **`FuturesContractInspector`**: Slide-in terminal panel detailing Canonical Identity, Specifications, Expiration Schedule, Volume/OI, Provenance, and non-executable disclaimer.
- **`CommodityDirectoryTable`**: Underlying commodities catalog with physical units, delivery districts, and active contract counts.
- **`SpotBenchmarkDirectoryTable`**: Verified physical spot benchmarks table with assessment methodology notices.

---

## 6. Strict Scope Boundaries & Deferrals

Stage 62 is strictly **read-only** and derivatives-discovery focused:
- **No Continuous Futures Engine**: Individual contracts are never synthetically rolled or back-adjusted.
- **No Term-Structure Modeling**: No curve bootstrapping, calendar spread trading, or contango/backwardation calculations.
- **No Trading / Order Execution**: Buy, Sell, and margin controls are strictly prohibited.
- **No Margin Engine**: SPAN and maintenance margin calculation is deferred.
- **No Futures Options**: Options on futures are deferred to Stages 141-142.
- **Next Stage**: Stage 63 (Build Market Movers).
