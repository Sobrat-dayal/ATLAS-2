# ATLAS — Portfolio Optimization and Quantitative Construction Platform (Stage 114)

## Executive Summary & Architecture Overview
The **Portfolio Optimization Engine** (ATLAS Stage 114 of 150) establishes institutional-grade quantitative portfolio construction capabilities on top of the Stage 110 accounting foundation, Stage 111 performance metrics, Stage 112 exposure classification, and Stage 113 performance attribution.

The platform provides mathematically validated, convex optimization formulations for multi-asset portfolios, including Markowitz Mean-Variance Utility, Analytical Minimum Variance, Target-Return Minimum Variance, Maximum Sharpe Ratio, Spinu Logarithmic Equal Risk Contribution (Risk Parity), Efficient Frontier tracing, and Rebalancing Proposals with turnover control.

---

## Canonical Roadmap Integration
```
Stage 110: Portfolios V1 (Accounts, Transactions, Positions, Cash, Valuation)
  │
  ├── Stage 111: Portfolio Performance Analytics (TWR, MWR, IRR, Cash-Flow Adjustments)
  │     │
  │     └── Stage 112: Portfolio Allocation & Exposure Intelligence (GICS, Asset Class, Geography)
  │           │
  │           └── Stage 113: Portfolio Performance Attribution (Brinson Decomposition, Carino Linking)
  │                 │
  │                 └── Stage 114: Portfolio Optimization & Construction (THIS STAGE)
```

---

## Mathematical Formulations

### 1. Modern Portfolio Theory (Mean-Variance Quadratic Utility)
$$\min_{w \in \mathbb{R}^N} \quad \frac{1}{2} w^T \Sigma w - \lambda w^T \mu$$
$$\text{subject to} \quad \sum_{i=1}^N w_i = 1, \quad 0 \le w_i \le 1 \quad (\text{or custom bounds})$$
- $\Sigma \in \mathbb{R}^{N \times N}$: Annualized covariance matrix (positive semi-definite).
- $\mu \in \mathbb{R}^N$: Annualized expected return vector.
- $\lambda \ge 0$: Investor risk aversion parameter.
- Analytical Gradient: $\nabla f(w) = \Sigma w - \lambda \mu$.
- Solved via Scipy Sequential Least Squares Programming (`SLSQP`).

### 2. Analytical Minimum Variance
$$\min_{w \in \mathbb{R}^N} \quad w^T \Sigma w \quad \text{s.t.} \quad \sum w_i = 1, \quad w_i \ge 0$$
- Unconstrained two-asset analytical benchmark (Part XXIX):
$$w_1^* = \frac{\sigma_2^2 - \sigma_{12}}{\sigma_1^2 + \sigma_2^2 - 2\sigma_{12}}, \quad w_2^* = 1 - w_1^*$$

### 3. Maximum Sharpe Ratio
$$\max_{w \in \mathbb{R}^N} \quad \frac{w^T \mu - r_f}{\sqrt{w^T \Sigma w}} \quad \text{s.t.} \quad \sum w_i = 1, \quad w_i \ge 0$$
- Formulated as minimizing $-\text{Sharpe}(w)$ with numerical gradient.

### 4. Equal Risk Contribution / Risk Parity (Spinu Convex Logarithmic Barrier)
Traditional risk budgeting sets:
$$RC_i = w_i (\Sigma w)_i = \frac{1}{N} \sigma_p^2 \quad \forall i$$
Direct minimization of $\sum (RC_i - \sigma_p^2 / N)^2$ is non-convex. ATLAS implements Florin Spinu's (2013) strictly convex unconstrained formulation:
$$\min_{y \in \mathbb{R}_{++}^N} \quad \frac{1}{2} y^T \Sigma y - c \sum_{i=1}^N \ln(y_i)$$
$$\text{Gradient:} \quad \nabla f(y) = \Sigma y - \frac{c}{y}$$
Solved via `L-BFGS-B`, then normalized:
$$w_i^* = \frac{y_i^*}{\sum_{j=1}^N y_j^*}$$
Guarantees global uniqueness with marginal risk discrepancy $< 10^{-6}$.

