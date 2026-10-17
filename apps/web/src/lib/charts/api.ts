/**
 * API client for ATLAS Charts V1 (Stage 66).
 *
 * Provides typed fetchers for:
 * - GET /api/v1/charts/instruments
 * - GET /api/v1/charts/instruments/{id}
 * - GET /api/v1/charts/history
 */

import {
  ChartHistoryResponse,
  ChartInstrumentMetadata,
  ChartSearchResponse,
} from "./types";

function getBaseApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "";
}

export interface FetchChartHistoryParams {
  instrumentId?: string;
  symbol?: string;
  interval?: string;
  start?: string;
  end?: string;
  before?: string;
  limit?: number;
  signal?: AbortSignal;
}

export interface FetchChartInstrumentsParams {
  q?: string;
  assetClass?: string;
  signal?: AbortSignal;
}

export async function fetchChartInstruments(
  params?: FetchChartInstrumentsParams
): Promise<ChartSearchResponse> {
  const query = new URLSearchParams();
  if (params?.q) query.set("q", params.q);
  if (params?.assetClass) query.set("asset_class", params.assetClass);

  const qs = query.toString();
  const url = `${getBaseApiUrl()}/api/v1/charts/instruments${qs ? `?${qs}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal: params?.signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch chart instruments (status ${res.status})`);
  }

  return (await res.json()) as ChartSearchResponse;
}

export async function fetchChartInstrument(
  identifier: string,
  signal?: AbortSignal
): Promise<ChartInstrumentMetadata> {
  const url = `${getBaseApiUrl()}/api/v1/charts/instruments/${encodeURIComponent(identifier)}`;

  const res = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch chart instrument '${identifier}' (status ${res.status})`);
  }

  return (await res.json()) as ChartInstrumentMetadata;
}

export async function fetchChartHistory(
  params: FetchChartHistoryParams
): Promise<ChartHistoryResponse> {
  const query = new URLSearchParams();
  if (params.instrumentId) query.set("instrument_id", params.instrumentId);
  if (params.symbol) query.set("symbol", params.symbol);
  if (params.interval) query.set("interval", params.interval);
  if (params.start) query.set("start", params.start);
  if (params.end) query.set("end", params.end);
  if (params.before) query.set("before", params.before);
  if (params.limit !== undefined) query.set("limit", params.limit.toString());

  const url = `${getBaseApiUrl()}/api/v1/charts/history?${query.toString()}`;

  const res = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal: params.signal,
  });

  if (!res.ok) {
    let errorMsg = `Chart history request failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errorMsg = errJson.error.message;
      } else if (errJson?.detail) {
        errorMsg = errJson.detail;
      }
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return (await res.json()) as ChartHistoryResponse;
}
