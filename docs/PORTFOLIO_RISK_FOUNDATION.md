# ATLAS — Stage 115: Portfolio Risk Foundation and Core Market-Risk Analytics

## Institutional Financial Risk Management Engine

### Executive Summary

ATLAS Stage 115 establishes the scientifically defensible, production-grade foundation for financial risk analysis across investment portfolios, accounts, benchmarks, and individual securities. The system provides mathematically precise, deterministic, and auditable calculations for:

1. **Portfolio Market-Risk Measurement**: Volatility, sample variance, Bessel correction ($N-1$), annualization policies ($K = 252, 52, 12$), and rolling volatility without hindsight bias.
2. **Drawdown Analytics**: Continuous cash-flow-neutral wealth index tracking, running peak detection, drawdown profiles ($D_t = W_t/P_t - 1$), maximum drawdown, current drawdown, and episode extraction (peak, trough, recovery horizons).
3. **Benchmark Sensitivity**: Covariance, Pearson correlation ($\rho$), historical beta ($\beta = \frac{Cov(P, B)}{Var(B)}$), annualized active tracking error ($TE$), with detection and safe disclosure of degenerate benchmark variance.
4. **Covariance Diagnostics & Euler Risk Contributions**: Model-estimated volatility ($\sqrt{w^T \Sigma w}$), Positive Semi-Definite (PSD) verification ($\lambda_{min} \ge 10^{-7}$), condition number ($\kappa$), Ledoit-Wolf diagonal shrinkage regularization, diversification ratio ($DR$), and security-level Euler risk decomposition ($VC_i, MRC_i, CRC_i, PCR_i$) with strict additivity reconciliation.
5. **Multi-Currency Risk Measurement**: Exact geometric compounding of local return and FX return ($1 + R_{base} = (1 + R_{local})(1 + R_{FX})$) and cash volatility.
6. **Data Quality Governance**: Observation coverage ratio, missing date interval audit, staleness detection, and reproducible input manifests with cryptographic hashing.
7. **Bloomberg-Style Risk Terminal**: Global route `/risk` and integrated tab in `/portfolios`, featuring interactive SVG charts, correlation heatmaps, episode tables, and methodology inspector.

---

### Canonical Roadmap Position

| Stage | Responsibility |
|---|---|
| 110 | Portfolios V1: Accounts, Transactions, Positions, Cash and Valuation |
| 111 | Portfolio Performance: TWR, MWR, XIRR, Equity Curves, Benchmarks |
| 112 | Portfolio Allocation & Exposure: GICS, Geography, Currency, Look-Through |
| 113 | Portfolio Attribution: Brinson-Fachler, Selection, Interaction, Linking |
| 114 | Portfolio Optimization: Mean-Variance, Efficient Frontier, Risk Parity |
| **115** | **Portfolio Risk Foundation & Core Market-Risk Analytics (Current)** |
| 116 | Value at Risk (VaR), Expected Shortfall (CVaR) and Tail Risk (Deferred) |
| 117 | Stress Testing, Scenario Analysis & Reverse Stress Testing (Deferred) |
| 118 | Portfolio Risk Limits, Warnings, and Breach Escalations (Deferred) |

---

### Core Mathematical Formulations

#### 1. Historical Volatility & Sample Variance
For a return series $R = [R_1, R_2, \dots, R_T]$ with $T \ge 2$:
$$\bar{R} = \frac{1}{T} \sum_{t=1}^T R_t$$
$$s^2 = \frac{1}{T - 1} \sum_{t=1}^T (R_t - \bar{R})^2$$
$$s = \sqrt{s^2}$$
$$\sigma_{annual} = s \cdot \sqrt{K}$$
where $K = 252$ for daily, $K = 52$ for weekly, and $K = 12$ for monthly sampling.

*Part XV Verification Fixture*: For alternating daily returns $[+1\%, -1\%, +1\%, -1\%]$, sample mean $\bar{R} = 0.0$, sample variance $s^2 = \frac{0.0004}{3} \approx 0.00013333$, period volatility $s \approx 1.1547\%$, and annualized volatility ($K=252$) is exactly:
$$\sigma_{annual} \approx 0.011547005 \cdot \sqrt{252} \approx 18.3303\%$$

#### 2. Cash-Flow-Neutral Drawdown & Watermark Analytics
From the Stage 111 cash-flow-adjusted wealth index $W_t$:
$$P_t = \max_{0 \le \tau \le t} W_\tau$$
$$D_t = \frac{W_t}{P_t} - 1.0$$
$$\text{MDD} = \min_{0 \le t \le T} D_t$$
$$\text{CDD} = D_T = \frac{W_T}{P_T} - 1.0$$

*Part XXI Verification Fixture*: Wealth index $[100, 120, 90, 99, 130]$ produces running peaks $[120, 120, 120, 130]$, drawdowns $[0\%, 0\%, -25\%, -17.5\%, 0\%]$, maximum drawdown $-25.0\%$, and empirical recovery at observation index 4 ($130 > 120$).

#### 3. Benchmark Sensitivity
Given matched observations $(R_{P, t}, R_{B, t})$:
$$\text{Cov}(P, B) = \frac{1}{T - 1} \sum_{t=1}^T (R_{P, t} - \bar{R}_P)(R_{B, t} - \bar{R}_B)$$
$$\beta = \frac{\text{Cov}(P, B)}{s_B^2}$$
$$\rho = \frac{\text{Cov}(P, B)}{s_P \cdot s_B}$$
$$\text{TE}_{annual} = \sqrt{K} \cdot \sqrt{\frac{1}{T - 1} \sum_{t=1}^T \left( (R_{P, t} - R_{B, t}) - (\bar{R}_P - \bar{R}_B) \right)^2}$$

