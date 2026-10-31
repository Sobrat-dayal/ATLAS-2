/**
 * Types for ATLAS INTELLIGENCE V1 (Stage 138).
 */

export type IntelligenceViewType =
  | "OVERVIEW"
  | "EVENTS"
  | "SCORING"
  | "ENTITIES"
  | "GRAPH"
  | "EXPOSURE"
  | "GEOGRAPHY"
  | "INVESTIGATIONS"
  | "HISTORY"
  | "SOURCES";

export type SectionStatus =
  | "READY"
  | "EMPTY"
  | "PARTIAL"
  | "STALE"
  | "SOURCE_UNAVAILABLE"
  | "ACCESS_DENIED"
  | "FAILED";

export type IntelligencePanelType =
  | "EVENT_MONITOR"
  | "EVENT_INSPECTOR"
  | "ENTITY_CONTEXT"
  | "ENTITY_GRAPH"
  | "EXPOSURE_SUMMARY"
  | "EXPOSURE_INSPECTOR"
  | "GEOGRAPHY_MAP"
  | "RESEARCH_EVIDENCE"
  | "SOURCE_INSPECTOR"
  | "COVERAGE_PANEL";

export interface IntelligencePanelDefinition {
  panel_type: IntelligencePanelType;
  title: string;
  description: string;
  supported_context_types: string[];
  supports_historical_asof: boolean;
  supports_linking: boolean;
  default_width_pct: number;
  default_height_pct: number;
}

export interface SourceFreshnessRecord {
  source_id: string;
  source_name: string;
  dataset: string;
  status: SectionStatus;
  last_updated: string;
  effective_data_date?: string | null;
  coverage_percentage?: string | number | null;
  verification_supported: boolean;
  historical_supported: boolean;
  licensing_restriction?: string | null;
  notes: string[];
}

export interface IntelligenceSearchResult {
  result_type: "EVENT" | "ENTITY" | "SOURCE" | "RESEARCH_DOCUMENT";
  entity_type?: string | null;
  canonical_id: string;
  display_title: string;
  disambiguation: string;
  source_reference?: string | null;
  timestamp?: string | null;
  verification_status?: string | null;
  is_entitled: boolean;
}

export interface IntelligenceInvestigationContext {
  context_id: string;
  selected_event_id?: string | null;
  selected_entity_ref?: {
    node_type: string;
    entity_id: string;
    canonical_name: string;
    country_code?: string | null;
    sector?: string | null;
  } | null;
  selected_portfolio_id?: string | null;
  selected_relationship_id?: string | null;
  selected_exposure_run_id?: string | null;
  selected_source_id?: string | null;
  geographic_scope?: Record<string, unknown> | null;
  time_window_start?: string | null;
  time_window_end?: string | null;
  known_as_of: string;
  valid_at?: string | null;
  active_filters?: Record<string, unknown>;
  tenant_id?: string | null;
}

export interface IntelligenceInvestigationPreset {
  preset_id: string;
  name: string;
  description: string;
  panels: IntelligencePanelType[];
  linking_channels: string[];
}

export interface IntelligenceSavedInvestigation {
  investigation_id: string;
  title: string;
  description?: string | null;
  owner_id: string;
  tenant_id?: string | null;
  primary_subject?: string | null;
  context: IntelligenceInvestigationContext;
  preset_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface IntelligenceOverviewSection {
  section_id: string;
  title: string;
  status: SectionStatus;
  items_count: number;
  data: Array<Record<string, unknown>>;
  warnings: string[];
  as_of: string;
}

export interface IntelligenceOverviewResponse {
  overview_id: string;
  generated_at: string;
  known_as_of: string;
  sections: Record<string, IntelligenceOverviewSection>;
  source_freshness: SourceFreshnessRecord[];
  active_warnings: string[];
  tenant_id?: string | null;
}
