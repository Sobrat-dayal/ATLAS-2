/**
 * API Client for ATLAS Company Peers and Comparable Company Analysis (Stage 87).
 * Interacts with /api/v1/companies/{company_id}/peers/* endpoints.
 */

import {
  CandidatesResponseDTO,
  CreatePeerGroupRequestDTO,
  HistoricalComparisonRequestDTO,
  HistoricalComparisonResponseDTO,
  MetricCatalogResponseDTO,
  PeerComparisonRequestDTO,
  PeerComparisonResponseDTO,
  PeerMethodologyResponseDTO,
  PeersOverviewResponseDTO,
  UpdatePeerGroupRequestDTO,
  UserPeerGroupDTO,
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

export class CompanyPeersApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "PEERS_API_ERROR") {
    super(message);
    this.name = "CompanyPeersApiError";
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
      // Fallback
    }
    throw new CompanyPeersApiError(errorDetail, res.status, errorCode);
  }
  return res.json();
}

/**
 * 1. Fetch top-level peers overview for the subject company.
 */
export async function fetchPeersOverview(companyId: string): Promise<PeersOverviewResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/overview`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<PeersOverviewResponseDTO>(res);
}

/**
 * 2. Fetch discovered comparable company candidates.
 */
export async function fetchPeerCandidates(
  companyId: string,
  limit: number = 20,
  competitorsOnly: boolean = false
): Promise<CandidatesResponseDTO> {
  const params = new URLSearchParams();
  if (limit) params.set("limit", limit.toString());
  if (competitorsOnly) params.set("competitors_only", "true");

  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/candidates?${params.toString()}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<CandidatesResponseDTO>(res);
}

/**
 * 3. Fetch standard metric catalog.
 */
export async function fetchMetricCatalog(companyId: string): Promise<MetricCatalogResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/metrics`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<MetricCatalogResponseDTO>(res);
}

/**
 * 4. Execute multi-company comparable financial and valuation analysis.
 */
export async function fetchPeerComparison(
  companyId: string,
  request: PeerComparisonRequestDTO
): Promise<PeerComparisonResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/compare`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
  });
  return handleResponse<PeerComparisonResponseDTO>(res);
}

/**
 * 5. Fetch historical multi-period comparison series.
 */
export async function fetchHistoricalComparison(
  companyId: string,
  request: HistoricalComparisonRequestDTO
): Promise<HistoricalComparisonResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/history`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
  });
  return handleResponse<HistoricalComparisonResponseDTO>(res);
}

/**
 * 6. Fetch user-owned and system default peer groups.
 */
export async function fetchUserPeerGroups(companyId: string): Promise<UserPeerGroupDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/groups`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<UserPeerGroupDTO[]>(res);
}

/**
 * 7. Fetch single peer group by ID.
 */
export async function fetchPeerGroup(companyId: string, groupId: string): Promise<UserPeerGroupDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/groups/${groupId}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<UserPeerGroupDTO>(res);
}

/**
 * 8. Create a new user-scoped peer group.
 */
export async function createPeerGroup(
  companyId: string,
  request: CreatePeerGroupRequestDTO
): Promise<UserPeerGroupDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/groups`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
  });
  return handleResponse<UserPeerGroupDTO>(res);
}

/**
 * 9. Update an existing peer group.
 */
export async function updatePeerGroup(
  companyId: string,
  groupId: string,
  request: UpdatePeerGroupRequestDTO
): Promise<UserPeerGroupDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/groups/${groupId}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(request),
  });
  return handleResponse<UserPeerGroupDTO>(res);
}

/**
 * 10. Delete an existing peer group.
 */
export async function deletePeerGroup(companyId: string, groupId: string): Promise<void> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/groups/${groupId}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new CompanyPeersApiError(`Failed to delete peer group: ${res.statusText}`, res.status);
  }
}

/**
 * 11. Fetch peer selection and comparison methodology disclosure.
 */
export async function fetchPeerMethodology(companyId: string): Promise<PeerMethodologyResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/companies/${companyId}/peers/methodology`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<PeerMethodologyResponseDTO>(res);
}
