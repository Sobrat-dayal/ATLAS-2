# Stage 106: Institutional-Grade Financial Research Analysis, Evidence-Backed Hypothesis Evaluation, and Reproducible Analytical Workbenches

**Project:** ATLAS — AI-Native Financial Intelligence and Quantitative Research Operating System  
**Canonical Roadmap Position:** Stage 106 of 150  
**Primary Module:** Research  
**Primary Route:** `/research`  
**Sub-Views:** Overview, Investigations, Source Library, Discovery, Document Viewer, Comparison, Analysis, Activity Timeline  

---

## 1. Executive Overview

Stage 106 bridges ATLAS's Research Foundation (Stage 104) and Document Intelligence (Stage 105) into an institutional-grade, reproducible analytical calculation and hypothesis evaluation engine. Designed to meet the stringent standards of quantitative researchers, buy-side fundamental analysts, and investment committees, Stage 106 delivers:

1. **Canonical Research Analysis Domain**: Typed `ResearchAnalysis` entity with stable identifiers, user ownership, investigation scoping, optimistic concurrency versioning (`revision`), and reproducible execution runs (`ResearchAnalysisRun`).
2. **Controlled Analysis Type Registry**: 13 institutional analysis types spanning company financial trends, canonical ratio evaluations, cross-sectional peer benchmarking, macroeconomic time-series, hypothesis evaluations, and bounded assumption sensitivities.
3. **Rigorous Financial Mathematics**: Period-over-period differences ($\Delta$), percentage changes ($\%\Delta$ with mandatory zero-base division guards and negative-base warnings), and compound annual growth rate (CAGR with positive endpoint constraints).
4. **Safe AST Expression Evaluator**: A sandboxed AST expression engine (`SafeExpressionEvaluator`) rejecting arbitrary Python/SQL/shell execution, `eval()`, `exec()`, imports, and function calls, while bounding expression depth and node count.
5. **Cross-Sectional Peer Benchmarking**: Seamless reuse of Stage 87 verified Peer Groups with non-parametric median, first quartile ($Q_1$), third quartile ($Q_3$), sample mean, dispersion metrics, explicit eligible count ($N$), and comparability divergence warnings.
6. **Deterministic Hypothesis Evaluation**: Formal test criteria linked to Stage 104 Hypotheses, evaluating observations into explicit supporting vs. contradicting evidence lists and institutional outcomes (`CRITERIA_MET`, `CRITERIA_NOT_MET`, `MIXED_RESULTS`, `INCONCLUSIVE`, `INSUFFICIENT_DATA`) without hyperbole or universal truth claims.
7. **Epistemic Research Findings Lifecycle**: Categorization of findings into `OBSERVED_FACT`, `CALCULATED_RESULT`, `STATISTICAL_OBSERVATION`, `ANALYST_INTERPRETATION`, and `INCONCLUSIVE_RESULT` with auditable review statuses and mandatory limitation disclosures.
8. **Controlled Sensitivity Analysis**: User-defined `ResearchAssumption` records generating bounded scenario matrices with non-predictive institutional disclosures.
9. **Cryptographic Analytical Provenance**: Watermarked source observation manifests indexing SEC EDGAR Form 10-K accession numbers, reporting dates, fact concepts, and versioned formula contracts.
10. **Institutional Terminal Workbench**: A high-density split-pane workspace (`ResearchAnalysisWorkspace`) featuring time series bar charts with CAGR badges, cross-sectional peer benchmark bars with median lines, macro observation timelines, live hypothesis criteria testers, findings editors, and provenance audit drawers.

---

## 2. Architecture & Data Flow

