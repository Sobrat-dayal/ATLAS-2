/**
 * Authenticated API client for Stage 58 ETFs & Funds Markets V1.
 */

import {
  FundDirectoryResponse,
  FundFilterOptionsResponse,
  FundOverviewDetailResponse,
} from "./types";

export interface FundDirectoryRequestOptions {
  token?: string | null;
  query?: string;
  fund_type?: string;
  market_country?: string;
  exchange?: string;
  domicile?: string;
  fund_category?: string;
  share_class_currency?: string;
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

export async function getFundDirectory(
  options?: FundDirectoryRequestOptions
): Promise<FundDirectoryResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.query && options.query.trim() !== "") {
    searchParams.set("query", options.query.trim());
  }
  if (options?.fund_type && options.fund_type !== "ALL") {
    searchParams.set("fund_type", options.fund_type);
  }
  if (options?.market_country && options.market_country !== "all") {
    searchParams.set("market_country", options.market_country);
  }
  if (options?.exchange && options.exchange !== "all") {
    searchParams.set("exchange", options.exchange);
  }
  if (options?.domicile && options.domicile !== "all") {
    searchParams.set("domicile", options.domicile);
  }
  if (options?.fund_category && options.fund_category !== "all") {
    searchParams.set("fund_category", options.fund_category);
  }
  if (options?.share_class_currency && options.share_class_currency !== "all") {
    searchParams.set("share_class_currency", options.share_class_currency);
  }
  if (options?.limit && options.limit > 0) {
    searchParams.set("limit", options.limit.toString());
  }
  if (options?.cursor) {
    searchParams.set("cursor", options.cursor);
  }

  const queryString = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/funds${queryString ? `?${queryString}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Fund Directory request failed (${res.status})`;
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

  const data = (await res.json()) as FundDirectoryResponse;
  return data;
}

export async function getFundFilterOptions(options?: {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}): Promise<FundFilterOptionsResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/funds/filters`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Failed to fetch fund filters (${res.status})`;
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

  const data = (await res.json()) as FundFilterOptionsResponse;
  return data;
}

export async function getFundOverview(
  instrumentEntityId: string,
  options?: {
    token?: string | null;
    baseUrl?: string;
    signal?: AbortSignal;
  }
): Promise<FundOverviewDetailResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/funds/${instrumentEntityId}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Failed to retrieve fund details (${res.status})`;
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

  const data = (await res.json()) as FundOverviewDetailResponse;
  return data;
}
