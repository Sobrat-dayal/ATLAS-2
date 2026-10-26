# ADVANCED SCREENER FACTORS: FUNDAMENTAL, TECHNICAL AND MULTI-FACTOR SCREENING ENGINE

**Canonical Roadmap:** Stage 96 of 150  
**Primary Module:** Screeners  
**Primary Route:** `/screeners`  
**Execution Standard:** Institutional-Grade Quantitative Discovery and Multi-Factor Screener  
**Zero LLM Invocations:** Fully deterministic mathematical and server-side execution

---

## 1. Executive Summary & Architecture

Stage 96 upgrades the ATLAS financial screening infrastructure established in Stage 94 (Query Engine & Canonical Universes) and Stage 95 (Interactive Visual Filter Builder) into an institutional-grade quantitative screening and research workspace.

Securities can be filtered simultaneously across:
1. **Advanced Financial Statements**: Revenue, Net Income, Operating Income, Gross Profit, Total Assets, Book Equity, and Shares.
2. **Growth Metrics**: YoY and QoQ Revenue Growth, Net Income Growth, EPS Growth, and Free Cash Flow Growth.
3. **Profitability & Margins**: Gross Margin, Operating Margin, and Net Profit Margin.
4. **Capital Efficiency**: Return on Equity (ROE), Return on Assets (ROA), and Return on Invested Capital (ROIC).
5. **Balance Sheet Strength & Solvency**: Total Debt, Net Debt, Debt-to-Equity, Current Ratio, Quick Ratio, and Interest Coverage.
6. **Cash Flow & Capital Allocation**: Operating Cash Flow, CapEx, Free Cash Flow (FCF), and FCF Yield.
7. **Advanced Valuation**: Trailing P/E, P/B, P/S, Enterprise Value (EV), EV/EBITDA, EV/Revenue, and Dividend Yield.
8. **Technical Trend & Moving Averages**: SMA (20, 50, 100, 200), EMA (20, 50, 200), Golden Cross, Death Cross, Price-to-SMA states.
9. **Technical Momentum & Oscillators**: 14-session Wilder RSI, MACD (12/26/9 line, signal, histogram, crossovers), Rate-of-Change Momentum (5d, 20d, 60d, 252d).
10. **Technical Volatility & Bands**: Bollinger Bands (middle, upper, lower, bandwidth, %B), 14-session Wilder ATR and ATR%, Annualized Realized Volatility.
11. **Technical Volume & Breakouts**: 20-session Relative Volume (RVOL), Average 20-session Volume, 52-Week High/Low, and % Distances.

```
+-----------------------------------------------------------------------------------------+
|                                    ATLAS APPSHELL                                       |
|                                       /screeners                                        |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
                      +---------------------------------------------+
                      |       STAGE 95 VISUAL FILTER BUILDER        |
                      |   - Filter Library (16 Category Tabs)       |
                      |   - Parameter Editors (Period, Components)  |
                      |   - Visual Condition Rows & Boolean Select  |
                      |   - Factor Methodology Inspector            |
                      +---------------------------------------------+
                                             |
                                             v
                      +---------------------------------------------+
                      |         STAGE 96 FACTOR REGISTRY            |
                      |   - 70 Canonical Filter Definitions         |
                      |   - Parameter Bounds Validation [2, 500]    |
                      |   - Financial Sector Inapplicability Rules  |
                      +---------------------------------------------+
                                             |
                   +-------------------------+-------------------------+
                   |                                                   |
                   v                                                   v
+------------------------------------+               +------------------------------------+
|        FUNDAMENTAL FACTORS         |               |         TECHNICAL FACTORS          |
| - Stage 82 Statements & 83 Ratios  |               | - 260 Completed Daily OHLCV Bars   |
| - Reporting Periods: FY2025/TTM    |               | - Split-Adjusted Pricing History   |
| - Strict Sector Accounting Rules   |               | - Zero Look-Ahead Bias & Warm-Up   |
| - Missing Data Policy (Strict NULL)|               | - Exact Decimal Math (TA-Lib Parity|
+------------------------------------+               +------------------------------------+
                   |                                                   |
                   +-------------------------+-------------------------+
                                             |
                                             v
                      +---------------------------------------------+
                      |         MULTI-FACTOR QUERY ENGINE           |
                      |   - Boolean AND Semantics Across Categories |
                      |   - Dynamic Parameter Calculation           |
                      |   - Server-Side Execution (0 Fanout)        |
                      +---------------------------------------------+
                                             |
                                             v
                      +---------------------------------------------+
                      |          SCREENER RESULTS & TABLE           |
                      |   - 47 Data Table Column Specifications     |
                      |   - Institutional Formatting ($B, %, x)     |
                      |   - Source Provenance Inspector             |
                      +---------------------------------------------+
```

