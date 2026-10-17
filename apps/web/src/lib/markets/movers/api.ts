/**
 * Authenticated API client for ATLAS Market Movers V1 (Stage 63).
 */

import {
  MarketMoverResponse,
  MarketMoversQueryParams,
  MoverMetricOptionsResponse,
  MoverUniverseResponse,
} from "./types";

export interface MoverRequestOptions extends MarketMoversQueryParams {
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
 * Fetch supported ranking universes.
 */
export async function getMoverUniverses(
  options?: { token?: string | null; baseUrl?: string; signal?: AbortSignal }
): Promise<MoverUniverseResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/movers/universes`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error");
    throw new Error(`Failed to fetch mover universes (${res.status}): ${errorText}`);
  }

  return res.json();
}

/**
 * Fetch metric options for a universe.
 */
export async function getMoverMetrics(
  universeId: string,
  options?: { token?: string | null; baseUrl?: string; signal?: AbortSignal }
): Promise<MoverMetricOptionsResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams({ universe_id: universeId });
  const url = `${baseUrl}/api/v1/markets/movers/metrics?${searchParams.toString()}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error");
    throw new Error(`Failed to fetch mover metrics (${res.status}): ${errorText}`);
  }

  return res.json();
}

/**
 * Fetch qualified market movers ranking snapshot.
 */
export async function getMarketMovers(
  options?: MoverRequestOptions
): Promise<MarketMoverResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.universe_id) {
    searchParams.set("universe_id", options.universe_id);
  }
  if (options?.category) {
    searchParams.set("category", options.category);
  }
  if (options?.window) {
    searchParams.set("window", options.window);
  }
  if (options?.exchange && options.exchange !== "all") {
    searchParams.set("exchange", options.exchange);
  }
  if (options?.limit) {
    searchParams.set("limit", options.limit.toString());
  }
  if (options?.cursor) {
    searchParams.set("cursor", options.cursor);
  }

  const queryStr = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/movers${queryStr ? `?${queryStr}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error");
    throw new Error(`Failed to fetch market movers (${res.status}): ${errorText}`);
  }

  return res.json();
}
