/**
 * TypeScript types for Watchlist Columns and Preferences (Stage 77).
 */

export type WatchlistColumnCategory = "identity" | "market" | "quote" | "quality";

export type WatchlistColumnValueType =
  | "TEXT"
  | "IDENTIFIER"
  | "ENUM"
  | "MONETARY"
  | "PERCENTAGE"
  | "TIMESTAMP"
  | "STATUS";

export type ColumnSortPolicy = "alpha" | "numeric" | "chronological" | "none";

export interface WatchlistColumnDefinition {
  id: string;
  version: number;
  label: string;
  description: string;
  category: WatchlistColumnCategory;
  value_type: WatchlistColumnValueType;
  source_capability: string;
  supported_asset_classes: string[];
  formatter_id: string;
  sort_policy: ColumnSortPolicy;
  default_visible: boolean;
  default_width: number;
  min_width: number;
  max_width: number;
  can_hide: boolean;
  can_resize: boolean;
  can_pin: boolean;
  can_sort: boolean;
}

export interface WatchlistColumnSortConfig {
  column_id: string | null;
  direction: "asc" | "desc" | null;
}

export interface WatchlistColumnConfigV1 {
  schema_version: number;
  ordered_column_ids: string[];
  visible_column_ids: string[];
  widths: Record<string, number>;
  pinned_left_column_ids: string[];
  sort: WatchlistColumnSortConfig;
}

export interface WatchlistColumnPreferencesResponse {
  watchlist_id: string;
  configuration_schema_version: number;
  revision: number;
  configuration: WatchlistColumnConfigV1;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface WatchlistColumnPreferencesUpdateRequest {
  configuration: WatchlistColumnConfigV1;
  expected_revision?: number;
}

export interface WatchlistRowCellValue {
  status: "AVAILABLE" | "UNAVAILABLE" | "NOT_APPLICABLE" | "NOT_ENTITLED" | "STALE";
  value?: unknown;
  unit?: string | null;
  measure_kind?: string | null;
  observed_at?: string | null;
  source?: string | null;
  freshness?: string | null;
  reason?: string | null;
}

export interface WatchlistRowProjection {
  item_id: string;
  instrument_entity_id: string;
  market_series_id: string;
  manual_position: number;
  values: Record<string, WatchlistRowCellValue>;
  has_company_page: boolean;
  issuer_id?: string | null;
}

export interface WatchlistRowsResponse {
  watchlist_id: string;
  membership_revision: number;
  selected_columns: string[];
  total_items: number;
  page: number;
  page_size: number;
  rows: WatchlistRowProjection[];
  is_sorted: boolean;
  sort_column_id?: string | null;
  sort_direction?: string | null;
  incompatible_units_detected: boolean;
}
