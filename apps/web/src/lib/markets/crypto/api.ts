/**
 * Authenticated API client for Stage 60 Cryptocurrency Markets V1.
 */

import {
  CryptoAssetDirectoryResponse,
  CryptoFilterOptionsResponse,
  CryptoSpotMarketDirectoryResponse,
  CryptoSpotMarketOverviewDetailResponse,
} from "./types";

export interface CryptoSpotMarketsRequestOptions {
  token?: string | null;
  base_asset?: string;
  quote_asset?: string;
  venue?: string;
  quote_asset_type?: string;
  query?: string;
  limit?: number;
  cursor?: string;
  baseUrl?: string;
  signal?: AbortSignal;
}

export interface CryptoAssetsRequestOptions {
  token?: string | null;
  query?: string;
  asset_kind?: string;
  network?: string;
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

export async function getCryptoSpotMarkets(
  options?: CryptoSpotMarketsRequestOptions
): Promise<CryptoSpotMarketDirectoryResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.base_asset && options.base_asset !== "all") {
    searchParams.set("base_asset", options.base_asset);
  }
  if (options?.quote_asset && options.quote_asset !== "all") {
    searchParams.set("quote_asset", options.quote_asset);
  }
  if (options?.venue && options.venue !== "all") {
    searchParams.set("venue", options.venue);
  }
  if (options?.quote_asset_type && options.quote_asset_type !== "all") {
    searchParams.set("quote_asset_type", options.quote_asset_type);
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
  const url = `${baseUrl}/api/v1/markets/crypto${queryString ? `?${queryString}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorDetail = `Failed to fetch crypto spot markets: ${res.statusText}`;
    try {
      const err = await res.json();
      if (err.error?.message) {
        errorDetail = err.error.message;
      } else if (err.detail) {
        errorDetail = err.detail;
      }
    } catch {
      // ignore JSON parse error
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export async function getCryptoAssets(
  options?: CryptoAssetsRequestOptions
): Promise<CryptoAssetDirectoryResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.query && options.query.trim() !== "") {
    searchParams.set("query", options.query.trim());
  }
  if (options?.asset_kind && options.asset_kind !== "all") {
    searchParams.set("asset_kind", options.asset_kind);
  }
  if (options?.network && options.network !== "all") {
    searchParams.set("network", options.network);
  }
  if (options?.limit && options.limit > 0) {
    searchParams.set("limit", options.limit.toString());
  }
  if (options?.cursor) {
    searchParams.set("cursor", options.cursor);
  }

  const queryString = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/crypto/assets${queryString ? `?${queryString}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
  });

  if (!res.ok) {
    let errorDetail = `Failed to fetch crypto assets: ${res.statusText}`;
    try {
      const err = await res.json();
      if (err.error?.message) {
        errorDetail = err.error.message;
      } else if (err.detail) {
        errorDetail = err.detail;
      }
    } catch {
      // ignore JSON parse error
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export async function getCryptoFilterOptions(options?: {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}): Promise<CryptoFilterOptionsResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/crypto/filters`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
  });

  if (!res.ok) {
    let errorDetail = `Failed to fetch crypto filters: ${res.statusText}`;
    try {
      const err = await res.json();
      if (err.error?.message) {
        errorDetail = err.error.message;
      } else if (err.detail) {
        errorDetail = err.detail;
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export async function getCryptoMarketDetail(
  instrumentEntityId: string,
  options?: {
    token?: string | null;
    baseUrl?: string;
    signal?: AbortSignal;
  }
): Promise<CryptoSpotMarketOverviewDetailResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/crypto/${instrumentEntityId}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorDetail = `Failed to fetch crypto market detail: ${res.statusText}`;
    try {
      const err = await res.json();
      if (err.error?.message) {
        errorDetail = err.error.message;
      } else if (err.detail) {
        errorDetail = err.detail;
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return res.json();
}
