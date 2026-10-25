# Institutional Company Financial Statements Architecture (Stage 82)

## 1. Executive Summary & Principles

Stage 82 establishes institutional-grade corporate financial statements within the ATLAS `/companies` module.
It transforms the Companies workspace into a professional financial terminal environment where users examine genuine corporate financial statements across reporting periods, inspect standardized accounting taxonomies, analyze multi-period historical comparisons, observe financial restatements, examine derived Trailing-Twelve-Month (TTM) views, and verify point-in-time source provenance.

### Core Architectural Principle
A financial statement is a time-bounded, source-qualified collection of accounting facts associated with a specific reporting entity, accounting framework, fiscal period, consolidation scope, unit, and reporting basis.

All financial observations originate from authoritative, canonical datasets (Stage 34 Fundamental Store). ATLAS strictly prohibits:
- Fictitious financial statements or mock accounting figures.
- Conflating cumulative Year-To-Date (YTD) disclosures with standalone quarters.
- Fabricating TTM values by multiplying one quarter by four ($Q \times 4$).
- Summing Balance Sheet stock positions across quarters to manufacture synthetic balances.
- Subtracting per-share figures or EPS naively without proper denominator weighting.
- Combining incompatible reporting currencies, consolidation scopes, or accounting frameworks without explicit disclosure.
- Substituting zero for missing financial facts.

---

## 2. Core Statement Types

