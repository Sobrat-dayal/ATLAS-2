/**
 * TypeScript types and DTO definitions for Stage 119 - Universal Saved System.
 */

export type SavedTargetType =
  | "INSTRUMENT"
  | "COMPANY"
  | "CHART_CONFIG"
  | "SCREENER_CONFIG"
  | "WATCHLIST_REFERENCE"
  | "ECONOMIC_SERIES"
  | "NEWS_ARTICLE"
  | "RESEARCH_INVESTIGATION"
  | "RESEARCH_DOCUMENT"
  | "RESEARCH_REPORT"
  | "RESEARCH_ANALYSIS_RUN"
  | "PORTFOLIO_REFERENCE"
  | "PORTFOLIO_VIEW_CONFIG"
  | "PORTFOLIO_ANALYSIS_RUN"
  | "RISK_RUN"
  | "RISK_SCENARIO"
  | "MARKET_VIEW_CONFIG"
  | "MAP_VIEW_CONFIG"
  | "DATA_RESOURCE"
  | "AI_ARTIFACT"
  | "INTELLIGENCE_ARTIFACT"
  | "OTHER_REGISTERED_RESOURCE";

export type SavedModule =
  | "home"
  | "markets"
  | "charts"
  | "watchlists"
  | "screeners"
  | "companies"
  | "economics"
  | "news"
  | "research"
  | "maps"
  | "intelligence"
  | "options"
  | "trading"
  | "portfolios"
  | "risk"
  | "ai"
  | "data"
  | "saved"
  | "workspaces"
  | "agents";

export type ResourceAvailabilityStatus =
  | "AVAILABLE"
  | "AVAILABLE_WITH_WARNINGS"
  | "TARGET_UPDATED"
  | "TARGET_SUPERSEDED"
  | "TARGET_DELETED"
  | "TARGET_NOT_FOUND"
  | "PERMISSION_REVOKED"
  | "SOURCE_RESTRICTED"
  | "UNSUPPORTED_CONFIG_VERSION"
  | "RESOURCE_UNAVAILABLE";

export type SavedReferenceSemantics =
  | "LIVE_REFERENCE"
  | "IMMUTABLE_RUN_REFERENCE"
  | "USER_OWNED_VIEW_CONFIGURATION";

export type SavedSortOption =
  | "RECENTLY_SAVED"
  | "RECENTLY_UPDATED"
  | "NAME_ASC"
  | "NAME_DESC"
  | "RESOURCE_TYPE"
  | "CUSTOM_ORDER";

export type SavedBulkActionType =
  | "FAVORITE"
  | "UNFAVORITE"
  | "PIN"
  | "UNPIN"
  | "ADD_TO_COLLECTION"
  | "REMOVE_FROM_COLLECTION"
  | "ADD_TAG"
  | "REMOVE_TAG"
  | "DELETE"
  | "RESTORE";

export type ViewConfigurationType =
  | "CHART"
  | "SCREENER"
  | "ECONOMICS"
  | "PORTFOLIO"
  | "RISK"
  | "MAP"
  | "DATA_QUERY";

export interface SavedItem {
  saved_item_id: string;
  owner_user_id: string;
  organization_id?: string | null;
  target_type: SavedTargetType;
  target_id: string;
  target_revision_id?: string | null;
  target_module: SavedModule;
  canonical_title: string;
  display_title: string;
  user_note?: string | null;
  favorite: boolean;
  pinned: boolean;
  view_configuration_id?: string | null;
  semantics: SavedReferenceSemantics;
  collection_ids: string[];
  tags: string[];
  availability_status: ResourceAvailabilityStatus;
  safe_deep_link: string;
  warnings: string[];
  saved_at: string;
  updated_at: string;
  deleted_at?: string | null;
  row_version: number;
}

export interface SavedItemListResponse {
  items: SavedItem[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface SavedCollection {
  collection_id: string;
  owner_user_id: string;
  name: string;
  description?: string | null;
  parent_collection_id?: string | null;
  item_count: number;
  sort_order: number;
  created_at: string;
  updated_at: string;
  row_version: number;
}

export interface SavedCollectionTree {
  collection: SavedCollection;
  children: SavedCollectionTree[];
}

export interface SavedTag {
  tag_id: string;
  name: string;
  normalized_name: string;
  item_count: number;
  created_at: string;
}

export interface SavedViewConfiguration {
  configuration_id: string;
  configuration_type: ViewConfigurationType;
  schema_version: number;
  payload: Record<string, unknown>;
  payload_hash: string;
  target_module: SavedModule;
  created_at: string;
  updated_at: string;
}

export interface SavedTargetDefinition {
  target_type: SavedTargetType;
  module: SavedModule;
  display_name: string;
  description: string;
  supports_view_config: boolean;
  supports_revision_pin: boolean;
  semantics: SavedReferenceSemantics;
}

export interface ResolvedTarget {
  target_type: SavedTargetType;
  target_id: string;
  exists: boolean;
  authorized: boolean;
  entitled: boolean;
  status: ResourceAvailabilityStatus;
  canonical_title: string;
  target_module: SavedModule;
  safe_deep_link: string;
  target_revision_id?: string | null;
  latest_revision_id?: string | null;
  warnings: string[];
}

export interface SavedLibrarySummary {
  total_saved_items: number;
  favorite_count: number;
  pinned_count: number;
  collection_count: number;
  tag_count: number;
  recent_saves_count: number;
}

export interface CreateSavedItemRequest {
  target_type: SavedTargetType;
  target_id: string;
  target_revision_id?: string | null;
  display_title_override?: string | null;
  user_note?: string | null;
  favorite?: boolean;
  pinned?: boolean;
  collection_ids?: string[];
  tags?: string[];
  view_configuration_id?: string | null;
  idempotency_key?: string | null;
}

export interface UpdateSavedItemRequest {
  display_title_override?: string | null;
  user_note?: string | null;
  favorite?: boolean | null;
  pinned?: boolean | null;
  target_revision_id?: string | null;
  expected_row_version?: number | null;
}

export interface CreateSavedCollectionRequest {
  name: string;
  description?: string | null;
  parent_collection_id?: string | null;
  sort_order?: number;
}

export interface CreateSavedTagRequest {
  name: string;
}

export interface UpdateSavedCollectionRequest {
  name?: string | null;
  description?: string | null;
  parent_collection_id?: string | null;
  sort_order?: number | null;
  expected_row_version?: number | null;
}

export interface CreateSavedConfigurationRequest {
  configuration_type: ViewConfigurationType;
  schema_version?: number;
  payload: Record<string, unknown>;
  target_module: SavedModule;
}

export interface ValidateConfigurationRequest {
  configuration_type: ViewConfigurationType;
  schema_version: number;
  payload: Record<string, unknown>;
  target_version?: number | null;
}

export interface ValidateConfigurationResponse {
  valid: boolean;
  schema_version: number;
  sanitized_payload: Record<string, unknown>;
  payload_hash: string;
  migrated_payload?: Record<string, unknown> | null;
  migrated_version?: number | null;
  warnings: string[];
}

export interface SavedBulkActionRequest {
  action: SavedBulkActionType;
  saved_item_ids: string[];
  collection_id?: string | null;
  tag_name?: string | null;
}

export interface BulkActionItemResult {
  saved_item_id: string;
  success: boolean;
  error?: string | null;
}

export interface SavedBulkActionResponse {
  action: SavedBulkActionType;
  total_requested: number;
  succeeded_count: number;
  failed_count: number;
  results: BulkActionItemResult[];
}
