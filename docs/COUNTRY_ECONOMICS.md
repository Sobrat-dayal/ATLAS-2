# ATLAS Country Economics Intelligence (Stage 90)

## Overview & Canonical Architecture

Stage 90 delivers institutional-grade Country Economics Intelligence within the ATLAS Macroeconomic Intelligence ecosystem (`/economics`), building directly on the canonical data foundations established in **Stage 89 (Economics V1)**.

While Stage 89 owns cross-economy indicator registries, source-series identities, historical observation records, revision vintages, and mathematical transformations, **Stage 90 owns deep sovereign country-level macroeconomic research**. It allows quantitative macroeconomists, sovereign risk analysts, and portfolio managers to dissect the national accounts, expenditure structures, supply-side Gross Value Added (GVA), inflation baskets, labor market dynamics, fiscal accounts, public debt, balance of payments, and demographic structures of individual sovereign nations and economic areas.

---

## Core Sovereign Coverage: Core G6 Economies

Stage 90 is seeded with verified, canonical sovereign datasets across the G6 core macroeconomic reporting jurisdictions:

| Country / Area | Geographic Entity ID | ISO Code | Scope Kind | Reporting Currency | Central Bank | Primary Statistical Authority | National Accounts Standard |
|---|---|---|---|---|---|---|---|
| **United States** | `geo-us` | `US` | `COUNTRY` | USD | Federal Reserve | Bureau of Economic Analysis (BEA) / BLS | SNA 2008 / NIPA (BEA) |
| **Euro Area** | `geo-ea` | `EA` | `ECONOMIC_AREA` | EUR | European Central Bank (ECB) | Eurostat | ESA 2010 (Eurostat) |
| **China** | `geo-cn` | `CN` | `COUNTRY` | CNY | People's Bank of China (PBOC) | National Bureau of Statistics (NBS) | CSNA 2016 (NBS) |
| **India** | `geo-in` | `IN` | `COUNTRY` | INR | Reserve Bank of India (RBI) | MoSPI (CSO) | 2011-12 Base NAS (MoSPI) |
| **Japan** | `geo-jp` | `JP` | `COUNTRY` | JPY | Bank of Japan (BOJ) | Economic and Social Research Institute (Cabinet Office) | 2015 Base JSNA (Cabinet Office) |
| **United Kingdom** | `geo-gb` | `GB` | `COUNTRY` | GBP | Bank of England (BOE) | Office for National Statistics (ONS) | ESA 2010 (ONS Blue Book) |

---

## Macroeconomic Principles & Strict Invariants

### 1. National Accounts & GDP Decomposition
- **Nominal vs. Real GDP:** Current-price GDP reflects contemporaneous price levels, whereas real chain-linked volume measures isolate genuine volume output.
- **Chain-Linked Non-Additivity:** In accordance with SNA 2008 / ESA 2010 standards, chain-linked volume components ($C, I, G, X-M$) are chain-weighted using Fisher or Laspeyres indices and are **strictly non-additive** outside the reference base year. ATLAS explicitly discloses non-additivity and does **not** force real components to sum to total real GDP.
- **Expenditure Approach:** Decomposes national output into:
  $$GDP = C + I + G + (X - M)$$
  where $C$ is Household Final Consumption, $I$ is Gross Capital Formation (Gross Fixed Capital Formation + Change in Inventories), $G$ is Government Final Consumption, and $(X - M)$ is Net Exports of Goods and Services.
- **Production Approach (Gross Value Added):**
  $$GDP_{market\ prices} = \sum GVA_{basic\ prices} + Taxes_{products} - Subsidies_{products}$$
  Sectors: Agriculture, Forestry & Fishing; Industry & Manufacturing; Construction; Commercial & Public Services.
- **GDP Per Capita:** Computed only when compatible annual GDP flows and official annual population estimates share the identical calendar/fiscal reference period.

### 2. Price Stability & Inflation
- **Headline vs. Core Inflation:** Headline CPI measures the entire consumer expenditure basket. Core CPI strips out volatile food and energy sub-indices to measure underlying price momentum.
- **Index Bases & Seasonal Adjustment:** Each country's price index level retains its official base year (e.g. US `1982-84=100`, Euro Area `2015=100`, Japan `2020=100`) and explicit seasonal adjustment metadata (`SEASONALLY_ADJUSTED` vs `NOT_ADJUSTED`).
- **Producer Prices & Deflators:** PPI reflects factory-gate wholesale output prices, and the GDP Deflator measures economy-wide domestic production price changes.

