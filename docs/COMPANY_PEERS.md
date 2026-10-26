# ATLAS Stage 87: Company Peers & Comparable Company Analysis

## Executive Summary

Stage 87 implements an institutional-grade **Company Peers and Comparable Company Analysis** system within ATLAS `/companies`. It delivers source-grounded comparable company identification, multi-taxonomy industry classification, user-scoped custom peer groups with concurrency control, cross-company financial statement and ratio benchmarking, relative market valuation analysis, statistical distributions (peer mean, median, IQR outlier detection, percentile ranks), and multi-year historical trend series.

Crucially, ATLAS enforces a strict architectural distinction:
- **`COMPARABLE_CANDIDATE`**: Inferred via objective industry taxonomy, size, and business model criteria.
- **`USER_SELECTED_PEER`**: An analyst's comparison preference; never alters corporate relationship graphs.
- **`SOURCE_DEFINED_PEER`**: Labeled by verified financial data providers.
- **`VERIFIED_COMPETITOR`**: Direct commercial competitor supported by verifiable filing evidence.

A comparable company is not automatically a competitor, and competitors are not always financially comparable.

---

## Architecture Overview

```
ATLAS AUTHENTICATED APPSHELL
                │
                ▼
             COMPANIES
             (Stage 81)
                │
                ▼
              PEERS
             (Stage 87)
                │
      ┌─────────┴──────────┐
      │                    │
      ▼                    ▼
  Peer Discovery      Peer Groups
      │                    │
      ▼                    ▼
Verified Industry       User-Scoped
Classification          Persistence
      │                    │
      └─────────┬──────────┘
                │
                ▼
    Canonical Company Resolution
                │
                ▼
    Comparable Company Selection
                │
      ┌─────────┴──────────┐
      │                    │
      ▼                    ▼
Financial Inputs     Market Valuation
      │                    │
      ▼                    ▼
   Stage 82              Stage 33
   Statements            Market Data
      │                    │
      ▼                    ▼
   Stage 83             Stage 83
   Ratio Registry       Valuation Ratios
      │                    │
      └─────────┬──────────┘
                │
                ▼
     Financial Compatibility Layer
                │
      ┌─────────┴──────────┐
      │                    │
      ▼                    ▼
  Period Alignment     Currency Alignment
      │                    │
      └─────────┬──────────┘
                │
                ▼
      Qualified Comparable Metrics
                │
      ┌─────────┴──────────┐
      │                    │
      ▼                    ▼
 Benchmark Statistics   Historical Analysis
      │                    │
      └─────────┬──────────┘
                │
                ▼
         Provenance / Entitlements
                │
                ▼
           Typed Peers API
                │
                ▼
     Professional Peers Workspace
```

---

## 1. Canonical Company Identity & Resolution

All peer relationships reference canonical Company UUIDs. Ticker symbols are treated strictly as secondary display aliases.
- **Subject Company**: Explicitly identified as the focus of the benchmarking group.
- **No Self-Peer Selection**: The subject company cannot be selected as a peer of itself.
- **Duplicate Issuer Deduplication**: Secondary exchange listings or ADRs are mapped to the primary issuer entity to prevent double counting.
- **Security Context**: Market capitalization and valuation multiples resolve share-class definitions and total diluted share counts.

---

## 2. Industry Classification Integration

Multi-taxonomy industry classifications are preserved with strict provenance:
- **GICS**: Global Industry Classification Standard (Sector, Industry Group, Industry, Sub-Industry). E.g., Apple Inc. is classified under GICS Code `45202030`: *Information Technology* → *Technology Hardware, Storage & Peripherals*.
- **ICB, NAICS, SIC**: Maintained as distinct taxonomy versions without cross-contamination.
- **Historical Classifications**: Classification versions are timestamped; current classifications are not projected retrospectively without source records.
- **Unknown Classifications**: Clearly marked as `UNAVAILABLE` rather than inferred via heuristic guesswork.

---

## 3. Peer Candidate Discovery Engine

Deterministic candidate scoring evaluates:
1. **Industry Similarity** (45%): Matching primary sub-industry, industry, or broader sector.
2. **Business Model & Scale** (30%): Revenue scale and enterprise capitalization compatibility.
3. **Geographic Scope** (15%): Primary operating jurisdiction and headquarters.
4. **Source Relationship Evidence** (10%): Verified SEC Form 10-K Item 1 competition disclosures.

Every candidate provides inspectable **selection reasons** explaining why it was discovered.

---

## 4. User Peer Group Persistence & Concurrency

Analyst-defined peer groups are stored per authenticated user:
- **User Isolation / RLS**: Private groups are inaccessible to other users.
- **System Default Groups**: Read-only baseline groups (e.g. `pg-tech-hardware-default`) that cannot be mutated or deleted.
- **Capacity Limits**: Bounded between 1 and 25 peer companies per group.
- **Revision Concurrency**: Every mutation increments `revision`. Outdated edits trigger `PEER_GROUP_REVISION_CONFLICT` (HTTP 409).

---

## 5. Financial Comparison & Period Alignment

Standardized metrics across six analytical categories:
- **Scale**: Total Revenue, Gross Profit, Operating Income, EBITDA, Net Income, Total Assets, Total Debt, Total Shareholders' Equity, Cash & Equivalents.
- **Growth**: Revenue Growth YoY.
- **Profitability**: Gross Margin, Operating Margin, EBITDA Margin, Net Margin, Return on Equity (ROE), Return on Assets (ROA), Return on Invested Capital (ROIC).
- **Liquidity**: Current Ratio, Quick Ratio.
- **Solvency**: Debt-to-Equity (D/E).
- **Cash Flow**: Free Cash Flow (FCF), Free Cash Flow Yield.

