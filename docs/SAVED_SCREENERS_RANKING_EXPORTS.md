# ATLAS Stage 97: Institutional-Grade Saved Screeners, Advanced Multi-Column Sorting, Quantitative Factor Rankings and Professional Financial Data Export System

## 1. Executive Summary & Canonical Roadmap Alignment
Stage 97 builds upon the foundational Screener Engine (Stage 94), Visual Filter Builder (Stage 95), and Multi-Factor Screening Engine (Stage 96) to establish a persistent, reproducible, and institutional research workflow within `/screeners`.

This stage delivers four mission-critical subsystems:
1. **Saved Screeners**: User-owned, tenant-isolated persistent screening configurations with UUID primary keys, optimistic concurrency revision protection (`expected_revision`), schema versioning (`1.0.0`), and Filter/Universe Registry compatibility.
2. **Advanced Multi-Column Sorting**: Deterministic server-side evaluation of up to 5 typed sort keys with direction (`ASC`, `DESC`), null ordering (`NULLS_LAST`, `NULLS_FIRST`), currency and reporting period compatibility, and immutable security identifier tie-breaking.
3. **Quantitative Factor Ranking Engine**: Cross-sectional factor evaluation supporting both single-factor rankings and multi-factor weighted composite scoring, sample size $N$ disclosure, strict complete-case missingness exclusion (zero imputation strictly prohibited), tie policies (`DENSE_RANK`, `COMPETITION_RANK`), cross-sectional percentiles ($0.0\%$ to $100.0\%$), and standardized sample Z-scores ($z = (x - \mu)/\sigma$, zero-variance $\sigma=0 \to z=0.0$).
4. **Professional Financial Data Export System**: Secure, licensed, reproducible dataset generation supporting machine-readable CSV (RFC 4180 / UTF-8) and multi-sheet Excel Workbooks (`Results`, `Methodology`, `Sources`, `Configuration`), spreadsheet formula-injection mitigation, background asynchronous export jobs, and time-limited authenticated downloads.

---

## 2. Distinct Domain Objects Architecture
A core architectural requirement of Stage 97 is the strict ontological separation of four distinct domain entities:
1. **Saved Screener (`SavedScreener`)**: A durable, versioned user-owned specification of *what* conditions, universe scopes, display columns, sorting keys, and quantitative rankings to evaluate. It is **not** a frozen list of tickers.
2. **Screening Execution (`ScreenerRunResponse`)**: An ephemeral or recorded evaluation of a screener specification against current market and fundamental source data as of an explicit point-in-time timestamp (`evaluated_as_of`).
3. **Ranking Evaluation (`ScreenerRankingResponse`)**: A statistical derivation assigning ordinal ranks, percentiles, or composite Z-scores across a precisely defined eligible candidate cohort.
4. **Export Artifact (`ScreenerExportJob` / `ScreenerExportArtifact`)**: A licensed, bounded, and format-specific data payload generated against a specific evaluated snapshot.

```
                    ATLAS SCREENER WORKSPACE (/screeners)
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
   [SAVED SCREEN STORE]                               [SCREENER ENGINE]
   • User Ownership (Tenant RLS)                      • Universe Scope
   • Monotonic Revision Token                         • Filter Predicates
   • Query Schema Version (1.0.0)                     • Authorized Data Sources
            │                                                   │
            └─────────────────────────┬─────────────────────────┘
                                      ▼
                        [EVALUATED MATCHING POPULATION]
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
   [ADVANCED MULTI-SORT]                              [FACTOR RANKING ENGINE]
   • Up to 5 Typed Keys                               • Cohort Eligibility
   • Direction: ASC / DESC                            • Single & Composite Z-Score
   • Nulls: NULLS_LAST / FIRST                        • Sample N Disclosure
   • Immutable Final Tie-Breaker                      • Complete-Case Exclusion
            │                                                   │
            └─────────────────────────┬─────────────────────────┘
                                      ▼
                          [STABLE PAGINATED GRID]
                                      │
                                      ▼
                           [SECURE EXPORT SUBSYSTEM]
                           • CSV (RFC 4180 / UTF-8)
                           • XLSX Multi-Sheet Workbooks
                           • Spreadsheet Injection Defense
                           • Background Asynchronous Jobs
                           • Time-Limited Authorized Downloads
```

---

## 3. Saved Screener Domain Model & Optimistic Concurrency

