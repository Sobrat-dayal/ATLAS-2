# ATLAS STAGE 140: GOD'S EYE FINANCIAL INTELLIGENCE

## Institutional-Grade Financial Situational Awareness and Universal Command Center

### 1. Executive Architecture Summary

Stage 140 delivers **God's Eye Financial Intelligence**, the unified institutional situational awareness command center for the ATLAS operating system. It serves as the institutional culmination of the platform's intelligence and spatial systems, orchestrating:
- **2D/3D Global Financial Earth**: High-performance MapLibre GL JS (2D), CesiumJS (3D Globe), and deck.gl/H3 spatial grids (Stages 129–131).
- **Corporate Geography & Infrastructure**: Corporate headquarters, manufacturing facilities, data centers, maritime container ports, strategic chokepoints, pipelines, and power grids (Stages 132–133).
- **Physical-World Observations**: USGS seismic feeds, NOAA hurricane tracking, severe convective storms, and satellite thermal anomalies (Stage 134).
- **Universal Event Model & Timeline**: Bitemporal, multi-clock, multi-source deduplicated event registry (Stage 135).
- **Event-to-Entity Knowledge Graph**: Canonical graph resolution, entity linkers, and bounded graph traversals (Stage 136).
- **Financial & Economic Exposure Engine**: Point-in-time revenue concentration, supply chain dependencies, and portfolio look-through (Stage 137).
- **INTELLIGENCE V1 Workspace**: Multi-panel command center layouts and investigation presets (Stage 138).
- **Intelligence Scoring & Prioritization**: Explainable multi-factor scoring, priority ranking, and model governance (Stage 139).
- **Observational Market Context**: High-fidelity tick/yield data around events strictly separated from causal claims.
- **Bitemporal "World Time Travel"**: Zero look-ahead historical world reconstruction as-of any datetime $T$.

---

### 2. Strict Institutional Boundary Invariants

God's Eye enforces five categorical guardrails to prevent analytical misinterpretation, false precision, and regulatory non-compliance:

1. **No Fictional Omniscience**:
   - "God's Eye" is a branded product name for unified situational awareness. It aggregates licensed, statutory, and sensor feeds. It does not possess covert, classified, or omniscient surveillance capabilities.
2. **Correlation vs. Causation**:
   - Co-occurrence or temporal proximity between an event (e.g., FOMC rate announcement) and an asset price movement is purely observational. God's Eye explicitly disclaims causal transmission.
3. **Proximity vs. Damage**:
   - Spatial proximity of a facility to a physical hazard (e.g., TSMC Fab 18 situated 74 km from a M7.4 seismic epicenter) does NOT imply operational damage or business interruption. Damage status defaults to `UNKNOWN` until certified on-site inspection reports are filed.
4. **Exposure vs. Loss**:
   - Quantitative exposure metrics represent structural revenue concentrations or portfolio weights. They do not represent projected monetary loss, value-at-risk, or default probabilities.
5. **Priority vs. Prediction & No Autonomous Trading**:
   - Priority scores reflect operational review priority and informational importance, not price forecasts or trade signals. God's Eye performs no automated order routing, broker execution, or portfolio mutation.

---

### 3. The 8 Canonical Investigation Lenses

| Lens ID | Label | Primary Categories | Spatial Layers | View Mode |
| :--- | :--- | :--- | :--- | :--- |
| `GLOBAL_EVENTS` | Global Events Situational Awareness | Multi-domain (Financial, Corporate, Macro, Hazard) | Global Event Clusters, Macro Tints, Major Facilities | 2D / 3D |
| `MONETARY_POLICY` | Monetary Policy & Central Banks | Central Bank Decisions, Economic Releases | Central Bank HQs, Sovereign Yield Spreads | 2D MapLibre |
| `CORPORATE_INTELLIGENCE` | Corporate Intelligence & Filings | 10-K/10-Q Filings, Earnings, M&A, Executive Changes | Corporate HQs, Operational Facilities, Supply Hops | 2D MapLibre |
| `GEOPOLITICAL` | Geopolitical & Sanctions Intelligence | Sanctions (OFAC), Tariffs, Export Controls | Sanctioned Jurisdictions, Trade Corridors | 2D MapLibre |
| `COMMODITY_INFRASTRUCTURE` | Commodity & Physical Infrastructure | Ports, Chokepoints, Pipelines, Refineries, Grids | Maritime Ports, Chokepoints, Pipeline Grids | 3D Cesium |
| `PHYSICAL_WORLD` | Physical World & Natural Hazards | USGS Earthquakes, Tropical Storms, Wildfires | Seismic Epicenters, Hazard Radii, Critical Facilities | 3D Cesium |
| `PORTFOLIO_INTELLIGENCE` | Portfolio Holdings Look-Through | Portfolio Holdings, Indirect Facility Exposure | Portfolio Facility Exposure, Supply Chain Risks | Hybrid Split |
| `HISTORICAL_RESEARCH` | Historical Point-in-Time Reconstruction | All categories filtered strictly as-of datetime $T$ | Historical Timelines, Vintage Topology | 2D MapLibre |

