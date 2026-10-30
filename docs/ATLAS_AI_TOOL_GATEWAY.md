# ATLAS AI Tool Gateway — Architectural Specification

**Canonical Roadmap:** Stage 126 of 150  
**Stage Title:** Build Secure ATLAS AI Tool Gateway  
**Primary Feature:** AI Tool Gateway and Permission-Aware Tool Calling  
**Primary Module:** ATLAS AI Assistant (`/ai` & persistent AppShell overlay)  
**Security Standard:** Zero-Trust Tool Invocation, Least Privilege, Server Authority, IDOR Defense, Prompt-Injection Fencing, Human-in-the-Loop Governance  

---

## 1. Executive Summary

Stage 126 establishes the **ATLAS Institutional AI Tool Gateway**, providing secure, typed, permission-aware function calling that connects the Stage 124 AI Assistant V1 and Stage 125 Context Awareness Engine to real, authorized, read-only ATLAS financial foundations.

Before Stage 126, the conversational AI operated purely on conversational turns and static context blocks. Stage 126 empowers the model to discover, propose, and execute structured operations against ATLAS financial data engines—including instrument search, market quotes, corporate fundamentals, macroeconomic observations, licensed news headlines, portfolio allocations, and historical risk runs—while treating the model as an **untrusted decision-making component**.

---

## 2. Strict Architectural Boundaries

| Milestone | Ownership & Capabilities | Prohibited Capabilities in Stage 126 |
|---|---|---|
| **Stage 126 (Current)** | Read-only financial tools (`DISCOVERY`, `DATA_READ`, `ANALYTICAL_READ`, `STATUS_READ`), Typed Argument Validation, Anti-IDOR Resource Authorization, Provider Disclosure Policies, Human Approval Engine, Prompt-Injection Fencing. | Arbitrary Python/SQL/shell execution, broker trading, portfolio mutations, workspace/chart mutations, broad vector RAG. |
| **Stage 127 (Future)** | AI Research and Retrieval-Augmented Generation: Document indexing, semantic vector pipelines, citation graphs. | Must not be implemented prematurely in Stage 126. |
| **Stage 128 (Future)** | Financial AI Actions: AI-driven portfolio rebalancing, chart mutation, order staging, screener mutations. | Strictly prohibited in Stage 126. |
| **Stage 123 Boundary** | Sandboxed Interactive Terminal Execution. | AI tools cannot invoke `execute_python`, `execute_sql`, or `execute_shell`. |
| **Trading Boundary** | Broker connectivity and trading execution. | Zero broker access; no trading backdoor. |

---

## 3. Core Architecture & Pipeline

```
[ User Request ] ───► [ Stage 124/125 Assistant Overlay ]
                                │
                                ▼
                   [ Tool Discovery Service ]
                    (Filters by Scope, Preferences,
                     Route Affinity, & Model Support)
                                │
                                ▼
                       [ Model Provider ]
                    (Proposes tool_id & arguments)
                                │
                                ▼
                  [ AiToolSecurityGateway ]
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
[ Anti-IDOR Resource ACLs ]                  [ Human Approval Engine ]
(Portfolio / Risk Run Ownership)              (SHA-256 Hash Binding, TTL,
                                               Replay Prevention)
        │                                               │
        └───────────────────────┬───────────────────────┘
                                ▼
                      [ AiToolDispatcher ]
                    (Schema Validation, Bounded
                     Timeout, Output Truncation)
                                │
                                ▼
                   [ Typed Financial Adapter ]
                  (19 Canonical Read-Only Tools)
                                │
                                ▼
                   [ Grounded Output Turn ]
                 (Enclosed in Fenced Delimiters,
                  Injected into Model Prompt)
                                │
                                ▼
                  [ Final Synthesized Answer ]
```

---

## 4. Canonical Tool Catalog

| Tool ID | Category | Capability Scope | Approval Class | Description |
|---|---|---|---|---|
| `atlas.instrument.search` | `DISCOVERY` | `tools:instrument:read` | `NO_APPROVAL_REQUIRED` | Search canonical instruments across global exchanges. |
| `atlas.instrument.get` | `DATA_READ` | `tools:instrument:read` | `NO_APPROVAL_REQUIRED` | Retrieve authorized instrument metadata (FIGI, ISIN). |
| `atlas.company.get` | `DATA_READ` | `tools:company:read` | `NO_APPROVAL_REQUIRED` | Retrieve corporate profile and sector classification. |
| `atlas.company.financials` | `DATA_READ` | `tools:company:read` | `NO_APPROVAL_REQUIRED` | Retrieve point-in-time financial statement facts with units. |
| `atlas.market.quote` | `DATA_READ` | `tools:market:read` | `NO_APPROVAL_REQUIRED` | Retrieve authorized market price quote with attribution. |
| `atlas.market.history_summary`| `ANALYTICAL_READ` | `tools:market:read` | `NO_APPROVAL_REQUIRED` | Summarize historical price action and realized volatility. |
| `atlas.watchlist.list` | `DATA_READ` | `tools:watchlist:read` | `NO_APPROVAL_REQUIRED` | List permitted watchlists and securities for user. |
| `atlas.screener.get_definition`| `DATA_READ` | `tools:screener:read` | `NO_APPROVAL_REQUIRED` | Inspect screener filter rules (read-only, no mutations). |
| `atlas.economics.search_series`| `DISCOVERY` | `tools:economics:read` | `NO_APPROVAL_REQUIRED` | Discover macroeconomic indicator series (FRED/BLS). |
| `atlas.economics.get_observations`| `DATA_READ` | `tools:economics:read` | `NO_APPROVAL_REQUIRED` | Retrieve chronological observations with dates and units. |
| `atlas.news.search_headlines` | `DATA_READ` | `tools:news:read` | `NO_APPROVAL_REQUIRED` | Search licensed wire headlines with injection defense. |
| `atlas.research.list_metadata` | `DATA_READ` | `tools:research:read` | `NO_APPROVAL_REQUIRED` | List authorized research report metadata and analyst notes. |
| `atlas.portfolio.list` | `DATA_READ` | `tools:portfolio:read` | `NO_APPROVAL_REQUIRED` | List authorized portfolios for authenticated user. |
| `atlas.portfolio.get_summary` | `DATA_READ` | `tools:portfolio:read` | `NO_APPROVAL_REQUIRED` | Retrieve allocation and total value (holdings redacted). |
| `atlas.portfolio.get_performance`| `ANALYTICAL_READ`| `tools:portfolio:read` | `NO_APPROVAL_REQUIRED` | Retrieve return metrics, alpha, beta, tracking error. |
| `atlas.risk.list_runs` | `DATA_READ` | `tools:risk:read` | `NO_APPROVAL_REQUIRED` | List historical risk calculation runs for user portfolios. |
| `atlas.risk.get_run_summary` | `ANALYTICAL_READ` | `tools:risk:read` | `NO_APPROVAL_REQUIRED` | Retrieve immutable historical risk metrics (VaR 95%, CVaR). |
| `atlas.data.list_sources` | `DISCOVERY` | `tools:data:read` | `NO_APPROVAL_REQUIRED` | Discover eligible financial data catalog sources. |
| `atlas.saved.list` | `DATA_READ` | `tools:saved:read` | `NO_APPROVAL_REQUIRED` | Read Stage 119 saved resource references. |
| `atlas.workspace.list` | `DATA_READ` | `tools:workspace:read` | `NO_APPROVAL_REQUIRED` | Read Stage 120 multi-panel workspace metadata. |

