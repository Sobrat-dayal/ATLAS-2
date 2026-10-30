/**
 * TypeScript domain contracts for ATLAS Stage 121: Global Workspace Linking.
 */

export type ContextScope = "PANEL_LOCAL" | "WORKSPACE" | "USER_APPLICATION" | "USER_CROSS_TAB";

export type ContextDimension =
  | "INSTRUMENT"
  | "COMPANY"
  | "PORTFOLIO"
  | "BENCHMARK"
  | "ECONOMIC_SERIES"
  | "DATE_RANGE"
  | "AS_OF_DATE"
  | "TIMEFRAME"
  | "REPORTING_CURRENCY"
  | "REGION";

export type SubscriptionMode = "PUBLISH" | "SUBSCRIBE" | "BIDIRECTIONAL" | "INDEPENDENT";

export type ContextEventType =
  | "GLOBAL_CONTEXT_INSTRUMENT_SELECTED"
  | "GLOBAL_CONTEXT_COMPANY_SELECTED"
  | "GLOBAL_CONTEXT_PORTFOLIO_SELECTED"
  | "GLOBAL_CONTEXT_BENCHMARK_SELECTED"
  | "GLOBAL_CONTEXT_ECONOMIC_SERIES_SELECTED"
  | "GLOBAL_CONTEXT_DATE_RANGE_CHANGED"
  | "GLOBAL_CONTEXT_AS_OF_CHANGED"
  | "GLOBAL_CONTEXT_TIMEFRAME_CHANGED"
  | "GLOBAL_CONTEXT_CURRENCY_CHANGED"
  | "GLOBAL_CONTEXT_CHANNEL_CHANGED"
  | "GLOBAL_CONTEXT_SUBSCRIPTION_CHANGED"
  | "GLOBAL_CONTEXT_RESTORED"
  | "GLOBAL_CONTEXT_RESET";

export type LinkingStatus =
  | "LINKED"
  | "INDEPENDENT"
  | "UPDATING"
  | "UPDATED"
  | "INCOMPATIBLE_CONTEXT"
  | "TARGET_UNAVAILABLE"
  | "ACCESS_DENIED"
  | "SOURCE_RESTRICTED"
  | "DATA_LOADING"
  | "DATA_STALE"
  | "UPDATE_FAILED";

export type TransformationType =
  | "INSTRUMENT_TO_COMPANY"
  | "COMPANY_TO_PRIMARY_LISTING"
  | "OPTION_TO_UNDERLYING"
  | "PORTFOLIO_TO_BENCHMARK"
  | "ECONOMIC_SERIES_TO_REGION";

export interface ResolvedEntity {
  entity_id: string;
  entity_type: string;
  canonical_name: string;
  display_name: string;
  symbol?: string | null;
  exchange?: string | null;
  currency?: string | null;
  country?: string | null;
  metadata?: Record<string, unknown>;
}

export interface LinkSubscription {
  subscription_id: string;
  channel_id: string;
  panel_instance_id: string;
  mode: SubscriptionMode;
  inbound_dimensions: ContextDimension[];
  outbound_dimensions: ContextDimension[];
  active: boolean;
  priority_policy: string;
  created_at: string;
}

export interface LinkChannel {
  channel_id: string;
  owner_user_id: string;
  workspace_id?: string | null;
  scope: ContextScope;
  name: string;
  display_color_token: string;
  enabled: boolean;
  supported_dimensions: ContextDimension[];
  context_snapshot: Record<string, unknown>;
  revision: number;
  created_at: string;
  updated_at: string;
}

export interface ContextSelectionEvent {
  event_id: string;
  causation_id?: string | null;
  correlation_id?: string | null;
  origin_user_id?: string;
  origin_workspace_id?: string | null;
  origin_panel_instance_id?: string | null;
  channel_id: string;
  scope: ContextScope;
  dimension: ContextDimension;
  canonical_target_id: string;
  target_type?: string;
  payload: Record<string, unknown>;
  context_revision: number;
  emitted_at: string;
  selection_reason?: string;
}

export interface PanelContextCapability {
  panel_type_id: string;
  publishable_dimensions: ContextDimension[];
  subscribable_dimensions: ContextDimension[];
  accepted_entity_types: string[];
  required_transformations: Record<string, string>;
  supported_timeframes: string[];
  supports_as_of: boolean;
  supports_currency: boolean;
}

export interface ChannelState {
  channel_id: string;
  revision: number;
  context: Record<string, unknown>;
  updated_at: string;
}
