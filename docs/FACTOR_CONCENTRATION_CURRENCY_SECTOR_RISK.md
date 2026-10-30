# ATLAS — Stage 117: Multi-Factor, Concentration, Currency, and Sector Risk Intelligence

## Executive Summary

Stage 117 expands the ATLAS Financial Risk Operating System from market-wide statistical risk (volatility, drawdowns, benchmark sensitivity, VaR, and scenario stress testing) into granular, source-qualified **structural risk intelligence**:
1. **Systematic Multi-Factor Equity Risk**: Fama-French style and economic factor exposure estimation ($b = B^T w$), factor covariance modeling, and Euler variance/volatility decomposition into systematic ($V_{\text{sys}} = b^T F b$) and specific/idiosyncratic ($V_{\text{spec}} = w^T D w$) risk.
2. **Portfolio Concentration & Diversification**: Herfindahl-Hirschman Index ($HHI = \sum w_i^2$), Effective Number of Holdings ($N_{\text{eff}} = 1/HHI$), Top-N concentration, and canonical issuer consolidation (aggregating multiple share classes and ADRs).
3. **Currency Risk & FX Sensitivity**: Currency denomination exposures, realized FX volatility, empirical FX regression betas ($\beta_{\text{FX}}$), and exact multiplicative return compounding with cross-interaction ($R_{\text{base}} = R_{\text{local}} + R_{\text{FX}} + R_{\text{local}} R_{\text{FX}}$).
4. **Sector and Industry Euler Risk Attribution**: Exact decomposition of portfolio covariance risk across economic sectors ($VC_s = \sum_{i \in s} w_i (\Sigma w)_i$), industry hierarchy drilldown, and benchmark-relative active sector tilts ($w_{A,s} = w_s - w_{B,s}$).
5. **2D Cross-Exposure Intelligence**: Factor $\times$ Sector exposure matrices ($b_{s,k} = \sum_{i \in s} w_i \beta_{i,k}$) with row-sum reconciliation ($\sum_s b_{s,k} \equiv b_k$) and Currency $\times$ Sector joint capital allocation matrices.
6. **Bloomberg-Style Risk Workspaces**: Institutional UI workspaces with dark terminal styling, interactive matrix heat tables, and dense metrics under `/risk`.

---

## Controlled Reference Fixtures & Mathematical Verification

Stage 117 establishes five exact reference fixtures verified by backend pytest suites and frontend TypeScript unit tests:

### 1. Part XIV Factor Exposure Aggregation Fixture
Given portfolio weights $w = [0.6, 0.4]$ and security factor exposure matrix $B \in \mathbb{R}^{2 \times 2}$:
$$
B = \begin{pmatrix} 1.2 & 0.5 \\ 0.8 & -0.2 \end{pmatrix}
$$
The portfolio factor loading vector $b = B^T w$ is:
$$
b_{\text{MKT}} = 0.6(1.2) + 0.4(0.8) = 0.72 + 0.32 = 1.04
$$
$$
b_{\text{HML}} = 0.6(0.5) + 0.4(-0.2) = 0.30 - 0.08 = 0.22
$$
**Verified**: $b = [1.04, 0.22]$ with relative tolerance $< 10^{-7}$.

---

### 2. Part XXII Factor Risk Decomposition & Euler Additivity Fixture
Given portfolio weights $w = [0.6, 0.4]$, portfolio factor loadings $b = [1.04, 0.22]$, factor covariance matrix $F = \text{diag}(0.04, 0.01)$, and specific residual variances $d = [0.0225, 0.0100]$:

1. **Systematic Variance ($V_{\text{sys}}$)**:
   $$V_{\text{sys}} = b^T F b = 1.04^2(0.04) + 0.22^2(0.01) = 0.043264 + 0.000484 = 0.043748$$
2. **Specific Variance ($V_{\text{spec}}$)**:
   $$V_{\text{spec}} = w^T D w = 0.6^2(0.0225) + 0.4^2(0.0100) = 0.008100 + 0.001600 = 0.009700$$
3. **Total Portfolio Variance ($V_{\text{total}}$)**:
   $$V_{\text{total}} = V_{\text{sys}} + V_{\text{spec}} = 0.043748 + 0.009700 = 0.053448$$
4. **Total Portfolio Volatility ($\sigma_P$)**:
   $$\sigma_P = \sqrt{V_{\text{total}}} = \sqrt{0.053448} \approx 0.231188235 \quad (23.1188\%)$$
