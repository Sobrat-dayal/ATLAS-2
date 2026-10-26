# ATLAS — MACROECONOMIC COMPARISONS & BENCHMARKING ENGINE (STAGE 93)

## Canonical Source-of-Truth Architectural Documentation

---

## 1. Executive Overview

Stage 93 establishes the institutional-grade **Global Macroeconomic Comparison and Benchmarking Engine** inside `/economics` of the ATLAS platform. 

The system enables economists, quantitative researchers, institutional asset allocators, sovereign risk analysts, and financial professionals to perform cross-country macroeconomic benchmarking, calculate statistical distributions, analyze historical convergence and divergence, evaluate pairwise correlations, and inspect full data lineage without relying on fabricated metrics, synthetic harmonized series, or ungrounded machine learning extrapolations.

Stage 93 completes the foundational 5-stage **Economics roadmap** sequence:
- **Stage 89**: Economics V1 (Canonical National Accounts Overview & Historical Series)
- **Stage 90**: Country Economics (Deep Sovereign Profiles & Category Semantics)
- **Stage 91**: Central Banks (Monetary Policy Decisions, Rates & Registry)
- **Stage 92**: Economic Calendar (Verified Releases, Consensus Forecasts & Surprises)
- **Stage 93**: Macro Comparisons (Cross-Country Benchmarking, Distributions & Correlations)

Following Stage 93, the roadmap transitions to **Stage 94: Screeners V1**.

---

## 2. Core Economic Comparability Principles

Cross-country economic comparison is valid only when underlying series measure compatible concepts, use congruent observation periods, maintain interpretable units, and preserve statistical methodology.

### Critical Inviolable Safeguards:
1. **Never Mix Nominal GDP in Different Local Currencies**:
   Nominal GDP expressed in local currencies cannot be numerically sorted or ranked. ATLAS converts or requires source-published common currency measures (Current USD) or Purchasing Power Parity (International Dollars).
2. **Never Confuse Nominal Market-FX GDP with PPP GDP**:
   GDP at Purchasing Power Parity accounts for domestic price level disparities and differs fundamentally from market-exchange-rate converted GDP. ATLAS tracks them as distinct indicators (`gdp_nominal_usd` vs `gdp_ppp_intl_dollars`).
3. **Never Mix Annualized and Non-Annualized Growth**:
   Quarterly annualized GDP growth rate is not interchangeable with YoY growth or non-annualized QoQ growth.
4. **Never Combine Central Government and General Government Fiscal Scopes**:
   Central government debt excludes subnational obligations, whereas general government includes regional and municipal entities. Debt-to-GDP and fiscal balance ratios are strictly qualified by accounting scope.
5. **No Double Counting of Sovereign Nations and Overlapping Economic Areas**:
   Supranational aggregates (such as the Euro Area `geo-ea`) are explicitly identified as `is_economic_area: true`. They cannot be naively summed with member sovereigns (e.g. Germany, France).
6. **No Arbitrary Averaging for World Aggregates**:
   A simple arithmetic mean of national growth or inflation rates does not constitute an official regional or world aggregate. Official published aggregates are favored, or rigorous GDP/population weighting is required and disclosed.
7. **No Arbitrary Normative Ranking**:
   Rankings are strictly numeric (`ascending` or `descending`). Higher inflation or lower unemployment are not normatively labeled "best" or "worst".
8. **Missing Values Are Never Zero**:
   Absent observations are excluded from rankings and distributions with sample sizes explicitly reported ($N$ eligible of $M$ total).
9. **Correlation Does Not Imply Causality**:
   Pairwise correlations require identical reference periods, a minimum sample size ($N \ge 4$), zero-variance guards, and warnings regarding nonstationarity and serial correlation in trending macroeconomic levels.

---

## 3. Supported Macroeconomic Indicators & Controlled Taxonomies

ATLAS Stage 93 supports 16 canonical comparable indicators across 7 economic pillars:

