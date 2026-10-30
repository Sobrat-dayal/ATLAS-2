/**
 * ATLAS Portfolios V1 — Optimization & Construction TypeScript Types (Stage 114).
 *
 * Institutional-Grade Quantitative Portfolio Construction:
 * Mean-Variance, Minimum Variance, Efficient Frontier, Maximum Sharpe,
 * Risk Parity, Rebalancing Proposals, and Solver Diagnostics.
 */

export type OptimizationObjective =
  | 'MINIMUM_VARIANCE'
  | 'MEAN_VARIANCE_UTILITY'
  | 'TARGET_RETURN_MIN_VARIANCE'
  | 'MAXIMUM_EXPECTED_RETURN'
  | 'EFFICIENT_FRONTIER'
  | 'MAXIMUM_SHARPE'
  | 'BENCHMARK_TRACKING_ERROR'
  | 'RISK_PARITY';

export type ExpectedReturnModel =
  | 'HISTORICAL_ARITHMETIC_MEAN'
  | 'EXPLICIT_USER_ASSUMPTIONS'
  | 'SHRINKAGE_MEAN';

export type CovarianceModel =
  | 'SAMPLE_COVARIANCE'
  | 'LEDOIT_WOLF_SHRINKAGE'
  | 'DIAGONAL_VARIANCE'
  | 'EXPONENTIALLY_WEIGHTED';

export type ConstraintType =
  | 'FULLY_INVESTED'
  | 'LONG_ONLY'
  | 'SECURITY_WEIGHT_BOUND'
  | 'CASH_WEIGHT_BOUND'
  | 'SECTOR_WEIGHT_BOUND'
  | 'ASSET_CLASS_WEIGHT_BOUND'
  | 'COUNTRY_WEIGHT_BOUND'
  | 'CURRENCY_WEIGHT_BOUND'
  | 'ISSUER_WEIGHT_BOUND'
  | 'BENCHMARK_ACTIVE_WEIGHT_BOUND'
  | 'TURNOVER_LIMIT'
  | 'TRANSACTION_COST_LIMIT'
  | 'VOLATILITY_LIMIT'
  | 'EXPECTED_RETURN_TARGET'
  | 'FROZEN_HOLDING';

export type SolverStatus =
  | 'OPTIMAL'
  | 'OPTIMAL_INACCURATE'
  | 'INFEASIBLE'
  | 'UNBOUNDED'
  | 'NUMERICAL_FAILURE'
  | 'MAX_ITERATIONS_EXCEEDED'
  | 'TIMEOUT';

export type FeasibilityStatus =
  | 'FEASIBLE'
  | 'FEASIBLE_WITH_SLACK_WARNING'
  | 'INFEASIBLE';

export type StudyStatus = 'ACTIVE' | 'ARCHIVED' | 'DRAFT';

export interface OptimizationConstraintRequestDTO {
  constraint_id?: string;
  constraint_type: ConstraintType;
  scope: string;
  target_id?: string;
  lower_bound?: string | number;
  upper_bound?: string | number;
  is_hard: boolean;
  penalty_weight?: string | number;
}

export interface OptimizationConstraintDTO {
  constraint_id: string;
  constraint_type: ConstraintType;
  scope: string;
  target_id?: string;
  lower_bound?: string;
  upper_bound?: string;
  is_hard: boolean;
  penalty_weight: string;
}

export interface CreateOptimizationStudyRequestDTO {
  name: string;
  description?: string;
  default_objective?: OptimizationObjective;
  universe_symbols?: string[];
}

export interface OptimizationStudyDTO {
  study_id: string;
  portfolio_id: string;
  name: string;
  description: string;
  status: StudyStatus;
  default_objective: OptimizationObjective;
  universe_symbols: string[];
  base_currency: string;
  created_at: string;
  updated_at: string;
}

export interface OptimizationStudiesListDTO {
  items: OptimizationStudyDTO[];
  total: number;
}

