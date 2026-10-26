/**
 * API Client for ATLAS Company Ownership Intelligence (Stage 85).
 */

import {
  BeneficialOwnersResponseDTO,
  CompanyOwnershipOverviewDTO,
  InsiderHoldingsResponseDTO,
  InstitutionalHoldingsResponseDTO,
  OwnershipChangesResponseDTO,
  OwnershipHoldersResponseDTO,
  OwnershipHistoryResponseDTO,
  OwnershipSecuritiesResponseDTO,
  ShareholdingPatternDTO,
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

export class CompanyOwnershipApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "OWNERSHIP_API_ERROR") {
    super(message);
    this.name = "CompanyOwnershipApiError";
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
    throw new CompanyOwnershipApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

export async function fetchOwnershipOverview(
  companyId: string,
  securityId?: string,
  reportingPeriod?: string
): Promise<CompanyOwnershipOverviewDTO> {
  const params = new URLSearchParams();
  if (securityId) params.append("security_id", securityId);
  if (reportingPeriod) params.append("reporting_period", reportingPeriod);

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/ownership/overview${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<CompanyOwnershipOverviewDTO>(res);
}

export async function fetchOwnershipSecurities(companyId: string): Promise<OwnershipSecuritiesResponseDTO> {
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/ownership/securities`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<OwnershipSecuritiesResponseDTO>(res);
}

export async function fetchOwnershipHolders(
  companyId: string,
  options?: {
    securityId?: string;
    reportingPeriod?: string;
    holderCategory?: string;
    limit?: number;
    offset?: number;
  }
): Promise<OwnershipHoldersResponseDTO> {
  const params = new URLSearchParams();
  if (options?.securityId) params.append("security_id", options.securityId);
  if (options?.reportingPeriod) params.append("reporting_period", options.reportingPeriod);
  if (options?.holderCategory) params.append("holder_category", options.holderCategory);
  if (options?.limit) params.append("limit", options.limit.toString());
  if (options?.offset) params.append("offset", options.offset.toString());

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/ownership/holders${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<OwnershipHoldersResponseDTO>(res);
}

export async function fetchInstitutionalHoldings(
  companyId: string,
  options?: {
    securityId?: string;
    reportingPeriod?: string;
    limit?: number;
    offset?: number;
  }
): Promise<InstitutionalHoldingsResponseDTO> {
  const params = new URLSearchParams();
  if (options?.securityId) params.append("security_id", options.securityId);
  if (options?.reportingPeriod) params.append("reporting_period", options.reportingPeriod);
  if (options?.limit) params.append("limit", options.limit.toString());
  if (options?.offset) params.append("offset", options.offset.toString());

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/ownership/institutions${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<InstitutionalHoldingsResponseDTO>(res);
}

export async function fetchInsiderHoldings(
  companyId: string,
  options?: {
    securityId?: string;
    reportingPeriod?: string;
    officersOnly?: boolean;
    directorsOnly?: boolean;
  }
): Promise<InsiderHoldingsResponseDTO> {
  const params = new URLSearchParams();
  if (options?.securityId) params.append("security_id", options.securityId);
  if (options?.reportingPeriod) params.append("reporting_period", options.reportingPeriod);
  if (options?.officersOnly) params.append("officers_only", "true");
  if (options?.directorsOnly) params.append("directors_only", "true");

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/ownership/insiders${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<InsiderHoldingsResponseDTO>(res);
}

export async function fetchBeneficialOwners(
  companyId: string,
  options?: {
    securityId?: string;
    reportingPeriod?: string;
  }
): Promise<BeneficialOwnersResponseDTO> {
  const params = new URLSearchParams();
  if (options?.securityId) params.append("security_id", options.securityId);
  if (options?.reportingPeriod) params.append("reporting_period", options.reportingPeriod);

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/ownership/beneficial${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<BeneficialOwnersResponseDTO>(res);
}

export async function fetchShareholdingPatterns(
  companyId: string,
  reportingPeriod?: string
): Promise<ShareholdingPatternDTO> {
  const params = new URLSearchParams();
  if (reportingPeriod) params.append("reporting_period", reportingPeriod);

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/ownership/patterns${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<ShareholdingPatternDTO>(res);
}

export async function fetchOwnershipHistory(
  companyId: string,
  securityId?: string
): Promise<OwnershipHistoryResponseDTO> {
  const params = new URLSearchParams();
  if (securityId) params.append("security_id", securityId);

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/ownership/history${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<OwnershipHistoryResponseDTO>(res);
}

export async function fetchOwnershipChanges(
  companyId: string,
  options?: {
    currentPeriod?: string;
    priorPeriod?: string;
    securityId?: string;
  }
): Promise<OwnershipChangesResponseDTO> {
  const params = new URLSearchParams();
  if (options?.currentPeriod) params.append("current_period", options.currentPeriod);
  if (options?.priorPeriod) params.append("prior_period", options.priorPeriod);
  if (options?.securityId) params.append("security_id", options.securityId);

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${getBaseApiUrl()}/api/v1/companies/${companyId}/ownership/changes${queryStr}`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<OwnershipChangesResponseDTO>(res);
}
