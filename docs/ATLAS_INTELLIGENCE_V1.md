# ATLAS STAGE 138 — INTELLIGENCE V1: THE UNIFIED INSTITUTIONAL FINANCIAL INTELLIGENCE WORKSPACE

## 1. Executive Architecture Summary

**Stage 138: Intelligence V1** delivers the institutional-grade, multi-domain financial intelligence command center for ATLAS. It unifies the preceding four stages:
- **Stage 135**: Universal Event Model & Canonical Event Ingestion
- **Stage 136**: Event-to-Entity Knowledge Graph & Typed Predicates
- **Stage 137**: Financial & Economic Exposure Engine & Explainable Math Formulas
- **Stages 129–134**: Geospatial Infrastructure, Corporate Geography & Live Physical World Observations
- **Stage 127**: Source Grounding & Provenance Lineage
- **Stages 120–121**: Multi-Panel Workspaces & Cross-Panel Linking Channels

Intelligence V1 provides portfolio managers, quantitative analysts, and risk officers with a single, verifiable, bitemporal workspace to investigate global financial, corporate, macroeconomic, regulatory, and physical phenomena without speculative hallucinations or invented metrics.

---

## 2. Canonical Investigation Sequence

All intelligence queries, cross-module linkings, and automated investigations strictly follow the canonical 9-step evidence chain:

```
[ EVENT ]
    │
    ▼
[ VERIFIED SOURCES ] (SEC EDGAR, Federal Reserve, USGS, etc.)
    │
    ▼
[ RELATED ENTITIES ] (Canonical Companies, Issuers, Central Banks, Countries)
    │
    ▼
[ KNOWLEDGE GRAPH ] (Typed Directed Edges: ISSUED_BY, AFFECTS_COMMODITY, etc.)
    │
    ▼
[ DOCUMENTED EXPOSURE ] (Formulas, Weights, Dollar Exposure, Direct/Indirect)
    │
    ▼
[ GEOGRAPHIC CONTEXT ] (Facilities, Ports, Coordinates, Proximity Buffers)
    │
    ▼
[ FINANCIAL & ECONOMIC DATA ] (Official Metrics, Time Series, Disclosures)
    │
    ▼
[ RESEARCH EVIDENCE ] (Primary Filings, Citations, Document Snapshots)
    │
    ▼
[ SAVED INVESTIGATION ] (Bitemporal Snapshot, Preset Layout, Tenant Isolation)
```

---

## 3. Strict Scope & Boundary Invariants

1. **Stage 139 Boundary (No Composite Intelligence Scoring)**:
   - Intelligence V1 strictly reports factual metrics (e.g. source verification count, event magnitude, portfolio weight, exposure dollar amount).
   - Prohibited: Composite risk/opportunity ratings (e.g. 0–100 scores), synthetic sentiment indices, stock price directional predictions, or buy/sell signal recommendations.
