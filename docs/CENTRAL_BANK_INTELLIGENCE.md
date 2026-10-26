# ATLAS Stage 91 — Central Bank Intelligence Architecture & Implementation Specification

## 1. Executive Overview & Institutional Mission

Stage 91 of the canonical 150-stage ATLAS development roadmap establishes **Institutional-Grade Central Bank Intelligence** inside the `/economics` module. Central banking authorities and monetary policy operations form the foundational bedrock of global financial asset pricing, credit cycle dynamics, currency valuations, and institutional macroeconomic research.

The primary objective of Stage 91 is to deliver an authoritative, source-grounded research workstation comparable in rigor, analytical depth, and usability to specialized institutional central bank desks and top-tier macroeconomic terminals. The platform provides verifiable, point-in-time answers to critical monetary policy inquiries:
- What is the latest officially announced target policy rate or target range for a central bank?
- When was the latest decision announced, when did it become effective, and was it scheduled or extraordinary?
- By how many exact basis points did specific administered instruments change?
- What are the underlying statutory mandates, operating strategies, and inflation target metrics?
- What are the exact verbatim forward guidance communications published by the institution?
- How did individual committee members vote where voting outcomes are officially disclosed?
- What are the official balance sheet holdings (total assets, liabilities, reserve balances, securities portfolios)?
- What active quantitative easing (QE), asset purchase runoff (QT), or liquidity facilities are authorized?

---

## 2. Architectural Principles & Invariants

Stage 91 adheres to rigorous domain constraints to prevent data fabrication, instrument conflation, and premature roadmap leakage:

1. **Decisions are Institutional Actions, Not Raw Market Prices**: An official monetary policy decision cannot be manufactured from generic interest rate series fluctuations. Every decision is an official institutional event backed by authenticated source documentation.
2. **Instrument Identity Integrity**: Administered target rates, target ranges (e.g., US Federal Funds Target Range), standing facility rates (ECB Deposit Facility, RBI SDF/MSF), and market-clearing effective rates (SOFR, €STR, SONIA) are strictly distinguished.
3. **Exact Target Range Handling**: Target ranges are never artificially collapsed into single midpoint rates unless an explicit derived metric is formally declared. Both upper and lower endpoints are tracked and calculated independently.
4. **Deterministic Basis-Point Arithmetic**: Basis-point changes are computed using exact decimal arithmetic:
   $$\Delta \text{bps} = (\text{New Rate} - \text{Previous Rate}) \times 100$$
   For target ranges, upper and lower movements are computed separately.
5. **No Speculative Predictions or Inferred Votes**: ATLAS does not guess individual votes, does not classify policymakers with arbitrary hawk/dove labels, and does not convert forward guidance into synthetic interest-rate probability forecasts.
6. **Stock vs. Flow and Program vs. Execution Clarity**: Balance sheet asset stocks are kept distinct from quantitative purchase flows, and authorized program envelopes are kept distinct from executed market operations.
7. **Point-in-Time Temporal Integrity**: Announcement timestamps, effective dates, document publication dates, and system ingestion timestamps are maintained as distinct temporal dimensions. Historical queries enforce strict no-look-ahead controls.
8. **Roadmap Boundaries**:
   - **Stage 91**: Owns institution-level central bank intelligence, frameworks, instruments, decisions, meetings, voting, balance sheets, and publications.
   - **Stage 92**: Reserved for the Global Economic Calendar, economic surprise engines, and release countdowns.
   - **Stage 93**: Reserved for Global Macro Comparisons, cross-country benchmarking, and policy differentials.

---

## 3. Canonical Central Bank Registry & Coverage

Stage 91 implements an extensible institutional registry covering major central banks and monetary authorities with verified official sources:

| Institution ID | Official Canonical Name | Acronym | Geography | Currency | Primary Policy Committee | Operational Source |
|---|---|---|---|---|---|---|
| `cb-fed` | Federal Reserve System | Federal Reserve | US | USD | Federal Open Market Committee (FOMC) | Board of Governors of the Federal Reserve System |
| `cb-ecb` | European Central Bank | ECB | EU / EMU | EUR | Governing Council | European Central Bank Eurosystem |
| `cb-boe` | Bank of England | BoE | GB | GBP | Monetary Policy Committee (MPC) | Bank of England Official Releases |
| `cb-boj` | Bank of Japan | BoJ | JP | JPY | Policy Board | Bank of Japan Monetary Policy Releases |
| `cb-rbi` | Reserve Bank of India | RBI | IN | INR | Monetary Policy Committee (MPC) | Reserve Bank of India Database on Indian Economy |
| `cb-pboc` | People's Bank of China | PBOC | CN | CNY | Monetary Policy Committee | People's Bank of China Official Publications |