---

## 2. Fundamental Factor Engine

### 2.1 Accounting Semantics & Financial Sector Eligibility
1. **Banking & Financial Institution Segregation**: Regulated financial institutions (e.g. `JPM`) operate without standard industrial COGS, inventories, or debt-service structures. Consequently, metrics such as Gross Margin, Operating Cash Flow, CapEx, Free Cash Flow, Net Debt, Current Ratio, and EV/EBITDA are marked `None` (unavailable).
2. **Strict NULL Evaluation**: When a user queries `fcf > 0` or `net_debt < 10B`, securities with inapplicable/missing values evaluate to `False`. Missing data is never coerced to zero.
3. **Negative Earnings & Multiple Qualification**: If net income is negative, the Price-to-Earnings ratio evaluates to `None` and renders as `N/M` (Not Meaningful), preventing inverted and misleading valuation rankings.
4. **Free Cash Flow Definition**:
   $$FCF = \text{Operating Cash Flow} - \text{Capital Expenditures}$$
   Where CapEx is defined as a positive outflow magnitude.
5. **Growth Metrics**:
   $$\text{YoY Revenue Growth} = \frac{\text{Revenue}_{t} - \text{Revenue}_{t-1}}{|\text{Revenue}_{t-1}|} \times 100$$
   Companies transitioning from negative baselines or with insufficient historical comparative periods are qualified rather than assigned fabricated percentages.

---

## 3. Technical Indicator Engine

### 3.1 Historical Bar Invariants & Completed-Bar Policy
Every price series is grounded on canonical, split-adjusted daily OHLCV bars. Each bar satisfies:
$$\text{High} \ge \max(\text{Open}, \text{Close}), \quad \text{Low} \le \min(\text{Open}, \text{Close}), \quad \text{Low} \le \text{High}, \quad \text{Volume} \ge 0$$
To guarantee reproducibility and eliminate look-ahead bias, daily screening defaults exclusively to completed sessions (`LAST_COMPLETED`).

### 3.2 Indicator Mathematics

#### 1. Simple Moving Average (SMA)
For period $N$:
$$\text{SMA}_N(t) = \frac{1}{N}\sum_{i=0}^{N-1}\text{Close}_{t-i}$$
Returns `None` if completed bars $< N$.

#### 2. Exponential Moving Average (EMA)
Multiplier:
$$\alpha = \frac{2}{N + 1}$$
Initialized with SMA of the first $N$ observations, recursively smoothed over remaining bars:
$$\text{EMA}_t = \alpha \cdot \text{Close}_t + (1 - \alpha) \cdot \text{EMA}_{t-1}$$

#### 3. Relative Strength Index (RSI)
Calculated via Wilder's smoothing over period $N$ (default 14):
$$\text{Change}_t = \text{Close}_t - \text{Close}_{t-1}$$
$$\text{Gain}_t = \max(\text{Change}_t, 0), \quad \text{Loss}_t = \max(-\text{Change}_t, 0)$$
Initial average gain/loss is arithmetic mean over first $N$ changes, followed by Wilder smoothing:
$$\text{AvgGain}_t = \frac{\text{AvgGain}_{t-1} \cdot (N-1) + \text{Gain}_t}{N}$$
$$\text{AvgLoss}_t = \frac{\text{AvgLoss}_{t-1} \cdot (N-1) + \text{Loss}_t}{N}$$
$$\text{RS} = \frac{\text{AvgGain}}{\text{AvgLoss}}, \quad \text{RSI} = 100 - \frac{100}{1 + \text{RS}}$$
*Edge Cases*: If $\text{AvgLoss} = 0$, RSI is $100.0$ if $\text{AvgGain} > 0$, or $50.0$ if all changes are 0. Strict warm-up requires at least $N + 1$ bars.

