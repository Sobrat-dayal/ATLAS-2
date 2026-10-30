/**
 * Typed Error Codes and User Messages for ATLAS Maps V1.
 */

export const MAP_ERROR_MESSAGES: Record<string, string> = {
  MAP_NOT_INITIALIZED: "Map renderer engine is initializing.",
  MAP_STYLE_NOT_FOUND: "Selected map style was not found.",
  MAP_STYLE_UNAVAILABLE: "Selected basemap style is currently unavailable.",
  MAP_BASEMAP_PROVIDER_UNAVAILABLE: "Basemap provider service is unreachable.",
  MAP_TILE_PROVIDER_RESTRICTED: "Map tile access is restricted by data licensing.",
  MAP_TILE_COORDINATES_INVALID: "Requested vector tile coordinates are out of bounds.",
  MAP_LAYER_NOT_FOUND: "Requested geospatial layer could not be found.",
  MAP_LAYER_DISABLED: "This layer is currently disabled in your view.",
  MAP_LAYER_ACCESS_DENIED: "You do not have permission to view this spatial layer.",
  MAP_DATASET_ACCESS_DENIED: "Access to this proprietary spatial dataset is denied.",
  MAP_COORDINATES_INVALID: "Invalid geographic coordinates provided.",
  MAP_BOUNDS_INVALID: "Invalid bounding box range.",
  MAP_SPATIAL_QUERY_TOO_LARGE: "Spatial query returned too many features. Please zoom in.",
  MAP_FEATURE_NOT_FOUND: "Geographic feature was not found.",
  MAP_VIEW_REVISION_CONFLICT: "Map view has been modified by another session. Please refresh.",
  MAP_WEBGL_UNAVAILABLE: "WebGL 2D hardware acceleration is unavailable in your browser.",
};

export function getMapErrorMessage(code: string): string {
  return MAP_ERROR_MESSAGES[code] || "An unexpected geospatial error occurred.";
}

