/**
 * TypeScript Interfaces for ATLAS Charts V1 (Stage 66).
 *
 * Strongly-typed definitions matching backend Pydantic models for historical OHLCV,
 * instrument metadata, coverage audits, and visualization settings.
 */

export type ChartRenderMode = "candlestick" | "line";

export interface ChartBarDTO {
  timestamp: string; // ISO 8601 UTC
  time_unix: number; // Unix timestamp in seconds
  open: string | number;
  high: string | number;
  low: string | number;
  close: string | number;
  volume: string | number | null;
  is_final: boolean;
}

export interface ChartInstrumentMetadata {
  entity_id: string;
  display_name: string;
  display_symbol: string;
  asset_class: "equities" | "etfs" | "fx" | "crypto" | "bonds" | "futures" | string;
  market_or_venue: string;
  price_currency: string;
  quotation_unit: string;
  supported_intervals: string[];
  default_interval: string;
  price_basis: string;
  adjustment_basis: string;
  provider_key: string;
  has_volume: boolean;
  is_futures: boolean;
  allows_negative_price: boolean;
  contract_expiration?: string | null;
  base_asset?: string | null;
  quote_asset?: string | null;
}

export interface ChartCoverageDTO {
  requested_start?: string | null;
  requested_end?: string | null;
  earliest_available_bar?: string | null;
  latest_available_bar?: string | null;
  returned_bars_count: number;
  total_bars_available: number;
  has_more: boolean;
  known_gaps_count: number;
  source_status: "QUALIFIED" | "NO_DATA" | "PARTIAL" | "DEGRADED" | string;
}

export interface ChartPaginationDTO {
  limit: number;
  has_more: boolean;
  next_cursor?: string | null;
}

export interface ChartHistoryResponse {
  schema_version: string;
  instrument: ChartInstrumentMetadata;
  interval: string;
  bars: ChartBarDTO[];
  coverage: ChartCoverageDTO;
  pagination?: ChartPaginationDTO | null;
}

export interface ChartSearchResponse {
  results: ChartInstrumentMetadata[];
  count: number;
}

export interface HoveredBarData {
  time_unix: number;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
  changePercent?: number | null;
}
