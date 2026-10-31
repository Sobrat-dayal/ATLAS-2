/**
 * API client for the ATLAS Event-to-Entity Knowledge Graph (Stage 136).
 */

import {
  AtlasEventEntityRelationship,
  CanonicalGraphNodeRef,
  EventEntityRelationshipRevision,
  GraphNeighborhood,
  GraphNodeType,
  GraphPath,
  PredicateType,
  RelationshipVerificationStatus,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {
      // Use status text
    }
    throw new Error(errorDetail);
  }

  return res.json() as Promise<T>;
}

export async function getKnowledgeGraphCapabilities() {
  return fetchJson<{
    stage: string;
    subsystem: string;
    max_traversal_depth: number;
    supported_node_types: string[];
    supported_predicates: string[];
    prohibited_predicates: string[];
    zero_look_ahead_enforced: boolean;
    cycle_detection_enforced: boolean;
    multi_tenancy_supported: boolean;
  }>(`${API_BASE}/api/v1/knowledge-graph/capabilities`);
}

export async function getNodeTypes() {
  return fetchJson<{
    node_types: Array<{ code: GraphNodeType; description: string }>;
  }>(`${API_BASE}/api/v1/knowledge-graph/node-types`);
}

export async function getPredicates() {
  return fetchJson<{
    approved_predicates: Array<{ code: PredicateType; name: string; allowed_pairs_count: number }>;
    prohibited_predicates: string[];
  }>(`${API_BASE}/api/v1/knowledge-graph/predicates`);
}

export async function resolveEntity(
  identifier: string,
  idType?: string,
  asOf?: string,
  requireExact: boolean = false
): Promise<CanonicalGraphNodeRef> {
  return fetchJson<CanonicalGraphNodeRef>(`${API_BASE}/api/v1/knowledge-graph/resolve-entity`, {
    method: 'POST',
    body: JSON.stringify({
      identifier,
      id_type: idType || null,
      as_of: asOf || null,
      require_exact: requireExact,
    }),
  });
}

export async function getEventNeighbors(
  eventId: string,
  options?: {
    predicate?: PredicateType;
    minVerification?: RelationshipVerificationStatus;
    asOf?: string;
  }
): Promise<AtlasEventEntityRelationship[]> {
  const params = new URLSearchParams();
  if (options?.predicate) params.append('predicate', options.predicate);
  if (options?.minVerification) params.append('min_verification', options.minVerification);
  if (options?.asOf) params.append('as_of', options.asOf);

  const qs = params.toString() ? `?${params.toString()}` : '';
  return fetchJson<AtlasEventEntityRelationship[]>(
    `${API_BASE}/api/v1/knowledge-graph/events/${encodeURIComponent(eventId)}/neighbors${qs}`
  );
}

export async function getEntityEvents(
  nodeType: GraphNodeType,
  entityId: string,
  options?: {
    predicate?: PredicateType;
    minVerification?: RelationshipVerificationStatus;
    asOf?: string;
  }
): Promise<AtlasEventEntityRelationship[]> {
  const params = new URLSearchParams();
  if (options?.predicate) params.append('predicate', options.predicate);
  if (options?.minVerification) params.append('min_verification', options.minVerification);
  if (options?.asOf) params.append('as_of', options.asOf);

  const qs = params.toString() ? `?${params.toString()}` : '';
  return fetchJson<AtlasEventEntityRelationship[]>(
    `${API_BASE}/api/v1/knowledge-graph/entities/${encodeURIComponent(nodeType)}/${encodeURIComponent(entityId)}/events${qs}`
  );
}

export async function getRelationship(relationshipId: string): Promise<AtlasEventEntityRelationship> {
  return fetchJson<AtlasEventEntityRelationship>(
    `${API_BASE}/api/v1/knowledge-graph/relationships/${encodeURIComponent(relationshipId)}`
  );
}

export async function getRelationshipEvidence(relationshipId: string) {
  return fetchJson<{
    relationship_id: string;
    evidence_ids: string[];
    derivation_method: string;
    assertion_origin: string;
    verification_status: string;
    proximity_metadata?: any;
  }>(`${API_BASE}/api/v1/knowledge-graph/relationships/${encodeURIComponent(relationshipId)}/evidence`);
}

export async function getRelationshipHistory(
  relationshipId: string
): Promise<EventEntityRelationshipRevision[]> {
  return fetchJson<EventEntityRelationshipRevision[]>(
    `${API_BASE}/api/v1/knowledge-graph/relationships/${encodeURIComponent(relationshipId)}/history`
  );
}

export async function findGraphPaths(
  sourceNodeType: GraphNodeType,
  sourceId: string,
  targetNodeType: GraphNodeType,
  targetId: string,
  maxDepth: number = 3,
  asOf?: string
): Promise<GraphPath[]> {
  return fetchJson<GraphPath[]>(`${API_BASE}/api/v1/knowledge-graph/paths`, {
    method: 'POST',
    body: JSON.stringify({
      source_node_type: sourceNodeType,
      source_id: sourceId,
      target_node_type: targetNodeType,
      target_id: targetId,
      max_depth: maxDepth,
      as_of: asOf || null,
    }),
  });
}

export async function getGraphNeighborhood(
  nodeType: GraphNodeType,
  entityId: string,
  depth: number = 1,
  asOf?: string
): Promise<GraphNeighborhood> {
  return fetchJson<GraphNeighborhood>(`${API_BASE}/api/v1/knowledge-graph/neighborhood`, {
    method: 'POST',
    body: JSON.stringify({
      node_type: nodeType,
      entity_id: entityId,
      depth,
      as_of: asOf || null,
    }),
  });
}

export async function evaluateAsOf(asOfTime: string): Promise<AtlasEventEntityRelationship[]> {
  return fetchJson<AtlasEventEntityRelationship[]>(`${API_BASE}/api/v1/knowledge-graph/as-of`, {
    method: 'POST',
    body: JSON.stringify({ as_of_time: asOfTime }),
  });
}

export async function getReviewQueue(): Promise<
  Array<{
    relationship_id: string;
    event_id: string;
    status: string;
    reason: string;
    added_at: string;
    tenant_id?: string | null;
  }>
> {
  return fetchJson(`${API_BASE}/api/v1/knowledge-graph/review-queue`);
}

export async function revokeRelationship(
  relationshipId: string,
  reason: string
): Promise<AtlasEventEntityRelationship> {
  return fetchJson<AtlasEventEntityRelationship>(
    `${API_BASE}/api/v1/knowledge-graph/relationships/${encodeURIComponent(relationshipId)}/revoke`,
    {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }
  );
}

