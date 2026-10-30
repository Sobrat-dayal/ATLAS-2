"""Domain Models and Dataclasses for ATLAS 3D God's Eye Globe (Stage 130).

Implements canonical 3D camera models, geodetic representations,
imagery providers, terrain abstractions, OGC 3D Tilesets, and 2D/3D interoperability schemas.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from atlas.maps.domain import DataQualityStatus, GeoCameraState, LicensingPolicy
from atlas.maps.globe.errors import GlobeCameraInvalidError


class RendererMode(str, Enum):
    MAP_2D = "2D"
    GLOBE_3D = "3D"


class GlobeImageryType(str, Enum):
    NATURAL_EARTH = "NATURAL_EARTH"
    SATELLITE = "SATELLITE"
    OPEN_STREET_MAP = "OPEN_STREET_MAP"
    CARTOGRAPHIC_DARK = "CARTOGRAPHIC_DARK"
    CARTOGRAPHIC_LIGHT = "CARTOGRAPHIC_LIGHT"


class GlobeTerrainType(str, Enum):
    ELLIPSOID = "ELLIPSOID"
    CESIUM_WORLD_TERRAIN = "CESIUM_WORLD_TERRAIN"
    LICENSED_TERRAIN = "LICENSED_TERRAIN"


class TilesetSourceType(str, Enum):
    OGC_3D_TILES = "OGC_3D_TILES"


class AltitudeMode(str, Enum):
    ABSOLUTE_ELLIPSOID_HEIGHT = "ABSOLUTE_ELLIPSOID_HEIGHT"
    RELATIVE_TO_TERRAIN = "RELATIVE_TO_TERRAIN"
    CLAMP_TO_TERRAIN = "CLAMP_TO_TERRAIN"


@dataclass(frozen=True)
class AtlasGlobeCamera:
    """Canonical 3D Globe camera state with strict validation and finite value guarantees."""

    longitude: float
    latitude: float
    height_meters: float
    heading_radians: float = 0.0
    pitch_radians: float = -math.pi / 2  # Looking straight down toward nadir (-90 deg)
    roll_radians: float = 0.0
    scene_mode: str = "SCENE3D"
    camera_schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if not math.isfinite(self.longitude) or not (-180.0 <= self.longitude <= 180.0):
            raise GlobeCameraInvalidError(
                f"Longitude must be finite and within [-180, 180], got {self.longitude}"
            )
        if not math.isfinite(self.latitude) or not (-90.0 <= self.latitude <= 90.0):
            raise GlobeCameraInvalidError(
                f"Latitude must be finite and within [-90, 90], got {self.latitude}"
            )
        if not math.isfinite(self.height_meters) or self.height_meters < 0:
            raise GlobeCameraInvalidError(
                f"Height must be a positive finite number of meters, got {self.height_meters}"
            )
        if not math.isfinite(self.heading_radians):
            raise GlobeCameraInvalidError("Heading must be a finite float")
        if not math.isfinite(self.pitch_radians) or not (-math.pi <= self.pitch_radians <= math.pi):
            raise GlobeCameraInvalidError("Pitch must be within [-pi, pi]")
        if not math.isfinite(self.roll_radians):
            raise GlobeCameraInvalidError("Roll must be a finite float")

    def to_dict(self) -> dict[str, Any]:
        return {
            "longitude": self.longitude,
            "latitude": self.latitude,
            "height_meters": self.height_meters,
            "heading_radians": self.heading_radians,
            "pitch_radians": self.pitch_radians,
            "roll_radians": self.roll_radians,
            "scene_mode": self.scene_mode,
            "camera_schema_version": self.camera_schema_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AtlasGlobeCamera:
        return cls(
            longitude=float(data["longitude"]),
            latitude=float(data["latitude"]),
            height_meters=float(data["height_meters"]),
            heading_radians=float(data.get("heading_radians", 0.0)),
            pitch_radians=float(data.get("pitch_radians", -math.pi / 2)),
            roll_radians=float(data.get("roll_radians", 0.0)),
            scene_mode=data.get("scene_mode", "SCENE3D"),
            camera_schema_version=data.get("camera_schema_version", "1.0"),
        )


@dataclass(frozen=True)
class GlobeImageryProvider:
    """Registered authorized globe imagery provider."""

    provider_id: str
    name: str
    imagery_type: GlobeImageryType
    source_url: str
    attribution: str
    licensing_policy: LicensingPolicy = LicensingPolicy.OPEN_DATA_CC_BY
    is_available: bool = True
    is_default: bool = False
    max_zoom: int = 19
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "imagery_type": self.imagery_type.value,
            "source_url": self.source_url,
            "attribution": self.attribution,
            "licensing_policy": self.licensing_policy.value,
            "is_available": self.is_available,
            "is_default": self.is_default,
            "max_zoom": self.max_zoom,
            "description": self.description,
        }


@dataclass(frozen=True)
class GlobeTerrainProvider:
    """Registered terrain elevation provider with honest elevation reporting."""

    provider_id: str
    name: str
    terrain_type: GlobeTerrainType
    attribution: str
    source_url_optional: str | None = None
    is_available: bool = True
    is_default: bool = False
    has_measured_elevation: bool = False
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "terrain_type": self.terrain_type.value,
            "attribution": self.attribution,
            "source_url_optional": self.source_url_optional,
            "is_available": self.is_available,
            "is_default": self.is_default,
            "has_measured_elevation": self.has_measured_elevation,
            "description": self.description,
        }


@dataclass(frozen=True)
class Atlas3DTilesetSource:
    """OGC 3D Tileset source definition with multi-tenant access control and bounding volume."""

    tileset_id: str
    dataset_id: str
    source_type: TilesetSourceType
    source_reference: str
    bounding_volume: dict[str, Any]
    attribution: str
    licensing_policy: LicensingPolicy = LicensingPolicy.OPEN_DATA_CC_BY
    tenant_id: str | None = (
        None  # None indicates system/public reference; string indicates tenant-private
    )
    is_available: bool = True
    data_quality: DataQualityStatus = DataQualityStatus.VERIFIED
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tileset_id": self.tileset_id,
            "dataset_id": self.dataset_id,
            "source_type": self.source_type.value,
            "source_reference": self.source_reference,
            "bounding_volume": self.bounding_volume,
            "attribution": self.attribution,
            "licensing_policy": self.licensing_policy.value,
            "tenant_id": self.tenant_id,
            "is_available": self.is_available,
            "data_quality": self.data_quality.value,
            "description": self.description,
        }


@dataclass
class UserGlobeView:
    """Persistent saved 3D globe view with multi-tenant isolation and optimistic revision locking."""

    view_id: str
    tenant_id: str
    owner_user_id: str
    name: str
    cesium_camera: AtlasGlobeCamera
    renderer_mode: RendererMode = RendererMode.GLOBE_3D
    maplibre_camera: GeoCameraState | None = None
    description: str = ""
    imagery_provider_id: str = "natural-earth"
    terrain_provider_id: str = "ellipsoid"
    visible_layer_references: list[str] = field(default_factory=list)
    selected_feature_id: str | None = None
    quality_profile: str = "balanced"
    revision: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "view_id": self.view_id,
            "tenant_id": self.tenant_id,
            "owner_user_id": self.owner_user_id,
            "name": self.name,
            "description": self.description,
            "renderer_mode": self.renderer_mode.value,
            "cesium_camera": self.cesium_camera.to_dict(),
            "maplibre_camera": self.maplibre_camera.to_dict() if self.maplibre_camera else None,
            "imagery_provider_id": self.imagery_provider_id,
            "terrain_provider_id": self.terrain_provider_id,
            "visible_layer_references": list(self.visible_layer_references),
            "selected_feature_id": self.selected_feature_id,
            "quality_profile": self.quality_profile,
            "revision": self.revision,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(frozen=True)
class GlobeRuntimeConfig:
    """Runtime capabilities and configuration parameters for the 3D globe."""

    default_imagery_provider_id: str
    default_terrain_provider_id: str
    ion_configured: bool
    supported_modes: list[str] = field(default_factory=lambda: ["2D", "3D"])
    max_active_viewers: int = 2
    default_camera: AtlasGlobeCamera = field(
        default_factory=lambda: AtlasGlobeCamera(
            longitude=0.0,
            latitude=20.0,
            height_meters=20000000.0,
            heading_radians=0.0,
            pitch_radians=-math.pi / 2,
            roll_radians=0.0,
        )
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_imagery_provider_id": self.default_imagery_provider_id,
            "default_terrain_provider_id": self.default_terrain_provider_id,
            "ion_configured": self.ion_configured,
            "supported_modes": self.supported_modes,
            "max_active_viewers": self.max_active_viewers,
            "default_camera": self.default_camera.to_dict(),
        }
