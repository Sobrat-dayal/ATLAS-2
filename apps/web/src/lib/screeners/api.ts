/**
 * Authenticated REST API Client for Financial Screeners V1 (Stage 94).
 */

import {
  CountryOption,
  ExchangeOption,
  ScreenerColumnDefinition,
  ScreenerCoverageResponse,
  ScreenerFilterDefinition,
  ScreenerRunRequest,
  ScreenerRunResponse,
  ScreenerUniverseDefinition,
  SectorOption,
  ValidationResponse,
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

export class ScreenerApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "SCREENER_API_ERROR") {
    super(message);
    this.name = "ScreenerApiError";
    this.status = status;
    this.code = code;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = "An unexpected error occurred.";
    let errorCode = "SCREENER_API_ERROR";
    try {
      const errorJson = await res.json();
      if (typeof errorJson?.detail === "string") {
        errorDetail = errorJson.detail;
      } else if (errorJson?.detail?.message) {
        errorDetail = errorJson.detail.message;
        errorCode = errorJson.detail.code || errorCode;
      } else if (errorJson?.message) {
        errorDetail = errorJson.message;
      }
    } catch {
      errorDetail = `Request failed with status ${res.status} ${res.statusText}`;
    }
    throw new ScreenerApiError(errorDetail, res.status, errorCode);
  }
  return res.json();
}

export async function fetchScreenerUniverses(signal?: AbortSignal): Promise<ScreenerUniverseDefinition[]> {
  const url = `${getBaseApiUrl()}/api/v1/screeners/universes`;
  const res = await fetch(url, { headers: getHeaders(), signal });
  return handleResponse<ScreenerUniverseDefinition[]>(res);
}

export async function fetchScreenerFilters(signal?: AbortSignal): Promise<ScreenerFilterDefinition[]> {
  const url = `${getBaseApiUrl()}/api/v1/screeners/filters`;
  const res = await fetch(url, { headers: getHeaders(), signal });
  return handleResponse<ScreenerFilterDefinition[]>(res);
}

export async function fetchScreenerColumns(signal?: AbortSignal): Promise<ScreenerColumnDefinition[]> {
  const url = `${getBaseApiUrl()}/api/v1/screeners/columns`;
  const res = await fetch(url, { headers: getHeaders(), signal });
  return handleResponse<ScreenerColumnDefinition[]>(res);
}

export async function fetchScreenerExchanges(signal?: AbortSignal): Promise<ExchangeOption[]> {
  const url = `${getBaseApiUrl()}/api/v1/screeners/exchanges`;
  const res = await fetch(url, { headers: getHeaders(), signal });
  return handleResponse<ExchangeOption[]>(res);
}

export async function fetchScreenerGeographies(signal?: AbortSignal): Promise<CountryOption[]> {
  const url = `${getBaseApiUrl()}/api/v1/screeners/geographies`;
  const res = await fetch(url, { headers: getHeaders(), signal });
  return handleResponse<CountryOption[]>(res);
}

export async function fetchScreenerIndustries(signal?: AbortSignal): Promise<SectorOption[]> {
  const url = `${getBaseApiUrl()}/api/v1/screeners/industries`;
  const res = await fetch(url, { headers: getHeaders(), signal });
  return handleResponse<SectorOption[]>(res);
}

export async function validateScreenerQuery(
  req: ScreenerRunRequest,
  signal?: AbortSignal
): Promise<ValidationResponse> {
  const url = `${getBaseApiUrl()}/api/v1/screeners/validate`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(req),
    signal,
  });
  return handleResponse<ValidationResponse>(res);
}

export async function runScreenerQuery(
  req: ScreenerRunRequest,
  signal?: AbortSignal
): Promise<ScreenerRunResponse> {
  const url = `${getBaseApiUrl()}/api/v1/screeners/run`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(req),
    signal,
  });
  return handleResponse<ScreenerRunResponse>(res);
}

export async function fetchScreenerCoverage(signal?: AbortSignal): Promise<ScreenerCoverageResponse> {
  const url = `${getBaseApiUrl()}/api/v1/screeners/coverage`;
  const res = await fetch(url, { headers: getHeaders(), signal });
  return handleResponse<ScreenerCoverageResponse>(res);
}