### Alias Resolution
The platform resolves common acronyms, national identifiers, and aliases (e.g., `"Fed"`, `"FOMC"`, `"ECB"`, `"BoE"`, `"BoJ"`, `"RBI"`, `"PBOC"`) to canonical entity IDs through Stage 22 identifier resolution infrastructure.

---

## 4. Monetary Policy Frameworks & Inflation Targets

Each institution operates under a verified legal statutory mandate and operating strategy:

- **Federal Reserve (`cb-fed`)**: Dual Mandate established by the Federal Reserve Act: maximum employment and price stability. Operates a Flexible Average Inflation Targeting (FAIT) framework targeting 2.0% headline PCE inflation over the longer run.
- **European Central Bank (`cb-ecb`)**: Primary statutory objective: price stability. Strategy: symmetric 2.0% inflation target over the medium term, measured by the Harmonised Index of Consumer Prices (HICP).
- **Bank of England (`cb-boe`)**: Remit from HM Treasury: 2.0% 12-month CPI inflation target with a $\pm 1.0\%$ open-letter threshold band (triggers formal explanation letters if inflation deviates below 1% or above 3%).
- **Bank of Japan (`cb-boj`)**: Price Stability Target: 2.0% year-on-year CPI inflation target achieved in a sustainable and stable manner accompanied by wage increases.
- **Reserve Bank of India (`cb-rbi`)**: Flexible Inflation Targeting (FIT) under the RBI Act: 4.0% headline CPI target with a tolerance band of $\pm 2.0\%$ (2.0% lower tolerance, 6.0% upper tolerance).
- **People's Bank of China (`cb-pboc`)**: Maintain currency stability and thereby promote economic growth. Sets annual ceiling target (traditionally around 3.0% CPI).

---

## 5. Policy Rate Instrument Registry

Central banks administer multiple distinct operational interest rates:

1. **Federal Reserve**:
   - `FED_FUNDS_TARGET_RANGE`: Target Range for the Federal Funds Rate (e.g. 5.25% - 5.50%).
   - `IORB`: Interest on Reserve Balances (Administered floor/anchor rate).
   - `DISCOUNT_RATE`: Primary Credit Facility rate.
2. **European Central Bank**:
   - `ECB_DFR`: Deposit Facility Rate (Key operational policy anchor).
   - `ECB_MRO`: Main Refinancing Operations Rate (Fixed rate tenders).
   - `ECB_MLF`: Marginal Lending Facility Rate (Ceiling rate).
3. **Bank of England**:
   - `BOE_BANK_RATE`: Official Bank Rate (Interest paid on central bank reserves).
4. **Bank of Japan**:
   - `BOJ_CALL_RATE`: Uncollateralized Overnight Call Rate target (e.g. 0.25%, transitioned from negative -0.10%).
   - `BOJ_COMPLEMENTARY_DEPOSIT`: Interest rate applied to policy-rate balances.
5. **Reserve Bank of India**:
   - `RBI_REPO_RATE`: Policy Repo Rate (Administered primary policy benchmark).
   - `RBI_SDF`: Standing Deposit Facility (Floor, 25 bps below Repo).
   - `RBI_MSF`: Marginal Standing Facility (Ceiling, 25 bps above Repo).
6. **People's Bank of China**:
   - `PBOC_7D_REVERSE_REPO`: 7-Day Reverse Repo Rate (Primary short-term policy signal).
   - `PBOC_1Y_LPR`: 1-Year Loan Prime Rate (Benchmark for corporate & household loans).
   - `PBOC_5Y_LPR`: 5-Year Loan Prime Rate (Benchmark for mortgage loans).

---

## 6. Monetary Policy Decisions & Rate Change Arithmetic

Monetary policy decisions track institutional actions:
- **Decision Kinds**: `RATE_INCREASE`, `RATE_DECREASE`, `RATE_HOLD`, `MULTI_INSTRUMENT_CHANGE`, `ASSET_PURCHASE_DECISION`, `LIQUIDITY_OPERATION_DECISION`, `FRAMEWORK_CHANGE`.
- **Scheduled vs. Unscheduled**: Decisions indicate whether they arose from regular calendar policy meetings or intermeeting emergency actions.
- **Announcement Timestamps vs. Effective Dates**: Decisions record exact announcement timestamps (e.g., 14:00 EST / 19:00 UTC) and the separate subsequent date when market facilities implement the rates.
- **Rate Holds**: A hold is recorded only when verified by an official policy decision statement maintaining rates; it is never assumed merely from an absence of data.

