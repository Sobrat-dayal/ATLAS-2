# Visual Screener Filter Builder Subsystem (Stage 95)

## 1. Overview & Architectural Role

The **Visual Screener Filter Builder** transforms the foundational screening engine established in Stage 94 into an institutional-grade, highly interactive, visually structured financial filter construction experience.

- **Primary Route**: `/screeners`
- **Canonical Stage**: 95 / 150
- **Architectural Role**: Presentation, validation, and typed query-construction interface over the canonical Stage 94 Screener Engine.
- **Authoritative Engine**: Stage 94 (`atlas.screeners`) remains the single source of truth for universe scoping, filter semantics, sorting, pagination, and execution.

---

## 2. Component Architecture

The visual builder subsystem is organized into modular components under `apps/web/src/components/screeners/visual-builder/`:

```
apps/web/src/components/screeners/visual-builder/
├── VisualScreenerBuilder.tsx       # Main builder workspace coordinating catalog, canvas, and toolbar
├── FilterLibrary.tsx               # Searchable metric catalog with category tabs and alias matching
├── ActiveConditionCanvas.tsx       # Main condition canvas with visual AND connectors & category cards
├── VisualConditionRow.tsx          # Condition row with metric selector, operator selector, and typed editor
├── VisualBuilderToolbar.tsx        # Action bar: Apply, Discard, Clear, Review Logic, Dirty badge
├── FilterDefinitionInspector.tsx   # Modal inspecting metric formula, methodology, and provenance
├── VisualQueryPreview.tsx          # Plain-English query transparency modal ("Review Logic")
└── editors/
    ├── DecimalFilterInput.tsx      # Exact decimal text entry with intermediate typing tolerance
    ├── MonetaryFilterInput.tsx     # Amount, currency selector (USD/EUR/GBP/INR/JPY), magnitude (K/M/B/T)
    ├── PercentageFilterInput.tsx   # Human-friendly percentage (%) and valuation multiple (x) controls
    ├── RangeFilterInput.tsx        # Lower and upper bound text inputs with boundary validation
    └── EnumFilterSelect.tsx        # Searchable multi-select popover for exchanges, countries, sectors
```

---

## 3. Supported Filter Categories & Typed Control Mappings

The canonical Stage 94 Filter Registry contains 26 source-backed financial filters mapped to typed visual editors:

