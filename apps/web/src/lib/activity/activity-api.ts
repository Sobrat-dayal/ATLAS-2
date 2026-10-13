/**
 * Authenticated API client for Stage 53 Home Personalized Activity.
 */

import {
  ActivityConsentResponse,
  ClearActivityResponse,
  RecordActivityEventRequest,
  UserActivityItem,
  UserActivityListResponse,
} from "./activity-types";

export interface ActivityRequestOptions {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}

function getBaseUrl(options?: ActivityRequestOptions): string {
  if (options?.baseUrl) return options.baseUrl;
  return process.env.NEXT_PUBLIC_API_URL || "";
}

function getHeaders(token?: string | null): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function getHomeActivity(
  params?: {
    limit?: number;
    cursor?: string | null;
  },
  options?: ActivityRequestOptions
): Promise<UserActivityListResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.cursor) searchParams.set("cursor", params.cursor);

  const qs = searchParams.toString();
  const url = `${baseUrl}/api/v1/home/activity${qs ? `?${qs}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Activity request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      }
    } catch {
      // Fallback
    }
    throw new Error(errorMessage);
  }

  return (await res.json()) as UserActivityListResponse;
}

export async function recordHomeActivity(
  payload: RecordActivityEventRequest,
  options?: ActivityRequestOptions
): Promise<UserActivityItem> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/home/activity/events`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Record activity request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      }
    } catch {
      // Fallback
    }
    throw new Error(errorMessage);
  }

  return (await res.json()) as UserActivityItem;
}

export async function setHomeActivityConsent(
  enabled: boolean,
  options?: ActivityRequestOptions
): Promise<ActivityConsentResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/home/activity/consent`;

  const res = await fetch(url, {
    method: "PUT",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    body: JSON.stringify({ enabled }),
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Update consent request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      }
    } catch {
      // Fallback
    }
    throw new Error(errorMessage);
  }

  return (await res.json()) as ActivityConsentResponse;
}

export async function clearHomeActivity(
  options?: ActivityRequestOptions
): Promise<ClearActivityResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/home/activity`;

  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Clear activity request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      }
    } catch {
      // Fallback
    }
    throw new Error(errorMessage);
  }

  return (await res.json()) as ClearActivityResponse;
}