### Period Alignment Modes:
- **`LATEST_COMMON_FISCAL_YEAR`**: Standardizes comparison to the latest shared fiscal year-end across all peers (e.g. FY2024).
- **`LATEST_AVAILABLE`**: Compares each company's most recent filing date while making period-end variances explicit.
- **`QUALIFIED_TTM`**: Trailing twelve months using Stage 82 quarterly summation; never multiplies a single quarter by four.

---

## 6. Relative Valuation Benchmarking

Valuation multiples are computed using canonical market data and earnings facts:
- **Price-to-Earnings (P/E)**: Market Capitalization / Consolidated Net Income.
- **Forward P/E**: Price / Consensus Forward EPS where authorized analyst estimates exist.
- **Price-to-Book (P/B)**: Market Capitalization / Total Shareholders' Equity.
- **Price-to-Sales (P/S)**: Market Capitalization / Total Revenue.
- **EV / EBITDA**: Enterprise Value / EBITDA.
- **EV / Revenue**: Enterprise Value / Total Revenue.
- **Free Cash Flow Yield**: Free Cash Flow / Market Capitalization × 100.

### Non-Meaningful Multiples Handling:
Where denominators are negative (e.g., negative equity for Dell Technologies and HP Inc. due to historical share repurchases), P/B and ROE are explicitly flagged as `NOT_MEANINGFUL` (`N/M`). They are never displayed as positive numbers and are excluded from median and mean calculations without silent elimination.

---

## 7. Statistical Benchmark Engine

Cross-sectional distributions provide institutional rigour:
- **Peer Median**: Exact median across valid peer observations (supports odd and even sample sizes).
- **Peer Mean**: Arithmetic mean over eligible values.
- **Min / Max Range**: Observational boundaries.
- **Sample Coverage Ratio**: Discloses eligible peers versus total selected peers (`eligible_count / total_count`).
- **Subject Relative Spread**:
  $$\text{Relative Spread} = \frac{\text{Subject Value} - \text{Peer Median}}{|\text{Peer Median}|} \times 100$$
- **Percentage-Point Differences**: For margins and return percentages ($\text{pp} = \text{Subject Margin} - \text{Median Margin}$).
- **Outlier Detection**: Tukey's Interquartile Range (IQR) fences $[Q_1 - 1.5 \times \text{IQR}, Q_3 + 1.5 \times \text{IQR}]$. Identified outliers are disclosed in statistics rather than silently dropped.

---

## 8. Multi-Period Historical Trend Series

Provides multi-year comparative trajectories (FY2021 through FY2024):
- True point-in-time observations without future data leakage or artificial forward-filling.
- Preserves fiscal calendars and restatement vintages.

---

## 9. API Specification

All endpoints are mounted under `/api/v1/companies/{company_id}/peers`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/overview` | Subject classification, default group, highlights, and counts |
| `GET` | `/candidates` | Verified comparable candidates with relevance scores and match reasons |
| `GET` | `/metrics` | Complete catalog of supported financial and valuation metrics |
| `POST` | `/compare` | Batched cross-company comparison matrix and statistical benchmarks |
| `POST` | `/history` | Multi-period historical time series for subject and peers |
| `GET` | `/groups` | Lists user-owned and system default peer groups |
| `POST` | `/groups` | Creates a new user peer group (max 25 peers) |
| `GET` | `/groups/{group_id}` | Retrieves a single peer group |
| `PATCH` | `/groups/{group_id}` | Updates name or peer membership with revision checking |
| `DELETE` | `/groups/{group_id}` | Deletes a user peer group |
| `GET` | `/methodology` | Discloses statistical formulas, outlier policies, and taxonomy hierarchy |

---

## 10. Frontend Architecture

Integrated directly into `/companies` workspace:
- **`PeersOverviewCards`**: Classification badges, peer count, median spreads for P/E and Operating Margin.
- **`PeerCandidateExplorer`**: Interactive table with relevance scores, selection reasons, and verified competitor toggles.
- **`PeerFinancialTable`**: Dense institutional matrix with sticky metrics, right-aligned tabular numerals, and clickable cell source inspection.
- **`PeerValuationTable`**: Relative valuation multiples, subject spread vs median, percentile rank, and sample counts.
- **`PeerHistoricalCharts`**: SVG line charts tracking 4-year trends for Revenue, Operating Margin, and P/E multiples.
- **`PeerScatterPlot`**: Growth vs Margin competitive positioning matrix with market-cap bubble sizing and median quadrant crosshairs.
- **`PeerGroupManager`**: Full CRUD interface for custom analyst peer groups.
- **`PeerSourceInspector`**: Inspects exact decimal values, XBRL filing references, and calculation lineage.

---

## 11. Security & Guardrails

- **0 LLM Calls**: All candidate discovery, classifications, and financial statistics are strictly deterministic.
- **0 Trading / Portfolio Mutations**: Peer analysis is an analytical research workspace and never places trades.
- **Data Entitlement & RLS**: Private peer groups are isolated per user; licensed taxonomy data adheres to source permissions.
- **Stage 88 Boundaries**: Supply chain intelligence, customer concentration, and supplier dependency networks are deferred strictly to Stage 88.
