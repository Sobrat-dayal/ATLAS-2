/**
 * Authenticated API client for ATLAS Cross-Asset Markets V1 (Stage 65).
 */

import {
  CrossAssetMode,
  CrossAssetOptionsResponse,
  CrossAssetOverviewResponse,
  CrossAssetUniverseResponse,
  CrossAssetWindow,
} from "./types";

export interface CrossAssetQueryParams {
  universe_id?: string;
  mode?: CrossAssetMode;
  window?: CrossAssetWindow;
  symbols?: string;
}

export interface CrossAssetRequestOptions extends CrossAssetQueryParams {
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
 * Fetch supported canonical cross-asset universes.
 */
export async function getCrossAssetUniverses(
  options?: { token?: string | null; baseUrl?: string; signal?: AbortSignal }
): Promise<CrossAssetUniverseResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/cross-asset/universes`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorDetail = `Failed to fetch cross-asset universes (${res.status})`;
    try {
      const errJson = await res.json();
      errorDetail = errJson?.error?.message || errJson?.detail || errorDetail;
    } catch {
      // fallback
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

/**
 * Fetch cross-asset supported analytical modes, windows, and parameters.
 */
export async function getCrossAssetOptions(
  options?: { token?: string | null; baseUrl?: string; signal?: AbortSignal }
): Promise<CrossAssetOptionsResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/cross-asset/options`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorDetail = `Failed to fetch cross-asset options (${res.status})`;
    try {
      const errJson = await res.json();
      errorDetail = errJson?.error?.message || errJson?.detail || errorDetail;
    } catch {
      // fallback
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

/**
 * Fetch cross-asset market overview / aligned performance snapshot.
 */
export async function getCrossAssetOverview(
  params: CrossAssetQueryParams = {},
  options?: { token?: string | null; baseUrl?: string; signal?: AbortSignal }
): Promise<CrossAssetOverviewResponse> {
  const baseUrl = getBaseUrl(options);
  const query = new URLSearchParams();

  if (params.universe_id) query.set("universe_id", params.universe_id);
  if (params.mode) query.set("mode", params.mode);
  if (params.window) query.set("window", params.window);
  if (params.symbols) query.set("symbols", params.symbols);

  const qs = query.toString();
  const url = `${baseUrl}/api/v1/markets/cross-asset${qs ? `?${qs}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorDetail = `Failed to fetch cross-asset overview (${res.status})`;
    try {
      const errJson = await res.json();
      errorDetail = errJson?.error?.message || errJson?.detail || errorDetail;
    } catch {
      // fallback
    }
    throw new Error(errorDetail);
  }

  return res.json();
}
