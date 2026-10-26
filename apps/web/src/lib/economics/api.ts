/**
 * Authenticated REST API Client for ATLAS Economics V1 (Stage 89).
 */

import {
  EconomicCoverageResponseDTO,
  EconomicGeographyDTO,
  EconomicIndicatorDTO,
  EconomicSeriesDTO,
  EconomicSeriesObservationsResponseDTO,
  EconomicVintageDTO,
  GlobalMacroOverviewResponseDTO,
  IndicatorCategory,
  TransformationDefinitionDTO,
  TransformationType,
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

export class EconomicsApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "ECONOMICS_API_ERROR") {
    super(message);
    this.name = "EconomicsApiError";
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
        errorDetail = typeof errorJson.detail === "string" ? errorJson.detail : JSON.stringify(errorJson.detail);
      } else if (errorJson.error?.message) {
        errorDetail = errorJson.error.message;
        errorCode = errorJson.error.code || errorCode;
      }
    } catch {
      // Use status text fallback
    }
    throw new EconomicsApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

/**
 * Fetch global macroeconomic overview snapshot for all major economies.
 */
export async function getGlobalMacroOverview(asOfDate?: string): Promise<GlobalMacroOverviewResponseDTO> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/overview`);
  if (asOfDate) {
    url.searchParams.set("as_of_date", asOfDate);
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<GlobalMacroOverviewResponseDTO>(res);
}

/**
 * Fetch all available indicator categories.
 */
export async function getIndicatorCategories(): Promise<IndicatorCategory[]> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/categories`);
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<IndicatorCategory[]>(res);
}

/**
 * Fetch canonical economic indicator catalog.
 */
export async function getEconomicIndicators(category?: IndicatorCategory): Promise<EconomicIndicatorDTO[]> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/indicators`);
  if (category) {
    url.searchParams.set("category", category);
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicIndicatorDTO[]>(res);
}

/**
 * Fetch a single economic indicator by ID.
 */
export async function getEconomicIndicator(indicatorId: string): Promise<EconomicIndicatorDTO> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/indicators/${encodeURIComponent(indicatorId)}`);
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicIndicatorDTO>(res);
}

/**
 * Discover source economic series.
 */
export async function getEconomicSeries(params?: {
  geography_id?: string;
  category?: IndicatorCategory;
  indicator_id?: string;
}): Promise<EconomicSeriesDTO[]> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/series`);
  if (params?.geography_id) {
    url.searchParams.set("geography_id", params.geography_id);
  }
  if (params?.category) {
    url.searchParams.set("category", params.category);
  }
  if (params?.indicator_id) {
    url.searchParams.set("indicator_id", params.indicator_id);
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicSeriesDTO[]>(res);
}

/**
 * Fetch economic series metadata by series ID.
 */
export async function getEconomicSeriesById(seriesId: string): Promise<EconomicSeriesDTO> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/series/${encodeURIComponent(seriesId)}`);
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicSeriesDTO>(res);
}

/**
 * Fetch bounded historical observations for a series, with optional mathematical transformation.
 */
export async function getEconomicObservations(
  seriesId: string,
  params?: {
    transformation?: TransformationType;
    start_period?: string;
    end_period?: string;
    as_of_date?: string;
    limit?: number;
  }
): Promise<EconomicSeriesObservationsResponseDTO> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/series/${encodeURIComponent(seriesId)}/observations`);
  if (params?.transformation) {
    url.searchParams.set("transformation", params.transformation);
  }
  if (params?.start_period) {
    url.searchParams.set("start_period", params.start_period);
  }
  if (params?.end_period) {
    url.searchParams.set("end_period", params.end_period);
  }
  if (params?.as_of_date) {
    url.searchParams.set("as_of_date", params.as_of_date);
  }
  if (params?.limit) {
    url.searchParams.set("limit", params.limit.toString());
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicSeriesObservationsResponseDTO>(res);
}

/**
 * Fetch official revision vintages for a series.
 */
export async function getEconomicVintages(
  seriesId: string,
  referencePeriod?: string
): Promise<EconomicVintageDTO[]> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/series/${encodeURIComponent(seriesId)}/vintages`);
  if (referencePeriod) {
    url.searchParams.set("reference_period", referencePeriod);
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicVintageDTO[]>(res);
}

/**
 * Fetch supported geographic entities (G6 major economies and economic areas).
 */
export async function getEconomicGeographies(): Promise<EconomicGeographyDTO[]> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/geographies`);
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicGeographyDTO[]>(res);
}

/**
 * Fetch economics system coverage metrics and provider status.
 */
export async function getEconomicCoverage(): Promise<EconomicCoverageResponseDTO> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/coverage`);
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EconomicCoverageResponseDTO>(res);
}

/**
 * Fetch supported versioned mathematical transformations.
 */
export async function getTransformations(): Promise<TransformationDefinitionDTO[]> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/economics/transformations`);
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<TransformationDefinitionDTO[]>(res);
}
