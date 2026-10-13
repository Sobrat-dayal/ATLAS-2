/**
 * Authenticated API client for Stage 56 Markets Overview V1.
 */

import { MarketsOverviewResponse } from "./types";

export interface MarketsOverviewRequestOptions {
  token?: string | null;
  group?: string;
  limit?: number;
  cursor?: string;
  featured_only?: boolean;
  baseUrl?: string;
  signal?: AbortSignal;
}

function getBaseUrl(options?: MarketsOverviewRequestOptions): string {
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

export async function getMarketsOverview(
  options?: MarketsOverviewRequestOptions
): Promise<MarketsOverviewResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.group && options.group.toLowerCase() !== "all") {
    searchParams.set("group", options.group.toLowerCase());
  }
  if (options?.limit && options.limit > 0) {
    searchParams.set("limit", options.limit.toString());
  }
  if (options?.cursor) {
    searchParams.set("cursor", options.cursor);
  }
  if (options?.featured_only) {
    searchParams.set("featured_only", "true");
  }

  const queryString = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/overview${queryString ? `?${queryString}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Markets Overview request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      }
    } catch {
      // Use fallback status message
    }
    throw new Error(errorMessage);
  }

  const data = (await res.json()) as MarketsOverviewResponse;
  return data;
}