#### 4. Moving Average Convergence Divergence (MACD)
$$\text{MACD Line} = \text{EMA}_{12}(\text{Close}) - \text{EMA}_{26}(\text{Close})$$
$$\text{Signal Line} = \text{EMA}_9(\text{MACD Line})$$
$$\text{Histogram} = \text{MACD Line} - \text{Signal Line}$$
Requires at least $26 + 9 = 35$ completed daily bars.

#### 5. Bollinger Bands
$$\text{Middle Band} = \text{SMA}_{20}(\text{Close})$$
$$\text{Upper Band} = \text{Middle} + 2 \cdot \sigma_{\text{sample}}$$
$$\text{Lower Band} = \text{Middle} - 2 \cdot \sigma_{\text{sample}}$$
$$\text{Bandwidth} = \frac{\text{Upper} - \text{Lower}}{\text{Middle}} \times 100$$
$$\%B = \frac{\text{Close} - \text{Lower}}{\text{Upper} - \text{Lower}}$$

#### 6. Average True Range (ATR)
$$\text{TR}_t = \max(\text{High}_t - \text{Low}_t, |\text{High}_t - \text{Close}_{t-1}|, |\text{Low}_t - \text{Close}_{t-1}|)$$
Smoothed using Wilder's 14-period method. ATR% normalized by latest closing price:
$$\text{ATR\%} = \frac{\text{ATR}}{\text{Close}} \times 100$$

#### 7. Momentum / Rate of Change (ROC)
$$\text{ROC}_N = \frac{\text{Close}_t - \text{Close}_{t-N}}{\text{Close}_{t-N}} \times 100$$
Evaluated over 5, 20, 60, and 252 sessions.

#### 8. Annualized Realized Volatility
Log returns:
$$r_t = \ln\left(\frac{\text{Close}_t}{\text{Close}_{t-1}}\right)$$
Sample standard deviation $\sigma_{\text{daily}}$ annualized assuming 252 trading sessions:
$$\text{Annualized Volatility} = \sigma_{\text{daily}} \cdot \sqrt{252} \times 100\%$$

#### 9. Relative Volume (RVOL)
$$\text{RVOL} = \frac{\text{Volume}_{\text{latest}}}{\text{Volume}_{20d\text{ avg}}}$$

---

## 4. Multi-Factor Query Planning & Execution

### 4.1 Filter Registry Catalog (70 Filters)
The canonical registry comprises 70 typed filters across 16 categories:
- **Profile & Venue**: `symbol`, `exchange_mic`, `listing_country_code`, `issuer_country_code`, `sector`, `industry`, `security_type`, `listing_status`.
- **Market Data**: `market_cap`, `last_price`, `price_change_pct`, `volume_latest`, `volume_20d_avg`, `traded_value_latest`.
- **Fundamentals**: `revenue`, `net_income`, `operating_income`, `total_assets`, `book_equity`, `eps`.
- **Valuation**: `pe_ratio`, `pb_ratio`, `ps_ratio`, `dividend_yield`, `ev`, `ev_to_ebitda`, `ev_to_revenue`.
- **Profitability**: `gross_margin`, `operating_margin`, `net_margin`.
- **Growth**: `revenue_growth_yoy`, `revenue_growth_qoq`, `net_income_growth_yoy`, `eps_growth_yoy`.
- **Balance Sheet & Solvency**: `total_debt`, `net_debt`, `debt_to_equity`, `current_ratio`, `quick_ratio`, `interest_coverage`.
- **Cash Flow**: `operating_cash_flow`, `capex`, `fcf`, `fcf_growth_yoy`, `fcf_yield`.
- **Capital Efficiency**: `roe`, `roa`, `roic`.
- **Technical Trend**: `sma_20`, `sma_50`, `sma_100`, `sma_200`, `ema_20`, `ema_50`, `ema_200`, `price_above_sma200`, `price_above_sma50`, `golden_cross`.
- **Technical Momentum**: `rsi_14`, `macd_line`, `macd_signal`, `macd_hist`, `macd_crossover`, `momentum_5d`, `momentum_20d`, `momentum_60d`, `momentum_252d`.
- **Technical Volatility**: `bollinger_middle`, `bollinger_upper`, `bollinger_lower`, `bollinger_bandwidth`, `bollinger_pct_b`, `atr_14`, `atr_pct`, `historical_volatility_20d`.
- **Technical Volume**: `relative_volume_20d`, `high_52w`, `low_52w`, `price_to_52w_high`, `price_to_52w_low`.

