# ATLAS 3D GOD'S EYE GLOBE — POSTGIS + CESIUMJS FOUNDATION (STAGE 130)

## 1. Executive Summary & Canonical Roadmap Position
**ATLAS Stage 130 of 150: 3D God's Eye View** builds an institutional-grade, interactive 3D Earth geospatial foundation powered by **CesiumJS**, seamlessly interoperable with the Stage 129 **MapLibre GL JS** 2D mapping engine and **PostgreSQL + PostGIS** spatial database.

The 3D God's Eye Globe provides institutional investors, macro analysts, and risk officers with a genuine physical-world perspective of the planet, enabling global navigation, high-resolution imagery inspection, topographic elevation sampling, 3D building volume visualization, and cross-module workspace intelligence.

```
                                  ATLAS MAPS
                                       │
                              MODE CONTROLLER
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
                   2D MODE                           3D MODE
                (MapLibre GL JS)                   (CesiumJS)
                      │                                 │
                      └────────────────┬────────────────┘
                                       ▼
                            SHARED GEOSPATIAL DOMAIN
                      ┌────────────────┼────────────────┐
                      ▼                ▼                ▼
                   CAMERAS          LAYERS           FEATURES
                      │                │                │
                      └────────────────┼────────────────┘
                                       ▼
                             POSTGIS / SPATIAL API
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
               DATASET REGISTRY                 SOURCE PROVENANCE
                      │                                 │
                      └────────────────┬────────────────┘
                                       ▼
                       MULTI-TENANT AUTHORIZATION & RLS
                                       ▼
                    SAVED / WORKSPACES / GLOBAL LINKING
```

---

## 2. Strict Scope Boundaries (Stages 131–134)
To ensure architecture integrity and avoid premature feature creep:
- **Stage 130 Owns**: CesiumJS WebGL globe engine, WGS84 ellipsoid coordinates, ECEF Cartesian3 conversions, 2D/3D camera interoperability, approved imagery catalog with legal attribution, terrain provider abstraction with honest ellipsoid fallback, OGC 3D Tileset registry with multi-tenant access control, globe picking, Feature Inspector, Saved Globe Views, and independent Workspace Globe panels.
- **Stage 131 (Deferred)**: deck.gl GPU-accelerated spatial analytics, H3 hexagonal indexing, millions of points aggregation, dynamic density heatmaps, and spatial joins.
- **Stage 132 (Deferred)**: Company headquarters, corporate supply-chain facilities, warehouses, and ownership network geometries.
- **Stage 133 (Deferred)**: Physical infrastructure layers (airports, maritime ports, energy pipelines, power grids, data centers, rail networks).
- **Stage 134 (Deferred)**: Real-time physical-world tracking (live aircraft, AIS vessel telemetry, live satellite tracking, real-time weather streams).

---

## 3. CesiumJS Runtime Architecture & Asset Hosting
- **Package**: `cesium@1.146.0` installed in `apps/web`.
- **Runtime Asset Pipeline**: Cesium requires external Web Workers and static assets (`Workers/`, `ThirdParty/`, `Assets/`, `Widgets/`). The build script `scripts/copy-cesium.mjs` automatically copies these assets from `node_modules/cesium/Build/Cesium` into `apps/web/public/cesium/` before development and production compilation.
- **Runtime Base URL**: Configured via `window.CESIUM_BASE_URL = '/cesium'` prior to Cesium module initialization, ensuring Web Workers resolve correctly across development and production environments.
- **Theme Preservation**: Cesium widget styles are imported into the isolated map canvas without polluting the global ATLAS design system.
- **Context Lifecycle**: A single active `Cesium.Viewer` is maintained per panel. The viewer is attached to a `ResizeObserver` calling `viewer.resize()`, and cleanly destroyed via `viewer.destroy()` upon unmount to prevent GPU resource leaks.

---

## 4. WGS84 Geodetic & Earth-Centered Cartesian (ECEF) Mathematics
- **Reference Ellipsoid**: Standard WGS84 ellipsoid ($a = 6,378,137.0\text{ m}$, $f = 1/298.257223563$, $b \approx 6,356,752.314245\text{ m}$).
- **Forward Transformation (Geodetic $\to$ ECEF Cartesian)**:
  $$\lambda = \text{radians}(lon), \quad \phi = \text{radians}(lat)$$
  $$N(\phi) = \frac{a}{\sqrt{1 - e^2 \sin^2(\phi)}}$$
  $$X = (N(\phi) + h) \cos(\phi) \cos(\lambda)$$
  $$Y = (N(\phi) + h) \cos(\phi) \sin(\lambda)$$
  $$Z = (N(\phi)(1 - e^2) + h) \sin(\phi)$$
- **Inverse Transformation (ECEF Cartesian $\to$ Geodetic)**:
  Uses **Bowring's closed-form algorithm** with iterative refinement, guaranteeing sub-millimeter precision across all latitudes and polar regions.
- **Zero Silent Unit Conversion Errors**: Explicit `degreesToRadians` and `radiansToDegrees` functions eliminate angular calculation bugs.

---

## 5. 2D/3D Camera Interoperability Engine
The platform allows seamless switching between 2D MapLibre and 3D Cesium without losing the user's geographic area of interest:
- **2D MapLibre $\to$ 3D Cesium**:
  Derives camera altitude above the ellipsoid:
  $$h = \frac{40,075,016.686 \times \cos(\text{radians}(lat))}{2^{zoom}}$$
  Converts MapLibre bearing $[0, 360^\circ)$ to Cesium heading radians $[0, 2\pi)$. Converts MapLibre pitch $[0, 60^\circ]$ to Cesium pitch $[-\pi/2, 0]$ (where $-\pi/2$ is nadir looking straight down).
