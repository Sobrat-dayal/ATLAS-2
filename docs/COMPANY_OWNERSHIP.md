# COMPANY OWNERSHIP INTELLIGENCE (STAGE 85)

## Master Architecture & Specification

Institutional-grade Company Ownership Intelligence system inside ATLAS, integrating canonical corporate issuing entities, verified securities and share classes, institutional shareholders, corporate insiders, beneficial owners, shareholding patterns, ownership concentration, voting rights, historical holdings, regulatory disclosure references, and professional shareholder research workspaces.

---

## 1. Executive Summary & Master Directive

ATLAS Stage 85 delivers a comprehensive, financially rigorous, and traceable Company Ownership Intelligence system embedded natively within the existing `/companies` module.

The system allows quantitative researchers, institutional investors, and equity analysts to understand:
- **Who owns a company** and through which legal entities or discretionary accounts;
- **What securities and share classes they own** (e.g. Common Stock, Class A, Class B, Preferred, ADRs);
- **How ownership is reported across regulatory jurisdictions** (SEC Forms 13F, 13D, 13G, Forms 3/4/5; SEBI shareholding patterns);
- **How positions change over time** with corporate-action and split compatibility;
- **What can legitimately be inferred** from underlying disclosures without conflating reporting managers with beneficial owners or transactions with total holdings.

### Strict Non-Negotiable Boundaries:
- **Stage 85 Owns Ownership Intelligence**.
- **Stage 86 Owns Filings** (universal EDGAR crawling, XBRL parsing, full regulatory filing search).
- **Stage 87 Owns Peers**.
- **Stage 88 Owns Supply Chains**.
- **Zero Synthetic Investors**: Never invent holders, share counts, or ownership percentages.
- **Zero Real-Time Conflation**: Disclosed holdings describe historical reporting dates subject to regulatory lags.
- **Zero LLM Calls**: 0 LLM calls for shareholder facts; 0 trading triggers; 0 portfolio mutations.

---

## 2. Canonical Ownership Domain Model

ATLAS models corporate ownership as qualified claims established from specific regulatory disclosures or authoritative datasets at specific dates:

```
                           +----------------------+
                           |   Issuing Company    | (Stage 18 Entity)
                           +----------+-----------+
                                      |
                           +----------v-----------+
                           | Financial Instrument | (Stage 17 Instrument)
                           +----------+-----------+
                                      |
                      +---------------+---------------+
                      |                               |
                      v                               v
           +--------------------+          +--------------------+
           |  OwnershipSnapshot |          |  OwnershipHolder   | (Stage 16 Universal Entity)
           | (Period End Date)  |          | (Manager/Insider)  |
           +----------+---------+          +----------+---------+
                      |                               |
                      +---------------+---------------+
                                      |
                                      v
                          +-----------------------+
                          |   OwnershipPosition   |
                          |  (Reported Holding)   |
                          +-----------+-----------+
                                      |
            +-------------------------+-------------------------+
            |                         |                         |
            v                         v                         v
  +-------------------+     +-------------------+     +-------------------+
  |   Institutional   |     |  Insider Position |     | Beneficial Owner  |
  | (13F Discretion)  |     |  (Section 16(a))  |     | (13D/13G Powers)  |
  +-------------------+     +-------------------+     +-------------------+
```

### 2.1 Distinction Matrix

| Dimension | Distinct Concept A | Distinct Concept B | ATLAS Architectural Rule |
| :--- | :--- | :--- | :--- |
| **Corporate Identity** | Issuing Company Entity | Issued Security / Instrument | A position is held in a specific share class, not merely a ticker string. |
| **Investment Entity** | Investment Manager (Adviser) | Managed Investment Fund | Vanguard Group (manager) is distinct from Vanguard 500 Index Fund. |
| **Legal Status** | Registered / Nominee Owner | Beneficial Economic Owner | Custodians (Cede & Co) are segregated from underlying beneficiaries. |
| **Holding Chain** | Direct Legal Ownership | Indirect / Intermediary Holding | Preserves disclosed entity holding structure without speculative flattening. |
| **Corporate Control** | Economic Ownership % | Voting Power Control % | Dual-class structures (e.g. 10:1 voting rights) maintain separate metrics. |
| **Disclosure Metric** | Absolute Shares Held | Ownership Percentage (%) | Percentages strictly require verified, compatible share-class denominators. |
| **Temporal Event** | Periodic Disclosed Position | Executed Trade Transaction | Form 4 transactions do not reveal total portfolio wealth or non-equity assets. |
| **Timing Lag** | Period As-Of Date | Filing Publication Timestamp | A 13F filing published in November describing September is not backdated to September. |
| **Valuation Basis** | Disclosed Position Value | Current Indicative Market Value | Disclosed values are historical filing facts; market estimates are labeled as of quote time. |

