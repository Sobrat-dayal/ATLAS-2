# ATLAS Global Physical Infrastructure Intelligence System (Stage 133 of 150)

## Executive Summary
The **ATLAS Global Physical Infrastructure Intelligence System** provides an institutional-grade geospatial and relational intelligence foundation for global physical assets, conduits, and networks. Spanning 9 major physical sectors—**Ports & Maritime**, **Airports & Aviation**, **Power Generation**, **Electricity Networks**, **Oil & Gas Pipelines**, **Mining & Mineral Processing**, **Hyperscale Data Centers**, **Railways**, and **Industrial Logistics**—the system connects authoritative physical asset data with corporate ownership, verified network topology, typed capacity records, and spatial analytics.

---

## 1. Roadmap Position & Scope Boundaries

### 1.1 Canonical Sequence
- **Preceding Stages:**
  - **Stage 129:** PostGIS + MapLibre 2D Geospatial Foundation
  - **Stage 130:** 3D God's Eye View (CesiumJS)
  - **Stage 131:** Large-Scale Geospatial Analytics (deck.gl + H3)
  - **Stage 132:** Corporate Geography & Facility Mapping
- **Stage 133 (Current):** Global Physical Infrastructure Intelligence
- **Succeeding Stage (Stage 134):** Live Physical-World Data Integration (AIS vessel tracking, ADS-B flight feeds, satellite orbits, real-time weather)

### 1.2 Strict Scope Boundaries
- **Stage 133 Owns:**
  - Authoritative reference assets, terminals, plants, substations, mines, data centers, tracks, and pipelines.
  - Verified network topology (nodes, edges, connectivity evidence, bounded graph queries).
  - Typed dimensional capacity records (MW vs MWh, TEU/yr, bpd, MMcf/d).
  - Corporate linkages (owners, operators, equity share).
  - Spatial indexing, H3 cell aggregation, and regional summaries.
- **Stage 134 Reservation:**
  - Live moving AIS positions, ADS-B transponder telemetry, dynamic satellite ground tracks, live weather radars, and telemetry feeds are strictly reserved for Stage 134.
- **Safety & Defense Boundaries:**
  - Operational control systems (SCADA, PLC actuation) and critical infrastructure targeting features are strictly prohibited.

---

## 2. Sector Taxonomy & Supported Asset Types

| Sector | Key Asset Types | Identifiers | Canonical Capacity Metrics |
| :--- | :--- | :--- | :--- |
| **Ports & Maritime** | Port Terminals, Container Terminals, Bulk Terminals, Cruise Berths, Trade Locations | UN/LOCODE, Terminal Code | TEU/year, Tonnes/year, Berths, Max Draft (m) |
| **Airports & Aviation** | Commercial Airports, Airfields, Cargo Hubs, Runways | ICAO (4-letter), IATA (3-letter) | Passengers/year, Air Cargo Tonnes/yr, Runways |
| **Power Generation** | Thermal, Nuclear, Hydro, Solar PV, Wind, Battery Storage | EIA Plant ID, GEM ID | Nameplate MW, Net Summer MW, MWh Storage |
| **Electricity Networks** | Transmission Lines, Substations, Interconnections | Grid Operator ID | Voltage (kV), MVA Capacity, Circuit Count |
| **Oil & Gas Pipelines** | Crude/Products Pipelines, Natural Gas Lines, Compressor Stations, Refineries | GEM Pipeline ID, PHMSA ID | Throughput (bpd), Throughput (MMcf/d), Storage (bbl) |
| **Mining & Resources** | Open Pit, Underground, Concentrators, Smelters, Tailings | USGS MRDS, S&P Global ID | Run-of-Mine (t/yr), Refined Output (t/yr), Reserves (t) |
| **Data Centers** | Hyperscale Campuses, Colocation Facilities, Cloud Hubs | DatacenterMap ID | IT Equipment Load (MW), Total Facility Power (MW), Gross sqft |
| **Railways** | Intermodal Yards, Marshalling Yards, Mainlines, Stations | ORM Track ID | Gauge (mm), Electrification (bool), Freight (t/yr) |
| **Logistics** | Distribution Centers, Bonded Warehouses, Air Cargo Hubs | Logistics Park Code | Gross Area (sqft), Storage Volume (m³) |