- **3D Cesium $\to$ 2D MapLibre**:
  Inverts the Mercator altitude equation:
  $$zoom = \log_2\left(\frac{40,075,016.686 \times \cos(\text{radians}(lat))}{\max(h, 100)}\right)$$
  Clamps latitude to Web Mercator bounds ($[-85.051129^\circ, +85.051129^\circ]$) to prevent projection singularities at the poles. Normalizes antimeridian longitude crossings ($[-180^\circ, +180^\circ]$).

---

## 6. Imagery & Terrain Provider Registries
### Approved Imagery Catalog
1. **Natural Earth II Global Reference** (`natural-earth`): Global shaded relief and bathymetry (Public Domain). Default baseline.
2. **CARTO Dark Matter 3D** (`carto-dark`): Dark high-contrast cartography optimized for institutional financial visualization (`© OpenStreetMap contributors, © CARTO`).
3. **CARTO Positron 3D** (`carto-light`): Low-saturation light cartography (`© OpenStreetMap contributors, © CARTO`).
4. **OpenStreetMap 3D** (`osm-standard`): Crowdsourced global street and boundary layer (`© OpenStreetMap contributors`).
5. **Sentinel-2 Cloudless** (`satellite-reference`): Real global optical satellite mosaic from European Space Agency Copernicus Sentinel-2 (`© Copernicus Sentinel data, © EOX IT Services GmbH`).
6. **Enterprise High-Resolution Orthoimagery** (`restricted-premium-satellite`): Restricted commercial aerial imagery requiring active tenant license entitlements.

### Terrain Provider Architecture
- **WGS84 Ellipsoid** (`ellipsoid`): Default mathematical ellipsoid with zero elevation distortion and guaranteed instant availability without external network dependencies.
- **Cesium World Terrain** (`cesium-world-terrain`): High-resolution global quantized-mesh terrain elevation. Active when `CESIUM_ION_TOKEN` is configured; otherwise honestly reported as unavailable.
- **Honest Elevation Semantics**: The system distinguishes mathematical ellipsoid surface ($h = 0.0\text{ m}$) from topographic elevation. The platform never fabricates terrain elevations.

---

## 7. OGC 3D Tileset Foundation & Multi-Tenant Security
- **Format**: Supports OGC 3D Tiles 1.0 and 1.1 hierarchical bounding volume hierarchies (`region`, `box`, `sphere`).
- **Catalog Sources**:
  - `atlas.reference.financial_district_3dtiles`: Public reference 3D mesh of the City of London financial core (`© UK Geospatial Commission`).
  - `atlas.tenant_alpha.confidential_vault_3dtiles`: Private tenant spatial asset (`tenant-alpha`).
- **Multi-Tenant Access Boundary**: Requesting a private 3D Tileset from an unauthorized tenant returns HTTP 403 Forbidden (`GlobeTilesetAccessDeniedError`). Zero metadata or geometry leaks across tenant boundaries.

---

## 8. Saved Globe Views & Multi-Panel Workspaces
- **Universal Saved Integration (Stage 119)**: Extends `UserMapView` with `renderer_mode = "3D"`, `cesium_camera`, `imagery_provider_id`, `terrain_provider_id`, and `visible_layer_references`.
- **Optimistic Concurrency**: Update operations verify the `expected_revision` number against the stored revision, preventing concurrent overwrite conflicts (`GlobeViewRevisionConflictError`).
- **Stage 120 Multi-Panel Workspaces**: The Map Panel adapter (`MapPanelAdapter.tsx`) supports independent 2D and 3D states. Multiple Globe panels maintain completely independent camera positions, viewports, and imagery sources without crosstalk (**Fixture I**).

---

## 9. Verification & Reference Fixture Matrix

| Fixture | Capability | Verification Result |
| :--- | :--- | :--- |
| **Fixture A** | Bare Globe & Ellipsoid Fallback | **PASSED**: Ellipsoid default; zero fake elevation. |
| **Fixture B** | Imagery Provider & Attribution | **PASSED**: Approved sources load with visible attribution; unentitled commercial imagery blocked. |
| **Fixture C** | Terrain Architecture & Outage Recovery | **PASSED**: Fallback to ellipsoid if terrain is unconfigured or timed out. |
| **Fixture D** | 2D/3D Camera Interoperability | **PASSED**: Round-trip center $\Delta < 0.001^\circ$, zoom $\Delta < 0.5$; pole/antimeridian edge cases clamped. |
| **Fixture E** | WGS84 ECEF Coordinate Precision | **PASSED**: Geodetic $\leftrightarrow$ Cartesian round-trip error $< 0.005\text{ m}$. |
| **Fixture F** | Authorized 3D Tileset Loading | **PASSED**: Public London 3D Tileset loaded with bounding volume and attribution. |
| **Fixture G** | Multi-Tenant 3D Tileset Isolation | **PASSED**: Cross-tenant request rejected with 403 Forbidden; zero leakage. |
| **Fixture H** | Saved Globe View & Revision Locking | **PASSED**: Saved view restored with exact camera fidelity; stale revision raises 409 Conflict. |
| **Fixture I** | Independent Workspace Panels | **PASSED**: Panel A (London) and Panel B (Tokyo) maintain independent cameras without crosstalk. |
| **Fixture J** | Error Taxonomy & Recovery | **PASSED**: Typed domain exceptions mapped to HTTP status codes (400, 403, 404, 409). |
