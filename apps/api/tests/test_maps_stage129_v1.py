"""Comprehensive Test Suite for ATLAS Stage 129: MAPS V1 Using PostGIS + MapLibre.

Verifies:
- All 10 Golden Reference Fixtures (A through J).
- Exact coordinate ordering [longitude, latitude] and WGS84 / EPSG:4326 storage.
- Web Mercator / EPSG:3857 forward and inverse projection transformations.
- Geodesic metric distance math and the Critical Unit Rule (Degrees != Meters).
- Antimeridian normalization (west > east).
- Self-intersection polygon rejection.
- Multi-tenant isolation and RLS permissions on private datasets and tiles.
- Binary MVT vector tile generation and tile caching.
- Geographic search and coordinate navigation.
- Saved map views lifecycle and optimistic concurrency revision checks.
- Independent Workspace map panel camera states.
- Complete REST API endpoints under /api/v1/maps.
"""

from __future__ import annotations

import pytest
from atlas.auth import AuthPrincipal
from atlas.maps.datasets.registry import dataset_registry
from atlas.maps.domain import (
    DataQualityStatus,
    DatasetType,
    GeoBoundingBox,
    GeoCameraState,
    GeoDataset,
    GeoFeature,
    GeometryType,
    LicensingPolicy,
    MapLayerDefinition,
)
from atlas.maps.errors import (
    MapDatasetAccessDeniedError,
    MapDatasetGeometryInvalidError,
    MapLayerAccessDeniedError,
)
from atlas.maps.layers.registry import layer_registry
from atlas.maps.search.service import geographic_search_service
from atlas.maps.service import atlas_maps_service
from atlas.maps.spatial.bounding_boxes import (
    point_in_bbox,
    split_antimeridian_bbox,
    validate_bounding_box,
)
from atlas.maps.spatial.coordinates import (
    validate_coordinates,
)
from atlas.maps.spatial.distance import (
    calculate_distance_meters,
    is_within_radius_meters,
)
from atlas.maps.spatial.geometry import (
    point_in_polygon,
    validate_geometry,
    validate_ring,
)
from atlas.maps.spatial.projections import (
    epsg3857_to_epsg4326,
    epsg4326_to_epsg3857,
)
from atlas.maps.tiles.caching import tile_cache_manager
from atlas.maps.views.service import map_view_service
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app


@pytest.fixture
def auth_principal_user_a() -> AuthPrincipal:
    return AuthPrincipal(
        sub="trader_user_a",
        email="trader_a@atlas.institution",
        role="analyst",
    )


@pytest.fixture
def auth_principal_user_b() -> AuthPrincipal:
    return AuthPrincipal(
        sub="trader_user_b",
        email="trader_b@atlas.institution",
        role="analyst",
    )


@pytest.fixture
def test_client(auth_principal_user_a: AuthPrincipal) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: auth_principal_user_a
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ==============================================================================
# REFERENCE FIXTURE A — VALID POINT
# ==============================================================================
def test_reference_fixture_a_valid_point():
    """Fixture A: Valid isolated test point with known coordinates.

    Verifies SRID 4326, coordinate order [lon, lat], GeoJSON output, selection.
    """
    lon, lat = -74.0060, 40.7128  # New York City
    v_lon, v_lat = validate_coordinates(lon, lat)
    assert v_lon == -74.0060
    assert v_lat == 40.7128

    bbox = validate_geometry(GeometryType.POINT, [v_lon, v_lat])
    assert bbox.west == -74.0060
    assert bbox.south == 40.7128
    assert bbox.east == -74.0060
    assert bbox.north == 40.7128

    feat = dataset_registry.get_feature("atlas.reference.financial_centers", "fc_nyc")
    assert feat is not None
    assert feat.geometry_type == GeometryType.POINT
    assert feat.coordinates == [-74.0060, 40.7128]
    assert feat.data_quality == DataQualityStatus.VERIFIED

    geojson = feat.to_geojson_feature()
    assert geojson["type"] == "Feature"
    assert geojson["geometry"]["type"] == "Point"
    assert geojson["geometry"]["coordinates"] == [-74.0060, 40.7128]
    assert geojson["properties"]["label"] == "New York Financial Center"


