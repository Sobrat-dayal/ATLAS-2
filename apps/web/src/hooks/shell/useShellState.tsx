"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useAuth } from "@/hooks/auth/useAuth";

interface ShellState {
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  agentDockOpen: boolean;
  setAgentDockOpen: (open: boolean) => void;
  
  agentDockWidth: number;
  setAgentDockWidth: (width: number) => void;
  
  activeBottomPanel: string | null;
  setActiveBottomPanel: (panel: string | null) => void;
  
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
  moduleFullscreen: false,
  setModuleFullscreen: () => {},
};

const ShellContext = createContext<ShellState>(defaultState);

export function ShellProvider({ children }: { children: ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [agentDockOpen, setAgentDockOpen] = useState(false);
  const [agentDockWidth, setAgentDockWidth] = useState(320);
  const [activeBottomPanel, setActiveBottomPanel] = useState<string | null>(null);
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
        if (typeof parsed.sidebarCollapsed === "boolean") setSidebarCollapsed(parsed.sidebarCollapsed);
        if (typeof parsed.agentDockOpen === "boolean") setAgentDockOpen(parsed.agentDockOpen);
        if (typeof parsed.agentDockWidth === "number") setAgentDockWidth(parsed.agentDockWidth);
        if (typeof parsed.activeBottomPanel !== "undefined") setActiveBottomPanel(parsed.activeBottomPanel);
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
        })
      );
    } catch {
      console.warn("Failed to save shell state to localStorage");
    }
  }, [sidebarCollapsed, agentDockOpen, agentDockWidth, activeBottomPanel, storageKey]);


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
