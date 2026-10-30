/**
 * Canonical Types for ATLAS Workspaces Architecture (Stage 120).
 */

export type WorkspaceStatus = "ACTIVE" | "ARCHIVED" | "SOFT_DELETED" | "UNAVAILABLE";

export type WorkspaceType = "CUSTOM" | "TEMPLATE_DERIVED" | "SYSTEM_DEFAULT";

export type LayoutNodeType = "SPLIT" | "TAB_STACK" | "PANEL";

export type SplitOrientation = "HORIZONTAL" | "VERTICAL";

export type PanelTypeId =
  | "MARKET_OVERVIEW"
  | "INSTRUMENT_CHART"
  | "WATCHLIST"
  | "SCREENER"
  | "COMPANY_OVERVIEW"
  | "ECONOMIC_SERIES"
  | "NEWS_FEED"
  | "RESEARCH_DOCUMENT"
  | "RESEARCH_REPORT"
  | "PORTFOLIO_SUMMARY"
  | "PORTFOLIO_PERFORMANCE"
  | "RISK_OVERVIEW"
  | "RISK_ANALYSIS"
  | "DATA_TABLE"
  | "OPTIONS_ANALYTICS"
  | "MAP_VIEW"
  | "INTELLIGENCE_RESULT"
  | "AI_ASSISTANT_VIEW"
  | "AGENT_STATUS";

export type ContextDimension =
  | "INSTRUMENT"
  | "COMPANY"
  | "PORTFOLIO"
  | "BENCHMARK"
  | "DATE_RANGE"
  | "AS_OF_DATE"
  | "TIMEFRAME"
  | "REPORTING_CURRENCY";

export type WorkspaceSortOption = "RECENTLY_OPENED" | "RECENTLY_MODIFIED" | "NAME" | "FAVORITES";

export type SaveState = "SAVED" | "SAVING" | "UNSAVED_CHANGES" | "CONFLICT" | "ERROR";

export interface SplitNode {
  node_id: string;
  node_type: "SPLIT";
  orientation: SplitOrientation;
  children: LayoutNode[];
  size_ratios: number[];
  min_size_rules?: Record<string, number>;
}

export interface TabStackNode {
  node_id: string;
  node_type: "TAB_STACK";
  panel_instance_ids: string[];
  active_panel_instance_id: string;
}

export interface PanelNode {
  node_id: string;
  node_type: "PANEL";
  panel_instance_id: string;
}

export type LayoutNode = SplitNode | TabStackNode | PanelNode;

export interface WorkspacePanelInstance {
  panel_instance_id: string;
  workspace_id: string;
  panel_type_id: PanelTypeId;
  title_override?: string | null;
  configuration: Record<string, unknown>;
  link_group_id?: string | null;
  independent_mode?: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceLinkGroup {
  link_group_id: string;
  workspace_id: string;
  name: string;
  color: string;
  context: Record<string, unknown>;
  version: number;
}

export interface WorkspaceLayout {
  root_node: LayoutNode;
  panel_instances: Record<string, WorkspacePanelInstance>;
  schema_version: number;
}

export interface Workspace {
  workspace_id: string;
  owner_user_id: string;
  organization_id?: string | null;
  name: string;
  description?: string | null;
  workspace_type: WorkspaceType;
  template_origin_id?: string | null;
  layout_schema_version: number;
  layout_revision: number;
  is_default: boolean;
  is_favorite: boolean;
  status: WorkspaceStatus;
  settings: Record<string, unknown>;
  panel_count?: number;
  layout?: WorkspaceLayout;
  link_groups?: WorkspaceLinkGroup[];
  created_at: string;
  updated_at: string;
  last_opened_at: string;
  deleted_at?: string | null;
}

export interface WorkspaceTemplate {
  template_id: string;
  name: string;
  description: string;
  category: string;
  layout_definition: {
    root_node: LayoutNode;
  };
  panel_definitions: Array<{
    panel_instance_id: string;
    panel_type_id: PanelTypeId;
    title_override?: string;
    configuration?: Record<string, unknown>;
    link_group_id?: string | null;
  }>;
  required_capabilities: string[];
  version: number;
}

export interface PanelTypeDefinition {
  panel_type_id: PanelTypeId;
  display_name: string;
  source_module: string;
  description: string;
  category: string;
  min_width_px: number;
  min_height_px: number;
  default_width_ratio: number;
  default_height_ratio: number;
  context_capabilities: ContextDimension[];
  supported_actions: string[];
  is_available: boolean;
  unavailability_reason?: string | null;
}

export interface CreateWorkspaceRequest {
  name: string;
  description?: string;
  template_id?: string;
  initial_layout?: Record<string, unknown>;
}

export interface UpdateWorkspaceMetadataRequest {
  name?: string;
  description?: string;
  is_favorite?: boolean;
  settings?: Record<string, unknown>;
}

export interface UpdateLayoutRequest {
  expected_revision: number;
  layout: {
    root_node: LayoutNode;
    panel_instances?: Record<string, unknown>;
    schema_version?: number;
  };
}

export interface AddPanelRequest {
  panel_type_id: PanelTypeId;
  title_override?: string;
  configuration?: Record<string, unknown>;
  link_group_id?: string;
  dock_target_panel_id?: string;
  dock_position?: "right" | "bottom" | "tab";
}