ATLAS supports the three fundamental corporate financial statements:
1. **Income Statement (`income_statement`)**: Measures financial performance over a reporting flow period (Revenue, Cost of Revenue, Gross Profit, Operating Expenses, Operating Income, Pretax Income, Tax Expense, Net Income, and Basic/Diluted EPS).
2. **Balance Sheet (`balance_sheet`)**: Measures point-in-time financial position at period end (Current Assets, Non-Current Assets, Total Assets, Current Liabilities, Non-Current Liabilities, Total Liabilities, Shareholders' Equity, and Noncontrolling Interests).
3. **Cash Flow Statement (`cash_flow_statement`)**: Measures cash generation and utilization across flow periods (Operating Activities, Investing Activities, Financing Activities, FX translation effects, Net Change in Cash, Beginning Cash, and Ending Cash).

---

## 3. Reporting Entity & Scope Resolution

### 3.1 Entity Identity vs Reporting Entity
A company's canonical identity is defined by its immutable `entity_id` UUID from Stage 18/81. However, corporate reporting structures frequently distinguish between parent corporations, separate operating subsidiaries, and consolidated groups.
Statements explicitly declare:
- `company_entity_id`: Canonical issuer UUID.
- `reporting_entity_id`: Specific filing/reporting legal entity UUID.
- `consolidation_scope`:
  - `CONSOLIDATED`: Aggregates parent and controlled subsidiary entities according to applicable accounting standards.
  - `STANDALONE`: Reflects the distinct legal corporate entity without subsidiary consolidation.

---

## 4. Standardized Accounting Taxonomy & Concept Hierarchy

### 4.1 Concept Registry & Stability
Every canonical statement line item uses a typed, stable `concept_id` (`ConceptHierarchyNode`).
- Income Statement: `revenue`, `product_revenue`, `service_revenue`, `cost_of_revenue`, `gross_profit`, `operating_expenses`, `research_and_development`, `selling_general_and_administrative`, `operating_income`, `interest_income`, `interest_expense`, `income_before_tax`, `income_tax_expense`, `net_income`, `basic_eps`, `diluted_eps`, `weighted_average_shares_diluted`.
- Balance Sheet: `cash_and_cash_equivalents`, `short_term_investments`, `accounts_receivable`, `inventory`, `current_assets`, `property_plant_equipment_net`, `non_current_assets`, `total_assets`, `accounts_payable`, `short_term_debt`, `current_liabilities`, `long_term_debt`, `non_current_liabilities`, `total_liabilities`, `common_stock`, `retained_earnings`, `total_equity`, `total_liabilities_and_equity`.
- Cash Flow Statement: `operating_activities`, `net_income_cash_flow`, `depreciation_and_amortization`, `stock_based_compensation`, `changes_in_working_capital`, `operating_cash_flow`, `capital_expenditures`, `investing_cash_flow`, `financing_cash_flow`, `debt_repayment`, `dividends_paid`, `share_repurchases`, `net_change_in_cash`, `cash_at_beginning_of_period`, `ending_cash_balance`.

### 4.2 Preservation of Original Reported Concepts
Standardized rows preserve original reported concepts and labels (`original_concept`, `original_label`). If a reported item cannot be mapped with certainty, it is retained as an unmapped item rather than coerced into an invalid classification.

---

## 5. Fiscal Period & Calendar Model

### 5.1 Period Types
- `ANNUAL`: Full fiscal year flows (typically 12 months, or 52/53 weeks).
- `QUARTERLY`: Three-month standalone flow period or quarter-end stock balance.
- `TTM`: Trailing-Twelve-Months derived sum of four consecutive standalone quarters.
- `SEMIANNUAL`: Six-month reporting period (common in international jurisdictions).
- `NINE_MONTH`: Nine-month cumulative YTD flow.

### 5.2 Non-Calendar Fiscal Years
Companies with non-calendar fiscal year-ends (e.g. Apple Inc. ending in late September, Microsoft ending in June, retail companies on 52/53-week 4-5-4 retail calendars) are indexed by their authoritative fiscal year and fiscal quarter rather than assumed calendar quarters.

---

## 6. Standalone Quarter Derivation

Where companies report cumulative Year-To-Date (YTD) numbers in 10-Q filings:
- **First Quarter**: $Q_1 = YTD_1$.
- **Second Quarter**: $Q_2 = YTD_2 - YTD_1$.
- **Third Quarter**: $Q_3 = YTD_3 - YTD_2$.
- **Fourth Quarter**: $Q_4 = FY - YTD_3$.

Derivations require verified compatibility across entity UUID, fiscal year, consolidation scope, reporting currency, and restatement revisions.
- Strictly prohibited: Deriving Balance Sheet values by subtracting periods (Balance Sheet facts are instant stock measures).
- Strictly prohibited: Subtracting per-share EPS figures without reconciling weighted shares.

---

## 7. Trailing-Twelve-Month (TTM) View

### 7.1 Flow Summation
For flow measures (Income Statement and Cash Flow Statement), TTM is calculated strictly when four consecutive, non-overlapping, standalone quarters are available:
$$TTM = \sum_{i=0}^3 Q_{t-i}$$
Or via the annual/YTD bridge:
$$TTM = FY_{previous} + YTD_{current} - YTD_{prior}$$

### 7.2 Strict Prohibitions
- NEVER calculate TTM by multiplying the latest quarter by four ($Q \times 4$).
- NEVER sum quarterly Balance Sheet balances to manufacture a TTM Balance Sheet. If requested, the API returns a 400 error and the UI disables the selector with an explanatory tooltip.

---

## 8. Precision, Scaling & Financial Formatting

### 8.1 Exact Decimal Storage
Authoritative accounting numbers are stored and calculated using exact Python `Decimal` objects (or string equivalents in JSON) to eliminate binary floating-point rounding errors.

### 8.2 Financial Formatting Conventions
- Negative values: Formatted in financial accounting parentheses, e.g. `(123.45)`.
- Zero vs Missing: Exact reported zero is formatted as `0.00`; missing/unreported facts are rendered as `—` (em-dash) with an accessible explanation.
- Per-share & share count scaling: Currency scaling (`billions`, `millions`) applies to aggregate monetary items only. EPS is kept in exact currency units (e.g. `$6.08`), and share counts are formatted in unit shares or millions of shares (`15,408.00M`).

---

## 9. Restatements, Revisions & Provenance

When companies amend prior filings, ATLAS tracks both versions:
- `is_restated`: Boolean indicating whether a period was amended.
- `revision_id`: Version of the data point.
- `source_document_id` & `source_filing_name`: Reference to the official SEC 10-K, 10-Q, or 8-K filing.
- Point-in-time data integrity: Future revisions published later are never backdated into historical snapshots without proper availability timestamps.

---

## 10. Historical Comparisons & Common-Size Analysis

### 10.1 Comparative Metrics
- **YoY Absolute Change**: $Current - PriorYear$.
- **YoY Percentage Change**: $\frac{Current - Prior}{|Prior|} \times 100$.
- **QoQ Absolute & Percentage Changes**: For standalone quarterly flows.
- **Negative / Zero Baselines**: When the base period value is non-positive, percentage calculations return `N/M` (Not Meaningful) to prevent misleading signs.

### 10.2 Common-Size Statement Presentation
- Income Statement: Expresses all line items as a percentage of `revenue`.
- Balance Sheet: Expresses all line items as a percentage of `total_assets`.

---

## 11. Accounting Consistency Diagnostics

Statement reads perform diagnostic evaluations without mutating source facts:
- **Balance Sheet Identity**: $Assets = Liabilities + Equity$.
  Evaluates difference $Assets - (Liabilities + Equity)$ against authorized rounding tolerances ($1,000 or 0.05% of Total Assets).
- **Cash Flow Reconciliation**:
  $Operating + Investing + Financing + FX \approx Net\ Change\ in\ Cash$
  $Beginning\ Cash + Net\ Change = Ending\ Cash$.
- Statuses: `CONSISTENT`, `WITHIN_ROUNDING_TOLERANCE`, `REQUIRES_REVIEW`, `INCOMPLETE`.

---

## 12. API Reference

All endpoints are hosted under `/api/v1/companies/{company_id}/statements`:
- `GET /catalog`: Available statements, fiscal years, quarters, scopes, and currencies.
- `GET /income`: Multi-period Income Statement.
- `GET /balance-sheet`: Multi-period Balance Sheet (point-in-time stock balances).
- `GET /cash-flow`: Multi-period Cash Flow Statement.
- `GET /{statement_type}`: Generic statement query by type.
- `GET /{statement_type}/sources`: Verified source document references and revision lineages.

---

## 13. Frontend Financial Statements Workspace

Hosted in `/companies/[companyId]` within the `Financial Statements` tab:
- **Tabs**: Income Statement, Balance Sheet, Cash Flow Statement.
- **Toolbar**: Annual / Quarterly / TTM toggle, Scope (Consolidated / Standalone), Scale (Billions, Millions, Thousands, Original, Auto), Comparison Mode (YoY $, YoY %, QoQ $, QoQ %, Common Size %), Expand/Collapse All.
- **Interactive Table**: Sticky line-item label column, sticky period headers, right-aligned numbers with tabular numerals, restatement badges, expand/collapse arrows.
- **Cell Popover**: Exact Decimal value, normalized concept ID, original reported concept, derivation kind, filing document, and restatement status.
- **Diagnostics Card**: Visual indication of Balance Sheet equation reconciliation and Cash Flow arithmetic checks.

---

## 14. Roadmap Boundaries

- **Stage 82 Owns**: Financial Statements, Accounting Taxonomies, Period Derivations, TTM views, Restatements, Diagnostics, and Statement Tables.
- **Deferred to Stage 83**: Comprehensive Financial Ratios (ROE, ROA, ROIC, Current Ratio, Debt/Equity, P/E, EV/EBITDA).
- **Deferred to Stage 84**: Earnings Analytics, EPS surprises, guidance forecasts.
- **Deferred to Stage 85**: Ownership analytics & insider transactions.
- **Deferred to Stage 86**: SEC filing parsers, XBRL ingestion pipelines, filing RAG.