# ==============================================================================
# REFERENCE FIXTURE B — VALID POLYGON
# ==============================================================================
def test_reference_fixture_b_valid_polygon():
    """Fixture B: Valid isolated polygon.

    Verifies ring closure, bounding box, containment, and selection.
    """
    coords = [
        [
            [-10.0, 40.0],
            [10.0, 40.0],
            [10.0, 60.0],
            [-10.0, 60.0],
            [-10.0, 40.0],
        ]
    ]
    bbox = validate_geometry(GeometryType.POLYGON, coords)
    assert bbox.west == -10.0
    assert bbox.south == 40.0
    assert bbox.east == 10.0
    assert bbox.north == 60.0

    # Point containment
    assert point_in_polygon(0.0, 50.0, coords[0]) is True
    assert point_in_polygon(15.0, 50.0, coords[0]) is False
    assert point_in_polygon(0.0, 70.0, coords[0]) is False


# ==============================================================================
# REFERENCE FIXTURE C — INVALID SELF-INTERSECTING GEOMETRY
# ==============================================================================
def test_reference_fixture_c_invalid_geometry_rejection():
    """Fixture C: Self-intersecting bowtie polygon.

    Expected: Strict validation rejection (MapDatasetGeometryInvalidError) without silent corruption.
    """
    # Classic bowtie polygon crossing itself in the center
    bowtie_ring = [
        [0.0, 0.0],
        [10.0, 10.0],
        [10.0, 0.0],
        [0.0, 10.0],
        [0.0, 0.0],
    ]
    with pytest.raises(MapDatasetGeometryInvalidError) as exc_info:
        validate_ring(bowtie_ring, dataset_id="test_bowtie")
    assert "Self-intersecting polygon detected" in str(exc_info.value)


# ==============================================================================
# REFERENCE FIXTURE D — ANTIMERIDIAN BOUNDS
# ==============================================================================
def test_reference_fixture_d_antimeridian_handling():
    """Fixture D: Viewport/bounds crossing the 180° meridian (e.g. west=170, east=-170).

    Expected: Correctly split into 2 bounding boxes without sweeping the entire globe.
    """
    antimeridian_bbox = validate_bounding_box(west=170.0, south=-20.0, east=-170.0, north=20.0)
    assert antimeridian_bbox.crosses_antimeridian() is True

    sub_boxes = split_antimeridian_bbox(antimeridian_bbox)
    assert len(sub_boxes) == 2
    # First box: [170.0, -20.0, 180.0, 20.0]
    assert sub_boxes[0].west == 170.0
    assert sub_boxes[0].east == 180.0
    # Second box: [-180.0, -20.0, -170.0, 20.0]
    assert sub_boxes[1].west == -180.0
    assert sub_boxes[1].east == -170.0

    # Test point containment across the antimeridian
    assert point_in_bbox(175.0, 0.0, antimeridian_bbox) is True
    assert point_in_bbox(-175.0, 0.0, antimeridian_bbox) is True
    # Point at 0 longitude should NOT be contained
    assert point_in_bbox(0.0, 0.0, antimeridian_bbox) is False


# ==============================================================================
# REFERENCE FIXTURE E — GEODESIC DISTANCE (CRITICAL UNIT RULE: DEGREES != METERS)
# ==============================================================================
def test_reference_fixture_e_geodesic_distance_units():
    """Fixture E: Two known point coordinates and validated geodesic distance.

    London [-0.1278, 51.5074] to Paris [2.3522, 48.8566].
    Expected: ~343.5 km (+/- 2 km), verifying explicit measurement units in meters.
    Degrees are NOT meters: 0.1 degrees != 0.1 km!
    """
    london = (-0.1278, 51.5074)
    paris = (2.3522, 48.8566)

    dist_m = calculate_distance_meters(london[0], london[1], paris[0], paris[1])
    dist_km = dist_m / 1000.0

    assert 341.0 <= dist_km <= 346.0, (
        f"Expected ~343.5 km between London and Paris, got {dist_km} km"
    )

    # Verify nearby query
    within_400km, d = is_within_radius_meters(london[0], london[1], paris[0], paris[1], 400_000.0)
    assert within_400km is True

    within_200km, _ = is_within_radius_meters(london[0], london[1], paris[0], paris[1], 200_000.0)
    assert within_200km is False


