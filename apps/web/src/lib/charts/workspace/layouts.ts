/**
 * Multi-Chart Layout Registry & Definitions for ATLAS Charts (Stage 72).
 *
 * Implements the 6 canonical financial analysis layouts:
 * - single: 1 full chart
 * - two-columns: 2 side-by-side charts
 * - two-rows: 2 vertically stacked charts
 * - three-left-focus: 1 primary chart on left, 2 stacked on right
 * - three-top-focus: 1 primary chart on top, 2 side-by-side on bottom
 * - four-grid: 2x2 grid of 4 charts
 */

import { ChartLayoutId, LayoutDefinition, WORKSPACE_RESOURCE_BUDGET } from "./types";

export const CHART_LAYOUTS: Record<ChartLayoutId, LayoutDefinition> = {
  single: {
    id: "single",
    label: "Single Chart",
    description: "One full workspace chart for focused technical analysis",
    panelCount: 1,
    icon: "single",
    minWidthPx: WORKSPACE_RESOURCE_BUDGET.minPanelWidthPx,
    minHeightPx: WORKSPACE_RESOURCE_BUDGET.minPanelHeightPx,
  },
  "two-columns": {
    id: "two-columns",
    label: "Two Columns",
    description: "Two side-by-side charts for pair or cross-asset comparison",
    panelCount: 2,
    icon: "two-columns",
    minWidthPx: WORKSPACE_RESOURCE_BUDGET.minPanelWidthPx * 2,
    minHeightPx: WORKSPACE_RESOURCE_BUDGET.minPanelHeightPx,
  },
  "two-rows": {
    id: "two-rows",
    label: "Two Rows",
    description: "Two vertically stacked charts for multi-timeframe analysis",
    panelCount: 2,
    icon: "two-rows",
    minWidthPx: WORKSPACE_RESOURCE_BUDGET.minPanelWidthPx,
    minHeightPx: WORKSPACE_RESOURCE_BUDGET.minPanelHeightPx * 2,
  },
  "three-left-focus": {
    id: "three-left-focus",
    label: "Three Charts (Left Focus)",
    description: "Large primary chart on left with two stacked charts on right",
    panelCount: 3,
    icon: "three-left-focus",
    minWidthPx: WORKSPACE_RESOURCE_BUDGET.minPanelWidthPx * 2,
    minHeightPx: WORKSPACE_RESOURCE_BUDGET.minPanelHeightPx * 2,
  },
  "three-top-focus": {
    id: "three-top-focus",
    label: "Three Charts (Top Focus)",
    description: "Large primary chart on top with two side-by-side charts below",
    panelCount: 3,
    icon: "three-top-focus",
    minWidthPx: WORKSPACE_RESOURCE_BUDGET.minPanelWidthPx * 2,
    minHeightPx: WORKSPACE_RESOURCE_BUDGET.minPanelHeightPx * 2,
  },
  "four-grid": {
    id: "four-grid",
    label: "Four Grid (2x2)",
    description: "Four-chart institutional grid for comprehensive multi-instrument coverage",
    panelCount: 4,
    icon: "four-grid",
    minWidthPx: WORKSPACE_RESOURCE_BUDGET.minPanelWidthPx * 2,
    minHeightPx: WORKSPACE_RESOURCE_BUDGET.minPanelHeightPx * 2,
  },
};

export const ORDERED_LAYOUT_IDS: ChartLayoutId[] = [
  "single",
  "two-columns",
  "two-rows",
  "three-left-focus",
  "three-top-focus",
  "four-grid",
];

export function getLayoutDefinition(id: ChartLayoutId): LayoutDefinition {
  return CHART_LAYOUTS[id] || CHART_LAYOUTS.single;
}

export function isValidLayoutId(id: string): id is ChartLayoutId {
  return id in CHART_LAYOUTS;
}

export function getRequiredPanelCount(id: ChartLayoutId): number {
  return getLayoutDefinition(id).panelCount;
}
