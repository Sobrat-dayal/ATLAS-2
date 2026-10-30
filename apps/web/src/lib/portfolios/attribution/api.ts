/**
 * ATLAS Portfolios V1 — Typed API Client for Attribution Analytics (Stage 113).
 */

import {
  AttributionBenchmarkSummaryDTO,
  AttributionCategoryDTO,
  AttributionDataQualityDTO,
  AttributionReconciliationDTO,
  AttributionRunDTO,
  CalculateAttributionRequestDTO,
  CurrencyEffectDTO,
  HistoricalPeriodDTO,
  MultiPeriodLinkedDTO,
  SecurityContributionDTO,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred.';
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail =
          typeof errorJson.detail === 'object'
            ? errorJson.detail.message || JSON.stringify(errorJson.detail)
            : errorJson.detail;
      }
    } catch {
      errorDetail = `Request failed with status ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

/**
 * Fetch the latest attribution run for a portfolio.
 */
export async function fetchPortfolioAttribution(
  portfolioId: string
): Promise<AttributionRunDTO> {
  return request<AttributionRunDTO>(`/portfolios/${portfolioId}/attribution`);
}

/**
 * Execute an on-demand performance attribution calculation with custom parameters.
 */
export async function calculatePortfolioAttribution(
  portfolioId: string,
  payload: CalculateAttributionRequestDTO
): Promise<AttributionRunDTO> {
  return request<AttributionRunDTO>(`/portfolios/${portfolioId}/attribution/calculate`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Fetch historical attribution calculation runs.
 */
export async function listPortfolioAttributionRuns(
  portfolioId: string
): Promise<{ items: AttributionRunDTO[]; total: number }> {
  return request<{ items: AttributionRunDTO[]; total: number }>(
    `/portfolios/${portfolioId}/attribution/runs`
  );
}

/**
 * Fetch attribution effects (allocation, selection, interaction).
 */
export async function fetchAttributionEffects(
  portfolioId: string
): Promise<AttributionCategoryDTO[]> {
  return request<AttributionCategoryDTO[]>(`/portfolios/${portfolioId}/attribution/effects`);
}

/**
 * Fetch security-level return contributions.
 */
export async function fetchAttributionSecurities(
  portfolioId: string
): Promise<SecurityContributionDTO[]> {
  return request<SecurityContributionDTO[]>(`/portfolios/${portfolioId}/attribution/securities`);
}

/**
 * Fetch GICS sector-level decomposition.
 */
export async function fetchAttributionSectors(
  portfolioId: string
): Promise<AttributionCategoryDTO[]> {
  return request<AttributionCategoryDTO[]>(`/portfolios/${portfolioId}/attribution/sectors`);
}

/**
 * Fetch industry group-level decomposition.
 */
export async function fetchAttributionIndustries(
  portfolioId: string
): Promise<AttributionCategoryDTO[]> {
  return request<AttributionCategoryDTO[]>(`/portfolios/${portfolioId}/attribution/industries`);
}

/**
 * Fetch currency decomposition (Local + FX + Cross).
 */
export async function fetchAttributionCurrencies(
  portfolioId: string
): Promise<CurrencyEffectDTO[]> {
  return request<CurrencyEffectDTO[]>(`/portfolios/${portfolioId}/attribution/currencies`);
}

/**
 * Fetch discrete historical period attribution.
 */
export async function fetchAttributionHistory(
  portfolioId: string
): Promise<HistoricalPeriodDTO[]> {
  return request<HistoricalPeriodDTO[]>(`/portfolios/${portfolioId}/attribution/history`);
}

/**
 * Fetch multi-period logarithmic linked attribution (Carino methodology).
 */
export async function fetchAttributionLinked(
  portfolioId: string
): Promise<MultiPeriodLinkedDTO | null> {
  return request<MultiPeriodLinkedDTO | null>(`/portfolios/${portfolioId}/attribution/linked`);
}

/**
 * Fetch attribution mathematical reconciliation.
 */
export async function fetchAttributionReconciliation(
  portfolioId: string
): Promise<AttributionReconciliationDTO> {
  return request<AttributionReconciliationDTO>(
    `/portfolios/${portfolioId}/attribution/reconciliation`
  );
}

/**
 * Fetch attribution data quality and provenance hash.
 */
export async function fetchAttributionDataQuality(
  portfolioId: string
): Promise<AttributionDataQualityDTO> {
  return request<AttributionDataQualityDTO>(
    `/portfolios/${portfolioId}/attribution/data-quality`
  );
}

/**
 * List supported benchmarks for performance attribution.
 */
export async function fetchAttributionBenchmarks(
  portfolioId: string
): Promise<AttributionBenchmarkSummaryDTO[]> {
  return request<AttributionBenchmarkSummaryDTO[]>(
    `/portfolios/${portfolioId}/attribution/benchmarks`
  );
}

