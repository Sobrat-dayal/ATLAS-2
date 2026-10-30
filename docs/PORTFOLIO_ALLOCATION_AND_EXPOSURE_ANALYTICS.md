# ATLAS Portfolio Allocation, Exposure Intelligence & Concentration Analytics Platform (Stage 112)

## Institutional-Grade Portfolio Allocation and Exposure Platform

The **ATLAS Portfolio Allocation, Exposure Intelligence, and Concentration Analytics Platform** delivers institutional-grade, mathematically verified portfolio composition and risk exposure intelligence built directly upon the Stage 110 accounting/valuation foundation and Stage 111 performance engine.

It implements CFA Institute / GIPS-aligned allocation methodologies, multi-dimensional exposure taxonomies (GICS sectors/industries, geographic domicile/HQ/listing policies, multi-currency denomination), fund and ETF look-through decomposition with cross-fund overlap, Herfindahl-Hirschman Index (HHI) concentration metrics, effective number of bets ($N_{\text{eff}}$), date-to-date allocation drift, and strict partition reconciliation auditing with SHA-256 provenance tracking.

---

## 1. Core Mathematical Foundations

### 1.1 Partition Weight Calculation & Denominator Invariants

Portfolio asset allocation and exposure weights are calculated with exact Python `Decimal` precision relative to the selected exposure basis (Net Asset Value, Total Assets, Long-Only, or Short-Only).

#### Mathematical Formulation:
$$w_i = \frac{v_i}{\text{NAV}}$$

Where:
- $v_i$ is the marked valuation of category or asset $i$ in portfolio base reporting currency.
- $\text{NAV}$ is the verified Net Asset Value of the portfolio ($V_{\text{long}} + V_{\text{short}} + \text{Cash}$).
- **Partition Reconciliation Invariant**: The sum of all partition weights across a mutually exclusive, collectively exhaustive classification dimension must sum to exactly $100\%$ ($1.000000$):
$$\left| \sum_{i=1}^{K} w_i - 1.0 \right| \le 10^{-4}$$
If the discrepancy exceeds $0.01\%$, a `RECONCILIATION_WARNING` or `RECONCILIATION_FAILED` status is raised with the exact residual variance tracked in audit logs.

- **Non-Positive NAV Guardrail**: If $\text{NAV} \le 0.00$, relative weight division is mathematically invalid. The engine raises a typed `PortfolioExposureNavInvalidError` and marks the exposure run as invalid rather than propagating zero-division or infinite ratios.

- **Reference Fixture (Part X Allocation Fixture)**:
  - Total Marked Equity Value: $\$15,000.00$
  - Cash Balance: $\$5,000.00$
  - Total Net Asset Value (NAV): $\$20,000.00$
  - Equity Weight: $\frac{\$15,000}{\$20,000} = \mathbf{75.0\%}$
  - Cash Weight: $\frac{\$5,000}{\$20,000} = \mathbf{25.0\%}$
  - Partition Sum: $75.0\% + 25.0\% = \mathbf{100.0\%}$

---

### 1.2 Concentration Analytics: HHI, Effective Bets & Quantile Ladders

Portfolio concentration is evaluated at both the individual **Security** level and the consolidated **Ultimate Parent Issuer** level (merging multiple share classes like GOOG and GOOGL, or ordinary shares and ADRs).

#### Mathematical Formulations:

1. **Herfindahl-Hirschman Index (HHI)**:
$$\text{HHI} = \sum_{i=1}^{n} w_i^2$$
Conventional normalized index scale ($0 \text{ to } 10,000$):
$$\text{HHI}_{\text{idx}} = 10,000 \times \text{HHI}$$

2. **Effective Number of Holdings / Bets ($N_{\text{eff}}$)**:
$$N_{\text{eff}} = \frac{1}{\text{HHI}} = \frac{1}{\sum_{i=1}^{n} w_i^2}$$
$N_{\text{eff}}$ represents the equivalent number of equal-weighted holdings yielding the same concentration profile as the actual portfolio.

3. **Concentration Classification Regimes**:
   - $\text{HHI} < 0.15$ ($\text{HHI}_{\text{idx}} < 1,500$): **Highly Diversified**
   - $0.15 \le \text{HHI} < 0.25$ ($1,500 \le \text{HHI}_{\text{idx}} < 2,500$): **Moderately Concentrated**
   - $\text{HHI} \ge 0.25$ ($\text{HHI}_{\text{idx}} \ge 2,500$): **Highly Concentrated**

4. **Quantile Concentration Ladders**:
Cumulative concentration weights across the largest holdings:
$$\text{Top } k = \sum_{j=1}^{k} w_{(j)} \quad \text{for } k \in \{1, 3, 5, 10, 20\}$$

