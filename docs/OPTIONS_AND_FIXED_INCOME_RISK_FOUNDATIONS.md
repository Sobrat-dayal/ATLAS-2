# ATLAS — Stage 118: Options and Fixed-Income Risk Foundations

## Executive Summary

Stage 118 expands the ATLAS Financial Risk Operating System into instrument-specific derivative and fixed-income analytics:
1. **Derivatives Contract Intelligence & Option Greeks**: Analytical Black-Scholes-Merton (BSM) closed-form pricing for European call and put options, continuous dividend yields, analytical first and second-order Greeks (Delta $\Delta$, Gamma $\Gamma$, Vega $\mathcal{V}$, Theta $\Theta$, Rho $\rho$), intrinsic/time value decomposition, and exact Put-Call Parity validation.
2. **Position Multiplier Scaling & Directional Risk**: Scaling per-contract sensitivities by contract multiplier ($M$) and position contracts ($Q$) into position-level risk ($QM = Q \times M$), evaluating Delta-equivalent underlying shares and dollar notionals, position Gamma, position Vega per 1% volatility point, calendar-day Theta decay, and basis-point Rho.
3. **Local Taylor Approximation vs. Full Model Repricing**: Comparing Greek-based nonlinear P&L approximations ($\Delta V \approx \Delta \Delta S + \frac{1}{2}\Gamma (\Delta S)^2 + \mathcal{V} \Delta \sigma - \Theta \Delta t + \rho \Delta r$) against exact full Black-Scholes model re-evaluations under spot, implied volatility, interest rate, and time passage shocks.
4. **Fixed-Income Cash-Flow Engine & Day-Count Conventions**: Cash flow schedule projection across standard coupon frequencies (Annual, Semi-Annual, Quarterly, Monthly), day-count conventions (`ACT_ACT`, `ACT_365F`, `ACT_360`, `THIRTY_360`), accrued interest calculation, and clean versus dirty price reconciliation ($\text{Dirty} = \text{Clean} + \text{Accrued}$).
5. **Yield-to-Maturity (YTM) Solver, Duration, and Convexity**: Root-solving yield to maturity from dirty price using analytical derivative Newton-Raphson with bisection fallback, Macaulay duration ($D_{\text{Mac}}$), Modified duration ($D_{\text{mod}}$), analytical bond Convexity ($C$), and Dollar Value of an 01 ($\text{DV01} = P \cdot D_{\text{mod}} \cdot 0.0001$).
6. **Key-Rate Duration (KRD) & Sensitivities**: Allocating bond cash flows across standardized key-rate tenor vertices (6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y) using linear triangle weighting, with exact additive reconciliation ($\sum \text{KRD}_k \equiv D_{\text{mod}}$ and $\sum \text{KRD\_DV01}_k \equiv \text{DV01}$).
7. **Cross-Asset Instrument Sensitivities Synthesis**: Unified portfolio synthesis integrating direct Equity delta (1.0 per unit), Options Delta-Equivalent Notional ($), and Fixed-Income DV01 ($) into a comprehensive cross-asset risk profile.
8. **Bloomberg-Style Risk Workspaces**: Institutional UI workspaces with dark terminal styling (`<OptionsRiskWorkspace />`, `<FixedIncomeRiskWorkspace />`), real-time BSM and bond solvers, and cash-flow schedule inspector under `/risk`.

---

## Controlled Reference Fixtures & Mathematical Verification

Stage 118 establishes four exact reference fixtures verified by backend pytest suites and frontend TypeScript unit tests to 10 decimal places:

### 1. Part XVII European Vanilla Call BSM Reference Fixture
Given:
- Underlying Spot Price $S = 100.0$
- Strike Price $K = 100.0$
- Risk-Free Interest Rate $r = 0.05$ (5.0% continuous)
- Dividend Yield $q = 0.00$
- Implied Volatility $\sigma = 0.20$ (20.0%)
- Time to Expiration $T = 1.0$ year
- Contract Multiplier $M = 1.0$

Analytical parameters:
$$
d_1 = \frac{\ln(100/100) + (0.05 - 0.0 + \frac{1}{2}(0.20)^2)(1.0)}{0.20 \sqrt{1.0}} = \frac{0.07}{0.20} = 0.35
$$
$$
d_2 = d_1 - \sigma \sqrt{T} = 0.35 - 0.20 = 0.15
$$
$$
N(d_1) = N(0.35) = 0.6368306512, \quad N(d_2) = N(0.15) = 0.5596176924
$$
$$
\phi(d_1) = \frac{1}{\sqrt{2\pi}} e^{-0.35^2 / 2} = 0.3752403469
$$

