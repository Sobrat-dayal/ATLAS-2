"""Pydantic DTO Schemas for ATLAS Maps V1 REST API.

Enforces strict input validation, type safety, and standardized responses.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MapCameraDTO(BaseModel):
    longitude: float = Field(..., ge=-180.0, le=180.0)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    zoom: float = Field(..., ge=0.0, le=22.0)
    bearing: float = Field(default=0.0)
    pitch: float = Field(default=0.0)
    bounds: Optional[List[float]] = None
    projection: str = Field(default="mercator")
    revision: int = Field(default=1)


class MapConfigResponse(BaseModel):
    default_camera: Dict[str, Any]
    canonical_crs: str
    tile_projection: str
    attribution: str
    default_style_id: str
    supported_styles: List[str]
    version: str


class MapStyleDTO(BaseModel):
    style_id: str
    display_name: str
    provider_id: str
    style_url: str
    attribution: str
    license_reference: str
    is_dark: bool
    is_available: bool
    max_zoom: float


class MapLayerDTO(BaseModel):
    layer_id: str
    dataset_id: str
    layer_name: str
    geometry_type: str
    source_type: str
    default_visibility: bool
    default_opacity: float
    min_zoom: float
    max_zoom: float
    display_order: int
    category: str
    license_reference: str


class MapDatasetDTO(BaseModel):
    dataset_id: str
    dataset_name: str
    description: str
    dataset_type: str
    geometry_types: List[str]
    feature_count: int
    attribution: str
    licensing_policy: str
    is_public: bool


class SpatialQueryRequest(BaseModel):
    west: float = Field(..., ge=-180.0, le=180.0)
    south: float = Field(..., ge=-90.0, le=90.0)
    east: float = Field(..., ge=-180.0, le=180.0)
    north: float = Field(..., ge=-90.0, le=90.0)
    dataset_ids: Optional[List[str]] = None
    layer_ids: Optional[List[str]] = None
    zoom: float = Field(default=2.0, ge=0.0, le=22.0)
    limit: int = Field(default=500, ge=1, le=5000)


class SpatialNearbyRequest(BaseModel):
    longitude: float = Field(..., ge=-180.0, le=180.0)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    radius_meters: float = Field(..., gt=0.0, le=10_000_000.0)
    dataset_ids: Optional[List[str]] = None
    limit: int = Field(default=50, ge=1, le=500)


class FeatureDetailResponse(BaseModel):
    feature_id: str
    dataset_id: str
    label: str
    geometry_type: str
    coordinates: Any
    properties: Dict[str, Any]
    bounding_box: Optional[List[float]] = None
    data_quality: str
    source_reference: str
    dataset_name: str
    attribution: str
    licensing_policy: str
    source_updated_at: str


class GeographicSearchResultDTO(BaseModel):
    result_id: str
    label: str
    place_type: str
    coordinates: List[float]
    bounding_box: Optional[List[float]] = None
    source_dataset_id: str
    disambiguation: str
    relevance_score: float


class SaveMapViewRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    camera: MapCameraDTO
    basemap_style_id: str = Field(default="atlas-dark")
    visible_layers: List[str] = Field(default_factory=list)
    layer_configurations: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    selected_feature_id: Optional[str] = None
    workspace_id: Optional[str] = None


class UpdateMapViewRequest(BaseModel):
    expected_revision: int = Field(..., ge=1)
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    camera: Optional[MapCameraDTO] = None
    basemap_style_id: Optional[str] = None
    visible_layers: Optional[List[str]] = None
    layer_configurations: Optional[Dict[str, Dict[str, Any]]] = None
    selected_feature_id: Optional[str] = None


class UserMapViewResponse(BaseModel):
    map_view_id: str
    owner_user_id: str
    name: str
    camera: MapCameraDTO
    basemap_style_id: str
    visible_layers: List[str]
    layer_configurations: Dict[str, Dict[str, Any]]
    selected_feature_id: Optional[str] = None
    workspace_id: Optional[str] = None
    tenant_id: Optional[str] = None
    revision: int
    map_schema_version: str
    created_at: str
    updated_at: str
