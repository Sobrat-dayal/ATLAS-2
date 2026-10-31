/**
 * TypeScript Contracts for ATLAS Options Analytics (Stage 141).
 */

export type OptionType = "CALL" | "PUT";

export type ExerciseStyle = "AMERICAN" | "EUROPEAN" | "BERMUDAN";

export type SettlementMethod = "PHYSICAL" | "CASH";

export type MoneynessState = "IN_THE_MONEY" | "AT_THE_MONEY" | "OUT_OF_THE_MONEY";

export type DeliverableType =
  | "STANDARD_100_SHARES"
  | "NONSTANDARD_CASH_AND_SHARES"
  | "CASH_INDEX"
  | "CUSTOM_LOT_SHARES";

export type ContractAdjustmentStatus = "STANDARD" | "ADJUSTED_CORPORATE_ACTION";

export type LegSide = "LONG_CALL" | "SHORT_CALL" | "LONG_PUT" | "SHORT_PUT";

export type QuoteQualityFlag =
  | "VALID"
  | "ZERO_BID"
  | "CROSSED_MARKET"
  | "LOCKED_MARKET"
  | "STALE_QUOTE"
  | "MISSING_ASK"
  | "WIDE_SPREAD";

export interface OptionDeliverable {
  deliverable_type: DeliverableType;
  shares_count: number;
  cash_amount: number;
  underlying_symbol: string;
  summary: string;
}

export interface AtlasOptionContract {
  option_contract_id: string;
  underlying_instrument_id: string;
  underlying_symbol: string;
  market_id: string;
  exchange_id: string;
  osi_symbol?: string | null;
  option_type: OptionType;
  strike_price: number;
  strike_currency: string;
  expiration_date: string;
  last_trading_date?: string | null;
  exercise_style: ExerciseStyle;
  settlement_method: SettlementMethod;
  contract_multiplier: number;
  deliverable: OptionDeliverable;
  adjustment_status: ContractAdjustmentStatus;
  adjustment_memo?: string | null;
  is_active: boolean;
  corporate_action_id?: string | null;
}

export interface OptionGreeks {
  delta?: number | null;
  gamma?: number | null;
  theta?: number | null;
  vega?: number | null;
  rho?: number | null;
  source_model?: string | null;
  as_of?: string | null;
  theta_unit?: string;
  vega_unit?: string;
}

export interface OptionQuote {
  contract_id: string;
  bid?: number | null;
  ask?: number | null;
  bid_size?: number | null;
  ask_size?: number | null;
  last_price?: number | null;
  last_trade_time?: string | null;
  volume: number;
  open_interest: number;
  open_interest_as_of?: string | null;
  implied_volatility?: number | null;
  greeks?: OptionGreeks | null;
  quote_timestamp: string;
  source_id: string;
  is_delayed: boolean;
  delay_minutes: number;
  quality_flags: QuoteQualityFlag[];
  currency: string;
}

export interface OptionChainRow {
  strike_price: number;
  moneyness: MoneynessState;
  call_contract?: AtlasOptionContract | null;
  call_quote?: OptionQuote | null;
  put_contract?: AtlasOptionContract | null;
  put_quote?: OptionQuote | null;
}

export interface OptionChainResponse {
  underlying_symbol: string;
  underlying_price: number;
  underlying_quote_time: string;
  expiration_date: string;
  days_to_expiration: number;
  rows: OptionChainRow[];
  total_call_volume: number;
  total_put_volume: number;
  total_call_oi: number;
  total_put_oi: number;
  put_call_volume_ratio?: number | null;
  put_call_oi_ratio?: number | null;
  source_id: string;
  is_delayed: boolean;
  delay_minutes: number;
  disclaimers: Record<string, string>;
}

export interface OptionStrategyLeg {
  contract_id: string;
  side: LegSide;
  quantity: number;
  entry_premium: number;
  premium_basis?: string;
  multiplier: number;
  custom_fee?: number;
}

export interface PayoffCoordinate {
  underlying_price: number;
  payoff: number;
  is_breakeven: boolean;
}

export interface OptionStrategyAnalysisResult {
  strategy_name: string;
  underlying_symbol: string;
  expiration_date: string;
  legs: OptionStrategyLeg[];
  net_opening_cash_flow: number;
  is_net_debit: boolean;
  total_estimated_fees: number;
  breakevens: number[];
  max_profit?: number | null;
  max_loss?: number | null;
  is_unbounded_profit: boolean;
  is_unbounded_loss: boolean;
  payoff_curve: PayoffCoordinate[];
  risk_warnings: string[];
  disclaimers: Record<string, string>;
  calculation_version: string;
}

export interface OptionPositionItem {
  portfolio_id: string;
  contract_id: string;
  underlying_symbol: string;
  option_type: string;
  strike_price: number;
  expiration_date: string;
  quantity: number;
  is_long: boolean;
  entry_cost: number;
  current_market_price?: number | null;
  market_value?: number | null;
  multiplier: number;
  unrealized_pnl?: number | null;
}

export interface StrategyTemplateDefinition {
  template_id: string;
  name: string;
  description: string;
  directional_bias: string;
  max_risk_profile: string;
  typical_legs_count: number;
}
