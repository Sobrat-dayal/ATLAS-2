import { HomeWidgetDefinition, HomeWidgetId } from "./types";

/**
 * Authoritative Static Widget Registry for ATLAS Home.
 * Distinguishes implemented V1 widgets from reserved future stage contracts.
 */
export const HOME_WIDGET_DEFINITIONS: readonly HomeWidgetDefinition[] = Object.freeze([
  {
    id: "current-context",
    title: "Current Focus",
    subtitle: "Selected Universal Entity",
    description: "Real-time inspection and context summary of the currently selected Universal Entity.",
    targetStage: 51,
    status: "implemented",
    defaultState: "available",
    placement: "primary",
    minimumWidth: 320,
  },
  {
    id: "quick-launch",
    title: "Quick Launch",
    subtitle: "Core Workspaces",
    description: "Operational navigation to canonical ATLAS modules and workspaces.",
    targetStage: 51,
    status: "implemented",
    defaultState: "available",
    placement: "secondary",
    minimumWidth: 320,
  },
  {
    id: "home-market-summary",
    title: "Market Summary",
    subtitle: "Indices & Asset Classes",
    description: "Global multi-asset indices, benchmark ETFs, FX, crypto, and commodity observations.",
    targetStage: 52,
    status: "implemented",
    defaultState: "available",
    placement: "primary",
    minimumWidth: 320,
  },
  {
    id: "home-personalized-activity",
    title: "Recent Activity",
    subtitle: "User History & Recent Entities",
    description: "Personalized entity view history, recent module visits, and user workflows.",
    targetStage: 53,
    status: "reserved",
    defaultState: "reserved",
    placement: "tertiary",
    minimumWidth: 300,
  },
  {
    id: "home-tasks-approvals",
    title: "Tasks & Approvals",
    subtitle: "Workflow Action Queue",
    description: "Pending workflow tasks, execution approvals, and background job actions.",
    targetStage: 54,
    status: "reserved",
    defaultState: "reserved",
    placement: "tertiary",
    minimumWidth: 300,
  },
  {
    id: "home-intelligence-feed",
    title: "Intelligence Feed",
    subtitle: "Signals & Anomalies",
    description: "Prioritized intelligence signals, cross-domain anomalies, and narrative tracking.",
    targetStage: 55,
    status: "reserved",
    defaultState: "reserved",
    placement: "full",
    minimumWidth: 320,
  },
  {
    id: "home-portfolio-summary",
    title: "Portfolio Summary",
    subtitle: "Allocations & Performance",
    description: "Portfolio valuation, risk metrics, and position allocations.",
    targetStage: 110,
    status: "planned",
    defaultState: "reserved",
    placement: "tertiary",
    minimumWidth: 320,
  },
  {
    id: "home-news-preview",
    title: "News Preview",
    subtitle: "Realtime Headlines",
    description: "Financial news coverage and corporate intelligence alerts.",
    targetStage: 99,
    status: "planned",
    defaultState: "reserved",
    placement: "tertiary",
    minimumWidth: 300,
  },
  {
    id: "home-economics-preview",
    title: "Macroeconomic Calendar",
    subtitle: "Indicators & Central Banks",
    description: "Global economic indicator releases and central bank schedules.",
    targetStage: 89,
    status: "planned",
    defaultState: "reserved",
    placement: "tertiary",
    minimumWidth: 300,
  },
  {
    id: "home-map-preview",
    title: "Geospatial Preview",
    subtitle: "God's Eye Intelligence",
    description: "Global logistics, supply chain hubs, and geopolitical spatial tracking.",
    targetStage: 129,
    status: "planned",
    defaultState: "reserved",
    placement: "full",
    minimumWidth: 320,
  },
  {
    id: "home-agent-activity",
    title: "Agent Operations",
    subtitle: "Autonomous Agent Runs",
    description: "Agent execution history, active goals, and automation runs.",
    targetStage: 146,
    status: "planned",
    defaultState: "reserved",
    placement: "tertiary",
    minimumWidth: 300,
  },
]);

export function getAllWidgetDefinitions(): readonly HomeWidgetDefinition[] {
  return HOME_WIDGET_DEFINITIONS;
}

export function getWidgetDefinition(id: HomeWidgetId): HomeWidgetDefinition | undefined {
  return HOME_WIDGET_DEFINITIONS.find((w) => w.id === id);
}

export function getImplementedWidgetDefinitions(): HomeWidgetDefinition[] {
  return HOME_WIDGET_DEFINITIONS.filter((w) => w.status === "implemented");
}

export function getReservedWidgetDefinitions(): HomeWidgetDefinition[] {
  return HOME_WIDGET_DEFINITIONS.filter((w) => w.status === "reserved");
}
