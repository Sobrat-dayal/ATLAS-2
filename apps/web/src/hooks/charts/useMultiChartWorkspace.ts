"use client";

/**
 * React hook connecting UI components to MultiChartWorkspaceStore (Stage 72).
 *
 * Provides reactive workspace state:
 * - Active layout ID and switching
 * - Active panel identification and switching
 * - Panel state management and scoped mutations
 * - Split ratios and responsive mobile tab state
 */

import { useCallback, useEffect, useState } from "react";
import {
  ChartLayoutId,
  ChartPanelState,
  ChartRenderMode,
  MultiChartWorkspaceState,
  workspaceStore,
} from "@/lib/charts";

export function useMultiChartWorkspace() {
  const [state, setState] = useState<MultiChartWorkspaceState>(() => workspaceStore.getState());

  useEffect(() => {
    const unsubscribe = workspaceStore.subscribe((newState) => {
      setState(newState);
    });
    return () => {
      unsubscribe();
    };
  }, []);

  const setLayoutId = useCallback((layoutId: ChartLayoutId) => {
    workspaceStore.setLayout(layoutId);
  }, []);

  const setActivePanelId = useCallback((panelId: string) => {
    workspaceStore.setActivePanel(panelId);
  }, []);

  const updatePanel = useCallback((panelId: string, updates: Partial<ChartPanelState>) => {
    workspaceStore.updatePanel(panelId, updates);
  }, []);

  const setSplitRatios = useCallback((ratios: Record<string, number>) => {
    workspaceStore.setSplitRatios(ratios);
  }, []);

  const setMobileTabMode = useCallback((isMobile: boolean) => {
    workspaceStore.setMobileTabMode(isMobile);
  }, []);

  const setActiveMobileTab = useCallback((panelId: string) => {
    workspaceStore.setActiveMobileTab(panelId);
  }, []);

  const selectInstrumentForActivePanel = useCallback(
    (symbol: string) => {
      if (state.activePanelId) {
        workspaceStore.updatePanel(state.activePanelId, { symbol });
      }
    },
    [state.activePanelId]
  );

  const setIntervalForActivePanel = useCallback(
    (interval: string) => {
      if (state.activePanelId) {
        workspaceStore.updatePanel(state.activePanelId, { interval });
      }
    },
    [state.activePanelId]
  );

  const setRenderModeForActivePanel = useCallback(
    (renderMode: ChartRenderMode) => {
      if (state.activePanelId) {
        workspaceStore.updatePanel(state.activePanelId, { renderMode });
      }
    },
    [state.activePanelId]
  );

  const activePanel = state.panels[state.activePanelId] || state.panels["panel-1"] || null;

  return {
    layoutId: state.layoutId,
    panelIds: state.panelIds,
    activePanelId: state.activePanelId,
    activePanel,
    panels: state.panels,
    splitRatios: state.splitRatios,
    isMobileTabMode: state.isMobileTabMode,
    activeMobileTabId: state.activeMobileTabId,
    setLayoutId,
    setActivePanelId,
    updatePanel,
    setSplitRatios,
    setMobileTabMode,
    setActiveMobileTab,
    selectInstrumentForActivePanel,
    setIntervalForActivePanel,
    setRenderModeForActivePanel,
  };
}
