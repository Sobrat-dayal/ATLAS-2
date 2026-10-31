/**
 * TypeScript Contracts for ATLAS QuantLib Options Strategy Engine (Stage 142).
 */

import { ExerciseStyle, LegSide, OptionType } from "../types";

export type PricingModelFamily =
  | "ANALYTIC_BLACK_SCHOLES_MERTON"
  | "BARONE_ADESI_WHALEY"
  | "BJERKSUND_STENSLAND"
  | "BINOMIAL_CRR"
  | "FINITE_DIFFERENCES"
  | "BLACK_76"
  | "BACHELIER";

export interface QuantPricingModelDefinition {
  model_id: string;
  name: string;
  family: PricingModelFamily;
  description: string;
  supported_exercise_styles: ExerciseStyle[];
  handles_discrete_dividends: boolean;
  is_closed_form: boolean;
  convergence_parameter_name?: string | null;
  default_steps: number;
}

export interface QuantModelGreeks {
  delta: number;
  gamma: number;
  theta_per_day: number;
  theta_annual: number;
  vega_per_point: number;
  vega_per_unit: number;
  rho_per_point: number;
  rho_per_bp: number;
  vanna?: number | null;
  volga?: number | null;
  calculation_method: "ANALYTIC" | "CENTRAL_FINITE_DIFFERENCE" | "TERMINAL_SETTLEMENT_CUTOFF";
}

export interface QuantPricingDiagnostics {
  quantlib_version: string;
  engine_class_name: string;
  exercise_type: string;
  elapsed_calculation_ms: number;
  evaluation_date: string;
  expiration_date: string;
  time_to_expiration_years: number;
  steps_computed: number;
  warnings: string[];
}

export interface OptionPricingResult {
  pricing_run_id: string;
  contract_id: string;
  underlying_symbol: string;
  strike_price: number;
  expiration_date: string;
  exercise_style: ExerciseStyle;
  model_id: string;
  theoretical_price: number;
  observed_market_bid?: number | null;
  observed_market_ask?: number | null;
  observed_market_mark?: number | null;
  model_market_difference?: number | null;
  contract_multiplier: number;
  greeks: QuantModelGreeks;
  diagnostics: QuantPricingDiagnostics;
  market_snapshot_id: string;
}

export interface QuantStrategyLeg {
  contract_id: string;
  side: LegSide;
  quantity: number;
  entry_premium: number;
  multiplier: number;
  strike_price: number;
  expiration_date: string;
  option_type: OptionType;
  exercise_style: ExerciseStyle;
  custom_fee: number;
}

export interface PayoffCoordinate {
  underlying_price: number;
  payoff: number;
}

export interface PreExpirationValuationPoint {
  underlying_price: number;
  pre_expiration_npv: number;
  delta: number;
  gamma: number;
  vega: number;
  theta: number;
}

export interface StrategyValuationResult {
  strategy_id: string;
  underlying_symbol: string;
  legs: QuantStrategyLeg[];
  pricing_model_id: string;
  evaluation_date: string;
  total_fees: number;
  net_opening_cash_flow: number;
  break_even_points: number[];
  max_profit?: number | null;
  max_loss?: number | null;
  is_unbounded_loss: boolean;
  aggregate_greeks: QuantModelGreeks;
  expiration_payoff_curve: PayoffCoordinate[];
  pre_expiration_curve?: PreExpirationValuationPoint[] | null;
  risk_warnings: string[];
  disclaimers: string[];
}

export interface ScenarioOutcome {
  spot_price: number;
  spot_pct_change: number;
  volatility: number;
  vol_pct_change: number;
  days_elapsed: number;
  scenario_date: string;
  mark_to_market_value: number;
  pnl_dollar: number;
  pnl_percentage: number;
  aggregate_delta: number;
  aggregate_gamma: number;
  aggregate_vega: number;
  aggregate_theta: number;
}

export interface ScenarioMatrixResult {
  spot_shifts_pct: number[];
  vol_shifts_pct: number[];
  matrix_grid: ScenarioOutcome[][];
  base_spot: number;
  base_vol: number;
  evaluation_date: string;
}

export interface StrategyComparisonItem {
  strategy_id: string;
  strategy_name: string;
  net_debit_credit: number;
  max_profit?: number | null;
  max_loss?: number | null;
  break_even_points: number[];
  net_delta: number;
  net_gamma: number;
  net_vega: number;
  net_theta: number;
  return_on_risk_ratio?: number | null;
  unbounded_risk: boolean;
}

export interface QuantCapabilities {
  stage: number;
  system_name: string;
  quantlib_version: string;
  supported_model_families: string[];
  registered_models_count: number;
  strategy_templates_count: number;
  disclaimers: string[];
  security_policies: {
    tenant_isolation_enforced: boolean;
    zero_fabrication_enforced: boolean;
    multi_expiration_mark_to_market_supported: boolean;
    automated_trading_allowed: boolean;
    broker_order_routing_allowed: boolean;
  };
}
