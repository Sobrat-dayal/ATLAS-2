/**
 * ATLAS Stage 57 - Equities Markets V1
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

export type EquitySubtype =
  | "common_equity"
  | "preferred_equity"
  | "depositary_receipt"
  | "unit"
  | "warrant"
  | "other";

export type EquityListingStatus =
  | "active"
  | "inactive"
  | "delisted"
  | "suspended"
  | "unknown";

export interface EquityDirectoryItem {
  instrument_entity_id: string;
  listing_id?: string | null;
  display_name: string;
  display_symbol: string;
  equity_subtype: string;

  exchange_id?: string | null;
  exchange_mic: string;
  exchange_display_name: string;
  listing_market_country: string;
  trading_currency: string;
  listing_status: string;

  issuer_company_entity_id?: string | null;
  quote_availability: boolean;

  // High-precision Decimal serialized as strings to preserve mathematical fidelity
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

  provider_key?: string | null;
  provider_display_name?: string | null;

  data_status: MarketSummaryDataStatus;
  unavailable_reason?: string | null;
}

export interface EquityCoverageSummary {
  configured_equities_count: number;
  covered_exchanges_count: number;
  market_countries_count: number;
  returned_count: number;
  available_quotes_count: number;
  unavailable_quotes_count: number;
}

export interface CountryOption {
  code: string;
  name: string;
  count: number;
}

export interface ExchangeOption {
  mic: string;
  name: string;
  country: string;
  count: number;
}

export interface TypeOption {
  id: string;
  label: string;
  count: number;
}

export interface StatusOption {
  id: string;
  label: string;
  count: number;
}

export interface EquityFilterOptionsResponse {
  countries: CountryOption[];
  exchanges: ExchangeOption[];
  equity_types: TypeOption[];
  listing_statuses: StatusOption[];
}

export interface EquityDirectoryFilters {
  market_country?: string | null;
  exchange?: string | null;
  equity_type?: string | null;
  listing_status?: string | null;
  query?: string | null;
}

export interface EquityDirectoryResponse {
  schema_version: number;
  generated_at: string;
  scope: string;
  items: EquityDirectoryItem[];
  filters: EquityDirectoryFilters;
  coverage: EquityCoverageSummary;
  available_filters: EquityFilterOptionsResponse;
  next_cursor?: string | null;
  has_more: boolean;
}

export interface EquityIdentifierItem {
  scheme: string;
  value: string;
  is_primary: boolean;
}

export interface EquityIssuerCompanyInfo {
  company_entity_id: string;
  canonical_name: string;
  short_name?: string | null;
  country_of_incorporation?: string | null;
  verified: boolean;
}

export interface EquityVenueDetails {
  mic: string;
  name: string;
  country: string;
  operating_mic?: string | null;
  city?: string | null;
  timezone?: string | null;
}

export interface EquityOverviewDetailResponse {
  schema_version: number;
  generated_at: string;
  item: EquityDirectoryItem;
  identifiers: EquityIdentifierItem[];
  issuer_company?: EquityIssuerCompanyInfo | null;
  venue_details: EquityVenueDetails;
  coverage_limitations: string[];
}
