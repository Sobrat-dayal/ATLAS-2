/**
 * Frontend Client for ATLAS Physical Infrastructure Intelligence Endpoints (Stage 133).
 */

import {
  H3InfrastructureCell,
  InfrastructureAsset,
  InfrastructureNetwork,
  RegionalSummary,
} from './types';

const API_BASE = '/api/v1/maps/infrastructure';

export async function fetchInfrastructureCategories(): Promise<any> {
  const res = await fetch(`${API_BASE}/categories`);
  if (!res.ok) throw new Error(`Failed to fetch categories: ${res.statusText}`);
  return res.json();
}

export async function fetchInfrastructureDatasets(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/datasets`);
  if (!res.ok) throw new Error(`Failed to fetch datasets: ${res.statusText}`);
  return res.json();
}

export async function fetchInfrastructureAssets(params?: {
  sector?: string;
  asset_type?: string;
  country?: string;
  company_id?: string;
  operator_id?: string;
  status?: string;
  min_capacity?: number;
  max_capacity?: number;
  capacity_metric?: string;
  historical_as_of?: string;
  actor_tenant_id?: string;
  is_commercial?: boolean;
  limit?: number;
}): Promise<{ count: number; assets: InfrastructureAsset[] }> {
  const searchParams = new URLSearchParams();
  if (params?.sector) searchParams.set('sector', params.sector);
  if (params?.asset_type) searchParams.set('asset_type', params.asset_type);
  if (params?.country) searchParams.set('country', params.country);
  if (params?.company_id) searchParams.set('company_id', params.company_id);
  if (params?.operator_id) searchParams.set('operator_id', params.operator_id);
  if (params?.status) searchParams.set('status', params.status);
  if (params?.min_capacity !== undefined) searchParams.set('min_capacity', String(params.min_capacity));
  if (params?.max_capacity !== undefined) searchParams.set('max_capacity', String(params.max_capacity));
  if (params?.capacity_metric) searchParams.set('capacity_metric', params.capacity_metric);
  if (params?.historical_as_of) searchParams.set('historical_as_of', params.historical_as_of);
  if (params?.actor_tenant_id) searchParams.set('actor_tenant_id', params.actor_tenant_id);
  if (params?.is_commercial !== undefined) searchParams.set('is_commercial', String(params.is_commercial));
  if (params?.limit) searchParams.set('limit', String(params.limit));

  const url = `${API_BASE}/assets?${searchParams.toString()}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to list assets: ${res.statusText}`);
  return res.json();
}

export async function fetchInfrastructureAsset(
  assetId: string,
  actorTenantId?: string
): Promise<InfrastructureAsset> {
  const searchParams = new URLSearchParams();
  if (actorTenantId) searchParams.set('actor_tenant_id', actorTenantId);

  const res = await fetch(`${API_BASE}/assets/${assetId}?${searchParams.toString()}`);
  if (!res.ok) throw new Error(`Asset '${assetId}' not found or restricted.`);
  return res.json();
}

export async function fetchAssetHistory(assetId: string): Promise<any[]> {
  const res = await fetch(`${API_BASE}/assets/${assetId}/history`);
  if (!res.ok) throw new Error(`Failed to fetch history for '${assetId}'.`);
  return res.json();
}

export async function fetchAssetRelationships(assetId: string): Promise<any[]> {
  const res = await fetch(`${API_BASE}/assets/${assetId}/relationships`);
  if (!res.ok) throw new Error(`Failed to fetch relationships for '${assetId}'.`);
  return res.json();
}

export async function searchSpatialAssets(
  bbox: [number, number, number, number],
  sector?: string,
  limit: number = 200
): Promise<{ count: number; assets: InfrastructureAsset[] }> {
  const res = await fetch(`${API_BASE}/assets/spatial-query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      min_lng: bbox[0],
      min_lat: bbox[1],
      max_lng: bbox[2],
      max_lat: bbox[3],
      sector,
      limit,
    }),
  });
  if (!res.ok) throw new Error(`Spatial query failed: ${res.statusText}`);
  return res.json();
}

export async function compareInfrastructureAssets(assetIds: string[]): Promise<any> {
  const res = await fetch(`${API_BASE}/assets/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ asset_ids: assetIds }),
  });
  if (!res.ok) throw new Error(`Comparison failed: ${res.statusText}`);
  return res.json();
}

export async function fetchNetworks(params?: {
  sector?: string;
  country?: string;
}): Promise<InfrastructureNetwork[]> {
  const searchParams = new URLSearchParams();
  if (params?.sector) searchParams.set('sector', params.sector);
  if (params?.country) searchParams.set('country', params.country);

  const res = await fetch(`${API_BASE}/networks?${searchParams.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch networks: ${res.statusText}`);
  return res.json();
}

export async function fetchNetwork(networkId: string): Promise<InfrastructureNetwork> {
  const res = await fetch(`${API_BASE}/networks/${networkId}`);
  if (!res.ok) throw new Error(`Failed to fetch network '${networkId}'.`);
  return res.json();
}

export async function queryNetworkSubgraph(
  networkId: string,
  startNodeId: string,
  maxHops: number = 5,
  onlyVerified: boolean = true
): Promise<any> {
  const res = await fetch(`${API_BASE}/networks/${networkId}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      start_node_id: startNodeId,
      max_hops: maxHops,
      only_verified: onlyVerified,
    }),
  });
  if (!res.ok) throw new Error(`Network query failed: ${res.statusText}`);
  return res.json();
}

export async function findNetworkConnection(
  networkId: string,
  startNodeId: string,
  targetNodeId: string,
  onlyVerified: boolean = true
): Promise<any> {
  const res = await fetch(`${API_BASE}/networks/${networkId}/connections`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      start_node_id: startNodeId,
      target_node_id: targetNodeId,
      only_verified: onlyVerified,
    }),
  });
  if (!res.ok) throw new Error(`Connection query failed: ${res.statusText}`);
  return res.json();
}

export async function fetchH3Aggregates(
  resolution: number = 7,
  sector?: string,
  country?: string
): Promise<{ resolution: number; cell_count: number; cells: H3InfrastructureCell[] }> {
  const res = await fetch(`${API_BASE}/aggregates`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resolution, sector, country }),
  });
  if (!res.ok) throw new Error(`H3 aggregation failed: ${res.statusText}`);
  return res.json();
}

export async function fetchCompanyInfrastructure(companyId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/companies/${companyId}/assets`);
  if (!res.ok) throw new Error(`Failed to fetch company infrastructure: ${res.statusText}`);
  return res.json();
}

export async function fetchRegionalSummary(
  regionName: string = 'Target Region',
  country?: string
): Promise<RegionalSummary> {
  const res = await fetch(`${API_BASE}/regional-summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ region_name: regionName, country }),
  });
  if (!res.ok) throw new Error(`Failed to fetch regional summary: ${res.statusText}`);
  return res.json();
}
