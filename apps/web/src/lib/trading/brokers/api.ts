/**
 * ATLAS Stage 145: Broker Sandbox API client.
 * STRICT SANDBOX ONLY — live execution blocked.
 */

const BASE = "/api/v1/trading/brokers";

export interface SandboxBrokerProvider {
  provider_id: string;
  display_name: string;
  environment: string;
  execution_host: string;
  allowed_hosts: string[];
  status: string;
  is_sandbox: boolean;
  capabilities: {
    supports_order_preview: boolean;
    supports_order_submit: boolean;
    supports_order_cancel: boolean;
    supports_order_read: boolean;
    supports_order_modify: boolean;
  };
}

export interface SandboxBrokerConnection {
  connection_id: string;
  tenant_id: string;
  provider_id: string;
  account_id: string | null;
  environment: string;
  status: string;
  created_at: string;
  last_verified_at: string | null;
}

export async function listBrokerProviders(): Promise<SandboxBrokerProvider[]> {
  const r = await fetch(`${BASE}/providers`);
  if (!r.ok) throw new Error(`listBrokerProviders: ${r.status}`);
  return r.json();
}

export async function listBrokerConnections(): Promise<SandboxBrokerConnection[]> {
  const r = await fetch(`${BASE}/connections`);
  if (!r.ok) throw new Error(`listBrokerConnections: ${r.status}`);
  return r.json();
}

export async function createBrokerConnection(payload: {
  provider_id: string;
  secret: string;
  account_id?: string;
  display_name?: string;
}): Promise<SandboxBrokerConnection> {
  const r = await fetch(`${BASE}/connections`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`createBrokerConnection: ${r.status}`);
  return r.json();
}

export async function verifyBrokerConnection(connectionId: string): Promise<{
  connection_id: string;
  status: string;
  last_verified_at?: string;
}> {
  const r = await fetch(`${BASE}/connections/${connectionId}/verify`, {
    method: "POST",
  });
  if (!r.ok) throw new Error(`verifyBrokerConnection: ${r.status}`);
  return r.json();
}

export async function previewBrokerOrder(payload: {
  connection_id: string;
  symbol: string;
  side: "BUY" | "SELL";
  order_type: string;
  quantity: number;
  limit_price?: number;
  stop_price?: number;
  time_in_force?: string;
}): Promise<any> {
  const r = await fetch(`${BASE}/orders/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`previewBrokerOrder: ${r.status}`);
  return r.json();
}

export async function submitBrokerOrder(payload: {
  connection_id: string;
  symbol: string;
  side: "BUY" | "SELL";
  order_type: string;
  quantity: number;
  limit_price?: number;
  stop_price?: number;
  time_in_force?: string;
}): Promise<any> {
  const r = await fetch(`${BASE}/orders/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`submitBrokerOrder: ${r.status}`);
  return r.json();
}
