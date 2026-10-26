/**
 * API Client for ATLAS Company Supply Chain Intelligence (Stage 88).
 * Interacts with /api/v1/companies/{company_id}/supply-chain/* endpoints.
 */

import {
  ConcentrationResponseDTO,
  CustomersListResponseDTO,
  HistoricalTimelineResponseDTO,
  RelationshipEvidenceDTO,
  SuppliersListResponseDTO,
  SupplyChainCoverageResponseDTO,
  SupplyChainFiltersDTO,
  SupplyChainNetworkResponseDTO,
  SupplyChainOverviewResponseDTO,
  SupplyChainRelationshipDTO,
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

export class CompanySupplyChainApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "SUPPLY_CHAIN_API_ERROR") {
    super(message);
    this.name = "CompanySupplyChainApiError";
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
      // Fallback to generic message
    }
    throw new CompanySupplyChainApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

export async function fetchSupplyChainOverview(
  companyId: string,
  signal?: AbortSignal
): Promise<SupplyChainOverviewResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/overview`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<SupplyChainOverviewResponseDTO>(res);
}

export async function fetchSuppliers(
  companyId: string,
  params?: {
    tier?: number;
    relationship_type?: string;
    country?: string;
  },
  signal?: AbortSignal
): Promise<SuppliersListResponseDTO> {
  const query = new URLSearchParams();
  if (params?.tier) query.set("tier", String(params.tier));
  if (params?.relationship_type) query.set("relationship_type", params.relationship_type);
  if (params?.country) query.set("country", params.country);

  const qs = query.toString() ? `?${query.toString()}` : "";
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/suppliers${qs}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<SuppliersListResponseDTO>(res);
}

export async function fetchCustomers(
  companyId: string,
  params?: {
    tier?: number;
    relationship_type?: string;
    country?: string;
  },
  signal?: AbortSignal
): Promise<CustomersListResponseDTO> {
  const query = new URLSearchParams();
  if (params?.tier) query.set("tier", String(params.tier));
  if (params?.relationship_type) query.set("relationship_type", params.relationship_type);
  if (params?.country) query.set("country", params.country);

  const qs = query.toString() ? `?${query.toString()}` : "";
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/customers${qs}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<CustomersListResponseDTO>(res);
}

export async function fetchNetwork(
  companyId: string,
  params?: {
    depth?: number;
    direction?: string;
    relationship_type?: string;
    max_nodes?: number;
    max_edges?: number;
  },
  signal?: AbortSignal
): Promise<SupplyChainNetworkResponseDTO> {
  const query = new URLSearchParams();
  if (params?.depth) query.set("depth", String(params.depth));
  if (params?.direction) query.set("direction", params.direction);
  if (params?.relationship_type) query.set("relationship_type", params.relationship_type);
  if (params?.max_nodes) query.set("max_nodes", String(params.max_nodes));
  if (params?.max_edges) query.set("max_edges", String(params.max_edges));

  const qs = query.toString() ? `?${query.toString()}` : "";
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/network${qs}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<SupplyChainNetworkResponseDTO>(res);
}

export async function fetchRelationshipDetail(
  companyId: string,
  relationshipId: string,
  signal?: AbortSignal
): Promise<SupplyChainRelationshipDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/relationships/${encodeURIComponent(relationshipId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<SupplyChainRelationshipDTO>(res);
}

export async function fetchRelationshipEvidence(
  companyId: string,
  relationshipId: string,
  signal?: AbortSignal
): Promise<RelationshipEvidenceDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/relationships/${encodeURIComponent(relationshipId)}/evidence`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<RelationshipEvidenceDTO[]>(res);
}

export async function fetchConcentration(
  companyId: string,
  signal?: AbortSignal
): Promise<ConcentrationResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/concentration`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<ConcentrationResponseDTO>(res);
}

export async function fetchHistory(
  companyId: string,
  signal?: AbortSignal
): Promise<HistoricalTimelineResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/history`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<HistoricalTimelineResponseDTO>(res);
}

export async function fetchCoverage(
  companyId: string,
  signal?: AbortSignal
): Promise<SupplyChainCoverageResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/coverage`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<SupplyChainCoverageResponseDTO>(res);
}

export async function fetchFilters(
  companyId: string,
  signal?: AbortSignal
): Promise<SupplyChainFiltersDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/supply-chain/filters`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
  });
  return handleResponse<SupplyChainFiltersDTO>(res);
}
