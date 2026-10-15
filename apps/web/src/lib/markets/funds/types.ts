/**
 * ATLAS Stage 58 - ETFs & Funds Markets V1
 * TypeScript Contracts & DTOs
 */

import {
  MarketSummaryChangeDirection,
  MarketSummaryDataStatus,
  MarketSummaryDeliveryDelay,
} from "@/lib/home/market-summary-types";

export type {
  MarketSummaryChangeDirection,
  MarketSummaryDataStatus,
  MarketSummaryDeliveryDelay,
};

export type FundType =
  | "ETF"
  | "OPEN_END_MUTUAL_FUND"
  | "CLOSED_END_FUND"
  | "OTHER_SUPPORTED_FUND";

export interface FundMarketQuoteView {
  last_price?: string | null;
  bid_price?: string | null;
  ask_price?: string | null;
  reference_close?: string | null;
  reference_source?: string | null;
  absolute_change?: string | null;
  percentage_change?: string | null;
  change_direction: MarketSummaryChangeDirection;
  source_timestamp?: string | null;
  received_at?: string | null;
  freshness_status: string;
  delivery_delay_status: MarketSummaryDeliveryDelay;
  provider_key: string;
  provider_display_name: string;
  data_status: MarketSummaryDataStatus;
  unavailable_reason?: string | null;
}

export interface FundNAVView {
  nav_per_unit?: string | null;
  nav_currency?: string | null;
  valuation_date?: string | null;
  published_at?: string | null;
  valuation_method: string;
  provider_key?: string | null;
  provenance?: string | null;
  is_available: boolean;
  unavailable_reason?: string | null;
}

export interface FundFeeView {
  net_expense_ratio?: string | null;
  gross_expense_ratio?: string | null;
  management_fee?: string | null;
  fee_scale: string;
  as_of_date?: string | null;
  is_available: boolean;
}

export interface FundAUMView {
  amount?: string | null;
  currency?: string | null;
  scope?: string | null;
  as_of_date?: string | null;
  is_available: boolean;
}

export interface FundDirectoryItem {
  instrument_entity_id: string;
  fund_product_entity_id?: string | null;
  share_class_entity_id?: string | null;
  display_name: string;
  display_symbol: string;
  fund_type: FundType | string;
  fund_type_label: string;
  fund_category: string;
  is_exchange_traded: boolean;
  exchange_mic?: string | null;
  exchange_display_name?: string | null;
  listing_market_country?: string | null;
  listing_market_country_code?: string | null;
  trading_currency?: string | null;
  listing_status: string;
  domicile: string;
  share_class_currency: string;
  distribution_policy: string;
  market_quote?: FundMarketQuoteView | null;
  official_nav?: FundNAVView | null;
  fees?: FundFeeView | null;
  aum?: FundAUMView | null;
  benchmark_name?: string | null;
  manager_name?: string | null;
}

export interface FundCoverageSummary {
  configured_funds_count: number;
  etf_count: number;
  mutual_fund_count: number;
  closed_end_fund_count: number;
  exchange_listed_count: number;
  returned_count: number;
  available_quotes_count: number;
  unavailable_quotes_count: number;
  available_nav_count: number;
  unavailable_nav_count: number;
}

export interface FundTypeOption {
  id: string;
  label: string;
  count: number;
}

export interface FundCountryOption {
  code: string;
  name: string;
  count: number;
}

export interface FundExchangeOption {
  mic: string;
  name: string;
  country: string;
  count: number;
}

export interface FundDomicileOption {
  name: string;
  count: number;
}

export interface FundCategoryOption {
  id: string;
  label: string;
  count: number;
}

export interface FundCurrencyOption {
  code: string;
  count: number;
}

export interface FundFilterOptionsResponse {
  fund_types: FundTypeOption[];
  countries: FundCountryOption[];
  exchanges: FundExchangeOption[];
  domiciles: FundDomicileOption[];
  categories: FundCategoryOption[];
  currencies: FundCurrencyOption[];
}

export interface FundDirectoryFilters {
  fund_type?: string | null;
  market_country?: string | null;
  exchange?: string | null;
  domicile?: string | null;
  fund_category?: string | null;
  share_class_currency?: string | null;
  query?: string | null;
}

export interface FundDirectoryResponse {
  schema_version: number;
  generated_at: string;
  scope: string;
  items: FundDirectoryItem[];
  filters: FundDirectoryFilters;
  coverage: FundCoverageSummary;
  available_filters: FundFilterOptionsResponse;
  next_cursor?: string | null;
  has_more: boolean;
  total_matched: number;
}

export interface FundIdentifierItem {
  scheme: string;
  value: string;
  is_primary: boolean;
}

export interface FundVenueDetails {
  mic: string;
  name: string;
  country: string;
  operating_mic?: string | null;
  city?: string | null;
  timezone?: string | null;
}

export interface FundBenchmarkDetails {
  benchmark_entity_id?: string | null;
  name: string;
  description?: string | null;
  is_verified: boolean;
}

export interface FundManagementDetails {
  manager_entity_id?: string | null;
  name: string;
  role: string;
  is_verified: boolean;
}

export interface FundOverviewDetailResponse {
  schema_version: number;
  generated_at: string;
  item: FundDirectoryItem;
  identifiers: FundIdentifierItem[];
  venue_details?: FundVenueDetails | null;
  benchmark_details?: FundBenchmarkDetails | null;
  management_details?: FundManagementDetails | null;
  coverage_limitations: string[];
}
