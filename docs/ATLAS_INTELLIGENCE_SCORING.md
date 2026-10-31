# ATLAS STAGE 139 — INTELLIGENCE SCORING, PRIORITIZATION, EXPLAINABILITY, VALIDATION AND GOVERNANCE ENGINE

## 1. Executive Architecture Summary

**Stage 139: Intelligence Scoring** delivers the institutional-grade, source-backed scoring, prioritization, explainability, validation, and governance engine for ATLAS.

It builds directly upon the foundational capabilities of:
- **Stage 135**: Universal Event Model & Canonical Event Ingestion
- **Stage 136**: Event-to-Entity Knowledge Graph & Typed Predicates
- **Stage 137**: Financial & Economic Exposure Engine & Explainable Math Formulas
- **Stage 138**: INTELLIGENCE V1 Master Command Center Workspace

Stage 139 answers:
**"WHICH VERIFIED ITEMS ARE MOST RELEVANT TO THE USER'S SPECIFIC INVESTIGATION, WHY WERE THEY PRIORITIZED, AND HOW RELIABLE IS THAT PRIORITIZATION?"**

---

## 2. Fundamental Scoring Principles & Strict Invariants

1. **A Score Is an Operational Measurement, NOT a Market Prediction**:
   - Scores represent human review urgency, relational directness, portfolio holdings weight, and evidence corroboration.
   - Prohibited interpretations: Stock price directional predictions, corporate bankruptcy probabilities, expected financial drawdowns, or automated trading triggers.
   - An event scoring 85/100 does **not** mean an 85% probability of affecting markets or an 85% loss risk.
2. **Deterministic Additive Baseline & Exact Explainability**:
   - $\text{Priority Index} = \frac{\sum_{i \in \text{available}} \text{weight}_i \times \text{transformed}_i}{\sum_{j \in \text{available}} \text{weight}_j} \times 100$
   - Individual factor contribution points sum **identically** to the final score value, guaranteeing mathematical explainability without residual discrepancies.
3. **Bitemporal Look-Ahead Bias Prevention**:
   - All feature extraction strictly enforces that feature publication and availability timestamps must not exceed the evaluation `known_as_of` horizon.
   - Any attempt to score historical data with future sources raises `ScoringLookAheadViolationError`.
4. **Anti-Gaming Anti-Syndication Invariant (Fixture E)**:
   - Multiple syndicated copies sharing the same root article fingerprint or wire report count as 1 independent confirmation (`independent_source_count = 1`), preventing synthetic corroboration inflation.
5. **Multi-Tenant Portfolio Privacy (Fixture D)**:
   - Proprietary portfolios, holdings, NAV weights, and portfolio attention scores are isolated to authenticated tenants. Unauthorized requests raise `ScoringTenantAccessDeniedError`.
6. **Stage 140 Boundary Enforcement**:
   - Prohibits automated God's Eye intelligence bots, autonomous surveillance agents, or synthetic execution loops. Complete Stage 139 and stop.

---

## 3. Primary Scoring Objectives & Ontology

| Objective ID | Target Construct | Default Scale | Key Factor Inputs | Prohibited Interpretations |
| :--- | :--- | :--- | :--- | :--- |
| `EVENT_REVIEW_PRIORITY` | Operational triage urgency index | 0–100 Index | Direct Entity Match, Independent Sources, Primary Filing, Recency | Stock return forecast, market impact probability, trade trigger |
| `EVENT_ENTITY_RELEVANCE` | Direct vs indirect graph connection | 0–100 Index | Predicates (`ISSUED_BY`, `TARGET_OF`, etc.), Hop Distance | Financial contagion coefficient, equity beta transmission |
| `PORTFOLIO_EVENT_ATTENTION` | Attention index based on authorized holdings | 0–100 Index | Portfolio NAV weight ($w_i$), Gross exposure, Direct issuer | Value-at-Risk (VaR), loss probability, expected drawdown |
| `ECONOMIC_EVENT_RELEVANCE` | Relevance to monetary policy & indicators | 0–100 Index | Central bank policy decision, release magnitude, sovereign jurisdiction | Universal equity beta, GDP growth forecast |
| `GEOGRAPHIC_EVENT_RELEVANCE` | Spatial co-location buffer | 0–100 Index | Distance step function ($d \le 10\text{km} \to 1.0$), Facility match | Confirmed asset damage, facility outage, business interruption loss |
| `SOURCE_EVIDENCE_ASSESSMENT` | Grounding, verification & conflict status | 0–100 Index | Deduplicated sources, Primary filings, Conflict penalties | Absolute philosophical truth, editorial credibility ranking |

---

## 4. Mathematical Factor Transformations

Raw feature inputs are mapped into normalized $[0.0, 1.0]$ intervals via domain-specific transformations:

1. **Binary Eligibility**:
   $$f(x) = \begin{cases} 1.0 & \text{if true} \\ 0.0 & \text{if false} \end{cases}$$
2. **Bounded Proportion** (e.g. Portfolio NAV Weight):
   $$f(x) = \min\left(\max\left(\frac{x}{x_{\max}}, 0.0\right), 1.0\right)$$
