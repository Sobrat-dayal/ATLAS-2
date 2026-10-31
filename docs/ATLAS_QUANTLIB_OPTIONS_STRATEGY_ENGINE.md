# ATLAS STAGE 142: QUANTLIB DERIVATIVES VALUATION, STRATEGY AND RISK ANALYTICS ENGINE

## 1. Executive Summary

Stage 142 integrates official QuantLib-Python bindings (`quantlib==1.44`) into the ATLAS financial intelligence platform, establishing an institutional-grade derivatives pricing, multi-leg options strategy valuation, second-order Greeks, 2D scenario matrix, and risk analytics engine.

Stage 142 addresses the core analytical limitation of Stage 141: where Stage 141 modeled piecewise-linear intrinsic payoff strictly at expiration ($T = \text{Expiry}$), Stage 142 provides full mark-to-market Black-Scholes-Merton and American early-exercise valuation across intermediate dates ($t < T$). This enables rigorous mark-to-market pricing of multi-expiration structures such as Calendar Spreads, Diagonal Spreads, and rolling hedge positions.

---

## 2. Quantitative Architecture & Pricing Models

### 2.1 Supported Pricing Models

The engine registers 7 canonical pricing model definitions across closed-form and numerical methods:

1. **Analytic European Black-Scholes-Merton (`BLACK_SCHOLES_MERTON`)**:
   - Closed-form analytic solution (`ql.AnalyticEuropeanEngine`).
   - Closed-form exact Greeks ($\Delta$, $\Gamma$, $\Theta$, $\mathcal{V}$, $\rho$).
   - Applicable strictly to European-style exercise.

2. **Barone-Adesi-Whaley Approximation (`BARONE_ADESI_WHALEY`)**:
   - Quadratic analytical approximation for American vanilla options (`ql.BaroneAdesiWhaleyApproximationEngine`).
   - High computational efficiency for exchange-listed equity and index options.

3. **Bjerksund-Stensland 2002 Approximation (`BJERKSUND_STENSLAND`)**:
   - Generalized closed-form approximation for American options (`ql.BjerksundStenslandApproximationEngine`).
   - Superior numerical accuracy for deep-in-the-money American calls and long-dated contracts.

4. **Binomial Cox-Ross-Rubinstein (`BINOMIAL_CRR`)**:
   - Recombining lattice engine (`ql.BinomialCRRVanillaEngine`).
   - User-configurable time steps (default: 100 steps).
   - Accurately captures early exercise boundaries and discrete dividend drop points.

5. **Finite Differences Crank-Nicolson (`CRANK_NICOLSON_FD`)**:
   - PDE grid solver (`ql.FdBlackScholesVanillaEngine`).
   - Default: 100 time steps and 100 asset mesh grid points.
   - Robust convergence under complex boundary conditions.

6. **Black-76 Commodity & Futures Options (`BLACK_76`)**:
   - For futures-style options (`ql.BlackCalculator`).
   - Evaluates contracts based on discounted forward prices.

7. **Bachelier Normal Volatility Model (`BACHELIER`)**:
   - Arithmetic Brownian motion pricing (`ql.BachelierCalculator`).
   - Supports zero or negative underlying interest rates / spread strikes.

---

### 2.2 Thread-Safe Isolated Evaluation Context

QuantLib maintains global evaluation dates in process memory (`ql.Settings.instance().evaluationDate`). To prevent concurrent multi-tenant requests from corrupting each other's valuation dates:

- All QuantLib invocations execute within the `isolated_quantlib_context(eval_date)` context manager.
- A process-wide `threading.RLock()` ensures atomic evaluation date setting, calculation execution, and state restoration.

---

### 2.3 Greek Calculation Engine & Explicit Unit Conventions

The engine enforces strict Greek unit conventions to prevent ambiguity in financial applications:

| Greek | Mathematical Definition | ATLAS Display Unit | Conversion Rule |
| :--- | :--- | :--- | :--- |
| **Delta ($\Delta$)** | $\frac{\partial V}{\partial S}$ | per $\$1.00$ spot change | Direct $\Delta$ |
| **Gamma ($\Gamma$)** | $\frac{\partial^2 V}{\partial S^2}$ | per $\$1.00$ spot change squared | Direct $\Gamma$ |
| **Theta Daily ($\Theta_d$)** | $\frac{\partial V}{\partial t}$ | per calendar day decay | $\Theta_{annual} / 365$ |
| **Theta Annual ($\Theta_a$)** | $365 \cdot \Theta_d$ | per 365 calendar days | $\Theta_{daily} \cdot 365$ |
| **Vega Point ($\mathcal{V}_p$)** | $\frac{\partial V}{\partial \sigma} \cdot 0.01$ | per 1% point IV change | $\mathcal{V}_{unit} \cdot 0.01$ |
| **Vega Unit ($\mathcal{V}_u$)** | $\frac{\partial V}{\partial \sigma}$ | per 1.0 unit (100%) IV change | $\mathcal{V}_{point} \cdot 100$ |
| **Rho Point ($\rho_p$)** | $\frac{\partial V}{\partial r} \cdot 0.01$ | per 1% point rate shift | $\rho_{unit} \cdot 0.01$ |
| **Rho Basis Point ($\rho_{bp}$)** | $\frac{\partial V}{\partial r} \cdot 0.0001$ | per 1 bp rate shift | $\rho_{point} / 100$ |
| **Vanna** | $\frac{\partial^2 V}{\partial S \partial \sigma}$ | dDelta / dVol | Central finite difference |
| **Volga (Vomma)** | $\frac{\partial^2 V}{\partial \sigma^2}$ | dVega / dVol | Central finite difference |

When analytic Greeks are unavailable from numerical engines (e.g. Finite Differences or Binomial trees), the engine automatically falls back to central finite-difference perturbations:
$$\Delta \approx \frac{V(S + h_S) - V(S - h_S)}{2 h_S}$$
$$\Gamma \approx \frac{V(S + h_S) - 2V(S) + V(S - h_S)}{h_S^2}$$

---

### 2.4 Discrete Dividends Handling

For American options with known discrete dividend events prior to expiration:
- The engine constructs a `ql.DividendSchedule` populated with `ql.FixedDividend(amount, date)`.
- Models supporting discrete dividends (`BINOMIAL_CRR`, `CRANK_NICOLSON_FD`) evaluate the exact stock price drop at ex-dividend dates and calculate early exercise probability before each ex-dividend date.

---

### 2.5 Multi-Leg Options Strategy Engine

#### 25 Canonical Strategy Templates
The engine provides 25 canonical options strategy templates:
1. Long Call / Short Call
2. Long Put / Short Put
3. Covered Call / Protective Put
4. Bull Call Spread / Bear Call Spread
5. Bull Put Spread / Bear Put Spread
6. Long Straddle / Short Straddle
7. Long Strangle / Short Strangle
8. Long Iron Condor / Short Iron Condor
9. Long Iron Butterfly / Short Iron Butterfly
10. Long Calendar Spread / Short Calendar Spread
11. Long Diagonal Spread / Short Diagonal Spread
12. Collar / Reverse Collar
13. Call Ratio Spread / Put Ratio Spread
14. Call Backspread / Put Backspread
15. Box Spread (Arbitrage Rate Synthetic)

#### Pre-Expiration Valuation ($t < T$)
For any intermediate valuation date $t < T$, the engine computes the full mark-to-market net present value of each leg under QuantLib, aggregating Greeks with respect to position sign (+1 for long, -1 for short), quantity, and contract lot multiplier (100).

#### Unbounded Risk Detection
For strategies with naked short calls where the number of short calls exceeds long calls, the engine sets:
- `is_unbounded_loss = True`
- `max_loss = None`
- Injects explicit severity warning: `CRITICAL: Naked short call exposure detected. Maximum theoretical loss is mathematically infinite.`

---

### 2.6 2D Spot $\times$ Volatility Stress Matrix

The `ScenarioEngine` generates a 2D matrix evaluating mark-to-market portfolio value across simultaneous Spot price shifts (e.g. -10%, -5%, 0%, +5%, +10%) and Volatility shifts (e.g. -5%, 0%, +5%). Each grid cell reports:
- Net P&L Dollar ($) and Percentage (%)
- Mark-to-market position value
- Aggregate Delta, Gamma, Vega, and Theta under the stressed scenario.

---

### 2.7 Computational Governance & Boundaries

1. **Zero Fabrication**: No simulated execution fills, no fake broker balances, no synthetic Greeks without a documented quantitative pricing engine.
2. **Read-Only Quantitative Decision Support**: The engine is strictly a research and risk intelligence tool. No automated order placement, broker routing, or algorithmic execution is permitted.
3. **Multi-Tenant Isolation**: Saved strategies and custom positions are partitioned by tenant ID and owner principal sub with RLS validation.
4. **License Entitlements**: Options market data feeds (e.g., CBOE, OPRA) are checked for active licenses before calculation; revocation immediately blocks pricing requests.