Calculated Greek sensitivities:
- **Call Price ($C$)**:
  $$C = 100(1)N(0.35) - 100 e^{-0.05} N(0.15) = 63.68306512 - 95.12294245(0.5596176924) = 10.4505835722$$
- **Delta ($\Delta$)**:
  $$\Delta = e^{-qT} N(d_1) = 0.6368306512$$
- **Gamma ($\Gamma$)**:
  $$\Gamma = \frac{e^{-qT} \phi(d_1)}{S \sigma \sqrt{T}} = \frac{0.3752403469}{100(0.20)(1.0)} = 0.01876201735$$
- **Vega ($\mathcal{V}_{\text{unit}}$)**:
  $$\mathcal{V}_{\text{unit}} = S e^{-qT} \phi(d_1) \sqrt{T} = 100(0.3752403469)(1.0) = 37.5240346917$$
- **Vega per 1% Vol Point ($\mathcal{V}_{1\text{vp}}$)**:
  $$\mathcal{V}_{1\text{vp}} = 0.01 \times \mathcal{V}_{\text{unit}} = 0.3752403469$$
- **Theta Calendar Year ($\Theta_{\text{year}}$)**:
  $$\Theta_{\text{year}} = -\frac{100(0.3752403469)(0.20)}{2} - 0.05(100)e^{-0.05}(0.5596176924) = -6.4140275464$$
- **Theta Calendar Day ($\Theta_{\text{day}}$)**:
  $$\Theta_{\text{day}} = \frac{\Theta_{\text{year}}}{365} = -0.0175726782$$
- **Rho Unit Rate ($\rho_{\text{unit}}$)**:
  $$\rho_{\text{unit}} = K T e^{-rT} N(d_2) = 100(1)e^{-0.05}(0.5596176924) = 53.2324815454$$
- **Rho per 1 bp ($\rho_{1\text{bp}}$)**:
  $$\rho_{1\text{bp}} = 0.0001 \times \rho_{\text{unit}} = 0.0053232482$$
- **Put-Call Parity**:
  $$\text{Parity Diff} = |(C - P) - (S e^{-qT} - K e^{-rT})| < 10^{-10}$$

**Verified**: All 10 metrics reconciled to 10 decimal places.

---

### 2. Part XXI Position Greeks Reference Fixture
Given 2 Long Contracts ($Q = 2.0$) with Multiplier $M = 100$ ($QM = 200$) on the reference call:
- **Position Delta in Underlying Units**:
  $$\Delta_{\text{pos, units}} = QM \cdot \Delta = 200(0.6368306512) = 127.3661302 \text{ shares}$$
- **Position Delta-Equivalent Notional**:
  $$\Delta_{\text{pos, notional}} = \Delta_{\text{pos, units}} \cdot S = 127.3661302 \times 100 = \$12,736.61302$$
- **Position Vega per 1% Vol Point**:
  $$\mathcal{V}_{\text{pos, 1vp}} = QM \cdot \mathcal{V}_{1\text{vp}} = 200(0.3752403469) = 75.04806938$$

**Verified**: Exact match to reference fixture.

---

### 3. Part XLII Zero-Coupon Bond Reference Fixture
Given:
- Face Value $F = 100.0$
- Maturity $T = 1.0$ year
- Coupon Rate $c = 0.0\%$
- Annual Compounding Yield $y = 0.05$ ($5.0\%$)
- Frequency $m = 1$

Analytical metrics:
- **Dirty Price ($P$)**:
  $$P = \frac{100}{1.05} = 95.2380952381$$
- **Macaulay Duration ($D_{\text{Mac}}$)**:
  $$D_{\text{Mac}} = 1.0 \text{ year}$$
- **Modified Duration ($D_{\text{mod}}$)**:
  $$D_{\text{mod}} = \frac{D_{\text{Mac}}}{1 + y} = \frac{1.0}{1.05} = 0.9523809524 \text{ years}$$
- **Convexity ($C$)**:
  $$C = \frac{1}{P} \frac{\partial^2 P}{\partial y^2} = \frac{2}{(1.05)^2} = 1.8140589569$$