2. **Stage 140 Boundary (No Premature God's Eye Automation)**:
   - Automated global surveillance agents and God's Eye master orchestration are deferred to Stage 140.
3. **Zero Numerical or Lineage Fabrication**:
   - Zero invented events or phantom relationships.
   - Unavailable exposures explicitly return `SectionStatus.EMPTY` or `EXPOSURE_UNAVAILABLE` rather than defaulting to $0 or 0%.
   - Physical proximity is reported with exact distance kilometers and explicit status `DAMAGE_ASSESSMENT_PENDING / UNKNOWN`.
4. **Bitemporal Point-in-Time Integrity**:
   - Every historical query enforces `valid_at` and `known_as_of` filters.
   - Prevents look-ahead bias by excluding future revisions or retractions from historical queries.

---

## 4. Multi-Domain Overview Orchestrator & Partial Failure Resilience

The backend master orchestrator (`AtlasIntelligenceService.get_unified_overview`) aggregates cross-domain intelligence sections:
- `major_events`: Canonical events within the temporal horizon.
- `key_entities`: Monitored companies, issuers, and macroeconomic authorities.
- `portfolio_exposures`: Tenant-isolated portfolio holdings and look-through exposures.
- `geospatial_alerts`: Physical phenomena in proximity to corporate assets.
- `macroeconomic_decisions`: Central bank announcements and sovereign benchmark releases.

### Resilience Invariant (Fixture H)
When an individual data source experiences degradation or an outage (e.g., Financial News Wire service outage), the orchestrator:
1. Marks the affected section as `SOURCE_UNAVAILABLE` or `PARTIAL`.
2. Attaches actionable warning metadata to the section and global overview envelope.
3. Serves the unaffected sections (e.g., SEC EDGAR corporate filings, Federal Reserve policy releases) with 100% operational fidelity and `READY` status.

---

## 5. Unified Fast Search & Canonical Entity Disambiguation

The unified search engine (`AtlasIntelligenceService.unified_search`) performs cross-domain discovery across events, entities, and sources:
- **Disambiguation Rules (Fixture I & Fixture O)**:
  - Resolves corporate entities by canonical identifiers (`COMP_AAPL`, `COMP_ACME`), legal name, ticker symbol, and CIK/LEI.
  - Distinguishes between companies, securities, central banks, and countries.
  - Returns explicit disambiguation strings (e.g., `Issuer of AAPL common stock • US Tech / Hardware`).
- **Permission Awareness (Fixture M)**:
  - Search results flag `is_entitled: false` when a tenant lacks the required subscription or institutional clearance for sensitive data sources.

---

## 6. Coordinated Multi-Panel Investigation Presets

Intelligence V1 ships with five canonical workspace presets:

| Preset ID | Name | Panel Configuration | Default Link Channel |
| :--- | :--- | :--- | :--- |
| `preset_event_investigation` | Global Event Investigation | Event Monitor, Event Inspector, Entity Graph, Research Evidence | `event_channel` |
| `preset_company_intelligence` | Company & Issuer Intelligence | Entity Context, Entity Graph, Exposure Summary, Source Inspector | `entity_channel` |
| `preset_economic_decision` | Central Bank & Macro Decision | Event Monitor, Entity Context, Exposure Inspector, Research Evidence | `macro_channel` |
| `preset_geographic_investigation` | Physical & Infrastructure Intelligence | Event Monitor, Geography Map, Exposure Inspector, Coverage Panel | `spatial_channel` |
| `preset_portfolio_exposure` | Portfolio Look-Through Analysis | Exposure Summary, Exposure Inspector, Entity Graph, Coverage Panel | `portfolio_channel` |

### Cross-Panel Linking Invariant (Fixture L)
Panels bound to a shared channel synchronize immediately upon selection (e.g. selecting an event in `EVENT_MONITOR` updates `EVENT_INSPECTOR` and `ENTITY_GRAPH`). Independent panels maintain their state without unwanted cross-talk.

---

## 7. Reference Fixture Verification Matrix (Fixtures A through O)

The implementation is verified against 15 canonical test fixtures (`apps/api/tests/test_intelligence_stage138_v1.py`):

- **Fixture A (Event Investigation)**: FOMC Rate Decision verified via Federal Reserve official bulletin, mapped to US jurisdiction.
- **Fixture B (Company Earnings)**: Apple Inc. Q4 10-K filing verified via SEC EDGAR CIK: 0000320193; factual metrics only.
- **Fixture C (Private Portfolio Protection)**: Multi-tenant portfolio isolation; Tenant A holdings are strictly inaccessible to Tenant B.
- **Fixture D (Geospatial Event)**: Earthquake near Acme manufacturing facility; distance 45.2 km confirmed, damage status `UNKNOWN`.
- **Fixture E (Source Conflict Preservation)**: Conflicting source statements preserved side-by-side with individual provenance.
- **Fixture F (Event Retraction Handling)**: Retracted claims flagged `RETRACTED` and excluded from verified knowledge graph.
- **Fixture G (Historical Knowledge As-Of)**: As-of timestamp query filters out subsequent revisions and restatements.
- **Fixture H (Partial Source Outage Resilience)**: Downed news feed produces warning while SEC and Fed feeds remain operational.
- **Fixture I (Ambiguous Identity Disambiguation)**: ACME ticker disambiguated to Acme Global Corp (COMP_ACME).
- **Fixture G (Exposure vs Loss Distinction)**: Direct revenue exposure documented without equating exposure to realized loss.
- **Fixture K (Live vs Historical Snapshot Isolation)**: Updating current state does not mutate saved point-in-time snapshots.
- **Fixture L (Workspace Linking Channel Coordination)**: Linked panels update synchronously; unlinked panels remain isolated.
- **Fixture M (Source Entitlement Enforcement)**: Non-entitled data sources return explicit denial with upgrade instructions.
- **Fixture N (Unavailable Exposure Reporting)**: Absence of quantitative exposure returns `EMPTY` / `UNAVAILABLE` rather than synthetic zeros.
- **Fixture O (Unified Cross-Domain Search)**: Search disambiguates across events, entities, and sources.

---

## 8. REST API Endpoints

The API router is mounted at `/api/v1/intelligence`:

- `GET /api/v1/intelligence/capabilities`: Intelligence V1 subsystem metadata and supported features.
- `GET /api/v1/intelligence/overview`: Multi-domain aggregated overview with partial failure resilience.
- `GET /api/v1/intelligence/presets`: Available investigation multi-panel presets.
- `GET /api/v1/intelligence/panels`: Available panel descriptors and linking contracts.
- `GET /api/v1/intelligence/search`: Fast unified search across events, entities, and sources.
- `GET /api/v1/intelligence/sources/status`: Data source freshness, latency, and operational health.
- `POST /api/v1/intelligence/sources/{source_id}/simulate-outage`: Simulate data source outage for failover testing.
- `POST /api/v1/intelligence/sources/{source_id}/restore`: Restore data source to operational health.
- `GET /api/v1/intelligence/entities/context`: Resolve canonical entity context, links, and exposures.
- `GET /api/v1/intelligence/investigations`: List saved investigations for the authenticated tenant.
- `POST /api/v1/intelligence/investigations`: Save a point-in-time investigation snapshot.
- `GET /api/v1/intelligence/investigations/{investigation_id}`: Retrieve a saved investigation by ID.
