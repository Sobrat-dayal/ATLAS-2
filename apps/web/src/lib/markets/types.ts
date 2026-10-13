/**
 * TypeScript Contracts for Stage 56 Markets Overview V1.
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

export type MarketsGroupFilter =
  | "all"
  | "benchmarks"
  | "equities"
  | "etfs"
  | "fx"
  | "crypto"
  | "commodities"
  | "bonds";

export type MarketTableSortField = "order" | "name" | "category" | "price" | "change";
export type SortDirection = "asc" | "desc";

export interface MarketGroupSummary {
  id: string;
  label: string;
  count: number;
}

export interface MarketsOverviewCoverage {
  configured_count: number;
  returned_count: number;
  available_count: number;
  unavailable_count: number;
}

export interface MarketsOverviewItem {
  instrument_entity_id: string;
  display_name: string;
  display_symbol?: string | null;
  instrument_category: string;
  market_group: string;
  venue?: string | null;
  value_kind: string;

  quote_currency?: string | null;
  quote_unit?: string | null;

  // High-precision Decimal serialized as strings to preserve mathematical fidelity
  last_price?: string | null;
  bid_price?: string | null;
  ask_price?: string | null;

  absolute_change?: string | null;
  percentage_change?: string | null;
  change_direction: MarketSummaryChangeDirection;

  source_timestamp?: string | null;
  received_at?: string | null;

  // Stage 44 freshness integration
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

  featured: boolean;
  display_order: number;
}

export interface MarketsOverviewResponse {
  schema_version: number;
  generated_at: string;
  scope: string;
  groups: MarketGroupSummary[];
  items: MarketsOverviewItem[];
  featured_items: MarketsOverviewItem[];
  coverage: MarketsOverviewCoverage;
  next_cursor?: string | null;
  has_more: boolean;
}
