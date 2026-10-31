# ATLAS Event-to-Entity Knowledge Graph and Relationship Intelligence Engine (Stage 136)

## Overview

Stage 136 establishes the institutional-grade **Event-to-Entity Knowledge Graph and Relationship Intelligence Engine** for the ATLAS platform. It connects canonical universal events (Stage 135) to foundational financial, corporate, legal, geographic, macroeconomic, and physical infrastructure entities across `/intelligence`, `/news`, `/markets`, `/companies`, `/economics`, `/research`, `/maps`, and `/data`.

The core semantic question answered by this engine is:
> *"What verified entities are related to this event, and what evidence establishes each relationship?"*

---

## Architectural Invariants & Scope Boundaries

1. **Strict Separation from Financial Exposure (Stage 137 Boundary)**:
   - A verified relationship or geographic proximity is **not proof of economic exposure, operational downtime, or financial loss**.
   - Portfolio stress testing, value-at-risk, supply chain loss modeling, and revenue sensitivity belong strictly to Stage 137.
2. **Prohibited Causal Predicates**:
   - Predicates such as `AFFECTS`, `AFFECTED_BY`, `CAUSED_LOSS`, `DAMAGED`, `EXPOSED_TO`, `IMPACTED`, `DESTROYED`, and `BANKRUPTED` are strictly prohibited.
   - Any attempt to register or query these raises `ProhibitedPredicateError`.
3. **No Entity Conflation**:
   - Securities are not legal entities; issuers are not individual share classes; parent corporations are not subsidiaries.
   - Corporate earnings link to reporting issuers and explicitly cited primary instruments without security explosion.
4. **Sanctions Exact Entity Matching**:
   - Official sanctions designations require exact LEI, CIK, or registered identifier matches.
   - Fuzzy name similarity matching is strictly rejected to prevent false-positive designations of innocent firms.
5. **Relational-Adjacency PostgreSQL Storage**:
   - Stores graph adjacency relationships directly in the relational schema without secondary graph databases (e.g. Neo4j).
6. **Zero Look-Ahead Point-in-Time Evaluation**:
   - Every relationship edge records `knowledge_available_at` (system time) alongside `temporal_valid_from`/`to` (valid time).
   - Historical queries evaluate only edges known and valid at the specified historical timestamp $T$.

---

## Canonical Node Reference Model (`CanonicalGraphNodeRef`)

The engine indexes and resolves 16 canonical node types:

| Node Type | Canonical Registry / Source | Example Identifiers |
| :--- | :--- | :--- |
| `EVENT` | Stage 135 Universal Event Registry | Canonical Key, Event ID |
| `COMPANY` | ATLAS Company Registry | CIK, Ticker, LEI |
| `ISSUER` | Legal Issuer Registry | CIK, LEI, Country |
| `LEGAL_ENTITY` | Global Legal Entity Registry | LEI, CRN, OGRN |
| `FINANCIAL_INSTRUMENT` | ATLAS Instrument Registry | ISIN, FIGI, Ticker |
| `SECTOR` | GICS / ICB Classification | Sector Code |
| `INDUSTRY` | Industry Taxonomy | Industry Code |
| `COUNTRY` | ISO Sovereign Boundaries | ISO-2, ISO-3 |
| `ADMINISTRATIVE_REGION` | PostGIS Administrative Subdivisions | Region Code |
| `COMMODITY` | Global Commodity Benchmarks | Commodity Symbol |
| `ECONOMIC_INDICATOR` | Macroeconomic Series Registry | Series ID |
| `CENTRAL_BANK` | Central Bank Directory | Central Bank Code |
| `REGULATORY_AUTHORITY` | Regulatory Directory | Agency Code (SEC, DOJ) |
| `CORPORATE_FACILITY` | Stage 132 Facility Registry | Facility ID |
| `INFRASTRUCTURE_ASSET` | Stage 133 Infrastructure Registry | Asset ID |
| `OTHER_SUPPORTED_CANONICAL_ENTITY` | Custom Canonical Entities | Entity ID |

---

## Approved Directed Predicates

