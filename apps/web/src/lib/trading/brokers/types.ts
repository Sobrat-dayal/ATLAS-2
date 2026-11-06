/**
 * ATLAS Stage 145: Broker Abstraction — TypeScript types.
 * SANDBOX ONLY — No live broker connections. No real money.
 */

export type BrokerAuthMethod = "API_KEY" | "OAUTH2" | "CLIENT_CREDENTIALS";
export type ConnectionStatus = "CONNECTED" | "DISCONNECTED" | "ERROR" | "PENDING" | "RATE_LIMITED";

export interface BrokerCapabilities {
  supports_market_orders: boolean;
  supports_limit_orders: boolean;
  supports_stop_orders: boolean;
  supports_options: boolean;
  supports_streaming: boolean;
  supports_fractional: boolean;
  base_currency: string;
  asset_classes: string[];
}

export interface BrokerProvider {
  provider_id: string;
  display_name: string;
  description: string;
  auth_method: BrokerAuthMethod;
  sandbox_base_url: string;
  capabilities: BrokerCapabilities;
  is_sandbox: boolean;
  logo_key: string;
}

export interface BrokerConnection {
  connection_id: string;
  tenant_id: string;
  owner_id: string;
  provider_id: string;
  display_name: string;
  status: ConnectionStatus;
  created_at: string;
  last_checked_at?: string;
  error_message?: string;
}

export interface BrokerAccountInfo {
  connection_id: string;
  account_id: string;
  account_type: string;
  currency: string;
  cash: number;
  portfolio_value: number;
  buying_power: number;
  is_sandbox: boolean;
}
