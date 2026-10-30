import type { ComponentType } from "react";
import type { AtlasModuleId } from "../../config/atlas-modules";

export type CommandCategory =
  | "navigation"
  | "search"
  | "selection"
  | "settings"
  | "shell";

export type CommandAvailability = "available" | "hidden" | "disabled";

export type AtlasCommandParseStatus =
  | "READY"
  | "INCOMPLETE"
  | "AMBIGUOUS"
  | "INVALID"
  | "UNAVAILABLE";

export type AtlasCommandSourceKind = "slash" | "shorthand";

export interface ResolvedTargetSummary {
  entity_id: string;
  entity_type: string;
  canonical_name: string;
  display_name: string;
  matched_value: string;
  match_kind: string;
  scope_entity_id?: string | null;
}

export interface AmbiguityCandidate {
  entity_id: string;
  entity_type: string;
  canonical_name: string;
  display_name: string;
  matched_value: string;
  match_kind: string;
  scope_entity_id?: string | null;
}

export interface AtlasCommandParseResult {
  command_language_version: number;
  status: AtlasCommandParseStatus;
  source_kind?: AtlasCommandSourceKind | null;
  normalized_command: string;
  command_id?: string | null;
  module?: string | null;
  action?: string | null;
  raw_target?: string | null;
  resolved_target?: ResolvedTargetSummary | null;
  arguments?: Record<string, unknown> | null;
  error_code?: string | null;
  error_message?: string | null;
  ambiguity_candidates?: AmbiguityCandidate[] | null;
  execution_summary?: string | null;
}

export interface CommandContext {
  pathname: string;
  currentModuleId?: AtlasModuleId;
  selectedEntityId?: string | null;
  canViewModule?: (moduleId: string) => boolean;
  hasPermission?: (permission: string) => boolean;
}

export interface CommandExecutionHelpers {
  navigate: (route: string) => void;
  selectEntity?: (entityId: string) => void;
  clearSelectedEntity: () => void;
  focusGlobalSearch: () => void;
  openSectionSettings: (moduleId: AtlasModuleId) => void;
  closePalette: () => void;
  toggleSidebar?: () => void;
  toggleAgentDock?: () => void;
  toggleTerminal?: () => void;
}

export interface CommandDefinition {
  id: string;
  label: string;
  description?: string;
  category: CommandCategory;
  keywords?: string[];
  aliases?: string[];
  icon?: ComponentType<{ className?: string }>;
  shortcut?: string;
  availability?: (context: CommandContext) => CommandAvailability;
  execute: (
    context: CommandContext,
    helpers: CommandExecutionHelpers,
    args?: Record<string, unknown>
  ) => Promise<void> | void;
}

export interface CommandMatch {
  command: CommandDefinition;
  tier: number; // 1 (best) to 8 (fuzzy)
  score: number;
  matchedField: "label" | "alias" | "keyword" | "description";
}
