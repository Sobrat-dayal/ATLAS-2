/**
 * Client API for Financial and Economic Exposure Engine (Stage 137).
 */

import {
  AtlasExposureResult,
  ExposureAnalysisRun,
  ExposureCoverageSummary,
  ExposureMeasureDefinition,
  ExposureScenarioRun,
  ExposureScenarioShock,
} from "./types";
import { CLIENT_MEASURE_DEFINITIONS } from "./measureDefinitions";

const API_BASE = "/api/v1/intelligence/exposure";

export async function fetchCapabilities(): Promise<Record<string, unknown>> {
  try {
    const res = await fetch(`${API_BASE}/capabilities`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("fetchCapabilities fallback", err);
  }
  return {
    stage: 137,
    system_name: "ATLAS Financial and Economic Exposure Engine",
    version: "1.0.0",
    supported_domains: [
      "COMPANY",
      "PORTFOLIO",
      "GEOGRAPHIC",
      "SECTOR",
      "COMMODITY",
      "CORPORATE_GROUP",
      "SUPPLY_CHAIN",
      "INFRASTRUCTURE",
      "DERIVATIVES",
      "MACRO_ECONOMIC"
    ]
  };
}

export async function fetchMeasures(): Promise<ExposureMeasureDefinition[]> {
  try {
    const res = await fetch(`${API_BASE}/measures`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("fetchMeasures fallback", err);
  }
  return Object.values(CLIENT_MEASURE_DEFINITIONS);
}

export async function runCompanyAnalysis(
  companyRef: Record<string, unknown>,
  segments: Array<Record<string, unknown>>,
  totalConsolidatedRevenue: number,
  currency = "USD",
  period = "FY2024"
): Promise<ExposureAnalysisRun> {
  const payload = {
    company_ref: companyRef,
    segments,
    total_consolidated_revenue: totalConsolidatedRevenue,
    currency,
    period
  };
  const res = await fetch(`${API_BASE}/analyze/company`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error(`Failed to analyze company exposure: ${res.statusText}`);
  }
  return await res.json();
}

export async function runPortfolioAnalysis(
  portfolioRef: Record<string, unknown>,
  positions: Array<Record<string, unknown>>,
  nav?: number,
  currency = "USD"
): Promise<ExposureAnalysisRun> {
  const payload = {
    portfolio_ref: portfolioRef,
    positions,
    nav,
    currency
  };
  const res = await fetch(`${API_BASE}/analyze/portfolio`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error(`Failed to analyze portfolio exposure: ${res.statusText}`);
  }
  return await res.json();
}

export async function runScenarioShock(
  scenarioId: string,
  scenarioName: string,
  shocks: ExposureScenarioShock[],
  positions: Array<Record<string, unknown>>,
  baseCurrency = "USD"
): Promise<ExposureScenarioRun> {
  const payload = {
    scenario_id: scenarioId,
    scenario_name: scenarioName,
    shocks,
    positions,
    base_currency: baseCurrency
  };
  const res = await fetch(`${API_BASE}/scenarios/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error(`Failed to run scenario shock: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchRun(runId: string): Promise<ExposureAnalysisRun> {
  const res = await fetch(`${API_BASE}/runs/${runId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch run ${runId}: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchLineage(exposureId: string): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/lineage/${exposureId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch lineage for ${exposureId}: ${res.statusText}`);
  }
  return await res.json();
}