| Metric Kind | Name | Category | Default Unit | Canonical Source Agency |
|---|---|---|---|---|
| `gdp_nominal_usd` | Gross Domestic Product (Nominal) | National Accounts | USD Billions | IMF WEO / World Bank |
| `gdp_real_growth_yoy` | Real GDP Growth (YoY) | National Accounts | % YoY | National Statistical Offices / OECD |
| `gdp_per_capita_usd` | Nominal GDP Per Capita | National Accounts | USD | World Bank / IMF WEO |
| `gdp_ppp_intl_dollars` | GDP at Purchasing Power Parity | National Accounts | Intl $ Billions | World Bank ICP / IMF WEO |
| `gdp_ppp_per_capita_intl` | PPP GDP Per Capita | National Accounts | Intl $ | World Bank ICP / IMF WEO |
| `cpi_headline_yoy` | Headline CPI Inflation | Prices & Inflation | % YoY | National Statistical Bureaus / Eurostat HICP |
| `cpi_core_yoy` | Core CPI Inflation | Prices & Inflation | % YoY | National Statistical Bureaus / BLS / Eurostat |
| `unemployment_rate` | Harmonized Unemployment Rate | Labor Market | % | ILO / OECD MEI / BLS |
| `labor_participation_rate` | Labor Force Participation Rate | Labor Market | % | National Labor Surveys / ILO |
| `central_bank_policy_rate` | Central Bank Policy Rate | Monetary Policy | % | Federal Reserve, ECB, BOJ, RBI, PBOC, BOE |
| `government_debt_to_gdp` | Gross Public Debt-to-GDP | Fiscal & Debt | % of GDP | IMF Fiscal Monitor / Eurostat |
| `fiscal_balance_to_gdp` | Government Fiscal Balance-to-GDP | Fiscal & Debt | % of GDP | IMF Fiscal Monitor / National Ministries of Finance |
| `trade_balance_to_gdp` | Goods & Services Trade Balance-to-GDP | External Sector | % of GDP | National Central Banks / IMF IFS |
| `current_account_to_gdp` | Current Account Balance-to-GDP | External Sector | % of GDP | IMF Balance of Payments / National Accounts |
| `foreign_exchange_reserves_usd` | Official FX & Gold Reserves | External Sector | USD Billions | IMF COFER / National Central Banks |
| `population_millions` | Total Resident Population | Demographics | Millions | UN Population Division / National Census |

---

## 4. Geographic Entities & Canonical Cohorts

ATLAS Stage 93 resolves sovereign economies and supranational statistical areas through Stage 19 Geographic Entities:

- **United States** (`geo-us`, `USA` / `US`)
- **Euro Area** (`geo-ea`, `EA` / `EUR`, `is_economic_area: true`)
- **China** (`geo-cn`, `CHN` / `CN`)
- **Japan** (`geo-jp`, `JPN` / `JP`)
- **United Kingdom** (`geo-gb`, `GBR` / `GB`)
- **India** (`geo-in`, `IND` / `IN`)

### Supported Cohorts:
1. **G7**: Advanced industrialized sovereign cohort (`US`, `EA`, `JP`, `GB`).
2. **G20**: Group of Twenty major advanced and emerging market economies.
3. **BRICS**: Major emerging market economies (`CN`, `IN`).
4. **OECD**: Organisation for Economic Co-operation and Development.
5. **EU_EURO_AREA**: European Union & Euro Area monetary union.
6. **CUSTOM_SELECTION**: Ad-hoc user selection bounded between 2 and 20 economies.

---

## 5. Statistical Comparison Engine Architecture

The backend comparison engine (`atlas.economics.comparisons`) is structured as follows:

