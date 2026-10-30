/**
 * ATLAS Portfolios V1 — Performance Analytics Type Definitions (Stage 111).
 *
 * Strongly-typed domain models and API transfer objects for:
 * - Time-Weighted Returns (TWR: exact subperiod geometric compounding & Modified Dietz)
 * - Money-Weighted Returns (MWR / XIRR)
 * - Benchmark comparisons & relative performance
 * - Periodic return calendar matrices
 * - Classified cash flow schedules
 * - Reproducible calculation run snapshots and data quality audits
 */

export type PerformanceMethodology = "EXACT_TWR" | "MODIFIED_DIETZ";

export type MeasurementScope = "PORTFOLIO" | "ACCOUNT";

export type PerformancePeriodType =
  | "1D"
  | "WTD"
  | "MTD"
  | "QTD"
  | "YTD"
  | "1M"
  | "3M"
  | "1Y"
  | "3Y"
  | "5Y"
  | "INCEPTION"
  | "CUSTOM";

export type CashFlowClassification =
  | "EXTERNAL_CONTRIBUTION"
  | "EXTERNAL_WITHDRAWAL"
  | "INTERNAL_SECURITY_TRADE"
  | "INTERNAL_INCOME"
  | "INTERNAL_FEE"
  | "INTERNAL_TRANSFER"
  | "CORPORATE_ACTION_NONCASH";

export type PerformanceStatus = "COMPLETED" | "PARTIAL" | "PENDING" | "FAILED";

export type DataCompletenessStatus =
  | "COMPLETE"
  | "COMPLETE_WITH_STALE_MARKS"
  | "PARTIAL_MISSING_PRICES"
  | "PARTIAL_MISSING_VALUATION"
  | "EMPTY";

export type BenchmarkReturnBasis = "PRICE_RETURN" | "TOTAL_RETURN";

export interface BenchmarkDefinitionDTO {
  benchmark_id: string;
  name: string;
  symbol: string;
  benchmark_type: string;
  return_basis: BenchmarkReturnBasis;
  currency: string;
  description: string;
}

export interface BenchmarkListResponse {
  benchmarks: BenchmarkDefinitionDTO[];
  items?: BenchmarkDefinitionDTO[];
  total: number;
}

export interface BenchmarkComparisonDTO {
  benchmark_id: string;
  benchmark_name: string;
  return_basis: BenchmarkReturnBasis;
  currency: string;
  portfolio_return: string;
  benchmark_return: string;
  arithmetic_difference: string;
  period_start: string;
  period_end: string;
  rebased_portfolio_index_end: string;
  rebased_benchmark_index_end: string;
  warning?: string | null;
}

export interface PerformanceDataQualityDTO {
  completeness: DataCompletenessStatus;
  missing_valuations: number;
  missing_market_prices: number;
  missing_fx_rates: number;
  stale_market_prices: number;
  warnings: string[];
  source_manifest: Record<string, unknown>;
}

export interface SubperiodReturnDTO {
  subperiod_index: number;
  start_time: string;
  end_time: string;
  start_value: string;
  end_value_pre_flow: string;
  net_external_flow: string;
  end_value_post_flow: string;
  subperiod_return: string;
  cumulative_twr_linked: string;
}

export interface PerformanceCashFlowDTO {
  id: string;
  portfolio_id: string;
  account_id?: string | null;
  source_transaction_id?: string | null;
  classification: CashFlowClassification;
  flow_date: string;
  native_amount: string;
  native_currency: string;
  base_amount: string;
  base_currency: string;
  fx_rate: string;
  investor_flow_amount: string;
  portfolio_flow_amount: string;
  description: string;
}

export interface PerformanceResponse {
  run_id: string;
  portfolio_id: string;
  account_id?: string | null;
  methodology: PerformanceMethodology;
  period_type: PerformancePeriodType;
  scope: MeasurementScope;
  period_start: string;
  period_end: string;
  base_currency: string;
  status: PerformanceStatus;
  twr_cumulative?: string | null;
  twr_annualized?: string | null;
  mwr_xirr?: string | null;
  beginning_value: string;
  ending_value: string;
  net_external_flows: string;
  total_contributions: string;
  total_withdrawals: string;
  total_dividends: string;
  total_fees: string;
  investment_gain: string;
  data_quality: PerformanceDataQualityDTO;
  subperiods: SubperiodReturnDTO[];
  dated_flows: PerformanceCashFlowDTO[];
  benchmark_comparison?: BenchmarkComparisonDTO | null;
  calculation_version: string;
  input_hash: string;
  created_at: string;
  completed_at?: string | null;
  error_code?: string | null;
  error_message?: string | null;
}

export interface PerformanceCalculateRequest {
  period_type?: PerformancePeriodType;
  methodology?: PerformanceMethodology;
  custom_start_date?: string;
  custom_end_date?: string;
  benchmark_id?: string;
  account_id?: string;
}

export interface PerformanceSeriesPoint {
  timestamp: string;
  portfolio_value: string;
  indexed_twr: string;
  benchmark_indexed?: string | null;
  cash_flow_amount?: string | null;
  cash_flow_type?: string | null;
}

export interface PerformanceSeriesResponse {
  portfolio_id: string;
  period_type: string;
  base_currency: string;
  points: PerformanceSeriesPoint[];
}

export interface PeriodicReturnDTO {
  period_label: string;
  period_type: "DAILY" | "MONTHLY" | "QUARTERLY" | "ANNUAL" | "YTD" | "TRAILING";
  start_date: string;
  end_date: string;
  return_value?: string | null;
  beginning_value: string;
  ending_value: string;
  net_external_flows: string;
  investment_gain: string;
  is_partial: boolean;
  completeness: DataCompletenessStatus;
}

export interface PeriodicReturnsResponse {
  portfolio_id: string;
  base_currency: string;
  returns: PeriodicReturnDTO[];
}

export interface PerformanceRunSummaryDTO {
  run_id: string;
  portfolio_id: string;
  account_id?: string | null;
  methodology: PerformanceMethodology;
  period_type: PerformancePeriodType;
  scope: MeasurementScope;
  period_start: string;
  period_end: string;
  twr_cumulative?: string | null;
  mwr_xirr?: string | null;
  status: PerformanceStatus;
  input_hash: string;
  created_at: string;
}

export interface PerformanceRunListResponse {
  runs?: PerformanceRunSummaryDTO[];
  items?: PerformanceRunSummaryDTO[];
  total: number;
}