---

## 7. Policy Meetings, Deliberations & Published Votes

The platform indexes historical policy committee meetings, multi-day schedules, and associated publications:
- **Meeting Duration**: Multi-day policy meetings preserve explicit start and end dates (e.g., 2-day FOMC meetings).
- **Official Voting Records**: Published individual voting results are recorded where officially disclosed:
  - Bank of England MPC: Individual voting records published with each decision (e.g., 8–1 vote splits with dissenting member names and preferred rate levels).
  - Federal Reserve FOMC: Voting records disclosed in official statements and meeting minutes.
  - Reserve Bank of India MPC: Voting outcomes for repo rate decisions and policy stance recorded with individual member names.
- **Undisclosed / Consensus Semantics**: Central banks that do not publish individual votes (e.g., ECB Governing Council consensus) are explicitly labeled with `NOT_DISCLOSED` without inventing hypothetical member positions.

---

## 8. Official Publications, Speeches & Forward Guidance

### Document Catalog & Security
- Catalogs official policy decision statements, meeting minutes, monetary policy reports, and financial stability reviews.
- Reuses Stage 20 canonical Document Entity architecture.
- Enforces strict sanitization on HTML/PDF text and prevents arbitrary URL injection or script execution.

### Official Speeches
- Tracks speeches and prepared remarks delivered by governors, chairs, and committee members.
- Captures delivery timestamps, publication timestamps, official titles, and permanent source references.

### Verbatim Forward Guidance
- Extracts exact, source-grounded sentences directly from official policy statements.
- Classifies forward guidance by category (`STATE_CONTINGENT`, `DATE_BASED`, `OUTLOOK_STATEMENT`, `POLICY_REACTION_FRAMEWORK`).
- Tracks validity status and supersession relationships when subsequent meeting statements modify prior guidance.
- Strictly prohibits generating speculative probability distributions or quantitative rate predictions.

---

## 9. Central Bank Balance Sheets & Policy Programs

### Balance Sheet Accounting
- Reflects central bank accounting data: Total Assets, Total Liabilities, Securities Held Outright, and Reserve Balances.
- Preserves reporting frequency, reporting currencies, and unit scale (in billions).
- Distinguishes central bank domestic reserve liabilities from national foreign exchange reserve assets.

### Policy Programs (QE / QT / Liquidity)
- Tracks asset purchase programs (e.g., Fed System Open Market Account Runoff, ECB Asset Purchase Programme / PEPP, BoE Asset Purchase Facility).
- Preserves explicit distinctions between:
  - Authorized Program Envelopes (e.g., €1,850 billion PEPP envelope).
  - Executed Purchase Flows.
  - Cumulative Portfolio Holdings Stocks.
  - Passive Balance Sheet Runoff (redemptions without full reinvestment).

---

## 10. API Specification (`/api/v1/economics/central-banks`)

