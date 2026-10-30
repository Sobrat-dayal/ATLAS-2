# ATLAS — Stage 116: Value at Risk (VaR), Expected Shortfall (ES), Scenario Testing, and Model Backtesting Platform

## 1. Architectural Positioning & Scope

Stage 116 establishes the institutional-grade Tail Risk and Scenario Analytics engine within the ATLAS Financial Intelligence Operating System. Operating under the primary global module `/risk`, it integrates directly with Portfolio Accounting (Stage 110), Performance (Stage 111), Exposures (Stage 112), Benchmarks (Stage 113), Optimization (Stage 114), and Core Risk Foundations (Stage 115).

```
Stage 110: Portfolio Accounting (Valuations, Positions, Cash)
    │
Stage 111: Historical Returns & Time-Series Performance
    │
Stage 115: Foundation Risk (Volatility, Drawdowns, Euler Contributions)
    │
    ▼
Stage 116: VaR, Expected Shortfall, Tail Distributions, Scenarios & Kupiec POF Backtesting
    │
    ├── Historical Simulation (Empirical Quantile & Fractional Tail Integration)
    ├── Parametric Delta-Normal (Gaussian VaR & Closed-Form Analytical ES)
    ├── Monte Carlo Simulation (Regularized PSD Covariance Cholesky Paths)
    ├── Loss Distribution Analytics (Histogram Binning, Quantiles, Leptokurtosis)
    ├── Multi-Currency Compounding: (1 + s_price)(1 + s_fx) - 1
    ├── Scenario Testing & Collision Priority: Security > Sector > Portfolio
    ├── Strict Position-to-Portfolio Reconciliation: Sum(Delta V_i) === Delta V_P
    └── Kupiec POF Unconditional Coverage Backtesting (LR_UC ~ Chi^2(1), 3.8415)
```

---

## 2. Mathematical Formalisms & Reference Fixtures

### 2.1 Historical Simulation VaR and Fractional Tail Expected Shortfall

Given a historical series of portfolio returns $r_t$ or losses $L_t = -r_t$ sorted in ascending order $L_{(1)} \le L_{(2)} \le \dots \le L_{(N)}$:

$$\text{VaR}_\alpha = Q(\alpha) = L_{(k)}, \quad k = \lceil \alpha N \rceil$$

For Expected Shortfall (CVaR), the exact continuous quantile integration over tail losses is evaluated:

$$\text{ES}_\alpha = \frac{1}{1 - \alpha} \int_\alpha^1 Q(u) \, du$$

Where $Q(u)$ represents the empirical step-function quantile across $N$ equally weighted intervals $[(i-1)/N, i/N]$. The tail boundary at $\alpha$ is weighted by the exact fractional overlap:

$$w_i = \frac{\min(i/N, 1) - \max((i-1)/N, \alpha)}{1 - \alpha}$$

$$\text{ES}_\alpha = \sum_{i=k}^N w_i L_{(i)}$$

#### Part XVI Reference Fixture Reconciled:
- Sample: 5 daily losses $[-2.0\%, -1.0\%, +0.5\%, +1.0\%, +3.0\%]$.
- $\alpha = 0.80$, $N = 5 \implies k = \lceil 0.8 \times 5 \rceil = 4$.
- $\text{VaR}_{0.80} = 1.0\%$.
- Tail region $[0.80, 1.00]$ lies entirely within the 5th observation $L_{(5)} = 3.0\%$.
- $\text{ES}_{0.80} = 3.0\%$.

---

### 2.2 Parametric Delta-Normal VaR and Closed-Form Gaussian Expected Shortfall

Assuming portfolio returns are distributed normally $r \sim \mathcal{N}(\mu_h, \sigma_h^2)$ over horizon $h$:

$$\text{VaR}_\alpha = -\mu_h + \sigma_h z_\alpha$$

Where $z_\alpha = \Phi^{-1}(\alpha)$. For Expected Shortfall:

$$\text{ES}_\alpha = \mathbb{E}[L \mid L \ge \text{VaR}_\alpha] = -\mu_h + \sigma_h \frac{\phi(z_\alpha)}{1 - \alpha}$$

Where $\phi(z) = \frac{1}{\sqrt{2\pi}} e^{-z^2 / 2}$ is the standard Gaussian probability density function.

#### Part XX Reference Fixture Reconciled:
- $\mu = 0.0$, $\sigma = 0.02$ (2.0% daily volatility).
- $\alpha = 0.95 \implies z_{0.95} = 1.64485362695$.
- $\text{VaR}_{0.95} = 0.02 \times 1.64485362695 = 3.2897\%$.
- $\phi(z_{0.95}) = 0.10313564037$.
- $\text{ES}_{0.95} = 0.02 \times \frac{0.10313564037}{0.05} = 4.1254\%$.
- Tail ratio: $\text{ES}_{0.95} / \text{VaR}_{0.95} \approx 1.254\times$.

