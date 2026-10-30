"""Pydantic Request and Response Schemas for ATLAS 3D Globe API (Stage 130).

Implements typed DTOs for globe runtime configurations, camera states,
imagery providers, terrain sources, 3D tilesets, and saved globe views.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GlobeCameraDTO(BaseModel):
    longitude: float = Field(..., ge=-180.0, le=180.0)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    height_meters: float = Field(..., ge=0.0)
    heading_radians: float = 0.0
    pitch_radians: float = -1.5707963267948966
    roll_radians: float = 0.0
    scene_mode: str = "SCENE3D"
    camera_schema_version: str = "1.0"


class MapLibreCameraDTO(BaseModel):
    center: tuple[float, float]
    zoom: float = Field(..., ge=0.0, le=22.0)
    pitch: float = Field(0.0, ge=0.0, le=85.0)
    bearing: float = Field(0.0, ge=0.0, le=360.0)


class GlobeRuntimeConfigDTO(BaseModel):
    default_imagery_provider_id: str
    default_terrain_provider_id: str
    ion_configured: bool
    supported_modes: list[str]
    max_active_viewers: int
    default_camera: GlobeCameraDTO


class GlobeImageryProviderDTO(BaseModel):
    provider_id: str
    name: str
    imagery_type: str
    source_url: str
    attribution: str
    licensing_policy: str
    is_available: bool
    is_default: bool
    max_zoom: int
    description: str


class GlobeTerrainProviderDTO(BaseModel):
    provider_id: str
    name: str
    terrain_type: str
    attribution: str
    source_url_optional: str | None = None
    is_available: bool
    is_default: bool
    has_measured_elevation: bool
    description: str


class Atlas3DTilesetSourceDTO(BaseModel):
    tileset_id: str
    dataset_id: str
    source_type: str
    source_reference: str
    bounding_volume: dict[str, Any]
    attribution: str
    licensing_policy: str
    tenant_id: str | None = None
    is_available: bool
    data_quality: str
    description: str


class UserGlobeViewDTO(BaseModel):
    view_id: str
    tenant_id: str
    owner_user_id: str
    name: str
    description: str
    renderer_mode: str
    cesium_camera: GlobeCameraDTO
    maplibre_camera: MapLibreCameraDTO | None = None
    imagery_provider_id: str
    terrain_provider_id: str
    visible_layer_references: list[str]
    selected_feature_id: str | None = None
    quality_profile: str
    revision: int
    created_at: str
    updated_at: str


class SaveGlobeViewRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    cesium_camera: GlobeCameraDTO
    description: str = ""
    renderer_mode: str = "3D"
    maplibre_camera: MapLibreCameraDTO | None = None
    imagery_provider_id: str = "natural-earth"
    terrain_provider_id: str = "ellipsoid"
    visible_layer_references: list[str] = Field(default_factory=list)
    selected_feature_id: str | None = None
    quality_profile: str = "balanced"


class UpdateGlobeViewRequest(BaseModel):
    expected_revision: int
    name: str | None = None
    description: str | None = None
    cesium_camera: GlobeCameraDTO | None = None
    maplibre_camera: MapLibreCameraDTO | None = None
    imagery_provider_id: str | None = None
    terrain_provider_id: str | None = None
    visible_layer_references: list[str] | None = None
    selected_feature_id: str | None = None
    quality_profile: str | None = None


class GlobeFeaturesQueryRequest(BaseModel):
    bounding_box: list[float] = Field(..., min_length=4, max_length=4)  # [west, south, east, north]
    layer_ids: list[str] | None = None


class CameraConversionRequest(BaseModel):
    from_mode: str = Field(..., description="'2D' or '3D'")
    maplibre_camera: MapLibreCameraDTO | None = None
    cesium_camera: GlobeCameraDTO | None = None


class CameraConversionResponse(BaseModel):
    cesium_camera: GlobeCameraDTO | None = None
    maplibre_camera: MapLibreCameraDTO | None = None