- **DV01 per 100 Face**:
  $$\text{DV01} = P \cdot D_{\text{mod}} \cdot 0.0001 = \frac{100}{(1.05)^2} \cdot 0.0001 = 0.0090702948$$

**Verified**: Exact match to 10 decimal places.

---

### 4. Part XLIII Two-Year 5% Par Bond Reference Fixture
Given:
- Face Value $F = 100.0$
- Coupon Rate $c = 5.0\%$ annual ($m = 1$)
- Annual Compounding Yield $y = 0.05$ ($5.0\%$)
- Maturity $T = 2.0$ years
- Cash flows: Year 1 = $5.00$, Year 2 = $105.00$

Analytical metrics:
- **Dirty Price ($P$)**:
  $$P = \frac{5}{1.05} + \frac{105}{(1.05)^2} = 4.7619047619 + 95.2380952381 = 100.0$$
- **Macaulay Duration ($D_{\text{Mac}}$)**:
  $$D_{\text{Mac}} = \frac{1(5 / 1.05) + 2(105 / 1.05^2)}{100} = \frac{4.7619047619 + 190.4761904762}{100} = 1.9523809524 \text{ years}$$
- **Modified Duration ($D_{\text{mod}}$)**:
  $$D_{\text{mod}} = \frac{1.9523809524}{1.05} = 1.8594104308 \text{ years}$$
- **Key-Rate Duration (KRD) Additivity**:
  $$\sum_k \text{KRD}_k \equiv D_{\text{mod}} = 1.8594104308$$

**Verified**: Exact match to 10 decimal places.

---

## Architectural Implementation

### 1. Backend Domain Architecture (`python/atlas/src/atlas/risk/`)

- `enums.py`:
  - Added `OptionType` (`CALL`, `PUT`), `ExerciseStyle` (`EUROPEAN`, `AMERICAN`, `BERMUDAN`), `OptionSettlementType` (`PHYSICAL`, `CASH`), `OptionsPricingModelId` (`EUROPEAN_BLACK_SCHOLES_MERTON`, `EUROPEAN_BLACK_76`, `VENDOR_SOURCED`, `NUMERICAL_BUMP_REPRICE`).
  - Added `CouponType` (`FIXED`, `ZERO_COUPON`, `FLOATING`, `STEP_UP`), `CouponFrequency` (`ANNUAL`, `SEMI_ANNUAL`, `QUARTERLY`, `MONTHLY`), `DayCountConvention` (`ACT_ACT`, `ACT_365F`, `ACT_360`, `THIRTY_360`), `BondPricingModelId` (`DISCOUNTED_CASHFLOW`, `YIELD_DURATION_CONVEXITY`, `CURVE_BUMP_REPRICE`), `YieldCurveInterpolation` (`LINEAR`, `CUBIC_SPLINE`, `FLAT_FORWARD`).
- `errors.py`:
  - Added 25 typed domain exceptions covering option contract validation, strike/spot positivity, implied volatility constraints, bond cashflow completeness, root-solver convergence, and multi-tenant access controls.
- `models.py`:
  - Defined `OptionContractRiskInput`, `OptionGreeksResult`, `OptionPositionRiskResult`, `PortfolioOptionsRiskSummary`.
  - Defined `BondCashFlowItem`, `BondCashFlowSchedule`, `KeyRateSensitivityItem`, `BondSensitivitiesResult`, `BondPositionRiskResult`, `PortfolioFixedIncomeRiskSummary`.
  - Defined `YieldCurvePoint`, `InterestRateCurveDefinition`, `PortfolioInstrumentSensitivitiesSummary`.
- `schemas.py`:
  - Pydantic V2 DTOs: `CalculateOptionsRiskRequest`, `OptionGreeksResultDTO`, `OptionPositionRiskDTO`, `PortfolioOptionsRiskSummaryDTO`, `CalculateFixedIncomeRiskRequest`, `BondSensitivitiesResultDTO`, `BondPositionRiskDTO`, `BondCashFlowScheduleDTO`, `InterestRateCurveDefinitionDTO`, `PortfolioInstrumentSensitivitiesSummaryDTO`.
