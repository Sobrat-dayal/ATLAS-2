# ATLAS AI Financial Action Engine — Stage 128 of 150

## Overview & Master Objective
Stage 128 completes the foundational 5-stage ATLAS AI Assistant sequence (Stages 124–128). It extends the conversational intelligence (Stage 124), context awareness (Stage 125), secure tool gateway (Stage 126), and source-grounded research/RAG (Stage 127) into an institutional-grade, user-approved **Financial Action Engine** across Charts, Screeners, Portfolios, and Risk.

The engine translates natural-language user intentions into structured, validated action proposals, generates cryptographic before/after diff previews, binds user approval securely, and coordinates genuine execution across existing ATLAS financial services with complete auditability, idempotency, and rollback capabilities.

---

## Strict Scope & Guardrails (Zero Fabrication & Safety Boundaries)

1. **The LLM Proposes, the Backend Validates, the User Approves, Financial Services Execute**:
   The AI model is never the final authority over financial mutations. All model proposals are treated as untrusted input.
2. **Prohibited Live Broker Orders (Fixture I)**:
   Any request to place live market or limit orders (`buy`, `sell`, `place order`) is rejected with `AiActionBrokerExecutionProhibitedError`.
3. **Prohibited Ledger & Cash Mutations**:
   Hypothetical portfolio rebalancing scenarios strictly produce non-executing drafts labeled `Hypothetical Allocation Proposal — Not Executed`. They never alter real accounting transactions, holdings, or cash balances (`AiActionLedgerMutationProhibitedError`).
4. **Immutable Risk Runs (Fixture D)**:
   Risk calculations executed on worker infrastructure produce permanent, immutable calculation records that cannot be overwritten or undone (`AiActionUndoUnavailableError`).
5. **Zero Fabrication**:
   The system never fabricates security screening matches, chart indicator values, portfolio weights, or Value-at-Risk outputs.

---

## Four Primary Action Domains

### 1. Charts (`atlas.chart.*`)
- **Supported Capabilities**:
  - `atlas.chart.select_instrument`: Switch active instrument on chart panel (`TEST_A`, `MSFT`, `AAPL`).
  - `atlas.chart.set_timeframe`: Configure interval (`1m`, `5m`, `15m`, `1h`, `1D`, `1W`, `1M`).
  - `atlas.chart.set_type`: Change chart type (`candlestick`, `line`, `area`, `bar`, `heikin_ashi`).
  - `atlas.chart.add_indicator`: Add technical indicators (SMA, EMA, RSI, MACD, BOLL, VOL, ATR, VWAP) with strict parameter validation (periods, standard deviations).
  - `atlas.chart.add_comparison`: Add percentage performance normalized comparison against benchmark or peer.
  - `atlas.chart.save_configuration` & `atlas.chart.restore_configuration`: Snapshot and restore chart layout.
- **Fixture A**: "Add 20-period SMA and 50-period SMA" parses into structured parameters, displays diff, binds approval, updates chart, and supports undo back to snapshot revision.

### 2. Screeners (`atlas.screener.*`)
- **Supported Capabilities**:
  - `atlas.screener.create_draft`: Initialize typed screening rule set.
  - `atlas.screener.add_filter`, `update_filter`, `remove_filter`: Configure typed filters with valid metric IDs (`revenue_growth_yoy`, `net_profit_margin`, `market_cap`, `pe_ratio`, `debt_to_equity`, `roe`), operators (`GREATER_THAN`, `LESS_THAN`, `BETWEEN`), and thresholds.
  - `atlas.screener.set_universe`: Select supported universe (`IN_NIFTY500`, `US_SP500`, `GLOBAL_TECH`).
  - `atlas.screener.execute`: Run query over real security database.
  - `atlas.screener.save` & `atlas.screener.restore_revision`: Persist approved screeners with revision tracking.
- **Fixture B**: "Find Indian companies with positive net profit, revenue growth above 15%, and market cap above 10,000 crore" returns genuine matching companies (`TCS.NS`, `INFY.NS`) and excludes non-matching securities.

### 3. Portfolios (`atlas.portfolio.*`)
- **Analytical & Hypothetical Drafts Only**:
  - `atlas.portfolio.analyze_allocation`: Inspect current asset/sector weights.
  - `atlas.portfolio.propose_targets`: Propose hypothetical target allocations (validates weights sum to 100%, long-only constraints).
  - `atlas.portfolio.calculate_allocation_delta`: Compute mathematical percentage point and notional deltas.
  - `atlas.portfolio.save_scenario_draft`: Save non-executing scenario draft.
- **Fixture C**: 100,000 USD portfolio with 60% Equity / 40% Bonds shifted to 50/50 target yields exact deltas of -10 pp (-10,000 USD) Equity and +10 pp (+10,000 USD) Bonds with zero ledger side effects.

