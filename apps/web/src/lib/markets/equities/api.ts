/**
 * Authenticated API client for Stage 57 Equities Markets V1.
 */

import {
  EquityDirectoryResponse,
  EquityFilterOptionsResponse,
  EquityOverviewDetailResponse,
} from "./types";

export interface EquityDirectoryRequestOptions {
  token?: string | null;
  query?: string;
  market_country?: string;
  exchange?: string;
  equity_type?: string;
  listing_status?: string;
  limit?: number;
  cursor?: string;
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

export async function getEquityDirectory(
  options?: EquityDirectoryRequestOptions
): Promise<EquityDirectoryResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.query && options.query.trim() !== "") {
    searchParams.set("query", options.query.trim());
  }
  if (options?.market_country && options.market_country !== "all") {
    searchParams.set("market_country", options.market_country);
  }
  if (options?.exchange && options.exchange !== "all") {
    searchParams.set("exchange", options.exchange);
  }
  if (options?.equity_type && options.equity_type !== "all") {
    searchParams.set("equity_type", options.equity_type);
  }
  if (options?.listing_status && options.listing_status !== "all") {
    searchParams.set("listing_status", options.listing_status);
  }
  if (options?.limit && options.limit > 0) {
    searchParams.set("limit", options.limit.toString());
  }
  if (options?.cursor) {
    searchParams.set("cursor", options.cursor);
  }

  const queryString = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/equities${queryString ? `?${queryString}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Equity Directory request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      } else if (errJson?.detail) {
        errorMessage = errJson.detail;
      }
    } catch {
      // Fallback message
    }
    throw new Error(errorMessage);
  }

  const data = (await res.json()) as EquityDirectoryResponse;
  return data;
}

export async function getEquityFilterOptions(options?: {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}): Promise<EquityFilterOptionsResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/equities/filters`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Failed to fetch equity filters (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      } else if (errJson?.detail) {
        errorMessage = errJson.detail;
      }
    } catch {
      // Fallback message
    }
    throw new Error(errorMessage);
  }

  const data = (await res.json()) as EquityFilterOptionsResponse;
  return data;
}

export async function getEquityOverview(
  instrumentEntityId: string,
  options?: {
    token?: string | null;
    baseUrl?: string;
    signal?: AbortSignal;
  }
): Promise<EquityOverviewDetailResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/equities/${instrumentEntityId}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Failed to retrieve equity details (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      } else if (errJson?.detail) {
        errorMessage = errJson.detail;
      }
    } catch {
      // Fallback message
    }
    throw new Error(errorMessage);
  }

  const data = (await res.json()) as EquityOverviewDetailResponse;
  return data;
}
