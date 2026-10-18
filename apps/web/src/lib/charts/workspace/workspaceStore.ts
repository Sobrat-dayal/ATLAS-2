/**
 * Multi-Chart Workspace Session Store for ATLAS Charts (Stage 72).
 *
 * Implements:
 * - Session-level in-memory state management for multi-chart layouts
 * - Stable panel identities (panel-1 through panel-4)
 * - Explicit active panel management (activePanelId)
 * - Safe layout expansion and reduction with session configuration retention
 * - Reactive subscription mechanism for UI components
 * - Zero database writes or cloud persistence (deferred to Stage 74)
 */

import {
  ChartLayoutId,
  ChartPanelState,
  MultiChartWorkspaceState,
  WORKSPACE_RESOURCE_BUDGET,
} from "./types";
import { getRequiredPanelCount } from "./layouts";

const DEFAULT_INSTRUMENTS = ["SPY", "BTCUSDT", "EURUSD", "AAPL"];

export type WorkspaceListener = (state: MultiChartWorkspaceState) => void;

export class MultiChartWorkspaceStore {
  private static instance: MultiChartWorkspaceStore;

  private state: MultiChartWorkspaceState;
  private listeners: Set<WorkspaceListener> = new Set();

  constructor() {
    const initialPanelId = "panel-1";
    const initialPanels: Record<string, ChartPanelState> = {
      [initialPanelId]: {
        panelId: initialPanelId,
        symbol: "SPY",
        instrument: null,
        interval: "1d",
        renderMode: "candlestick",
        isActive: true,
        lifecycleStatus: "READY",
        isLivePaused: false,
        isFollowingLatest: true,
      },
    };

    this.state = {
      layoutId: "single",
      panelIds: [initialPanelId],
      activePanelId: initialPanelId,
      splitRatios: {
        primary: 0.5,
        secondary: 0.5,
      },
      panels: initialPanels,
      isMobileTabMode: false,
      activeMobileTabId: initialPanelId,
    };
  }

  public static getInstance(): MultiChartWorkspaceStore {
    if (!MultiChartWorkspaceStore.instance) {
      MultiChartWorkspaceStore.instance = new MultiChartWorkspaceStore();
    }
    return MultiChartWorkspaceStore.instance;
  }

  public getState(): MultiChartWorkspaceState {
    return { ...this.state };
  }

  /**
   * Switches the active layout preset, allocating new panels or suspending unused panels
   * while preserving existing panel configurations and session drawing/indicator state.
   */
  public setLayout(layoutId: ChartLayoutId): void {
    const requiredCount = Math.min(
      getRequiredPanelCount(layoutId),
      WORKSPACE_RESOURCE_BUDGET.maxVisiblePanels
    );

    const currentPanelIds = [...this.state.panelIds];
    const newPanels = { ...this.state.panels };

    // Allocate additional panels if needed
    while (currentPanelIds.length < requiredCount) {
      const nextIndex = currentPanelIds.length + 1;
      const nextId = `panel-${nextIndex}`;
      const defaultSymbol = DEFAULT_INSTRUMENTS[nextIndex - 1] || "SPY";

      // If panel was previously created in this session, restore it; otherwise create fresh
      if (!newPanels[nextId]) {
        newPanels[nextId] = {
          panelId: nextId,
          symbol: defaultSymbol,
          instrument: null,
          interval: "1d",
          renderMode: "candlestick",
          isActive: false,
          lifecycleStatus: "READY",
          isLivePaused: false,
          isFollowingLatest: true,
        };
      } else {
        newPanels[nextId].lifecycleStatus = "READY";
      }

      currentPanelIds.push(nextId);
    }

    // If reducing panel count, truncate visible panelIds and mark extra panels as SUSPENDED
    const visiblePanelIds = currentPanelIds.slice(0, requiredCount);
    for (let i = requiredCount; i < currentPanelIds.length; i++) {
      const suspendedId = currentPanelIds[i];
      if (newPanels[suspendedId]) {
        newPanels[suspendedId].lifecycleStatus = "SUSPENDED";
      }
    }

    // Ensure activePanelId is within visible panels
    let activeId = this.state.activePanelId;
    if (!visiblePanelIds.includes(activeId)) {
      activeId = visiblePanelIds[0] || "panel-1";
    }

    // Update isActive flag across panels
    Object.keys(newPanels).forEach((id) => {
      newPanels[id].isActive = id === activeId;
    });

    this.state = {
      ...this.state,
      layoutId,
      panelIds: visiblePanelIds,
      activePanelId: activeId,
      panels: newPanels,
      activeMobileTabId: activeId,
    };

    this.notify();
  }

  /**
   * Designates a panel as active for receiving toolbar inputs, global search, and keyboard focus.
   */
  public setActivePanel(panelId: string): void {
    if (!this.state.panels[panelId]) return;

    const newPanels = { ...this.state.panels };
    Object.keys(newPanels).forEach((id) => {
      newPanels[id] = {
        ...newPanels[id],
        isActive: id === panelId,
      };
    });

    this.state = {
      ...this.state,
      activePanelId: panelId,
      activeMobileTabId: panelId,
      panels: newPanels,
    };

    this.notify();
  }

  /**
   * Updates state for a specific chart panel without mutating other panels.
   */
  public updatePanel(panelId: string, updates: Partial<ChartPanelState>): void {
    const existing = this.state.panels[panelId];
    if (!existing) return;

    let hasChanges = false;
    for (const [key, val] of Object.entries(updates)) {
      if ((existing as any)[key] !== val) {
        hasChanges = true;
        break;
      }
    }
    if (!hasChanges) return;

    this.state = {
      ...this.state,
      panels: {
        ...this.state.panels,
        [panelId]: {
          ...existing,
          ...updates,
        },
      },
    };

    this.notify();
  }

  /**
   * Updates split ratios when splitters are dragged or resized.
   */
  public setSplitRatios(ratios: Record<string, number>): void {
    this.state = {
      ...this.state,
      splitRatios: {
        ...this.state.splitRatios,
        ...ratios,
      },
    };
    this.notify();
  }

  /**
   * Sets mobile tab view mode.
   */
  public setMobileTabMode(isMobile: boolean): void {
    if (this.state.isMobileTabMode !== isMobile) {
      this.state = {
        ...this.state,
        isMobileTabMode: isMobile,
      };
      this.notify();
    }
  }

  public setActiveMobileTab(panelId: string): void {
    this.setActivePanel(panelId);
  }

  public subscribe(listener: WorkspaceListener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify(): void {
    const state = this.getState();
    this.listeners.forEach((listener) => {
      try {
        listener(state);
      } catch (err) {
        console.error("Error in workspace store listener:", err);
      }
    });
  }

  /**
   * Atomically loads a validated workspace state from a saved chart layout.
   */
  public loadWorkspaceState(newState: MultiChartWorkspaceState): void {
    this.state = {
      layoutId: newState.layoutId,
      panelIds: [...newState.panelIds],
      activePanelId: newState.activePanelId,
      splitRatios: { ...(newState.splitRatios || {}) },
      panels: { ...newState.panels },
      isMobileTabMode: newState.isMobileTabMode ?? false,
      activeMobileTabId: newState.activeMobileTabId || newState.activePanelId,
    };
    this.notify();
  }

  public reset(): void {
    this.state.panelIds = ["panel-1"];
    this.state.layoutId = "single";
    this.state.activePanelId = "panel-1";
    this.notify();
  }
}

export const workspaceStore = MultiChartWorkspaceStore.getInstance();
