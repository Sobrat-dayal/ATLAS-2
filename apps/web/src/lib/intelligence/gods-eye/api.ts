/**
 * Client API functions for ATLAS God's Eye Financial Intelligence (Stage 140).
 */

import {
  GodsEyeCapabilitiesResponse,
  GodsEyeInvestigationResult,
  GodsEyeLensDefinition,
  GodsEyeLensType,
  GodsEyeViewMode,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchGodsEyeCapabilities(): Promise<GodsEyeCapabilitiesResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/gods-eye/capabilities`);
  if (!res.ok) {
    throw new Error(`Failed to fetch God's Eye capabilities: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchGodsEyeLenses(): Promise<GodsEyeLensDefinition[]> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/gods-eye/lenses`);
  if (!res.ok) {
    throw new Error(`Failed to fetch God's Eye lenses: ${res.statusText}`);
  }
  return res.json();
}

export interface InvestigateParams {
  lens?: GodsEyeLensType;
  as_of?: string | null;
  selected_entity_id?: string | null;
  selected_event_id?: string | null;
  selected_portfolio_id?: string | null;
  tenant_id?: string;
  view_mode?: GodsEyeViewMode;
  max_graph_depth?: number;
  max_entities?: number;
  scoring_policy_id?: string | null;
  search_query?: string | null;
}

export async function fetchGodsEyeInvestigation(
  params: InvestigateParams = {}
): Promise<GodsEyeInvestigationResult> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/gods-eye/investigate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      lens: params.lens || "GLOBAL_EVENTS",
      as_of: params.as_of || null,
      selected_entity_id: params.selected_entity_id || null,
      selected_event_id: params.selected_event_id || null,
      selected_portfolio_id: params.selected_portfolio_id || null,
      tenant_id: params.tenant_id || "default",
      view_mode: params.view_mode || "TWO_DIMENSIONAL",
      max_graph_depth: params.max_graph_depth ?? 2,
      max_entities: params.max_entities ?? 50,
      scoring_policy_id: params.scoring_policy_id || null,
      search_query: params.search_query || null,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `God's Eye investigation failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchEntitySituationalAwareness(
  entityId: string,
  lens: GodsEyeLensType = "CORPORATE_INTELLIGENCE",
  asOf?: string | null
): Promise<GodsEyeInvestigationResult> {
  const url = new URL(`${BASE_URL}/api/v1/intelligence/gods-eye/entity/${encodeURIComponent(entityId)}`);
  url.searchParams.set("lens", lens);
  if (asOf) url.searchParams.set("as_of", asOf);

  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`Failed to fetch entity situational awareness: ${res.statusText}`);
  }
  return res.json();
}

export async function reconstructHistoricalWorld(
  asOf: string,
  lens: GodsEyeLensType = "HISTORICAL_RESEARCH",
  selectedEntityId?: string | null
): Promise<GodsEyeInvestigationResult> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/gods-eye/historical-reconstruction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      as_of: asOf,
      lens,
      selected_entity_id: selectedEntityId || null,
    }),
  });

  if (!res.ok) {
    throw new Error(`Failed to reconstruct historical world: ${res.statusText}`);
  }
  return res.json();
}

export async function compareHistoricalVintages(
  entityId: string,
  asOfV1: string,
  asOfV2: string
): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/gods-eye/compare-vintages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      entity_id: entityId,
      as_of_v1: asOfV1,
      as_of_v2: asOfV2,
    }),
  });

  if (!res.ok) {
    throw new Error(`Failed to compare historical vintages: ${res.statusText}`);
  }
  return res.json();
}