---

## 3. Unit Dimensional Integrity & Capacity Rules

### 3.1 Rate of Transfer (Power) vs Stored Work (Energy)
- **Power (MW, GW, kW):** Measures instantaneous rate of energy flow.
- **Energy (MWh, GWh, kWh):** Measures stored work or volume over time.
- **Dimensional Rule:** Power and Energy records belong to disjoint physical dimensions. Mathematical addition across dimensions (e.g. 100 MW + 400 MWh = 500 MW) is prohibited and raises `IncompatibleCapacityUnitError` (Fixture B).

### 3.2 Reporting Basis Preservation
- Reported capacity values are strictly qualified by basis:
  - `NAMEPLATE`: Manufacturer design rating.
  - `NET_SUMMER` / `NET_WINTER`: Seasonal derated net output delivered to grid.
  - `GROSS`: Total generated power before parasitic station load.
  - `DESIGN`: Engineering throughput capacity.
  - `OPERATIONAL_PEAK`: Maximum recorded historical throughput.
- Discrepancies between Nameplate and Net capacity are flagged in side-by-side asset comparisons (Fixture F).

### 3.3 Unknown Capacity Handling
- When official throughput records are unavailable (e.g. general aviation airfield without commercial traffic stats), the value renders as `Not available` (`null`). Fabricating placeholder throughput is prohibited (Fixture K).

---

## 4. Verified Network Topology & Crossing Invariants

### 4.1 Graph Data Model
- **Network Nodes:** Distinct geographic points with coordinates `(lat, lng)`, type (`substation`, `junction`, `compressor_station`, `terminal`), and optional asset link.
- **Network Edges:** Directed or bidirectional physical conduits with LineString coordinates, length in km, voltage rating, or diameter.

### 4.2 Geometric Crossing Separation (Fixtures C & D)
- **Physical Invariant:** Two pipelines crossing in geographic coordinates, or a rail line crossing another on an overpass bridge, remain **topologically disconnected** unless an explicit junction switch or interconnecting node exists in authoritative source records.
- Crossing lines without verified junction nodes cannot be traversed as connected routes.

### 4.3 Bounded Graph Traversal
- Graph traversals (subgraph reachability and shortest path) enforce a maximum depth limit (`max_depth <= 5`). Exceeding the authorized depth bound raises `TraversalDepthExceededError`. Cycle prevention is enforced via visited sets.

---

## 5. Summary of All 14 Canonical Reference Fixtures

| Fixture | Scenario | Expected Behavior | Verification Status |
| :--- | :--- | :--- | :--- |
| **Fixture A** | Plant P (300 MW) with G1 (100 MW) and G2 (200 MW) | Deduplicated rollup: Plant total is 300 MW; Plant count = 1, Unit count = 2. No double counting to 600 MW. | Passed |
| **Fixture B** | Battery Storage (100 MW power, 400 MWh storage) | Stored and displayed separately; addition raises `IncompatibleCapacityUnitError`. | Passed |
| **Fixture C** | Crossing pipeline routes without junction | Authoritative topology leaves lines disconnected; path traversal returns None. | Passed |
| **Fixture D** | Rail bridge overpass crossing another track | No junction node; grade-separated crossing does not form an edge. | Passed |
| **Fixture E** | UN/LOCODE vs Specific Terminal | UN/LOCODE `USLAX` tracked as broad trade location; Pier 400 tracked as distinct terminal. | Passed |
| **Fixture F** | Plant A (Nameplate 500 MW) vs Plant B (Net 450 MW) | Bases preserved; comparison alerts user to differing reporting bases. | Passed |
| **Fixture G** | Owner (Company A) vs Operator (Company B) | Distinct roles displayed; no false ownership claim attributed to Company B. | Passed |
| **Fixture H** | Approximate pipeline route | Precision set to `ROUTE_CORRIDOR`, `is_approximate_route = true`. | Passed |
| **Fixture I** | 1 power plant with 3 generating units in same cell | H3 aggregation reports `facility_count = 1` and `unit_count = 3` without inflation. | Passed |
| **Fixture J** | Construction in 2023, Operational in 2025 | Historical query returns verified point-in-time status for each date; future dates rejected. | Passed |
| **Fixture K** | Airport without throughput measurement | Displays `Throughput: Not available` (`null`), never fabricated numbers. | Passed |
| **Fixture L** | Private network and asset | Unauthorized tenant requests receive 403 / `SensitiveAssetAccessDeniedError`. | Passed |
| **Fixture M** | Non-commercial dataset license | Publication in commercial mode prohibited (`CommercialUseProhibitedError`). | Passed |
| **Fixture N** | Revoked source entitlement | Revoking entitlement immediately suppresses asset lookup and derived H3 aggregates. | Passed |

