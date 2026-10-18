/**
 * Multi-Chart Workspace Domain Types for ATLAS Charts (Stage 72).
 *
 * Implements:
 * - 6 canonical financial chart layout presets:
 *   - single: 1 full workspace chart
 *   - two-columns: 2 side-by-side charts
 *   - two-rows: 2 vertically stacked charts
 *   - three-left-focus: 1 large chart left, 2 stacked on right
 *   - three-top-focus: 1 large chart top, 2 side-by-side below
 *   - four-grid: 2x2 grid of 4 charts
 * - Stable chart panel state and lifecycle tracking
 * - Explicit active panel management
 * - Strict panel independence (instruments, intervals, chart types, indicators, drawings)
 * - Shared data caching and live subscription reference counting contracts
 * - Resource budgeting and responsive presentation modes
 */

import { ChartInstrumentMetadata, ChartRenderMode } from "../types";

export type ChartLayoutId =
  | "single"
  | "two-columns"
  | "two-rows"
  | "three-left-focus"
  | "three-top-focus"
  | "four-grid";

export type ChartPanelLifecycleStatus =
  | "CREATED"
  | "INITIALIZING"
  | "READY"
  | "SUSPENDED"
  | "ERROR"
  | "DISPOSING"
  | "DISPOSED";

export interface ChartPanelState {
  panelId: string;
  symbol: string;
  instrument: ChartInstrumentMetadata | null;
  interval: string;
  renderMode: ChartRenderMode;
  isActive: boolean;
  lifecycleStatus: ChartPanelLifecycleStatus;
  isLivePaused: boolean;
  isFollowingLatest: boolean;
  error?: string | null;
}

export interface LayoutDefinition {
  id: ChartLayoutId;
  label: string;
  description: string;
  panelCount: number;
  icon: string;
  minWidthPx: number;
  minHeightPx: number;
}

export interface SplitRatios {
  primary?: number; // Normalized split ratio (0.1 to 0.9, default ~0.5)
  secondary?: number; // Nested split ratio
}

export interface MultiChartWorkspaceState {
  layoutId: ChartLayoutId;
  panelIds: string[];
  activePanelId: string;
  splitRatios: Record<string, number>;
  panels: Record<string, ChartPanelState>;
  isMobileTabMode: boolean;
  activeMobileTabId: string;
}

export interface ResourceBudgetConfig {
  maxVisiblePanels: number;
  maxMountedRenderers: number;
  minPanelWidthPx: number;
  minPanelHeightPx: number;
  maxDrawingsPerPanel: number;
  maxIndicatorsPerPanel: number;
  maxLiveSubscriptions: number;
  queryCacheCapacity: number;
}

export const WORKSPACE_RESOURCE_BUDGET: ResourceBudgetConfig = {
  maxVisiblePanels: 4,
  maxMountedRenderers: 4,
  minPanelWidthPx: 320,
  minPanelHeightPx: 220,
  maxDrawingsPerPanel: 250,
  maxIndicatorsPerPanel: 12,
  maxLiveSubscriptions: 10,
  queryCacheCapacity: 50,
};
