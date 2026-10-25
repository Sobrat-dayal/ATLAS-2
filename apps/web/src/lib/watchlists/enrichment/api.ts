/**
 * Frontend API client for Watchlist Enrichment V1 (Stage 79).
 */

import {
  EnrichmentColumnMetadata,
  WatchlistEnrichmentRequest,
  WatchlistEnrichmentResponse,
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

/**
 * Fetch registered enrichment capabilities and column specifications.
 */
export async function getEnrichmentCapabilities(
  category?: string,
  signal?: AbortSignal
): Promise<EnrichmentColumnMetadata[]> {
  const base = getBaseApiUrl();
  const url = new URL(`${base}/api/v1/watchlists/enrichment/capabilities`);
  if (category) {
    url.searchParams.set("category", category);
  }

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
    signal,
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch enrichment capabilities (${res.status})`);
  }

  return res.json();
}

/**
 * Batch query enrichment values for watchlist items.
 */
export async function queryWatchlistEnrichment(
  watchlistId: string,
  request: WatchlistEnrichmentRequest,
  signal?: AbortSignal
): Promise<WatchlistEnrichmentResponse> {
  const base = getBaseApiUrl();
  const res = await fetch(`${base}/api/v1/watchlists/${watchlistId}/enrichment/query`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
    signal,
    cache: "no-store",
  });

  if (!res.ok) {
    const errBody = await res.json().catch(() => null);
    const msg = errBody?.detail || `Failed to fetch watchlist enrichment (${res.status})`;
    throw new Error(msg);
  }

  return res.json();
}