- `options_pricing.py` (`BlackScholesMertonEngine`):
  - Standard European Black-Scholes-Merton closed-form pricing.
  - Analytical first and second-order Greeks ($\Delta, \Gamma, \mathcal{V}, \Theta, \rho$).
  - Position multiplier scaling ($QM = Q \times M$).
  - Taylor approximation vs. full model repricing across spot, volatility, interest rate, and time decay shocks.
  - Central difference numerical perturbation verification.
- `fixed_income_pricing.py` (`BondCashFlowEngine`):
  - Multi-period cash flow schedule generator supporting `ACT_ACT`, `ACT_365F`, `ACT_360`, `30_360`.
  - Accrued interest accounting and clean vs dirty price reconciliation.
  - Newton-Raphson YTM solver with analytical derivative $dP/dy$ and bisection fallback.
  - Analytical Macaulay duration, Modified duration, Convexity, and DV01.
  - Linear triangle key-rate duration (KRD) allocation with exact additivity.
  - Calibrated benchmark sovereign yield curve term structure (1M to 30Y).
- `service.py` (`RiskService`):
  - Added methods `calculate_options_risk`, `get_portfolio_options_risk`, `calculate_fixed_income_risk`, `get_portfolio_fixed_income_risk`, `get_bond_cash_flows`, `get_yield_curve_risk`, `get_instrument_sensitivities`.

---

### 2. FastAPI REST Router (`apps/api/src/atlas_api/routers/risk.py`)

12 production REST endpoints:
- `GET /api/v1/risk/options/models`
- `POST /api/v1/risk/options/calculate`
- `GET /api/v1/risk/portfolios/{id}/options`
- `GET /api/v1/risk/portfolios/{id}/options/greeks`
- `GET /api/v1/risk/portfolios/{id}/options/underlyings`
- `GET /api/v1/risk/fixed-income/models`
- `POST /api/v1/risk/fixed-income/calculate`
- `GET /api/v1/risk/portfolios/{id}/fixed-income`
- `GET /api/v1/risk/portfolios/{id}/fixed-income/cashflows`
- `GET /api/v1/risk/portfolios/{id}/fixed-income/dv01`
- `GET /api/v1/risk/portfolios/{id}/fixed-income/curves`
- `GET /api/v1/risk/portfolios/{id}/instrument-sensitivities`

---

### 3. Frontend Architecture (`apps/web/`)

- `types.ts`: TypeScript domain definitions for all Stage 118 models, enums, and DTOs.
- `api.ts`: Typed client methods for options and bond calculations, summaries, cash flows, and curves.
- `formatting.ts`: Institutional formatters for Delta, Gamma, Vega, Theta, Rho, Duration, Convexity, DV01, Bond Price, and Yield.
- `useRiskTerminal.ts`: Integrated `"options"` and `"fixed_income"` tabs, state management, and real-time calculation actions.
- `<OptionsRiskWorkspace />`:
  - KPI Summary Bar (Market Value, Net Delta Notional, Net Vega, Net Theta, Net Rho).
  - Positions & Scaled Greeks table with symbol filtering.
  - Position inspector with Taylor approximation vs. full model repricing comparison.
  - Underlying asset delta-equivalent breakdown.
  - Interactive closed-form BSM option calculator.
- `<FixedIncomeRiskWorkspace />`:
  - KPI Summary Bar (Debt Value, Total DV01, Modified Duration, Macaulay Duration, Convexity, Weighted YTM).
  - Holdings and sensitivity table.
  - Projected coupon and principal cash flow schedule drilldown.
  - Key-rate DV01 term structure histogram.
  - Calibrated sovereign yield curve points table.
  - Interactive bond sensitivity solver (YTM, duration, convexity, DV01).

---

## Verification & Test Results

1. **Backend Test Suite (`apps/api/tests/test_risk_options_and_fixed_income_v1.py`)**:
   - `14 passed, 0 failed` in 17.25s.
   - Verified Part XVII European Call, Part XXI Position Greeks, Part XLII Zero-Coupon Bond, Part XLIII Par Bond, Put-Call Parity, Finite Difference Bumps, Day-Count Conventions, YTM Solver, KRD Additivity, FastAPI Endpoints, and Multi-Tenant Isolation.
2. **Frontend Unit Tests (`apps/web/src/lib/risk/__tests__/risk_stage118_v1.test.ts`)**:
   - `7 passed, 0 failed` in 982ms.
3. **Next.js Production Build (`apps/web`)**:
   - `pnpm --filter web build` succeeded with zero TypeScript or route compilation errors.

