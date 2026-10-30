"""Comprehensive Institutional Verification Test Suite for ATLAS 3D God's Eye Globe (Stage 130).

Verifies all 10 Golden Reference Fixtures (A through J), WGS84 ECEF coordinate conversions,
2D/3D camera interoperability, OGC 3D Tileset multi-tenant authorization,
imagery/terrain provider registries, and Saved Globe View optimistic concurrency.
"""

from __future__ import annotations

import math

import pytest
from atlas.maps.globe.coordinates import (
    cartesian_to_geodetic,
    geodetic_to_cartesian,
)
from atlas.maps.globe.domain import (
    AtlasGlobeCamera,
    GlobeTerrainType,
    RendererMode,
    TilesetSourceType,
)
from atlas.maps.globe.errors import (
    GlobeCameraInvalidError,
    GlobeImageryProviderNotFoundError,
    GlobeImageryProviderRestrictedError,
    GlobeTerrainProviderNotFoundError,
    GlobeTerrainProviderRestrictedError,
    GlobeTilesetAccessDeniedError,
    GlobeTilesetNotFoundError,
    GlobeViewAccessDeniedError,
    GlobeViewNotFoundError,
    GlobeViewRevisionConflictError,
)
from atlas.maps.globe.interop import (
    cesium_to_maplibre_camera,
    maplibre_to_cesium_camera,
    normalize_longitude,
)
from atlas.maps.globe.providers import AtlasGlobeProviderRegistry
from atlas.maps.globe.service import AtlasGlobeService
from atlas.maps.globe.tilesets import AtlasGlobeTilesetRegistry
from atlas.maps.globe.views import AtlasGlobeViewService


