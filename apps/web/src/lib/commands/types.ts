import type { ComponentType } from "react";
import type { AtlasModuleId } from "../../config/atlas-modules";

export type CommandCategory =
  | "navigation"
  | "search"
  | "selection"
  | "settings"
  | "shell";

export type CommandAvailability = "available" | "hidden" | "disabled";

export interface CommandContext {
  pathname: string;
  currentModuleId?: AtlasModuleId;
  selectedEntityId?: string | null;
  canViewModule?: (moduleId: string) => boolean;
  hasPermission?: (permission: string) => boolean;
}

export interface CommandExecutionHelpers {
  navigate: (route: string) => void;
  clearSelectedEntity: () => void;
  focusGlobalSearch: () => void;
  openSectionSettings: (moduleId: AtlasModuleId) => void;
  closePalette: () => void;
  toggleSidebar?: () => void;
  toggleAgentDock?: () => void;
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
  execute: (context: CommandContext, helpers: CommandExecutionHelpers) => Promise<void> | void;
}

export interface CommandMatch {
  command: CommandDefinition;
  tier: number; // 1 (best) to 8 (fuzzy)
  score: number;
  matchedField: "label" | "alias" | "keyword" | "description";
}