All endpoints require standard authenticated principals (`ATLAS_ACCESS` permission) and return typed Pydantic V2 responses:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/economics/central-banks` | List all supported central banks |
| `GET` | `/api/v1/economics/central-banks/coverage` | System-wide coverage matrix across all central banks |
| `GET` | `/api/v1/economics/central-banks/{bank_id}` | Direct institution profile lookup |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/overview` | Master research overview (framework, rates, latest decision, balance sheet) |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/profile` | Institutional identity, headquarters, committee, official site |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/framework` | Statutory mandate, strategy, inflation targets, source citation |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/targets` | Official inflation target metric, bounds, and tolerance bands |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/committee` | Policy committee structure, total members, charter URL |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/instruments` | List all administered policy instruments |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/instruments/{code}` | Specific policy instrument details |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/rates` | Current policy interest rates and target ranges |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/rates/history` | Chronological official policy rate observation series |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/decisions` | Monetary policy decision history (supports `?as_of=` point-in-time filtering) |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/decisions/{id}` | Specific decision details and exact basis-point changes |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/meetings` | Policy committee meeting history |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/meetings/{id}` | Specific meeting details, decision links, and minutes dates |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/meetings/{id}/voting` | Committee voting record and dissenting rationales |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/publications` | Official publications, statements, and minutes |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/publications/{id}` | Specific official publication details and source URLs |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/speeches` | Policymaker speech transcripts and summaries |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/guidance` | Verbatim forward guidance excerpts and classification |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/balance-sheet` | Balance sheet positions, assets, liabilities, and reserves |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/programs` | Asset purchase, QT, and liquidity facilities |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/timeline` | Unified chronological policy event timeline |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/coverage` | Indicator and publication coverage matrix for institution |
| `GET` | `/api/v1/economics/central-banks/{bank_id}/sources` | Source provenance, verified authority, and tier |

---

## 11. Frontend Research Workstation (`/economics` -> `Central Banks`)

The frontend workspace provides a high-density, terminal-grade interface structured into dedicated analytical views:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ATLAS GLOBAL TOP BAR                                                                   │
├────────────┬───────────────────────────────────────────────────────────┬───────────────┤
│            │ ECONOMICS / CENTRAL BANKS                                 │               │
│            │ [Federal Reserve ▼] [US / USD] [Active Mandate: Dual]    │               │
│            │ [Overview] [Rates] [Decisions] [Meetings]                 │               │
│            │ [Publications] [Speeches] [Balance Sheet] [Timeline]     │               │
│            ├───────────────────────────────────────────────────────────┤               │
│            │ INSTITUTIONAL OVERVIEW & STATUTORY MANDATE               │               │
│            │ • Statutory Mandate Summary & Strategy                    │               │
│            │ • Official Target Metric: PCE Inflation (2.0%)            │               │
│            │ • Policy Instruments: Fed Funds Target Range (5.25-5.50%) │               │
│            │ • Latest Verified Decision: 50 bps Cut (Sep 18, 2024)     │               │
│            ├───────────────────────────────────────────────────────────┤               │
│            │ ADMINISTERED RATES & RECENT ACTIONS                       │               │
│            │ Code | Instrument Name | Rate / Range | Effective Date    │               │
│ GLOBAL     ├───────────────────────────────────────────────────────────┤ AGENT DOCK    │
│ SIDEBAR    │ MONETARY POLICY DECISION HISTORY                          │               │
│            │ Date | Type | Instrument | Previous | New | Delta (bps)   │               │
│            ├───────────────────────────────────────────────────────────┤               │
│            │ POLICY MEETINGS & VOTING RECORDS                          │               │
│            │ Meeting ID | Dates | Outcome | Minutes Date | Votes       │               │
│            ├───────────────────────────────────────────────────────────┤               │
│            │ VERBATIM FORWARD GUIDANCE & OFFICIAL STATEMENTS           │               │
│            ├───────────────────────────────────────────────────────────┤               │
│            │ BALANCE SHEET ASSETS, LIABILITIES & RUNOFF (QT)          │               │
│            ├───────────────────────────────────────────────────────────┤               │
│            │ SOURCE PROVENANCE & METHODOLOGY INSPECTOR                 │               │
├────────────┴───────────────────────────────────────────────────────────┴───────────────┤
│ ATLAS BOTTOM TASKBAR                                                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Quality Verification & Test Coverage

Stage 91 verification confirms zero defects across all layers:
- **Backend Test Suite**: 18 comprehensive tests in `apps/api/tests/test_central_banks.py`:
  - Canonical identity & alias resolution (`cb-fed`, `cb-ecb`, `cb-boe`, `cb-boj`, `cb-rbi`, `cb-pboc`).
  - Dual mandates, symmetric price stability, and inflation target tolerance bands.
  - Target range calculations and non-parallel bound validation.
  - Negative interest rates (e.g., BOJ historical -0.10% policy balance rate).
  - Rate hike, cut, and confirmed hold arithmetic.
  - Multi-day meeting durations and minutes publication lags.
  - Voting splits, individual member dissent, and undisclosed vote semantics.
  - Official publications, sanitized speeches, and verbatim forward guidance.
  - Balance sheet stock/flow accounting and QT runoff program parameters.
  - Point-in-time as-of temporal isolation (historical knowledge boundaries).
  - REST API endpoint contracts and 404 error envelopes.
  - Zero read side-effects (0 mutations, 0 trades, 0 LLM calls).
- **Regression Tests**: All 49 existing tests in `tests/test_country_economics.py` and `tests/test_economics_v1.py` pass cleanly.
- **Frontend Verification**: TypeScript compilation (`npx tsc --noEmit`) and Next.js production build (`npm run build`) succeeded with 0 errors.