---

## 3. Institutional Holdings (SEC Form 13F)

### 3.1 Regulatory Scope & Semantics
Institutional investment managers exercising investment discretion over $100M+ in Section 13(f) securities file Form 13F quarterly with the US SEC.
- **Reporting Delay**: Filings are due within 45 calendar days following the end of each calendar quarter.
- **Investment Discretion**: The filer reports securities over which it exercises sole or shared investment discretion. It does not establish beneficial ownership for its own corporate balance sheet.
- **Derivative Holdings**: Put and call options are reported as separate contract positions and are **never** summed into common stock equity share counts.
- **Short Positions**: Form 13F does not require short positions. Absence of a holding does not imply a short position.
- **Non-Duplication**: Parent managers and sub-advisers reporting shared discretion are deduplicated to prevent double-counting the same economic shares.

---

## 4. Beneficial Ownership (SEC Schedules 13D & 13G)

### 4.1 SEC Rule 13d-3 Power Classifications
Section 13(d) and 13(g) require disclosures from any person or group that becomes the beneficial owner of more than 5% of a registered equity security class:
- **Sole Voting Power**: Exclusive power to vote or direct the voting of shares.
- **Shared Voting Power**: Shared power with trustees, general partners, or co-advisers to vote shares.
- **Sole Dispositive Power**: Exclusive power to direct the disposition or sale of shares.
- **Shared Dispositive Power**: Shared power to direct the disposition of shares.
- **Schedule 13G**: Passive institutional investors, qualifying brokers, and passive <20% holders.
- **Schedule 13D**: Activist investors or parties acquiring equity with potential control or board influence intent.

---

## 5. Corporate Insiders (SEC Section 16 & Forms 3/4/5)

### 5.1 Reporting Persons
Section 16 applies to corporate directors, named executive officers (CEO, CFO, COO, General Counsel), and principal holders owning more than 10% of any registered class of equity securities:
- **Form 3**: Initial statement of beneficial ownership when becoming an insider.
- **Form 4**: Statement of changes in beneficial ownership, required within 2 business days of transaction.
- **Form 5**: Annual statement of beneficial ownership for exempt or unrecorded transactions.
- **Post-Transaction Holdings**: Certified total holdings remaining after the transaction are preserved. Transactions without disclosed resulting balances are not extrapolated.
- **Personal Privacy Minimization**: Sensitive personal data (residential addresses, telephone numbers, personal emails, SSNs) is strictly excluded.

---

## 6. Shareholding Patterns & Multi-Jurisdiction Coverage

### 6.1 Native Taxonomy Preservation
ATLAS does not force non-US ownership disclosures into artificial US 13F molds:
- **US Equities**: Form 13F Institutional Managers, Section 16 Insiders, and Public Retail Float.
- **Indian Equities (SEBI)**: Promoter & Promoter Group (Indian Promoters, Foreign Promoters, Pledged/Encumbered Shares), Public Institutions (Mutual Funds, FPIs/FIIs, Insurance, Financial Institutions), Public Non-Institutions (Corporate Bodies, Retail Individuals).
- **Pledged Shares**: Preserved as encumbrance metrics without treating pledged shares as executed sales.

---

## 7. Mathematical Formulations & Ownership Arithmetic

All ownership calculations use exact `Decimal` precision with zero-division protection:

### 7.1 Qualified Ownership Percentage
$$\text{Ownership \%} = \left( \frac{\text{Shares Held}}{\text{Compatible Shares Outstanding}} \right) \times 100$$
- If `shares_outstanding <= 0` or missing: returns `None` (unavailable), displaying absolute share count without speculative percentage.
- Denominator must match the identical security identity, share class, and reporting date.

