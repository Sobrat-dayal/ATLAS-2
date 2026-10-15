/**
 * TypeScript type definitions for ATLAS FX Markets V1 (Stage 59).
 */

export type FxRateKind =
  | "SPOT_BID_ASK"
  | "INDICATIVE_MID"
  | "REFERENCE_RATE"
  | "LAST_TRADE"
  | "UNKNOWN"
  | "CROSSED_INVALID"
  | "ARITHMETIC_IDENTITY";

export type FxCalculationDirection = "DIRECT" | "REVERSE" | "SAME_CURRENCY";

export type FxConversionMode =
  | "INDICATIVE_MID"
  | "OBSERVED_REFERENCE"
  | "QUOTE_SIDE_ILLUSTRATION";

export interface CurrencyItem {
  code: string;
  name: string;
  symbol: string;
  minor_units: number;
  country_or_region: string;
}

export interface FxQuoteView {
  bid: string | number | null;
  ask: string | number | null;
  midpoint: string | number | null;
  spread_absolute: string | number | null;
  spread_bps: string | number | null;
  spread_pips: string | number | null;
  rate_kind: FxRateKind | string;
  change_24h?: string | number | null;
  change_24h_percent?: string | number | null;
  qualified_reference_close?: string | number | null;
  data_status: string;
  freshness_status: string;
  provider: string;
  observed_at: string | null;
  received_at: string | null;
}

export interface FxPairDirectoryItem {
  instrument_entity_id: string;
  display_pair: string;
  base_currency: string;
  quote_currency: string;
  instrument_kind: string;
  pip_size: string | number;
  rate_precision: number;
  quote: FxQuoteView | null;
  provider_aliases: string[];
}

export interface FxPairCoverageSummary {
  total_pairs: number;
  base_currencies_count: number;
  quote_currencies_count: number;
  pairs_with_quotes: number;
  pairs_with_bid_ask: number;
  pairs_with_spread: number;
  scope: string;
}

export interface FxPairDirectoryResponse {
  items: FxPairDirectoryItem[];
  total_count: number;
  coverage: FxPairCoverageSummary;
  next_cursor: string | null;
  has_more: boolean;
}

export interface FxPairOverviewDetailResponse {
  pair: FxPairDirectoryItem;
  base_currency_info: CurrencyItem;
  quote_currency_info: CurrencyItem;
  orientation_explanation: string;
}

export interface FxCurrenciesResponse {
  items: CurrencyItem[];
  total_count: number;
}

export interface FxConversionRequest {
  amount: string | number;
  from_currency: string;
  to_currency: string;
  mode?: FxConversionMode;
}

export interface FxConversionResponse {
  from_currency: string;
  to_currency: string;
  input_amount: string | number;
  output_amount: string | number;
  rate_used: string | number;
  rate_kind: string;
  calculation_direction: FxCalculationDirection | string;
  source_pair_entity_id: string | null;
  quote_side: string | null;
  source_timestamp: string | null;
  received_at: string | null;
  freshness_status: string;
  delay_status: string;
  provider: string;
  indicative: boolean;
  disclaimer: string;
}