*Part XXVIII Verification Fixture*: When $R_P = 2 R_B$, $\beta = 2.0$ and $\rho = 1.0$ exactly. When $s_B^2 = 0$, the engine raises `RiskBenchmarkVarianceZeroError` and returns `ZERO_VARIANCE` metric status.

#### 4. Covariance Parametric Risk & Euler Risk Decomposition
Given weight vector $w$ and covariance matrix $\Sigma$:
$$\sigma_P^2 = w^T \Sigma w$$
$$\sigma_P = \sqrt{w^T \Sigma w}$$

By Euler's homogeneous function theorem, the total portfolio volatility decomposes into additive constituent contributions:
- **Variance Contribution**: $VC_i = w_i (\Sigma w)_i \implies \sum_{i=1}^N VC_i = \sigma_P^2$
- **Marginal Volatility Contribution**: $MRC_i = \frac{(\Sigma w)_i}{\sigma_P} = \frac{\partial \sigma_P}{\partial w_i}$
- **Component Volatility Contribution**: $CRC_i = w_i \cdot MRC_i \implies \sum_{i=1}^N CRC_i = \sigma_P$
- **Percentage Contribution to Risk**: $PCR_i = \frac{CRC_i}{\sigma_P} \implies \sum_{i=1}^N PCR_i = 1.0$ (100%)

*Part XXXV & XL Verification Fixture*: 2 uncorrelated assets with $\Sigma = \text{diag}(0.04, 0.09)$ and weights $w = [0.5, 0.5]$:
$$\sigma_P^2 = (0.5)^2(0.04) + (0.5)^2(0.09) = 0.01 + 0.0225 = 0.0325$$
$$\sigma_P = \sqrt{0.0325} \approx 18.027756\%$$
$$VC = [0.01, 0.0225]$$
$$PCR = [30.7692\%, 69.2308\%]$$
Euler additivity holds strictly.

#### 5. Multi-Currency Return Geometric Compounding
$$1 + R_{base} = (1 + R_{local})(1 + R_{FX})$$
$$R_{base} = R_{local} + R_{FX} + (R_{local} \cdot R_{FX})$$

---

### Backend Architecture

```
python/atlas/src/atlas/risk/
├── enums.py                # RiskSubjectType, RiskMetricCode, RiskModelType, etc.
├── errors.py               # 24 typed domain exceptions inheriting from RiskError
├── models.py               # Immutable domain dataclasses
├── schemas.py              # Pydantic V2 DTOs matching frontend contracts
├── volatility.py           # Sample volatility, Bessel variance, rolling window
├── drawdown.py             # Wealth index, peaks, drawdowns, episode extraction
├── benchmark.py            # Covariance, Beta, Correlation, Tracking Error
├── covariance_risk.py      # Euler risk decomposition, PSD check, condition number
├── multi_currency.py       # Geometric currency compounding & foreign cash
├── quality.py              # Coverage ratio, missing interval and staleness audits
├── reconciliation.py       # Euler additivity & covariance identity verification
├── service.py              # Multi-tenant orchestrator, registries, caching
└── __init__.py             # Public exports

apps/api/src/atlas_api/routers/risk.py  # 13 REST API endpoints with auth & multi-tenancy
apps/api/tests/test_risk_foundation_v1.py # 12 pytest verification fixtures
```

---

### Frontend Architecture

```
apps/web/src/
├── lib/risk/
│   ├── types.ts            # DTOs, Enums, Response contracts
│   ├── formatting.ts       # Institutional formatters & status badges
│   ├── api.ts              # Typed fetch client for all /risk endpoints
│   └── __tests__/
│       └── risk_v1.test.ts # Node test runner verifying math reference fixtures
├── hooks/risk/
│   └── useRiskTerminal.ts  # Workspace state, selection, calculation lifecycle
├── components/risk/
│   ├── RiskHeader.tsx               # Portfolio, account, benchmark, model selectors
│   ├── RiskOverviewSummary.tsx       # Bloomberg-style KPI cards & coverage bar
│   ├── HistoricalVolatilityChart.tsx # SVG rolling volatility chart with window selector
│   ├── DrawdownChart.tsx            # SVG underwater drawdown valley fill & peak marker
│   ├── DrawdownEpisodesTable.tsx    # Line-item episodes, trough, and recovery horizons
│   ├── BenchmarkSensitivityPanel.tsx# Beta, correlation, tracking error, caveats
│   ├── CovarianceDiagnosticsPanel.tsx# PSD status, condition number, correlation heatmap
│   ├── RiskContributionTable.tsx    # Euler decomposition table & reconciliation footer
│   ├── RiskModelInspector.tsx       # Model definitions, formulas, and limitations
│   ├── RiskDataQualityPanel.tsx     # Observation coverage, intervals, and input hash
│   ├── RiskRunHistory.tsx           # Audit log of persisted calculation runs
│   └── RiskTerminalWorkspace.tsx    # Master multi-tab workspace
└── app/(atlas)/risk/page.tsx        # Global route rendering RiskTerminalWorkspace
```

---

### Quality Gates & Verification

- **Backend Pytest**: 12/12 passing (`test_risk_foundation_v1.py`).
- **Regression Suite**: 52/52 passing across Stages 110–115 (`test_portfolios_v1.py`, `test_portfolio_performance_v1.py`, `test_portfolio_exposure_v1.py`, `test_portfolio_attribution_v1.py`, `test_portfolio_optimization_v1.py`, `test_risk_foundation_v1.py`).
- **Frontend Unit Tests**: 148/148 passing (`pnpm test`).
- **Type Checking**: 0 errors (`pnpm exec tsc --noEmit`).
- **Production Build**: Complete success (`pnpm build`).
- **Safety**: Pure read-only calculations; never mutates portfolio accounting ledgers or submits orders.

