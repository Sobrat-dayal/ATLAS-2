/**
 * TypeScript Data Transfer Objects for Company Supply Chain Intelligence (Stage 88).
 * Strictly mirrors backend schemas in atlas.companies.supply_chain.schemas.
 */

export type SupplyChainRelationshipType =
  | "SUPPLIES_COMPONENTS_TO"
  | "SUPPLIES_RAW_MATERIALS_TO"
  | "SUPPLIES_PRODUCTS_TO"
  | "PROVIDES_SERVICES_TO"
  | "CONTRACT_MANUFACTURES_FOR"
  | "OEM_SUPPLIES_TO"
  | "ODM_MANUFACTURES_FOR"
  | "DISTRIBUTES_PRODUCTS_FOR"
  | "PROVIDES_LOGISTICS_TO"
  | "SELLS_GOODS_TO"
  | "LICENSES_TECHNOLOGY_TO"
  | "OTHER_COMMERCIAL_RELATIONSHIP";

export type RelationshipDirection = "UPSTREAM_SUPPLIER" | "DOWNSTREAM_CUSTOMER";

export type VerificationStatus =
  | "VERIFIED"
  | "SOURCE_REPORTED"
  | "CORROBORATED"
  | "CANDIDATE_UNVERIFIED"
  | "DISPUTED"
  | "OBSOLETE"
  | "UNKNOWN";

export type RelationshipLifecycleStatus =
  | "ACTIVE_CONFIRMED"
  | "HISTORICALLY_REPORTED"
  | "PLANNED"
  | "TERMINATED_CONFIRMED"
  | "STATUS_UNKNOWN";

export type ConcentrationScope =
  | "CONSOLIDATED_REVENUE"
  | "SEGMENT_REVENUE"
  | "TOTAL_PROCUREMENT_SPEND"
  | "DIRECT_MATERIALS_SPEND"
  | "SOURCE_DEFINED";

export type EntityKind = "PUBLIC_COMPANY" | "PRIVATE_COMPANY" | "SUBSIDIARY" | "CORPORATE_GROUP";

export interface RelationshipEvidenceDTO {
  evidence_id: string;
  source_document_id: string;
  source_provider_id: string;
  source_title: string;
  section_anchor: string;
  filing_date: string;
  published_at: string;
  observed_at: string;
  excerpt: string;
  review_status: string;
  entitlement_scope: string;
  document_url?: string | null;
}

export interface SupplyChainRelationshipDTO {
  relationship_id: string;
  supplier_entity_id: string;
  supplier_name: string;
  customer_entity_id: string;
  customer_name: string;
  relationship_type: SupplyChainRelationshipType;
  supplied_item_type: string;
  supplied_item_description: string;
  verification_status: VerificationStatus;
  lifecycle_status: RelationshipLifecycleStatus;
  is_direct: boolean;
  tier_level: number;
  contract_value_usd?: number | null;
  reported_revenue_percentage?: number | null;
  effective_from?: string | null;
  effective_to?: string | null;
  last_reported_at?: string | null;
  evidence_count: number;
  primary_evidence?: RelationshipEvidenceDTO | null;
  notes?: string | null;
}

export interface SuppliersListResponseDTO {
  subject_company_entity_id: string;
  total_suppliers: number;
  suppliers: SupplyChainRelationshipDTO[];
  tier_1_count: number;
  tier_2_count: number;
}

export interface CustomersListResponseDTO {
  subject_company_entity_id: string;
  total_customers: number;
  customers: SupplyChainRelationshipDTO[];
  tier_1_count: number;
  tier_2_count: number;
}

export interface SupplyChainNodeDTO {
  entity_id: string;
  name: string;
  kind: EntityKind;
  ticker?: string | null;
  country: string;
  industry: string;
  sector: string;
  tier: number;
  is_subject: boolean;
}

export interface SupplyChainEdgeDTO {
  relationship_id: string;
  source: string;
  target: string;
  relationship_type: SupplyChainRelationshipType;
  item_description: string;
  verification_status: VerificationStatus;
  lifecycle_status: RelationshipLifecycleStatus;
  tier_level: number;
  evidence_count: number;
}

export interface SupplyChainNetworkResponseDTO {
  subject_company_entity_id: string;
  traversal_depth: number;
  direction: string;
  nodes: SupplyChainNodeDTO[];
  edges: SupplyChainEdgeDTO[];
  node_count: number;
  edge_count: number;
  truncated: boolean;
}

export interface ConcentrationObservationDTO {
  observation_id: string;
  subject_company_entity_id: string;
  counterparty_entity_id?: string | null;
  counterparty_name: string;
  is_anonymous: boolean;
  relationship_direction: RelationshipDirection;
  reporting_period: string;
  fiscal_year: number;
  source_reported_percentage?: number | null;
  derived_percentage?: number | null;
  exposure_amount_usd?: number | null;
  scope: ConcentrationScope;
  denominator_description: string;
  evidence_reference: string;
  filing_date: string;
  notes?: string | null;
}

export interface ConcentrationResponseDTO {
  subject_company_entity_id: string;
  customer_concentration: ConcentrationObservationDTO[];
  supplier_concentration: ConcentrationObservationDTO[];
  top_customer_combined_pct?: number | null;
  top_supplier_combined_pct?: number | null;
  currency: string;
  reporting_period: string;
  qualitative_summary: string;
}

export interface HistoricalRelationshipEventDTO {
  event_id: string;
  relationship_id: string;
  counterparty_entity_id: string;
  counterparty_name: string;
  event_type: string;
  event_date: string;
  description: string;
  source_reference: string;
  verification_status: VerificationStatus;
}

export interface HistoricalTimelineResponseDTO {
  subject_company_entity_id: string;
  events: HistoricalRelationshipEventDTO[];
  total_events: number;
  first_observation_date?: string | null;
  latest_observation_date?: string | null;
}

export interface SupplyChainCoverageResponseDTO {
  subject_company_entity_id: string;
  verified_supplier_count: number;
  verified_customer_count: number;
  unresolved_counterparty_count: number;
  authorized_providers: string[];
  jurisdiction_coverage: string[];
  latest_filing_date?: string | null;
  stale_disclosures_count: number;
  coverage_statement: string;
  limitations: string[];
}

export interface SupplyChainOverviewResponseDTO {
  subject_company_entity_id: string;
  company_name: string;
  ticker?: string | null;
  industry: string;
  verified_tier_1_suppliers_count: number;
  verified_tier_1_customers_count: number;
  tier_2_upstream_count: number;
  tier_2_downstream_count: number;
  has_material_customer_concentration: boolean;
  has_critical_single_source_suppliers: boolean;
  latest_disclosure_date?: string | null;
  coverage: SupplyChainCoverageResponseDTO;
}

export interface SupplyChainFiltersDTO {
  relationship_types: SupplyChainRelationshipType[];
  verification_statuses: VerificationStatus[];
  lifecycle_statuses: RelationshipLifecycleStatus[];
  countries: string[];
}