### Event-to-Entity Predicates
- `DIRECT_SUBJECT`: The entity is the explicit primary subject of the event.
- `EXPLICITLY_MENTIONS`: The entity is explicitly mentioned in disclosure or article text.
- `ANNOUNCED_BY`: Reporting company, issuer, or agency releasing the announcement.
- `ISSUED_BY`: Sovereign or regulatory authority issuing the decree or mandate.
- `REGULATED_BY`: Enforcement or reviewing regulatory agency.
- `OFFICIALLY_DESIGNATES`: Formal government sanctions designation (exact match only).
- `OFFICIAL_ACTION_TARGET`: Legal target of regulatory or antitrust enforcement.
- `CORPORATE_ACTION_PARTICIPANT`: Participant in corporate action (e.g., Acquirer in M&A).
- `CORPORATE_ACTION_TARGET`: Target firm of corporate transaction.
- `CONCERNS_INSTRUMENT`: Explicit primary security referenced in the event.
- `RELEASES_INDICATOR`: Statistical indicator series released.
- `DECIDED_BY`: Central bank or monetary committee decision maker.
- `HAS_ISSUING_JURISDICTION`: Sovereign jurisdiction responsible for the official act.
- `OCCURRED_IN`: Geographic jurisdiction or region where the event occurred.
- `REPORTED_AT`: Location from which a news dispatch originated.
- `REFERENCES_COMMODITY`: Standardized commodity referenced in agreement.
- `REFERENCES_SECTOR`: Sector explicitly cited in policy or legislation.
- `REFERENCES_INDUSTRY`: Granular industry classification cited.
- `REFERENCES_FACILITY`: Specific corporate facility or site referenced.
- `REFERENCES_INFRASTRUCTURE_ASSET`: Specific physical asset referenced.
- `GEOGRAPHICALLY_NEAR`: Spatially proximate asset within verified radius; strictly asserts distance (km), never physical damage.
- `SOURCE_REPORTED_ASSOCIATION`: Journalistic association; classified as Candidate.

### Event-to-Event Predicates
- `REVISES`, `SUPERSEDES`, `CORRECTS`, `RETRACTS`, `FORMAL_FOLLOW_UP_TO`, `IMPLEMENTS`, `OFFICIALLY_RESPONDS_TO`.

### Foundational Structural Predicates (Multi-Hop)
- `SUBSIDIARY_OF`, `PARENT_OF`, `ISSUED_BY_COMPANY`, `OPERATED_BY`, `LOCATED_IN`, `PRIMARY_EXCHANGE_IN`, `COMPRISING_SECTOR`.

---

## Specialized Event Family Linkers

1. **`EarningsRelationshipLinker`**: Links earnings releases to reporting issuer and explicitly cited primary securities; prevents share class explosion.
2. **`CorporateActionRelationshipLinker`**: Accurately assigns Acquirer, Target, and Reviewing Regulators.
3. **`EconomicReleaseRelationshipLinker`**: Links releases to indicator series, statistical agencies, and issuing countries.
4. **`CentralBankRelationshipLinker`**: Connects monetary decisions to central banks, sovereign jurisdictions, and policy targets.
5. **`SanctionsRelationshipLinker`**: Matches exact legal entities; strictly avoids fuzzy collisions with innocent firms.
6. **`NaturalEventRelationshipLinker`**: Computes spatial haversine distances to registered infrastructure; strictly prohibits `DAMAGED` or `AFFECTS` predicates.
7. **`InfrastructureRelationshipLinker`**: Links infrastructure disruptions to physical assets and operators.
8. **`RegulatoryRelationshipLinker`**: Connects SEC/antitrust matters to regulators and targets.
9. **`GeopoliticalRelationshipLinker`**: Links treaties and trade actions to participating nations.
10. **`NewsReportedRelationshipLinker`**: Classifies rumors as candidate associations.

---

## 20 Institutional Test Fixtures (A through T)

