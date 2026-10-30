/**
 * Type definitions for Stage 125: ATLAS AI Context Awareness Engine.
 */

export type ContextMode = "OFF" | "FOCUSED" | "WORKSPACE" | "CUSTOM";

export type DataQualityStatus = "COMPLETE" | "PARTIAL" | "STALE" | "RESTRICTED";

export type ProviderDisclosureStatus = "ALLOWED" | "REDACTED" | "PROHIBITED";

export type ContextType =
  | "PAGE_CONTEXT"
  | "MODULE_CONTEXT"
  | "INSTRUMENT_CONTEXT"
  | "COMPANY_CONTEXT"
  | "CHART_CONTEXT"
  | "WATCHLIST_CONTEXT"
  | "SCREENER_CONTEXT"
  | "ECONOMICS_CONTEXT"
  | "NEWS_CONTEXT"
  | "RESEARCH_CONTEXT"
  | "PORTFOLIO_CONTEXT"
  | "RISK_CONTEXT"
  | "OPTIONS_CONTEXT"
  | "DATA_CONTEXT"
  | "SAVED_RESOURCE_CONTEXT"
  | "WORKSPACE_CONTEXT"
  | "WORKSPACE_PANEL_CONTEXT"
  | "LINKED_CONTEXT"
  | "USER_SUPPLIED_CONTEXT";

export interface ContextItem {
  context_item_id: string;
  context_type: ContextType;
  canonical_target_id: string;
  source_reference: string;
  as_of: string;
  content_summary: string;
  data_quality_status: DataQualityStatus;
  provider_disclosure_status: ProviderDisclosureStatus;
  estimated_tokens: number;
  content_hash: string;
  is_pinned: boolean;
  relevance_score: number;
  structured_payload: Record<string, unknown>;
  provenance: Record<string, unknown>;
}

export interface ContextExcludedItem {
  target_id: string;
  type: string;
  reason: string;
  detail?: string | null;
}

export interface AiContextEnvelope {
  context_request_id: string;
  context_mode: ContextMode;
  source_page: string;
  active_module: string;
  active_workspace_id?: string | null;
  focused_panel_id?: string | null;
  global_link_channel_id?: string | null;
  resolved_context_items: ContextItem[];
  excluded_items: ContextExcludedItem[];
  total_estimated_tokens: number;
  token_budget: number;
  quality_summary: string;
  warnings: string[];
  assembled_at: string;
}

export interface AiContextPreferences {
  preference_id: string;
  owner_user_id: string;
  tenant_id?: string | null;
  context_mode: ContextMode;
  allow_workspace_context: boolean;
  allow_portfolio_holdings_context: boolean;
  allow_research_drafts_context: boolean;
  pinned_context_references: string[];
  excluded_context_references: string[];
  provider_disclosure_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateAiContextPreferencesRequest {
  context_mode?: ContextMode;
  allow_workspace_context?: boolean;
  allow_portfolio_holdings_context?: boolean;
  allow_research_drafts_context?: boolean;
  pinned_context_references?: string[];
  excluded_context_references?: string[];
  provider_disclosure_enabled?: boolean;
}

export interface AiContextCapability {
  capability_id: string;
  module_route: string;
  context_type: string;
  display_name: string;
  description: string;
  sensitivity_tier: string;
  provider_disclosure_policy: string;
  requires_explicit_consent: boolean;
}

export interface AiContextPreviewRequest {
  current_route: string;
  active_module?: string;
  workspace_id?: string;
  focused_panel_id?: string;
  global_link_channel_id?: string;
  context_mode_override?: ContextMode;
  requested_references?: Array<{
    type: string;
    target_id: string;
    is_pinned?: boolean;
    parameters?: Record<string, unknown>;
  }>;
  extra_adapter_params?: Record<string, unknown>;
}

export interface AiContextSourceManifest {
  manifest_id: string;
  generation_id: string;
  owner_user_id: string;
  tenant_id?: string | null;
  context_mode: string;
  source_items: Array<{
    context_item_id: string;
    context_type: string;
    target_id: string;
    source_reference: string;
    as_of?: string;
    data_quality?: string;
    content_hash?: string;
    tokens?: number;
  }>;
  total_estimated_tokens: number;
  assembled_at: string;
  created_at: string;
}

