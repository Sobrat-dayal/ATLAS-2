/**
 * Typed Definitions for ATLAS 3D God's Eye Globe (Stage 130).
 *
 * Enforces canonical 3D camera states, geodetic representations,
 * imagery/terrain provider registries, and OGC 3D Tileset schemas.
 */

export type RendererMode = "2D" | "3D";

export type GlobeImageryType =
  | "NATURAL_EARTH"
  | "SATELLITE"
  | "OPEN_STREET_MAP"
  | "CARTOGRAPHIC_DARK"
  | "CARTOGRAPHIC_LIGHT";

export type GlobeTerrainType = "ELLIPSOID" | "CESIUM_WORLD_TERRAIN" | "LICENSED_TERRAIN";

export type TilesetSourceType = "OGC_3D_TILES";

export type AltitudeMode =
  | "ABSOLUTE_ELLIPSOID_HEIGHT"
  | "RELATIVE_TO_TERRAIN"
  | "CLAMP_TO_TERRAIN";

export type GlobeQualityProfile = "low" | "balanced" | "high";

export type GlobeStatus = "INITIALIZING" | "READY" | "WEBGL_UNAVAILABLE" | "ERROR";

export interface AtlasGlobeCamera {
  longitude: number; // [-180, 180]
  latitude: number; // [-90, 90]
  height_meters: number; // positive float
  heading_radians: number; // [0, 2pi)
  pitch_radians: number; // [-pi/2, pi/2] (-pi/2 is nadir)
  roll_radians: number; // [0, 2pi)
  scene_mode?: string;
  camera_schema_version?: string;
}

export interface GlobeImageryProvider {
  provider_id: string;
  name: string;
  imagery_type: GlobeImageryType;
  source_url: string;
  attribution: string;
  licensing_policy: string;
  is_available: boolean;
  is_default: boolean;
  max_zoom: number;
  description: string;
}

export interface GlobeTerrainProvider {
  provider_id: string;
  name: string;
  terrain_type: GlobeTerrainType;
  attribution: string;
  source_url_optional?: string | null;
  is_available: boolean;
  is_default: boolean;
  has_measured_elevation: boolean;
  description: string;
}

export interface Atlas3DTilesetSource {
  tileset_id: string;
  dataset_id: string;
  source_type: TilesetSourceType;
  source_reference: string;
  bounding_volume: Record<string, unknown>;
  attribution: string;
  licensing_policy: string;
  tenant_id?: string | null;
  is_available: boolean;
  data_quality: string;
  description: string;
}

export interface UserGlobeView {
  view_id: string;
  tenant_id: string;
  owner_user_id: string;
  name: string;
  description: string;
  renderer_mode: RendererMode;
  cesium_camera: AtlasGlobeCamera;
  maplibre_camera?: {
    center: [number, number];
    zoom: number;
    pitch: number;
    bearing: number;
  } | null;
  imagery_provider_id: string;
  terrain_provider_id: string;
  visible_layer_references: string[];
  selected_feature_id?: string | null;
  quality_profile: GlobeQualityProfile;
  revision: number;
  created_at: string;
  updated_at: string;
}

export interface GlobeRuntimeConfig {
  default_imagery_provider_id: string;
  default_terrain_provider_id: string;
  ion_configured: boolean;
  supported_modes: string[];
  max_active_viewers: number;
  default_camera: AtlasGlobeCamera;
}

