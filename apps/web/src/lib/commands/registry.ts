import {
  Settings,
  Sliders,
  Search,
  XCircle,
  PanelLeft,
  Bot,
} from "lucide-react";
import { ATLAS_MODULES_LIST } from "../../config/atlas-modules";
import { SECTION_SETTINGS_REGISTRY } from "../../config/section-settings";
import type {
  CommandDefinition,
  CommandContext,
} from "./types";

/**
 * Generates the 20 canonical navigation commands corresponding to the 20 ATLAS modules.
 */
function createNavigationCommands(): CommandDefinition[] {
  return ATLAS_MODULES_LIST.map((module) => {
    const rawAliases = module.aliases || [];
    const keywords = [
      module.label.toLowerCase(),
      module.route.replace("/", ""),
      ...rawAliases.map((a) => a.toLowerCase()),
    ];

    return {
      id: `navigation.${module.id}`,
      label: `Go to ${module.label}`,
      description: module.description,
      category: "navigation",
      keywords: Array.from(new Set(keywords)),
      aliases: rawAliases,
      icon: module.icon,
      availability: (context: CommandContext) => {
        if (context.canViewModule && !context.canViewModule(module.id)) {
          return "hidden";
        }
        return "available";
      },
      execute: (_context, helpers) => {
        helpers.navigate(module.route);
      },
    };
  });
}

/**
 * Creates the standard shell, settings, search, and selection commands.
 */
function createShellCommands(): CommandDefinition[] {
  return [
    {
      id: "search.focus",
      label: "Search Entities",
      description: "Focus global entity search for companies, securities, and countries.",
      category: "search",
      keywords: [
        "search",
        "find",
        "lookup",
        "ticker",
        "company",
        "security",
        "instrument",
        "isin",
        "figi",
        "country",
        "macro",
        "series",
      ],
      aliases: ["search", "find", "entities"],
      icon: Search,
      execute: (_context, helpers) => {
        helpers.focusGlobalSearch();
      },
    },
    {
      id: "entity.selection.clear",
      label: "Clear Selected Entity",
      description: "Deselect currently active entity context across all workspaces.",
      category: "selection",
      keywords: [
        "clear",
        "deselect",
        "reset",
        "entity",
        "unselect",
        "remove entity",
      ],
      aliases: ["clear entity", "deselect"],
      icon: XCircle,
      availability: (context: CommandContext) => {
        return context.selectedEntityId ? "available" : "hidden";
      },
      execute: (_context, helpers) => {
        helpers.clearSelectedEntity();
      },
    },
    {
      id: "settings.global.open",
      label: "Open Global Settings",
      description: "Open global application preferences, security, and appearance.",
      category: "settings",
      keywords: [
        "settings",
        "preferences",
        "configuration",
        "config",
        "options",
        "account",
        "theme",
      ],
      aliases: ["settings", "preferences", "config"],
      icon: Settings,
      shortcut: "⌘,",
      execute: (_context, helpers) => {
        helpers.navigate("/settings");
      },
    },
    {
      id: "settings.section.open",
      label: "Open Current Section Settings",
      description: "Configure view preferences and settings for the active workspace module.",
      category: "settings",
      keywords: [
        "section settings",
        "module settings",
        "customize",
        "configure",
        "view options",
      ],
      aliases: ["section settings", "module settings"],
      icon: Sliders,
      availability: (context: CommandContext) => {
        if (
          context.currentModuleId &&
          SECTION_SETTINGS_REGISTRY[context.currentModuleId]
        ) {
          return "available";
        }
        return "hidden";
      },
      execute: (context, helpers) => {
        if (context.currentModuleId) {
          helpers.openSectionSettings(context.currentModuleId);
        }
      },
    },
    {
      id: "shell.sidebar.toggle",
      label: "Toggle Sidebar",
      description: "Collapse or expand the application navigation sidebar.",
      category: "shell",
      keywords: ["sidebar", "navigation", "collapse", "expand", "menu"],
      aliases: ["sidebar", "collapse sidebar"],
      icon: PanelLeft,
      execute: (_context, helpers) => {
        helpers.toggleSidebar?.();
      },
    },
    {
      id: "shell.agent_dock.toggle",
      label: "Toggle Agent Dock",
      description: "Open or close the side docked agent intelligence panel.",
      category: "shell",
      keywords: ["agent dock", "dock", "agent", "assistant", "ai panel"],
      aliases: ["dock", "agent dock"],
      icon: Bot,
      execute: (_context, helpers) => {
        helpers.toggleAgentDock?.();
      },
    },
  ];
}

/**
 * Validates registry definitions to guarantee unique IDs, non-empty labels,
 * and valid categories. Throws in development/tests if invalid.
 */
function validateCommandRegistry(commands: CommandDefinition[]): void {
  const seenIds = new Set<string>();
  for (const cmd of commands) {
    if (!cmd.id || cmd.id.trim() === "") {
      throw new Error("Command definition missing id");
    }
    if (seenIds.has(cmd.id)) {
      throw new Error(`Duplicate command ID detected in registry: "${cmd.id}"`);
    }
    seenIds.add(cmd.id);

    if (!cmd.label || cmd.label.trim() === "") {
      throw new Error(`Command "${cmd.id}" missing label`);
    }
    if (!cmd.category) {
      throw new Error(`Command "${cmd.id}" missing category`);
    }
    if (typeof cmd.execute !== "function") {
      throw new Error(`Command "${cmd.id}" missing execute handler function`);
    }
  }
}

/**
 * Generates the Stage 47 entity-context navigation commands.
 * These commands update the active selected entity and route to the target module.
 */
function createEntityNavigationCommands(): CommandDefinition[] {
  const entityModules = [
    { id: "charts", label: "Open in Charts", route: "/charts" },
    { id: "news", label: "Open in News", route: "/news" },
    { id: "research", label: "Open in Research", route: "/research" },
    { id: "maps", label: "Open in Maps", route: "/maps" },
    { id: "options", label: "Open in Options", route: "/options" },
    { id: "companies", label: "Open in Companies", route: "/companies" },
    { id: "markets", label: "Open in Markets", route: "/markets" },
    { id: "intelligence", label: "Open in Intelligence", route: "/intelligence" },
  ] as const;

  return entityModules.map((m) => ({
    id: `navigation.${m.id}.entity`,
    label: m.label,
    description: `Select entity and navigate to ${m.id} workspace.`,
    category: "selection",
    keywords: [m.id, "open", "entity", "navigate"],
    availability: (context: CommandContext) => {
      if (context.canViewModule && !context.canViewModule(m.id)) {
        return "hidden";
      }
      return "available";
    },
    execute: (_context, helpers, args) => {
      const entityId = args?.entityId;
      if (typeof entityId === "string" && entityId) {
        helpers.selectEntity?.(entityId);
      }
      helpers.navigate(m.route);
    },
  }));
}

/**
 * Initial static command definitions for Stage 46 & Stage 47.
 */
const initialCommands: CommandDefinition[] = [
  ...createNavigationCommands(),
  ...createEntityNavigationCommands(),
  ...createShellCommands(),
];

// Validate registry integrity on module initialization
validateCommandRegistry(initialCommands);

export const COMMAND_REGISTRY: readonly CommandDefinition[] = Object.freeze(initialCommands);

/**
 * Retrieves all registered commands.
 */
export function getAllCommands(): readonly CommandDefinition[] {
  return COMMAND_REGISTRY;
}

/**
 * Looks up a single command by its stable ID.
 */
export function getCommandById(id: string): CommandDefinition | undefined {
  return COMMAND_REGISTRY.find((cmd) => cmd.id === id);
}