3. **Exponential Recency Decay**:
   $$f(t) = 2^{-t / t_{\text{half-life}}}$$
   Domain half-lives: breaking alerts (24h), earnings filings (72h), central bank decisions (168h), regulatory actions (720h).
4. **Distance Step Function**:
   $$f(d) = \begin{cases} 1.0 & \text{if } d \le 10\text{ km} \\ 0.70 & \text{if } d \le 50\text{ km} \\ 0.40 & \text{if } d \le 100\text{ km} \\ 0.20 & \text{if } d \le 250\text{ km} \\ 0.05 & \text{otherwise} \end{cases}$$
5. **Ordinal Count Saturation**:
   $$f(c) = \min\left(\frac{c}{c_{\text{sat}}}, 1.0\right)$$

---

## 5. Model Governance & Versioning Lifecycle

- **Governance States**: `DRAFT`, `VALIDATING`, `VALIDATED`, `APPROVED`, `ACTIVE`, `SHADOW`, `DISABLED`, `ROLLED_BACK`, `RETIRED`.
- **Validation Gates**: Candidate models must achieve $\text{NDCG}@10 \ge 0.70$ and zero look-ahead violations on historical benchmark datasets before promotion.
- **Rollback Safeguard (Fixture J)**:
  - If a candidate version fails validation or produces unexpected drift, an authorized administrator (`RISK_ADMIN`) can roll back production to the previously approved version.
  - Generates an immutable `ScoringGovernanceAuditRecord` tracking user ID, timestamp, previous version, and rationale.

---

## 6. Reference Fixture Verification Matrix (Fixtures A through S)

The implementation is verified against 19 canonical test fixtures (`apps/api/tests/test_intelligence_stage139_scoring.py`):

- **Fixture A (Direct Relevance)**: Verified earnings announcement directly linked to issuer; no invented price impact.
- **Fixture B (Indirect Relevance)**: Subsidiary incident yields qualified indirect context for parent with explicit path explanation.
- **Fixture C (Portfolio Attention)**: Verified 20% NAV holding weight produces elevated attention without inferring 20% loss.
- **Fixture D (Portfolio Privacy)**: Tenant B cannot access or compute attention scores for Tenant A's private portfolio.
- **Fixture E (Article Duplication / Anti-Gaming)**: 10 syndicated wire copies yield `independent_source_count = 1`.
- **Fixture F (Source Conflict)**: Conflicting source values trigger conflict flag and evidence penalty.
- **Fixture G (Data Coverage)**: Sparse event records report explicit coverage ratio and missing feature list without silent 0 imputation.
- **Fixture H (Future Information / Look-Ahead Bias)**: Event published after `known_as_of` rejected with `ScoringLookAheadViolationError`.
- **Fixture I (Model Revision & Comparison)**: Compares policy v1 vs v2 with exact factor contribution deltas.
- **Fixture J (Model Rollback)**: Unauthorized user blocked from activating models; rollback restores approved version with audit trail.
- **Fixture K (Historical Portfolio Snapshot)**: Portfolio attention uses historical holdings snapshot valid at as-of date.
- **Fixture L (Geographic Proximity)**: Spatial distance scored (12 km maps to 0.70) without inferring physical asset destruction.
- **Fixture M (Category Comparability)**: Distinct objectives prevent meaningless magnitude comparison between earthquakes and rate hikes.
- **Fixture N (Probabilistic Calibration Limits)**: Computes Brier score and ECE when binary targets exist; marks not applicable otherwise.
- **Fixture O (Source Retraction)**: Retracted event marked `NOT_APPLICABLE` with `None` score.
- **Fixture P (Quota & Resource Protection)**: Ranking requests exceeding 500 candidate events raise `ScoringQuotaExceededError`.
- **Fixture Q (Ranking Stability & Deterministic Ties)**: Identical candidates sorted deterministically by score, valid_at, and event_id.
- **Fixture R (Missing Source License)**: Restricted sources omitted gracefully without data leakage.
- **Fixture S (Scoring Semantics)**: High priority score (89.8/100) interpreted strictly as review triage recommendation.

---

## 7. REST API Endpoints

The scoring API is mounted at `/api/v1/intelligence/scoring`:

- `GET /capabilities`: Scoring capabilities, supported objectives, scales, and compliance guarantees.
- `GET /objectives`: List all canonical scoring objectives.
- `GET /objectives/{objective_id}`: Retrieve single objective definition.
- `GET /models`: List registered scoring models and active versions.
- `GET /models/{model_id}`: Retrieve model definition.
- `GET /policies`: List scoring policies with factor weights and coverage thresholds.
- `GET /policies/{policy_id}`: Retrieve policy details.
- `POST /scores/calculate`: Calculate point-in-time score and exact factor contributions.
- `POST /rankings/query`: Rank candidate events with deterministic secondary tie-breaking.
- `POST /rankings/compare`: Compare two scoring model versions on the same event.
- `GET /evaluations`: List historical model evaluation manifests.
- `GET /evaluations/{evaluation_id}`: Retrieve evaluation manifest by ID.
- `GET /telemetry`: Operational health, score distribution, and drift status.
- `POST /governance/models/{model_id}/activate`: Promote validated model version to production.
- `POST /governance/models/{model_id}/rollback`: Roll back model to previous approved version.
- `GET /governance/audit`: Retrieve immutable governance audit log.