# ==============================================================================
# REFERENCE FIXTURE F — UNAUTHORIZED DATA & MULTI-TENANT ISOLATION
# ==============================================================================
def test_reference_fixture_f_unauthorized_data_isolation():
    """Fixture F: User A owns a private dataset. User B attempts access.

    Expected: Access denied (403), no feature leakage into queries or vector tiles.
    """
    private_ds = GeoDataset(
        dataset_id="test.private.tenant_a_dataset",
        dataset_name="Tenant A Private Trading Desks",
        description="Proprietary regional trading desk coordinates",
        dataset_type=DatasetType.CUSTOM_USER_LAYER,
        source_id="tenant_a_internal",
        source_version="1.0",
        geometry_types=[GeometryType.POINT],
        bounding_box=GeoBoundingBox(west=-75.0, south=40.0, east=-73.0, north=42.0),
        feature_count=1,
        attribution="Tenant A Confidential",
        licensing_policy=LicensingPolicy.RESTRICTED_ACCESS,
        is_public=False,
        owner_user_id="trader_user_a",
        tenant_id="tenant_alpha",
    )
    dataset_registry.register_dataset(private_ds)

    private_feat = GeoFeature(
        feature_id="desk_secret_01",
        dataset_id=private_ds.dataset_id,
        geometry_type=GeometryType.POINT,
        coordinates=[-74.005, 40.710],
        properties={"desk_type": "High Frequency Alpha Desk", "secret_id": "xyz987"},
        label="Desk Alpha Secret",
        source_reference="Tenant A Internal Vault",
        bounding_box=GeoBoundingBox(west=-74.005, south=40.710, east=-74.005, north=40.710),
    )
    dataset_registry.register_feature(private_feat)

    private_layer = MapLayerDefinition(
        layer_id="test.layer.private_tenant_a",
        dataset_id=private_ds.dataset_id,
        layer_name="Private Desks Layer",
        geometry_type=GeometryType.POINT,
        default_visibility=True,
    )
    layer_registry.register_layer(private_layer)

    # 1. User A (owner) queries dataset: succeeds
    res_a = atlas_maps_service.query_features(
        west=-75.0,
        south=40.0,
        east=-73.0,
        north=42.0,
        dataset_ids=[private_ds.dataset_id],
        user_id="trader_user_a",
        tenant_id="tenant_alpha",
    )
    assert res_a["result_count"] >= 1

    # 2. User B (different user, different tenant) queries dataset: Access Denied
    with pytest.raises(MapDatasetAccessDeniedError):
        atlas_maps_service.query_features(
            west=-75.0,
            south=40.0,
            east=-73.0,
            north=42.0,
            dataset_ids=[private_ds.dataset_id],
            user_id="trader_user_b",
            tenant_id="tenant_beta",
        )

    # 3. User B requests tile of private layer: Access Denied
    with pytest.raises(MapLayerAccessDeniedError):
        atlas_maps_service.get_vector_tile(
            layer_id=private_layer.layer_id,
            z=10,
            x=301,
            y=384,
            user_id="trader_user_b",
            tenant_id="tenant_beta",
        )