| Category | Filter ID | Metric Name | Value Type | Unit Kind | Visual Editor |
|---|---|---|---|---|---|
| **Market Data** | `market_cap` | Market Capitalization | CURRENCY | MONETARY | `MonetaryFilterInput` |
| **Market Data** | `last_price` | Last Traded Price | CURRENCY | MONETARY | `MonetaryFilterInput` |
| **Market Data** | `price_change_pct` | Price Change % | PERCENTAGE | PERCENT | `PercentageFilterInput` |
| **Market Data** | `volume_latest` | Session Volume | INTEGER | SHARES | `DecimalFilterInput` |
| **Market Data** | `volume_20d_avg` | Average Daily Volume (20d) | INTEGER | SHARES | `DecimalFilterInput` |
| **Market Data** | `traded_value_latest` | Daily Traded Value / Turnover | CURRENCY | MONETARY | `MonetaryFilterInput` |
| **Fundamentals** | `revenue` | Revenue | CURRENCY | MONETARY | `MonetaryFilterInput` |
| **Fundamentals** | `net_income` | Net Income | CURRENCY | MONETARY | `MonetaryFilterInput` |
| **Fundamentals** | `operating_income` | Operating Income (EBIT) | CURRENCY | MONETARY | `MonetaryFilterInput` |
| **Fundamentals** | `total_assets` | Total Assets | CURRENCY | MONETARY | `MonetaryFilterInput` |
| **Fundamentals** | `book_equity` | Shareholders' Equity | CURRENCY | MONETARY | `MonetaryFilterInput` |
| **Fundamentals** | `eps` | Diluted Earnings Per Share | NUMERIC | CURRENCY_PER_SHARE | `DecimalFilterInput` |
| **Valuation** | `pe_ratio` | P/E Ratio (Trailing) | NUMERIC | MULTIPLE | `PercentageFilterInput` |
| **Valuation** | `pb_ratio` | P/B Ratio | NUMERIC | MULTIPLE | `PercentageFilterInput` |
| **Valuation** | `ps_ratio` | P/S Ratio | NUMERIC | MULTIPLE | `PercentageFilterInput` |
| **Valuation** | `dividend_yield` | Dividend Yield % | PERCENTAGE | PERCENT | `PercentageFilterInput` |
| **Profitability** | `gross_margin` | Gross Profit Margin % | PERCENTAGE | PERCENT | `PercentageFilterInput` |
| **Profitability** | `operating_margin` | Operating Profit Margin % | PERCENTAGE | PERCENT | `PercentageFilterInput` |
| **Profitability** | `net_margin` | Net Profit Margin % | PERCENTAGE | PERCENT | `PercentageFilterInput` |
| **Profitability** | `roe` | Return on Equity (ROE) % | PERCENTAGE | PERCENT | `PercentageFilterInput` |
| **Profitability** | `roa` | Return on Assets (ROA) % | PERCENTAGE | PERCENT | `PercentageFilterInput` |
| **Industry** | `sector` | Sector | ENUM | DIMENSIONLESS | `EnumFilterSelect` |
| **Industry** | `industry` | Industry Group | ENUM | DIMENSIONLESS | `EnumFilterSelect` |
| **Listing** | `exchange_mic` | Exchange (MIC) | ENUM | DIMENSIONLESS | `EnumFilterSelect` |
| **Geography** | `listing_country_code` | Listing Country Code | ENUM | DIMENSIONLESS | `EnumFilterSelect` |
| **Geography** | `issuer_country_code` | Issuer Domicile Country Code | ENUM | DIMENSIONLESS | `EnumFilterSelect` |

---

## 4. Condition Identity & Predicate Construction

- **Stable Client Condition Identity**: Each condition row possesses a unique, stable client-side `conditionId` (e.g. `cond-1730000000-abcde`), independent of the `filterId`. This ensures editing, duplicating, and removing condition rows does not cause React component key corruption or loss of focus.
- **Multiple Conditions on Same Metric**: Users can legitimately construct bounding brackets on the same metric (e.g. `Price >= $50` AND `Price <= $150`).
- **Initial Operator & Default Shapes**: Newly added filters instantiate with sensible registry-defined default operators (e.g. `GTE` for market cap and price, `LTE` for P/E and P/B, `IN` for sectors and exchanges).
- **Empty & Intermediate Input States**: Empty inputs are classified as `incomplete` draft states rather than fatal errors or zeros. Intermediate typing sequences (`-`, `12.`) are preserved during editing without premature validation failure.

---

## 5. Two-Layer Validation & Contradiction Detection

Validation operates in two complementary layers:

### Layer 1: Client-Side Interactive Validation (`apps/web/src/lib/screeners/validation.ts`)
1. **Precision & Number Safety**: Rejects non-finite values (`NaN`, `Infinity`, `-Infinity`). Preserves exact string representation.
2. **Range Boundary Validation**: Enforces that for `BETWEEN` operators, the lower bound does not exceed the upper bound.
3. **Condition Limits**: Enforces the canonical budget limit of 20 active filters.
4. **Universe Dependency Checks**: Cross-references metric `eligible_security_types` against the selected universe's allowed security types, generating informative notices if incompatible.
5. **Deterministic Contradiction Detection (`contradictions.ts`)**:
   - Detects when separate numeric bounds form an empty solution set (e.g. `Price > $200` AND `Price < $100`).
   - Detects unsatisfiable strict inequalities on identical boundaries (e.g. `Price > $100` AND `Price < $100`).
   - Detects conflicting equality constraints on single-valued classifications (e.g. `sector == 'Technology'` AND `sector == 'Healthcare'`).

