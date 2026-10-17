/**
 * Type definitions for ATLAS Market Movers V1 (Stage 63).
 */

export type MoverCategory = "gainers" | "losers" | "most_active";

export type MoverAssetClass = "equity" | "crypto" | "futures" | "fx" | "bond";

export type ComparisonWindow =
  | "previous_regular_session"
  | "rolling_24h"
  | "current_session"
  | "previous_session_settlement";

export type CoverageStatus =
  | "COMPLETE_FOR_DEFINED_UNIVERSE"
  | "PARTIAL_COVERAGE"
  | "DEGRADED"
  | "UNAVAILABLE";

export type ExclusionReason =
  | "NO_CURRENT_QUOTE"
  | "NO_REFERENCE"
  | "STALE_CURRENT"
  | "UNKNOWN_FRESHNESS"
  | "INCOMPATIBLE_SERIES"
  | "INCOMPATIBLE_UNIT"
  | "INCOMPATIBLE_WINDOW"
  | "UNVERIFIED_ADJUSTMENT"
  | "INVALID_DENOMINATOR"
  | "MISSING_VOLUME"
  | "INVALID_ACTIVITY_SCOPE"
  | "INSTRUMENT_INACTIVE"
  | "NOT_ENTITLED"
  | "DATA_SOURCE_UNAVAILABLE"
  | "OTHER";

export interface MoverUniverseDefinition {
  universe_id: string;
  display_name: string;
  asset_class: MoverAssetClass;
  instrument_types: string[];
  market_scope: string;
  exchange_scope: string[];
  listing_currency_scope: string[];
  eligibility_policy: string;
  metric_policy: string;
  data_entitlement_policy: string;
  supported_categories: MoverCategory[];
  supported_windows: ComparisonWindow[];
  default_window: ComparisonWindow;
  activity_unit?: string | null;
  activity_metric_label?: string | null;
  is_active: boolean;
}

export interface MoverMetricDefinition {
  metric_id: string;
  metric_kind: MoverCategory;
  asset_class: MoverAssetClass;
  observation_basis: string;
  reference_basis: string;
  window: ComparisonWindow;
  unit: string;
  sort_direction: "DESC" | "ASC";
  qualification_policy: string;
}

export interface MoverRankedItem {
  rank: number;
  instrument_entity_id: string;
  market_series_identity: string;
  display_name: string;
  symbol: string;
  asset_class: MoverAssetClass;
  exchange_or_venue: string;
  ranking_value: string | number;
  ranking_unit: string;
  current_observation?: string | number | null;
  reference_observation?: string | number | null;
  absolute_change?: string | number | null;
  percent_change?: string | number | null;
  activity_observation?: string | number | null;
  activity_unit?: string | null;
  source_timestamp?: string | null;
  reference_timestamp?: string | null;
  reference_period_label?: string | null;
  provider: string;
  freshness_status: string;
  delay_status: string;
  delivery_delay_seconds?: number | null;
  eligibility_notes?: string | null;
}

export interface MoverCoverage {
  universe_size: number;
  candidate_count: number;
  evaluated_count: number;
  qualified_count: number;
  excluded_count: number;
  exclusion_reasons: Record<string, number>;
  coverage_status: CoverageStatus;
  ranking_as_of: string;
}

export interface MarketMoverResponse {
  schema_version: string;
  snapshot_id: string;
  universe_id: string;
  universe_display_name: string;
  category: MoverCategory;
  metric_id: string;
  window: ComparisonWindow;
  asset_class: MoverAssetClass;
  calculated_at: string;
  coverage: MoverCoverage;
  items: MoverRankedItem[];
  next_cursor?: string | null;
  has_more: boolean;
  source_status: string;
}

export interface MoverUniverseResponse {
  schema_version: string;
  universes: MoverUniverseDefinition[];
  default_universe_id: string;
}

export interface MoverMetricOptionsResponse {
  schema_version: string;
  universe_id: string;
  asset_class: MoverAssetClass;
  supported_categories: MoverCategory[];
  supported_windows: ComparisonWindow[];
  activity_metric_label?: string | null;
  activity_unit?: string | null;
  metrics: MoverMetricDefinition[];
}

export interface MarketMoversQueryParams {
  universe_id?: string;
  category?: MoverCategory;
  window?: ComparisonWindow;
  exchange?: string;
  limit?: number;
  cursor?: string | null;
}