### 5. Well-Conditioned Covariance Estimation (Ledoit-Wolf Shrinkage)
$$\Sigma_{LW} = \delta F + (1 - \delta) S$$
- $S$: Sample covariance matrix.
- $F$: Structured diagonal target (constant variance).
- $\delta \in [0, 1]$: Asymptotically optimal shrinkage intensity.
- Positive semi-definite verification ($\lambda_{\min} \ge 10^{-7}$) with diagonal loading jitter if required.

### 6. Rebalancing Proposals & Turnover
$$\text{Turnover} = \frac{1}{2} \sum_{i=1}^N |w_{i,\text{cand}} - w_{i,\text{curr}}|$$
$$\Delta V_i = (w_{i,\text{cand}} - w_{i,\text{curr}}) \cdot \text{NAV}$$
$$\text{Transaction Cost} = c \sum_{i=1}^N |\Delta w_i| \cdot \text{NAV}$$
Enforces zero cash leak ($|\sum \Delta V_i| < 10^{-4}$ for fully invested portfolios).

---

## API Endpoints (`/api/v1/portfolios/{id}/optimization/...`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/studies` | Create a new named optimization research study |
| `GET` | `/studies` | List active and archived optimization studies |
| `GET` | `/studies/{id}` | Retrieve optimization study by ID |
| `DELETE` | `/studies/{id}` | Archive optimization study |
| `POST` | `/runs` | Execute optimization run with objective and constraints |
| `GET` | `/runs` | List execution runs for portfolio or study |
| `GET` | `/runs/latest` | Retrieve latest optimization run |
| `GET` | `/runs/{id}` | Retrieve specific optimization run |
| `GET` | `/runs/{id}/candidate` | Candidate weights and portfolio risk/return |
| `GET` | `/runs/{id}/frontier` | Pareto-optimal efficient frontier points |
| `GET` | `/runs/{id}/comparison` | Current vs candidate weight shifts and trades |
| `GET` | `/runs/{id}/diagnostics` | Solver diagnostics, iters, PSD status, hashes |
| `GET` | `/universe` | Eligible asset universe with sector metadata |
| `POST` | `/constraints/validate` | Pre-check linear feasibility and budget bounds |
| `GET` | `/methodologies` | Catalog of mathematical objectives and models |

---

## Frontend Workspaces (`/portfolios` -> Optimization & Frontier)

1. **Optimization Summary Cards**: Expected Return, Portfolio Volatility, Sharpe Ratio, Turnover %, Estimated Costs, Solver Status.
2. **Efficient Frontier Chart**: Interactive SVG curve with discrete points, Dominated-point filtering, and Current vs Candidate vs Tangency vs Min-Var markers.
3. **Current vs Candidate Table**: Side-by-side weight breakdown, value deltas, buy/sell flags, and self-funding confirmation.
4. **Candidate Allocation Chart**: Structural sectoral and security-level allocation shift visualization.
5. **Optimization Constraint Builder**: Interactive form to add/remove regulatory and concentration caps, with instant feasibility pre-check.
6. **Hypothetical Trade Proposals**: Order ticket proposals with prominent institutional non-execution disclosure banner.
7. **Solver Diagnostics Inspector**: Iterations, solve time in ms, KKT stationarity, PSD verification, condition number, and input SHA-256 hash.
8. **Sensitivity Scenarios Grid**: Stress testing under alpha shocks (+100 bps) and risk aversion spectrum ($\lambda \in [1.0, 4.0]$).
9. **Mathematical Methodology Inspector**: Expandable mathematical formulation disclosures and citations.
10. **Study Manager**: Named study organization and multi-universe mandate preservation.
