/**
 * TypeScript type definitions for ATLAS Cryptocurrency Markets V1 (Stage 60).
 */

export type CryptoRateKind =
  | "SPOT_TRADE"
  | "BID_ASK_QUOTE"
  | "INDICATIVE_COMPOSITE"
  | "CROSSED_INVALID"
  | "UNKNOWN";

export type QuoteAssetType = "fiat" | "stablecoin" | "crypto";

export interface CryptoAssetItem {
  asset_entity_id: string;
  symbol: string;
  name: string;
  asset_kind: string;
  network_id?: string | null;
  contract_address?: string | null;
  token_standard?: string | null;
  decimals: number;
  description: string;
}

export interface CryptoVenueItem {
  venue_id: string;
  name: string;
  venue_type: string;
  jurisdiction: string;
}

export interface CryptoQuoteView {
  last_price: string | number | null;
  bid: string | number | null;
  ask: string | number | null;
  midpoint: string | number | null;
  spread_absolute: string | number | null;
  spread_bps: string | number | null;
  rate_kind: CryptoRateKind | string;
  change_24h?: string | number | null;
  change_24h_percent?: string | number | null;
  volume_24h_base?: string | number | null;
  volume_24h_quote?: string | number | null;
  quote_asset_unit: string;
  data_status: string;
  freshness_status: string;
  provider: string;
  observed_at: string | null;
  received_at: string | null;
}

export interface CryptoSpotMarketDirectoryItem {
  instrument_entity_id: string;
  market_symbol: string;
  base_asset_symbol: string;
  base_asset_name: string;
  quote_asset_symbol: string;
  quote_asset_type: QuoteAssetType | string;
  venue_id: string;
  venue_name: string;
  venue_market_symbol: string;
  market_type: string;
  price_precision: number;
  quantity_precision: number;
  quote: CryptoQuoteView | null;
  provider_aliases: string[];
}

export interface CryptoCoverageSummary {
  total_assets: number;
  total_spot_markets: number;
  total_venues: number;
  markets_with_quotes: number;
  markets_with_bid_ask: number;
  markets_with_volume: number;
  markets_with_24h_change: number;
  scope: string;
}

export interface CryptoFilterOptionsResponse {
  base_assets: string[];
  quote_assets: string[];
  venues: CryptoVenueItem[];
  quote_asset_types: string[];
}

export interface CryptoSpotMarketDirectoryResponse {
  items: CryptoSpotMarketDirectoryItem[];
  total_count: number;
  coverage_summary: CryptoCoverageSummary;
  available_filters: CryptoFilterOptionsResponse;
  next_cursor?: string | null;
}

export interface CryptoAssetDirectoryResponse {
  items: CryptoAssetItem[];
  total_count: number;
  next_cursor?: string | null;
}

export interface CryptoSpotMarketOverviewDetailResponse {
  instrument_entity_id: string;
  market_symbol: string;
  base_asset: CryptoAssetItem;
  quote_asset_symbol: string;
  quote_asset_type: string;
  venue: CryptoVenueItem;
  venue_market_symbol: string;
  market_type: string;
  price_precision: number;
  quantity_precision: number;
  min_quantity: string | number;
  quote: CryptoQuoteView;
  provider_aliases: string[];
  disclaimer: string;
}

export interface CryptoMarketFiltersState {
  query?: string;
  base_asset?: string;
  quote_asset?: string;
  venue?: string;
  quote_asset_type?: string;
  limit?: number;
  cursor?: string;
}