### 7.2 Shares Change
$$\Delta \text{Shares} = \text{Shares}_t - \text{Shares}_{t-1}$$

### 7.3 Relative Position Change Percentage
$$\text{Position Change \%} = \left( \frac{\text{Shares}_t - \text{Shares}_{t-1}}{\text{Shares}_{t-1}} \right) \times 100 \quad (\text{for } \text{Shares}_{t-1} > 0)$$
- New position ($\text{Shares}_{t-1} = 0$): Classified as `NEW_HOLDING` (+100.0%).
- Exited position ($\text{Shares}_t = 0$): Classified as `EXITED` (-100.0%).

### 7.4 Percentage Points Impact
$$\Delta \text{Stake}_{pp} = \text{Ownership \%}_t - \text{Ownership \%}_{t-1}$$

### 7.5 Concentration Metrics
- **Top 1 Stake %**: Largest verified disclosed shareholder.
- **Top 5 Stake %**: Sum of top 5 non-duplicated disclosed holders over shares outstanding.
- **Top 10 Stake %**: Sum of top 10 non-duplicated disclosed holders over shares outstanding.
- **Disclosed Sample %**: Total shares in the current disclosure dataset over shares outstanding.

---

## 8. REST API Specification

Mounted under `/api/v1/companies/{company_id}/ownership`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/overview` | Executive ownership summary, top 10 holders, concentration, and pattern preview |
| `GET` | `/securities` | List eligible securities and share classes with canonical shares outstanding |
| `GET` | `/holders` | Verified reported holders with pagination, sorting, and category filters |
| `GET` | `/institutions` | Form 13F institutional manager holdings, indicative values, and quarterly changes |
| `GET` | `/insiders` | Form 4 corporate insider positions, roles, governance tags, and changes |
| `GET` | `/beneficial` | Schedule 13D/13G beneficial owners with voting and dispositive power breakdowns |
| `GET` | `/patterns` | Jurisdiction-specific macro shareholding pattern distribution and pledged shares |
| `GET` | `/history` | Historical multi-quarter ownership snapshots and concentration trajectory |
| `GET` | `/changes` | Comparative position adjustments between historical quarters |

---

## 9. Frontend Architecture (`apps/web`)

Integrated into `/companies` workspace:

```
apps/web/src/
|
+-- lib/companies/ownership/
|    +-- types.ts           # Strongly typed DTO interfaces
|    +-- api.ts             # Authenticated REST client
|    +-- index.ts           # Barrel export
|
+-- hooks/companies/
|    +-- useCompanyOwnership.ts  # Reactive multi-subtab state management hook
|
+-- components/companies/ownership/
     +-- OwnershipWorkspace.tsx         # Primary container with security & period selectors
     +-- OwnershipOverviewCards.tsx     # Executive metrics (Top 1, Top 5, Float, Denominator)
     +-- InstitutionalHoldersTable.tsx  # Dense terminal table of 13F asset managers
     +-- InsiderHoldingsTable.tsx       # Corporate officers & directors with Form 4 details
     +-- BeneficialOwnersTable.tsx      # Schedule 13D/13G holders with voting/dispositive powers
     +-- ShareholdingPatternPanel.tsx   # Stacked progress distribution & category cards
     +-- OwnershipHistoryChart.tsx      # Multi-quarter concentration trajectory & snapshot table
     +-- OwnershipChangesTable.tsx      # Q/Q position adjustments with status indicators
     +-- index.ts                       # Barrel export
```

---

## 10. Quality Assurance & Test Verification

All unit, regression, type check, and build tests pass cleanly:

1. **Python Unit & Integration Tests**: 12/12 passed (`test_company_ownership.py`).
2. **Companies Regression Suite**: 133/133 passed (`test_companies_v1.py`, `test_company_financial_statements.py`, `test_company_financial_ratios.py`, `test_company_earnings.py`, `test_company_ownership.py`).
3. **Python Linter (`ruff`)**: 0 errors, all imports sorted and formatted.
4. **TypeScript Type Checking (`tsc`)**: 0 errors across entire Next.js workspace.
5. **Next.js Production Build**: Compiled successfully in 3.0s, all 38 application routes generated cleanly.
