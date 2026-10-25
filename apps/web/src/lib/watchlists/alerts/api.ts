/**
 * Authenticated REST Client for Watchlist Alerts V1 (Stage 80).
 */

import {
  AlertCapabilitiesResponse,
  AlertHealthResponse,
  AlertListResponse,
  CreateAlertPayload,
  UpdateAlertPayload,
  WatchlistAlertRule,
  WatchlistAlertTrigger,
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

export class WatchlistAlertApiError extends Error {
  public status: number;
  public code?: string;
  public details?: unknown;

  constructor(message: string, status: number, code?: string, details?: unknown) {
    super(message);
    this.name = "WatchlistAlertApiError";
    this.status = status;
    this.code = code;
    this.details = details;
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
    const errorObj = json?.error as Record<string, unknown> | undefined;
    const message =
      (errorObj?.message as string) ||
      (json?.detail as string) ||
      (json?.message as string) ||
      `HTTP error ${res.status}`;
    const code = (errorObj?.code as string) || (json?.code as string);
    throw new WatchlistAlertApiError(message, res.status, code, json);
  }

  return json as T;
}

export async function getWatchlistAlerts(
  watchlistId: string,
  page = 1,
  pageSize = 50,
  state?: string,
): Promise<AlertListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (state) {
    params.set("state", state);
  }

  const res = await fetch(
    `${getBaseApiUrl()}/api/v1/watchlists/${watchlistId}/alerts?${params.toString()}`,
    {
      method: "GET",
      headers: getHeaders(),
    },
  );
  return handleResponse<AlertListResponse>(res);
}

export async function createWatchlistAlert(
  watchlistId: string,
  payload: CreateAlertPayload,
): Promise<WatchlistAlertRule> {
  const res = await fetch(`${getBaseApiUrl()}/api/v1/watchlists/${watchlistId}/alerts`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse<WatchlistAlertRule>(res);
}

export async function getWatchlistAlert(
  watchlistId: string,
  alertId: string,
): Promise<WatchlistAlertRule> {
  const res = await fetch(
    `${getBaseApiUrl()}/api/v1/watchlists/${watchlistId}/alerts/${alertId}`,
    {
      method: "GET",
      headers: getHeaders(),
    },
  );
  return handleResponse<WatchlistAlertRule>(res);
}

export async function updateWatchlistAlert(
  watchlistId: string,
  alertId: string,
  payload: UpdateAlertPayload,
): Promise<WatchlistAlertRule> {
  const res = await fetch(
    `${getBaseApiUrl()}/api/v1/watchlists/${watchlistId}/alerts/${alertId}`,
    {
      method: "PATCH",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    },
  );
  return handleResponse<WatchlistAlertRule>(res);
}

export async function deleteWatchlistAlert(
  watchlistId: string,
  alertId: string,
): Promise<boolean> {
  const res = await fetch(
    `${getBaseApiUrl()}/api/v1/watchlists/${watchlistId}/alerts/${alertId}`,
    {
      method: "DELETE",
      headers: getHeaders(),
    },
  );
  return handleResponse<boolean>(res);
}

export async function pauseWatchlistAlert(
  watchlistId: string,
  alertId: string,
): Promise<WatchlistAlertRule> {
  const res = await fetch(
    `${getBaseApiUrl()}/api/v1/watchlists/${watchlistId}/alerts/${alertId}/pause`,
    {
      method: "POST",
      headers: getHeaders(),
    },
  );
  return handleResponse<WatchlistAlertRule>(res);
}

export async function resumeWatchlistAlert(
  watchlistId: string,
  alertId: string,
): Promise<WatchlistAlertRule> {
  const res = await fetch(
    `${getBaseApiUrl()}/api/v1/watchlists/${watchlistId}/alerts/${alertId}/resume`,
    {
      method: "POST",
      headers: getHeaders(),
    },
  );
  return handleResponse<WatchlistAlertRule>(res);
}

export async function getWatchlistAlertHistory(
  watchlistId: string,
  alertId: string,
  limit = 50,
  offset = 0,
): Promise<WatchlistAlertTrigger[]> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  const res = await fetch(
    `${getBaseApiUrl()}/api/v1/watchlists/${watchlistId}/alerts/${alertId}/history?${params.toString()}`,
    {
      method: "GET",
      headers: getHeaders(),
    },
  );
  return handleResponse<WatchlistAlertTrigger[]>(res);
}

export async function getWatchlistAlertCapabilities(): Promise<AlertCapabilitiesResponse> {
  const res = await fetch(`${getBaseApiUrl()}/api/v1/watchlists/alert-capabilities`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<AlertCapabilitiesResponse>(res);
}

export async function getWatchlistAlertHealth(): Promise<AlertHealthResponse> {
  const res = await fetch(`${getBaseApiUrl()}/api/v1/watchlists/alert-health`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<AlertHealthResponse>(res);
}