---

### 4. 20 Reference Test Fixtures (A through T)

God's Eye has been verified against the 20 institutional test fixtures:
- **Fixture A (Monetary Policy)**: Central bank decision -> jurisdiction -> official bulletin -> time-aligned market context; no price forecasts.
- **Fixture B (Company Earnings)**: 10-K filing -> canonical issuer -> period -> graph -> verified financial metrics; no fake surprise.
- **Fixture C (Port Closure)**: Port P -> Operator O -> geometry; no fabricated supply-chain collapse or revenue loss.
- **Fixture D (Earthquake)**: USGS event -> nearby facility -> distance km confirmed; damage status `UNKNOWN`.
- **Fixture E (Sanctions)**: Official sanctions designation -> legal entity match; no false linkage to similarly named companies.
- **Fixture F (Portfolio Attention)**: Authorized portfolio -> holding H -> event E; Stage 137 exposure + Stage 139 attention; no loss forecast.
- **Fixture G (Historical Information)**: Event at T1, correction at T2; as-of query between T1 and T2 excludes future correction.
- **Fixture H (Source Outage)**: One provider offline; unaffected sources remain functional; no fake empty-world crash.
- **Fixture I (Market Coincidence)**: Stock move after rate decision; observational price context; no causal leap.
- **Fixture J (Private Portfolio Protection)**: User B cannot see User A's private portfolio, exposure, or attention score.
- **Fixture K (Source Revocation)**: Revocation locks derived outputs, invalidates cache, and updates licenses.
- **Fixture L (Historical Company Ownership)**: Corporate group reconstruction respects valid historical relationships at as-of date.
- **Fixture M (Scoring Version)**: Retains versioning; comparing v1 vs v2 explains factor delta without false probability claims.
- **Fixture N (Geographic Precision)**: Country-level event does not fabricate street coordinates or nearby facility links.
- **Fixture O (Workspace Linking)**: Linked panels synchronize; independent panels remain isolated; no echo loops.
- **Fixture P (AI Investigation)**: Authorized read-only investigation tool (`atlas.gods_eye.investigate`) returns verified evidence trail with unknowns disclosed.
- **Fixture Q (Graph Traversal Bounding)**: High-degree node traversal bounded to max depth/limit with pagination; no infrastructure crash.
- **Fixture R (Map Resource Cleanup)**: Switching 2D/3D and panels cleans up WebGL context and suspends inactive rendering loops.
- **Fixture S (Incomplete Global Coverage)**: Accurate reporting of unmonitored countries; missing data != 0.
- **Fixture T (Mixed Source Times)**: Distinguishes occurrence time, publication time, and ingestion time.

---

### 5. Backend REST API Endpoints

All endpoints are mounted under `/api/v1/intelligence/gods-eye`:
- `GET /capabilities`: Return stage, version, 8 lenses, guarantees, and disclaimers.
- `GET /lenses`: List the 8 canonical lenses with metadata.
- `GET /lens/{lens_id}`: Retrieve definition for a specific lens.
- `POST /investigate`: Execute cross-domain situational query.
- `GET /entity/{entity_id}`: Entity situational awareness query.
- `POST /historical-reconstruction`: Reconstruct world state as-of datetime $T$.
- `POST /compare-vintages`: Compare entity relationships across two historical vintages.
- `POST /ai-tool/investigate`: Authorized read-only AI investigation tool (`atlas.gods_eye.investigate`).

---

### 6. Verification and Test Results

- **Backend Pytest**: 29 passed in `apps/api/tests/test_intelligence_stage140_gods_eye.py`.
- **Regression Pytest Suite**: 126 passed across Stages 135–139. Total passing backend tests: **155**.
- **Frontend Unit Tests**: 313 passed cleanly in `pnpm --filter web test`.
- **Next.js Production Build**: Turbopack compiled successfully in 7.8s with 0 errors across all 39 static and dynamic routes.

