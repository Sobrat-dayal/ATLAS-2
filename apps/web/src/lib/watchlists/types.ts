/**
 * TypeScript type definitions for Watchlists V1 (Stage 76).
 */

export interface WatchlistSummary {
  id: string;
  owner_user_id: string;
  name: string;
  description: string | null;
  item_count: number;
  revision: number;
  created_at: string;
  updated_at: string;
}

export interface WatchlistListResponse {
  items: WatchlistSummary[];
  total: number;
  page: number;
  page_size: number;
}

export type ChangeDirection = "up" | "down" | "flat" | "unknown";
export type FreshnessStatus = "fresh" | "aging" | "stale" | "unavailable";
export type DeliveryDelayStatus = "realtime" | "delayed" | "unknown";

export interface WatchlistItem {
  id: string;
  watchlist_id: string;
  instrument_entity_id: string;
  market_series_id: string;
  position: number;
  created_at: string;

  // Canonical Display Metadata
  symbol: string;
  display_name: string;
  canonical_name: string;
  asset_class: string;
  venue: string | null;
  quote_currency: string | null;
  quote_unit: string | null;

  // Latest Qualified Market Data Snapshot
  is_quote_available: boolean;
  quote_measure: string | null;
  last_price: string | null;
  bid_price: string | null;
  ask_price: string | null;
  absolute_change: string | null;
  percentage_change: string | null;
  change_direction: ChangeDirection;
  source_timestamp: string | null;
  freshness_status: FreshnessStatus;
  delivery_delay_status: DeliveryDelayStatus;
  delay_seconds: number | null;
  provider: string | null;

  // Verified Issuer / Company Cross-Navigation
  issuer_entity_id: string | null;
  has_company_page: boolean;
}

export interface WatchlistDetail {
  id: string;
  owner_user_id: string;
  name: string;
  description: string | null;
  revision: number;
  created_at: string;
  updated_at: string;
  items: WatchlistItem[];
  total_items: number;
  page: number;
  page_size: number;
}

export interface CreateWatchlistPayload {
  name: string;
  description?: string | null;
}

export interface UpdateWatchlistPayload {
  name?: string | null;
  description?: string | null;
}

export interface AddWatchlistItemPayload {
  instrument_entity_id: string;
  market_series_id?: string;
}

export interface ReorderWatchlistItemsPayload {
  ordered_item_ids: string[];
  expected_revision: number;
}

export interface ReorderWatchlistItemsResponse {
  watchlist_id: string;
  revision: number;
  ordered_item_ids: string[];
}
