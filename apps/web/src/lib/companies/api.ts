/**
 * Authenticated REST API Client for ATLAS Companies V1 (Stage 81).
 */

import {
  CompanyFinancialSummary,
  CompanyMarketSummary,
  CompanyOverviewResponse,
  CompanySearchResponse,
  PaginatedDocumentsResponse,
  PaginatedNewsResponse,
  PaginatedSecuritiesResponse,
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

export class CompanyApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "COMPANY_API_ERROR") {
    super(message);
    this.name = "CompanyApiError";
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
    throw new CompanyApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

export async function searchCompanies(
  query?: string,
  page: number = 1,
  pageSize: number = 20,
  organizationType?: string,
  status?: string,
  signal?: AbortSignal
): Promise<CompanySearchResponse> {
  const base = getBaseApiUrl();
  const params = new URLSearchParams();
  if (query && query.trim()) params.append("query", query.trim());
  params.append("page", String(page));
  params.append("page_size", String(pageSize));
  if (organizationType) params.append("organization_type", organizationType);
  if (status) params.append("status", status);

  const url = `${base}/api/v1/companies?${params.toString()}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<CompanySearchResponse>(res);
}

export async function getCompanyOverview(
  companyId: string,
  signal?: AbortSignal
): Promise<CompanyOverviewResponse> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/companies/${encodeURIComponent(companyId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<CompanyOverviewResponse>(res);
}

export async function getCompanySecurities(
  companyId: string,
  page: number = 1,
  pageSize: number = 25,
  signal?: AbortSignal
): Promise<PaginatedSecuritiesResponse> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/companies/${encodeURIComponent(companyId)}/securities?page=${page}&page_size=${pageSize}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<PaginatedSecuritiesResponse>(res);
}

export async function getCompanyMarketSummary(
  companyId: string,
  signal?: AbortSignal
): Promise<CompanyMarketSummary> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/companies/${encodeURIComponent(companyId)}/market-summary`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<CompanyMarketSummary>(res);
}

export async function getCompanyFinancialSummary(
  companyId: string,
  signal?: AbortSignal
): Promise<CompanyFinancialSummary> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/companies/${encodeURIComponent(companyId)}/financial-summary`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<CompanyFinancialSummary>(res);
}

export async function getCompanyNews(
  companyId: string,
  page: number = 1,
  pageSize: number = 10,
  signal?: AbortSignal
): Promise<PaginatedNewsResponse> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/companies/${encodeURIComponent(companyId)}/news?page=${page}&page_size=${pageSize}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<PaginatedNewsResponse>(res);
}

export async function getCompanyDocuments(
  companyId: string,
  page: number = 1,
  pageSize: number = 10,
  signal?: AbortSignal
): Promise<PaginatedDocumentsResponse> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/companies/${encodeURIComponent(companyId)}/documents?page=${page}&page_size=${pageSize}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<PaginatedDocumentsResponse>(res);
}
