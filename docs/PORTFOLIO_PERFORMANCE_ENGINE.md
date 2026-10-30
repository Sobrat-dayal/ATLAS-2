# ATLAS Portfolio Performance Analytics Engine (Stage 111)

## Institutional-Grade Portfolio Performance Analytics Engine

The **ATLAS Portfolio Performance Analytics Engine** provides institutional-grade, mathematically verified portfolio return measurement built directly on the Stage 110 double-entry transaction ledger and marked portfolio valuation foundation.

It implements CFA Institute / GIPS-aligned return calculations, strictly eliminating common naive return fallacies and providing complete cryptographic transparency.

---

## 1. Core Mathematical Methodologies

### 1.1 Time-Weighted Return (TWR) — Exact Subperiod Segmentation

TWR measures the compound rate of growth of a portfolio, completely removing the distorting effects of external investor cash inflows and outflows.

#### Mathematical Formulation:
For $T$ subperiods bounded by external cash flows:
$$R_{\text{twr}} = \prod_{i=1}^{T} (1 + R_i) - 1$$

Where each discrete subperiod return $R_i$ is computed from pre-flow valuations:
$$R_i = \frac{V_{i,\text{pre}} - V_{i-1,\text{post}}}{V_{i-1,\text{post}}}$$

- **Boundary Segmentation Rule**: A new subperiod is initiated **only** when an external investor flow (`EXTERNAL_CONTRIBUTION` or `EXTERNAL_WITHDRAWAL`) occurs.
- **Reference Fixture (Part XIII)**:
  - Subperiod 1: $\$100 \to \$110 \implies R_1 = +10.0\%$
  - External Contribution: $+\$50$ at start of Subperiod 2 $\implies$ starting capital $\$160$
  - Subperiod 2: $\$160 \to \$176 \implies R_2 = +10.0\%$
  - Compound TWR: $(1 + 0.10) \times (1 + 0.10) - 1 = \mathbf{21.0\%}$
  - *Strictly rejects naive ending/beginning calculation $\frac{\$176 - \$100}{\$100} = 76.0\%$.*

### 1.2 Modified Dietz Approximate TWR

When exact pre-flow subperiod valuations are not available (e.g. historical periods with only beginning and ending marks):
$$R_{\text{dietz}} = \frac{V_e - V_b - F}{V_b + \sum_{t} F_t \cdot W_t}$$

Where the flow day-weight $W_t$ is:
$$W_t = \frac{CD - D_t}{CD}$$
- $CD$: Total calendar days in the period
- $D_t$: Days from the beginning of the period to the flow date

### 1.3 Money-Weighted Return (MWR / XIRR)

MWR calculates the Internal Rate of Return (IRR) on all dated cash flows from the investor's perspective.

#### Mathematical Formulation:
$$\sum_{t=0}^{N} \frac{C_t}{(1 + r)^{\frac{d_t - d_0}{365}}} = 0$$

- **Investor Perspective Convention**:
  - Contributions / Deposits: Negative flow ($C_t < 0$)
  - Withdrawals: Positive flow ($C_t > 0$)
  - Terminal Marked Valuation: Positive liquidation-equivalent flow ($C_N > 0$)
- **Day-Count Convention**: ACT/365 (365.0 days)
- **Bounded Numerical Solver**:
  - Uses Newton-Raphson iteration with analytic derivative:
    $$f'(r) = -\sum_{t=0}^{N} \left(\frac{d_t - d_0}{365}\right) \cdot \frac{C_t}{(1 + r)^{\frac{d_t - d_0}{365} + 1}}$$
  - Bounded search interval: $r \in [-0.9999, 50.0]$
  - Guaranteed bisection fallback if Newton iterates step out of bounds or fail to converge within 100 iterations.
- **Multiple Roots Diagnostics**: Evaluates Descartes' rule of signs on cumulative net cash flows. If multiple sign changes exist, flags an explicit warning informing the analyst of non-unique internal rate of return roots.
- **Reference Fixture (Part XIX)**: $-\$1,000$ at $t_0$, $+\$1,100$ at $t_0 + 365 \text{ days} \implies \mathbf{10.0\%}$ annualized IRR.

### 1.4 Geometric Annualization (CAGR)

For measurement periods spanning 1 year or longer ($D \ge 365$ calendar days):
$$R_{\text{ann}} = (1 + R_{\text{cum}})^{\frac{365.25}{D}} - 1$$

- **Guardrail**: If $D < 365$ days, annualized return is strictly returned as `null` / `N/A`, preventing misleading extrapolation of short-term volatility.

---

## 2. Cash Flow Classification Matrix

Transactions are deterministically classified based on whether they cross the boundary of the measured entity:

| Transaction Type | Scope: PORTFOLIO | Scope: ACCOUNT | Classification | Flow Amount ($F_t$) |
|---|---|---|---|---|
| `CASH_DEPOSIT` | Crosses boundary | Crosses boundary | `EXTERNAL_CONTRIBUTION` | Positive flow |
| `CASH_WITHDRAWAL` | Crosses boundary | Crosses boundary | `EXTERNAL_WITHDRAWAL` | Negative flow |
| `BUY` / `SELL` | Internal trade | Internal trade | `INTERNAL_SECURITY_TRADE` | $0.00$ flow |
| `CASH_DIVIDEND` | Internal income | Internal income | `INTERNAL_INCOME` | $0.00$ flow |
| `CASH_INTEREST` | Internal income | Internal income | `INTERNAL_INCOME` | $0.00$ flow |
| `ACCOUNT_FEE` | Internal fee | Internal fee | `INTERNAL_FEE` | $0.00$ flow |
| `CASH_TRANSFER_IN` | Internal between accounts | External into account | `INTERNAL_TRANSFER` / `EXTERNAL_CONTRIBUTION` | $0.00$ / $+Amount$ |
| `CASH_TRANSFER_OUT` | Internal between accounts | External out of account | `INTERNAL_TRANSFER` / `EXTERNAL_WITHDRAWAL` | $0.00$ / $-Amount$ |
| `STOCK_SPLIT` | Non-cash corporate action | Non-cash corporate action | `CORPORATE_ACTION_NONCASH` | $0.00$ flow |

---

## 3. Multi-Currency Performance Engine

When portfolio investments and cash balances are denominated in currencies differing from the portfolio's base reporting currency:

1. **Cash Flow Conversion**: Converted at the verified European Central Bank / market spot FX rate on the **exact flow date**.
2. **Valuation Point Conversion**: Valuations are converted at the spot FX rate as of each **valuation timestamp**.
3. **Reference Fixture (Part XXXIV)**:
   - Native USD: Starts at $\$100.00$, ends at $\$110.00 \implies R_{\text{USD}} = \mathbf{10.0\%}$
   - Historical FX (USD/INR): Starts at $80.0$, ends at $90.0$
   - Base INR Starting Valuation: $100 \times 80 = 8,000 \text{ INR}$
   - Base INR Ending Valuation: $110 \times 90 = 9,900 \text{ INR}$
   - Base INR Return: $\frac{9,900 - 8,000}{8,000} = \mathbf{23.75\%}$

---

## 4. Canonical Market Benchmarks

Built-in institutional benchmarks for relative performance attribution:

1. **`BENCHMARK_SP500`**: S&P 500 Index (`PRICE_RETURN`, USD)
   - *Requires Price vs Total Return compliance notice when compared against total return portfolios.*
2. **`BENCHMARK_SPY`**: SPDR S&P 500 ETF Trust (`TOTAL_RETURN`, USD)
3. **`BENCHMARK_NASDAQ100`**: NASDAQ 100 Index (`PRICE_RETURN`, USD)
4. **`BENCHMARK_ACWI`**: MSCI All Country World Index (`TOTAL_RETURN`, USD)

### Comparative Metrics:
- **Arithmetic Difference / Relative Return**:
  $$\Delta R = R_{\text{portfolio}} - R_{\text{benchmark}}$$
- **Rebased Index Series**: Both series normalized to $100.00$ at period start for visual tracking.

---

## 5. Cryptographic Provenance & Auditability

Every performance calculation produces an immutable snapshot containing:
- **`run_id`**: Universally unique execution identifier
- **`calculation_version`**: Semantic calculation engine version tag
- **`input_hash`**: SHA-256 digest of input parameters (period bounds, transaction count, ledger revision tag, methodology)
- **`data_quality`**: Granular tracking of missing prices, missing FX rates, and stale quotes

---

## 6. REST API Endpoints

Mounted under `/api/v1/portfolios`:

- `GET /benchmarks`: List available canonical benchmarks
- `GET /{portfolio_id}/performance`: Retrieve active performance summary for a period
- `POST /{portfolio_id}/performance/calculate`: Trigger immutable calculation run
- `GET /{portfolio_id}/performance/runs`: List historical calculation runs
- `GET /{portfolio_id}/performance/runs/{run_id}`: Inspect specific historical run
- `GET /{portfolio_id}/performance/series`: Time-series equity curve and rebased growth curve
- `GET /{portfolio_id}/performance/periodic`: Monthly and annual periodic returns grid
- `GET /{portfolio_id}/performance/cash-flows`: Classified cash flow schedule
- `GET /{portfolio_id}/performance/data-quality`: Data completeness and mark audit

---

## 7. Frontend Bloomberg-Style Workspace

Located at `/portfolios` under the **Performance Analytics** tab:
- **Summary KPI Cards**: TWR Cumulative, Annualized Return (CAGR), Money-Weighted (XIRR), Net Investment Gain, Balance Reconciliation
- **Time-Weighted Growth Chart**: Rebased growth comparison ($100.00$ start) with benchmark overlay and interactive cash flow milestone dots
- **Portfolio Value Chart**: Historical monetary equity curve with shaded area and crosshair inspection
- **Periodic Returns Table**: Monthly matrix (Jan..Dec + Full Year) with variance heat-shading
- **Cash Flow Ledger**: Table with investor vs portfolio perspective discrimination
- **Benchmark Analysis**: Relative performance card, arithmetic difference, and total return compliance warning
- **Methodology Inspector**: Slide-over audit modal detailing mathematical formulations and input hash
- **Data Quality Panel**: Audit status and quote freshness diagnostics
- **Run History**: Immutable audit log of past calculation runs