```
                      +---------------------------------------+
                      |         ATLAS Client (/research)      |
                      |  - Analysis Studio & History         |
                      |  - Financial Trend & Benchmark Charts|
                      |  - Hypothesis Tester & Findings Tab   |
                      |  - Sensitivity & Provenance Drawers  |
                      +-------------------+-------------------+
                                          | HTTP / JSON REST
                                          v
                      +---------------------------------------+
                      |       FastAPI Research Router         |
                      |  /api/v1/research/analyses/...        |
                      |  /api/v1/research/hypotheses/...      |
                      |  /api/v1/research/findings/...        |
                      |  /api/v1/research/assumptions/...     |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |           ResearchService             |
                      |  - Specification Validation           |
                      |  - Execution Engine Orchestration     |
                      |  - Hypothesis Evaluation Resolution   |
                      |  - Findings & Assumption Management   |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |      Analysis Execution Engine        |
                      |  - Historical Trend Computations     |
                      |  - Cross-Sectional Peer Statistics   |
                      |  - Macro Series Alignment            |
                      |  - Safe AST Expression Evaluator     |
                      |  - Watermark & Accession Manifest    |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |          ResearchRepository           |
                      |  - Analyses & Historical Runs        |
                      |  - Pre-Indexed Canonical Statements  |
                      |  - Stage 87 Verified Peer Data       |
                      |  - SEC Form 10-K Accession Spans     |
                      |  - Multi-Tenant RLS Enforcement      |
                      +---------------------------------------+
```

---

## 3. Supported Analysis Types

| Type ID | Label | Primary Subject | Supported Metrics | Calculation Methods |
|---|---|---|---|---|
| `COMPANY_FINANCIAL_TREND` | Company Financial Trend | `COMPANY` | Revenue, Net Income, Operating Cash Flow, Capex, Gross Margin | Period $\Delta$, $\%\Delta$, CAGR, AST expressions |
| `COMPANY_RATIO_ANALYSIS` | Company Ratio Analysis | `COMPANY` | Operating Margin, ROE, ROIC, Current Ratio, Debt-to-Equity | Ratio timeseries, baseline comparison |
| `CASH_FLOW_ANALYSIS` | Cash Flow & FCF Analysis | `COMPANY` | OCF, Capex, Free Cash Flow, FCF Conversion | FCF derivation, OCF/Net Income ratio |
| `CAPITAL_STRUCTURE_ANALYSIS` | Capital Structure Analysis | `COMPANY` | Total Debt, Cash & Equivalents, Net Debt, Equity | Net debt computation, Leverage ratios |
| `PEER_BENCHMARKING` | Cross-Sectional Peer Benchmarking | `COMPANY` | Revenue Growth, Operating Margin, ROIC, P/E, EV/EBITDA | Median, $Q_1$, $Q_3$, Mean, StdDev, Min, Max |
| `INDUSTRY_COMPARISON` | Industry Cohort Analysis | `INDUSTRY` | Industry Revenue, Margins, Dispersion | Cohort aggregation, percentile distribution |
| `MACROECONOMIC_TIME_SERIES` | Macroeconomic Time Series | `ECONOMIC_ENTITY` | CPI, Effective Fed Funds Rate, Real GDP, 10Y Yield | Period change, inflation rate, vintage cutoffs |
| `MULTI_INDICATOR_COMPARISON` | Multi-Indicator Macro Comparison | `ECONOMIC_ENTITY` | Dual-indicator macro metrics | Multi-series alignment, descriptive dispersion |
| `HISTORICAL_MARKET_CONTEXT` | Historical Market Context | `FINANCIAL_INSTRUMENT`| Daily/Monthly close, Volume, Total Return | Non-causal event window returns |
| `EVENT_DISCLOSURE_COMPARISON`| Corporate Event Disclosure Analysis| `FINANCIAL_EVENT` | Disclosed revenues, synergies, transaction metrics| Pre/post disclosure delta |
| `HYPOTHESIS_EVALUATION` | Evidence-Based Hypothesis Testing | Any | Any canonical metric | Deterministic relational operator testing |
| `DESCRIPTIVE_STATISTICAL_ANALYSIS`| Descriptive Statistical Analysis| Any | Continuous numeric time series | Mean, Median, Variance, Skewness, Kurtosis |
| `ASSUMPTION_SENSITIVITY_ANALYSIS`| Scenario & Sensitivity Analysis | `COMPANY` | Base revenue, cost growth, margin assumption | Deterministic what-if arithmetic matrix |

---

## 4. Quantitative Financial Calculations & Validation Rules

