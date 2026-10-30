# ATLAS Maps V1: PostGIS + MapLibre 2D Geospatial Intelligence Foundation

## Executive Summary
Stage 129 establishes the institutional 2D geospatial intelligence foundation of the ATLAS financial operating system. Powered by MapLibre GL JS on the frontend and spatially-enabled PostgreSQL / PostGIS on the backend, ATLAS Maps delivers interactive global exploration, coordinate-accurate boundary rendering, financial capitals and monetary authority intelligence, MVT vector tile delivery, metric proximity analysis, and seamless integration with Universal Saved (Stage 119) and Workspaces (Stage 120).

---

## 1. Roadmap Position & Explicit Scope Boundaries

| Stage | Responsibility | Status |
|---|---|---|
| 124 | AI Assistant V1 | Completed |
| 125 | AI Context Awareness Engine | Completed |
| 126 | Secure AI Tool Gateway | Completed |
| 127 | AI Research & Grounded RAG | Completed |
| 128 | AI Financial Action Engine | Completed |
| **129** | **2D Maps Foundation (PostGIS + MapLibre)** | **Delivered (Stage 129)** |
| 130 | 3D God's Eye Globe (CesiumJS) | Deferred to Stage 130 |
| 131 | Large-Scale Visualization (deck.gl & H3) | Deferred to Stage 131 |
| 132 | Company Facilities & Financial Entities | Deferred to Stage 132 |
| 133 | Physical Infrastructure Layers | Deferred to Stage 133 |
| 134 | Live Physical-World Data Layers | Deferred to Stage 134 |

### Scope Governance & Strict Prohibitions
- **No 3D Globe**: CesiumJS globe, 3D terrain, orbital cameras, and 3D Tiles are strictly reserved for Stage 130.
- **No Large-Scale GPU Aggregations**: deck.gl hexagonal grids and H3 analytical indexing are strictly reserved for Stage 131.
- **No Fabricated Company Facilities**: Corporate headquarters, factories, distribution hubs, and ownership mappings are reserved for Stage 132 with verified corporate data sources.
- **No Fabricated Physical Infrastructure**: Pipelines, electrical grids, ports, airports, and mines are reserved for Stage 133.
- **No Simulated Live Tracking**: Live flights, vessels, weather feeds, and satellite orbits are reserved for Stage 134.
- **Zero Hallucinated Geography**: Never fabricate coordinates, sovereign borders, or financial locations. All reference data derives from verified geographic standards (Natural Earth, ISO 3166-1, central bank registries).
- **Public Tile Service Respect**: Public community OSM servers are not treated as unrestricted production CDNs. Licensed Carto, OpenFreeMap, and Esri reference services are configured with legally compliant visible attribution.

---

## 2. Geospatial Architecture & Mathematics

```
┌─────────────────────────────────────────────────────────────┐
│                    ATLAS MAPS V1 ENGINE                     │
├─────────────────────────────────────────────────────────────┤
│ FRONTEND (Next.js / React 19 / TypeScript)                  │
│  - MapLibre GL JS 2D WebGL Rendering Surface                │
│  - Reactive Camera Synchronization & ResizeObserver         │
│  - Layer Visibility & Opacity Management                    │
│  - Geographic Search & Coordinate Disambiguation            │
│  - Feature Inspector with Provenance & Quality Badges       │
│  - Saved View Management & Workspace Map Panel Adapter      │
├─────────────────────────────────────────────────────────────┤
│ BACKEND (FastAPI / Python Modular Monolith)                 │
│  - Spatial Query Engine (Bounding-Box & Antimeridian Split) │
│  - Metric Proximity Queries (Haversine Law of Cosines)      │
│  - Binary MVT Vector Tile Generator (Proto 2.1 Wire Spec)   │
│  - Geographic Search & Coordinate Resolver                  │
│  - Multi-Tenant Tile & Dataset Authorization                │
│  - Persistent Map Views Repository with Revision Locks      │
├─────────────────────────────────────────────────────────────┤
│ SPATIAL DATABASE (PostgreSQL + PostGIS)                     │
│  - Canonical Geographic Storage: WGS84 / EPSG:4326          │
│  - Planar Tile Coordinate System: Web Mercator / EPSG:3857  │
│  - Exact Mathematical Forward & Inverse Projections         │
│  - Tables: geo_datasets, geo_features, map_layers,          │
│            user_map_views, map_audit_events                 │
└─────────────────────────────────────────────────────────────┘
```

### Coordinate Reference Systems & Projections
1. **Canonical Geographic Storage: WGS84 / EPSG:4326**
   - Coordinates strictly ordered as `[longitude, latitude]` in degrees.
   - Longitude: $[-180.0, 180.0]$
   - Latitude: $[-90.0, 90.0]$
   - Silent coordinate swapping is detected and rejected with `MapCoordinatesInvalidError`.

2. **Map Tile Projection: Web Mercator / EPSG:3857**
   - Planar coordinates $(x, y)$ in meters over equatorial circumference:
     $$x = \text{lon} \times \frac{\pi}{180} \times 6,378,137.0$$
     $$y = \ln\left(\tan\left(\frac{\pi}{4} + \frac{\text{lat} \times \pi}{360}\right)\right) \times 6,378,137.0$$
   - Web Mercator latitudes are bounded to $[-85.05112878^\circ, +85.05112878^\circ]$ to prevent polar infinity singularities.

