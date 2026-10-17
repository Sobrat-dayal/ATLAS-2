/**
 * Type definitions for ATLAS Cross-Asset Markets V1 (Stage 65).
 */

export type CrossAssetMode = "native_overview" | "aligned_performance";

export type CrossAssetWindow = "last_24h" | "last_7d" | "last_30d";

export type AssetClass =
  | "equities"
  | "etfs"
  | "fx"
  | "crypto"
  | "bonds"
  | "futures";

export type NativeMetricKind =
  | "EQUITY_PRICE_CHANGE"
  | "ETF_MARKET_PRICE_CHANGE"
  | "FX_SPOT_RATE_CHANGE"
  | "CRYPTO_SPOT_24H_CHANGE"
  | "BOND_YIELD_BPS_CHANGE"
  | "FUTURES_SETTLEMENT_CHANGE";

export type ProxyKind = "none" | "ETF Proxy" | "Futures Proxy" | "Benchmark Index";

export type CrossAssetCoverageStatus =
  | "COMPLETE_FOR_DEFINED_SET"
  | "PARTIAL"
  | "DEGRADED"
  | "UNAVAILABLE";

export interface NativeMetricObservation {
  metric_kind: NativeMetricKind;
  display_label: string;
  current_value: number | string;
  reference_value?: number | string | null;
  change_value?: number | string | null;
  change_percent?: number | string | null;
  unit: string;
  as_of_time: string;
  session_status: string;
}

export interface AlignedPricePerformance {
  eligible: boolean;
  price_return_percent?: number | string | null;
  indexed_value?: number | string | null;
  start_price?: number | string | null;
  end_price?: number | string | null;
  quote_currency: string;
  quote_unit: string;
  effective_start_time?: string | null;
  effective_end_time?: string | null;
  start_time_offset_seconds?: number | null;
  end_time_offset_seconds?: number | null;
  currency_interpretation: string;
  is_common_currency_converted: boolean;
  exclusion_reason?: string | null;
  exclusion_detail?: string | null;
}

export interface CrossAssetMember {
  instrument_entity_id: string;
  market_series_identity: string;
  display_name: string;
  symbol: string;
  asset_class: AssetClass;
  market_or_venue: string;
  is_benchmark: boolean;
  is_proxy: boolean;
  proxy_kind: ProxyKind;
  proxy_benchmark_target?: string | null;
  native_metric: NativeMetricObservation;
  aligned_performance: AlignedPricePerformance;
  freshness_status: string;
  is_delayed: boolean;
  delay_minutes: number;
  provider: string;
}

export interface AssetClassSummarySection {
  asset_class: AssetClass;
  display_title: string;
  native_metric_description: string;
  representative_members: CrossAssetMember[];
  total_members: number;
  qualified_members: number;
  coverage_status: CrossAssetCoverageStatus;
}

export interface CrossAssetCoverage {
  requested_members: number;
  authorized_members: number;
  evaluated_members: number;
  qualified_members: number;
  excluded_members: number;
  exclusions_by_reason: Record<string, number>;
  included_asset_classes: AssetClass[];
  unavailable_asset_classes: AssetClass[];
  completeness_status: CrossAssetCoverageStatus;
}

export interface CrossAssetUniverseDefinition {
  universe_id: string;
  display_name: string;
  description: string;
  asset_classes: AssetClass[];
  member_count: number;
  default_symbols: string[];
}

export interface CrossAssetExclusionItem {
  symbol: string;
  display_name: string;
  asset_class: string;
  reason: string;
  detail: string;
}

export interface CrossAssetOverviewResponse {
  schema_version: string;
  snapshot_id: string;
  universe_id: string;
  universe_name: string;
  mode: CrossAssetMode;
  comparison_window: CrossAssetWindow;
  requested_start: string;
  requested_end: string;
  calculated_at: string;
  alignment_methodology: string;
  currency_policy_label: string;
  coverage: CrossAssetCoverage;
  asset_class_sections: AssetClassSummarySection[];
  comparison_members: CrossAssetMember[];
  exclusions: CrossAssetExclusionItem[];
}

export interface CrossAssetUniverseResponse {
  universes: CrossAssetUniverseDefinition[];
  count: number;
}

export interface CrossAssetOptionsResponse {
  modes: CrossAssetMode[];
  windows: CrossAssetWindow[];
  asset_classes: AssetClass[];
  max_selection_count: number;
  currency_policy: string;
  alignment_tolerance_seconds: number;
}