- **Reference Fixture (Part XXVIII Concentration Fixture)**:
  - Holding A: $w_A = 0.50$ ($50\%$)
  - Holding B: $w_B = 0.25$ ($25\%$)
  - Holding C: $w_C = 0.25$ ($25\%$)
  - $\text{HHI} = 0.50^2 + 0.25^2 + 0.25^2 = 0.2500 + 0.0625 + 0.0625 = \mathbf{0.3750}$
  - $\text{HHI}_{\text{idx}} = 10,000 \times 0.3750 = \mathbf{3,750}$ (Regime: `HIGHLY_CONCENTRATED`)
  - $N_{\text{eff}} = \frac{1}{0.3750} \approx \mathbf{2.67}$ effective holdings.

---

### 1.3 Fund & ETF Look-Through Decomposition

For portfolios containing collective investment vehicles (ETFs, mutual funds, closed-end funds), the engine decomposes fund holdings into their underlying constituents:

#### Mathematical Formulation:
For fund $F$ with portfolio weight $W_F$ and constituent holding $k$ with fund internal weight $w_{k,F}$:
$$w_{\text{look-through}}(k) = W_F \times w_{k,F}$$

When security $k$ is held both directly in the portfolio ($w_{\text{direct}}(k)$) and indirectly via one or more funds:
$$w_{\text{effective}}(k) = w_{\text{direct}}(k) + \sum_{F} (W_F \times w_{k,F})$$

- **Recursive Depth & Cycle Protection**:
  Look-through traversal enforces a strict maximum recursion depth (default 3 levels) and maintains a visited set of instrument identifiers to prevent circular fund-in-fund reference loops (`PortfolioExposureLookThroughCycleError`).

- **Residual Non-Decomposed Bucket**:
  Constituents below disclosure thresholds or missing from holdings feeds are preserved in an explicit `residual_unmapped` holding row to guarantee that total fund constituent weights reconcile to exactly $100\%$ of the fund's valuation.

- **Reference Fixture (Part XXXII ETF Look-Through Fixture)**:
  - Portfolio NAV: $\$100,000.00$
  - Direct AAPL holding: $\$60,000.00$ ($w_{\text{direct}} = 60.0\%$)
  - SPY ETF holding: $\$40,000.00$ ($W_{\text{SPY}} = 40.0\%$)
  - SPY internal AAPL constituent weight: $w_{\text{AAPL},\text{SPY}} = 7.20\%$
  - Look-through indirect AAPL weight: $40.0\% \times 7.20\% = \mathbf{2.88\%}$ ($\$2,880.00$)
  - Total effective AAPL exposure: $60.0\% + 2.88\% = \mathbf{62.88\%}$ ($\$62,880.00$)
  - *Prevents hidden concentration risk from ETF wrappers.*

---

### 1.4 Cross-Fund Overlap Analysis

When multiple ETFs or funds are held simultaneously, the engine calculates the pairwise and consolidated overlap between funds:

#### Mathematical Formulation:
For two funds $A$ and $B$, the pairwise common holding overlap is:
$$\text{Overlap}(A, B) = \sum_{k \in (A \cap B)} \min(w_{k,A}, w_{k,B})$$

The portfolio-level duplicated exposure is:
$$w_{\text{overlap}}(k) = \sum_{F} W_F \cdot w_{k,F} \quad \text{for all } F \text{ holding } k$$

---

### 1.5 Historical Allocation Drift Analytics

To assess active portfolio drift or rebalancing drift across time, the engine computes exact date-to-date allocation differences:

#### Mathematical Formulation:
$$\Delta w_i(t_1 \to t_2) = w_i(t_2) - w_i(t_1)$$
$$\Delta \text{bps}_i(t_1 \to t_2) = 10,000 \times (w_i(t_2) - w_i(t_1))$$
$$\Delta v_i(t_1 \to t_2) = v_i(t_2) - v_i(t_1)$$

---

## 2. Multi-Dimensional Exposure Taxonomies

The platform categorizes portfolio exposures across multiple independent classification axes:

1. **Asset Class**:
   - `EQUITY`: Public ordinary equities, preferred shares, ADRs/GDRs.
   - `FIXED_INCOME`: Sovereign bonds, investment-grade corporate bonds, high-yield bonds, TIPS.
   - `CASH_EQUIVALENT`: Fiat currencies, money market funds, cash deposits, treasury bills.
   - `COMMODITY`: Precious metals, industrial metals, energy, agriculture.
   - `REAL_ESTATE`: REITs, property funds.
   - `ALTERNATIVE`: Private equity, hedge funds, structured products, digital assets.
   - `DERIVATIVE`: Options, futures, swaps.

2. **GICS Sector & Industry Classification**:
   - Complete 11 GICS Sectors: Energy, Materials, Industrials, Consumer Discretionary, Consumer Staples, Health Care, Financials, Information Technology, Communication Services, Utilities, Real Estate.
   - 25 Industry Groups with hierarchical parent roll-up.

3. **Geographic Policy Engine**:
   - **Country of Domicile**: Legal registration jurisdiction (e.g. Ireland for UCITS ETFs, Cayman Islands for offshore entities).
   - **Country of Headquarters**: Primary corporate operational head office (e.g. United States for Apple, Inc.).
   - **Primary Exchange Listing**: Country of primary exchange listing (e.g. US for ADRs, India for local shares).
   - Standard ISO 3166-1 alpha-2 codes with regional roll-ups (North America, Europe, Asia-Pacific, Emerging Markets).

