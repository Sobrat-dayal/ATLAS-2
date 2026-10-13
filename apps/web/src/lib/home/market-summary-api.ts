/**
 * Authenticated API client for Stage 52 Home Market Summary.
 */

import { HomeMarketSummaryResponse } from "./market-summary-types";

export interface MarketSummaryRequestOptions {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}

function getBaseUrl(options?: MarketSummaryRequestOptions): string {
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

export async function getHomeMarketSummary(
  options?: MarketSummaryRequestOptions
): Promise<HomeMarketSummaryResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/home/market-summary`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Market Summary request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      }
    } catch {
      // Use fallback error message
    }
    throw new Error(errorMessage);
  }

  const data = (await res.json()) as HomeMarketSummaryResponse;
  return data;
}
