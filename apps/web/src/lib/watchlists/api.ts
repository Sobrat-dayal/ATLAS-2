/**
 * Authenticated REST API Client for Watchlists V1 (Stage 76).
 */

import {
  AddWatchlistItemPayload,
  CreateWatchlistPayload,
  ReorderWatchlistItemsPayload,
  ReorderWatchlistItemsResponse,
  UpdateWatchlistPayload,
  WatchlistDetail,
  WatchlistItem,
  WatchlistListResponse,
  WatchlistSummary,
} from "./types";

function getBaseApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

function getHeaders(extra?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...extra,
  };
  return headers;
}

export class WatchlistApiError extends Error {
  public status: number;
  public code?: string;
  public details?: unknown;

  constructor(message: string, status: number, code?: string, details?: unknown) {
    super(message);
    this.name = "WatchlistApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export class WatchlistConflictApiError extends WatchlistApiError {
  constructor(message: string, status: number, code?: string) {
    super(message, status, code);
    this.name = "WatchlistConflictApiError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (res.status === 204) {
    return true as unknown as T;
  }

  let json: Record<string, unknown> | null = null;
  try {
    json = (await res.json()) as Record<string, unknown>;
  } catch {
    json = null;
  }

  if (!res.ok) {
    const errorDetail = json?.detail;
    let message = `Watchlist API error (${res.status})`;
    let code: string | undefined;

    if (typeof errorDetail === "string") {
      message = errorDetail;
    } else if (errorDetail && typeof errorDetail === "object") {
      const errObj = errorDetail as Record<string, unknown>;
      if (typeof errObj.message === "string") {
        message = errObj.message;
      }
      if (typeof errObj.code === "string") {
        code = errObj.code;
      }
    }

    if (res.status === 409 || res.status === 412) {
      throw new WatchlistConflictApiError(message, res.status, code);
    }
    throw new WatchlistApiError(message, res.status, code, json);
  }

  return json as T;
}

export async function listWatchlists(
  page: number = 1,
  pageSize: number = 20,
  signal?: AbortSignal
): Promise<WatchlistListResponse> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/watchlists?page=${page}&page_size=${pageSize}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
    cache: "no-store",
  });
  return handleResponse<WatchlistListResponse>(res);
}

export async function createWatchlist(
  payload: CreateWatchlistPayload,
  signal?: AbortSignal
): Promise<WatchlistSummary> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/watchlists`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
    signal,
  });
  return handleResponse<WatchlistSummary>(res);
}

export async function getWatchlist(
  id: string,
  page: number = 1,
  pageSize: number = 50,
  signal?: AbortSignal
): Promise<WatchlistDetail> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/watchlists/${id}?page=${page}&page_size=${pageSize}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
    signal,
    cache: "no-store",
  });
  return handleResponse<WatchlistDetail>(res);
}

export async function updateWatchlist(
  id: string,
  payload: UpdateWatchlistPayload,
  expectedRevision?: number,
  signal?: AbortSignal
): Promise<WatchlistSummary> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/watchlists/${id}`;
  const extraHeaders: Record<string, string> = {};
  if (expectedRevision !== undefined) {
    extraHeaders["If-Match"] = `W/"${expectedRevision}"`;
  }
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(extraHeaders),
    body: JSON.stringify(payload),
    signal,
  });
  return handleResponse<WatchlistSummary>(res);
}

export async function deleteWatchlist(id: string, signal?: AbortSignal): Promise<void> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/watchlists/${id}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
    signal,
  });
  await handleResponse<boolean>(res);
}

export async function addWatchlistItem(
  watchlistId: string,
  payload: AddWatchlistItemPayload,
  signal?: AbortSignal
): Promise<WatchlistItem> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/watchlists/${watchlistId}/items`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
    signal,
  });
  return handleResponse<WatchlistItem>(res);
}

export async function removeWatchlistItem(
  watchlistId: string,
  itemId: string,
  signal?: AbortSignal
): Promise<void> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/watchlists/${watchlistId}/items/${itemId}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
    signal,
  });
  await handleResponse<boolean>(res);
}

export async function reorderWatchlistItems(
  watchlistId: string,
  payload: ReorderWatchlistItemsPayload,
  signal?: AbortSignal
): Promise<ReorderWatchlistItemsResponse> {
  const base = getBaseApiUrl();
  const url = `${base}/api/v1/watchlists/${watchlistId}/items/order`;
  const res = await fetch(url, {
    method: "PUT",
    headers: getHeaders({
      "If-Match": `W/"${payload.expected_revision}"`,
    }),
    body: JSON.stringify(payload),
    signal,
  });
  return handleResponse<ReorderWatchlistItemsResponse>(res);
}
