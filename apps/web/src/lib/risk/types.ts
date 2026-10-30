/**
 * ATLAS Financial Risk Foundation — TypeScript Domain Types (Stage 115).
 *
 * Institutional-Grade Financial Risk Management:
 * Historical & Rolling Volatility, Drawdown Analytics, Benchmark Sensitivity,
 * Covariance Diagnostics, Euler Risk Contributions, and Data Quality Governance.
 */

export type RiskSubjectType = 'PORTFOLIO' | 'BENCHMARK' | 'SECURITY' | 'ACCOUNT';

export type RiskMetricCode =
  | 'HISTORICAL_VOLATILITY'
  | 'HISTORICAL_VARIANCE'
  | 'ROLLING_VOLATILITY'
  | 'MAX_DRAWDOWN'
  | 'CURRENT_DRAWDOWN'
  | 'DRAWDOWN_SERIES'
  | 'WEALTH_INDEX'
  | 'BETA'
  | 'CORRELATION'
  | 'TRACKING_ERROR'
  | 'COVARIANCE_MATRIX'
  | 'SECURITY_RISK_CONTRIBUTION'
  | 'VALUE_AT_RISK'
  | 'EXPECTED_SHORTFALL'
  | 'STRESS_TEST_LOSS'
  | 'MULTI_CURRENCY_RISK';

export type RiskModelType =
  | 'HISTORICAL_SAMPLE'
  | 'ROLLING_SAMPLE'
  | 'CASH_FLOW_ADJUSTED_WEALTH'
  | 'COVARIANCE_PARAMETRIC'
  | 'MULTI_CURRENCY_FACTOR'
  | 'EXPONENTIALLY_WEIGHTED'
  | 'MONTE_CARLO';

export type RiskCalculationStatus = 'PENDING' | 'CALCULATING' | 'COMPLETED' | 'FAILED' | 'STALE';

export type RiskMetricStatus = 'VALID' | 'INSUFFICIENT_DATA' | 'ZERO_VARIANCE' | 'NOT_APPLICABLE' | 'DEGRADED';

export type RiskReturnFrequency = 'DAILY' | 'WEEKLY' | 'MONTHLY';

export type AnnualizationPolicy = 'DAYS_252' | 'DAYS_365' | 'WEEKS_52' | 'MONTHS_12';

export type DataCoverageStatus = 'FULL' | 'ACCEPTABLE' | 'DEGRADED' | 'CRITICAL_GAPS';

export type DrawdownEpisodeStatus = 'RECOVERED' | 'ONGOING';

export type ReturnBasis = 'NET_OF_FEES' | 'GROSS_OF_FEES' | 'TOTAL_RETURN';

export interface CalculateRiskRequestDTO {
  subject_type?: RiskSubjectType;
  subject_id?: string;
  account_id?: string;
  metric_codes?: RiskMetricCode[];
  model_id?: string;
  period_start?: string;
  period_end?: string;
  return_frequency?: RiskReturnFrequency;
  annualization_policy?: AnnualizationPolicy;
  reporting_currency?: string;
  benchmark_id?: string;
  rolling_window_size?: number;
}

export interface RiskMetricDefinitionDTO {
  metric_code: RiskMetricCode;
  display_name: string;
  category: string;
  mathematical_formula: string;
  default_frequency: RiskReturnFrequency;
  annualization_policy: AnnualizationPolicy;
  supported_subject_types: RiskSubjectType[];
  units: string;
  methodology_version: string;
}

export interface RiskModelDefinitionDTO {
  model_id: string;
  model_type: RiskModelType;
  version: string;
  display_name: string;
  description: string;
  allowed_metrics: RiskMetricCode[];
  limitations: string[];
}

export interface RollingObservationDTO {
  window_end: string;
  metric_value: number;
  observation_count: number;
  is_complete: boolean;
}

export interface DrawdownEpisodeDTO {
  episode_id: string;
  peak_date: string;
  peak_value: number;
  trough_date: string;
  trough_value: number;
  max_drawdown: number;
  recovery_date?: string | null;
  time_to_trough_days: number;
  recovery_duration_days?: number | null;
  status: DrawdownEpisodeStatus;
}

