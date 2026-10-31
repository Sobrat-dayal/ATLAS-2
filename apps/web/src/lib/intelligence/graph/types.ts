/**
 * TypeScript domain types for Event-to-Entity Knowledge Graph (Stage 136).
 */

export type GraphNodeType =
  | 'EVENT'
  | 'COMPANY'
  | 'ISSUER'
  | 'LEGAL_ENTITY'
  | 'FINANCIAL_INSTRUMENT'
  | 'SECTOR'
  | 'INDUSTRY'
  | 'COUNTRY'
  | 'ADMINISTRATIVE_REGION'
  | 'COMMODITY'
  | 'ECONOMIC_INDICATOR'
  | 'CENTRAL_BANK'
  | 'REGULATORY_AUTHORITY'
  | 'CORPORATE_FACILITY'
  | 'INFRASTRUCTURE_ASSET'
  | 'OTHER_SUPPORTED_CANONICAL_ENTITY';

export type PredicateType =
  // Event-to-Entity Direct & Mention Predicates
  | 'DIRECT_SUBJECT'
  | 'EXPLICITLY_MENTIONS'
  | 'ANNOUNCED_BY'
  | 'ISSUED_BY'
  | 'REGULATED_BY'
  | 'OFFICIALLY_DESIGNATES'
  | 'OFFICIAL_ACTION_TARGET'
  | 'CORPORATE_ACTION_PARTICIPANT'
  | 'CORPORATE_ACTION_TARGET'
  | 'CONCERNS_INSTRUMENT'
  | 'RELEASES_INDICATOR'
  | 'DECIDED_BY'
  | 'HAS_ISSUING_JURISDICTION'
  | 'OCCURRED_IN'
  | 'REPORTED_AT'
  | 'REFERENCES_COMMODITY'
  | 'REFERENCES_SECTOR'
  | 'REFERENCES_INDUSTRY'
  | 'REFERENCES_FACILITY'
  | 'REFERENCES_INFRASTRUCTURE_ASSET'
  | 'GEOGRAPHICALLY_NEAR'
  | 'SOURCE_REPORTED_ASSOCIATION'
  // Event-to-Event
  | 'REVISES'
  | 'SUPERSEDES'
  | 'CORRECTS'
  | 'RETRACTS'
  | 'FORMAL_FOLLOW_UP_TO'
  | 'IMPLEMENTS'
  | 'OFFICIALLY_RESPONDS_TO'
  // Entity-to-Entity Foundational Structure
  | 'SUBSIDIARY_OF'
  | 'PARENT_OF'
  | 'ISSUED_BY_COMPANY'
  | 'OPERATED_BY'
  | 'LOCATED_IN'
  | 'PRIMARY_EXCHANGE_IN'
  | 'COMPRISING_SECTOR';

export type RelationshipOrigin =
  | 'OFFICIAL_DISCLOSURE'
  | 'REGULATORY_FILING'
  | 'GOVERNMENT_ACTION'
  | 'STATISTICAL_AGENCY'
  | 'CENTRAL_BANK_RELEASE'
  | 'NEWS_REPORT'
  | 'GEOSPATIAL_CALCULATION'
  | 'HUMAN_ANALYST'
  | 'AUTOMATED_LINKER';

export type RelationshipVerificationStatus =
  | 'VERIFIED_DIRECT'
  | 'SOURCE_SUPPORTED'
  | 'CORROBORATED'
  | 'CANDIDATE'
  | 'CONFLICTED'
  | 'REJECTED'
  | 'REVOKED';

export interface CanonicalGraphNodeRef {
  node_type: GraphNodeType;
  entity_id: str;
  canonical_name: str;
  identifier_map: Record<string, string>;
  country_code?: string | null;
  sector?: string | null;
  metadata?: Record<string, any>;
  tenant_id?: string | null;
}

export type str = string;

export interface AtlasEventEntityRelationship {
  relationship_id: string;
  event_id: string;
  event_revision_id?: string | null;
  source_node: CanonicalGraphNodeRef;
  target_node: CanonicalGraphNodeRef;
  predicate: PredicateType;
  relationship_role?: string | null;
  assertion_origin: RelationshipOrigin;
  verification_status: RelationshipVerificationStatus;
  temporal_valid_from?: string | null;
  temporal_valid_to?: string | null;
  knowledge_available_at: string;
  evidence_ids: string[];
  derivation_method: string;
  proximity_metadata?: {
    distance_km?: number;
    calculation_basis?: string;
    event_coordinates?: [number, number];
    asset_coordinates?: [number, number];
    threshold_radius_km?: number;
    disclaimer?: string;
  } | null;
  metadata?: Record<string, any>;
  tenant_id?: string | null;
  is_revoked?: boolean;
  revocation_reason?: string | null;
}

export interface EventEntityRelationshipRevision {
  revision_id: string;
  relationship_id: string;
  revision_number: number;
  changed_fields: Record<string, any>;
  reason: string;
  recorded_at: string;
}

export interface GraphPathHop {
  hop_number: number;
  from_node: CanonicalGraphNodeRef;
  to_node: CanonicalGraphNodeRef;
  predicate: PredicateType;
  relationship_id: string;
  verification_status: RelationshipVerificationStatus;
  evidence_ids: string[];
  temporal_valid_from?: string | null;
  temporal_valid_to?: string | null;
  explanation: string;
}

export interface GraphPath {
  path_id: string;
  source_node: CanonicalGraphNodeRef;
  target_node: CanonicalGraphNodeRef;
  hops: GraphPathHop[];
  total_hops: number;
  factual_explanation: string;
}

export interface GraphNeighborhood {
  center_node: CanonicalGraphNodeRef;
  depth: number;
  nodes: CanonicalGraphNodeRef[];
  relationships: AtlasEventEntityRelationship[];
  total_nodes: number;
  total_relationships: number;
}
