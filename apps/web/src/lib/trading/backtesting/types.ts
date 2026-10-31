/**
 * ATLAS Stage 143: NautilusTrader Historical Backtesting Engine Types.
 * Strict type safety matching python backend domain.
 */

export type BacktestRunStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";

export type FillModelType =
  | "TOUCHED_BID_ASK"
  | "CROSS_BID_ASK"
  | "VOLUME_CONSTRAINED"
  | "PROBABILISTIC";

export type SlippagePolicy = "NONE" | "FIXED_TICKS" | "FIXED_BPS" | "VOLUME_WEIGHTED";

export type FeeModelType =
  | "ZERO_FEE"
  | "PER_SHARE"
  | "PER_CONTRACT"
  | "MAKER_TAKER"
  | "PERCENTAGE";

export type LatencyModelType = "ZERO_LATENCY" | "FIXED_MS" | "JITTER_DISTRIBUTION";

export type DataGranularity = "1m" | "5m" | "15m" | "1h" | "1d";

export interface HistoricalDatasetManifest {
  dataset_id: string;
  provider_id: string;
  symbol: string;
  instrument_type: "EQUITY" | "OPTION" | "FUTURE" | "FX";
  data_granularity: DataGranularity;
  start_date: string;
  end_date: string;
  records_count: number;
  has_gaps: boolean;
  checksum: string;
  license_id: string;
  currency: string;
  has_options_quotes: boolean;
  is_delisted_inclusive: boolean;
}

export interface AtlasBacktestConfig {
  run_id?: string;
  name?: string;
  owner_id?: string;
  tenant_id?: string;
  is_private?: boolean;
  strategy_id: string;
  strategy_parameters?: Record<string, any>;
  dataset_id: string;
  start_date?: string;
  end_date?: string;
  initial_cash?: number;
  base_currency?: string;
  account_type?: "CASH" | "MARGIN";
  fill_model?: FillModelType;
  slippage_policy?: SlippagePolicy;
  slippage_value?: number;
  fee_model?: FeeModelType;
  commission_rate?: number;
  latency_model?: LatencyModelType;
  latency_ms?: number;
  max_position_size?: number;
  max_order_rate_per_sec?: number;
  random_seed?: number;
  include_replay_events?: boolean;
}

export interface OrderRecord {
  order_id: string;
  run_id: string;
  instrument_id: string;
  order_side: "BUY" | "SELL";
  order_type: "MARKET" | "LIMIT" | "STOP";
  quantity: number;
  limit_price?: number;
  stop_price?: number;
  status: "SUBMITTED" | "ACCEPTED" | "FILLED" | "PARTIALLY_FILLED" | "REJECTED" | "CANCELLED";
  submitted_at: string;
  accepted_at?: string;
  completed_at?: string;
  rejection_reason?: string;
}

export interface FillRecord {
  fill_id: string;
  order_id: string;
  instrument_id: string;
  order_side: "BUY" | "SELL";
  quantity: number;
  fill_price: number;
  commission: number;
  slippage_cost: number;
  fill_timestamp: string;
}

export interface PositionRecord {
  instrument_id: string;
  quantity: number;
  average_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
}

export interface EquitySnapshot {
  timestamp: string;
  equity: number;
  cash: number;
  unrealized_pnl: number;
  realized_pnl: number;
  drawdown_pct: number;
}

export interface TradeRecord {
  trade_id: string;
  instrument_id: string;
  direction: "LONG" | "SHORT";
  entry_time: string;
  entry_price: number;
  exit_time: string;
  exit_price: number;
  quantity: number;
  gross_pnl: number;
  commissions: number;
  slippage_cost: number;
  net_pnl: number;
  holding_period_days: number;
  exit_reason: string;
}

export interface DrawdownMetrics {
  max_drawdown_pct: number;
  max_drawdown_dollar: number;
  peak_equity: number;
  trough_equity: number;
  peak_timestamp?: string;
  trough_timestamp?: string;
  recovery_timestamp?: string;
  is_recovered: boolean;
}

export interface PerformanceMetrics {
  total_return_dollar: number;
  total_return_pct: number;
  cagr_pct: number;
  annualized_volatility_pct: number;
  sharpe_ratio?: number;
  sortino_ratio?: number;
  calmar_ratio?: number;
  profit_factor?: number;
  win_rate_pct: number;
  expectancy_dollar: number;
  total_trades_count: number;
  winning_trades_count: number;
  losing_trades_count: number;
  total_commissions_paid: number;
  total_slippage_cost: number;
  drawdown: DrawdownMetrics;
}

export interface ReplayEvent {
  timestamp: string;
  event_type: "BAR" | "ORDER_SUBMIT" | "ORDER_FILL" | "ORDER_REJECT" | "DIVIDEND" | "EXPIRATION";
  instrument_id: string;
  price: number;
  volume: number;
  description: string;
  portfolio_equity: number;
  unrealized_pnl: number;
}

export interface AtlasStrategyDefinition {
  strategy_id: string;
  name: string;
  category: "EQUITY" | "MOMENTUM" | "MEAN_REVERSION" | "VOLATILITY" | "OPTIONS";
  description: string;
  default_parameters: Record<string, any>;
  supported_instrument_types: string[];
}

export interface ParameterExperimentConfig {
  base_config: AtlasBacktestConfig;
  parameter_grid: Record<string, any[]>;
  metric_target?: string;
}

export interface ParameterExperimentResult {
  experiment_id: string;
  total_combinations: number;
  evaluated_combinations: number;
  ranked_runs: Array<{
    parameters: Record<string, any>;
    metrics: Record<string, any>;
    overfitting_warning: boolean;
  }>;
  overfitting_flag_count: number;
}

export interface WalkForwardFold {
  fold_index: number;
  train_start: string;
  train_end: string;
  test_start: string;
  test_end: string;
  train_sharpe?: number;
  test_sharpe?: number;
  in_sample_return_pct?: number;
  out_of_sample_return_pct?: number;
}

export interface WalkForwardResult {
  experiment_id: string;
  strategy_id: string;
  folds: WalkForwardFold[];
  walk_forward_efficiency_ratio: number;
  is_robust: boolean;
}

export interface AtlasBacktestResult {
  run_id: string;
  status: BacktestRunStatus;
  config: AtlasBacktestConfig;
  performance: PerformanceMetrics;
  equity_curve: EquitySnapshot[];
  trades: TradeRecord[];
  orders: OrderRecord[];
  fills: FillRecord[];
  final_positions: PositionRecord[];
  replay_events?: ReplayEvent[];
  warnings: string[];
  execution_duration_sec: number;
  created_at: string;
  disclaimers: string[];
}

export interface BacktestComparisonResult {
  run_ids: string[];
  compared_metrics: Record<string, Record<string, any>>;
  correlation_matrix: Record<string, Record<string, number>>;
}

export const STAGE_143_DISCLAIMERS = [
  "Hypothetical backtesting results have inherent limitations and do not represent actual trading.",
  "No representation is made that any strategy will achieve profits or losses similar to those shown.",
  "Point-in-time simulations exclude survivorship bias only where delisted security history is licensed and retained.",
  "Backtest analytics are provided for quantitative research and performance attribution purposes only.",
  "Live automated execution and broker routing are strictly prohibited in Stage 143.",
];
