/**
 * Client API for ATLAS Maps V1 Geospatial Services.
 */

import {
  GeoFeatureDetail,
  GeographicSearchResult,
  MapBasemapStyle,
  MapConfig,
  MapDataset,
  MapLayer,
  UserMapView,
} from "./types";

const API_BASE = "/api/v1/maps";

export async function fetchMapConfig(): Promise<MapConfig> {
  const res = await fetch(`${API_BASE}/config`);
  if (!res.ok) throw new Error("Failed to load map configuration");
  return res.json();
}

export async function fetchMapStyles(): Promise<MapBasemapStyle[]> {
  const res = await fetch(`${API_BASE}/styles`);
  if (!res.ok) throw new Error("Failed to load map styles");
  return res.json();
}

export async function fetchMapLayers(): Promise<MapLayer[]> {
  const res = await fetch(`${API_BASE}/layers`);
  if (!res.ok) throw new Error("Failed to load map layers");
  return res.json();
}

export async function fetchMapDatasets(): Promise<MapDataset[]> {
  const res = await fetch(`${API_BASE}/datasets`);
  if (!res.ok) throw new Error("Failed to load datasets");
  return res.json();
}

export async function querySpatialFeatures(params: {
  west: number;
  south: number;
  east: number;
  north: number;
  dataset_ids?: string[];
  layer_ids?: string[];
  zoom?: number;
  limit?: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/features/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error("Failed to query spatial features");
  return res.json();
}

export async function queryNearbyFeatures(params: {
  longitude: number;
  latitude: number;
  radius_meters: number;
  dataset_ids?: string[];
  limit?: number;
}): Promise<any[]> {
  const res = await fetch(`${API_BASE}/features/nearby`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error("Failed to query nearby features");
  return res.json();
}

export async function fetchFeatureDetail(featureId: string): Promise<GeoFeatureDetail> {
  const res = await fetch(`${API_BASE}/features/${encodeURIComponent(featureId)}`);
  if (!res.ok) throw new Error(`Failed to fetch feature detail: ${res.statusText}`);
  return res.json();
}

export async function searchGeographicPlaces(
  query: string,
  limit: number = 10
): Promise<GeographicSearchResult[]> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  const res = await fetch(`${API_BASE}/search?${params.toString()}`);
  if (!res.ok) throw new Error("Geographic search failed");
  return res.json();
}

export async function listSavedMapViews(workspaceId?: string): Promise<UserMapView[]> {
  const url = workspaceId
    ? `${API_BASE}/views?workspace_id=${encodeURIComponent(workspaceId)}`
    : `${API_BASE}/views`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to list saved map views");
  return res.json();
}

export async function saveMapView(payload: {
  name: string;
  camera: any;
  basemap_style_id?: string;
  visible_layers?: string[];
  layer_configurations?: Record<string, any>;
  selected_feature_id?: string | null;
  workspace_id?: string | null;
}): Promise<UserMapView> {
  const res = await fetch(`${API_BASE}/views`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to save map view");
  return res.json();
}

export async function restoreMapView(viewId: string): Promise<UserMapView> {
  const res = await fetch(`${API_BASE}/views/${encodeURIComponent(viewId)}`);
  if (!res.ok) throw new Error("Failed to restore map view");
  return res.json();
}

export async function updateMapView(
  viewId: string,
  expectedRevision: number,
  updates: Record<string, any>
): Promise<UserMapView> {
  const res = await fetch(`${API_BASE}/views/${encodeURIComponent(viewId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ expected_revision: expectedRevision, ...updates }),
  });
  if (res.status === 409) {
    throw new Error("Revision conflict: Map view has been modified elsewhere.");
  }
  if (!res.ok) throw new Error("Failed to update map view");
  return res.json();
}

export async function deleteMapView(viewId: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/views/${encodeURIComponent(viewId)}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete map view");
  return true;
}

