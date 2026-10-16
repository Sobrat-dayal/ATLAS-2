/**
 * Authenticated API client for ATLAS Futures & Commodities Markets V1 (Stage 62).
 */

import {
  CommodityDirectoryItem,
  CommodityDirectoryResponse,
  FuturesContractDirectoryResponse,
  FuturesContractOverviewResponse,
  FuturesContractQueryParams,
  FuturesFilterOptionsResponse,
  SpotBenchmarkDirectoryResponse,
} from "./types";

export interface FuturesRequestOptions extends FuturesContractQueryParams {
  token?: string | null;
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

/**
 * Fetch paginated futures contracts directory with active filters.
 */
export async function getFuturesContracts(
  options?: FuturesRequestOptions
): Promise<FuturesContractDirectoryResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.query && options.query.trim()) {
    searchParams.set("query", options.query.trim());
  }
  if (options?.category && options.category !== "all") {
    searchParams.set("category", options.category);
  }
  if (options?.exchange && options.exchange !== "all") {
    searchParams.set("exchange", options.exchange);
  }
  if (options?.product_entity_id && options.product_entity_id !== "all") {
    searchParams.set("product_entity_id", options.product_entity_id);
  }
  if (options?.root_symbol && options.root_symbol !== "all") {
    searchParams.set("root_symbol", options.root_symbol);
  }
  if (options?.contract_month && options.contract_month !== "all") {
    searchParams.set("contract_month", options.contract_month);
  }
  if (options?.settlement_type && options.settlement_type !== "all") {
    searchParams.set("settlement_type", options.settlement_type);
  }
  if (options?.lifecycle_status && options.lifecycle_status !== "all") {
    searchParams.set("lifecycle_status", options.lifecycle_status);
  }
  if (options?.limit) {
    searchParams.set("limit", options.limit.toString());
  }
  if (options?.cursor) {
    searchParams.set("cursor", options.cursor);
  }

  const queryString = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/futures/contracts${
    queryString ? `?${queryString}` : ""
  }`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: Failed to fetch futures contracts`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // Ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

/**
 * Fetch filter choices and coverage metrics from futures catalog.
 */
export async function getFuturesFilterOptions(options?: {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}): Promise<FuturesFilterOptionsResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/futures/filters`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: Failed to fetch futures filters`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // Ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

/**
 * Fetch comprehensive overview for a single futures contract.
 */
export async function getFuturesContractOverview(
  instrumentEntityId: string,
  options?: {
    token?: string | null;
    baseUrl?: string;
    signal?: AbortSignal;
  }
): Promise<FuturesContractOverviewResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/futures/contracts/${encodeURIComponent(
    instrumentEntityId
  )}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: Failed to fetch futures contract overview`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // Ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

/**
 * Fetch canonical commodities catalog with associated products and contracts.
 */
export async function getCommodities(options?: {
  category?: string;
  query?: string;
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}): Promise<CommodityDirectoryResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.category && options.category !== "all") {
    searchParams.set("category", options.category);
  }
  if (options?.query && options.query.trim()) {
    searchParams.set("query", options.query.trim());
  }

  const queryString = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/futures/commodities${
    queryString ? `?${queryString}` : ""
  }`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: Failed to fetch commodities`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // Ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

/**
 * Fetch a single commodity overview with associated products.
 */
export async function getCommodity(
  commodityEntityId: string,
  options?: {
    token?: string | null;
    baseUrl?: string;
    signal?: AbortSignal;
  }
): Promise<CommodityDirectoryItem> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/futures/commodities/${encodeURIComponent(
    commodityEntityId
  )}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: Failed to fetch commodity`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // Ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

/**
 * Fetch physical commodity spot benchmarks.
 */
export async function getSpotBenchmarks(options?: {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}): Promise<SpotBenchmarkDirectoryResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/futures/spot-benchmarks`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: Failed to fetch spot benchmarks`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // Ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}
