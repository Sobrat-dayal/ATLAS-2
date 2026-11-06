/**
 * ATLAS Stage 144: Paper Trading Engine — TypeScript domain types.
 * All accounts are PAPER/SIMULATED only. No real broker. No real money.
 */

export type PaperOrderStatus = "PENDING" | "OPEN" | "PARTIAL" | "FILLED" | "CANCELLED" | "REJECTED" | "EXPIRED";
export type PaperOrderSide = "BUY" | "SELL";
export type PaperOrderType = "MARKET" | "LIMIT" | "STOP" | "STOP_LIMIT" | "TRAILING_STOP";
export type AssetClass = "EQUITY" | "OPTION" | "FUTURE" | "FOREX" | "CRYPTO";
export type TimeInForce = "DAY" | "GTC" | "IOC" | "FOK" | "GTD";

export interface PaperFill {
  fill_id: string;
  order_id: string;
  symbol: string;
  side: PaperOrderSide;
  filled_qty: number;
  fill_price: number;
  fee: number;
  slippage: number;
  timestamp: string;
}

export interface PaperOrder {
  order_id: string;
  client_order_id: string;
  account_id: string;
  symbol: string;
  asset_class: AssetClass;
  side: PaperOrderSide;
  order_type: PaperOrderType;
  quantity: number;
  limit_price?: number;
  stop_price?: number;
  time_in_force: TimeInForce;
  status: PaperOrderStatus;
  filled_qty: number;
  avg_fill_price?: number;
  total_fee: number;
  created_at: string;
  updated_at: string;
  fills: PaperFill[];
}

export interface PaperPosition {
  position_id: string;
  account_id: string;
  symbol: string;
  asset_class: AssetClass;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
  cost_basis: number;
  updated_at: string;
}

export interface PaperAccount {
  account_id: string;
  tenant_id: string;
  owner_id: string;
  name: string;
  currency: string;
  initial_cash: number;
  cash: number;
  buying_power: number;
  margin_used: number;
  portfolio_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
  daily_realized_pnl: number;
  kill_switch_active: boolean;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AccountSnapshot {
  snapshot_id: string;
  account_id: string;
  cash: number;
  portfolio_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
  timestamp: string;
}

export interface PaperStrategyDeployment {
  deployment_id: string;
  account_id: string;
  strategy_class: string;
  parameters: Record<string, unknown>;
  status: "ACTIVE" | "STOPPED" | "FAILED";
  deployed_at: string;
}
