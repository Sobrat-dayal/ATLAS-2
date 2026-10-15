/**
 * Authenticated API client for Stage 59 FX Markets V1.
 */

import {
  FxConversionRequest,
  FxConversionResponse,
  FxCurrenciesResponse,
  FxPairDirectoryResponse,
  FxPairOverviewDetailResponse,
} from "./types";

export interface FxDirectoryRequestOptions {
  token?: string | null;
  base_currency?: string;
  quote_currency?: string;
  query?: string;
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

export async function getFxDirectory(
  options?: FxDirectoryRequestOptions
): Promise<FxPairDirectoryResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.base_currency && options.base_currency !== "all") {
    searchParams.set("base_currency", options.base_currency);
  }
  if (options?.quote_currency && options.quote_currency !== "all") {
    searchParams.set("quote_currency", options.quote_currency);
  }
  if (options?.query && options.query.trim() !== "") {
    searchParams.set("query", options.query.trim());
  }
  if (options?.limit && options.limit > 0) {
    searchParams.set("limit", options.limit.toString());
  }
  if (options?.cursor) {
    searchParams.set("cursor", options.cursor);
  }

  const queryString = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/fx${queryString ? `?${queryString}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `FX Directory request failed (${res.status})`;
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

  return res.json();
}

export async function getFxCurrencies(options?: {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}): Promise<FxCurrenciesResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/fx/currencies`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Supported FX Currencies request failed (${res.status})`;
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

  return res.json();
}

export async function getFxPairDetail(
  instrumentEntityId: string,
  options?: {
    token?: string | null;
    baseUrl?: string;
    signal?: AbortSignal;
  }
): Promise<FxPairOverviewDetailResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/fx/${instrumentEntityId}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `FX Pair Overview request failed (${res.status})`;
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

  return res.json();
}

export async function convertFxCurrency(
  payload: FxConversionRequest,
  options?: {
    token?: string | null;
    baseUrl?: string;
    signal?: AbortSignal;
  }
): Promise<FxConversionResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/fx/convert`;

  const headers = getHeaders(options?.token) as Record<string, string>;
  headers["Content-Type"] = "application/json";

  const res = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMessage = `Currency conversion failed (${res.status})`;
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

  return res.json();
}
