/**
 * TypeScript type definitions and DTOs for ATLAS Futures & Commodities Markets V1 (Stage 62).
 */

export type CommodityCategory =
  | "energy"
  | "precious_metals"
  | "industrial_metals"
  | "agriculture"
  | "soft_commodities"
  | "livestock"
  | "financial_index";

export type SettlementType = "physical" | "cash" | "other_unknown";

export type ContractLifecycle =
  | "active"
  | "expired"
  | "delisted"
  | "suspended"
  | "unknown";

export type SettlementStatus = "FINAL" | "PRELIMINARY";

export type VolumeWindow = "SESSION" | "DAILY" | "UNKNOWN";

export interface CommoditySummary {
  commodity_entity_id: string;
  name: string;
  slug: string;
  category: CommodityCategory;
  grade_specification?: string | null;
  physical_unit: string;
  reference_region?: string | null;
  delivery_characteristics?: string | null;
}

export interface FuturesProductSummary {
  product_entity_id: string;
  underlying_entity_id: string;
  root_symbol: string;
  name: string;
  exchange: string;
  exchange_mic: string;
  category: CommodityCategory;
  contract_size: string | number;
  size_unit: string;
  quote_currency: string;
  quote_unit: string;
  tick_size: string | number;
  tick_value?: string | number | null;
  settlement_type: SettlementType;
  contract_multiplier?: string | number;
}

export interface FuturesContractSpecificationView {
  contract_size: string | number;
  size_unit: string;
  quote_currency: string;
  quote_unit: string;
  tick_size: string | number;
  tick_value?: string | number | null;
  settlement_type: SettlementType;
  contract_multiplier: string | number;
  trading_hours: string;
  expiration_date: string;
  last_trading_date: string;
  first_notice_date?: string | null;
  last_notice_date?: string | null;
  delivery_start_date?: string | null;
  delivery_end_date?: string | null;
  settlement_date: string;
}

export interface FuturesPriceObservationView {
  last?: string | number | null;
  bid?: string | number | null;
  ask?: string | number | null;
  spread?: string | number | null;
  quote_unit: string;
  quote_currency: string;
  source_timestamp: string;
  received_at: string;
  freshness_status: string;
  delay_status: string;
  provider: string;
}

export interface FuturesSettlementObservationView {
  settlement_price?: string | number | null;
  settlement_status: SettlementStatus;
  trade_date?: string | null;
  publication_timestamp?: string | null;
  quote_unit: string;
  provider: string;
}

export interface FuturesPriceChangeView {
  change_absolute?: string | number | null;
  change_percent?: string | number | null;
  reference_price?: string | number | null;
  reference_type: string;
  change_ticks?: string | number | null;
}

export interface FuturesVolumeOpenInterestView {
  volume?: number | null;
  volume_window: VolumeWindow;
  open_interest?: number | null;
  open_interest_as_of?: string | null;
  provider: string;
}

export interface FuturesContractDirectoryItem {
  instrument_entity_id: string;
  product_entity_id: string;
  underlying_entity_id: string;
  symbol: string;
  name: string;
  product_name: string;
  underlying_name: string;
  exchange: string;
  exchange_mic: string;
  category: CommodityCategory;
  contract_year: number;
  contract_month_code: string;
  contract_month: string;
  expiration_date: string;
  last_trading_date: string;
  lifecycle_status: ContractLifecycle;
  settlement_type: SettlementType;
  contract_size: string | number;
  size_unit: string;
  tick_size: string | number;
  tick_value?: string | number | null;
  quote_currency: string;
  quote_unit: string;

  price_observation: FuturesPriceObservationView;
  settlement_observation: FuturesSettlementObservationView;
  price_change: FuturesPriceChangeView;
  volume_open_interest: FuturesVolumeOpenInterestView;
}

export interface FuturesContractOverviewResponse {
  instrument_entity_id: string;
  symbol: string;
  name: string;
  exchange: string;
  exchange_mic: string;
  contract_year: number;
  contract_month_code: string;
  contract_month: string;
  lifecycle_status: ContractLifecycle;

  underlying: CommoditySummary;
  product: FuturesProductSummary;
  specifications: FuturesContractSpecificationView;

  price_observation: FuturesPriceObservationView;
  settlement_observation: FuturesSettlementObservationView;
  price_change: FuturesPriceChangeView;
  volume_open_interest: FuturesVolumeOpenInterestView;

  provider: string;
  freshness_status: string;
  delay_status: string;
  source_timestamp: string;
  received_at: string;
}

export interface CommodityDirectoryItem {
  commodity_entity_id: string;
  name: string;
  slug: string;
  category: CommodityCategory;
  grade_specification?: string | null;
  physical_unit: string;
  reference_region?: string | null;
  delivery_characteristics?: string | null;
  associated_products_count: number;
  active_contracts_count: number;
  associated_products: FuturesProductSummary[];
}

export interface CommoditySpotBenchmarkView {
  benchmark_entity_id: string;
  commodity_entity_id: string;
  commodity_name: string;
  name: string;
  grade: string;
  location: string;
  currency: string;
  quote_unit: string;
  assessment_methodology: string;
  latest_price?: string | number | null;
  previous_price?: string | number | null;
  change_absolute?: string | number | null;
  change_percent?: string | number | null;
  as_of_date: string;
  provider: string;
}

export interface FuturesCoverageSummary {
  total_commodities: number;
  total_products: number;
  total_contracts: number;
  active_contracts: number;
  contracts_with_last: number;
  contracts_with_settlement: number;
  contracts_with_volume: number;
  contracts_with_open_interest: number;
  exchanges_represented: string[];
}

export interface FuturesProductOption {
  product_entity_id: string;
  root_symbol: string;
  name: string;
  exchange: string;
  category: string;
}

export interface FuturesFilterOptionsResponse {
  categories: string[];
  exchanges: string[];
  products: FuturesProductOption[];
  months: string[];
  settlement_types: string[];
  lifecycle_statuses: string[];
  coverage: FuturesCoverageSummary;
}

export interface FuturesContractDirectoryResponse {
  items: FuturesContractDirectoryItem[];
  total: number;
  limit: number;
  cursor?: string | null;
  next_cursor?: string | null;
  has_more: boolean;
  coverage: FuturesCoverageSummary;
}

export interface CommodityDirectoryResponse {
  items: CommodityDirectoryItem[];
  total: number;
}

export interface SpotBenchmarkDirectoryResponse {
  items: CommoditySpotBenchmarkView[];
  total: number;
}

export interface FuturesContractQueryParams {
  query?: string;
  category?: string;
  exchange?: string;
  product_entity_id?: string;
  root_symbol?: string;
  contract_month?: string;
  settlement_type?: string;
  lifecycle_status?: string;
  limit?: number;
  cursor?: string;
}
