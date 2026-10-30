import { CheckSquare, Bot, Layers, BellRing, Download, Activity, Terminal } from "lucide-react";
import { BottomPanelDefinition, BottomPanelId } from "./types";
import {
  TasksPanel,
  AgentsPanel,
  JobsPanel,
  AlertsPanel,
  DownloadsPanel,
  SystemHealthPanel,
  TerminalPanel,
} from "@/components/bottom-taskbar/panels";

/**
 * Canonical 7 Bottom Taskbar panels in strict roadmap order:
 * 1. Tasks
 * 2. Agents
 * 3. Jobs
 * 4. Alerts
 * 5. Downloads
 * 6. System Health
 * 7. Terminal (Trailing)
 */
export const PANEL_DEFINITIONS: readonly BottomPanelDefinition[] = Object.freeze([
  {
    id: "tasks",
    label: "Tasks",
    description: "Task management and operational status",
    icon: CheckSquare,
    placement: "primary",
    availability: "reserved",
    component: TasksPanel,
  },
  {
    id: "agents",
    label: "Agents",
    description: "Agent execution details and team status",
    icon: Bot,
    placement: "primary",
    availability: "reserved",
    component: AgentsPanel,
  },
  {
    id: "jobs",
    label: "Jobs",
    description: "Background jobs and worker processing",
    icon: Layers,
    placement: "primary",
    availability: "reserved",
    component: JobsPanel,
  },
  {
    id: "alerts",
    label: "Alerts",
    description: "Alert monitoring and condition rules",
    icon: BellRing,
    placement: "primary",
    availability: "reserved",
    component: AlertsPanel,
  },
  {
    id: "downloads",
    label: "Downloads",
    description: "Generated reports and download tracking",
    icon: Download,
    placement: "primary",
    availability: "reserved",
    component: DownloadsPanel,
  },
  {
    id: "system-health",
    label: "System Health",
    description: "Infrastructure and service connectivity",
    icon: Activity,
    placement: "primary",
    availability: "reserved",
    component: SystemHealthPanel,
  },
  {
    id: "terminal",
    label: "Terminal",
    description: "Integrated developer terminal shell (Stage 122)",
    icon: Terminal,
    placement: "trailing",
    availability: "available",
    component: TerminalPanel,
  },
]);

/**
 * Validates the static panel registry meets architectural invariants.
 */
export function validatePanelRegistry(panels: readonly BottomPanelDefinition[] = PANEL_DEFINITIONS): void {
  if (panels.length !== 7) {
    throw new Error(`Expected exactly 7 bottom panels, found ${panels.length}`);
  }

  const seenIds = new Set<string>();
  const canonicalOrder: BottomPanelId[] = [
    "tasks",
    "agents",
    "jobs",
    "alerts",
    "downloads",
    "system-health",
    "terminal",
  ];

  for (let i = 0; i < panels.length; i++) {
    const panel = panels[i];
    if (seenIds.has(panel.id)) {
      throw new Error(`Duplicate bottom panel id found: ${panel.id}`);
    }
    seenIds.add(panel.id);

    if (panel.id !== canonicalOrder[i]) {
      throw new Error(`Invalid panel order at position ${i}: expected ${canonicalOrder[i]}, got ${panel.id}`);
    }

    if (!panel.label || panel.label.trim() === "") {
      throw new Error(`Bottom panel ${panel.id} must have a non-empty label`);
    }

    if (typeof panel.component !== "function") {
      throw new Error(`Bottom panel ${panel.id} has invalid component renderer`);
    }

    if (panel.id === "terminal") {
      if (panel.placement !== "trailing") {
        throw new Error("Terminal panel must have placement='trailing'");
      }
    } else {
      if (panel.placement !== "primary") {
        throw new Error(`Panel ${panel.id} must have placement='primary'`);
      }
    }
  }
}

// Run validation at module load time
validatePanelRegistry(PANEL_DEFINITIONS);

export function getAllPanelDefinitions(): readonly BottomPanelDefinition[] {
  return PANEL_DEFINITIONS;
}

export function getPrimaryPanelDefinitions(): readonly BottomPanelDefinition[] {
  return PANEL_DEFINITIONS.filter((p) => p.placement === "primary");
}

export function getTrailingPanelDefinitions(): readonly BottomPanelDefinition[] {
  return PANEL_DEFINITIONS.filter((p) => p.placement === "trailing");
}

export function getPanelDefinition(id: BottomPanelId): BottomPanelDefinition | undefined {
  return PANEL_DEFINITIONS.find((p) => p.id === id);
}
