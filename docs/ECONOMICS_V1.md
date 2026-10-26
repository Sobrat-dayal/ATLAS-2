# ATLAS Economics V1 — Institutional-Grade Global Macroeconomic Intelligence

**Source-of-Truth Architectural Specification for Stage 89**

---

## 1. Executive Summary & Vision

Stage 89 introduces **ATLAS Economics V1**, establishing the authoritative foundation for macroeconomic intelligence in the ATLAS financial terminal.

Economics V1 is hosted at:
```
/economics
```
Preserving all 20 global modules, the persistent AppShell, global Sidebar, Top Bar, Agent Dock, and Bottom Taskbar.

### Foundational Principles
1. **Statistical Qualification**: An economic statistic is meaningful only in the context of its precise canonical indicator definition, sovereign jurisdiction, measurement unit, reference period, seasonal-adjustment policy, calculation methodology, publishing agency, and publication vintage.
2. **Strict Anti-Fabrication Rule**: Under no circumstances does ATLAS fabricate economic observations, synthesize unweighted "World GDP" averages from arbitrary countries, invent inflation rates, or substitute market prices/quotes for sovereign macroeconomic statistics.
3. **Temporal Integrity**: An observation reference period (e.g., `2024-Q3`) is strictly distinguished from its source publication timestamp (`2024-10-30T12:30:00Z`) and internal ingestion timestamp. Point-in-time querying prevents look-ahead information leakage.
4. **Unit-Safe Transformations**: Price levels (Index Points) are distinct from percentage growth rates (%). Policy rate movements are measured in `PERCENTAGE_POINTS` (%p) or `BASIS_POINTS` (bps), never misleading relative percentages. Compound annualized quarterly growth is calculated strictly on positive constant-price GDP levels:
   $$\text{Growth}_{\text{QoQ, Ann.}} = \left[ \left(\frac{y_t}{y_{t-1}}\right)^4 - 1 \right] \times 100$$
5. **Deterministic Operation**: 0 LLM calls, 0 autonomous trading actions, 0 portfolio mutations, and 0 database writes during ordinary reads.

---

## 2. Canonical Economic Indicator & Series Model

```
Canonical Indicator (EconomicIndicator)
   ├── indicator_id (e.g. ind-real-gdp-growth)
   ├── canonical_code (e.g. GDP_GROWTH_QOQ_ANN)
   ├── display_name ("Real GDP Growth (QoQ Annualized)")
   ├── category (NATIONAL_ACCOUNTS)
   ├── default_unit (PERCENT)
   └── expected_frequency (QUARTERLY)
            │
            ▼ (1:N Mapped to Sovereign Jurisdictions)
Source Series (EconomicSeries)
   ├── series_id (e.g. ser-us-gdp-growth)
   ├── canonical_indicator_id (ind-real-gdp-growth)
   ├── geography_id (geo-us)
   ├── source_provider_id ("BEA")
   ├── source_series_code ("A191RL1Q225SBEA")
   ├── unit (PERCENT)
   ├── frequency (QUARTERLY)
   ├── seasonal_adjustment (SEASONALLY_ADJUSTED)
   └── price_basis (CONSTANT_PRICES)
            │
            ▼ (1:N Historical Observations)
Observation (EconomicObservationRecord)
   ├── reference_period ("2024-Q3")
   ├── exact_value (Decimal("2.8"))
   ├── unit (PERCENT)
   ├── status (PRELIMINARY | REVISED | FINAL)
   ├── published_at ("2024-10-30T12:30:00Z")
   └── source_revision ("Advance Estimate")
```