### 3.1 Entity Schema
Every saved screen is stored with strict typing and tenant isolation:
- `saved_screen_id`: Immutable UUID string.
- `owner_user_id`: Authenticated user UUID enforcing row-level security.
- `name`: Human-readable identifier (1 to 120 characters, trimmed).
- `description`: Optional thesis and strategy summary (max 1,000 characters).
- `query_schema_version`: String literal `"1.0.0"`.
- `universe`: `UniverseSelection` containing `universe_id`, `exchange_mics`, `listing_country_codes`, `sectors`.
- `filters`: Array of canonical `FilterCriterion` objects.
- `columns`: Array of visible column identifier strings.
- `sort`: Array of `SortCriterion` objects.
- `ranking`: Optional `ScreenerRankingSpec` object.
- `period_policy`: Reporting policy string (e.g. `"latest_annual"`, `"latest_quarter"`).
- `currency_policy`: Financial currency policy string (e.g. `"USD"`, `"native"`).
- `revision`: Monotonically increasing positive integer (`1, 2, 3...`).
- `status`: Lifecycle state (`"active"`, `"archived"`, `"deleted"`).
- `created_at` / `updated_at`: Server-generated ISO-8601 UTC timestamps.
- `last_executed_at`: Timestamp of latest explicit rerun.

### 3.2 Optimistic Concurrency & Revision Protection
When updating an existing saved screener, the client must supply `expected_revision`.
If the database record has been modified by a concurrent browser session or background process, a `409 Conflict` (`SavedScreenerConflictError`) is raised. The frontend informs the analyst and provides options to save as a new copy or reload the latest server state without silent data loss.

### 3.3 Quotas & Limitations
- Maximum 100 active saved screeners per authenticated user account.
- Name length: 1 to 120 characters.
- Description length: Up to 1,000 characters.

---

## 4. Advanced Multi-Column Sorting Engine

### 4.1 Specification
Sorting operates globally across all matching securities server-side prior to pagination:
- Maximum 5 sorting keys.
- `field_id`: Column or metric identifier.
- `direction`: `"desc"` (descending) or `"asc"` (ascending).
- `null_order`: `"nulls_last"` (default for financial metrics) or `"nulls_first"`.

### 4.2 Deterministic Evaluation & Tie-Breaking
1. Rows are sorted sequentially by Sort Rule 1, then Sort Rule 2, ..., Sort Rule $K$.
2. For numeric fields, comparison evaluates raw numeric floats/doubles (not locale-formatted strings).
3. If two securities have identical values across all user-specified sort keys, an immutable final tie-breaker is appended:
   ```python
   (row.instrument_entity_id, row.listing_id)
   ```
   This guarantees absolute cursor pagination stability and prevents duplicate or omitted rows across paginated views.

---

## 5. Quantitative Factor Ranking Engine

### 5.1 Principles & Guardrails
- **No Investment Recommendations**: Factor scores indicate relative statistical positions within a defined cohort. They are never labeled as "Buy/Sell" recommendations or "Guaranteed Alpha".
- **Transparent Cohorts**: Evaluated population is explicit: `FILTER_MATCHED_SECURITIES` (subset meeting filter criteria) or `ALL_ELIGIBLE_UNIVERSE` (entire active universe).
- **Strict Complete-Case Missingness Exclusion**: Securities missing any required factor observation are excluded from that ranking calculation. Zero imputation (e.g. assuming missing P/E is 0) is strictly forbidden.
- **Sample Size Disclosure**: Sample $N$, eligible count, and excluded count are prominently returned.

### 5.2 Mathematical Methodologies
1. **Factor Orientation**:
   - `HIGHER_VALUE_FIRST`: Higher numeric values receive better rank (Rank 1).
   - `LOWER_VALUE_FIRST`: Lower numeric values receive better rank (Rank 1) (e.g. Valuation multiples, Historical Volatility).
2. **Tie Assignment**:
   - `DENSE_RANK`: Ranks are consecutive integers without gaps ($1, 2, 2, 3$).
   - `COMPETITION_RANK`: Tied items share rank, skipping subsequent integers ($1, 2, 2, 4$).
3. **Cross-Sectional Percentile**:
   $$\text{Percentile}_i = \frac{N - \text{Rank}_i}{N - 1} \times 100.0\%$$
   Bounded between $0.0\%$ (worst) and $100.0\%$ (best).
4. **Standardized Sample Z-Scores**:
   $$z_i = \frac{x_i - \mu}{\sigma}$$
   where $\mu$ is the cohort sample mean and $\sigma$ is sample standard deviation ($N - 1$ degrees of freedom).
   - **Zero-Variance Protection**: If all observations are identical ($\sigma = 0.0$), $z_i = 0.0$ for all securities to prevent division-by-zero errors.
5. **Weighted Composite Scoring**:
   $$\text{CompositeScore}_i = \sum_{j=1}^{M} w_j \cdot z_{ij}$$
   where weights are strictly positive and normalized:
   $$\sum_{j=1}^{M} w_j = 1.0$$

---

## 6. Financial Data Export Architecture

