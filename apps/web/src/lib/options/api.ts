/**
 * Client API interface for ATLAS Options Analytics (Stage 141).
 */

import {
  AtlasOptionContract,
  OptionChainResponse,
  OptionPositionItem,
  OptionQuote,
  OptionStrategyAnalysisResult,
  OptionStrategyLeg,
  StrategyTemplateDefinition,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getOptionsCapabilities() {
  const res = await fetch(`${API_BASE}/api/v1/options/capabilities`);
  if (!res.ok) throw new Error(`Failed to fetch capabilities: ${res.statusText}`);
  return res.json();
}

export async function getOptionUnderlyings(): Promise<
  Array<{
    symbol: string;
    name: string;
    market_id: string;
    spot_price: number;
    quote_time: string;
    currency: string;
    has_adjusted_contracts: boolean;
  }>
> {
  const res = await fetch(`${API_BASE}/api/v1/options/underlyings`);
  if (!res.ok) throw new Error(`Failed to fetch underlyings: ${res.statusText}`);
  const data = await res.json();
  return data.underlyings;
}

export async function getOptionExpirations(symbol: string): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/v1/options/expirations/${encodeURIComponent(symbol)}`);
  if (!res.ok) throw new Error(`Failed to fetch expirations: ${res.statusText}`);
  const data = await res.json();
  return data.expirations;
}

export async function getOptionChain(
  symbol: string,
  expirationDate: string,
  tenantId?: string,
  providerSourceId?: string
): Promise<OptionChainResponse> {
  const params = new URLSearchParams();
  if (tenantId) params.append("tenant_id", tenantId);
  if (providerSourceId) params.append("provider_source_id", providerSourceId);

  const url = `${API_BASE}/api/v1/options/chain/${encodeURIComponent(symbol)}/${encodeURIComponent(expirationDate)}?${params.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to fetch option chain: ${res.statusText}`);
  }
  return res.json();
}

export async function getOptionContract(contractId: string): Promise<AtlasOptionContract> {
  const res = await fetch(`${API_BASE}/api/v1/options/contract/${encodeURIComponent(contractId)}`);
  if (!res.ok) throw new Error(`Failed to fetch contract: ${res.statusText}`);
  return res.json();
}

export async function getOptionQuote(
  contractId: string,
  tenantId?: string,
  providerSourceId?: string
): Promise<OptionQuote> {
  const params = new URLSearchParams();
  if (tenantId) params.append("tenant_id", tenantId);
  if (providerSourceId) params.append("provider_source_id", providerSourceId);

  const res = await fetch(`${API_BASE}/api/v1/options/quote/${encodeURIComponent(contractId)}?${params.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch quote: ${res.statusText}`);
  return res.json();
}

export async function getVolatilitySmile(
  symbol: string,
  expirationDate: string
): Promise<{
  underlying_symbol: string;
  expiration_date: string;
  smile_points: Array<{ strike_price: number; implied_volatility: number; option_type: string }>;
  skew_metrics?: {
    put_skew_25d?: number;
    call_skew_25d?: number;
    risk_reversal_25d?: number;
  };
}> {
  const res = await fetch(
    `${API_BASE}/api/v1/options/volatility/smile/${encodeURIComponent(symbol)}/${encodeURIComponent(expirationDate)}`
  );
  if (!res.ok) throw new Error(`Failed to fetch smile: ${res.statusText}`);
  return res.json();
}

export async function getVolatilityTermStructure(symbol: string): Promise<{
  underlying_symbol: string;
  points: Array<{ expiration_date: string; days_to_expiration: number; atm_iv: number }>;
}> {
  const res = await fetch(`${API_BASE}/api/v1/options/volatility/term-structure/${encodeURIComponent(symbol)}`);
  if (!res.ok) throw new Error(`Failed to fetch term structure: ${res.statusText}`);
  return res.json();
}

export async function getStrikeActivity(
  symbol: string,
  expirationDate: string
): Promise<{
  underlying_symbol: string;
  expiration_date: string;
  activity_by_strike: Array<{
    strike_price: number;
    call_volume: number;
    put_volume: number;
    call_open_interest: number;
    put_open_interest: number;
    total_volume: number;
    total_open_interest: number;
  }>;
}> {
  const res = await fetch(
    `${API_BASE}/api/v1/options/activity/${encodeURIComponent(symbol)}/${encodeURIComponent(expirationDate)}`
  );
  if (!res.ok) throw new Error(`Failed to fetch strike activity: ${res.statusText}`);
  return res.json();
}

export async function getStrategyTemplates(): Promise<StrategyTemplateDefinition[]> {
  const res = await fetch(`${API_BASE}/api/v1/options/strategies/templates`);
  if (!res.ok) throw new Error(`Failed to fetch templates: ${res.statusText}`);
  const data = await res.json();
  return data.templates;
}

export async function analyzeOptionStrategy(payload: {
  strategy_name?: string;
  underlying_symbol?: string;
  expiration_date?: string;
  legs: OptionStrategyLeg[];
  total_fees?: number;
}): Promise<OptionStrategyAnalysisResult> {
  const res = await fetch(`${API_BASE}/api/v1/options/strategies/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Analysis failed: ${res.statusText}`);
  }
  return res.json();
}

export async function getUserOptionPositions(portfolioId: string): Promise<OptionPositionItem[]> {
  const res = await fetch(`${API_BASE}/api/v1/options/portfolios/${encodeURIComponent(portfolioId)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to fetch positions: ${res.statusText}`);
  }
  const data = await res.json();
  return data.positions;
}

export async function getUnderlyingAdjustments(symbol: string): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/v1/options/adjustments/${encodeURIComponent(symbol)}`);
  if (!res.ok) throw new Error(`Failed to fetch adjustments: ${res.statusText}`);
  const data = await res.json();
  return data.adjustments;
}

