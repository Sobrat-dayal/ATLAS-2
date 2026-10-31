/**
 * Client API interface for ATLAS QuantLib Options Strategy Engine (Stage 142).
 */

import {
  OptionPricingResult,
  QuantCapabilities,
  QuantPricingModelDefinition,
  QuantStrategyLeg,
  ScenarioMatrixResult,
  StrategyComparisonItem,
  StrategyValuationResult,
} from "./types";
import { StrategyTemplateDefinition } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getQuantCapabilities(): Promise<QuantCapabilities> {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/capabilities`);
  if (!res.ok) throw new Error(`Failed to fetch quant capabilities: ${res.statusText}`);
  return res.json();
}

export async function listQuantModels(): Promise<QuantPricingModelDefinition[]> {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/models`);
  if (!res.ok) throw new Error(`Failed to fetch quant models: ${res.statusText}`);
  const data = await res.json();
  return data.models;
}

export async function getQuantModel(modelId: string): Promise<QuantPricingModelDefinition> {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/models/${encodeURIComponent(modelId)}`);
  if (!res.ok) throw new Error(`Failed to fetch model '${modelId}': ${res.statusText}`);
  return res.json();
}

export async function listQuantStrategyTemplates(): Promise<StrategyTemplateDefinition[]> {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/templates`);
  if (!res.ok) throw new Error(`Failed to fetch strategy templates: ${res.statusText}`);
  const data = await res.json();
  return data.templates;
}

export interface SinglePriceRequestPayload {
  contract_id: string;
  evaluation_date?: string;
  spot_price: number;
  risk_free_rate?: number;
  dividend_yield?: number;
  volatility?: number;
  model_id?: string;
  dividend_items?: Array<{ date: string; amount: number }>;
  numerical_steps?: number;
  provider_source_id?: string;
}

export async function priceSingleContract(payload: SinglePriceRequestPayload): Promise<OptionPricingResult> {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/price`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Pricing failed: ${res.statusText}`);
  }
  return res.json();
}

export interface BatchPriceRequestPayload {
  contract_ids: string[];
  evaluation_date?: string;
  spot_price: number;
  risk_free_rate?: number;
  dividend_yield?: number;
  model_id?: string;
  provider_source_id?: string;
}

export async function priceBatchContracts(payload: BatchPriceRequestPayload): Promise<OptionPricingResult[]> {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/price/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Batch pricing failed: ${res.statusText}`);
  }
  const data = await res.json();
  return data.results;
}

export interface AnalyzeStrategyRequestPayload {
  legs: QuantStrategyLeg[];
  spot_price: number;
  evaluation_date?: string;
  risk_free_rate?: number;
  dividend_yield?: number;
  volatility?: number;
  pricing_model_id?: string;
  total_fees?: number;
  generate_pre_expiration?: boolean;
}

export async function analyzeQuantStrategy(
  payload: AnalyzeStrategyRequestPayload
): Promise<StrategyValuationResult> {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/strategies/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Strategy analysis failed: ${res.statusText}`);
  }
  return res.json();
}

export interface ScenarioMatrixRequestPayload {
  legs: QuantStrategyLeg[];
  base_spot: number;
  base_vol: number;
  spot_shifts_pct?: number[];
  vol_shifts_pct?: number[];
  evaluation_date?: string;
  risk_free_rate?: number;
  pricing_model_id?: string;
}

export async function computeScenarioMatrix(
  payload: ScenarioMatrixRequestPayload
): Promise<ScenarioMatrixResult> {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/scenarios/matrix`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Scenario matrix computation failed: ${res.statusText}`);
  }
  return res.json();
}

export interface CompareStrategiesRequestPayload {
  strategies: Array<{
    strategy_id: string;
    strategy_name: string;
    legs: QuantStrategyLeg[];
    total_fees?: number;
  }>;
  spot_price: number;
  evaluation_date?: string;
  volatility?: number;
}

export async function compareQuantStrategies(
  payload: CompareStrategiesRequestPayload
): Promise<StrategyComparisonItem[]> {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/strategies/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Strategy comparison failed: ${res.statusText}`);
  }
  const data = await res.json();
  return data.comparison;
}

export interface SaveStrategyPayload {
  strategy_id?: string;
  title: string;
  underlying_symbol: string;
  legs: QuantStrategyLeg[];
  pricing_model_id?: string;
  evaluation_date?: string;
  total_fees?: number;
  is_private?: boolean;
}

export async function saveUserStrategy(payload: SaveStrategyPayload) {
  const res = await fetch(`${API_BASE}/api/v1/options/quant/strategies`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Save strategy failed: ${res.statusText}`);
  }
  return res.json();
}

