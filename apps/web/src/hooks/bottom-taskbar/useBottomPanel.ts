"use client";

import { useShellState } from "@/hooks/shell/useShellState";
import { BottomPanelController } from "@/lib/bottom-taskbar";

/**
 * Hook to access and control the Bottom Workspace Panel.
 * Provides typed state, open/close/toggle actions, and height controls.
 */
export function useBottomPanel(): BottomPanelController {
  const {
    activeBottomPanel,
    bottomPanelHeight,
    openBottomPanel,
    closeBottomPanel,
    toggleBottomPanel,
    setBottomPanelHeight,
  } = useShellState();

  return {
    activePanelId: activeBottomPanel,
    isOpen: activeBottomPanel !== null,
    panelHeight: bottomPanelHeight,
    openPanel: openBottomPanel,
    closePanel: closeBottomPanel,
    togglePanel: toggleBottomPanel,
    setPanelHeight: setBottomPanelHeight,
  };
}