5. **Euler Factor Variance Contributions ($VC_k$)**:
   $$VC_{\text{MKT}} = b_{\text{MKT}} (F b)_{\text{MKT}} = 1.04(0.04 \times 1.04) = 0.043264$$
   $$VC_{\text{HML}} = b_{\text{HML}} (F b)_{\text{HML}} = 0.22(0.01 \times 0.22) = 0.000484$$
6. **Exact Euler Additivity**:
   $$\sum_k VC_k = 0.043264 + 0.000484 = 0.043748 \equiv V_{\text{sys}}$$
   $$\sum_k VC_k + V_{\text{spec}} = 0.043748 + 0.009700 = 0.053448 \equiv V_{\text{total}}$$
   $$\sum_k RC_k + RC_{\text{spec}} = \frac{0.043264}{\sigma_P} + \frac{0.000484}{\sigma_P} + \frac{0.009700}{\sigma_P} \equiv \sigma_P$$
**Verified**: Reconciled to machine precision ($< 10^{-9}$).

---

### 3. Part XXXI Concentration HHI & Effective Holdings Fixture
Given a three-asset normalized capital partition $w = [0.50, 0.30, 0.20]$:
1. **Herfindahl-Hirschman Index ($HHI$)**:
   $$HHI = 0.50^2 + 0.30^2 + 0.20^2 = 0.25 + 0.09 + 0.04 = 0.3800$$
2. **Effective Number of Holdings ($N_{\text{eff}}$)**:
   $$N_{\text{eff}} = \frac{1}{HHI} = \frac{1}{0.38} \approx 2.631578947 \quad (2.6 \text{ holdings})$$
3. **Top-N Concentration**:
   $$\text{Top 1} = 50.00\%, \quad \text{Top 2} = 80.00\%, \quad \text{Top 3} = 100.00\%$$
**Verified**: Evaluated and formatted in backend and frontend unit tests.

---

### 4. Part XLIV Discrete Currency Return Multiplicative Compounding Fixture
For an asset denominated in a foreign currency where the local asset return is $R_{\text{local}} = +10.0\%$ and the exchange rate return against the portfolio base currency is $R_{\text{FX}} = -5.0\%$:
1. **Exact Multiplicative Compounding**:
   $$1 + R_{\text{base}} = (1 + R_{\text{local}})(1 + R_{\text{FX}}) = (1.10)(0.95) = 1.0450$$
2. **Decomposition Components**:
   $$R_{\text{base}} = R_{\text{local}} + R_{\text{FX}} + R_{\text{local}} \cdot R_{\text{FX}}$$
   $$R_{\text{local}} = +0.1000 \quad (+10.0\%)$$
   $$R_{\text{FX}} = -0.0500 \quad (-5.0\%)$$
   $$\text{Interaction} = 0.10 \times (-0.05) = -0.0050 \quad (-0.5\%)$$
   $$R_{\text{base}} = 0.10 - 0.05 - 0.005 = +0.0450 \quad (+4.5\%)$$
**Verified**: Eliminates naive linear approximation error ($+5.0\%$) and confirms exact $+4.5\%$.

---

### 5. Part LVII Sector Euler Risk Attribution Fixture
Given two uncorrelated sectors (Tech and Financials) each with $50\%$ portfolio weight:
$$
w = [0.5, 0.5], \quad \Sigma = \begin{pmatrix} 0.04 & 0.00 \\ 0.00 & 0.09 \end{pmatrix}
$$
1. **Portfolio Variance ($V_P$)**:
   $$V_P = w^T \Sigma w = 0.5^2(0.04) + 0.5^2(0.09) = 0.0100 + 0.0225 = 0.0325$$
2. **Sector Variance Contributions ($VC_s$)**:
   $$VC_{\text{Tech}} = w_1 (\Sigma w)_1 = 0.5(0.04 \times 0.5) = 0.0100$$
   $$VC_{\text{Fin}} = w_2 (\Sigma w)_2 = 0.5(0.09 \times 0.5) = 0.0225$$
3. **Exact Additivity**:
   $$VC_{\text{Tech}} + VC_{\text{Fin}} = 0.0100 + 0.0225 = 0.0325 \equiv V_P$$
**Verified**: Strict equality verified across backend decomposition and frontend UI charts.

---

## Architectural Components

