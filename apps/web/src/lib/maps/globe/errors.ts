/**
 * Error Taxonomy and User-Facing Formatter for ATLAS 3D Globe (Stage 130).
 */

export const GLOBE_ERROR_CODES = {
  NOT_INITIALIZED: "GLOBE_NOT_INITIALIZED",
  RENDERER_UNAVAILABLE: "GLOBE_RENDERER_UNAVAILABLE",
  WEBGL_UNSUPPORTED: "GLOBE_WEBGL_UNSUPPORTED",
  CONTEXT_LOST: "GLOBE_CONTEXT_LOST",
  IMAGERY_PROVIDER_NOT_FOUND: "GLOBE_IMAGERY_PROVIDER_NOT_FOUND",
  IMAGERY_PROVIDER_RESTRICTED: "GLOBE_IMAGERY_PROVIDER_RESTRICTED",
  TERRAIN_PROVIDER_RESTRICTED: "GLOBE_TERRAIN_PROVIDER_RESTRICTED",
  CAMERA_INVALID: "GLOBE_CAMERA_INVALID",
  TILESET_NOT_FOUND: "GLOBE_TILESET_NOT_FOUND",
  TILESET_ACCESS_DENIED: "GLOBE_TILESET_ACCESS_DENIED",
  VIEW_REVISION_CONFLICT: "GLOBE_VIEW_REVISION_CONFLICT",
} as const;

export function formatGlobeErrorMessage(errorCode: string, defaultMessage?: string): string {
  switch (errorCode) {
    case GLOBE_ERROR_CODES.WEBGL_UNSUPPORTED:
    case GLOBE_ERROR_CODES.RENDERER_UNAVAILABLE:
      return "WebGL 3D graphics hardware acceleration is unavailable in your browser or device.";
    case GLOBE_ERROR_CODES.CONTEXT_LOST:
      return "WebGL graphics context was lost due to GPU memory constraints or driver reset. Reloading...";
    case GLOBE_ERROR_CODES.IMAGERY_PROVIDER_RESTRICTED:
      return "Access to this imagery layer is restricted by institutional licensing policies.";
    case GLOBE_ERROR_CODES.TERRAIN_PROVIDER_RESTRICTED:
      return "Cesium World Terrain requires a valid CESIUM_ION_TOKEN. Using standard WGS84 Ellipsoid.";
    case GLOBE_ERROR_CODES.TILESET_ACCESS_DENIED:
      return "Access denied: this 3D Tileset is private to another tenant.";
    case GLOBE_ERROR_CODES.VIEW_REVISION_CONFLICT:
      return "Conflict: this globe view was modified in another session. Please reload to see the latest version.";
    case GLOBE_ERROR_CODES.CAMERA_INVALID:
      return "Invalid camera parameters specified.";
    default:
      return defaultMessage || "An unexpected geospatial error occurred.";
  }
}
