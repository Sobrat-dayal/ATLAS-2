"""Master 3D God's Eye Globe Service for ATLAS (Stage 130).

Integrates Cesium 3D Globe capabilities, imagery/terrain catalogs,
OGC 3D Tileset authorization, saved views, and Stage 129 PostGIS features.
"""

from __future__ import annotations

import os

from atlas.maps.datasets.registry import AtlasDatasetRegistry, dataset_registry
from atlas.maps.domain import GeoBoundingBox, GeoCameraState, GeoFeature
from atlas.maps.globe.domain import (
    Atlas3DTilesetSource,
    AtlasGlobeCamera,
    GlobeImageryProvider,
    GlobeRuntimeConfig,
    GlobeTerrainProvider,
    RendererMode,
    UserGlobeView,
)
from atlas.maps.globe.interop import cesium_to_maplibre_camera
from atlas.maps.globe.providers import AtlasGlobeProviderRegistry
from atlas.maps.globe.tilesets import AtlasGlobeTilesetRegistry
from atlas.maps.globe.views import AtlasGlobeViewService
from atlas.maps.layers.registry import AtlasLayerRegistry, layer_registry
from atlas.maps.search.service import AtlasGeographicSearchService, geographic_search_service


class AtlasGlobeService:
    """Master service providing high-level 3D globe operations, security, and data integration."""

    def __init__(
        self,
        provider_registry: AtlasGlobeProviderRegistry | None = None,
        tileset_registry: AtlasGlobeTilesetRegistry | None = None,
        view_service: AtlasGlobeViewService | None = None,
        datasets: AtlasDatasetRegistry | None = None,
        layers: AtlasLayerRegistry | None = None,
        search_svc: AtlasGeographicSearchService | None = None,
    ) -> None:
        self.providers = provider_registry or AtlasGlobeProviderRegistry()
        self.tilesets = tileset_registry or AtlasGlobeTilesetRegistry()
        self.views = view_service or AtlasGlobeViewService()
        self.datasets = datasets or dataset_registry
        self.layers = layers or layer_registry
        self.search = search_svc or geographic_search_service

    def get_runtime_config(self, tenant_id: str, user_id: str) -> GlobeRuntimeConfig:
        """Retrieve runtime globe capabilities and default configuration."""
        has_ion = bool(os.environ.get("CESIUM_ION_TOKEN"))
        return GlobeRuntimeConfig(
            default_imagery_provider_id="natural-earth",
            default_terrain_provider_id="ellipsoid",
            ion_configured=has_ion,
            supported_modes=["2D", "3D"],
            max_active_viewers=2,
            default_camera=AtlasGlobeCamera(
                longitude=0.0,
                latitude=20.0,
                height_meters=20000000.0,
                heading_radians=0.0,
                pitch_radians=-1.5707963267948966,
                roll_radians=0.0,
            ),
        )

    # Imagery Operations
    def list_imagery_providers(
        self,
        tenant_id: str,
        include_restricted: bool = False,
    ) -> list[GlobeImageryProvider]:
        return self.providers.list_imagery(include_restricted=include_restricted)

    def get_imagery_provider(
        self,
        provider_id: str,
        tenant_id: str,
        tenant_entitled: bool = True,
    ) -> GlobeImageryProvider:
        return self.providers.get_imagery(provider_id, tenant_entitled=tenant_entitled)

    # Terrain Operations
    def list_terrain_providers(
        self,
        tenant_id: str,
        include_restricted: bool = False,
    ) -> list[GlobeTerrainProvider]:
        return self.providers.list_terrain(include_restricted=include_restricted)

    def get_terrain_provider(
        self,
        provider_id: str,
        tenant_id: str,
        tenant_entitled: bool = True,
    ) -> GlobeTerrainProvider:
        return self.providers.get_terrain(provider_id, tenant_entitled=tenant_entitled)

    # 3D Tileset Operations (Multi-tenant)
    def list_tilesets(self, tenant_id: str, is_admin: bool = False) -> list[Atlas3DTilesetSource]:
        return self.tilesets.list_tilesets(tenant_id=tenant_id, is_admin=is_admin)

    def get_tileset(
        self,
        tileset_id: str,
        tenant_id: str,
        is_admin: bool = False,
    ) -> Atlas3DTilesetSource:
        return self.tilesets.get_tileset(
            tileset_id=tileset_id, tenant_id=tenant_id, is_admin=is_admin
        )

    # Saved View Operations (Multi-tenant with Revision Locking)
    def list_views(self, tenant_id: str, owner_user_id: str | None = None) -> list[UserGlobeView]:
        return self.views.list_views(tenant_id=tenant_id, owner_user_id=owner_user_id)

    def get_view(self, view_id: str, tenant_id: str) -> UserGlobeView:
        return self.views.get_view(view_id=view_id, tenant_id=tenant_id)

    def save_view(
        self,
        tenant_id: str,
        owner_user_id: str,
        name: str,
        cesium_camera: AtlasGlobeCamera,
        description: str = "",
        renderer_mode: RendererMode = RendererMode.GLOBE_3D,
        maplibre_camera: GeoCameraState | None = None,
        imagery_provider_id: str = "natural-earth",
        terrain_provider_id: str = "ellipsoid",
        visible_layer_references: list[str] | None = None,
        selected_feature_id: str | None = None,
        quality_profile: str = "balanced",
    ) -> UserGlobeView:
        # If 2D camera not provided, derive it through interop conversion
        if maplibre_camera is None:
            maplibre_camera = cesium_to_maplibre_camera(cesium_camera)

        return self.views.create_view(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            name=name,
            cesium_camera=cesium_camera,
            description=description,
            renderer_mode=renderer_mode,
            maplibre_camera=maplibre_camera,
            imagery_provider_id=imagery_provider_id,
            terrain_provider_id=terrain_provider_id,
            visible_layer_references=visible_layer_references,
            selected_feature_id=selected_feature_id,
            quality_profile=quality_profile,
        )

    def update_view(
        self,
        view_id: str,
        tenant_id: str,
        expected_revision: int,
        owner_user_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        cesium_camera: AtlasGlobeCamera | None = None,
        maplibre_camera: GeoCameraState | None = None,
        imagery_provider_id: str | None = None,
        terrain_provider_id: str | None = None,
        visible_layer_references: list[str] | None = None,
        selected_feature_id: str | None = None,
        quality_profile: str | None = None,
    ) -> UserGlobeView:
        if cesium_camera is not None and maplibre_camera is None:
            maplibre_camera = cesium_to_maplibre_camera(cesium_camera)

        return self.views.update_view(
            view_id=view_id,
            tenant_id=tenant_id,
            expected_revision=expected_revision,
            owner_user_id=owner_user_id,
            name=name,
            description=description,
            cesium_camera=cesium_camera,
            maplibre_camera=maplibre_camera,
            imagery_provider_id=imagery_provider_id,
            terrain_provider_id=terrain_provider_id,
            visible_layer_references=visible_layer_references,
            selected_feature_id=selected_feature_id,
            quality_profile=quality_profile,
        )

    def delete_view(self, view_id: str, tenant_id: str, owner_user_id: str | None = None) -> bool:
        return self.views.delete_view(
            view_id=view_id, tenant_id=tenant_id, owner_user_id=owner_user_id
        )

    # Feature Queries & Geocoding Integration
    def query_features(
        self,
        bbox: GeoBoundingBox,
        layer_ids: list[str] | None = None,
        tenant_id: str = "default-tenant",
    ) -> list[GeoFeature]:
        """Query spatial features within a bounding box from Stage 129 PostGIS dataset registry."""
        results: list[GeoFeature] = []
        target_layers = layer_ids or [
            "atlas.layer.financial_centers",
            "atlas.layer.world_countries",
        ]

        for layer_id in target_layers:
            layer = self.layers.get_layer(layer_id)
            if not layer:
                continue
            dataset = self.datasets.get_dataset(layer.dataset_id, tenant_id=tenant_id)
            if not dataset:
                continue
            for feature in dataset.features:
                if feature.geometry.intersects_bounding_box(bbox):
                    results.append(feature)

        return results


# Module-level singleton
globe_service = AtlasGlobeService()