### Layer 2: Server-Side Authoritative Validation (`/api/v1/screeners/validate`)
The FastAPI backend authoritative service validates:
- Approved filter registry membership.
- Operator allowlisting per metric.
- Decimal parsing and non-finite number rejection.
- Range bound ordering.
- Contradiction detection across accumulated boundaries.
- Returns condition-specific attribution issues (`ConditionValidationIssueDTO`) with `condition_id`, `field_path`, `code`, `severity`, and `message`.

---

## 6. Draft vs Applied Query State Management

The Visual Builder maintains strict separation between query editing and query execution:

1. **Draft Query (`draftConditions`)**: Represents the active editing state in the visual builder canvas.
2. **Applied Query (`appliedConditions`)**: Represents the exact query specification that produced the currently rendered results table.
3. **Dirty Indicator**: When draft conditions differ from applied conditions, an institutional `Changes not applied` badge is displayed.
4. **Primary Actions**:
   - **Apply Filters**: Validates client state, serializes conditions into canonical `FilterCriterionDTO[]`, executes the screener query via `/api/v1/screeners/run`, and atomically updates applied state.
   - **Discard Changes**: Reverts draft conditions to match the last successfully applied query.
   - **Clear All**: Clears active draft conditions cleanly.
5. **Request Race Protection**: In-flight requests are cancelled using `AbortController` when superseded. Late responses from obsolete requests are discarded, ensuring old query results never overwrite newer results.

---

## 7. Query Transparency & URL State Synchronization

### Query Review ("Review Logic")
The plain-English query transparency panel (`VisualQueryPreview.tsx`) generates an unambiguous institutional summary:
- Selected investment universe and eligibility scope.
- Explicit conjunction (`WHERE ... AND ... AND ...`).
- Human-readable numbers, scale factors (`BILLIONS`), and currencies (`USD`).
- Disclosed reporting period policy and currency conversion basis.

### URL State Synchronization (`url-state.ts`)
- Bounded query parameter encoding (`?filters=...`).
- Versioned payload format (`v: 1`).
- Reconstructs visual conditions upon URL load, validating each filter ID and operator against the active registry.
- Unrecognized or manipulated parameters are rejected with explicit warnings rather than crashing the workspace.

---

## 8. Terminal Ergonomics & Accessibility

- **Bloomberg-Inspired Institutional UX**: Compact cards, dark theme surfaces, fine borders (`border-border/60`), tabular monospace numerals for financial values.
- **Full Keyboard Navigation**:
  - Global metric search input with instant focus.
  - Arrow key navigation across metric options.
  - Enter to add filter condition.
  - Escape to dismiss inspector and review logic modals.
- **Screen-Reader Accessibility**: Explicit `aria-label` on all inputs, operators, magnitude toggles, and remove actions. Field-level validation messages programmatically linked.
- **Responsive Layout**: Operates cleanly from desktop (1920px), through tablet (768px), down to compact mobile viewport (320px).

---

## 9. Verification & Automated Test Coverage

The Visual Screener Filter Builder is backed by comprehensive automated test suites:

- **Backend Tests (`apps/api/tests/test_screener_visual_builder.py` + `test_screeners.py`)**:
  - 35 passed tests verifying presentation metadata, condition issue attribution, contradiction detection, and universe dependency validation.
- **Frontend Tests (`apps/web/src/lib/screeners/__tests__/visual-builder.test.ts`)**:
  - 13 passed tests verifying magnitude multipliers, client validation, contradiction detection, query review generation, and URL state round-tripping.
- **TypeScript Typecheck**: `tsc --noEmit` clean (0 errors).
- **Production Build**: `next build` clean (all 38 routes rendered successfully).

---

## 10. Roadmap Boundaries

| Stage | Responsibility | Status |
|---|---|---|
| **94** | Financial Screeners V1 — common screening dataset and query engine | **Completed** |
| **95** | **Visual Screener Filters — visual query builder, typed controls, validation, transparency** | **Completed** |
| **96** | Fundamental, technical, and multi-factor screening expansion | **Deferred to Stage 96** |
| **97** | Saved screens, sorting, ranking, and exports | **Deferred to Stage 97** |
| **98** | Natural-language screener translation hooks | **Deferred to Stage 98** |
