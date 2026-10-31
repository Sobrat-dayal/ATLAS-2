/**
 * ATLAS Spatial Analytics and H3 Engine TypeScript Types (Stage 131).
 */

export type SpatialVisualizationType = 'scatterplot' | 'h3_hexagon' | 'heatmap' | 'hexagon_grid';

export type SpatialAggregationMethod = 'count' | 'sum' | 'mean' | 'weighted_mean' | 'distinct_count' | 'density';

export type NullValuePolicy = 'exclude' | 'zero' | 'warn';

export type TimeBucketInterval = '1h' | '1d' | '1w' | '1m' | '1q' | '1y';

export type ColorPalette = 'viridis' | 'magma' | 'blues' | 'turbo' | 'cividis' | 'spectral';

export interface SpatialMetricDefinition {
  metric_id: string;
  dataset_id: string;
  display_name: string;
  description: string;
  unit: string;
  value_type: 'integer' | 'float' | 'currency' | 'percentage';
  allowed_aggregations: SpatialAggregationMethod[];
  default_aggregation: SpatialAggregationMethod;
  currency?: string;
  null_policy: NullValuePolicy;
  minimum_contributor_threshold: number;
  is_temporal: boolean;
}

export interface AtlasH3Aggregate {
  h3_cell_id: string;
  h3_resolution: number;
  metric_id: string;
  aggregation_method: SpatialAggregationMethod;
  value: number | null;
  record_count: number;
  non_null_count: number;
  distinct_count?: number | null;
  valid_weight_sum?: number | null;
  cell_area_km2: number;
  density?: number | null;
  unit: string;
  is_suppressed: boolean;
  time_bucket?: string | null;
  data_quality: string;
}

export interface SpatialSummaryStatistics {
  total_records: number;
  total_cells: number;
  suppressed_cells: number;
  sum_value: number;
  mean_value: number;
  min_value: number;
  max_value: number;
  weighted_mean?: number | null;
  unit: string;
}

export interface SpatialAnalyticsQuery {
  dataset_id: string;
  metric_id: string;
  aggregation: SpatialAggregationMethod;
  visualization_type: SpatialVisualizationType;
  h3_resolution: number;
  bounds?: [number, number, number, number]; // [west, south, east, north]
  filters?: Record<string, unknown>;
  time_range_start?: string;
  time_range_end?: string;
  time_bucket?: TimeBucketInterval;
  historical_as_of?: string;
  min_contributors?: number;
  result_limit?: number;
}

export interface SpatialAnalyticsResult {
  query_id: string;
  dataset_id: string;
  dataset_version: string;
  metric_id: string;
  aggregation: SpatialAggregationMethod;
  visualization_type: SpatialVisualizationType;
  h3_resolution: number;
  unit: string;
  aggregates: AtlasH3Aggregate[];
  summary: SpatialSummaryStatistics;
  bounds?: [number, number, number, number] | null;
  time_scope?: { bucket?: string } | null;
  data_quality: string;
  source_attribution: string;
  licensing_policy: string;
  is_truncated: boolean;
  execution_time_ms: number;
  computed_at: string;
}

export interface RegionComparisonResult {
  region_a_name: string;
  region_b_name: string;
  metric_id: string;
  unit: string;
  region_a_summary: SpatialSummaryStatistics;
  region_b_summary: SpatialSummaryStatistics;
  absolute_difference: number;
  relative_difference_pct?: number | null;
  higher_region?: string | null;
  area_normalized_a: number;
  area_normalized_b: number;
}

export interface CellDetailsResponse {
  h3_cell_id: string;
  resolution: number;
  cell_area_km2: number;
  centroid: { latitude: number; longitude: number };
  is_pentagon: boolean;
  supported_drill_down: boolean;
}

export interface ColorScaleConfig {
  palette: ColorPalette;
  min: number;
  max: number;
  steps?: number;
  isLogarithmic?: boolean;
}

