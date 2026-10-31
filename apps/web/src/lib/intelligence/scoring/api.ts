/**
 * REST API client for ATLAS Intelligence Scoring (Stage 139).
 */

import {
  AtlasIntelligenceScore,
  IntelligenceScoringPolicy,
  RankedItem,
  ScoringCapabilitiesResponse,
  ScoringEvaluationManifest,
  ScoringModelDefinition,
  ScoringObjectiveDefinition,
  ScoringTelemetrySummary,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export async function fetchScoringCapabilities(): Promise<ScoringCapabilitiesResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/scoring/capabilities`);
  if (!res.ok) {
    throw new Error(`Failed to fetch scoring capabilities: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchScoringObjectives(): Promise<ScoringObjectiveDefinition[]> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/scoring/objectives`);
  if (!res.ok) {
    throw new Error(`Failed to fetch scoring objectives: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchScoringModels(): Promise<ScoringModelDefinition[]> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/scoring/models`);
  if (!res.ok) {
    throw new Error(`Failed to fetch scoring models: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchScoringPolicies(objectiveId?: string): Promise<IntelligenceScoringPolicy[]> {
  const query = objectiveId ? `?objective_id=${encodeURIComponent(objectiveId)}` : "";
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/scoring/policies${query}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch scoring policies: ${res.statusText}`);
  }
  return await res.json();
}

export async function calculateIntelligenceScore(payload: {
  event_data: Record<string, unknown>;
  objective_id?: string;
  policy_id?: string;
  model_version?: string;
  known_as_of?: string;
  context?: Record<string, unknown>;
}): Promise<AtlasIntelligenceScore> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/scoring/scores/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Failed to calculate score: ${res.statusText}`);
  }
  return await res.json();
}

export async function queryIntelligenceRankings(payload: {
  candidate_events: Array<Record<string, unknown>>;
  objective_id?: string;
  policy_id?: string;
  model_version?: string;
  known_as_of?: string;
  context?: Record<string, unknown>;
  limit?: number;
}): Promise<RankedItem[]> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/scoring/rankings/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Failed to query rankings: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchScoringEvaluations(): Promise<ScoringEvaluationManifest[]> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/scoring/evaluations`);
  if (!res.ok) {
    throw new Error(`Failed to fetch evaluations: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchScoringTelemetry(modelId: string = "MOD_EVENT_PRIORITY"): Promise<ScoringTelemetrySummary> {
  const res = await fetch(`${BASE_URL}/api/v1/intelligence/scoring/telemetry?model_id=${encodeURIComponent(modelId)}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch telemetry: ${res.statusText}`);
  }
  return await res.json();
}