---

## 6. REST API Endpoints Reference

All endpoints are mounted under `/api/v1/maps/infrastructure`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/categories` | Supported physical infrastructure sectors and taxonomy. |
| `GET` | `/datasets` | Registered infrastructure datasets with licensing terms. |
| `GET` | `/assets` | Search assets with multi-parameter filtering (sector, country, company, capacity, status, as-of date). |
| `GET` | `/assets/{id}` | Detailed asset record with capacity records, coordinates, and corporate links. |
| `GET` | `/assets/{id}/history` | Historical status transition timeline. |
| `GET` | `/assets/{id}/sources` | Source citations, licensing class, and precision metadata. |
| `GET` | `/assets/{id}/relationships` | Verified corporate linkages (owners, operators, equity shares). |
| `POST` | `/assets/spatial-query` | Bounded spatial bounding box search. |
| `POST` | `/assets/compare` | Side-by-side asset comparison with basis discrepancy analysis. |
| `GET` | `/networks` | List networks accessible to actor. |
| `GET` | `/networks/{id}` | Retrieve network topology, nodes, and conduits. |
| `POST` | `/networks/{id}/query` | Bounded graph reachability traversal from origin node. |
| `POST` | `/networks/{id}/connections` | Shortest verified path between origin and target nodes. |
| `POST` | `/aggregates` | H3 hexagonal cell aggregation with distinct facility counting. |
| `GET` | `/companies/{id}/assets` | Corporate infrastructure exposure across sectors and roles. |
| `POST` | `/regional-summary` | Aggregated regional infrastructure breakdown. |

---

## 7. Frontend Interface & Map Integration

### 7.1 Map Controls
- **Toolbar Toggle:** Dedicated **Infrastructure** button in `AtlasMapToolbar` toggles Infrastructure Intelligence mode.
- **Sector Panel (`InfrastructureSectorPanel`):** High-contrast color-coded toggle chips for all 9 sectors with live asset counts.
- **Filter Bar (`InfrastructureFilters`):** Search, ISO country filter, operational status selector, and point-in-time date picker.
- **Legend (`InfrastructureNetworkLegend`):** Displays visual symbols, transmission voltages, pipeline conduits, and corridor indicators.

### 7.2 Interactive Drawers & Modals
- **Asset Inspector (`InfrastructureAssetInspector`):** Detailed slide-out drawer displaying verified capacity records, entity links, precision badges, and status history.
- **Network Explorer (`InfrastructureNetworkInspector`):** Graph query interface for bounded path finding and reachability exploration.
- **Regional Summary (`InfrastructureRegionalSummary`):** Modal displaying distinct facility vs unit counts and sector distributions.
- **Asset Comparison (`InfrastructureAssetComparison`):** Multi-column comparison card highlighting capacity reporting basis differences.
