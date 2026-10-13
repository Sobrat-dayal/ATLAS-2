import { ATLAS_MODULES, ATLAS_MODULES_LIST, AtlasModuleId } from "@/config/atlas-modules";
import { QuickLaunchItem } from "./types";

/**
 * Curated primary module IDs for the Home command center Quick Launch.
 * Prioritizes core analytical, intelligence, and execution workspaces.
 */
export const PRIMARY_QUICK_LAUNCH_IDS: readonly AtlasModuleId[] = Object.freeze([
  "markets",
  "charts",
  "companies",
  "economics",
  "research",
  "maps",
  "intelligence",
  "portfolios",
  "ai",
  "agents",
]);

/**
 * Derives Quick Launch items directly from the Stage 4 canonical module registry.
 */
export function getAllQuickLaunchItems(): QuickLaunchItem[] {
  return ATLAS_MODULES_LIST.map((mod) => ({
    id: mod.id,
    label: mod.label,
    route: mod.route,
    icon: mod.icon,
    description: mod.description,
    order: mod.order,
    isPrimary: PRIMARY_QUICK_LAUNCH_IDS.includes(mod.id),
    requiredPermission: mod.requiredPermission,
  }));
}

export function getCuratedQuickLaunchItems(): QuickLaunchItem[] {
  return PRIMARY_QUICK_LAUNCH_IDS.map((id) => {
    const mod = ATLAS_MODULES[id];
    return {
      id: mod.id,
      label: mod.label,
      route: mod.route,
      icon: mod.icon,
      description: mod.description,
      order: mod.order,
      isPrimary: true,
      requiredPermission: mod.requiredPermission,
    };
  });
}