3. **Critical Unit Rule: Degrees are NOT Meters**
   - $0.1^\circ$ longitude varies from $11.132\text{ km}$ at the equator to $0\text{ km}$ at the poles.
   - All spatial proximity calculations use great-circle metric geodesics over earth mean radius $R = 6,371,000\text{ m}$:
     $$a = \sin^2\left(\frac{\Delta\text{lat}}{2}\right) + \cos(\text{lat}_1)\cos(\text{lat}_2)\sin^2\left(\frac{\Delta\text{lon}}{2}\right)$$
     $$d = 2R \arctan2(\sqrt{a}, \sqrt{1 - a})$$
   - Proximity endpoints explicitly return `distance_meters` and `distance_km`.

4. **Antimeridian Crossing Normalization**
   - When a viewport crosses the $180^\circ$ meridian ($\text{west} > \text{east}$), the query engine splits the bounding envelope into two disjoint queries:
     $$B_1 = [\text{west}, \text{south}, 180.0, \text{north}], \quad B_2 = [-180.0, \text{south}, \text{east}, \text{north}]$$
   - Prevents naive database queries from sweeping the entire globe backwards.

5. **Strict Geometry Validation**
   - Polygon rings must have $\ge 4$ coordinates, be closed ($\text{first} == \text{last}$), and contain no self-intersecting non-adjacent edges.
   - Bowtie or complex self-intersecting geometries are rejected with `MapDatasetGeometryInvalidError`.

---

## 3. Vector Tile Pipeline (MVT 2.1)

To deliver high-performance visual layers without pushing multi-megabyte GeoJSON blobs to clients, ATLAS Maps implements a native binary Mapbox Vector Tile (MVT) encoder compliant with Google Protocol Buffers wire format.
- **Tile Coordinates**: Validated $z \in [0, 22]$, $x \in [0, 2^z - 1]$, $y \in [0, 2^z - 1]$.
- **Tile Envelope**: Computed in Web Mercator meters matches PostGIS `ST_TileEnvelope(z, x, y)`.
- **Local Tile Extent**: 4096 units.
- **Command Encoding**: CommandInteger (`MoveTo`=1, `LineTo`=2, `ClosePath`=7) and ParameterInteger (ZigZag delta encoding).
- **Multi-Tenant Cache Isolation**: Public tiles are cached under `map_tile:pub:{layer}:r{rev}:{z}:{x}:{y}` while private tenant tiles are hashed under `map_tile:priv:{layer}:r{rev}:{hash(tenant,user)}:{z}:{x}:{y}`. Private features are never leaked into shared caches.

---

## 4. Basemap Providers & Licensing

| Style ID | Display Name | Provider | Legal Attribution |
|---|---|---|---|
| `atlas-dark` | ATLAS Institutional Dark | CARTO Dark Matter | © OpenStreetMap contributors, © CARTO, © OpenFreeMap |
| `atlas-light` | ATLAS High-Contrast Light | CARTO Positron | © OpenStreetMap contributors, © CARTO, © OpenFreeMap |
| `atlas-minimal` | ATLAS Minimalist Geopolitical | OpenFreeMap Bright | © OpenStreetMap contributors, © CARTO, © OpenFreeMap |
| `atlas-satellite` | ATLAS Reference Imagery | Esri World Imagery | Source: Esri, Maxar, Earthstar Geographics, and GIS User Community |

---

## 5. Reference Test Fixtures Summary

All 10 Golden Reference Fixtures pass:
- **Fixture A (Valid Point)**: Valid coordinates (New York City $[-74.0060, 40.7128]$), WGS84 SRID, GeoJSON feature generation, and feature selection.
- **Fixture B (Valid Polygon)**: Closed boundary ring, bounding box calculation, point-in-polygon containment test.
- **Fixture C (Invalid Geometry)**: Self-intersecting bowtie polygon rejected with `MapDatasetGeometryInvalidError` without silent corruption.
- **Fixture D (Antimeridian)**: Bounding box spanning $170^\circ$ to $-170^\circ$ split into normalized eastern/western boxes without global sweep.
- **Fixture E (Geodesic Distance)**: London to Paris great-circle distance verified at $343.5\text{ km}$, confirming degree/meter separation.
- **Fixture F (Unauthorized Data)**: Tenant A private dataset strictly isolated; Tenant B queries and tile requests return 403 Forbidden with zero data leakage.
- **Fixture G (Style Change)**: Basemap switching from Dark to Light preserves camera center, zoom, active layers, and selected feature.
- **Fixture H (Saved View)**: Saving camera, style, layers, opacity, and feature selection round-trips with exact authorized restoration.
- **Fixture I (Independent Workspaces)**: Workspace Panel A (New York) and Panel B (Tokyo) maintain strictly isolated cameras; panning Panel A does not alter Panel B.
- **Fixture J (Restricted Tiles)**: Restricted layer cache invalidated upon access revocation; subsequent unauthorized tile requests rejected.

---

## 6. Integration Points

1. **Stage 119 — Universal Saved Library**: Persists `MAP_VIEW_CONFIG` target types under module `maps`.
2. **Stage 120 — Workspaces**: Registered `MAP_VIEW` panel type handled by `MapPanelAdapter` with independent camera, style, and layer states.
3. **Stage 121 — Global Workspace Linking**: Subscribes and publishes `REGION` and `INSTRUMENT` dimensions across linked channels.
4. **Stage 125 — AI Context Awareness**: Exposes current viewport bounds, active layers, and selected geographic feature.

---

## 7. Stage 130 Handoff: 3D God's Eye Globe
Stage 130 will extend ATLAS Maps into 3D using CesiumJS. It will directly inherit:
- The PostGIS database schemas and geometry tables (`geo_datasets`, `geo_features`).
- The MVT vector tile infrastructure and caching system.
- The geographic search service and financial center coordinates.
- Saved map views and Workspace panel state models.
- Multi-tenant RLS policies and licensing governance.

