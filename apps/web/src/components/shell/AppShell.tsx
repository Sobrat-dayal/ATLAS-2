"use client";

import { useShellState } from "@/hooks/shell/useShellState";
import { AtlasBackgroundLayer } from "./AtlasBackgroundLayer";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { MainWorkspace } from "./MainWorkspace";
import { AgentDock } from "./AgentDock";
import { BottomTaskbar } from "./BottomTaskbar";
import { MarketTickerBar } from "./MarketTickerBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { moduleFullscreen } = useShellState();

  if (moduleFullscreen) {
    return (
      <div className="flex h-[100dvh] w-full flex-col overflow-hidden bg-atlas-bg-0 text-atlas-text-primary relative z-0">
        <AtlasBackgroundLayer />
        <MainWorkspace>
          {children}
        </MainWorkspace>
      </div>
    );
  }

  return (
    <div className="flex h-[100dvh] w-full flex-col overflow-hidden bg-atlas-bg-0 text-atlas-text-primary relative z-0">
      <AtlasBackgroundLayer />
      {/* Persistent Top Layer */}
      <TopBar />
      <MarketTickerBar />

      {/* Middle Layer (Sidebar + Main + Agent Dock) */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        
        <MainWorkspace>
          {children}
        </MainWorkspace>
        
        <AgentDock />
      </div>

      {/* Bottom Layer */}
      <BottomTaskbar />
    </div>
  );
}
