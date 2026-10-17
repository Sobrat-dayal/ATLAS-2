/**
 * Authenticated API client for ATLAS Market Heatmaps V1 (Stage 64).
 */

import {
  HeatmapComparisonWindow,
  HeatmapHierarchyMode,
  HeatmapOptionsResponse,
  HeatmapUniverseResponse,
  HeatmapVisualizationMode,
  MarketHeatmapResponse,
} from "./types";

export interface HeatmapQueryParams {
  universe_id?: string;
  visualization_mode?: HeatmapVisualizationMode;
  hierarchy_mode?: HeatmapHierarchyMode;
  comparison_window?: HeatmapComparisonWindow;
  sector?: string;
  max_nodes?: number;
}

export interface HeatmapRequestOptions extends HeatmapQueryParams {
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
 * Fetch supported heatmap candidate universes.
 */
export async function getHeatmapUniverses(
  options?: { token?: string | null; baseUrl?: string; signal?: AbortSignal }
): Promise<HeatmapUniverseResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/heatmaps/universes`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error");
    throw new Error(`Failed to fetch heatmap universes (${res.status}): ${errorText}`);
  }

  return res.json();
}

/**
 * Fetch supported modes, hierarchies, and taxonomy metadata.
 */
export async function getHeatmapOptions(
  options?: { token?: string | null; baseUrl?: string; signal?: AbortSignal }
): Promise<HeatmapOptionsResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/markets/heatmaps/options`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error");
    throw new Error(`Failed to fetch heatmap options (${res.status}): ${errorText}`);
  }

  return res.json();
}

/**
 * Fetch qualified market heatmap calculation snapshot.
 */
export async function getMarketHeatmap(
  options?: HeatmapRequestOptions
): Promise<MarketHeatmapResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();

  if (options?.universe_id) {
    searchParams.set("universe_id", options.universe_id);
  }
  if (options?.visualization_mode) {
    searchParams.set("visualization_mode", options.visualization_mode);
  }
  if (options?.hierarchy_mode) {
    searchParams.set("hierarchy_mode", options.hierarchy_mode);
  }
  if (options?.comparison_window) {
    searchParams.set("comparison_window", options.comparison_window);
  }
  if (options?.sector) {
    searchParams.set("sector", options.sector);
  }
  if (options?.max_nodes) {
    searchParams.set("max_nodes", options.max_nodes.toString());
  }

  const queryString = searchParams.toString();
  const url = `${baseUrl}/api/v1/markets/heatmaps${queryString ? `?${queryString}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    signal: options?.signal,
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error");
    throw new Error(`Failed to fetch market heatmap (${res.status}): ${errorText}`);
  }

  return res.json();
}