### Period-over-Period Variance & Growth
- **Absolute Delta ($\Delta$):**
  $$\Delta = X_t - X_{t-1}$$
- **Percentage Delta ($\%\Delta$):**
  $$\%\Delta = \frac{X_t - X_{t-1}}{X_{t-1}} \times 100$$
- **Zero-Base Guard:** If $X_{t-1} = 0$, the system returns `null` with explicit `N/A (Zero Base)` labeling.
- **Negative-Base Warning:** When $X_{t-1} < 0$ (e.g. moving from negative net income to positive or deeper negative), standard percentage growth calculations produce inverted signs. The engine flags this with `NEGATIVE_BASE_CAUTION` and reports absolute change rather than distorted percentage growth.

### Compound Annual Growth Rate (CAGR)
$$\text{CAGR} = \left(\frac{X_{\text{end}}}{X_{\text{start}}}\right)^{\frac{1}{n}} - 1$$
- **Positive Endpoint Requirement:** Enforced strictly: $X_{\text{start}} > 0$, $X_{\text{end}} > 0$, and elapsed periods $n > 0$.
- **Endpoint Guard:** Returns `null` if $X_{\text{start}} \le 0$ or $X_{\text{end}} \le 0$, returning an informative limitation badge rather than generating complex numbers or NaN.

### Safe AST Expression Evaluator
Custom calculated metrics are executed using `SafeExpressionEvaluator`:
- **Prohibited:** `eval()`, `exec()`, arbitrary Python, SQL, shell, imports (`__import__`), attribute lookups (`.`), builtins (`globals()`, `locals()`), and function calls.
- **Allowed:** Binary arithmetic operators (`+`, `-`, `*`, `/`), unary operators (`+`, `-`), numerical constants, and declared variable identifiers matching metric concepts.
- **Guards:** Recursion depth bounded to 10; AST node count bounded to 50; division by zero safely returns `None`.

### Non-Parametric Peer Statistics
- **Sample Median:** Middle observation for odd sample size, or arithmetic mean of the two central values for even sample size.
- **Quartiles ($Q_1, Q_3$):** Computed using linear interpolation between closest ranks.
- **Sample Dispersion:** Sample variance ($s^2 = \frac{1}{n-1} \sum (x_i - \bar{x})^2$) and standard deviation ($s$).
- **Reporting Disclosures:** Always reports eligible sample size $N$, excluded observation count, and comparability divergence warnings (e.g., non-conterminous fiscal year-ends or differing consolidation scopes).

---

## 5. Hypothesis Evaluation & Evidence Grounding

Stage 106 connects Stage 104 Hypotheses to empirical datasets via `ResearchHypothesisEvaluation`:

1. **Deterministic Test Criteria:**
   - Metric concept identifier (e.g., `operating_margin`).
   - Relational operator (`GREATER_THAN`, `GREATER_THAN_OR_EQUAL`, `LESS_THAN`, `LESS_THAN_OR_EQUAL`, `EQUALS`, `NOT_EQUALS`).
   - Threshold value (e.g., `0.30` for 30%).
   - Minimum required observations $N_{\text{min}}$.
2. **Outcome Classification:**
   - `CRITERIA_MET`: All eligible observations satisfy the condition.
   - `CRITERIA_NOT_MET`: Zero observations satisfy the condition.
   - `MIXED_RESULTS`: Observations satisfy condition for some periods but fail in others.
   - `INCONCLUSIVE`: Sample size $N < N_{\text{min}}$ or significant reporting discrepancies prevent conclusive determination.
   - `INSUFFICIENT_DATA`: Missing required input series.
3. **Evidence Linkage:**
   - Observations meeting criteria are indexed as `supporting_evidence_ids`.
   - Observations violating criteria are indexed as `contradicting_evidence_ids`.
4. **Epistemic Qualification:**
   - Meeting user criteria is explicitly qualified as conditional evidence within the selected historical window, not proof of an immutable financial law or profitable trading strategy.

---

## 6. Epistemic Research Findings Lifecycle

Research Findings formalize analyst takeaways with complete data lineage:

