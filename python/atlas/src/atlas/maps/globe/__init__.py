"""ATLAS 3D God's Eye Globe Package (Stage 130).

Provides Cesium 3D Globe integration, WGS84 coordinates, 2D/3D camera interop,
imagery/terrain provider registries, OGC 3D Tilesets, and saved globe views.
"""

from atlas.maps.globe.coordinates import (
    cartesian_to_geodetic,
    degrees_to_radians,
    geodetic_to_cartesian,
    radians_to_degrees,
    validate_globe_coordinates,
)
from atlas.maps.globe.domain import (
    AltitudeMode,
    Atlas3DTilesetSource,
    AtlasGlobeCamera,
    GlobeImageryProvider,
    GlobeImageryType,
    GlobeRuntimeConfig,
    GlobeTerrainProvider,
    GlobeTerrainType,
    RendererMode,
    TilesetSourceType,
    UserGlobeView,
)
from atlas.maps.globe.errors import (
    GlobeCameraConversionError,
    GlobeCameraInvalidError,
    GlobeDomainError,
    GlobeGroundIntersectionUnavailableError,
    GlobeImageryLoadFailedError,
    GlobeImageryProviderNotFoundError,
    GlobeImageryProviderRestrictedError,
    GlobeMemoryBudgetExceededError,
    GlobeNotInitializedError,
    GlobeRendererUnavailableError,
    GlobeTerrainLoadFailedError,
    GlobeTerrainProviderNotFoundError,
    GlobeTerrainProviderRestrictedError,
    GlobeTilesetAccessDeniedError,
    GlobeTilesetLicenseRestrictedError,
    GlobeTilesetLoadFailedError,
    GlobeTilesetNotFoundError,
    GlobeViewAccessDeniedError,
    GlobeViewNotFoundError,
    GlobeViewRevisionConflictError,
)
from atlas.maps.globe.interop import cesium_to_maplibre_camera, maplibre_to_cesium_camera
from atlas.maps.globe.providers import AtlasGlobeProviderRegistry
from atlas.maps.globe.service import AtlasGlobeService, globe_service
from atlas.maps.globe.tilesets import AtlasGlobeTilesetRegistry
from atlas.maps.globe.views import AtlasGlobeViewService

__all__ = [
    "AltitudeMode",
    "Atlas3DTilesetSource",
    "AtlasGlobeCamera",
    "AtlasGlobeProviderRegistry",
    "AtlasGlobeService",
    "AtlasGlobeTilesetRegistry",
    "AtlasGlobeViewService",
    "GlobeCameraConversionError",
    "GlobeCameraInvalidError",
    "GlobeDomainError",
    "GlobeGroundIntersectionUnavailableError",
    "GlobeImageryLoadFailedError",
    "GlobeImageryProvider",
    "GlobeImageryProviderNotFoundError",
    "GlobeImageryProviderRestrictedError",
    "GlobeImageryType",
    "GlobeMemoryBudgetExceededError",
    "GlobeNotInitializedError",
    "GlobeRendererUnavailableError",
    "GlobeRuntimeConfig",
    "GlobeTerrainLoadFailedError",
    "GlobeTerrainProvider",
    "GlobeTerrainProviderNotFoundError",
    "GlobeTerrainProviderRestrictedError",
    "GlobeTerrainType",
    "GlobeTilesetAccessDeniedError",
    "GlobeTilesetLicenseRestrictedError",
    "GlobeTilesetLoadFailedError",
    "GlobeTilesetNotFoundError",
    "GlobeViewAccessDeniedError",
    "GlobeViewNotFoundError",
    "GlobeViewRevisionConflictError",
    "RendererMode",
    "TilesetSourceType",
    "UserGlobeView",
    "cartesian_to_geodetic",
    "cesium_to_maplibre_camera",
    "degrees_to_radians",
    "geodetic_to_cartesian",
    "globe_service",
    "maplibre_to_cesium_camera",
    "radians_to_degrees",
    "validate_globe_coordinates",
]

