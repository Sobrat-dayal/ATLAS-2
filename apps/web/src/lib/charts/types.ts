/**
 * TypeScript Interfaces for ATLAS Charts V1 (Stage 66).
 *
 * Strongly-typed definitions matching backend Pydantic models for historical OHLCV,
 * instrument metadata, coverage audits, and visualization settings.
 */

export type ChartRenderMode = "candlestick" | "bar" | "line" | "area";

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
  interval_source_kind?: "NATIVE" | "DERIVED" | string;
  derived_source_interval?: string | null;
}

// ============================================================================
// Stage 68 Multi-Timeframe Interval Types
// ============================================================================

export type ChartIntervalId =
  | "1m"
  | "5m"
  | "15m"
  | "30m"
  | "1h"
  | "4h"
  | "1d"
  | "1w"
  | "1M";

export type ChartIntervalAvailability =
  | "AVAILABLE_NATIVE"
  | "AVAILABLE_DERIVED"
  | "PARTIAL"
  | "UNAVAILABLE";

export interface ChartIntervalOptionDTO {
  interval_id: ChartIntervalId | string;
  display_label: string;
  duration_seconds: number | null;
  availability: ChartIntervalAvailability | string;
  native_or_derived: "NATIVE" | "DERIVED" | "UNAVAILABLE" | string;
  is_supported: boolean;
  source_interval?: string | null;
  earliest_available?: string | null;
  latest_available?: string | null;
  live_bar_supported: boolean;
  unavailability_reason?: string | null;
}

export interface ChartIntervalsResponse {
  schema_version: string;
  instrument_entity_id: string;
  display_symbol: string;
  instrument?: ChartInstrumentMetadata | null;
  default_interval: string;
  intervals: ChartIntervalOptionDTO[];
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

// ============================================================================
// Stage 67 Live Chart Streaming Types
// ============================================================================

export type ChartConnectionState =
  | "DISCONNECTED"
  | "CONNECTING"
  | "CONNECTED"
  | "RECONNECTING"
  | "ERROR";

export type ChartMarketDataFreshness =
  | "LIVE"
  | "DELAYED"
  | "STALE"
  | "UNKNOWN"
  | "UNAVAILABLE";

export type ChartLiveCapability =
  | "HISTORICAL_ONLY"
  | "LIVE_PRICE_AVAILABLE"
  | "LIVE_BAR_AVAILABLE"
  | "UNAVAILABLE";

export type ChartDisplayState =
  | "HISTORICAL_ONLY"
  | "LIVE_PRICE_AVAILABLE"
  | "LIVE_BAR_AVAILABLE"
  | "PAUSED"
  | "RECONCILING";

export interface LiveQuoteDTO {
  bid_price: number | string | null;
  ask_price: number | string | null;
  bid_size?: number | string | null;
  ask_size?: number | string | null;
  last_price: number | string | null;
  last_size?: number | string | null;
  as_of: string | null;
  is_midpoint: boolean;
  has_genuine_last: boolean;
}

export interface ChartLiveStateResponse {
  schema_version: string;
  instrument_entity_id: string;
  display_symbol: string;
  market_or_venue: string;
  price_currency: string;
  quotation_unit: string;
  quote: LiveQuoteDTO | null;
  source_timestamp: string | null;
  received_at: string | null;
  provider: string;
  freshness_status: ChartMarketDataFreshness | string;
  delay_status: "REALTIME" | "DELAYED_15M" | "UNKNOWN" | string;
  live_capability: ChartLiveCapability | string;
  availability: "AVAILABLE" | "UNAVAILABLE" | string;
  is_paused: boolean;
}

export interface LiveChartSubscriptionKey {
  instrument_entity_id: string;
  variant?: string | null;
  symbol?: string | null;
}

export interface LiveChartEvent {
  schema_version?: number;
  event_type?: string;
  instrument_entity_id?: string;
  instrument_id?: string;
  source_timestamp?: string;
  payload?: {
    quote?: Partial<LiveQuoteDTO> & Record<string, unknown>;
  } & Record<string, unknown>;
  [key: string]: unknown;
}
