"use client";

import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from "react";
import { useAuth } from "@/hooks/auth/useAuth";
import {
  BottomPanelId,
  DEFAULT_BOTTOM_PANEL_HEIGHT,
  clampBottomPanelHeight,
} from "@/lib/bottom-taskbar";

interface ShellState {
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  agentDockOpen: boolean;
  setAgentDockOpen: (open: boolean) => void;
  
  agentDockWidth: number;
  setAgentDockWidth: (width: number) => void;
  
  activeBottomPanel: BottomPanelId | null;
  setActiveBottomPanel: (panel: BottomPanelId | null) => void;
  bottomPanelHeight: number;
  setBottomPanelHeight: (height: number) => void;
  toggleBottomPanel: (panel: BottomPanelId) => void;
  openBottomPanel: (panel: BottomPanelId) => void;
  closeBottomPanel: () => void;
  
  moduleFullscreen: boolean;
  setModuleFullscreen: (fullscreen: boolean) => void;
}

const defaultState: ShellState = {
  sidebarCollapsed: false,
  setSidebarCollapsed: () => {},
  agentDockOpen: false,
  setAgentDockOpen: () => {},
  agentDockWidth: 320,
  setAgentDockWidth: () => {},
  activeBottomPanel: null,
  setActiveBottomPanel: () => {},
  bottomPanelHeight: DEFAULT_BOTTOM_PANEL_HEIGHT,
  setBottomPanelHeight: () => {},
  toggleBottomPanel: () => {},
  openBottomPanel: () => {},
  closeBottomPanel: () => {},
  moduleFullscreen: false,
  setModuleFullscreen: () => {},
};

const ShellContext = createContext<ShellState>(defaultState);

export function ShellProvider({ children }: { children: ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [agentDockOpen, setAgentDockOpen] = useState(false);
  const [agentDockWidth, setAgentDockWidth] = useState(320);
  const [activeBottomPanel, setActiveBottomPanel] = useState<BottomPanelId | null>(null);
  const [bottomPanelHeight, setBottomPanelHeightState] = useState(DEFAULT_BOTTOM_PANEL_HEIGHT);
  const [moduleFullscreen, setModuleFullscreen] = useState(false);

  const { session } = useAuth();
  const userId = session?.user?.id;
  const storageKey = userId ? `atlas.user.${userId}.shell-state` : "atlas-shell-state";

  // Hydrate from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem(storageKey) || (!userId ? null : localStorage.getItem("atlas-shell-state"));
      if (saved) {
        const parsed = JSON.parse(saved);
        // eslint-disable-next-line react-hooks/set-state-in-effect
        if (typeof parsed.sidebarCollapsed === "boolean") setSidebarCollapsed(parsed.sidebarCollapsed);
        if (typeof parsed.agentDockOpen === "boolean") setAgentDockOpen(parsed.agentDockOpen);
        if (typeof parsed.agentDockWidth === "number") setAgentDockWidth(parsed.agentDockWidth);
        if (typeof parsed.activeBottomPanel !== "undefined") setActiveBottomPanel(parsed.activeBottomPanel);
        if (typeof parsed.bottomPanelHeight === "number") {
          setBottomPanelHeightState(clampBottomPanelHeight(parsed.bottomPanelHeight));
        }
      }
    } catch {
      console.warn("Failed to parse shell state from localStorage");
    }
  }, [storageKey, userId]);

  // Save to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(
        storageKey,
        JSON.stringify({
          sidebarCollapsed,
          agentDockOpen,
          agentDockWidth,
          activeBottomPanel,
          bottomPanelHeight,
        })
      );
    } catch {
      console.warn("Failed to save shell state to localStorage");
    }
  }, [sidebarCollapsed, agentDockOpen, agentDockWidth, activeBottomPanel, bottomPanelHeight, storageKey]);

  const toggleBottomPanel = useCallback((panelId: BottomPanelId) => {
    setActiveBottomPanel((prev) => (prev === panelId ? null : panelId));
  }, []);

  const openBottomPanel = useCallback((panelId: BottomPanelId) => {
    setActiveBottomPanel(panelId);
  }, []);

  const closeBottomPanel = useCallback(() => {
    setActiveBottomPanel(null);
  }, []);

  const setBottomPanelHeight = useCallback((height: number) => {
    setBottomPanelHeightState(clampBottomPanelHeight(height));
  }, []);

  return (
    <ShellContext.Provider
      value={{
        sidebarCollapsed,
        setSidebarCollapsed,
        agentDockOpen,
        setAgentDockOpen,
        agentDockWidth,
        setAgentDockWidth,
        activeBottomPanel,
        setActiveBottomPanel,
        bottomPanelHeight,
        setBottomPanelHeight,
        toggleBottomPanel,
        openBottomPanel,
        closeBottomPanel,
        moduleFullscreen,
        setModuleFullscreen,
      }}
    >
      {children}
    </ShellContext.Provider>
  );
}

export function useShellState() {
  return useContext(ShellContext);
}
