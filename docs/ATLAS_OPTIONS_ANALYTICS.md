# ATLAS — INSTITUTIONAL OPTIONS ANALYTICS TERMINAL (STAGE 141)

## 1. Executive Summary

Stage 141 delivers the **Institutional Options Analytics Terminal** within the canonical route `/options`. The terminal provides comprehensive options market discovery, dual-sided options chains, source-provided volatility analytics and Greeks, multi-leg strategy modeling with analytical breakeven root finding, and tenant-isolated portfolio holdings integration.

The system strictly adheres to institutional fidelity standards:
- **Zero Fabrication**: Unsupported fields, missing quotes, or missing Greeks remain `None` / unavailable. Missing Greeks are never set to $0.0$.
- **Explicit Multipliers**: Multipliers are dynamically sourced from canonical contract terms (e.g. 100 for U.S. equities, 50 for Indian NSE NIFTY index options).
- **Corporate Action Isolation**: Nonstandard deliverables (e.g. 150 shares + \$250 cash resulting from reverse splits or special distributions) are recorded in an immutable adjustment registry and excluded from vanilla 100-share expiration payoff calculations.
- **Expiration Settlement Boundary**: Payoff calculations model piecewise-linear terminal intrinsic value at expiration settlement ($T = \text{Expiry}$). Prior-to-expiration mark-to-market Black-Scholes / QuantLib pricing is explicitly reserved for Stage 142.
- **Strict Read-Only Semantics**: The terminal performs analytical research, volatility modeling, and strategy inspection. Autonomous order routing, paper trading, and broker sandboxes are prohibited and scheduled for Stages 144–145.

---

## 2. Architecture & Modules

The options analytics engine is organized under `python/atlas/src/atlas/options/` and `apps/web/src/components/options/`:

```
python/atlas/src/atlas/options/
├── domain.py                      # Canonical domain models, enums, deliverables, quotes, and disclaimers
├── errors.py                      # Domain-specific typed exceptions
├── service.py                     # Master AtlasOptionsService orchestrator
├── router.py                      # FastAPI REST endpoints mounted at /api/v1/options
├── contracts/
│   ├── identifiers.py             # Standard OSI 21-character symbology & Indian NSE parser
│   ├── deliverables.py            # Standard 100-share, custom lot, cash-settled, and adjusted deliverables
│   ├── adjustments.py             # Corporate action adjustment registry & history
│   └── registry.py                # Contract registry seeded with SPY, AAPL, NIFTY, and XYZ
├── market_data/
│   ├── capabilities.py            # Provider capabilities & dynamic license entitlement registry
│   ├── quotes.py                  # Quote store & data quality sanity checks (zero bid, crossed, locked, stale)
│   └── chains.py                  # Dual-sided calls/puts chain builder & moneyness calculator
├── analytics/
│   ├── moneyness.py               # Intrinsic, extrinsic, and DTE calculations
│   ├── spreads.py                 # Bid-ask spread metrics & wide-spread detection
│   ├── volatility.py              # IV smile, skew (25D put/call skew, risk reversal), and term structure
│   └── activity.py                # Strike volume, open interest, and put/call ratios
├── strategies/
│   ├── templates.py               # 20 canonical strategy templates
│   ├── validation.py              # Strategy leg validation (multi-expiration & adjusted contract exclusion)
│   ├── opening_cashflow.py        # Net debit / net credit opening cash flow calculation
│   ├── payoff.py                  # Piecewise-linear expiration payoff engine & curve generation
│   └── breakevens.py              # Analytical breakeven root finding & max gain/loss bounds
└── portfolios/
    └── integration.py             # Tenant-isolated portfolio options holdings service

apps/web/src/
├── app/(atlas)/options/page.tsx   # Next.js options route mounting OptionsTerminal
├── components/options/
│   ├── OptionsTerminal.tsx        # Master terminal cockpit
│   ├── OptionsNavigation.tsx      # Subview navigation (Overview, Chain, Volatility, Activity, Strategies, Positions)
│   ├── UnderlyingSearch.tsx       # Ticker search & quick switcher (SPY, AAPL, NIFTY, XYZ)
│   ├── ExpirationSelector.tsx     # Listed expiration chips with DTE badges
│   ├── OptionsChain.tsx           # Dual-sided calls/strikes/puts grid with moneyness highlights
│   ├── OptionContractInspector.tsx# Contract specifications drawer (OSI, deliverables, quote timestamps)
│   ├── OptionAdjustmentInspector.tsx# Corporate action adjustment history modal
│   ├── OptionsVolatilityView.tsx  # IV smile chart, 25-delta skew cards, and term structure
│   ├── OptionsActivityView.tsx    # Strike volume vs open interest comparison bars
│   ├── OptionsStrategyBuilder.tsx # Multi-leg strategy builder with template loader and risk alerts
│   ├── StrategyPayoffChart.tsx    # Interactive SVG expiration payoff diagram with breakeven lines
│   ├── OptionsPositionsView.tsx   # Read-only user portfolio options holdings
│   └── index.ts                   # Component barrel export
└── lib/options/
    ├── types.ts                   # TypeScript data contracts matching Python domain
    ├── formatters.ts              # Currency, strike, percent, OSI symbology, and quality flag formatters
    ├── api.ts                     # Fetch client connecting to /api/v1/options/*
    └── __tests__/options.test.ts  # Node unit test suite for formatters, symbology, and math
```