### 4.2 Query Execution Pipeline
1. **Universe Filtering**: Candidate securities selected by asset class, security types, and listing status.
2. **Metadata & Sector Pushdown**: Instant pre-filtering on exchange, geography, and sector.
3. **Fundamental Factor Pushdown**: Evaluated against canonical fiscal profile. Inapplicable sectors return false on numerical filters.
4. **Technical Indicator Resolution**: Evaluated on precomputed completed daily bar cache or dynamically recomputed on candidate's historical bar series if custom parameter specified (e.g. custom period).
5. **Boolean Composition**: All conditions combined using deterministic Boolean AND semantics.
6. **Sorting & Keyset Pagination**: High-performance in-memory sort on requested column and cursor pagination.
7. **Cell Formatting & Provenance Enrichment**: Cells formatted with institutional units (`$B`, `$M`, `%`, `x`, `shares`, `N/M`, `—`).

---

## 5. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/screeners/factors` | List all 70 approved factors (filterable by `?category=...`) |
| `GET` | `/api/v1/screeners/factors/{factor_id}` | Inspect factor methodology, formula, lookback, and allowed operators |
| `GET` | `/api/v1/screeners/factors/{factor_id}/parameters` | Retrieve allowed parameter bounds (e.g. `period: [2..500]`) and default values |
| `POST` | `/api/v1/screeners/factors/validate` | Pre-validate factor conditions and parameter bounds without running a full screen |
| `POST` | `/api/v1/screeners/run` | Execute multi-factor screen across canonical universes |

### Error Codes
- `FACTOR_NOT_FOUND`: Filter ID is not present in canonical registry.
- `SCREENER_PARAMETER_INVALID`: Parameter key not allowed or period out of bounds $[2, 500]$.
- `SCREENER_OPERATOR_NOT_SUPPORTED`: Operator not allowed for metric's value type.
- `SCREENER_VALUE_TYPE_INVALID`: Value could not be parsed to valid finite Decimal.
- `SCREENER_RANGE_INVALID`: Lower boundary exceeds upper boundary in `BETWEEN` filter.
- `SCREENER_QUERY_LIMIT_EXCEEDED`: Query exceeds max filter count (20 active conditions).

---

## 6. Verification & Automated Test Results

### 6.1 Backend Test Suite (`pytest`)
- **Total Test Cases**: 54 passed (0 failures, 0 regressions).
- **Files Tested**:
  - `apps/api/tests/test_screener_advanced_factors.py`: 19 passed.
  - `apps/api/tests/test_screener_visual_builder.py`: 15 passed.
  - `apps/api/tests/test_screeners.py`: 20 passed.
- **TA-Lib Numerical Tolerances**:
  - SMA: $|\Delta| < 10^{-13}$
  - RSI: $|\Delta| < 0.005$
  - Bollinger Bands: $|\Delta| < 10^{-13}$
  - ATR: $|\Delta| < 10^{-4}$

### 6.2 Frontend Test Suite (`node:test`)
- **Total Test Cases**: 16 passed (0 failures).
- **Files Tested**:
  - `apps/web/src/lib/screeners/__tests__/stage96_factors.test.ts`: 3 passed.
  - `apps/web/src/lib/screeners/__tests__/visual-builder.test.ts`: 13 passed.
- **TypeScript & ESLint Quality**:
  - `npx tsc --noEmit`: 0 errors.
  - `npx eslint src/lib/screeners/ src/components/screeners/`: 0 errors.

---

## 7. Roadmap Boundaries & Prohibitions

1. **Stage 97 Reserved**: Saved screens persistence, multi-column ranking leaderboards, composite attractiveness scores, and CSV/Excel exports are deferred to Stage 97.
2. **Stage 98 Reserved**: Natural-language translation and conversational filter building are deferred to Stage 98.
3. **Stage 143 Reserved**: Strategy equity backtesting and historical portfolio simulations are deferred to Stage 143.
4. **Zero LLM Calls**: Normal screener execution operates with 0 LLM calls.
5. **No Synthetic Price Filling**: Securities with insufficient bar history (e.g. delisted `ENE` with 10 bars) strictly return `None` for indicators requiring longer lookbacks (e.g. 200 SMA).
