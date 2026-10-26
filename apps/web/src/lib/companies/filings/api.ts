/**
 * API Client for ATLAS Company Filings Intelligence (Stage 86).
 * Interacts with /api/v1/companies/{company_id}/filings/* endpoints.
 */

import {
  FilingCatalogResponseDTO,
  FilingComparisonResponseDTO,
  FilingContentDTO,
  FilingCoverageDTO,
  FilingDetailDTO,
  FilingDocumentDTO,
  FilingSearchResponseDTO,
  FilingSourceReferenceDTO,
  FilingsOverviewSummaryDTO,
  XBRLFactsResponseDTO,
} from "./types";

function getBaseApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

function getHeaders(extra?: Record<string, string>): Record<string, string> {
  const token = typeof window !== "undefined" ? localStorage.getItem("atlas_auth_token") : null;
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

export class CompanyFilingsApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "FILINGS_API_ERROR") {
    super(message);
    this.name = "CompanyFilingsApiError";
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
      // Fallback to generic status text
    }
    throw new CompanyFilingsApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

export async function fetchFilingsOverview(companyId: string): Promise<FilingsOverviewSummaryDTO> {
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings/overview`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FilingsOverviewSummaryDTO>(res);
}

export async function fetchFilingCoverage(companyId: string): Promise<FilingCoverageDTO> {
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings/coverage`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FilingCoverageDTO>(res);
}

export async function fetchFilingCatalog(
  companyId: string,
  options?: {
    formType?: string;
    category?: string;
    filedFrom?: string;
    filedTo?: string;
    reportingPeriod?: string;
    isAmendment?: boolean;
    limit?: number;
    offset?: number;
  }
): Promise<FilingCatalogResponseDTO> {
  const params = new URLSearchParams();
  if (options?.formType) params.append("form_type", options.formType);
  if (options?.category) params.append("category", options.category);
  if (options?.filedFrom) params.append("filed_from", options.filedFrom);
  if (options?.filedTo) params.append("filed_to", options.filedTo);
  if (options?.reportingPeriod) params.append("reporting_period", options.reportingPeriod);
  if (options?.isAmendment !== undefined) params.append("is_amendment", String(options.isAmendment));
  if (options?.limit !== undefined) params.append("limit", String(options.limit));
  if (options?.offset !== undefined) params.append("offset", String(options.offset));

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FilingCatalogResponseDTO>(res);
}

export async function searchFilings(
  companyId: string,
  query: string,
  category?: string,
  limit?: number
): Promise<FilingSearchResponseDTO> {
  const params = new URLSearchParams();
  params.append("q", query);
  if (category) params.append("category", category);
  if (limit) params.append("limit", String(limit));

  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings/search?${params.toString()}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FilingSearchResponseDTO>(res);
}

export async function fetchFilingDetail(companyId: string, filingId: string): Promise<FilingDetailDTO> {
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings/${filingId}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FilingDetailDTO>(res);
}

export async function fetchFilingDocuments(companyId: string, filingId: string): Promise<FilingDocumentDTO[]> {
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings/${filingId}/documents`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FilingDocumentDTO[]>(res);
}

export async function fetchFilingContent(
  companyId: string,
  filingId: string,
  documentId?: string
): Promise<FilingContentDTO> {
  const params = new URLSearchParams();
  if (documentId) params.append("document_id", documentId);
  const queryStr = params.toString() ? `?${params.toString()}` : "";

  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings/${filingId}/content${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FilingContentDTO>(res);
}

export async function fetchFilingFacts(
  companyId: string,
  filingId: string,
  conceptPrefix?: string
): Promise<XBRLFactsResponseDTO> {
  const params = new URLSearchParams();
  if (conceptPrefix) params.append("concept_prefix", conceptPrefix);
  const queryStr = params.toString() ? `?${params.toString()}` : "";

  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings/${filingId}/facts${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<XBRLFactsResponseDTO>(res);
}

export async function fetchFilingSources(companyId: string, filingId: string): Promise<FilingSourceReferenceDTO> {
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings/${filingId}/sources`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FilingSourceReferenceDTO>(res);
}

export async function compareFilings(
  companyId: string,
  leftFilingId: string,
  rightFilingId: string
): Promise<FilingComparisonResponseDTO> {
  const params = new URLSearchParams();
  params.append("left_filing_id", leftFilingId);
  params.append("right_filing_id", rightFilingId);

  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/filings/compare?${params.toString()}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FilingComparisonResponseDTO>(res);
}