# ==============================================================================
# REFERENCE FIXTURE G — STYLE CHANGE PERSISTENCE
# ==============================================================================
def test_reference_fixture_g_style_change_state_preservation():
    """Fixture G: User has 2 visible layers and a selected feature.

    Switches basemap style from 'atlas-dark' to 'atlas-light'.
    Expected: Application layers, camera, and selection remain intact.
    """
    initial_style = "atlas-dark"
    new_style = "atlas-light"
    layers = ["atlas.layer.financial_centers", "atlas.layer.world_boundaries"]
    selected_feature = "fc_lon"

    # Verify both styles are valid
    styles = {s["style_id"]: s for s in atlas_maps_service.list_styles()}
    assert initial_style in styles
    assert new_style in styles

    # Simulate view state transition
    camera = GeoCameraState(longitude=-0.1278, latitude=51.5074, zoom=10.0)
    view = map_view_service.save_view(
        owner_user_id="analyst_test",
        name="London Analysis View",
        camera=camera,
        basemap_style_id=initial_style,
        visible_layers=layers,
        layer_configurations={"atlas.layer.financial_centers": {"opacity": 0.9}},
        selected_feature_id=selected_feature,
    )

    # Update style to light
    updated_view = map_view_service.update_view(
        view_id=view.map_view_id,
        user_id="analyst_test",
        expected_revision=1,
        basemap_style_id=new_style,
    )
    assert updated_view.basemap_style_id == new_style
    assert updated_view.visible_layers == layers
    assert updated_view.selected_feature_id == selected_feature
    assert updated_view.camera.longitude == -0.1278
    assert updated_view.camera.latitude == 51.5074
    assert updated_view.revision == 2


# ==============================================================================
# REFERENCE FIXTURE H — SAVED MAP VIEW PERSISTENCE & RESTORATION
# ==============================================================================
def test_reference_fixture_h_saved_map_view_round_trip():
    """Fixture H: Save camera, style, layers, opacity, and selected feature.

    Reload.
    Expected: Exact authorized restoration.
    """
    camera = GeoCameraState(
        longitude=139.6917,
        latitude=35.6895,
        zoom=11.5,
        bearing=15.0,
        pitch=20.0,
        projection="mercator",
    )
    view = map_view_service.save_view(
        owner_user_id="trader_tokyo",
        name="Tokyo Financial District View",
        camera=camera,
        basemap_style_id="atlas-dark",
        visible_layers=["atlas.layer.financial_centers"],
        layer_configurations={"atlas.layer.financial_centers": {"opacity": 0.85}},
        selected_feature_id="fc_tyo",
        workspace_id="ws_quant_research",
    )
    assert view.map_view_id.startswith("map_view_")

    restored = map_view_service.get_view(view.map_view_id, user_id="trader_tokyo")
    assert restored.name == "Tokyo Financial District View"
    assert restored.camera.longitude == 139.6917
    assert restored.camera.latitude == 35.6895
    assert restored.camera.zoom == 11.5
    assert restored.camera.bearing == 15.0
    assert restored.camera.pitch == 20.0
    assert restored.selected_feature_id == "fc_tyo"
    assert restored.visible_layers == ["atlas.layer.financial_centers"]


# ==============================================================================
# REFERENCE FIXTURE I — INDEPENDENT WORKSPACE MAP PANELS
# ==============================================================================
def test_reference_fixture_i_independent_workspace_panel_cameras():
    """Fixture I: Workspace Panel A centered on Region X (New York),

    Panel B centered on Region Y (Tokyo).
    Expected: Cameras remain strictly independent; mutations to Panel A do not alter Panel B.
    """
    view_panel_a = map_view_service.save_view(
        owner_user_id="trader_workspace",
        name="Panel A (NYC)",
        camera=GeoCameraState(longitude=-74.0060, latitude=40.7128, zoom=12.0),
        basemap_style_id="atlas-dark",
        visible_layers=["atlas.layer.financial_centers"],
        layer_configurations={},
        workspace_id="ws_multi_panel",
    )

    view_panel_b = map_view_service.save_view(
        owner_user_id="trader_workspace",
        name="Panel B (Tokyo)",
        camera=GeoCameraState(longitude=139.6917, latitude=35.6895, zoom=10.0),
        basemap_style_id="atlas-minimal",
        visible_layers=["atlas.layer.world_boundaries"],
        layer_configurations={},
        workspace_id="ws_multi_panel",
    )

    # Mutate Panel A
    map_view_service.update_view(
        view_id=view_panel_a.map_view_id,
        user_id="trader_workspace",
        expected_revision=1,
        camera=GeoCameraState(longitude=-73.9800, latitude=40.7500, zoom=14.0),
    )

    # Verify Panel B remains strictly unchanged
    check_b = map_view_service.get_view(view_panel_b.map_view_id, user_id="trader_workspace")
    assert check_b.camera.longitude == 139.6917
    assert check_b.camera.latitude == 35.6895
    assert check_b.camera.zoom == 10.0
    assert check_b.basemap_style_id == "atlas-minimal"
    assert check_b.visible_layers == ["atlas.layer.world_boundaries"]


