/**
 * Client API Functions for ATLAS Spatial Analytics and H3 Engine (Stage 131).
 */

import {
  CellDetailsResponse,
  RegionComparisonResult,
  SpatialAnalyticsQuery,
  SpatialAnalyticsResult,
  SpatialMetricDefinition,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

export async function fetchAnalyticsCapabilities(): Promise<any> {
  const res = await fetch(`${API_BASE}/maps/analytics/capabilities`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error('Failed to fetch spatial analytics capabilities');
  return res.json();
}

export async function fetchAnalyticsMetrics(datasetId: string): Promise<SpatialMetricDefinition[]> {
  const res = await fetch(`${API_BASE}/maps/analytics/metrics?dataset_id=${encodeURIComponent(datasetId)}`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error(`Failed to fetch metrics for dataset ${datasetId}`);
  return res.json();
}

export async function executeSpatialQuery(query: SpatialAnalyticsQuery): Promise<SpatialAnalyticsResult> {
  const payload = {
    dataset_id: query.dataset_id,
    metric_id: query.metric_id,
    aggregation: query.aggregation,
    visualization_type: query.visualization_type,
    h3_resolution: query.h3_resolution,
    bounds: query.bounds
      ? {
          west: query.bounds[0],
          south: query.bounds[1],
          east: query.bounds[2],
          north: query.bounds[3],
        }
      : null,
    filters: query.filters || {},
    time_range_start: query.time_range_start,
    time_range_end: query.time_range_end,
    time_bucket: query.time_bucket,
    historical_as_of: query.historical_as_of,
    min_contributors: query.min_contributors ?? 5,
    result_limit: query.result_limit ?? 5000,
  };

  const res = await fetch(`${API_BASE}/maps/analytics/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail?.message || `Spatial query failed with status ${res.status}`);
  }

  return res.json();
}

export async function fetchCellDetails(cellId: string): Promise<CellDetailsResponse> {
  const res = await fetch(`${API_BASE}/maps/analytics/cells/${encodeURIComponent(cellId)}`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error(`Failed to fetch details for cell ${cellId}`);
  return res.json();
}

export async function compareRegions(params: {
  dataset_id: string;
  metric_id: string;
  aggregation: string;
  region_a_name: string;
  region_a_bounds: [number, number, number, number];
  region_b_name: string;
  region_b_bounds: [number, number, number, number];
  h3_resolution?: number;
}): Promise<RegionComparisonResult> {
  const payload = {
    dataset_id: params.dataset_id,
    metric_id: params.metric_id,
    aggregation: params.aggregation,
    region_a_name: params.region_a_name,
    region_a_bounds: {
      west: params.region_a_bounds[0],
      south: params.region_a_bounds[1],
      east: params.region_a_bounds[2],
      north: params.region_a_bounds[3],
    },
    region_b_name: params.region_b_name,
    region_b_bounds: {
      west: params.region_b_bounds[0],
      south: params.region_b_bounds[1],
      east: params.region_b_bounds[2],
      north: params.region_b_bounds[3],
    },
    h3_resolution: params.h3_resolution ?? 6,
  };

  const res = await fetch(`${API_BASE}/maps/analytics/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail?.message || `Region comparison failed with status ${res.status}`);
  }

  return res.json();
}