### Supported Indicator Categories
- `NATIONAL_ACCOUNTS`: Real GDP, Nominal GDP, Quarterly Growth, Gross Fixed Capital Formation.
- `INFLATION`: Consumer Price Index (CPI), Core CPI, Harmonized Index of Consumer Prices (HICP), PPI.
- `LABOR_MARKET`: Unemployment Rate, Labor Force Participation, Nonfarm Payrolls.
- `INTEREST_RATES`: Central Bank Policy Target Rates, Target Upper/Lower Bounds, Overnight Benchmark Rates.
- `MONETARY`: M1, M2, Central Bank Balance Sheet Totals.
- `INDUSTRIAL_ACTIVITY`: Industrial Production Index, Manufacturing Output.
- `CONSUMPTION`: Retail Sales Volumes and Values.
- `FISCAL`: General Government Debt to GDP, Fiscal Balance / Deficit.
- `EXTERNAL_SECTOR`: Trade Balance (Goods & Services), Current Account Balance.
- `HOUSING`: Case-Shiller Index, Housing Starts, Building Permits.
- `BUSINESS_SURVEYS`: Verified licensed survey metrics where authorized.

---

## 3. Geographic Scope & Sovereign Coverage Matrix

Stage 89 verifies operational coverage across the **G6 major economies and monetary areas**:

| ISO Code | Country / Economic Area | Sovereign Statistical Agency | Central Bank | Operational Indicators |
|---|---|---|---|---|
| **US** | United States | Bureau of Economic Analysis (BEA) / Bureau of Labor Statistics (BLS) | Federal Reserve | Real GDP, CPI YoY, CPI Index, Unemployment, Fed Funds Target |
| **EA** | Euro Area | Eurostat | European Central Bank (ECB) | Real GDP QoQ, HICP Inflation YoY, Unemployment, Deposit Facility Rate |
| **CN** | China | National Bureau of Statistics (NBS) | People's Bank of China (PBOC) | Real GDP YoY, CPI YoY, Surveyed Urban Unemployment, 1Y LPR |
| **IN** | India | Ministry of Statistics and Programme Implementation (MoSPI) | Reserve Bank of India (RBI) | Real GDP YoY, CPI YoY, Policy Repo Rate |
| **JP** | Japan | Cabinet Office / Statistics Bureau of Japan | Bank of Japan (BOJ) | Real GDP QoQ, CPI YoY, Unemployment, Uncollateralized Overnight Call Rate |
| **GB** | United Kingdom | Office for National Statistics (ONS) | Bank of England (BOE) | Real GDP QoQ, CPI YoY, Unemployment (LFS), Official Bank Rate |

*Crucial Boundary*: Euro Area (`EA`) is an economic and currency union, distinct from individual member nation sovereigns. National central banks execute ECB Governing Council policy, but sovereign fiscal indicators remain national.

---

## 4. Measurement Units & Mathematical Precision

The system enforces typed `StatisticalUnit` values:

| Statistical Unit | Representation | Domain Example | Misinterpretation Prevention |
|---|---|---|---|
| `PERCENT` | `%` | Real GDP Growth (+2.8%), Inflation (+2.4%) | Cannot be confused with Index Points or Currency |
| `PERCENTAGE_POINTS` | `%p` | Unemployment change (-0.1 %p) | Change from 5.0% to 6.0% is +1.0 %p, NOT +1.0% |
| `BASIS_POINTS` | `bps` | FOMC Rate cut (-50 bps) | $(\text{Rate}_t - \text{Rate}_{t-1}) \times 100$ |
| `INDEX_POINTS` | `Pts` | US CPI Level (314.796) | An index level of 314.796 is NEVER a 314.8% inflation rate |
| `CURRENCY_USD_BILLIONS` | `$B` | Nominal US GDP ($29,350.4B) | Preserves scale; not confused with millions or local currency |
| `LOCAL_CURRENCY_BILLIONS` | `LC $B` | Japan GDP (¥600,000B) | Distinct from USD-converted market FX rate values |

All statistical math uses Python `Decimal` objects with exact round-half-up precision to eliminate floating-point representation drift.

---

## 5. Versioned Mathematical Transformation Registry

Transformations are strictly versioned (`version = 1.0.0`) and enforce frequency, period adjacency, and denominator sanity:

