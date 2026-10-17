/**
 * API client for Technical Indicators (Stage 69).
 */

import {
  IndicatorCalculationRequest,
  IndicatorCalculationResponse,
  IndicatorCatalogResponse,
  IndicatorDefinition,
} from "./types";

function getBaseApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "";
}

export async function fetchIndicatorCatalog(
  signal?: AbortSignal
): Promise<IndicatorDefinition[]> {
  const url = `${getBaseApiUrl()}/api/v1/charts/indicators/catalog`;
  const res = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch indicator catalog (status ${res.status})`);
  }

  const data = (await res.json()) as IndicatorCatalogResponse;
  return data.indicators || [];
}

export async function calculateIndicators(
  request: IndicatorCalculationRequest,
  signal?: AbortSignal
): Promise<IndicatorCalculationResponse> {
  const url = `${getBaseApiUrl()}/api/v1/charts/indicators/calculate`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(request),
    signal,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    const msg = errorBody?.error?.message || errorBody?.detail || `status ${res.status}`;
    throw new Error(`Failed to calculate indicators: ${msg}`);
  }

  return (await res.json()) as IndicatorCalculationResponse;
}
