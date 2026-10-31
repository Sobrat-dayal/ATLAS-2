/**
 * API client functions for Corporate Geography endpoints (Stage 132).
 */

import {
  CompanyComparisonResult,
  CompanyFootprintResponse,
  CompanyFootprintSummary,
  CorporateFacility,
  FacilityEvidenceClaim,
  FacilityStatusHistory,
  MappedCompanySearchResult,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function searchMappedCompanies(query: string = ""): Promise<MappedCompanySearchResult[]> {
  const url = new URL(`${API_BASE}/maps/companies/search`);
  if (query) url.searchParams.set("q", query);

  const res = await fetch(url.toString(), {
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to search mapped companies: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchCompanyFootprint(
  companyId: string,
  options?: {
    includeSubsidiaries?: boolean;
    country?: string;
    asOf?: string;
  }
): Promise<CompanyFootprintResponse> {
  const url = new URL(`${API_BASE}/maps/companies/${encodeURIComponent(companyId)}/footprint`);
  if (options?.includeSubsidiaries !== undefined) {
    url.searchParams.set("include_subsidiaries", String(options.includeSubsidiaries));
  }
  if (options?.country) {
    url.searchParams.set("country", options.country);
  }
  if (options?.asOf) {
    url.searchParams.set("as_of", options.asOf);
  }

  const res = await fetch(url.toString(), {
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to load company footprint: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchCompanySummary(
  companyId: string,
  options?: { includeSubsidiaries?: boolean; asOf?: string }
): Promise<CompanyFootprintSummary> {
  const url = new URL(`${API_BASE}/maps/companies/${encodeURIComponent(companyId)}/summary`);
  if (options?.includeSubsidiaries !== undefined) {
    url.searchParams.set("include_subsidiaries", String(options.includeSubsidiaries));
  }
  if (options?.asOf) {
    url.searchParams.set("as_of", options.asOf);
  }

  const res = await fetch(url.toString(), {
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to load company summary: ${res.statusText}`);
  }
  return res.json();
}

export async function compareCompanyFootprintsApi(
  companyAId: string,
  companyBId: string,
  includeSubsidiaries: boolean = true,
  asOf?: string
): Promise<CompanyComparisonResult> {
  const url = `${API_BASE}/maps/companies/compare`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      company_a_id: companyAId,
      company_b_id: companyBId,
      include_subsidiaries: includeSubsidiaries,
      as_of: asOf,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to compare companies: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchFacilityDetails(facilityId: string): Promise<CorporateFacility> {
  const url = `${API_BASE}/maps/facilities/${encodeURIComponent(facilityId)}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch facility details: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchFacilitySources(facilityId: string): Promise<FacilityEvidenceClaim[]> {
  const url = `${API_BASE}/maps/facilities/${encodeURIComponent(facilityId)}/sources`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch facility sources: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchFacilityHistory(facilityId: string): Promise<FacilityStatusHistory[]> {
  const url = `${API_BASE}/maps/facilities/${encodeURIComponent(facilityId)}/history`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch facility history: ${res.statusText}`);
  }
  return res.json();
}

export async function spatialQueryFacilities(params: {
  query?: string;
  countryCode?: string;
  bbox?: [number, number, number, number];
  asOf?: string;
  limit?: number;
}): Promise<CorporateFacility[]> {
  const url = `${API_BASE}/maps/facilities/spatial-query`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: params.query,
      country_code: params.countryCode,
      bbox: params.bbox,
      as_of: params.asOf,
      limit: params.limit || 200,
    }),
  });
  if (!res.ok) {
    throw new Error(`Spatial query failed: ${res.statusText}`);
  }
  return res.json();
}

export async function aggregateFacilitiesH3Api(params: {
  companyId?: string;
  includeSubsidiaries?: boolean;
  resolution?: number;
  asOf?: string;
}): Promise<any> {
  const url = `${API_BASE}/maps/facilities/aggregate`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      company_id: params.companyId,
      include_subsidiaries: params.includeSubsidiaries ?? true,
      resolution: params.resolution || 4,
      as_of: params.asOf,
    }),
  });
  if (!res.ok) {
    throw new Error(`H3 aggregation failed: ${res.statusText}`);
  }
  return res.json();
}

export async function submitFacilityCorrectionApi(params: {
  facilityId: string;
  correctionType: string;
  details: string;
}): Promise<any> {
  const url = `${API_BASE}/maps/facilities/corrections`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      facility_id: params.facilityId,
      correction_type: params.correctionType,
      details: params.details,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to submit facility correction: ${res.statusText}`);
  }
  return res.json();
}