4. **Currency Exposure**:
   - Underlying instrument trading currency vs. portfolio base currency.
   - FX risk transparency isolating unhedged foreign denomination exposure.

---

## 3. Cryptographic Provenance & Data Completeness

Every exposure run produces an immutable audit record:

1. **Deterministic Input Digest (`sha256`)**:
   A SHA-256 hash computed over:
   - Portfolio ID & Account Scope
   - Valuation timestamp & Net Asset Value
   - Position count & Cash balance sum
   - Taxonomy versions (GICS 2024, ISO-3166)
   - Valuation mark sources

2. **Data Completeness Tiers**:
   - `COMPLETE`: 100% of holdings mapped to certified canonical taxonomy records.
   - `COMPLETE_WITH_FALLBACKS`: 100% categorized, but with one or more fallback estimations.
   - `PARTIAL_UNMAPPED`: Contains unmapped instruments (tracked in explicit unmapped row).
   - `INCOMPLETE`: Valuation data missing for active positions.

---

## 4. REST API Endpoint Reference

Exposed under `/api/v1/portfolios/{portfolio_id}/...`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/exposures` | Comprehensive multi-dimensional exposure run |
| `POST`| `/exposures/calculate` | Trigger on-demand exposure calculation with custom parameters |
| `GET` | `/exposures/asset-classes` | Asset class partition weights and values |
| `GET` | `/exposures/sectors` | GICS sector breakdown with look-through option |
| `GET` | `/exposures/industries` | GICS industry group breakdown |
| `GET` | `/exposures/geography` | Country and regional exposure with policy selector |
| `GET` | `/exposures/currencies` | Denomination currency exposure |
| `GET` | `/exposures/concentration` | Top-N holdings, HHI, and effective number of bets |
| `GET` | `/exposures/issuers` | Consolidated ultimate parent issuer concentration |
| `GET` | `/exposures/look-through` | Fund and ETF constituent decomposition |
| `GET` | `/exposures/fund-overlap` | Cross-fund constituent overlap matrix |
| `GET` | `/exposures/historical` | Historical allocation time series |
| `GET` | `/exposures/drift` | Date-to-date allocation drift comparison |
| `GET` | `/exposures/data-quality` | Taxonomy mapping coverage and provenance hash |
| `GET` | `/exposures/taxonomies` | Supported classification dimensions and schemes |
| `GET` | `/exposures/runs` | Historical exposure calculation run snapshots |
| `GET` | `/exposures/runs/{run_id}` | Detailed historical exposure run snapshot by ID |

---

## 5. Professional Bloomberg-Style Frontend Workspace

Accessible at `/portfolios` under the **Allocation & Exposures** tab:

1. **Allocation Summary Cards**:
   - Marked Net Asset Value & Currency
   - Cash Allocation Percentage
   - Top 1 & Top 5 Concentration Weights
   - Herfindahl-Hirschman Index (HHI) with Regime Badge
   - Partition Reconciliation Audit Status (`RECONCILED`)

2. **Dimension Workspace Panels**:
   - **GICS Sectors**: Visual bar allocations, market value, and benchmark delta.
   - **Asset Classes**: Multi-asset breakdown with progress bars.
   - **Geographic Exposures**: Country breakdown with interactive policy switcher (Domicile / HQ / Listing).
   - **Currency Exposures**: FX denomination exposure vs base currency.
   - **Portfolio Concentration**: HHI, $N_{\text{eff}}$, quantile ladder (Top 1/3/5/10/20), and securities vs issuers toggle.
   - **Fund & ETF Look-Through**: Decomposition view of ETF constituents and cross-fund overlap.
   - **Historical Allocation & Drift**: Date-to-date drift comparison ($\Delta w$ in bps and value).
   - **Data Quality & Provenance**: SHA-256 cryptographic digest, instrument coverage ratios, and audit metadata.

---

## 6. Strict Stage Boundaries & Architectural Deferrals

- **Stage 112 Boundary**: Exclusively delivers portfolio allocation, multi-dimensional exposure intelligence, concentration analytics, ETF look-through, and historical drift.
- **Stage 113 Deferral (Portfolio Attribution)**: Brinson-Fachler, Brinson-Hood-Beebower, allocation vs selection effects, and active return decomposition are strictly deferred to Stage 113.
- **Stage 114 Deferral (Portfolio Optimization)**: Mean-variance optimization, Black-Litterman, risk parity, and frontier generation are strictly deferred to Stage 114.
- **Stages 115–118 Deferral (Risk Analytics)**: Parametric VaR, Historical VaR, Monte Carlo VaR, Stress Testing, and Tail Risk are strictly deferred to Stages 115–118.
- **Stages 143–149 Deferral (Trading & Execution)**: Zero live broker orders or automated trading signals.

