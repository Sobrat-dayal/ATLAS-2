/**
 * Client API for ATLAS INTELLIGENCE V1 (Stage 138).
 */

import {
  IntelligenceInvestigationContext,
  IntelligenceInvestigationPreset,
  IntelligenceOverviewResponse,
  IntelligencePanelDefinition,
  IntelligenceSavedInvestigation,
  IntelligenceSearchResult,
  SourceFreshnessRecord,
} from "./types";
import { CLIENT_INVESTIGATION_PRESETS } from "./presets";

const API_BASE = "/api/v1/intelligence";

export async function fetchIntelligenceCapabilities(): Promise<Record<string, unknown>> {
  try {
    const res = await fetch(`${API_BASE}/capabilities`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("fetchCapabilities fallback", err);
  }
  return {
    stage: 138,
    system_name: "ATLAS INTELLIGENCE V1",
    version: "1.0.0",
    supported_views: [
      "OVERVIEW", "EVENTS", "ENTITIES", "GRAPH", "EXPOSURE",
      "GEOGRAPHY", "INVESTIGATIONS", "HISTORY", "SOURCES"
    ]
  };
}

export async function fetchIntelligenceOverview(params?: {
  as_of?: string;
  selected_entity_id?: string;
  selected_portfolio_id?: string;
}): Promise<IntelligenceOverviewResponse> {
  const res = await fetch(`${API_BASE}/overview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params || {})
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch overview: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchIntelligencePresets(): Promise<IntelligenceInvestigationPreset[]> {
  try {
    const res = await fetch(`${API_BASE}/presets`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("fetchPresets fallback", err);
  }
  return Object.values(CLIENT_INVESTIGATION_PRESETS);
}

export async function fetchIntelligencePanels(): Promise<IntelligencePanelDefinition[]> {
  try {
    const res = await fetch(`${API_BASE}/panels`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("fetchPanels fallback", err);
  }
  return [];
}

export async function executeUnifiedSearch(
  query: string,
  limit = 15
): Promise<IntelligenceSearchResult[]> {
  const res = await fetch(`${API_BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, limit })
  });
  if (!res.ok) {
    throw new Error(`Failed to search: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchSourcesStatus(): Promise<SourceFreshnessRecord[]> {
  try {
    const res = await fetch(`${API_BASE}/sources/status`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("fetchSourcesStatus fallback", err);
  }
  return [];
}

export async function resolveEntityContext(
  entityId: string,
  nodeType?: string,
  asOf?: string
): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/entities/context`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ entity_id: entityId, node_type: nodeType, as_of: asOf })
  });
  if (!res.ok) {
    throw new Error(`Failed to resolve entity context: ${res.statusText}`);
  }
  return await res.json();
}

export async function saveInvestigation(payload: {
  investigation_id: string;
  title: string;
  description?: string;
  primary_subject?: string;
  preset_id?: string;
  context: IntelligenceInvestigationContext;
}): Promise<IntelligenceSavedInvestigation> {
  const res = await fetch(`${API_BASE}/investigations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error(`Failed to save investigation: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchInvestigation(
  investigationId: string
): Promise<IntelligenceSavedInvestigation> {
  const res = await fetch(`${API_BASE}/investigations/${investigationId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch investigation ${investigationId}: ${res.statusText}`);
  }
  return await res.json();
}