### 3. Labor Market Dynamics
- **Survey Methodologies:** Preserves official sovereign survey standards (e.g. US BLS Current Population Survey, UK ONS Labour Force Survey, China NBS Urban Labor Survey).
- **Labor Force Participation:** Measures the active labor force (employed + actively seeking work) divided by the eligible working-age population.
- **Wages:** Real wages are calculated strictly by deflating nominal wage growth by contemporaneous headline CPI.

### 4. Government Finances & Public Debt
- **Accounting Scope Invariant:** Never confuses `CENTRAL_GOVERNMENT` budgetary finances with `GENERAL_GOVERNMENT` consolidated finances (which include state, provincial, and local government bodies and social security funds).
- **Accounting Basis Invariant:** Accrual vs. cash execution basis is explicitly identified.
- **Stock vs. Flow Timing:** Public Debt is a balance sheet stock measured at period end; GDP is an annual flow. Debt-to-GDP ratios are strictly calculated against compatible annual GDP denominators.
- **Primary Balance:** Net fiscal balance excluding sovereign debt interest expenditures.

### 5. External Sector & Balance of Payments
- **Trade Balance vs. Current Account:** Merchandise trade balances reflect customs goods flows (FOB/CIF). The Current Account reflects total goods, commercial services, **net primary income** (foreign investment yields and compensation), and **secondary income** (transfers and remittances). They are never treated as equivalent.
- **Foreign Reserves:** Official sovereign foreign exchange and reserve asset stock in specified reserve currencies.

### 6. Demographics & Structural Statistics
- Population totals, growth rates, working-age cohorts (15–64), youth dependency, and urbanization are benchmarked to official census records. Zero synthetic monthly population interpolation is permitted.

---

## REST API Specification

All Country Economics endpoints are exposed under `/api/v1/economics/countries` and require authenticated principals (`PermissionCode.ATLAS_ACCESS`):

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/economics/countries` | List all supported sovereign country economic profiles. |
| `GET` | `/api/v1/economics/countries/{country_id}/overview` | Master macroeconomic overview (growth, inflation, labor, fiscal, external). |
| `GET` | `/api/v1/economics/countries/{country_id}/profile` | Canonical sovereign country metadata and standards. |
| `GET` | `/api/v1/economics/countries/{country_id}/gdp` | National accounts GDP expenditure decomposition. |
| `GET` | `/api/v1/economics/countries/{country_id}/gdp/production` | Gross Value Added (GVA) by sector (production approach). |
| `GET` | `/api/v1/economics/countries/{country_id}/inflation` | CPI price levels, headline & core inflation, components. |
| `GET` | `/api/v1/economics/countries/{country_id}/labor` | Employment surveys, participation, wages, youth unemployment. |
| `GET` | `/api/v1/economics/countries/{country_id}/industry` | Industrial production, retail sales volumes, housing starts, sentiment. |
| `GET` | `/api/v1/economics/countries/{country_id}/monetary` | Monetary aggregates (M1/M2), bank credit, and policy rate context. |
| `GET` | `/api/v1/economics/countries/{country_id}/fiscal` | Government budget execution, primary balances, gross/net debt. |
| `GET` | `/api/v1/economics/countries/{country_id}/external` | Goods & services trade, current account, FDI, FX reserves. |
| `GET` | `/api/v1/economics/countries/{country_id}/demographics` | Total population, age structure (15-64), dependency, urbanization. |
| `GET` | `/api/v1/economics/countries/{country_id}/coverage` | Indicator coverage matrix and statistical availability. |

---

## Canonical Roadmap Boundaries

- **Stage 89 (Preceding):** Economics V1 (Global Macroeconomic Intelligence, Canonical Indicators, Vintages).
- **Stage 90 (Current):** Country Economics Intelligence (Sovereign Profiles, GDP Decomposition, National Accounts).
- **Stage 91 (Upcoming):** Central Banks (Policy Decisions, Statements, Speeches, Balance Sheets, Timelines).
- **Stage 92 (Deferred):** Economic Calendar (Release Schedules, Consensus Forecasts, Surprise Metrics).
- **Stage 93 (Deferred):** Macro Comparisons (Cross-Country Benchmarking, Multi-Country Factor Models).
