"""Typed Error Taxonomy for ATLAS 3D God's Eye Globe (Stage 130).

Enforces strict domain errors, zero-trust validation, 3D coordinate mathematics,
license adherence, and multi-tenant security boundaries.
"""

from __future__ import annotations

from atlas.maps.errors import MapDomainError


class GlobeDomainError(MapDomainError):
    """Base error for all 3D globe geospatial and rendering domain failures."""

    def __init__(self, message: str, code: str = "GLOBE_ERROR"):
        super().__init__(message, code=code)


class GlobeNotInitializedError(GlobeDomainError):
    def __init__(self, message: str = "Cesium 3D Globe subsystem or viewer is not initialized"):
        super().__init__(message, code="GLOBE_NOT_INITIALIZED")


class GlobeRendererUnavailableError(GlobeDomainError):
    def __init__(self, reason: str = "WebGL context could not be created or was lost"):
        super().__init__(
            f"3D Globe renderer unavailable: {reason}",
            code="GLOBE_RENDERER_UNAVAILABLE",
        )
        self.reason = reason


class GlobeCameraInvalidError(GlobeDomainError):
    def __init__(self, reason: str = "Camera parameters outside valid domain"):
        super().__init__(
            f"Invalid 3D globe camera state: {reason}",
            code="GLOBE_CAMERA_INVALID",
        )
        self.reason = reason


class GlobeCameraConversionError(GlobeDomainError):
    def __init__(self, reason: str = "Conversion between 2D and 3D camera failed"):
        super().__init__(
            f"Camera interoperability conversion failed: {reason}",
            code="GLOBE_CAMERA_CONVERSION_FAILED",
        )
        self.reason = reason


class GlobeImageryProviderNotFoundError(GlobeDomainError):
    def __init__(self, provider_id: str):
        super().__init__(
            f"Globe imagery provider '{provider_id}' not found in registry",
            code="GLOBE_IMAGERY_PROVIDER_NOT_FOUND",
        )
        self.provider_id = provider_id


class GlobeImageryProviderRestrictedError(GlobeDomainError):
    def __init__(self, provider_id: str, reason: str = "Tenant not entitled or license expired"):
        super().__init__(
            f"Access to imagery provider '{provider_id}' is restricted: {reason}",
            code="GLOBE_IMAGERY_PROVIDER_RESTRICTED",
        )
        self.provider_id = provider_id
        self.reason = reason


class GlobeImageryLoadFailedError(GlobeDomainError):
    def __init__(self, provider_id: str, reason: str = "Network timeout or tile error"):
        super().__init__(
            f"Failed to load imagery provider '{provider_id}': {reason}",
            code="GLOBE_IMAGERY_LOAD_FAILED",
        )
        self.provider_id = provider_id
        self.reason = reason


class GlobeTerrainProviderNotFoundError(GlobeDomainError):
    def __init__(self, provider_id: str):
        super().__init__(
            f"Globe terrain provider '{provider_id}' not found in registry",
            code="GLOBE_TERRAIN_PROVIDER_NOT_FOUND",
        )
        self.provider_id = provider_id


class GlobeTerrainProviderRestrictedError(GlobeDomainError):
    def __init__(self, provider_id: str, reason: str = "Terrain token missing or unauthorized"):
        super().__init__(
            f"Access to terrain provider '{provider_id}' is restricted: {reason}",
            code="GLOBE_TERRAIN_PROVIDER_RESTRICTED",
        )
        self.provider_id = provider_id
        self.reason = reason


class GlobeTerrainLoadFailedError(GlobeDomainError):
    def __init__(self, provider_id: str, reason: str = "Terrain provider failed or timed out"):
        super().__init__(
            f"Failed to load terrain provider '{provider_id}': {reason}",
            code="GLOBE_TERRAIN_LOAD_FAILED",
        )
        self.provider_id = provider_id
        self.reason = reason


class GlobeTilesetNotFoundError(GlobeDomainError):
    def __init__(self, tileset_id: str):
        super().__init__(
            f"3D Tileset '{tileset_id}' not found in registry",
            code="GLOBE_TILESET_NOT_FOUND",
        )
        self.tileset_id = tileset_id


class GlobeTilesetAccessDeniedError(GlobeDomainError):
    def __init__(self, tileset_id: str, tenant_id: str):
        super().__init__(
            f"Access denied to 3D Tileset '{tileset_id}' for tenant '{tenant_id}'",
            code="GLOBE_TILESET_ACCESS_DENIED",
        )
        self.tileset_id = tileset_id
        self.tenant_id = tenant_id


class GlobeTilesetLicenseRestrictedError(GlobeDomainError):
    def __init__(self, tileset_id: str, reason: str = "Commercial license required"):
        super().__init__(
            f"3D Tileset '{tileset_id}' licensing restriction: {reason}",
            code="GLOBE_TILESET_LICENSE_RESTRICTED",
        )
        self.tileset_id = tileset_id
        self.reason = reason


class GlobeTilesetLoadFailedError(GlobeDomainError):
    def __init__(self, tileset_id: str, reason: str = "Malformed tileset.json or unreachable URI"):
        super().__init__(
            f"Failed to load 3D Tileset '{tileset_id}': {reason}",
            code="GLOBE_TILESET_LOAD_FAILED",
        )
        self.tileset_id = tileset_id
        self.reason = reason


class GlobeLayerUnsupportedError(GlobeDomainError):
    def __init__(self, layer_id: str, mode: str = "3D"):
        super().__init__(
            f"Layer '{layer_id}' does not support rendering in {mode} mode",
            code="GLOBE_LAYER_UNSUPPORTED",
        )
        self.layer_id = layer_id
        self.mode = mode


class GlobeGroundIntersectionUnavailableError(GlobeDomainError):
    def __init__(
        self, reason: str = "Viewing ray points into sky/space without Earth surface intersection"
    ):
        super().__init__(
            f"Ground intersection unavailable: {reason}",
            code="GLOBE_GROUND_INTERSECTION_UNAVAILABLE",
        )
        self.reason = reason


class GlobeViewNotFoundError(GlobeDomainError):
    def __init__(self, view_id: str):
        super().__init__(
            f"Saved globe view '{view_id}' not found",
            code="GLOBE_VIEW_NOT_FOUND",
        )
        self.view_id = view_id


class GlobeViewAccessDeniedError(GlobeDomainError):
    def __init__(self, view_id: str, user_id: str):
        super().__init__(
            f"Access denied to saved globe view '{view_id}' for user '{user_id}'",
            code="GLOBE_VIEW_ACCESS_DENIED",
        )
        self.view_id = view_id
        self.user_id = user_id


class GlobeViewRevisionConflictError(GlobeDomainError):
    def __init__(self, view_id: str, expected_rev: int, current_rev: int):
        super().__init__(
            f"Conflict updating globe view '{view_id}': expected revision {expected_rev}, got {current_rev}",
            code="GLOBE_VIEW_REVISION_CONFLICT",
        )
        self.view_id = view_id
        self.expected_rev = expected_rev
        self.current_rev = current_rev


class GlobeMemoryBudgetExceededError(GlobeDomainError):
    def __init__(self, current_mb: float, limit_mb: float):
        super().__init__(
            f"Globe GPU/tile memory budget exceeded: {current_mb:.1f}MB exceeds limit of {limit_mb:.1f}MB",
            code="GLOBE_MEMORY_BUDGET_EXCEEDED",
        )
        self.current_mb = current_mb
        self.limit_mb = limit_mb
