/**
 * Type definitions for ATLAS Market Heatmaps V1 (Stage 64).
 */

export type HeatmapVisualizationMode = "equal_size" | "market_cap_weighted";

export type HeatmapHierarchyMode = "none" | "sector" | "industry";

export type HeatmapComparisonWindow =
  | "previous_regular_session"
  | "rolling_24h"
  | "previous_session_settlement";

export type HeatmapCoverageStatus =
  | "COMPLETE_FOR_DEFINED_UNIVERSE"
  | "PARTIAL_COVERAGE"
  | "DEGRADED"
  | "UNAVAILABLE";

export type HeatmapExclusionReason =
  | "NO_CURRENT_QUOTE"
  | "NO_REFERENCE"
  | "MISSING_WEIGHT"
  | "INVALID_WEIGHT"
  | "STALE_OBSERVATION"
  | "INCOMPATIBLE_WINDOW"
  | "INVALID_DENOMINATOR"
  | "INACTIVE_SECURITY"
  | "NOT_ENTITLED"
  | "DATA_SOURCE_UNAVAILABLE";

export interface HeatmapUniverseDefinition {
  universe_id: string;
  display_name: string;
  asset_class: string;
  market_scope: string;
  exchange_scope: string[];
  supported_modes: HeatmapVisualizationMode[];
  supported_hierarchies: HeatmapHierarchyMode[];
  supported_windows: HeatmapComparisonWindow[];
  default_window: HeatmapComparisonWindow;
  default_mode: HeatmapVisualizationMode;
  default_hierarchy: HeatmapHierarchyMode;
  weight_metric_label?: string | null;
  weight_unit?: string | null;
  taxonomy?: string | null;
  is_active: boolean;
}

export interface HeatmapLeafNode {
  node_id: string;
  node_kind: "instrument";
  instrument_entity_id: string;
  market_series_identity: string;
  symbol: string;
  display_name: string;
  asset_class: string;
  exchange_or_venue: string;
  sector?: string | null;
  industry?: string | null;
  current_price?: number | string | null;
  reference_price?: number | string | null;
  percent_change?: number | string | null;
  absolute_change?: number | string | null;
  weight_value?: number | string | null;
  weight_unit?: string | null;
  normalized_weight?: number | string | null;
  currency: string;
  freshness_status: string;
  delay_status: string;
  delivery_delay_seconds?: number | null;
  provider: string;
  source_timestamp?: string | null;
  reference_timestamp?: string | null;
  reference_period_label?: string | null;
  is_qualified: boolean;
  exclusion_reason?: HeatmapExclusionReason | null;
}

export interface HeatmapGroupNode {
  group_id: string;
  group_kind: "sector" | "industry";
  label: string;
  taxonomy: string;
  constituent_count: number;
  qualified_count: number;
  aggregate_return?: number | string | null;
  aggregate_method: string;
  total_weight?: number | string | null;
  normalized_weight?: number | string | null;
  children: HeatmapLeafNode[];
}

export interface HeatmapCoverage {
  universe_size: number;
  candidate_count: number;
  qualified_count: number;
  missing_returns: number;
  missing_weights: number;
  unclassified_count: number;
  coverage_status: HeatmapCoverageStatus;
  total_qualified_weight?: number | string | null;
  exclusion_breakdown: Record<string, number>;
}

export interface MarketHeatmapResponse {
  schema_version: string;
  snapshot_id: string;
  universe_id: string;
  universe_name: string;
  asset_class: string;
  comparison_window: HeatmapComparisonWindow;
  visualization_mode: HeatmapVisualizationMode;
  hierarchy_mode: HeatmapHierarchyMode;
  calculated_at: string;
  weight_metric_label?: string | null;
  weight_unit?: string | null;
  color_domain_min: number | string;
  color_domain_max: number | string;
  coverage: HeatmapCoverage;
  nodes: HeatmapLeafNode[];
  groups: HeatmapGroupNode[];
  notes?: string | null;
}

export interface HeatmapUniverseResponse {
  universes: HeatmapUniverseDefinition[];
  count: number;
}

export interface HeatmapOptionsResponse {
  modes: HeatmapVisualizationMode[];
  hierarchies: HeatmapHierarchyMode[];
  windows: HeatmapComparisonWindow[];
  taxonomies: string[];
}
