# COMPANY EARNINGS INTELLIGENCE (STAGE 84)

## Master Architecture & Specification

Institutional-grade corporate earnings intelligence system inside ATLAS, integrating canonical corporate earnings events, reported financial results, analyst consensus expectations, earnings surprise analytics, management guidance tracking, conference call references, and institutional research workspaces.

---

## 1. Domain Model & Core Concepts

ATLAS models corporate earnings through eight distinct, strongly-typed domain representations rather than conflating disparate data into a single generic record:

```
                                  +-------------------+
                                  |   EarningsEvent   |
                                  +---------+---------+
                                            |
                         +------------------+------------------+
                         |                                     |
                         v                                     v
               +-------------------+                 +-------------------+
               |  EarningsActual   |                 | ConsensusSnapshot |
               | (Reported Results)|                 | (Pre-Release Est.)|
               +---------+---------+                 +---------+---------+
                         |                                     |
                         +------------------+------------------+
                                            |
                                            v
                                 +--------------------+
                                 |  EarningsSurprise  |
                                 |  (Decimal-Safe)    |
                                 +--------------------+
                                            |
                +---------------------------+---------------------------+
                |                                                       |
                v                                                       v
     +--------------------+                                  +--------------------+
     | ManagementGuidance |                                  |    EarningsCall    |
     | (Corporate Forward)|                                  | (Webcasts/Trans.)  |
     +--------------------+                                  +--------------------+
```

### 1.1 EarningsEvent
- **Event Identity**: `event_id` (UUID), `company_id` (UUID canonical entity), `fiscal_period` (e.g. `Q4 2024`, `FY 2024`).
- **Timing & Precision**: `announced_date`, `announced_time`, `timezone` (IANA format, e.g. `America/New_York`), `is_confirmed` (boolean).
- **Session Classification**: `BEFORE_MARKET` (BMO), `AFTER_MARKET` (AMC), `DURING_HOURS`, or `UNSPECIFIED`.
- **Status Lifecycle**: `CONFIRMED`, `ESTIMATED`, `TENTATIVE`, `POSTPONED`, `CANCELLED`, `COMPLETED`.

### 1.2 EarningsActual
- **Reported Accounting Metrics**: Diluted EPS, Basic EPS, Total Revenue.
- **Accounting Basis**: GAAP, Non-GAAP, or IFRS.
- **Reporting Scope**: Standalone quarterly vs. cumulative year-to-date (YTD); consolidated corporate group scope.
- **Currency & Units**: Preserved in reported currency (e.g. USD, EUR, INR) without speculative conversion.
- **Lineage**: Linked to Stage 82 Financial Statement Fact IDs (`source_fact_id`).

### 1.3 ConsensusSnapshot
- **Expectation Baseline**: Aggregate analyst mean / median consensus published prior to the announcement.
- **Pre-Release Cutoff**: Guaranteed available timestamp `as_of < announced_date`. Post-announcement revisions are strictly excluded.
- **Analyst Coverage**: Actual eligible firm count (`analyst_count`), range bounds (`eps_high`, `eps_low`, `revenue_high`, `revenue_low`).

### 1.4 EarningsSurprise
- **Absolute Surprise**:
  $$\text{EPS Surprise}_{\text{abs}} = \text{EPS}_{\text{actual}} - \text{EPS}_{\text{estimate}}$$
  $$\text{Revenue Surprise}_{\text{abs}} = \text{Revenue}_{\text{actual}} - \text{Revenue}_{\text{estimate}}$$
- **Percentage Surprise**:
  $$\text{Surprise}_{\%} = \frac{\text{Actual} - \text{Estimate}}{|\text{Estimate}|} \times 100$$
- **Zero-Estimate Protection**: When Estimate is zero, percentage surprise is mathematically undefined; absolute surprise is displayed and percentage is assigned `None` with documented qualification.
- **Negative-Estimate Handling**: Denominator uses $|\text{Estimate}|$ ensuring mathematical consistency, qualified with sign context.
- **Classification Policy**:
  - `BEAT`: $\text{Actual} > \text{Estimate}$
  - `MISS`: $\text{Actual} < \text{Estimate}$
  - `IN_LINE`: $|\text{Actual} - \text{Estimate}| \le 0.05\%$ (or exact equality for per-share rounding)
  - `NOT_COMPARABLE`: Incompatible basis (e.g. GAAP actual vs non-GAAP consensus without adjustment).

### 1.5 ManagementGuidance
- **Corporate Projections**: Company-issued forward projections released during earnings calls or press releases.
- **Clear Distinction**: Strictly distinguished from 3rd-party analyst consensus.
- **Range & Point Projections**: Minimum, maximum, and midpoint values with explicit currency and basis.
- **Status Tracking**: `ACTIVE`, `REVISED`, `WITHDRAWN`, `SUPERSEDED`.