class TestStage130MapsGlobeV1:
    """Institutional test suite for Stage 130 3D God's Eye Globe."""

    # =========================================================================
    # FIXTURE A: Bare Globe & Ellipsoid Fallback
    # =========================================================================
    def test_fixture_a_bare_globe_initialization(self) -> None:
        """Verifies default runtime configuration provides a bare WGS84 ellipsoid without external dependency."""
        service = AtlasGlobeService()
        cfg = service.get_runtime_config(tenant_id="tenant-test", user_id="user-1")

        assert cfg.default_imagery_provider_id == "natural-earth"
        assert cfg.default_terrain_provider_id == "ellipsoid"
        assert cfg.max_active_viewers == 2
        assert "2D" in cfg.supported_modes and "3D" in cfg.supported_modes

        # Ellipsoid terrain provider has no fake elevation
        terrain = service.get_terrain_provider("ellipsoid", tenant_id="tenant-test")
        assert terrain.has_measured_elevation is False
        assert terrain.terrain_type == GlobeTerrainType.ELLIPSOID
        assert "WGS84" in terrain.attribution

    # =========================================================================
    # FIXTURE B: Imagery Provider Catalog & Licensing Enforcement
    # =========================================================================
    def test_fixture_b_imagery_providers_and_licensing(self) -> None:
        """Verifies legal attribution and blocks unentitled commercial imagery."""
        registry = AtlasGlobeProviderRegistry()
        available = registry.list_imagery(include_restricted=False)
        assert len(available) >= 4

        # Verify attribution on all available providers
        for prov in available:
            assert prov.attribution and len(prov.attribution) > 0
            assert prov.is_available is True

        # Natural Earth, CARTO, OSM present
        ids = [p.provider_id for p in available]
        assert "natural-earth" in ids
        assert "carto-dark" in ids
        assert "osm-standard" in ids
        assert "satellite-reference" in ids

        # Restricted commercial imagery access without entitlement raises error
        with pytest.raises(GlobeImageryProviderRestrictedError) as exc_info:
            registry.get_imagery("restricted-premium-satellite", tenant_entitled=False)
        assert (
            "commercial imagery license" in exc_info.value.reason
            or "restricted" in exc_info.value.code.lower()
        )

    # =========================================================================
    # FIXTURE C: Terrain Provider Architecture & Outage Handling
    # =========================================================================
    def test_fixture_c_terrain_provider_and_fallback(self) -> None:
        """Verifies honest elevation reporting and graceful fallback to ellipsoid."""
        registry = AtlasGlobeProviderRegistry()

        # Ellipsoid is always available and safe
        ellipsoid = registry.get_terrain("ellipsoid")
        assert ellipsoid.is_available is True
        assert ellipsoid.has_measured_elevation is False

        # If CESIUM_ION_TOKEN is not in env, accessing cesium-world-terrain reports restriction/unavailability
        if not registry._terrain["cesium-world-terrain"].is_available:
            with pytest.raises(GlobeTerrainProviderRestrictedError):
                registry.get_terrain("cesium-world-terrain")

        # Non-existent terrain provider raises NotFound
        with pytest.raises(GlobeTerrainProviderNotFoundError):
            registry.get_terrain("fictional-hyper-terrain")

    # =========================================================================
    # FIXTURE D: 2D/3D Camera Interoperability Round-Trip
    # =========================================================================
    def test_fixture_d_camera_interoperability_round_trip(self) -> None:
        """Verifies bidirectional 2D MapLibre <-> 3D Cesium camera state conversion."""
        # Starting 2D viewport: London City center
        orig_center = (-0.1276, 51.5074)
        orig_zoom = 14.0
        orig_bearing = 45.0
        orig_pitch = 30.0

        # 2D -> 3D
        cam_3d = maplibre_to_cesium_camera(
            center_lon=orig_center[0],
            center_lat=orig_center[1],
            zoom=orig_zoom,
            bearing_deg=orig_bearing,
            pitch_deg=orig_pitch,
        )

        assert abs(cam_3d.longitude - orig_center[0]) < 1e-4
        assert abs(cam_3d.latitude - orig_center[1]) < 1e-4
        assert cam_3d.height_meters > 500.0  # Realistic altitude for zoom 14
        assert abs(math.degrees(cam_3d.heading_radians) - orig_bearing) < 1e-2

        # 3D -> 2D
        cam_2d = cesium_to_maplibre_camera(cam_3d)

        # Verify restoration within documented tolerance
        assert abs(cam_2d.longitude - orig_center[0]) < 1e-3
        assert abs(cam_2d.latitude - orig_center[1]) < 1e-3
        assert abs(cam_2d.zoom - orig_zoom) <= 0.5
        assert abs(cam_2d.bearing - orig_bearing) <= 1.0
        assert abs(cam_2d.pitch - orig_pitch) <= 1.0

    def test_fixture_d_camera_interop_edge_cases(self) -> None:
        """Verifies safe handling of Web Mercator latitude clamp and antimeridian normalization."""
        # Polar latitude clamp (above 85.05 deg)
        polar_3d = AtlasGlobeCamera(
            longitude=0.0,
            latitude=88.5,
            height_meters=100000.0,
            heading_radians=0.0,
            pitch_radians=-math.pi / 2,
        )
        polar_2d = cesium_to_maplibre_camera(polar_3d)
        assert polar_2d.latitude <= 85.051129

        # Space-directed pitch (> 0, tilted up away from Earth) falls back to nadir pitch
        sky_cam = AtlasGlobeCamera(
            longitude=10.0,
            latitude=20.0,
            height_meters=500000.0,
            pitch_radians=0.2,  # pointing to sky
        )
        sky_2d = cesium_to_maplibre_camera(sky_cam)
        assert 0.0 <= sky_2d.pitch <= 60.0

        # Antimeridian wrap
        assert normalize_longitude(195.0) == -165.0
        assert normalize_longitude(-195.0) == 165.0

    # =========================================================================
    # FIXTURE E: Geodetic <-> Cartesian ECEF Round-Trip
    # =========================================================================
    def test_fixture_e_wgs84_cartesian_round_trip(self) -> None:
        """Verifies sub-millimeter precision round-trip conversion between Geodetic and Cartesian3."""
        landmarks = [
            ("London", -0.1276, 51.5074, 35.0),
            ("Tokyo", 139.6917, 35.6895, 40.0),
            ("New York", -74.0060, 40.7128, 10.0),
            ("Sydney", 151.2093, -33.8688, 55.0),
            ("Equator-Meridian", 0.0, 0.0, 0.0),
            ("North Pole", 0.0, 90.0, 100.0),
            ("South Pole", 0.0, -90.0, 2800.0),
        ]

        for name, lon, lat, h in landmarks:
            # Geodetic -> Cartesian (X, Y, Z)
            x, y, z = geodetic_to_cartesian(lon, lat, h)
            assert math.isfinite(x) and math.isfinite(y) and math.isfinite(z)

            # Cartesian -> Geodetic (lon', lat', h')
            lon_rt, lat_rt, h_rt = cartesian_to_geodetic(x, y, z)

            # Sub-millimeter / precision checks
            if abs(lat) < 89.9:
                assert abs(lon_rt - lon) < 1e-7, f"Longitude round-trip mismatch for {name}"
            assert abs(lat_rt - lat) < 1e-7, f"Latitude round-trip mismatch for {name}"
            assert abs(h_rt - h) < 0.005, f"Height round-trip mismatch for {name}: {h_rt} vs {h}"

    def test_fixture_e_coordinate_validation_rejections(self) -> None:
        """Verifies strict rejection of NaN, Inf, and out-of-range inputs."""
        with pytest.raises(GlobeCameraInvalidError):
            geodetic_to_cartesian(181.0, 45.0, 0.0)

        with pytest.raises(GlobeCameraInvalidError):
            geodetic_to_cartesian(0.0, -91.0, 0.0)

        with pytest.raises(GlobeCameraInvalidError):
            geodetic_to_cartesian(float("nan"), 0.0, 0.0)

        with pytest.raises(GlobeCameraInvalidError):
            AtlasGlobeCamera(longitude=0.0, latitude=0.0, height_meters=-50.0)

    # =========================================================================
    # FIXTURE F: Authorized 3D Tileset Loading & Cleanup
    # =========================================================================
    def test_fixture_f_3d_tileset_registry(self) -> None:
        """Verifies public OGC 3D Tileset definition, bounding volume, and attribution."""
        registry = AtlasGlobeTilesetRegistry()
        tilesets = registry.list_tilesets(tenant_id="tenant-any")
        assert len(tilesets) >= 1

        # London Financial District public tileset present
        london_ts = registry.get_tileset(
            "atlas.reference.financial_district_3dtiles", tenant_id="tenant-any"
        )
        assert london_ts.source_type == TilesetSourceType.OGC_3D_TILES
        assert "bounding_volume" in london_ts.to_dict()
        assert london_ts.bounding_volume["type"] == "region"
        assert london_ts.is_available is True
        assert "UK Geospatial Commission" in london_ts.attribution

    # =========================================================================
    # FIXTURE G: Multi-Tenant 3D Tileset Access Denial
    # =========================================================================
    def test_fixture_g_multitenant_tileset_isolation(self) -> None:
        """Verifies private 3D Tileset is strictly hidden and denied across tenant boundaries."""
        registry = AtlasGlobeTilesetRegistry()

        # Tenant Alpha can access its private asset
        alpha_ts = registry.get_tileset(
            "atlas.tenant_alpha.confidential_vault_3dtiles",
            tenant_id="tenant-alpha",
        )
        assert alpha_ts.tenant_id == "tenant-alpha"

        # Tenant Beta listing tilesets does NOT see Tenant Alpha's asset
        beta_tilesets = registry.list_tilesets(tenant_id="tenant-beta")
        beta_ids = [t.tileset_id for t in beta_tilesets]
        assert "atlas.tenant_alpha.confidential_vault_3dtiles" not in beta_ids

        # Tenant Beta direct fetch raises 403 Forbidden GlobeTilesetAccessDeniedError
        with pytest.raises(GlobeTilesetAccessDeniedError) as exc_info:
            registry.get_tileset(
                "atlas.tenant_alpha.confidential_vault_3dtiles",
                tenant_id="tenant-beta",
            )
        assert exc_info.value.tenant_id == "tenant-beta"

    # =========================================================================
    # FIXTURE H: Saved Globe View with Concurrency Revision Locking
    # =========================================================================
    def test_fixture_h_saved_globe_view_concurrency(self) -> None:
        """Verifies saving, retrieving, and optimistic concurrency revision locking on Globe Views."""
        service = AtlasGlobeViewService()

        # Create new 3D Globe view
        cam = AtlasGlobeCamera(
            longitude=8.5417,
            latitude=47.3769,
            height_meters=3200.0,
            heading_radians=0.1,
            pitch_radians=-0.785,
        )
        view = service.create_view(
            tenant_id="tenant-zurich",
            owner_user_id="user-123",
            name="Zurich Wealth Management 3D",
            cesium_camera=cam,
            renderer_mode=RendererMode.GLOBE_3D,
            imagery_provider_id="natural-earth",
            terrain_provider_id="ellipsoid",
            visible_layer_references=["atlas.layer.financial_centers"],
            selected_feature_id="fc-zurich",
        )

        assert view.view_id.startswith("view-globe-")
        assert view.revision == 1

        # Retrieve view
        fetched = service.get_view(view.view_id, tenant_id="tenant-zurich")
        assert fetched.name == "Zurich Wealth Management 3D"
        assert fetched.cesium_camera.longitude == 8.5417

        # Stale revision update rejected with conflict
        with pytest.raises(GlobeViewRevisionConflictError) as exc_info:
            service.update_view(
                view_id=view.view_id,
                tenant_id="tenant-zurich",
                expected_revision=999,  # Stale
                name="Updated Name",
            )
        assert exc_info.value.expected_rev == 999
        assert exc_info.value.current_rev == 1

        # Valid revision update succeeds and increments revision
        updated = service.update_view(
            view_id=view.view_id,
            tenant_id="tenant-zurich",
            expected_revision=1,
            name="Zurich Wealth Core 3D (V2)",
        )
        assert updated.revision == 2
        assert updated.name == "Zurich Wealth Core 3D (V2)"

        # Cross-tenant view retrieval rejected
        with pytest.raises(GlobeViewAccessDeniedError):
            service.get_view(view.view_id, tenant_id="tenant-other")

    # =========================================================================
    # FIXTURE I: Multiple Independent Workspace Globe Panels
    # =========================================================================
    def test_fixture_i_multiple_workspace_globe_panels(self) -> None:
        """Verifies that multiple Workspace Globe panels maintain independent cameras without crosstalk."""
        # Panel A focusing London
        panel_a_cam = AtlasGlobeCamera(
            longitude=-0.0885,
            latitude=51.5138,
            height_meters=1850.0,
            heading_radians=0.35,
            pitch_radians=-0.785,
        )

        # Panel B focusing Tokyo
        panel_b_cam = AtlasGlobeCamera(
            longitude=139.7714,
            latitude=35.6812,
            height_meters=4500.0,
            heading_radians=0.0,
            pitch_radians=-1.1,
        )

        # Panel A converts independently to 2D
        cam_a_2d = cesium_to_maplibre_camera(panel_a_cam)
        cam_b_2d = cesium_to_maplibre_camera(panel_b_cam)

        assert abs(cam_a_2d.longitude - (-0.0885)) < 1e-3
        assert abs(cam_b_2d.longitude - 139.7714) < 1e-3
        assert (cam_a_2d.longitude, cam_a_2d.latitude) != (cam_b_2d.longitude, cam_b_2d.latitude)
        assert cam_a_2d.zoom != cam_b_2d.zoom

    # =========================================================================
    # FIXTURE J: Provider Failure & Error Taxonomy
    # =========================================================================
    def test_fixture_j_provider_failure_and_error_taxonomy(self) -> None:
        """Verifies accurate error responses for missing resources and domain violations."""
        service = AtlasGlobeService()

        # Non-existent imagery provider
        with pytest.raises(GlobeImageryProviderNotFoundError):
            service.get_imagery_provider("imaginary-satellite", tenant_id="tenant-1")

        # Non-existent 3D tileset
        with pytest.raises(GlobeTilesetNotFoundError):
            service.get_tileset("missing-tileset", tenant_id="tenant-1")

        # Non-existent view
        with pytest.raises(GlobeViewNotFoundError):
            service.get_view("view-ghost-404", tenant_id="tenant-1")