export interface BenchmarkSensitivityDTO {
  benchmark_id: string;
  benchmark_symbol: string;
  benchmark_name: string;
  beta?: number | null;
  correlation?: number | null;
  tracking_error_annualized?: number | null;
  benchmark_volatility_annualized?: number | null;
  portfolio_volatility_annualized?: number | null;
  covariance?: number | null;
  matched_observations: number;
  status: RiskMetricStatus;
  warning?: string | null;
}

export interface RiskContributionItemDTO {
  symbol: string;
  name: string;
  category_label: string;
  weight: number;
  marginal_volatility_contribution: number;
  component_volatility_contribution: number;
  percentage_volatility_contribution: number;
  variance_contribution: number;
}

export interface CovarianceDiagnosticsDTO {
  model_name: string;
  dimensions: number;
  is_psd: boolean;
  condition_number: number;
  min_eigenvalue: number;
  regularization_applied: boolean;
  diversification_ratio: number;
  correlation_matrix: number[][];
  symbols: string[];
}

export interface RiskDataCoverageDTO {
  required_observations: number;
  available_observations: number;
  matched_observations: number;
  coverage_ratio: number;
  missing_intervals: string[];
  stale_observations: number;
  unsupported_instruments: string[];
  status: DataCoverageStatus;
}

export interface RiskInputManifestDTO {
  portfolio_valuation_id?: string | null;
  performance_run_id?: string | null;
  benchmark_id?: string | null;
  return_frequency: RiskReturnFrequency;
  annualization_policy: AnnualizationPolicy;
  reporting_currency: string;
  input_hash: string;
}

export interface RiskCalculationRunDTO {
  risk_run_id: string;
  subject_id: string;
  subject_type: RiskSubjectType;
  model_type: RiskModelType;
  model_version: string;
  calculation_as_of: string;
  observation_start: string;
  observation_end: string;
  reporting_currency: string;
  frequency: RiskReturnFrequency;
  annualization_factor: number;
  status: RiskCalculationStatus;
  historical_volatility?: number | null;
  historical_variance?: number | null;
  rolling_volatility_series: RollingObservationDTO[];
  wealth_index_series: [string, number][];
  drawdown_series: [string, number][];
  max_drawdown?: number | null;
  current_drawdown?: number | null;
  drawdown_episodes: DrawdownEpisodeDTO[];
  benchmark_sensitivity?: BenchmarkSensitivityDTO | null;
  model_estimated_variance?: number | null;
  model_estimated_volatility?: number | null;
  security_contributions: RiskContributionItemDTO[];
  covariance_diagnostics?: CovarianceDiagnosticsDTO | null;
  data_coverage: RiskDataCoverageDTO;
  input_manifest: RiskInputManifestDTO;
  warnings: string[];
  created_at: string;
  completed_at?: string | null;
}

export interface PortfolioRiskSummaryDTO {
  portfolio_id: string;
  risk_run_id: string;
  as_of: string;
  reporting_currency: string;
  historical_volatility?: number | null;
  model_volatility?: number | null;
  max_drawdown?: number | null;
  current_drawdown?: number | null;
  beta?: number | null;
  correlation?: number | null;
  tracking_error?: number | null;
  coverage_ratio: number;
  status: RiskCalculationStatus;
  input_hash: string;
}

export interface RiskRunsListDTO {
  items: RiskCalculationRunDTO[];
  total: number;
}

export interface VolatilityResponseDTO {
  historical_volatility_annualized?: number | null;
  historical_variance?: number | null;
  model_volatility_annualized?: number | null;
  annualization_factor: number;
  frequency: RiskReturnFrequency;
  rolling_series: RollingObservationDTO[];
  status: RiskMetricStatus;
}

export interface DrawdownsResponseDTO {
  max_drawdown?: number | null;
  current_drawdown?: number | null;
  drawdown_series: [string, number][];
  wealth_index_series: [string, number][];
  episodes: DrawdownEpisodeDTO[];
  status: RiskMetricStatus;
}

export interface ContributionsResponseDTO {
  model_variance?: number | null;
  model_volatility?: number | null;
  diversification_ratio?: number | null;
  contributions: RiskContributionItemDTO[];
  covariance_diagnostics?: CovarianceDiagnosticsDTO | null;
  status: RiskMetricStatus;
}