1. **`SOURCE_REPORTED`**: Raw observation pass-through without mutation.
2. **`ABSOLUTE_CHANGE`**: $y_t - y_{t-1}$.
3. **`PERCENT_CHANGE`**: $\left(\frac{y_t - y_{t-1}}{|y_{t-1}|}\right) \times 100$ (Guarded against zero denominators).
4. **`YEAR_OVER_YEAR` (YoY)**:
   - For Monthly series ($k=12$): $\left(\frac{y_t}{y_{t-12}} - 1\right) \times 100$
   - For Quarterly series ($k=4$): $\left(\frac{y_t}{y_{t-4}} - 1\right) \times 100$
   - Validates that $t$ and $t-k$ represent matching months or quarters across exactly 1 year.
5. **`MONTH_OVER_MONTH` (MoM)**: Consecutive monthly percentage change ($k=1$).
6. **`QUARTER_OVER_QUARTER` (QoQ)**: Consecutive quarterly percentage change ($k=1$).
7. **`ANNUALIZED_QUARTERLY_GROWTH`**:
   $$\left[ \left(\frac{y_t}{y_{t-1}}\right)^4 - 1 \right] \times 100$$
   Requires positive constant-price quarterly levels.
8. **`PERCENTAGE_POINT_CHANGE`**: $y_t - y_{t-1}$ for series with unit `PERCENT`. Output unit: `PERCENTAGE_POINTS`.
9. **`BASIS_POINT_CHANGE`**: $(y_t - y_{t-1}) \times 100$ for series with unit `PERCENT`. Output unit: `BASIS_POINTS`.

---

## 6. Revision Tracking & Publication Semantics

Official agencies routinely release successive estimates of economic activity as more survey data arrives:

### BEA GDP Vintages for 2024-Q3
1. **Advance Estimate**: Released 2024-10-30 (+2.8% QoQ annualized) &mdash; Status: `PRELIMINARY`
2. **Second Estimate**: Released 2024-11-27 (+2.8% QoQ annualized) &mdash; Status: `REVISED`
3. **Third Estimate**: Released 2024-12-19 (+3.1% QoQ annualized) &mdash; Status: `FINAL`

### Point-in-Time Query Execution
When a client requests observations with `as_of_date = 2024-11-01`:
- The service filters out all observations and revisions published after `2024-11-01T23:59:59Z`.
- The user observes the `Advance Estimate` (+2.8%), exactly as it was known to market participants on November 1st, 2024.
- Third Estimate (+3.1%) is excluded, preventing model backtest and analytical look-ahead leakage.

---

## 7. Global Macroeconomic Snapshot Semantics

The `/api/v1/economics/overview` endpoint provides a high-density matrix of major economies.

### Why No "World GDP" Average Exists
Constructing an ad-hoc "World GDP Growth" figure by averaging 6 national growth rates is statistically invalid because:
- National accounts use different base years and weightings.
- GDP conversion at market FX rates differs substantially from Purchasing Power Parity (PPP).
- Reporting periods differ across sovereign statistical release calendars (e.g. US Q3 vs. UK Q3 vs. India Q2).
- Only official multi-lateral institutions (IMF, World Bank, OECD) calculate weighted world aggregates using formal international comparison programs.

ATLAS displays each economy with its independent reference period, unit, and source agency badge.

---

## 8. Authenticated REST API Reference

All endpoints live under `/api/v1/economics` and require Bearer token authentication and `atlas.access` authorization.