- **Categories:**
  - `OBSERVED_FACT`: Direct reporting from verified filings (e.g., Apple FY24 revenue of \$391.04B).
  - `CALCULATED_RESULT`: Derived quantitative value produced by an immutable analysis run (e.g., 3-year revenue CAGR of 1.95%).
  - `STATISTICAL_OBSERVATION`: Cross-sectional or regression finding with explicit sample $N$ (e.g., Apple operating margin exceeds peer median by 750 bps).
  - `ANALYST_INTERPRETATION`: Qualitative takeaway or hypothesis thesis authored by the analyst.
  - `INCONCLUSIVE_RESULT`: Finding explicitly stating that available empirical evidence is insufficient or contradictory.
- **Review Progression:** `DRAFT` $\to$ `NEEDS_EVIDENCE` $\to$ `READY_FOR_REVIEW` $\to$ `REVIEWED` $\to$ `REVISED` $\to$ `ARCHIVED`.
- **Limitation Disclosures:** Mandatory recording of methodological boundaries, unobserved periods, and accounting standard differences.

---

## 7. Controlled Assumption & Sensitivity Analysis

To support rigorous what-if modeling without descending into speculative valuation engines:

1. **Explicit Assumption Attribution:** Every parameter in `ResearchAssumption` is tagged as `SOURCE_REPORTED`, `ANALYST_ASSUMED`, or `DERIVED`. Unverified analyst estimates are prohibited from being labeled market consensus.
2. **Deterministic Arithmetic Grids:** Scenarios evaluate deterministic formulas (e.g., $\text{Adjusted Revenue} = \text{Base Revenue} \times (1 + g)$) across finite parameter ranges.
3. **Institutional Disclaimers:** Mandatory disclaimer header:
   > *"Hypothetical what-if calculations are non-predictive illustrative models and do not represent forecasts, expected probabilities, or investment recommendations."*

---

## 8. Cryptographic Provenance & Watermarks

Every `ResearchAnalysisRun` captures an auditable provenance trail:
- **Specification Hash:** Deterministic SHA-256 hash of the normalized input specification.
- **Source Watermark Manifest:** Mapping of every input observation to:
  - Canonical SEC EDGAR Accession Number (e.g., `0000320193-24-000106`).
  - Filing Form Type (`10-K`, `10-Q`).
  - Reporting Period End Date.
  - Publication / Filing Timestamp.
  - Fact Concept Identifier and Reporting Currency.
- **Point-in-Time Qualification:** Adheres to strict historical publication cutoffs to prevent future restatements or subsequent disclosure leakage into historical analysis frames.

---

## 9. Core REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/research/analysis-types` | List 13 supported analysis types and parameter contracts |
| `POST` | `/api/v1/research/analyses/validate` | Pre-flight validation of analysis specification |
| `GET` | `/api/v1/research/analyses` | List user-owned analyses with multi-factor filtering |
| `POST` | `/api/v1/research/analyses` | Create new analysis definition |
| `GET` | `/api/v1/research/analyses/{id}` | Retrieve analysis definition by ID |
| `PATCH` | `/api/v1/research/analyses/{id}` | Revision-safe update of analysis specification |
| `POST` | `/api/v1/research/analyses/{id}/duplicate` | Duplicate analysis specification within authorized scope |
| `DELETE` | `/api/v1/research/analyses/{id}` | Soft-delete or archive analysis |
| `POST` | `/api/v1/research/analyses/{id}/runs` | Execute reproducible analysis run |
| `GET` | `/api/v1/research/analyses/{id}/runs` | List run history for an analysis |
| `GET` | `/api/v1/research/analysis-runs/{run_id}` | Retrieve run execution metadata and status |
| `GET` | `/api/v1/research/analysis-runs/{run_id}/results`| Retrieve computed observations, deltas, and statistics |
| `GET` | `/api/v1/research/analysis-runs/{run_id}/provenance` | Retrieve SEC accession watermarks and formula lineage |
| `GET` | `/api/v1/research/hypotheses/{id}/evaluations` | List historical hypothesis evaluation runs |
| `POST` | `/api/v1/research/hypotheses/{id}/evaluations` | Execute deterministic hypothesis test against run |
| `GET` | `/api/v1/research/hypothesis-evaluations/{id}` | Retrieve evaluation criteria, outcome, and evidence lists |
| `GET` | `/api/v1/research/analyses/{id}/findings` | List research findings linked to an analysis |
| `POST` | `/api/v1/research/analyses/{id}/findings` | Create evidence-linked research finding |
| `GET` | `/api/v1/research/findings/{finding_id}` | Retrieve finding details, revisions, and citations |
| `PATCH` | `/api/v1/research/findings/{finding_id}` | Update finding text, review status, or limitations |
| `DELETE` | `/api/v1/research/findings/{finding_id}` | Archive or remove research finding |
| `GET` | `/api/v1/research/analyses/{id}/assumptions` | List analyst assumptions for an analysis |
| `POST` | `/api/v1/research/analyses/{id}/assumptions` | Register new parameter assumption |
| `DELETE` | `/api/v1/research/assumptions/{assumption_id}` | Remove parameter assumption |
| `POST` | `/api/v1/research/analyses/{id}/scenarios/sensitivity`| Execute deterministic what-if sensitivity matrix |

