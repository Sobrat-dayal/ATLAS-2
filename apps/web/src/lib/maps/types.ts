/**
 * Canonical Types and Contracts for ATLAS Maps V1 (Stage 129).
 */

export type DataQualityStatus = "verified" | "provisional" | "approximate" | "uncertain";

export interface GeoBoundingBox {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface MapCameraState {
  longitude: number;
  latitude: number;
  zoom: number;
  bearing: number;
  pitch: number;
  bounds?: [number, number, number, number] | null;
  projection: string;
  revision: number;
}

export interface MapBasemapStyle {
  style_id: string;
  display_name: string;
  provider_id: string;
  style_url: string;
  attribution: string;
  license_reference: string;
  is_dark: boolean;
  is_available: boolean;
  max_zoom: number;
}

export interface MapLayer {
  layer_id: string;
  dataset_id: string;
  layer_name: string;
  geometry_type: string;
  source_type: string;
  default_visibility: boolean;
  default_opacity: number;
  min_zoom: number;
  max_zoom: number;
  display_order: number;
  category: string;
  license_reference: string;
  // Local UI state
  visible?: boolean;
  opacity?: number;
}

export interface MapDataset {
  dataset_id: string;
  dataset_name: string;
  description: string;
  dataset_type: string;
  geometry_types: string[];
  feature_count: number;
  attribution: string;
  licensing_policy: string;
  is_public: boolean;
}

export interface GeoFeatureDetail {
  feature_id: string;
  dataset_id: string;
  label: string;
  geometry_type: string;
  coordinates: any;
  properties: Record<string, any>;
  bounding_box?: [number, number, number, number] | null;
  data_quality: DataQualityStatus;
  source_reference: string;
  dataset_name: string;
  attribution: string;
  licensing_policy: string;
  source_updated_at: string;
}

export interface GeographicSearchResult {
  result_id: string;
  label: string;
  place_type: "country" | "region" | "city" | "financial_center" | "coordinates";
  coordinates: [number, number];
  bounding_box?: [number, number, number, number] | null;
  source_dataset_id: string;
  disambiguation: string;
  relevance_score: number;
}

export interface UserMapView {
  map_view_id: string;
  owner_user_id: string;
  name: string;
  camera: MapCameraState;
  basemap_style_id: string;
  visible_layers: string[];
  layer_configurations: Record<string, Record<string, any>>;
  selected_feature_id?: string | null;
  workspace_id?: string | null;
  tenant_id?: string | null;
  revision: number;
  map_schema_version: string;
  created_at: string;
  updated_at: string;
}

export interface MapConfig {
  default_camera: MapCameraState;
  canonical_crs: string;
  tile_projection: string;
  attribution: string;
  default_style_id: string;
  supported_styles: string[];
  version: string;
}

