/**
 * TypeScript definitions for ATLAS Watchlist Enrichment V1 (Stage 79).
 */

export type EnrichmentCategory =
  | "fundamentals"
  | "valuation"
  | "technical"
  | "events"
  | "earnings"
  | "news";

export type EnrichmentStatus =
  | "AVAILABLE"
  | "STALE"
  | "NOT_APPLICABLE"
  | "UNAVAILABLE"
  | "NOT_ENTITLED"
  | "INSUFFICIENT_HISTORY"
  | "ERROR";

export interface WatchlistEnrichmentValue {
  column_id: string;
  status: EnrichmentStatus;
  value?: unknown;
  value_type?: string;
  unit?: string | null;
  currency?: string | null;
  entity_id?: string | null;
  company_id?: string | null;
  market_series_id?: string | null;
  fiscal_period?: string | null;
  fiscal_year?: number | null;
  period_end_date?: string | null;
  observation_time?: string | null;
  publication_time?: string | null;
  as_of_date?: string | null;
  source_id?: string | null;
  source_document_id?: string | null;
  methodology_id?: string | null;
  revision_id?: string | null;
  headline?: string | null;
  publisher?: string | null;
  url?: string | null;
  event_status?: string | null;
  reason?: string | null;
}

export interface EnrichmentColumnMetadata {
  column_id: string;
  label: string;
  description: string;
  category: EnrichmentCategory;
  value_type: string;
  source_capability: string;
  supported_asset_classes: string[];
  unit?: string;
  currency_dependent: boolean;
  can_sort: boolean;
  default_visible: boolean;
  methodology?: string;
}

export interface WatchlistEnrichmentItemRequest {
  item_id: string;
  instrument_entity_id: string;
  company_entity_id?: string | null;
  market_series_id?: string | null;
  asset_class?: string;
  last_price?: number | null;
  quote_currency?: string;
}

export interface WatchlistEnrichmentRequest {
  watchlist_id?: string;
  selected_column_ids: string[];
  items: WatchlistEnrichmentItemRequest[];
}

export interface WatchlistEnrichmentResponse {
  watchlist_id: string;
  as_of: string;
  results: Record<string, Record<string, WatchlistEnrichmentValue>>;
  partial_errors: Record<string, string>;
}