### 1.6 EarningsCall
- **Audio Webcasts**: Direct references to verified official investor-relations audio streams.
- **Presentation Materials**: Direct links to official earnings slide decks and shareholder letters.
- **Transcript Licensing**: Rights-aware document metadata (`AVAILABLE`, `LICENSED_ONLY`, `RESTRICTED`, `PENDING`). No synthesized or LLM-generated fake transcripts.

---

## 2. Temporal & Point-in-Time Integrity

ATLAS enforces institutional data hygiene:
1. **No Look-Ahead Leakage**: Consensus snapshots are bound to pre-release availability timestamps. Analysts' post-release updates cannot retroactively modify historical surprise benchmarks.
2. **Restatement Awareness**: Restated financial results are flagged as `Restated`. Original reported actuals remain preserved to explain initial market reaction.
3. **No Estimated Future Fabrication**: If an upcoming earnings announcement date is not verified by corporate disclosure, it is labeled `ESTIMATED` or marked `Unavailable`. Adding arbitrary 90-day intervals is prohibited.

---

## 3. Pure Decimal Arithmetic & Zero-Division Safety

All calculations in `python/atlas/src/atlas/companies/earnings/calculator.py` execute using Python's `Decimal` module:
- No IEEE-754 binary floating point precision artifacts.
- Zero denominator protection (`InvalidOperation` and `ZeroDivisionError` trapped cleanly).
- Bounded formatting with explicit scaling (Billions, Millions, or 2-decimal per-share precision).

---

## 4. API Specification

All endpoints are mounted under `/api/v1/companies/{company_id}/earnings/`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/overview` | Complete summary including latest reported result, next scheduled release, and next consensus |
| `GET` | `/history` | Historical quarterly/annual results with actuals, consensus, and calculated surprises |
| `GET` | `/events` | Catalog of corporate earnings announcement events (completed, confirmed, estimated) |
| `GET` | `/events/{event_id}` | Detailed single event profile |
| `GET` | `/guidance` | Corporate management guidance projections and revisions |
| `GET` | `/calls` | Conference calls, webcasts, and licensed transcript document references |

### Query Parameters
- `period_type`: `QUARTERLY` (default) or `ANNUAL`.
- `limit`: Number of historical quarters to return (default: 20, max: 40).

---

## 5. Security & Entitlements

1. **Authentication**: Mandatory via `PermissionCode.ATLAS_ACCESS`.
2. **Entitlement Isolation**: Users without analyst consensus entitlements receive financial actuals with consensus and surprise fields marked `UNAVAILABLE`.
3. **Derived-Data Protection**: Restricted consensus values are never leaked through surprise percentages.
4. **Licensing**: Full transcript texts are gated by document licensing permissions.
5. **Zero Side-Effects**: Read requests execute 0 database writes, 0 trading orders, 0 provider fanout on ordinary page load, and 0 LLM executions.

---

## 6. Frontend Workspace

The institutional earnings research interface resides in `/companies`:
- **Overview Cards**: Displays latest reported quarter, Diluted EPS vs consensus, Total Revenue vs consensus, and next confirmed/estimated announcement date with pre-market/after-market timing.
- **Actual vs Estimate Interactive Chart**: Dual-metric SVG chart toggleable between EPS and Revenue with beat/miss colored bars and hover tooltip inspectors.
- **Historical Results Table**: High-density table featuring fiscal periods, announcement dates, sessions, diluted EPS, consensus EPS, surprise %, actual revenue, estimate revenue, and expander drawers for methodology auditing.
- **Management Guidance Panel**: Company-issued range and point forward projections with revision and withdrawal tracking.
- **Earnings Calls Panel**: Conference call schedules, executive agendas, webcast audio links, and transcript document references.

---

## 7. Roadmap Stage Boundaries

- **Stage 81**: Companies V1 (Directory & Profiles).
- **Stage 82**: Financial Statements (Balance Sheet, Income Statement, Cash Flow).
- **Stage 83**: Financial Ratios (Profitability, Liquidity, Solvency, Valuation Multiples).
- **Stage 84**: **Company Earnings Intelligence** (Current completed stage).
- **Stage 85**: Company Ownership Intelligence (Institutional holders, insider holdings, beneficial ownership).
- **Stage 86**: Corporate Regulatory Filings & Advanced Search.
- **Stage 87**: Peer Intelligence & Cross-Company Benchmarking.
- **Stage 88**: Supply Chain Relationships & Networks.

*No functionality reserved for Stage 85 or subsequent stages has been implemented in Stage 84.*