---

## 10. Frontend Architecture & Components

The frontend is implemented inside `apps/web/src/components/research/analysis/`:

- `ResearchAnalysisWorkspace.tsx`: Master split-pane workbench integrating sidebar list and studio view.
- `ResearchAnalysisStudio.tsx`: Master studio containing action toolbar, summary KPI strip, historical run selector, and 6 specialized sub-tabs.
- `FinancialTrendChart.tsx`: Source-grounded time-series bar chart rendering period bars, deltas, CAGR badge, restatement markers, and tooltips.
- `PeerBenchmarkChart.tsx`: Cross-sectional horizontal bar chart with median reference lines, target company highlighting, and sample size $N$ disclosures.
- `EconomicResearchChart.tsx`: Macroeconomic observation timeline displaying indicator values with vintage cutoff tags.
- `AnalysisResultsTable.tsx`: Tabular observation grid displaying period labels, reported values, deltas, percentage growth, SEC Form 10-K accession links, and missingness status.
- `HypothesisEvaluationPanel.tsx`: Interactive criteria evaluator allowing live selection of relational operators and thresholds, executing evaluations and rendering supporting vs. contradicting evidence lists.
- `FindingsWorkspace.tsx`: Epistemic findings drawer with create modal, review status badges, limitation inputs, and direct links to underlying calculations.
- `ScenarioSensitivityWorkspace.tsx`: Analyst assumption manager and deterministic what-if sensitivity matrix with interactive slider adjustments and institutional disclaimers.
- `AnalysisProvenanceInspector.tsx`: Audit drawer displaying run metadata, SHA-256 specification hash, versioned formula contracts, and Form 10-K accession manifests.
- `NewAnalysisDialog.tsx`: Modal for configuring entity, metric, frequency, reporting currency, and missing data policies with pre-flight validation.
- `ResearchAnalysisList.tsx`: High-density sidebar list with full-text search, type filtering, and status badges.

---

## 11. Security, Authorization & Roadmap Boundaries

1. **Multi-Tenant Ownership & RLS**: Analyses, runs, findings, and assumptions are strictly bound to authenticated user accounts (`owner_user_id`). Cross-user read or execution attempts return `403 Forbidden`.
2. **Zero Code Injection**: The `SafeExpressionEvaluator` rejects Python builtins, imports, and arbitrary SQL/shell executions.
3. **Zero Automated Trading / Broker Execution**: Research Analysis is strictly an analytical and epistemic workbench. Prohibited from executing broker trades, altering client portfolios, or generating automated BUY/SELL order recommendations.
4. **Zero Fabrication Policy**: Synthetic companies, fake peer rankings, and unverified economic observations are strictly prohibited. Missing observations are qualified explicitly rather than coerced to zero.
5. **Roadmap Boundary**: Stage 106 is complete. Stage 107 remains strictly deferred.