---

## 3. Canonical Strategy Templates (20 Presets)

ATLAS pre-configures 20 institutional options strategy templates with directional bias and risk profile classification:

| ID | Strategy Name | Legs | Directional Bias | Risk Profile |
|---|---|---|---|---|
| `LONG_CALL` | Long Call | 1 | Bullish | Defined Risk (Premium Paid) |
| `LONG_PUT` | Long Put | 1 | Bearish | Defined Risk (Premium Paid) |
| `SHORT_CALL` | Short Naked Call | 1 | Bearish / Neutral | **Unbounded Upside Risk** |
| `SHORT_PUT` | Short Naked Put | 1 | Bullish / Neutral | Substantial Downside Risk ($K - P$) |
| `COVERED_CALL` | Covered Call | 1 | Neutral / Mildly Bullish | Defined Upside / Full Underlying Downside |
| `PROTECTIVE_PUT` | Protective Put (Married Put) | 1 | Bullish | Defined Risk Floor |
| `BULL_CALL_SPREAD` | Bull Call Vertical Spread | 2 | Bullish | Defined Risk / Defined Profit |
| `BEAR_CALL_SPREAD` | Bear Call Vertical Spread | 2 | Bearish | Defined Risk / Defined Profit |
| `BULL_PUT_SPREAD` | Bull Put Vertical Spread | 2 | Bullish | Defined Risk / Defined Profit |
| `BEAR_PUT_SPREAD` | Bear Put Vertical Spread | 2 | Bearish | Defined Risk / Defined Profit |
| `LONG_STRADDLE` | Long Straddle | 2 | High Volatility / Neutral | Defined Risk / Double Uncapped Profit |
| `SHORT_STRADDLE` | Short Straddle | 2 | Low Volatility / Neutral | **Unbounded Double Risk** |
| `LONG_STRANGLE` | Long Strangle | 2 | High Volatility / Neutral | Defined Risk / Double Uncapped Profit |
| `SHORT_STRANGLE` | Short Strangle | 2 | Low Volatility / Neutral | **Unbounded Double Risk** |
| `LONG_CALL_BUTTERFLY` | Long Call Butterfly Spread | 3 | Neutral | Defined Risk / Defined Profit |
| `LONG_PUT_BUTTERFLY` | Long Put Butterfly Spread | 3 | Neutral | Defined Risk / Defined Profit |
| `IRON_BUTTERFLY` | Iron Butterfly Spread | 4 | Neutral | Defined Risk / Defined Profit |
| `IRON_CONDOR` | Iron Condor Spread | 4 | Range-Bound / Neutral | Defined Risk / Defined Profit |
| `COLLAR` | Long Collar | 2 | Mildly Bullish | Defined Risk Floor / Capped Upside |
| `SYNTHETIC_LONG_STOCK`| Synthetic Long Stock | 2 | Strong Bullish | Substantial Downside / Uncapped Upside |

---

## 4. API Reference

All endpoints are registered under `/api/v1/options`:

1. `GET /api/v1/options/capabilities`: Returns terminal metadata, supported markets, and legal disclaimers.
2. `GET /api/v1/options/underlyings`: Returns active underlying instruments, spot prices, currencies, and adjustment indicators.
3. `GET /api/v1/options/expirations/{symbol}`: Returns available listed expiration dates for an underlying.
4. `GET /api/v1/options/chain/{symbol}/{expiration_date}`: Generates a dual-sided calls/puts options chain with moneyness states and summary ratios.
5. `GET /api/v1/options/contract/{contract_id}`: Retrieves comprehensive contract terms, deliverable specifications, and OSI symbol.
6. `GET /api/v1/options/quote/{contract_id}`: Retrieves market quotes, volume, open interest, and source Greeks.
7. `GET /api/v1/options/volatility/smile/{symbol}/{expiration_date}`: Returns implied volatility smile points across strikes and 25-delta skew metrics.
8. `GET /api/v1/options/volatility/term-structure/{symbol}`: Returns ATM implied volatility term structure across expiration dates.
9. `GET /api/v1/options/activity/{symbol}/{expiration_date}`: Returns strike-by-strike volume and open interest distributions.
10. `GET /api/v1/options/strategies/templates`: Returns metadata for the 20 canonical strategy templates.
11. `POST /api/v1/options/strategies/analyze`: Validates multi-leg strategies, calculates net opening cash flow, analytical breakevens, max profit/loss, and generates high-resolution piecewise-linear expiration payoff curves.
12. `GET /api/v1/options/portfolios/{portfolio_id}`: Returns tenant-isolated options positions and unrealized P&L.
13. `GET /api/v1/options/adjustments/{symbol}`: Returns corporate action adjustment records and deliverable histories.

---

## 5. Test Suite & Verification Results

### Backend Pytest Suite (`apps/api/tests/test_options_stage141.py`)
- **29 Passed / 29 Total Tests (100% Pass Rate)**:
  - Capabilities and mandatory disclaimers.
  - OSI 21-character symbology formatting and parsing.
  - Test A: Standard Call Intrinsic & Expiration Payoff ($S_T=\$120, K=\$100, P=\$5, M=100 \implies P\&L=\$1,500$).
  - Test B: Standard Put Intrinsic & Expiration Payoff ($S_T=\$80, K=\$100, P=\$4, M=100 \implies P\&L=\$1,600$).
  - Test C: Out-of-the-Money Call Expiration Loss ($S_T=\$80, K=\$100, P=\$5 \implies P\&L=-\$500$, Max Loss=\$500).
  - Test D: Bull Call Vertical Spread ($100/110$ call spread, Net Debit \$500, Max Profit \$500, Max Loss \$500, Breakeven \$105).
  - Test E: Long Straddle (Debit \$900, Breakevens \$91 and \$109, Max Loss \$900).
  - Test F: Naked Short Call Unbounded Upside Loss Detection (`is_unbounded_loss=True`, `max_loss=None`).
  - Test G: Corporate Action Nonstandard Deliverable Payoff Exclusion (`OptionsAdjustedDeliverableUnsupportedError`).
  - Test H: Zero Bid Market Quote Sanity Handling (`ZERO_BID` quality flag, no artificial bids).
  - Test I: Crossed Market Data Quality Flagging (`CROSSED_MARKET` when Bid > Ask).
  - Test J: Stale Quote Flagging (`STALE_QUOTE`).
  - Test K: Open Interest Prior-Session Reporting Date Fidelity.
  - Test L: Missing Greeks Fidelity (Unprovided Greeks remain `None`, never set to 0.0).
  - Test M: Multi-Expiration Calendar Spread Payoff Exclusion (`OptionsMultiExpirationPayoffUnsupportedError`).
  - Test N: Indian NSE Lot Sizes ($M=50$ for NIFTY, INR currency, amounts scale by 50).
  - Test O: Corporate Action Reconciliation and Adjustment History.
  - Test P: Multi-Tenant Portfolio Isolation (Unauthorized user access raises `OptionsTenantAccessDeniedError`).
  - Test Q: Provider License Revocation Enforcement (`OptionsEntitlementRequiredError`).
  - Test R: No Broker Execution or Order Routing Boundaries.
  - Fast-API REST Endpoints testing.

### Full Regression Across Stages 135–141
- **184 Passed / 184 Total Tests (100% Pass Rate)**:
  - Stage 135 Universal Events: 26 passed.
  - Stage 136 Event Graph: 24 passed.
  - Stage 137 Financial Exposure: 27 passed.
  - Stage 138 Intelligence V1: 25 passed.
  - Stage 139 Intelligence Scoring: 24 passed.
  - Stage 140 God's Eye Intelligence: 29 passed.
  - Stage 141 Options Analytics: 29 passed.

### Frontend Unit Tests (`apps/web/src/lib/options/__tests__/options.test.ts`)
- **8 Passed / 8 Total Tests (100% Pass Rate)**:
  - Multi-currency formatting (USD, INR, EUR, negative balances).
  - Strike price formatting.
  - Percentage and number localization.
  - Days to expiration (DTE) human-readable labels.
  - Moneyness badge mapping.
  - Quote quality flag formatting.
  - Standard 21-character OSI symbol serialization.
  - OSI symbol parsing.
