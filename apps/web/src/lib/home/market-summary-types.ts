/**
 * TypeScript Contracts for Stage 52 Home Market Summary.
 */

export type MarketSummaryDataStatus =
  | "available"
  | "no_quote"
  | "not_configured"
  | "unresolved_instrument"
  | "source_unavailable"
  | "error";

export type MarketSummaryChangeDirection = "up" | "down" | "flat" | "unknown";

export type MarketSummaryDeliveryDelay = "realtime" | "delayed" | "unknown";

export interface HomeMarketSummaryCoverage {
  configured_count: number;
  available_count: number;
  unavailable_count: number;
}

export interface HomeMarketSummaryItem {
  instrument_entity_id: string;
  display_name: string;
  display_symbol?: string | null;
  instrument_category: string;
  value_kind: string;

  quote_currency?: string | null;
  quote_unit?: string | null;

  // Decimal strings from backend
  last_price?: string | null;
  bid_price?: string | null;
  ask_price?: string | null;

  absolute_change?: string | null;
  percentage_change?: string | null;
  change_direction: MarketSummaryChangeDirection;

  source_timestamp?: string | null;
  received_at?: string | null;

  freshness_status: string;
  delivery_delay_status: MarketSummaryDeliveryDelay;
  delay_seconds?: number | null;

  provider_key?: string | null;
  provider_display_name?: string | null;

  reference_close?: string | null;
  reference_session_date?: string | null;
  reference_source?: string | null;

  data_status: MarketSummaryDataStatus;
  unavailable_reason?: string | null;
}

export interface HomeMarketSummaryResponse {
  schema_version: number;
  generated_at: string;
  items: HomeMarketSummaryItem[];
  coverage: HomeMarketSummaryCoverage;
}