---

### 2.3 Monte Carlo Gaussian Factor Simulation

1. Construct the asset covariance matrix $\Sigma \in \mathbb{R}^{K \times K}$.
2. Verify positive semi-definiteness (PSD); if $\lambda_{\min} < 10^{-8}$, apply eigenvalue floor regularization $\Sigma_{\text{PSD}} = V \max(\Lambda, 10^{-8}) V^T$.
3. Compute the Cholesky factor $A A^T = \Sigma_{\text{PSD}}$.
4. For $M$ reproducible simulation paths drawn via `np.random.default_rng(seed)`:
   $$z^{(m)} \sim \mathcal{N}(0, I_K), \quad r^{(m)} = \mu + A z^{(m)}, \quad r_P^{(m)} = w^T r^{(m)}$$
5. Empirical loss quantiles and tail averages are extracted from simulated paths.

---

### 2.4 Multi-Currency Multiplicative Compounding

Foreign currency positions compound asset price shocks and FX currency shocks multiplicatively:

$$R_{\text{compound}} = (1 + s_{\text{price}})(1 + s_{\text{fx}}) - 1 \ne s_{\text{price}} + s_{\text{fx}}$$

#### Part XXXIV Reference Fixture Reconciled:
- Asset price shock $s_{\text{price}} = -10\%$.
- FX depreciation $s_{\text{fx}} = -5\%$.
- Naive additive return: $-10\% + (-5\%) = -15.0\%$.
- Correct multiplicative return: $(1 - 0.10)(1 - 0.05) - 1 = 0.90 \times 0.95 - 1 = -14.50\%$.

---

### 2.5 Scenario Shock Collision Precedence & Exact Portfolio Reconciliation

When evaluating multi-level scenarios containing shocks at different hierarchy tiers, collision resolution follows strict institutional precedence:

$$\text{Security Shock} \succ \text{Industry Shock} \succ \text{Sector Shock} \succ \text{Asset Class Shock} \succ \text{Currency Shock} \succ \text{Portfolio-Wide Shock}$$

Every position is revalued to determine shocked value $V_i' = V_{i,0} (1 + R_i)$ and dollar P&L $\Delta V_i = V_i' - V_{i,0}$. Total portfolio revaluation strictly satisfies:

$$\sum_{i=1}^M \Delta V_i \equiv \Delta V_P, \quad |\sum \Delta V_i - \Delta V_P| < 10^{-4}$$

#### Part XLIII Reference Fixture Reconciled:
- Asset A: Base $60,000, shock -10% $\implies V_A' = \$54,000, \Delta V_A = -\$6,000$.
- Asset B: Base $40,000, shock +5% $\implies V_B' = \$42,000, \Delta V_B = +\$2,000$.
- Portfolio Base NAV: $\$100,000$.
- Shocked NAV: $\$96,000$.
- Portfolio P&L: $-\$4,000$.
- Return: $-4.00\%$.
- Exact Reconciliation Diff: $0.0000$ (Reconciled).

---

### 2.6 Kupiec POF Unconditional Coverage Backtesting Test

Backtesting compares rolling one-step-ahead VaR forecasts against realized returns over an audit window of $N$ days. An exception is recorded when realized loss exceeds forecast VaR:

$$I_t = \mathbb{I}(L_t > \text{VaR}_t(\alpha)), \quad x = \sum_{t=1}^N I_t$$

Under the null hypothesis $H_0$ that the model has accurate unconditional coverage, the failure probability is $p_0 = 1 - \alpha$. The Kupiec likelihood ratio statistic is:

$$LR_{UC} = -2 \ln \left[ \frac{(1 - p_0)^{N - x} p_0^x}{(1 - \hat{p})^{N - x} \hat{p}^x} \right] \sim \chi^2(1)$$

Where $\hat{p} = x / N$. At the institutional 95% confidence level ($df = 1$), the critical value is:

$$\chi^2_{0.05, 1} = 3.841459$$

- If $LR_{UC} \le 3.841459 \implies \text{ACCEPT\_UNCONDITIONAL\_COVERAGE}$.
- If $LR_{UC} > 3.841459$ and $\hat{p} > p_0 \implies \text{REJECT\_TOO\_MANY\_EXCEPTIONS}$ (Model underestimates risk).
- If $LR_{UC} > 3.841459$ and $\hat{p} < p_0 \implies \text{REJECT\_TOO\_FEW\_EXCEPTIONS}$ (Model overestimates risk).
- If $N < 30 \implies \text{INSUFFICIENT\_OBSERVATIONS}$ warning flagged.

---

## 3. Backend Implementation Components

