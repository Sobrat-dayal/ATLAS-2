/**
 * TypeScript Contracts for ATLAS God's Eye Financial Intelligence (Stage 140).
 */

export type GodsEyeLensType =
  | "GLOBAL_EVENTS"
  | "MONETARY_POLICY"
  | "CORPORATE_INTELLIGENCE"
  | "GEOPOLITICAL"
  | "COMMODITY_INFRASTRUCTURE"
  | "PHYSICAL_WORLD"
  | "PORTFOLIO_INTELLIGENCE"
  | "HISTORICAL_RESEARCH";

export type GodsEyeViewMode =
  | "TWO_DIMENSIONAL"
  | "THREE_DIMENSIONAL_GLOBE"
  | "HYBRID_SPLIT";

export type GodsEyeDamageAssessmentStatus =
  | "UNKNOWN"
  | "CONFIRMED_OPERATIONAL"
  | "REPORTED_DISRUPTED"
  | "CONFIRMED_DAMAGED"
  | "DESTROYED";

export type GodsEyeSectionStatus =
  | "READY"
  | "DEGRADED"
  | "EMPTY"
  | "RESTRICTED"
  | "ERROR";

export interface MarketContextSnapshot {
  benchmark_symbol: string;
  price_before: number;
  price_after: number;
  pct_change: number;
  time_window: string;
  is_observational_only: boolean;
  disclaimer: string;
}

export interface GodsEyeMapFeature {
  id: string;
  feature_type: string;
  name: string;
  coordinates: number[];
  geometry_type: string;
  properties: Record<string, any>;
  confidence: number;
  verified: boolean;
  damage_status: GodsEyeDamageAssessmentStatus;
}

export interface GodsEyeLensDefinition {
  lens_id: GodsEyeLensType;
  label: string;
  description: string;
  primary_event_categories: string[];
  default_layers: string[];
  default_view_mode: GodsEyeViewMode;
  requires_portfolio: boolean;
  supported_graph_predicates: string[];
}

export interface GodsEyeInvestigationResult {
  investigation_id: string;
  lens: GodsEyeLensType;
  as_of: string;
  is_historical_reconstruction: boolean;
  view_mode: GodsEyeViewMode;
  events: Array<{
    event_id: string;
    category: string;
    title: string;
    occurred_at: string;
    published_at: string;
    ingested_at: string;
    verification_status: string;
    severity: string;
    priority_score?: number;
    priority_tier?: string;
    scoring_factors?: Array<{ name: string; contribution: number }>;
  }>;
  map_features: GodsEyeMapFeature[];
  knowledge_graph_subgraph: {
    root_node: string;
    traversal_depth: number;
    node_count: number;
    edge_count: number;
    nodes: Array<{ id: string; label: string; type: string; is_root?: boolean }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
      predicate: string;
      confidence?: number;
      verified?: boolean;
      valid_from?: string;
      valid_to?: string | null;
      is_active_as_of?: boolean;
    }>;
  };
  exposure_summary?: {
    entity_or_portfolio_id: string;
    gross_revenue_exposure_pct?: number;
    supply_chain_tier1_concentration_pct?: number;
    portfolio_lookthrough_weight_pct?: number | null;
    primary_vulnerable_corridor?: string;
    disclaimer: string;
    coverage_status: string;
  } | null;
  scoring_summary?: {
    model_version: string;
    policy_applied: string;
    top_priority_score?: number | null;
    disclaimer: string;
  } | null;
  market_context?: MarketContextSnapshot | null;
  evidence_sources: Array<{
    source_id: string;
    name: string;
    source_type: string;
    verification_tier: string;
    url?: string;
  }>;
  section_statuses: Record<string, GodsEyeSectionStatus>;
  disclaimers: Record<string, string>;
  coverage_notes: string[];
  telemetry: Record<string, any>;
}

export interface GodsEyeCapabilitiesResponse {
  stage: number;
  system_name: string;
  version: string;
  supported_lenses: GodsEyeLensType[];
  supported_view_modes: GodsEyeViewMode[];
  guarantees: string[];
  disclaimers: Record<string, string>;
}

