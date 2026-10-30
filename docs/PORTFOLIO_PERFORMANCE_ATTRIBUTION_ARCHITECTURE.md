# ATLAS Portfolio Performance Attribution Architecture (Stage 113)

## 1. Executive Summary

Stage 113 delivers the institutional-grade **Portfolio Performance Attribution Architecture** for ATLAS. Building directly upon the Stage 110 Portfolio Accounting ledger, Stage 111 Performance Analytics (Time-Weighted Returns, Money-Weighted Returns), and Stage 112 Multi-Dimensional Exposure Intelligence, this module decomposes observed portfolio results relative to financial market benchmarks into mathematically rigorous, auditable, and source-grounded active return components.

```
                                    ┌────────────────────────────────────────────────────────┐
                                    │             Active Return: R_P - R_B                   │
                                    └───────────────────────────┬────────────────────────────┘
                                                                │
                   ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
                   ▼                                            ▼                                            ▼
   ┌───────────────────────────────┐            ┌───────────────────────────────┐            ┌───────────────────────────────┐
   │       Allocation Effect       │            │       Selection Effect        │            │      Interaction Effect       │
   │  A_k = (w_P - w_B)(R_B - R_0) │            │     S_k = w_B · (R_P - R_B)   │            │   I_k = (w_P - w_B)(R_P - R_B)│
   └───────────────────────────────┘            └───────────────────────────────┘            └───────────────────────────────┘
                   │                                            │                                            │
                   └────────────────────────────────────────────┼────────────────────────────────────────────┘
                                                                ▼
                                    ┌────────────────────────────────────────────────────────┐
                                    │    Five-Point Mathematical Reconciliation Engine       │
                                    │        Reconstructed Port ≡ Port Return (Δ = 0 bps)    │
                                    │        Reconstructed Bench ≡ Bench Ret  (Δ = 0 bps)    │
                                    │        Total Attributed ≡ Active Return (Δ = 0 bps)    │
                                    │        Security Contributions Sum ≡ Port Ret (Δ = 0)   │
                                    │        Residual ≤ 10^-4 (Strict Tolerance Verification)│
                                    └────────────────────────────────────────────────────────┘
```

---

## 2. Core Mathematical Methodologies

### 2.1 Brinson-Fachler Decomposition (1985)
The primary institutional arithmetic attribution methodology. Sector allocation is evaluated relative to total benchmark return ($R_B$), rewarding positive allocation decisions and penalizing overweights in sectors that underperformed the broader market:

$$\Delta R = R_P - R_B = \sum_{k} \left( A_k + S_k + I_k \right)$$

Where for each category or sector $k$:
- **Allocation Effect ($A_k$)**:
  $$A_k = (w_{P,k} - w_{B,k}) \cdot (R_{B,k} - R_B)$$
- **Selection Effect ($S_k$)**:
  $$S_k = w_{B,k} \cdot (R_{P,k} - R_{B,k})$$
- **Interaction Effect ($I_k$)**:
  $$I_k = (w_{P,k} - w_{B,k}) \cdot (R_{P,k} - R_{B,k})$$
- **Total Category Effect ($E_k$)**:
  $$E_k = A_k + S_k + I_k$$

### 2.2 Brinson-Hood-Beebower Decomposition (1986)
The classic baseline decomposition without benchmark mean subtraction. Implemented alongside Brinson-Fachler for institutional comparability with legacy custodial reporting:

$$A_k^{BHB} = (w_{P,k} - w_{B,k}) \cdot R_{B,k}$$

### 2.3 Off-Benchmark Categories & Cash Drag
When a portfolio holds assets or cash outside benchmark constituents ($w_{B,k} = 0$):
- **Allocation Effect**: $(w_{P,k} - 0) \cdot (R_B - R_B) = 0.00$ (in Brinson-Fachler).
- **Selection Effect**: $0.00 \cdot (R_{P,k} - R_B) = 0.00$.
- **Interaction / Residual Effect**: $(w_{P,k} - 0) \cdot (R_{P,k} - R_B) = w_{P,k} \cdot (R_{P,k} - R_B)$.
This precisely captures the cash drag or off-benchmark excess performance without distorting benchmark-matched segments.

### 2.4 Multi-Period Compounding (Carino Logarithmic Linking)
To overcome the mathematical impossibility of summing single-period arithmetic attribution across compounded multi-period horizons, ATLAS implements the Carino (1999) logarithmic linking methodology.

For each discrete sub-period $t \in [1, \dots, T]$:
$$c_t = \frac{\ln(1 + R_{P,t}) - \ln(1 + R_{B,t})}{R_{P,t} - R_{B,t}} \cdot \frac{R_P^{comp} - R_B^{comp}}{\ln(1 + R_P^{comp}) - \ln(1 + R_B^{comp})}$$

With limiting case handling as $R_{P,t} \to R_{B,t}$:
$$c_t \to \frac{1}{1 + R_{B,t}} \cdot \frac{R_P^{comp} - R_B^{comp}}{\ln(1 + R_P^{comp}) - \ln(1 + R_B^{comp})}$$

