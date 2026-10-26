/**
 * Authenticated REST API Client for Macroeconomic Comparisons & Benchmarking (Stage 93).
 */

import {
  CohortAggregateRequestDTO,
  CohortAggregateResponseDTO,
  ComparableIndicatorDTO,
  ComparisonEligibilityRecordDTO,
  ComparisonMatrixRequestDTO,
  ComparisonMatrixResponseDTO,
  CorrelationAnalysisRequestDTO,
  CorrelationAnalysisResponseDTO,
  DistributionStatisticsRequestDTO,
  DistributionSummaryDTO,
  DivergenceAnalysisRequestDTO,
  DivergenceAnalysisResponseDTO,
  EconomicRankingsRequestDTO,
  EconomicRankingsResponseDTO,
  GeographicCohortDTO,
  HistoricalTrendsRequestDTO,
  HistoricalTrendsResponseDTO,
  MacroCoverageSummaryDTO,
} from "./types";


function getBaseApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

function getHeaders(extra?: Record<string, string>): Record<string, string> {
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...extra,
  };
}

export class MacroComparisonApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "MACRO_COMPARISON_API_ERROR") {
    super(message);
    this.name = "MacroComparisonApiError";
    this.status = status;
    this.code = code;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    let errorCode = "UNKNOWN_ERROR";
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        errorDetail =
          typeof errorJson.detail === "string"
            ? errorJson.detail
            : JSON.stringify(errorJson.detail);
      } else if (errorJson.error?.message) {
        errorDetail = errorJson.error.message;
        errorCode = errorJson.error.code || errorCode;
      }
    } catch {
      // Ignore JSON parse errors for non-JSON responses
    }
    throw new MacroComparisonApiError(errorDetail, res.status, errorCode);
  }
  return res.json();
}

/**
 * Fetch all available comparable economic indicators.
 */
export async function getComparableIndicators(category?: string): Promise<ComparableIndicatorDTO[]> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/comparisons/indicators`);
  if (category) {
    url.searchParams.append("category", category);
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<ComparableIndicatorDTO[]>(res);
}

/**
 * Fetch all sovereign countries and economic areas available for benchmarking.
 */
export async function getComparisonGeographies(): Promise<Array<{
  geography_id: string;
  name: string;
  iso_code: string;
  is_economic_area: boolean;
}>> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/geographies`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<Array<{
    geography_id: string;
    name: string;
    iso_code: string;
    is_economic_area: boolean;
  }>>(res);
}

/**
 * Fetch supported geopolitical and economic cohorts (G7, G20, BRICS, OECD, EU).
 */
export async function getGeographicCohorts(): Promise<GeographicCohortDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/cohorts`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<GeographicCohortDTO[]>(res);
}

/**
 * Validate comparability of a metric across countries.
 */
export async function checkComparisonEligibility(
  metricKind: string,
  geographyIds: string[]
): Promise<ComparisonEligibilityRecordDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/eligibility`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({
      metric_kind: metricKind,
      geography_ids: geographyIds,
    }),
    cache: "no-store",
  });
  return handleResponse<ComparisonEligibilityRecordDTO[]>(res);
}

/**
 * Generate a cross-country economic comparison matrix.
 */
export async function getComparisonMatrix(
  request: ComparisonMatrixRequestDTO
): Promise<ComparisonMatrixResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/matrix`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
    cache: "no-store",
  });
  return handleResponse<ComparisonMatrixResponseDTO>(res);
}

/**
 * Rank countries by a chosen economic indicator with tie-breaking and qualification.
 */
export async function getEconomicRankings(
  request: EconomicRankingsRequestDTO
): Promise<EconomicRankingsResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/rankings`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
    cache: "no-store",
  });
  return handleResponse<EconomicRankingsResponseDTO>(res);
}

/**
 * Compute descriptive statistical distributions (mean, median, IQR, std dev).
 */
export async function getDistributionStatistics(
  request: DistributionStatisticsRequestDTO
): Promise<DistributionSummaryDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/distributions`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
    cache: "no-store",
  });
  return handleResponse<DistributionSummaryDTO>(res);
}

/**
 * Fetch aligned multi-country historical time series, optionally rebased to 100.
 */
export async function getHistoricalTrends(
  request: HistoricalTrendsRequestDTO
): Promise<HistoricalTrendsResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/history`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
    cache: "no-store",
  });
  return handleResponse<HistoricalTrendsResponseDTO>(res);
}

/**
 * Compute pairwise convergence/divergence differentials and ratios.
 */
export async function getDivergenceAnalysis(
  request: DivergenceAnalysisRequestDTO
): Promise<DivergenceAnalysisResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/divergence`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
    cache: "no-store",
  });
  return handleResponse<DivergenceAnalysisResponseDTO>(res);
}

/**
 * Calculate Pearson or Spearman correlation coefficients for aligned series pairs.
 */
export async function getCorrelationAnalysis(
  request: CorrelationAnalysisRequestDTO
): Promise<CorrelationAnalysisResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/correlations`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
    cache: "no-store",
  });
  return handleResponse<CorrelationAnalysisResponseDTO>(res);
}

/**
 * Fetch macro comparison data coverage and source methodology summary.
 */
export async function getMacroCoverageSummary(): Promise<MacroCoverageSummaryDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/coverage`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    cache: "no-store",
  });
  return handleResponse<MacroCoverageSummaryDTO>(res);
}

/**
 * Compute qualified group aggregate or retrieve official published regional aggregate.
 */
export async function getMacroAggregates(
  request: CohortAggregateRequestDTO
): Promise<CohortAggregateResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/comparisons/aggregates`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
    cache: "no-store",
  });
  return handleResponse<CohortAggregateResponseDTO>(res);
}