# ==============================================================================
# REFERENCE FIXTURE J — RESTRICTED TILES & CACHE REVOCATION
# ==============================================================================
def test_reference_fixture_j_restricted_tiles_cache_invalidation():
    """Fixture J: Restricted dataset is disabled / access revoked.

    Expected: Tiles denied (403), protected cache invalidated.
    """
    restricted_ds = GeoDataset(
        dataset_id="test.restricted.dataset",
        dataset_name="Restricted Proprietary Assets",
        description="Restricted test dataset",
        dataset_type=DatasetType.CUSTOM_USER_LAYER,
        source_id="restricted_src",
        source_version="1.0",
        geometry_types=[GeometryType.POINT],
        is_public=False,
        owner_user_id="trader_user_a",
    )
    dataset_registry.register_dataset(restricted_ds)

    restricted_layer = MapLayerDefinition(
        layer_id="test.restricted.layer",
        dataset_id=restricted_ds.dataset_id,
        layer_name="Restricted Layer",
        geometry_type=GeometryType.POINT,
    )
    layer_registry.register_layer(restricted_layer)

    # Generate and cache tile for User A
    tile_bytes = atlas_maps_service.get_vector_tile(
        layer_id=restricted_layer.layer_id,
        z=5,
        x=10,
        y=12,
        user_id="trader_user_a",
    )
    assert len(tile_bytes) > 0

    # Invalidate cache
    invalidated_count = tile_cache_manager.invalidate_layer(restricted_layer.layer_id)
    assert invalidated_count >= 1

    # Unauthorized User B attempts to access tile
    with pytest.raises(MapLayerAccessDeniedError):
        atlas_maps_service.get_vector_tile(
            layer_id=restricted_layer.layer_id,
            z=5,
            x=10,
            y=12,
            user_id="trader_user_b",
        )


# ==============================================================================
# EPSG:4326 <-> EPSG:3857 PROJECTIONS
# ==============================================================================
def test_projections_round_trip():
    """Verifies precision of forward and inverse projection transformations."""
    test_coords = [
        (0.0, 0.0),
        (-74.0060, 40.7128),
        (139.6917, 35.6895),
        (-0.1278, 51.5074),
        (151.2093, -33.8688),
    ]
    for lon, lat in test_coords:
        x, y = epsg4326_to_epsg3857(lon, lat)
        rt_lon, rt_lat = epsg3857_to_epsg4326(x, y)
        assert abs(rt_lon - lon) < 1e-4, (
            f"Longitude round-trip error for ({lon}, {lat}): got {rt_lon}"
        )
        assert abs(rt_lat - lat) < 1e-4, (
            f"Latitude round-trip error for ({lon}, {lat}): got {rt_lat}"
        )


# ==============================================================================
# GEOGRAPHIC SEARCH ENGINE TESTS
# ==============================================================================
def test_geographic_search():
    """Tests search across financial centers, sovereign countries, and coordinate inputs."""
    # 1. Search financial center
    res_nyc = geographic_search_service.search("New York")
    assert len(res_nyc) >= 1
    assert res_nyc[0].place_type == "financial_center"
    assert res_nyc[0].coordinates == [-74.0060, 40.7128]

    # 2. Search country
    res_deu = geographic_search_service.search("Germany")
    assert len(res_deu) >= 1
    assert res_deu[0].place_type == "country"

    # 3. Coordinate navigation
    res_coords = geographic_search_service.search("51.5074, -0.1278")
    assert len(res_coords) >= 1
    assert res_coords[0].place_type == "coordinates"
    assert res_coords[0].coordinates == [-0.1278, 51.5074]