```
python/atlas/src/atlas/risk/
├── enums.py            # FactorFamily, ConcentrationDimension, CurrencyExposureType, ModelDiagnosticStatus
├── errors.py           # 19 typed domain exceptions for Stage 117
├── models.py           # RiskFactorDefinition, SecurityFactorExposure, FactorRiskContribution,
│                       # FactorModelDiagnostics, FactorRiskRun, ConcentrationSnapshot,
│                       # CurrencyRiskSnapshot, SectorRiskSnapshot, CrossExposureMatrix
├── schemas.py          # Pydantic v2 DTOs for factor calculations and snapshots
├── factors.py          # FactorRiskEngine: OLS regressions, diagnostics, covariance, Euler decomposition
├── concentration.py    # ConcentrationEngine: HHI, effective holdings, issuer consolidation
├── currency_risk.py    # CurrencyRiskEngine: FX volatility, betas, multiplicative return interaction
├── sector_risk.py      # SectorRiskEngine: Sector Euler variance/volatility contributions, hierarchy
├── cross_exposure.py   # CrossExposureEngine: Factor x Sector, Currency x Sector 2D matrices
└── service.py          # RiskService orchestration and multi-tenant security verification
```

---

## FastAPI REST Router Endpoints (`apps/api/src/atlas_api/routers/risk.py`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/risk/factors` | Lists canonical risk factor catalog |
| `GET` | `/api/v1/risk/factors/{factor_id}` | Retrieves single factor definition |
| `POST` | `/api/v1/risk/factor-models/calculate` | Executes multi-factor risk decomposition |
| `GET` | `/api/v1/risk/portfolios/{id}/factors` | Retrieves latest multi-factor risk run |
| `GET` | `/api/v1/risk/portfolios/{id}/factors/exposures` | Retrieves security factor loadings & OLS fit |
| `GET` | `/api/v1/risk/portfolios/{id}/factors/contributions` | Retrieves systematic factor risk contributions |
| `GET` | `/api/v1/risk/portfolios/{id}/factors/diagnostics` | Retrieves regression collinearity diagnostics |
| `GET` | `/api/v1/risk/portfolios/{id}/concentration` | Retrieves HHI, effective holdings & Top-N |
| `GET` | `/api/v1/risk/portfolios/{id}/concentration/issuers` | Retrieves consolidated issuer concentration |
| `GET` | `/api/v1/risk/portfolios/{id}/currencies` | Retrieves currency risk snapshot & decomposition |
| `GET` | `/api/v1/risk/portfolios/{id}/currencies/exposures` | Retrieves currency denomination items |
| `GET` | `/api/v1/risk/portfolios/{id}/currencies/sensitivity` | Retrieves empirical FX betas and interaction |
| `GET` | `/api/v1/risk/portfolios/{id}/sectors` | Retrieves sector Euler risk attribution |
| `GET` | `/api/v1/risk/portfolios/{id}/sectors/contributions` | Retrieves sector risk contribution list |
| `GET` | `/api/v1/risk/portfolios/{id}/cross-exposures` | Retrieves 2D cross-exposure matrix |
| `GET` | `/api/v1/risk/portfolios/{id}/factor-benchmark` | Retrieves active benchmark factor tilts |

---

## Frontend Web Workspaces (`apps/web/src/components/risk/`)

- `<FactorRiskWorkspace />`: Systematic vs idiosyncratic risk summary cards, factor loading table, benchmark active tilts, security-level OLS regressions, and condition number diagnostics.
- `<ConcentrationWorkspace />`: HHI metric card, Effective holdings count ($N_{\text{eff}}$), antitrust concentration badge, Top-N cumulative concentration, and dimension selector (Security, Issuer, Sector, Industry, Asset Class, Country).
- `<CurrencyRiskWorkspace />`: Base vs foreign currency exposure, historical realized FX volatility, FX regression betas ($\beta_{\text{FX}}$), and interactive Part XLIV return decomposition card.
- `<SectorRiskWorkspace />`: Portfolio vs benchmark sector weights, active tilts, Euler variance contributions, and expandable industry hierarchy drilldown.
- `<CrossExposureWorkspace />`: 2D interactive matrix heat table (Factor $\times$ Sector, Currency $\times$ Sector) with row-sum reconciliation.
- `<RiskTerminalWorkspace />`: Integrated sub-tab navigation supporting all risk dimensions under primary route `/risk`.

---

## Canonical Roadmap Scope Guardrails

- **Read-Only Analytics**: Strictly read-only; never mutates portfolio positions, transactions, or cash balances, and never submits live broker orders.
- **Deferred to Stage 118**: Options Greeks (Delta, Gamma, Vega, Theta, Rho), Fixed-Income Duration, Convexity, DV01, Key Rate Duration, and credit spread duration.