### 4. Risk (`atlas.risk.*`)
- **Worker-Backed Computation & Immutability**:
  - Supported Models: `historical_var`, `parametric_var`, `expected_shortfall`, `stress_test_equity_rates`.
  - Full parameter validation (confidence level 95%–99.5%, horizons 1–21 days, lookback window 252 days).
  - Stress testing: 10% equity decline (-$6,000) and 100 bps rate shock (-$2,000 on bonds) yields simulated total impact of -$8,000 USD.
- **Fixture D**: Historical 99% 1-day VaR calculated mathematically and archived as an immutable run record.

---

## Security, Approval & Concurrency Architecture

### Exact Approval Binding (Fixture E)
User approval is cryptographically bound to:
$$\text{Approval} = f(\text{user\_id}, \text{tenant\_id}, \text{action\_id}, \text{target\_resource}, \text{resource\_revision}, \text{normalized\_args\_hash}, \text{preview\_hash}, \text{expires\_at})$$
If an attacker attempts to substitute a different target resource or modify arguments between approval and execution, execution is denied with `AiActionApprovalMismatchError`.

### Optimistic Concurrency & Revision Locking (Fixture F)
Prior to execution, the target resource revision is checked. If another process or user modified the resource after the preview was generated, execution is blocked with `AiActionResourceConflictError`, preventing stale overwrites.

### Idempotency & Replay Prevention (Fixture G)
Every effectful action execution requires an `idempotency_key`. Repeated submissions return cached execution receipts without duplicate processing. Approvals are marked consumed upon execution, preventing approval replay attacks.

### Multi-Step Workflow Coordination (Fixture J)
Multi-action plans (e.g. Screener -> Chart Comparison) follow explicit dependency graphs. If a step fails, prior successful steps remain recorded in immutable receipts, the plan is marked `PARTIALLY_COMPLETED`, and subsequent dependent steps are halted safely.

---

## API Endpoints (`/api/v1/ai/actions`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/ai/actions/capabilities` | List all supported action capabilities and schemas |
| `POST` | `/api/v1/ai/actions/plan` | Parse intent, resolve context, and build action plan with previews |
| `GET` | `/api/v1/ai/actions/plans/{id}` | Retrieve action plan and preview diffs |
| `POST` | `/api/v1/ai/actions/plans/{id}/approve` | Bind explicit user confirmation to preview hash |
| `POST` | `/api/v1/ai/actions/plans/{id}/deny` | Deny proposed action |
| `POST` | `/api/v1/ai/actions/plans/{id}/execute` | Execute approved plan with idempotency protection |
| `GET` | `/api/v1/ai/actions/receipts/{id}` | Retrieve immutable execution receipt |
| `POST` | `/api/v1/ai/actions/actions/{id}/undo` | Restore prior snapshot for reversible operations |
| `GET` | `/api/v1/ai/actions/history` | List authorized action history for current user |

---

## Golden Reference Fixture Matrix

| Fixture | Scenario | Domain | Verification Result |
|---|---|---|---|
| **Fixture A** | Add 20 & 50 SMA to chart and undo | Charts | Verified: SMA 20/50 added, diff verified, undo restores prior revision |
| **Fixture B** | India Tech screener: rev growth > 15%, profit > 0, cap > 10,000 Cr | Screeners | Verified: Matches TCS & INFY, excludes Reliance & Smallcap |
| **Fixture C** | Portfolio 60/40 Equity/Bonds shifted to 50/50 target | Portfolios | Verified: -10 pp / -$10k Equity, +10 pp / +$10k Bonds, 0 ledger mutations |
| **Fixture D** | 99% 1-day Historical VaR on TEST_P | Risk | Verified: Real calculation, immutable run, undo rejected |
| **Fixture E** | Approval substitution attack (Chart A approved, Port B attempted) | Security | Verified: Blocked with `AiActionApprovalMismatchError` |
| **Fixture F** | Revision conflict during concurrent screener modification | Concurrency | Verified: Blocked with `AiActionResourceConflictError` |
| **Fixture G** | Duplicate submission with same idempotency key | Idempotency | Verified: Exact 1 execution, second resolves from cache |
| **Fixture H** | Malicious prompt injection attempting ledger mutation | Security | Verified: Blocked with `AiActionLedgerMutationProhibitedError` |
| **Fixture I** | Prohibited trading order ("Buy 100 shares immediately") | Security | Verified: Blocked with `AiActionBrokerExecutionProhibitedError` |
| **Fixture J** | Multi-step plan: Step 1 succeeds, Step 2 fails | Coordination | Verified: Marked `PARTIALLY_COMPLETED` with discrete step receipts |

---

## Roadmap Progression
- **Stage 128 Complete**: AI Financial Actions for Charts, Screeners, Portfolios, and Risk.
- **Stage 129 Handoff**: Maps milestones, following the frozen canonical roadmap. Geospatial infrastructure remains completely untouched.

