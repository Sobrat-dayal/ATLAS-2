/**
 * API client methods for Stage 77 Watchlist Columns and Preferences.
 */

import {
  WatchlistColumnConfigV1,
  WatchlistColumnDefinition,
  WatchlistColumnPreferencesResponse,
  WatchlistRowsResponse,
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

export async function getColumnRegistry(
  signal?: AbortSignal
): Promise<WatchlistColumnDefinition[]> {
  const base = getBaseApiUrl();
  const res = await fetch(`${base}/api/v1/watchlists/columns`, {
    method: "GET",
    headers: getHeaders(),
    signal,
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch column registry (${res.status})`);
  }
  return res.json();
}

export async function getWatchlistColumnPreferences(
  watchlistId: string,
  signal?: AbortSignal
): Promise<WatchlistColumnPreferencesResponse> {
  const base = getBaseApiUrl();
  const res = await fetch(`${base}/api/v1/watchlists/${watchlistId}/columns`, {
    method: "GET",
    headers: getHeaders(),
    signal,
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch watchlist column preferences (${res.status})`);
  }
  return res.json();
}

export async function updateWatchlistColumnPreferences(
  watchlistId: string,
  config: WatchlistColumnConfigV1,
  expectedRevision?: number,
  signal?: AbortSignal
): Promise<WatchlistColumnPreferencesResponse> {
  const base = getBaseApiUrl();
  const extraHeaders: Record<string, string> = {};
  if (expectedRevision !== undefined) {
    extraHeaders["If-Match"] = `W/"${expectedRevision}"`;
  }
  const res = await fetch(`${base}/api/v1/watchlists/${watchlistId}/columns`, {
    method: "PUT",
    headers: getHeaders(extraHeaders),
    body: JSON.stringify({
      configuration: config,
      expected_revision: expectedRevision,
    }),
    signal,
  });
  if (res.status === 409 || res.status === 412) {
    const err = new Error("Column preferences revision conflict");
    (err as unknown as { status: number }).status = res.status;
    throw err;
  }
  if (!res.ok) {
    const errBody = await res.json().catch(() => null);
    const msg = errBody?.detail?.message || `Failed to update column preferences (${res.status})`;
    throw new Error(msg);
  }
  return res.json();
}

export async function resetWatchlistColumnPreferences(
  watchlistId: string,
  signal?: AbortSignal
): Promise<WatchlistColumnPreferencesResponse> {
  const base = getBaseApiUrl();
  const res = await fetch(`${base}/api/v1/watchlists/${watchlistId}/columns/reset`, {
    method: "POST",
    headers: getHeaders(),
    signal,
  });
  if (!res.ok) {
    throw new Error(`Failed to reset column preferences (${res.status})`);
  }
  return res.json();
}

export async function getProjectedWatchlistRows(
  watchlistId: string,
  page: number = 1,
  pageSize: number = 50,
  sortColumnId?: string | null,
  sortDirection?: "asc" | "desc" | null,
  signal?: AbortSignal
): Promise<WatchlistRowsResponse> {
  const base = getBaseApiUrl();
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  if (sortColumnId) {
    params.set("sort_column_id", sortColumnId);
  }
  if (sortDirection) {
    params.set("sort_direction", sortDirection);
  }
  const res = await fetch(`${base}/api/v1/watchlists/${watchlistId}/rows?${params.toString()}`, {
    method: "GET",
    headers: getHeaders(),
    signal,
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch projected watchlist rows (${res.status})`);
  }
  return res.json();
}
