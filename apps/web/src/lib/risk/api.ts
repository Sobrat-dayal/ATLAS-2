/**
 * ATLAS Financial Risk Foundation — Typed API Client (Stage 115).
 */

import {
  BenchmarkSensitivityDTO,
  CalculateRiskRequestDTO,
  ContributionsResponseDTO,
  DrawdownsResponseDTO,
  PortfolioRiskSummaryDTO,
  RiskCalculationRunDTO,
  RiskDataCoverageDTO,
  RiskInputManifestDTO,
  RiskMetricDefinitionDTO,
  RiskModelDefinitionDTO,
  RiskRunsListDTO,
  VolatilityResponseDTO,
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
    let errorDetail = 'An unexpected error occurred in the risk engine.';
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
 * Retrieves catalog of available risk metrics.
 */
export async function getRiskMetrics(): Promise<RiskMetricDefinitionDTO[]> {
  return request<RiskMetricDefinitionDTO[]>('/risk/metrics');
}

/**
 * Retrieves catalog of available risk models.
 */
export async function getRiskModels(): Promise<RiskModelDefinitionDTO[]> {
  return request<RiskModelDefinitionDTO[]>('/risk/models');
}

/**
 * Triggers an institutional risk calculation run for a portfolio.
 */
export async function calculateRisk(req: CalculateRiskRequestDTO): Promise<RiskCalculationRunDTO> {
  return request<RiskCalculationRunDTO>('/risk/calculations', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Fetches a completed risk calculation run by ID.
 */
export async function getRiskCalculationRun(runId: string): Promise<RiskCalculationRunDTO> {
  return request<RiskCalculationRunDTO>(`/risk/calculations/${runId}`);
}

/**
 * Fetches the input audit manifest and provenance hash for a run.
 */
export async function getRiskInputManifest(runId: string): Promise<RiskInputManifestDTO> {
  return request<RiskInputManifestDTO>(`/risk/calculations/${runId}/sources`);
}

/**
 * Retrieves the latest portfolio risk summary.
 */
export async function getPortfolioRiskSummary(
  portfolioId: string,
  accountId?: string
): Promise<PortfolioRiskSummaryDTO> {
  const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : '';
  return request<PortfolioRiskSummaryDTO>(`/risk/portfolios/${portfolioId}${query}`);
}

/**
 * Retrieves annualized historical and rolling volatility series.
 */
export async function getPortfolioVolatility(
  portfolioId: string,
  options?: { accountId?: string; windowSize?: number }
): Promise<VolatilityResponseDTO> {
  const params = new URLSearchParams();
  if (options?.accountId) params.append('account_id', options.accountId);
  if (options?.windowSize) params.append('window_size', options.windowSize.toString());
  const queryString = params.toString() ? `?${params.toString()}` : '';
  return request<VolatilityResponseDTO>(`/risk/portfolios/${portfolioId}/volatility${queryString}`);
}

/**
 * Retrieves drawdown analysis, wealth index series, and episode breakdown.
 */
export async function getPortfolioDrawdowns(
  portfolioId: string,
  accountId?: string
): Promise<DrawdownsResponseDTO> {
  const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : '';
  return request<DrawdownsResponseDTO>(`/risk/portfolios/${portfolioId}/drawdowns${query}`);
}

/**
 * Retrieves benchmark sensitivity: beta, correlation, tracking error, covariance.
 */
export async function getPortfolioBenchmarkSensitivity(
  portfolioId: string,
  options?: { accountId?: string; benchmarkId?: string }
): Promise<BenchmarkSensitivityDTO> {
  const params = new URLSearchParams();
  if (options?.accountId) params.append('account_id', options.accountId);
  if (options?.benchmarkId) params.append('benchmark_id', options.benchmarkId);
  const queryString = params.toString() ? `?${params.toString()}` : '';
  return request<BenchmarkSensitivityDTO>(`/risk/portfolios/${portfolioId}/benchmark${queryString}`);
}

/**
 * Retrieves security-level Euler risk contributions and covariance diagnostics.
 */
export async function getPortfolioContributions(
  portfolioId: string,
  accountId?: string
): Promise<ContributionsResponseDTO> {
  const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : '';
  return request<ContributionsResponseDTO>(`/risk/portfolios/${portfolioId}/contributions${query}`);
}

/**
 * Retrieves data coverage, missing intervals, and input completeness audit.
 */
export async function getPortfolioDataQuality(
  portfolioId: string,
  accountId?: string
): Promise<RiskDataCoverageDTO> {
  const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : '';
  return request<RiskDataCoverageDTO>(`/risk/portfolios/${portfolioId}/quality${query}`);
}

/**
 * Retrieves historical risk calculation runs for auditing.
 */
export async function getPortfolioRiskRuns(
  portfolioId: string,
  limit: number = 20
): Promise<RiskRunsListDTO> {
  return request<RiskRunsListDTO>(`/risk/portfolios/${portfolioId}/runs?limit=${limit}`);
}

