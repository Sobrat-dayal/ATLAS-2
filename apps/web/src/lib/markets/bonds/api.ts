/**
 * Authenticated API client for ATLAS Bonds & Fixed-Income Markets V1 (Stage 61).
 */

import {
  BondDirectoryFilters,
  BondDirectoryResponse,
  BondFilterOptionsResponse,
  BondOverviewResponse,
} from "./types";

export interface BondDirectoryRequestOptions extends BondDirectoryFilters {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}

function getBaseUrl(options?: { baseUrl?: string }): string {
  if (options?.baseUrl) return options.baseUrl;
  return process.env.NEXT_PUBLIC_API_URL || "";
}

function getHeaders(token?: string | null): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Fetch paginated bond securities directory with active filters.
 */
export async function getBondsDirectory(
  options?: BondDirectoryRequestOptions
): Promise<BondDirectoryResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.query && options.query.trim()) {
    searchParams.set("query", options.query.trim());
  }
  if (options?.issuer_type && options.issuer_type !== "all") {
    searchParams.set("issuer_type", options.issuer_type);
  }
  if (options?.issuer_entity_id) {
    searchParams.set("issuer_entity_id", options.issuer_entity_id);
  }
  if (options?.bond_type && options.bond_type !== "all") {
    searchParams.set("bond_type", options.bond_type);
  }
  if (options?.currency && options.currency !== "all") {
    searchParams.set("currency", options.currency);
  }
  if (options?.coupon_type && options.coupon_type !== "all") {
    searchParams.set("coupon_type", options.coupon_type);
  }
  if (options?.maturity_bucket && options.maturity_bucket !== "all") {
    searchParams.set("maturity_bucket", options.maturity_bucket);
  }
  if (options?.limit) {
    searchParams.set("limit", options.limit.toString());
  }
  if (options?.cursor) {
    searchParams.set("cursor", options.cursor);
  }

  const queryString = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/bonds${queryString ? `?${queryString}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: Failed to fetch bond directory`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // Ignore json parse error
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

/**
 * Fetch available filter choices and coverage metrics from bond catalog.
 */
export async function getBondFilterOptions(options?: {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}): Promise<BondFilterOptionsResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/bonds/filters`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: Failed to fetch bond filter options`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // Ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

/**
 * Fetch comprehensive inspection details for a selected bond security.
 */
export async function getBondOverview(
  instrumentEntityId: string,
  options?: {
    token?: string | null;
    baseUrl?: string;
    signal?: AbortSignal;
  }
): Promise<BondOverviewResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/bonds/${encodeURIComponent(instrumentEntityId)}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: Failed to fetch bond overview`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // Ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}