| Fixture | Scenario | Verified Invariant |
| :--- | :--- | :--- |
| **A** | Earnings Issuer Linking | Links to Apple Inc.; primary stock; no warrants or OTC explosion. |
| **B** | Multiple Share Classes | Issuer event links to Alphabet Inc.; does not fabricate GOOG vs GOOGL edges. |
| **C** | Sanctions Exact Match | Designated Russian Volga entity linked; innocent UK firm excluded. |
| **D** | Central Bank Decision | Decided by Federal Reserve; issuing jurisdiction United States. |
| **E** | Economic Indicator Series | Links to US CPI indicator and Bureau of Labor Statistics. |
| **F** | Corporate Action Roles | Microsoft = Acquirer; Activision = Target; FTC = Regulator. |
| **G** | Subsidiary to Parent Multi-Hop | DeepMind announces Gemini -> Subsidiary of Alphabet (2 hops); Alphabet not falsely relabeled as announcer. |
| **H** | Earthquake Proximity | Sendai earthquake -> Onagawa NPP (~80 km) via `GEOGRAPHICALLY_NEAR`; zero damage claim. |
| **I** | Geographic Precision | Country-level German tax event does not fabricate facility proximity. |
| **J** | Commodity Mention | OPEC+ cuts reference Brent Crude; no spurious distributor edges. |
| **K** | Historical Ownership As-Of | As-of 2022 ARM links to SoftBank; query in 2024 reflects public status. |
| **L** | Knowledge Horizon As-Of | T1 query excludes T2 SEC amendment edge (Zero Look-Ahead). |
| **M** | Multi-Source Corroboration | 1 TSMC relationship edge grounded by 3 distinct evidence records. |
| **N** | Conflicted Rumor Review | Takeover rumor with conflicting bidders flagged as `CONFLICTED` in review queue. |
| **O** | Revoked Data Source | Revoked source invalidates and hides relationship edge. |
| **P** | Multi-Tenant Isolation | Tenant Alpha private edge completely invisible to Tenant Beta. |
| **Q** | Cycle Detection | Cross-holding cycle between Alpha Corp and Beta Corp terminates safely. |
| **R** | Event Retraction Bridge | Stage 135 event retraction revokes all dependent graph edges. |
| **S** | Reused Ticker Disambiguation | Ticker `META` resolves to Meta Financial in 2020 and Meta Platforms in 2023. |
| **T** | Factual Path Explanation | Colonial Pipeline outage -> Asset -> Operator with zero economic loss claims. |

---

## FastAPI REST Endpoints (`/api/v1/knowledge-graph`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/capabilities` | Returns graph capabilities, boundaries, and prohibited predicates. |
| `GET` | `/node-types` | Lists all 16 canonical graph node types. |
| `GET` | `/predicates` | Lists approved directed predicates and prohibited list. |
| `POST` | `/resolve-entity` | Resolves identifiers (LEI, CIK, Ticker, etc.) with temporal filtering. |
| `GET` | `/events/{id}/neighbors` | Direct 1-hop entities connected to an event. |
| `GET` | `/entities/{type}/{id}/events`| Direct 1-hop events connected to an entity. |
| `GET` | `/relationships/{id}` | Detailed relationship edge inspection. |
| `GET` | `/relationships/{id}/evidence` | Supporting evidence identifiers and derivation basis. |
| `GET` | `/relationships/{id}/history` | Non-destructive revision audit trail. |
| `POST` | `/relationships/{id}/revoke` | Revokes a relationship edge with reason. |
| `POST` | `/paths` | Discovers verified acyclic multi-hop paths (max depth 5). |
| `POST` | `/neighborhood` | Extracts k-hop neighborhood subgraphs. |
| `POST` | `/as-of` | Evaluates knowledge graph state point-in-time as-of timestamp. |
| `GET` | `/review-queue` | Returns uncorroborated candidate/conflicted relations. |

---

## Frontend Explorer UI (`/intelligence`)

- **Interactive Canvas (`GraphCanvas`)**: SVG/HTML5 canvas with circular layout, interactive pan/zoom, directed edge arrows, node category colors, and selection halos.
- **Accessible Table View (`GraphTableView`)**: Accessible tabular alternative with search filter, sortable columns, and verification badges.
- **Deep Edge Inspector (`GraphRelationshipInspector`)**: Evidence links, assertion origin, bitemporal validities, spatial proximity metrics, and revocation prompt.
- **Path Inspector (`GraphPathInspector`)**: Hop-by-hop breakdown with numbered steps, verified predicates, and factual explanations with zero loss claims.
- **Point-in-Time Time-Travel (`GraphHistoricalControls`)**: Allows analysts to dial any UTC timestamp and evaluate graph state with zero look-ahead bias.