```
ATLAS ECONOMICS
       |
       v
  FastAPI Router (/api/v1/economics/comparisons)
       |
       v
  MacroComparisonsService
       |
  +----+--------------------------------+
  |                                     |
  v                                     v
Concept Compatibility Resolver   Geographic Cohort Filter
  |                                     |
  +-----------------+-------------------+
                    |
                    v
       Period & Unit Alignment Layer
                    |
      +-------------+-------------+
      |                           |
      v                           v
  Descriptive Distributions     Sovereign Rankings
  (Mean, Median, IQR, StdDev)   (Standard & Dense Ties)
      |                           |
      +-------------+-------------+
                    |
      +-------------+-------------+
      |                           |
      v                           v
  Historical Trends             Pairwise Divergence
  (Index-to-100 Rebase)         (Differentials & Ratios)
      |                           |
      +-------------+-------------+
                    |
                    v
        Paired Sample Correlations
        (Pearson & Spearman with N >= 4 Guards)
                    |
                    v
          Data Lineage & Provenance
```

### Statistical Methods Implemented:
- **Mean (Unweighted)**:
  $$\bar{x} = \frac{1}{N} \sum_{i=1}^N x_i$$
- **Weighted Mean (Population or GDP)**:
  $$\bar{x}_w = \frac{\sum_{i=1}^N w_i x_i}{\sum_{i=1}^N w_i}$$
- **Standard Deviation (Sample)**:
  $$s = \sqrt{\frac{1}{N-1} \sum_{i=1}^N (x_i - \bar{x})^2}$$
- **Quartiles ($Q_1, Q_3$) & Median**: Deterministic linear interpolation on sorted sample.
- **Index-to-100 Rebasing**:
  $$I_{i,t} = \frac{x_{i,t}}{x_{i, \text{base}}} \times 100$$
- **Pearson Linear Correlation**:
  $$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$$
- **Spearman Rank Correlation**:
  $$r_s = 1 - \frac{6 \sum d_i^2}{N(N^2 - 1)}$$

---

## 6. Frontend Workspace Architecture

The frontend workspace is mounted at `/economics` under the `Macro Comparisons` sub-tab.

```
apps/web/src/components/economics/comparisons/
  ├── MacroComparisonsWorkspace.tsx     # Coordinator and state container
  ├── MacroComparisonToolbar.tsx       # Subviews, cohorts, countries, alignment
  ├── MacroComparisonMatrix.tsx        # High-density cross-country terminal table
  ├── MacroRankingTable.tsx            # Sovereign rankings with competition/dense ties
  ├── MacroDistributionPanel.tsx       # Mean, median, quartiles, dispersion diagram
  ├── MacroHistoricalTrendChart.tsx    # Multi-country SVG charts with index rebase
  ├── MacroDivergencePanel.tsx         # Pairwise spread differentials (bps / pp)
  ├── MacroCorrelationMatrix.tsx       # Paired correlation coefficients and caveats
  ├── ComparisonMethodologyInspector.tsx # Lineage and agency audit modal
  ├── ComparisonCoveragePanel.tsx      # Comprehensive data availability matrix
  └── index.ts                         # Public exports
```

---

## 7. Automated Test Suite Verification

Comprehensive test suites in `apps/api/tests/test_macro_comparisons.py` cover:
- Metric metadata resolution and canonical categories
- Geographic cohorts and area classification
- Concept compatibility and qualification flags
- Multi-country comparison matrix generation
- Sovereign rankings (descending, ascending, competition ties, dense ties)
- Descriptive statistical distributions (mean, median, IQR, std dev, population weighting, GDP weighting)
- Multi-country historical trends with base-period indexing
- Pairwise divergence differentials in basis points and percentage points
- Pearson and Spearman correlations with sample size guards and zero-variance protection
- REST API endpoint integration across all 11 routes

Full economics regression suite (Stages 89, 90, 91, 92, 93) executes with **98 passed, 0 failures**.
TypeScript compilation (`npx tsc --noEmit`) passes with **0 errors**.
Next.js production build succeeds with clean outputs.