export interface ExecuteOptimizationRequestDTO {
  study_id?: string;
  objective_type?: OptimizationObjective;
  universe_symbols?: string[];
  expected_return_model?: ExpectedReturnModel;
  covariance_model?: CovarianceModel;
  user_return_assumptions?: Record<string, string | number>;
  constraints?: OptimizationConstraintRequestDTO[];
  risk_aversion?: number;
  risk_free_rate?: number;
  target_return?: number;
  max_turnover?: number;
  proportional_cost_rate?: string | number;
  is_long_only?: boolean;
}

export interface ExpectedReturnEstimateDTO {
  model: ExpectedReturnModel;
  symbols: string[];
  estimates: Record<string, string>;
  annualization_factor: string;
}

export interface CovarianceEstimateDTO {
  model: CovarianceModel;
  symbols: string[];
  matrix: number[][];
  is_psd: boolean;
  condition_number: number;
  regularization_applied: boolean;
}

export interface SolverDiagnosticsDTO {
  solver_name: string;
  solver_version: string;
  problem_type: string;
  status: SolverStatus;
  iterations: number;
  objective_value?: number;
  solve_time_ms: number;
  max_constraint_violation: number;
  active_constraints: string[];
  warnings: string[];
}

export interface CandidatePortfolioDTO {
  weights: Record<string, string>;
  cash_weight: string;
  estimated_return: string;
  estimated_variance: string;
  estimated_volatility: string;
  estimated_sharpe?: string;
  estimated_turnover: string;
  estimated_cost: string;
  feasibility_status: FeasibilityStatus;
  constraint_slacks: Record<string, string>;
}

export interface EfficientFrontierPointDTO {
  target_return: string;
  candidate_weights: Record<string, string>;
  estimated_return: string;
  estimated_volatility: string;
  estimated_sharpe?: string;
  solver_status: SolverStatus;
  is_dominated: boolean;
}

export interface CurrentVsCandidateItemDTO {
  symbol: string;
  name: string;
  category_id: string;
  category_label: string;
  current_weight: string;
  candidate_weight: string;
  weight_delta: string;
  current_value: string;
  candidate_value: string;
  trade_value_delta: string;
  trade_direction: 'BUY' | 'SELL' | 'HOLD';
  estimated_cost: string;
}

export interface SensitivityScenarioDTO {
  scenario_name: string;
  parameter_name: string;
  parameter_value: string;
  estimated_return: string;
  estimated_volatility: string;
  estimated_turnover: string;
  candidate_weights: Record<string, string>;
}

export interface PortfolioOptimizationRunDTO {
  run_id: string;
  study_id?: string;
  portfolio_id: string;
  objective_type: OptimizationObjective;
  base_currency: string;
  universe_symbols: string[];
  baseline_nav: string;
  baseline_weights: Record<string, string>;
  expected_returns: ExpectedReturnEstimateDTO;
  covariance: CovarianceEstimateDTO;
  constraints: OptimizationConstraintDTO[];
  candidate: CandidatePortfolioDTO;
  frontier_points: EfficientFrontierPointDTO[];
  comparisons: CurrentVsCandidateItemDTO[];
  diagnostics: SolverDiagnosticsDTO;
  sensitivity_results: SensitivityScenarioDTO[];
  input_hash: string;
  created_at: string;
  completed_at?: string;
}

export interface OptimizationRunsListDTO {
  items: PortfolioOptimizationRunDTO[];
  total: number;
}

export interface UniverseAssetDTO {
  symbol: string;
  name: string;
  asset_class: string;
  sector: string;
  is_current_holding: boolean;
}

export interface MethodologyDefinitionDTO {
  id: string;
  name: string;
  description: string;
}

export interface OptimizationMethodologiesDTO {
  objectives: MethodologyDefinitionDTO[];
  expected_return_models: MethodologyDefinitionDTO[];
  covariance_models: MethodologyDefinitionDTO[];
  constraint_types: { id: string; name: string }[];
}

export interface ConstraintValidationResultDTO {
  is_feasible: boolean;
  message: string;
  constraint_count: number;
  conflicts: string[];
}