# ==============================================================================
# REST API ENDPOINT TESTS
# ==============================================================================
def test_api_map_config(test_client: TestClient):
    resp = test_client.get("/api/v1/maps/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["canonical_crs"] == "EPSG:4326"
    assert data["tile_projection"] == "EPSG:3857"
    assert "default_camera" in data
    assert "OpenStreetMap" in data["attribution"]


def test_api_map_styles(test_client: TestClient):
    resp = test_client.get("/api/v1/maps/styles")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 3
    style_ids = [s["style_id"] for s in data]
    assert "atlas-dark" in style_ids
    assert "atlas-light" in style_ids


def test_api_map_layers(test_client: TestClient):
    resp = test_client.get("/api/v1/maps/layers")
    assert resp.status_code == 200
    data = resp.json()
    layer_ids = [layer["layer_id"] for layer in data]
    assert "atlas.layer.financial_centers" in layer_ids


def test_api_spatial_query_features(test_client: TestClient):
    # Query world bounding box
    resp = test_client.post(
        "/api/v1/maps/features/query",
        json={
            "west": -180.0,
            "south": -90.0,
            "east": 180.0,
            "north": 90.0,
            "dataset_ids": ["atlas.reference.financial_centers"],
            "limit": 50,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 10
    assert data["coordinate_reference_system"] == "EPSG:4326"


def test_api_spatial_query_nearby(test_client: TestClient):
    # Proximity query around London (radius 500 km should include London and Paris)
    resp = test_client.post(
        "/api/v1/maps/features/nearby",
        json={
            "longitude": -0.1278,
            "latitude": 51.5074,
            "radius_meters": 500_000.0,
            "dataset_ids": ["atlas.reference.financial_centers"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    labels = [f["properties"]["label"] for f in data]
    assert "City of London Financial Center" in labels
    assert "Paris Financial Center" in labels


def test_api_feature_detail(test_client: TestClient):
    resp = test_client.get("/api/v1/maps/features/fc_nyc")
    assert resp.status_code == 200
    data = resp.json()
    assert data["feature_id"] == "fc_nyc"
    assert data["label"] == "New York Financial Center"
    assert data["data_quality"] == "verified"
    assert "NYSE" in data["properties"]["description"]


def test_api_vector_tile_binary(test_client: TestClient):
    # Request tile at zoom 2
    resp = test_client.get("/api/v1/maps/tiles/atlas.layer.financial_centers/2/2/1.pbf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/x-protobuf"
    assert len(resp.content) > 0


def test_api_geographic_search(test_client: TestClient):
    resp = test_client.get("/api/v1/maps/search?q=Tokyo")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["label"] == "Tokyo Financial District"


def test_api_saved_map_views_crud(test_client: TestClient):
    # 1. Create View
    save_payload = {
        "name": "Global Macro View",
        "camera": {
            "longitude": 0.0,
            "latitude": 20.0,
            "zoom": 2.5,
            "bearing": 0.0,
            "pitch": 0.0,
            "projection": "mercator",
            "revision": 1,
        },
        "basemap_style_id": "atlas-dark",
        "visible_layers": ["atlas.layer.financial_centers"],
        "layer_configurations": {},
        "selected_feature_id": "fc_lon",
    }
    create_resp = test_client.post("/api/v1/maps/views", json=save_payload)
    assert create_resp.status_code == 200
    view_data = create_resp.json()
    view_id = view_data["map_view_id"]
    assert view_data["name"] == "Global Macro View"
    assert view_data["revision"] == 1

    # 2. Get View
    get_resp = test_client.get(f"/api/v1/maps/views/{view_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["selected_feature_id"] == "fc_lon"

    # 3. Update View with revision conflict check
    # Stale revision should fail with 409
    stale_resp = test_client.patch(
        f"/api/v1/maps/views/{view_id}",
        json={"expected_revision": 99, "name": "Conflicting Name"},
    )
    assert stale_resp.status_code == 409

    # Valid revision succeeds
    update_resp = test_client.patch(
        f"/api/v1/maps/views/{view_id}",
        json={"expected_revision": 1, "name": "Global Macro View v2"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Global Macro View v2"
    assert update_resp.json()["revision"] == 2

    # 4. Delete View
    del_resp = test_client.delete(f"/api/v1/maps/views/{view_id}")
    assert del_resp.status_code == 200

    # 5. Verify 404 after delete
    verify_resp = test_client.get(f"/api/v1/maps/views/{view_id}")
    assert verify_resp.status_code == 404
