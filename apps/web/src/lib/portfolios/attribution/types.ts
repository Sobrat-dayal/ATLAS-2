/**
 * ATLAS Portfolios V1 — Attribution Analytics TypeScript Types (Stage 113).
 *
 * Institutional-Grade Performance Attribution: Brinson-Fachler, BHB,
 * Security Return Contributions, Multi-Period Carino Linking, Currency Decomposition,
 * and Mathematical Reconciliation.
 */

export type AttributionMethod =
  | 'BRINSON_FACHLER'
  | 'BRINSON_HOOD_BEEBOWER'
  | 'ABSOLUTE_RETURN_CONTRIBUTION'
  | 'MULTIPERIOD_CARINO_LINKED'
  | 'CURRENCY_LOCAL_FX_DECOMPOSITION';

export type AttributionDimension =
  | 'SECTOR'
  | 'INDUSTRY'
  | 'ASSET_CLASS'
  | 'GEOGRAPHY'
  | 'CURRENCY';

export type ReconciliationStatus =
  | 'RECONCILED'
  | 'RECONCILED_WITH_ROUNDING_TOLERANCE'
  | 'PARTIAL_COVERAGE'
  | 'UNRECONCILED';

export type AttributionCompleteness =
  | 'FULL_COVERAGE'
  | 'PARTIAL_COVERAGE'
  | 'BENCHMARK_CONSTITUENTS_MISSING'
  | 'UNMAPPED_CATEGORIES';

export interface AttributionCategoryDTO {
  category_id: string;
  category_label: string;
  portfolio_weight: string;
  benchmark_weight: string;
  weight_delta: string;
  portfolio_return: string;
  benchmark_return: string;
  return_delta: string;
  allocation_effect: string;
  selection_effect: string;
  interaction_effect: string;
  total_effect: string;
  is_residual: boolean;
  position_count: number;
  sub_industries?: AttributionCategoryDTO[];
}

export interface SecurityContributionDTO {
  symbol: string;
  name: string;
  category_id: string;
  category_label: string;
  portfolio_weight: string;
  security_return: string;
  return_contribution: string;
  rank: number;
}

export interface CurrencyEffectDTO {
  currency: string;
  portfolio_weight: string;
  local_return: string;
  fx_return: string;
  cross_product_effect: string;
  total_base_return: string;
  total_currency_effect: string;
}

export interface HistoricalPeriodDTO {
  period_index: number;
  period_label: string;
  start_date: string;
  end_date: string;
  portfolio_return: string;
  benchmark_return: string;
  active_return: string;
  allocation_effect: string;
  selection_effect: string;
  interaction_effect: string;
  carino_weight: string;
}

export interface MultiPeriodLinkedDTO {
  linking_method: string;
  period_count: number;
  compound_portfolio_return: string;
  compound_benchmark_return: string;
  compound_active_return: string;
  linked_allocation_effect: string;
  linked_selection_effect: string;
  linked_interaction_effect: string;
  linked_residual: string;
  is_reconciled: boolean;
  periods: HistoricalPeriodDTO[];
}

export interface AttributionReconciliationDTO {
  portfolio_return: string;
  reconstructed_portfolio_return: string;
  portfolio_reconciled: boolean;
  benchmark_return: string;
  reconstructed_benchmark_return: string;
  benchmark_reconciled: boolean;
  active_return: string;
  total_attributed: string;
  attribution_reconciled: boolean;
  residual: string;
  security_contributions_sum: string;
  security_contributions_reconciled: boolean;
  status: ReconciliationStatus;
  tolerance: string;
}

export interface AttributionDataQualityDTO {
  completeness: AttributionCompleteness;
  portfolio_holdings_coverage_ratio: string;
  benchmark_constituent_coverage_ratio: string;
  taxonomy_coverage_ratio: string;
  missing_securities_count: number;
  unmapped_sector_weight: string;
  input_hash: string;
  warnings: string[];
}

export interface AttributionRunDTO {
  id: string;
  portfolio_id: string;
  account_id?: string | null;
  benchmark_id: string;
  benchmark_name: string;
  period_start: string;
  period_end: string;
  reporting_currency: string;
  attribution_method: AttributionMethod;
  methodology_version: string;
  classification_dimension: AttributionDimension;
  taxonomy_id: string;
  taxonomy_version: string;
  portfolio_return: string;
  benchmark_return: string;
  active_return: string;
  total_allocation_effect: string;
  total_selection_effect: string;
  total_interaction_effect: string;
  total_attributed: string;
  reconciliation_residual: string;
  category_results: AttributionCategoryDTO[];
  security_contributions: SecurityContributionDTO[];
  top_contributors: SecurityContributionDTO[];
  top_detractors: SecurityContributionDTO[];
  currency_effects: CurrencyEffectDTO[];
  reconciliation: AttributionReconciliationDTO;
  data_quality: AttributionDataQualityDTO;
  multi_period?: MultiPeriodLinkedDTO | null;
  created_at: string;
  completed_at?: string | null;
}

export interface AttributionBenchmarkSummaryDTO {
  benchmark_id: string;
  name: string;
  symbol: string;
  benchmark_type: string;
  return_basis: string;
  currency: string;
  description: string;
  has_constituent_data: boolean;
}

export interface CalculateAttributionRequestDTO {
  benchmark_id?: string;
  account_id?: string | null;
  attribution_method?: AttributionMethod;
  classification_dimension?: AttributionDimension;
  period_start?: string;
  period_end?: string;
  reporting_currency?: string;
  include_currency_decomposition?: boolean;
  include_multi_period_linking?: boolean;
  multi_period_periods?: number;
}

