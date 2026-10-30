"""Typed Error Taxonomy for ATLAS Maps V1 (Stage 129).

Enforces strict domain errors, zero-trust validation, spatial exception handling,
license adherence, and multi-tenant security boundaries.
"""

from __future__ import annotations


class MapDomainError(Exception):
    """Base error for all geospatial and mapping domain failures."""

    def __init__(self, message: str, code: str = "MAP_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class MapNotInitializedError(MapDomainError):
    def __init__(self, message: str = "Map subsystem or instance is not initialized"):
        super().__init__(message, code="MAP_NOT_INITIALIZED")


class MapStyleNotFoundError(MapDomainError):
    def __init__(self, style_id: str):
        super().__init__(f"Map style '{style_id}' not found", code="MAP_STYLE_NOT_FOUND")
        self.style_id = style_id


class MapStyleUnavailableError(MapDomainError):
    def __init__(self, style_id: str, reason: str = "Provider unavailable"):
        super().__init__(
            f"Map style '{style_id}' unavailable: {reason}", code="MAP_STYLE_UNAVAILABLE"
        )
        self.style_id = style_id


class MapBasemapProviderUnavailableError(MapDomainError):
    def __init__(self, provider_id: str):
        super().__init__(
            f"Basemap provider '{provider_id}' is unavailable",
            code="MAP_BASEMAP_PROVIDER_UNAVAILABLE",
        )
        self.provider_id = provider_id


class MapTileProviderRestrictedError(MapDomainError):
    def __init__(self, layer_id: str, reason: str = "Tile provider licensing or usage restricted"):
        super().__init__(
            f"Tile access restricted for layer '{layer_id}': {reason}",
            code="MAP_TILE_PROVIDER_RESTRICTED",
        )
        self.layer_id = layer_id


class MapTileCoordinatesInvalidError(MapDomainError):
    def __init__(self, z: int, x: int, y: int, reason: str = "Out of valid zoom/coordinate range"):
        super().__init__(
            f"Invalid tile coordinates z={z}, x={x}, y={y}: {reason}",
            code="MAP_TILE_COORDINATES_INVALID",
        )
        self.z = z
        self.x = x
        self.y = y


class MapTileGenerationFailedError(MapDomainError):
    def __init__(self, layer_id: str, reason: str):
        super().__init__(
            f"MVT vector tile generation failed for layer '{layer_id}': {reason}",
            code="MAP_TILE_GENERATION_FAILED",
        )
        self.layer_id = layer_id


class MapLayerNotFoundError(MapDomainError):
    def __init__(self, layer_id: str):
        super().__init__(f"Map layer '{layer_id}' not found", code="MAP_LAYER_NOT_FOUND")
        self.layer_id = layer_id


class MapLayerDisabledError(MapDomainError):
    def __init__(self, layer_id: str):
        super().__init__(f"Map layer '{layer_id}' is currently disabled", code="MAP_LAYER_DISABLED")
        self.layer_id = layer_id


class MapLayerAccessDeniedError(MapDomainError):
    def __init__(self, layer_id: str, tenant_id: str | None = None):
        super().__init__(
            f"Access denied to map layer '{layer_id}' for tenant '{tenant_id}'",
            code="MAP_LAYER_ACCESS_DENIED",
        )
        self.layer_id = layer_id
        self.tenant_id = tenant_id


class MapDatasetNotFoundError(MapDomainError):
    def __init__(self, dataset_id: str):
        super().__init__(
            f"Geographic dataset '{dataset_id}' not found", code="MAP_DATASET_NOT_FOUND"
        )
        self.dataset_id = dataset_id


class MapDatasetAccessDeniedError(MapDomainError):
    def __init__(self, dataset_id: str, user_id: str | None = None):
        super().__init__(
            f"Access denied to dataset '{dataset_id}' for user '{user_id}'",
            code="MAP_DATASET_ACCESS_DENIED",
        )
        self.dataset_id = dataset_id
        self.user_id = user_id


class MapDatasetLicenseRestrictedError(MapDomainError):
    def __init__(self, dataset_id: str, license_type: str):
        super().__init__(
            f"Dataset '{dataset_id}' access restricted under license '{license_type}'",
            code="MAP_DATASET_LICENSE_RESTRICTED",
        )
        self.dataset_id = dataset_id
        self.license_type = license_type


class MapDatasetGeometryInvalidError(MapDomainError):
    def __init__(self, dataset_id: str, reason: str):
        super().__init__(
            f"Invalid geometry in dataset '{dataset_id}': {reason}",
            code="MAP_DATASET_GEOMETRY_INVALID",
        )
        self.dataset_id = dataset_id


class MapGeometrySridInvalidError(MapDomainError):
    def __init__(self, srid: int, expected: int = 4326):
        super().__init__(
            f"Invalid spatial reference identifier (SRID) {srid}, expected {expected}",
            code="MAP_GEOMETRY_SRID_INVALID",
        )
        self.srid = srid
        self.expected = expected


class MapCoordinatesInvalidError(MapDomainError):
    def __init__(self, lon: float, lat: float, reason: str = "Coordinates out of bounds"):
        super().__init__(
            f"Invalid geographic coordinates lon={lon}, lat={lat}: {reason}",
            code="MAP_COORDINATES_INVALID",
        )
        self.lon = lon
        self.lat = lat


class MapBoundsInvalidError(MapDomainError):
    def __init__(self, west: float, south: float, east: float, north: float, reason: str):
        super().__init__(
            f"Invalid bounding box [{west}, {south}, {east}, {north}]: {reason}",
            code="MAP_BOUNDS_INVALID",
        )
        self.west = west
        self.south = south
        self.east = east
        self.north = north


class MapSpatialQueryInvalidError(MapDomainError):
    def __init__(self, reason: str):
        super().__init__(
            f"Spatial query validation failed: {reason}", code="MAP_SPATIAL_QUERY_INVALID"
        )


class MapSpatialQueryTooLargeError(MapDomainError):
    def __init__(self, feature_count: int, max_allowed: int = 5000):
        super().__init__(
            f"Spatial query returned {feature_count} features, exceeding maximum allowed limit of {max_allowed}",
            code="MAP_SPATIAL_QUERY_TOO_LARGE",
        )
        self.feature_count = feature_count
        self.max_allowed = max_allowed


class MapSpatialQueryTimeoutError(MapDomainError):
    def __init__(self, timeout_seconds: float):
        super().__init__(
            f"Spatial query execution timed out after {timeout_seconds} seconds",
            code="MAP_SPATIAL_QUERY_TIMEOUT",
        )


class MapFeatureNotFoundError(MapDomainError):
    def __init__(self, feature_id: str):
        super().__init__(
            f"Geographic feature '{feature_id}' not found", code="MAP_FEATURE_NOT_FOUND"
        )
        self.feature_id = feature_id


class MapFeatureAccessDeniedError(MapDomainError):
    def __init__(self, feature_id: str, user_id: str | None = None):
        super().__init__(
            f"Access denied to feature '{feature_id}' for user '{user_id}'",
            code="MAP_FEATURE_ACCESS_DENIED",
        )
        self.feature_id = feature_id


class MapSearchProviderUnavailableError(MapDomainError):
    def __init__(self, provider: str = "internal"):
        super().__init__(
            f"Geographic search provider '{provider}' is unavailable",
            code="MAP_SEARCH_PROVIDER_UNAVAILABLE",
        )


class MapSearchRateLimitedError(MapDomainError):
    def __init__(self, wait_seconds: int = 60):
        super().__init__(
            f"Geographic search rate limit reached. Retry in {wait_seconds} seconds",
            code="MAP_SEARCH_RATE_LIMITED",
        )
        self.wait_seconds = wait_seconds


class MapViewNotFoundError(MapDomainError):
    def __init__(self, view_id: str):
        super().__init__(f"Saved map view '{view_id}' not found", code="MAP_VIEW_NOT_FOUND")
        self.view_id = view_id


class MapViewAccessDeniedError(MapDomainError):
    def __init__(self, view_id: str, user_id: str | None = None):
        super().__init__(
            f"Access denied to saved map view '{view_id}' for user '{user_id}'",
            code="MAP_VIEW_ACCESS_DENIED",
        )
        self.view_id = view_id


class MapViewRevisionConflictError(MapDomainError):
    def __init__(self, view_id: str, current_rev: int, attempted_rev: int):
        super().__init__(
            f"Revision conflict for saved view '{view_id}': current={current_rev}, attempted={attempted_rev}",
            code="MAP_VIEW_REVISION_CONFLICT",
        )
        self.view_id = view_id
        self.current_rev = current_rev
        self.attempted_rev = attempted_rev


class MapCacheInvalidationFailedError(MapDomainError):
    def __init__(self, key: str, reason: str):
        super().__init__(
            f"Failed to invalidate map cache for key '{key}': {reason}",
            code="MAP_CACHE_INVALIDATION_FAILED",
        )


class MapWebGLUnavailableError(MapDomainError):
    def __init__(self, message: str = "WebGL rendering context is unavailable in this environment"):
        super().__init__(message, code="MAP_WEBGL_UNAVAILABLE")


class MapInternalError(MapDomainError):
    def __init__(self, message: str = "Internal geospatial engine error"):
        super().__init__(message, code="MAP_INTERNAL_ERROR")