---

## 5. Security & Governance Infrastructure

### 5.1 The Model Is an Untrusted Component
- The model proposes tool invocations (`tool_id` and arguments).
- The server validates arguments strictly against typed schemas.
- The server authorizes every invocation using existing authorization and tenant policies.
- Rejection of unknown tools yields `AI_TOOL_NOT_FOUND` without fallback to arbitrary execution.

### 5.2 Anti-IDOR Resource Authorization
- Invocations referencing private resources (e.g. `portfolio_id`, `run_id`, `screener_id`) enforce strict owner-bound ACL checks.
- Unauthorized access raises `AiToolResourceAccessDeniedError` (`AI_TOOL_RESOURCE_ACCESS_DENIED`) without leaking resource existence or metadata.

### 5.3 Cryptographic Human Approval Framework
- Tools classified as `USER_CONFIRMATION_REQUIRED` issue an approval token (`AiToolApprovalRequest`).
- The approval token binds a deterministic SHA-256 hash of the normalized arguments (`normalized_arguments_hash`).
- If an attacker swaps arguments between approval and execution, the gateway rejects invocation with `AiToolApprovalMismatchError`.
- Tokens have a 5-minute TTL and enforce strict one-time consumption (replay prevention).

### 5.4 Third-Party Provider Disclosure Policies
- Any tool returning data marked `ProviderDisclosurePolicy.PROHIBITED` is denied from external model transmission (`AiToolProviderDisclosureDeniedError`).
- Redacted fields are stripped before payload leaves the institutional perimeter.

### 5.5 Indirect Prompt-Injection Fencing
- All untrusted external text (e.g. news headlines, analyst notes) is sanitized and enclosed in `<atlas_verified_financial_context data-purpose="untrusted-read-only-financial-context">`.
- XML tags and markdown escapes within untrusted text are neutralized, preventing prompt execution hijacking.

### 5.6 Infinite Loop & Sequence Limit Enforcement
- Maximum tool invocations per generation run is capped at 4.
- Exceeding the sequence limit raises `AiToolSequenceLimitExceededError`, halting generation safely and preventing uncontrolled token consumption.

---

## 6. Verification Matrix (Reference Fixtures A–J)

| Fixture | Scenario | Expected Behavior | Verification Status |
|---|---|---|---|
| **Fixture A** | Instrument Search | Returns canonical MSFT record with FIGI, ISIN, exchange; no ticker guessing. | PASS (pytest) |
| **Fixture B** | Market Quote | Returns live BBO quote or explicit `quote_available: false`; no data fabrication. | PASS (pytest) |
| **Fixture C** | Company Financials | Retrieves FY24 ($100M) and FY25 ($125M) revenue; computes 25.0% annual growth. | PASS (pytest) |
| **Fixture D** | Unauthorized Portfolio | User B attempts `atlas.portfolio.get_summary(P)` owned by User A -> Access Denied. | PASS (pytest) |
| **Fixture E** | Provider Disclosure | Data with `PROHIBITED` disclosure policy is blocked from model transmission. | PASS (pytest) |
| **Fixture F** | Prompt Injection | Malicious instruction inside headline is fenced in read-only tags, not executed. | PASS (pytest) |
| **Fixture G** | Unknown Tool | Model proposes `atlas.system.execute_anything` -> `AI_TOOL_NOT_FOUND`. | PASS (pytest) |
| **Fixture H** | Infinite Tool Loop | Repeated proposals terminate at limit 4 with `AI_TOOL_SEQUENCE_LIMIT_EXCEEDED`. | PASS (pytest) |
| **Fixture I** | Approval Argument Swap | Approval issued for Resource A cannot be executed for Resource B -> Mismatch error. | PASS (pytest) |
| **Fixture J** | Historical Risk Run | `atlas.risk.get_run_summary` retrieves immutable original metrics without mutating. | PASS (pytest) |