### 6.1 Supported Formats & Workbooks
1. **CSV (RFC 4180 / UTF-8)**: Machine-readable comma-delimited format with deterministic column headers.
2. **Excel (.xlsx)**: Institutional multi-sheet workbook:
   - **`Results` Sheet**: Filtered matching securities, ticker symbols, company names, currency, and metric columns.
   - **`Methodology` Sheet**: Mathematical formulas, ranking parameters, tie policies, and sample statistics.
   - **`Sources` Sheet**: Source attribution, provider provenance, and observation timestamps.
   - **`Configuration` Sheet**: Query JSON specification, universe metadata, filter criteria, and query schema version.

### 6.2 Spreadsheet Formula-Injection Defense
Untrusted textual content (e.g. company names, descriptions, free-text attributes) that could be interpreted by spreadsheet engines (Microsoft Excel, LibreOffice Calc, Google Sheets) as dynamic formulas is neutralized:
- Any text starting with `=, +, -, @, \t, \r` is prefixed with an apostrophe (`'`).
- Valid numeric primitives (including negative numbers like `-14.5%` or negative EPS) remain native numeric cells and are **never** corrupted.
- Ticker symbols and leading-zero alphanumeric identifiers are explicitly formatted as Text cells to prevent unintended numeric truncation.

### 6.3 Background Export Jobs
- **Synchronous Threshold**: Requests under 1,000 rows complete synchronously within the request lifecycle.
- **Asynchronous Processing**: Requests exceeding 1,000 rows (up to 50,000 max quota) generate background jobs with durable statuses (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`, `EXPIRED`).
- **Storage & Retention**: Artifacts are stored in private local object/file storage (`artifacts/exports/`). Files automatically expire and are purged after 24 hours. Downloads require authenticated bearer authorization.

---

## 7. HTTP API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/screeners/saved` | List authenticated user's saved screeners with search and pagination |
| `POST` | `/api/v1/screeners/saved` | Create a new persistent saved screener strategy |
| `GET` | `/api/v1/screeners/saved/{id}` | Retrieve details of an owned saved screener |
| `PUT` | `/api/v1/screeners/saved/{id}` | Update saved screener with optimistic concurrency verification |
| `DELETE` | `/api/v1/screeners/saved/{id}` | Soft-delete owned saved screener |
| `POST` | `/api/v1/screeners/saved/{id}/duplicate` | Clone owned screener with new UUID identity |
| `POST` | `/api/v1/screeners/saved/{id}/run` | Execute saved screener query against latest market data |
| `POST` | `/api/v1/screeners/ranking/evaluate` | Standalone quantitative factor ranking evaluation |
| `POST` | `/api/v1/screeners/exports` | Request dataset export (CSV / XLSX) |
| `GET` | `/api/v1/screeners/exports` | List recent export jobs for authenticated user |
| `GET` | `/api/v1/screeners/exports/{id}` | Check status and progress of export job |
| `POST` | `/api/v1/screeners/exports/{id}/cancel` | Cancel queued or running export job |
| `GET` | `/api/v1/screeners/exports/{id}/download` | Stream authorized file download |

---

## 8. Verification & Quality Gates

### 8.1 Backend Verification
- Unit & integration tests in `apps/api/tests/test_screener_saved_and_ranking.py`: **12 passed**
- Full screener regression suite (`test_screeners.py`, `test_screener_visual_builder.py`, `test_screener_advanced_factors.py`, `test_screener_saved_and_ranking.py`): **66 passed**
- Static linting with `ruff check`: **0 errors (All checks passed)**

### 8.2 Frontend Verification
- Unit test suite `apps/web/src/lib/screeners/__tests__/stage97_saved_ranking_exports.test.ts`: **5 passed (21 total passing in screener frontend suite)**
- TypeScript strict typecheck (`npx tsc --noEmit`): **0 errors**
- Production build (`npm run build`): **Compiled and built successfully (all 38 routes)**

---

## 9. Canonical Roadmap Boundary (Stage 97 vs Stage 98)
Stage 97 is strictly bounded. The following are deferred to Stage 98 and later stages:
- **Natural Language Translation**: Stage 98 owns free-text and conversational screening translation hooks. Stage 97 requires exactly 0 LLM calls.
- **Universal Saved Platform**: Stage 119 owns general cross-module bookmarks and global collections.
- **Workspaces & Collaboration**: Stage 120 owns multi-user collaboration and shared workspaces.
- **Autonomous Monitoring & Alerts**: Automated periodic screen scans and trade entry notifications are deferred to later monitoring stages.
- **Backtesting & Order Execution**: Stages 143–145 own Backtesting, Paper Trading, and Broker Execution. Stage 97 performs no portfolio mutations.
