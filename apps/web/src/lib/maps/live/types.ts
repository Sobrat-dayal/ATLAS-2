/**
 * ATLAS Maps Live Physical-World TypeScript Types (Stage 134).
 */

export type LiveObservationCategory =
  | "AIRCRAFT"
  | "VESSEL"
  | "SATELLITE"
  | "WEATHER_OBSERVATION"
  | "WEATHER_FORECAST"
  | "WEATHER_ALERT"
  | "EARTHQUAKE"
  | "ACTIVE_FIRE"
  | "NATURAL_EVENT";

export type FreshnessState =
  | "CURRENT"
  | "DELAYED"
  | "STALE"
  | "EXPIRED"
  | "HISTORICAL"
  | "SOURCE_UNAVAILABLE";

export type ObservationDataClass =
  | "OBSERVED"
  | "PROPAGATED"
  | "FORECAST"
  | "REFERENCE";

export type ProviderStatus =
  | "ONLINE"
  | "DEGRADED"
  | "OFFLINE"
  | "UNCONFIGURED"
  | "ACCESS_RESTRICTED";

export interface LiveGeoProvider {
  provider_id: string;
  name: string;
  category: LiveObservationCategory;
  status: ProviderStatus;
  configured: boolean;
  requires_auth: boolean;
  nominal_latency_seconds: number;
  ttl_seconds: number;
  last_sync_at?: string;
  rate_limit_remaining?: number;
  attribution: string;
  license_note: string;
  endpoint_url?: string;
  status_reason?: string;
}

export interface AtlasGeoObservation {
  observation_id: string;
  category: LiveObservationCategory;
  data_class: ObservationDataClass;
  entity_id: string;
  entity_name?: string;
  provider_id: string;
  product_id: string;
  source_revision: number;
  longitude: number;
  latitude: number;
  altitude_m?: number;
  heading_deg?: number;
  speed_mps?: number;
  vertical_rate_mps?: number;
  geometry: {
    type: string;
    coordinates: any;
  };
  observed_at: string;
  source_published_at?: string;
  received_at: string;
  ingested_at: string;
  freshness_state: FreshnessState;
  freshness_age_seconds: number;
  properties: Record<string, any>;
  source_attribution: string;
  provenance_note?: string;
  sequence_number: number;
}

export interface SatelliteState {
  norad_cat_id: number;
  name: string;
  propagated_at_utc: string;
  epoch_utc: string;
  epoch_age_days: number;
  is_stale_epoch: boolean;
  subpoint_latitude: number;
  subpoint_longitude: number;
  altitude_km: number;
  velocity_km_s: number;
  footprint_radius_km: number;
  data_class: ObservationDataClass;
  provenance_note: string;
}

export interface TrajectorySegment {
  entity_id: string;
  category: LiveObservationCategory;
  segment_id: string;
  start_time: string;
  end_time: string;
  point_count: number;
  coordinates: [number, number, number][];
  timestamps: string[];
  has_gap_break: boolean;
  gap_reason?: string;
}

export interface InfrastructureProximityMatch {
  facility_id: string;
  facility_name: string;
  facility_sector: string;
  facility_coordinates: [number, number];
  observation_id: string;
  observation_category: LiveObservationCategory;
  event_entity_id: string;
  distance_km: number;
  inside_alert_perimeter: boolean;
  severity?: string;
  damage_assessment: string;
  damage_confirmed: boolean;
  disclaimer: string;
}

export interface LivePlaybackState {
  mode: "LIVE" | "PAUSED" | "HISTORICAL";
  playbackTimeUtc: string;
  speedMultiplier: number; // 1, 5, 10, 60
  windowSeconds: number;
}