The linked cumulative attribution effects satisfy the exact additivity identity:
$$\sum_{t=1}^T c_t \cdot A_t + \sum_{t=1}^T c_t \cdot S_t + \sum_{t=1}^T c_t \cdot I_t \equiv R_P^{comp} - R_B^{comp}$$

### 2.5 Security-Level Absolute Return Contributions
Each asset $j$ in the portfolio contributes to total portfolio return according to its average or beginning NAV weight:
$$C_j = w_{P,j} \cdot R_{P,j}$$
$$\sum_{j} C_j \equiv R_P$$
Rankings are generated to highlight the **Top 5 Return Contributors** and **Top 5 Return Detractors**.

### 2.6 Multi-Currency Local/FX Decomposition
Unhedged international equity holdings undergo three-way currency decomposition:
$$R_{base} = R_{local} + R_{FX} + (R_{local} \cdot R_{FX})$$
Where:
- $R_{local}$: Asset performance in local quotation currency.
- $R_{FX}$: Currency appreciation/depreciation vs reporting currency.
- $R_{local} \cdot R_{FX}$: Cross-product compounding interaction term.

---

## 3. Five-Point Audit & Mathematical Reconciliation

To satisfy institutional audit standards, each attribution calculation run executes 5 independent verification checks:

1. **Portfolio Return Reconstruction**: $\left|\sum w_{P,k} R_{P,k} - R_P\right| \le \text{tolerance}$
2. **Benchmark Return Reconstruction**: $\left|\sum w_{B,k} R_{B,k} - R_B\right| \le \text{tolerance}$
3. **Active Return Additivity**: $\left|\left( \sum A_k + \sum S_k + \sum I_k \right) - (R_P - R_B)\right| \le \text{tolerance}$
4. **Security Contributions Sum**: $\left|\sum C_j - R_P\right| \le \text{tolerance}$
5. **Residual Boundedness**: $\text{Residual} \le 10^{-4}$ ($1.0$ bps).

Each calculation is assigned a cryptographic **SHA-256 Input Provenance Hash** computed over holdings weights, prices, benchmark snapshot weights, and returns, guaranteeing complete determinism and reproducibility.

---

## 4. REST API Endpoints

The API is mounted under `/api/v1/portfolios/{portfolio_id}/attribution`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/attribution` | Retrieves the latest valid performance attribution run. |
| `POST` | `/attribution/calculate` | Executes an on-demand calculation with specified benchmark, method, or dates. |
| `GET` | `/attribution/runs` | Lists historical attribution calculation runs. |
| `GET` | `/attribution/runs/{run_id}` | Retrieves a specific historical run by ID with tenant isolation. |
| `GET` | `/attribution/effects` | Retrieves allocation, selection, and interaction effects across categories. |
| `GET` | `/attribution/securities` | Retrieves security-level return contributions and rankings. |
| `GET` | `/attribution/sectors` | Retrieves GICS sector-level decomposition. |
| `GET` | `/attribution/industries` | Retrieves industry group-level decomposition. |
| `GET` | `/attribution/currencies` | Retrieves multi-currency local/FX decomposition. |
| `GET` | `/attribution/history` | Retrieves discrete sub-period historical attribution series. |
| `GET` | `/attribution/linked` | Retrieves Carino multi-period logarithmic linked attribution results. |
| `GET` | `/attribution/reconciliation` | Retrieves 5-point mathematical audit checks and tolerance status. |
| `GET` | `/attribution/data-quality` | Retrieves coverage ratios and cryptographic SHA-256 hash. |
| `GET` | `/attribution/benchmarks` | Lists supported benchmarks with constituent metadata. |

---

## 5. Bloomberg-Style Frontend Workspace

The frontend workspace provides a high-density, Bloomberg-style analytical interface:
- **`AttributionSummaryCards`**: High-contrast KPI metric cards for Portfolio Return, Benchmark Return, Active Return, Allocation Effect, Selection Effect, Interaction Effect, and Audit Status.
- **`ActiveReturnWaterfall`**: Dynamic decomposition chart bridging zero to total active return.
- **`SectorAttributionTable`**: Dense tabular view with expandable sub-industries, sorting, and total reconciliation.
- **`SecurityContributionPanel`**: Top 5 Contributors and Detractors spotlight cards, plus a full ranked contribution table.
- **`MultiPeriodAttributionPanel`**: Carino linked monthly historical table with compound active return verification.
- **`CurrencyAttributionPanel`**: Local vs FX vs interaction term breakdown.
- **`BenchmarkInspectorPanel`**: Point-in-time constituent inspector with on-demand benchmark switching.
- **`MethodologyInspectorPanel`**: Mathematical formulas, CFA GIPS alignment, and institutional disclosures.
- **`AttributionReconciliationPanel`**: Visual audit checklist verifying tolerances and displaying the SHA-256 hash.