| Method | Endpoint | Query Parameters | Description |
|---|---|---|---|
| `GET` | `/api/v1/economics/overview` | `as_of_date` | Global macroeconomic matrix for G6 economies with independent reference periods. |
| `GET` | `/api/v1/economics/categories` | &mdash; | Returns all controlled indicator categories. |
| `GET` | `/api/v1/economics/indicators` | `category` | Canonical indicator catalog with default units and frequencies. |
| `GET` | `/api/v1/economics/indicators/{id}` | &mdash; | Canonical indicator detail by UUID or slug. |
| `GET` | `/api/v1/economics/series` | `geography_id`, `category`, `indicator_id` | Discover sovereign source series. |
| `GET` | `/api/v1/economics/series/{id}` | &mdash; | Source series metadata, definitions, agency URLs. |
| `GET` | `/api/v1/economics/series/{id}/observations` | `transformation`, `start_period`, `end_period`, `as_of_date`, `limit` | Bounded historical observations with mathematical transformation engine. |
| `GET` | `/api/v1/economics/series/{id}/vintages` | `reference_period` | Official revision vintages (Advance, Second, Third estimates). |
| `GET` | `/api/v1/economics/geographies` | &mdash; | Supported sovereign jurisdictions and economic areas. |
| `GET` | `/api/v1/economics/coverage` | &mdash; | Coverage metrics, verified providers, and governance notices. |
| `GET` | `/api/v1/economics/transformations` | &mdash; | Registered mathematical transformations and unit transition rules. |

---

## 9. Frontend Economics Workspace

The frontend workspace at `apps/web/src/components/economics/EconomicsWorkspace.tsx` provides three primary functional views:

1. **Global Overview**:
   - `GlobalMacroSnapshotCards`: Anchor metrics (Real GDP Growth, CPI Headline Inflation, Central Bank Policy Rates, Labor Unemployment).
   - `MajorEconomiesTable`: Matrix comparing US, Euro Area, China, India, Japan, and UK with click-to-chart actions, explicit reference period tags, and agency badges.
   - `EconomicCoveragePanel`: Architectural disclaimers, sovereign boundaries, and point-in-time governance rules.
2. **Indicator Explorer**:
   - Filter pills for National Accounts, Inflation, Labor Market, Interest Rates, Monetary, Fiscal, External Sector, and Industrial Activity.
   - Geography dropdown filter.
   - Text search across series codes, indicator titles, and agencies.
3. **Historical Series View**:
   - `EconomicSeriesChart`: Interactive SVG line and bar chart with frequency-aware time axis, unit-aware Y axis, zero-baseline support for negative numbers, missing-period gap retention, and hover crosshair tooltips.
   - Preset buttons: `1Y`, `3Y`, `5Y`, `10Y`, `MAX`.
   - Transformation dropdown: Real-time calculation of YoY, MoM, QoQ, Annualized QoQ, %p change, or basis points.
   - `EconomicObservationsTable`: Tabular history with pagination and CSV export.
   - `EconomicSourceInspector`: Provenance drawer displaying canonical IDs, agency definitions, and revision vintages.

---

## 10. Quality Gates & Verification

- **Backend Pytest**: 27 dedicated tests in `apps/api/tests/test_economics_v1.py` covering canonical indicator identity, frequency validation, G6 geography mappings, inflation price level vs rate distinction, GDP compound annualization math, interest rate basis points math, revision vintages, point-in-time query boundaries, HTTP API endpoints, 404/400 errors, and zero side-effects.
- **Regression Suite**: 218 total backend tests passing across Companies, Earnings, Ratios, Statements, Filings, Peers, Supply Chain, and Economics.
- **Python Lint**: `ruff check` passes with 0 warnings/errors.
- **TypeScript**: `npx tsc --noEmit` passes with 0 type errors.
- **Production Build**: Next.js 16.3.8 Turbopack build succeeds with route `/economics` rendered statically.

---

## 11. Roadmap Boundaries & Stage 90 Preparation

Stage 89 delivers Economics V1.
Future roadmap stages build on this foundation:
- **Stage 90**: Country Economics &mdash; Comprehensive sovereign economic dossiers, fiscal decomposition, demographic profiles.
- **Stage 91**: Central Banks &mdash; Monetary policy meetings, decision timelines, balance sheet research, speeches.
- **Stage 92**: Economic Calendar &mdash; Release schedules, consensus forecast surveys, event surprises.
- **Stage 93**: Macro Comparisons &mdash; Cross-country correlation matrices, macroeconomic percentile rankings.

**Stage 89 is Complete.**