| Component | Path | Responsibility |
|---|---|---|
| Domain Models | `python/atlas/src/atlas/risk/models.py` | Typed dataclasses for `VaRResult`, `ExpectedShortfallResult`, `LossDistribution`, `RiskScenario`, `RiskScenarioRun`, `KupiecTestResult`, `VaRBacktestRun`. |
| Tail Risk Engine | `python/atlas/src/atlas/risk/tail_var.py` | Empirical quantile with fractional tail integration, parametric Delta-Normal analytical ES, Monte Carlo Gaussian with Cholesky factor, 25-bin histogram generator. |
| Scenario Engine | `python/atlas/src/atlas/risk/scenarios.py` | Predefined historical episodes (COVID-19, GFC 2008, 2022 Tech Rates, 2011 Downgrade), multi-currency compounding, precedence collision resolution, exact reconciliation validator. |
| Diagnostics Engine | `python/atlas/src/atlas/risk/diagnostics.py` | Rolling historical VaR backtest, exception detector, Kupiec POF likelihood ratio test, p-value calculation. |
| Service Layer | `python/atlas/src/atlas/risk/service.py` | Orchestration, multi-tenant portfolio ownership enforcement, in-memory caching and retrieval. |
| REST API Router | `apps/api/src/atlas_api/routers/risk.py` | 26 FastAPI endpoints exposing tail risk, scenarios, runs, distributions, comparisons, and backtests. |
| Backend Test Suite | `apps/api/tests/test_risk_tail_and_scenarios_v1.py` | 9 comprehensive tests covering all mathematical fixtures, precedence, reconciliation, Kupiec status, and multi-tenant isolation. |

---

## 4. Frontend Workspace & Components

| Component | Path | Function |
|---|---|---|
| Summary Cards | `apps/web/src/components/risk/tail/TailRiskSummaryCards.tsx` | High-density KPI cards for VaR ($ and %), ES ($ and %), Leptokurtosis Multiplier, and Sample Coverage, with interactive model, confidence, and horizon selectors. |
| Distribution Chart | `apps/web/src/components/risk/tail/LossDistributionChart.tsx` | Interactive SVG histogram with 25 bins, VaR threshold marker, shaded tail loss region, hover tooltip, and quantile breakdown chips. |
| Model Comparison | `apps/web/src/components/risk/tail/TailModelComparisonTable.tsx` | Side-by-side technical comparison of Historical Simulation, Parametric Normal, and Monte Carlo models with assumptions and caveats. |
| Scenario Library | `apps/web/src/components/risk/scenarios/ScenarioLibraryTable.tsx` | Catalogue of predefined historical stress episodes and custom scenarios with one-click "Shock" execution and "Compare All" action. |
| Scenario Builder | `apps/web/src/components/risk/scenarios/ScenarioBuilderModal.tsx` | Modal dialog allowing users to define multi-tier custom shock scenarios with validation against $s \ge -100\%$. |
| Results Workspace | `apps/web/src/components/risk/scenarios/ScenarioResultsWorkspace.tsx` | Shocked NAV vs Base NAV, Portfolio P&L and Return %, reconciliation status badge, position-level collision breakdown table, and comparative matrix. |
| Backtest Panel | `apps/web/src/components/risk/diagnostics/VaRExceptionBacktestPanel.tsx` | Kupiec POF scorecards ($LR_{UC}$, p-value, critical value 3.8415), rolling VaR forecast vs realized loss SVG chart, and breach observations table. |
| Risk Hook | `apps/web/src/hooks/risk/useRiskTerminal.ts` | State machine and asynchronous actions for tail risk calculation, scenario execution, custom scenario creation, and rolling backtests. |
| Terminal Workspace | `apps/web/src/components/risk/RiskTerminalWorkspace.tsx` | Tabbed terminal layout integrating Overview, VaR & Expected Shortfall, Scenario Testing, and VaR Diagnostics alongside Stage 115 components. |
| Frontend Tests | `apps/web/src/lib/risk/__tests__/risk_tail_v1.test.ts` | 10 unit tests verifying formatting, Part XVI, Part XX, Part XXXIV, Part XLIII fixtures, and Kupiec critical values. |

---

## 5. Verification & Audit Results

- **Backend Pytest**:
  - `pytest apps/api/tests/test_risk_foundation_v1.py apps/api/tests/test_risk_tail_and_scenarios_v1.py`: **21 passed** with 0 failures.
  - Full suite: `pytest apps/api/tests/ -k risk`: **23 passed** with 0 failures.
- **Frontend Unit Tests**:
  - `node --test apps/web/src/lib/risk/__tests__/risk_tail_v1.test.ts apps/web/src/lib/risk/__tests__/risk_v1.test.ts`: **19 passed** with 0 failures.
- **TypeScript Typecheck**:
  - `pnpm.cmd --filter web exec tsc --noEmit`: Exited with code 0 (no type errors).
- **Next.js Production Build**:
  - `pnpm.cmd --filter web build`: Compiled successfully; all 38 static and dynamic routes (including `/risk`) generated cleanly.

