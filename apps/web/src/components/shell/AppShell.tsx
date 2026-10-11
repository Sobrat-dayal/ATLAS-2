"use client";

import { useShellState } from "@/hooks/shell/useShellState";
import { AtlasBackgroundLayer } from "./AtlasBackgroundLayer";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { MainWorkspace } from "./MainWorkspace";
import { AgentDock } from "./AgentDock";
import { BottomTaskbar, BottomPanelHost } from "@/components/bottom-taskbar";
import { MarketTickerBar } from "./MarketTickerBar";
import { SectionSettingsDrawer } from "@/components/settings/SectionSettingsDrawer";
import { CommandPalette } from "@/components/command-palette";
import { useCommandPaletteShortcut } from "@/hooks/commands";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { moduleFullscreen } = useShellState();
  useCommandPaletteShortcut();

  if (moduleFullscreen) {
    return (
      <div className="flex h-[100dvh] w-full flex-col overflow-hidden bg-atlas-bg-0 text-atlas-text-primary relative z-0">
        <AtlasBackgroundLayer />
        <MainWorkspace>
          {children}
        </MainWorkspace>
        <CommandPalette />
      </div>
    );
  }

  return (
    <div className="flex h-[100dvh] w-full flex-col overflow-hidden bg-atlas-bg-0 text-atlas-text-primary relative z-0">
      <AtlasBackgroundLayer />
      {/* Persistent Top Layer */}
      <TopBar />
      <MarketTickerBar />

      {/* Middle Layer (Sidebar + Workspace Column + Agent Dock) */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        
        <div className="flex flex-1 flex-col overflow-hidden relative min-w-0 min-h-0">
          <MainWorkspace>
            {children}
          </MainWorkspace>
          <BottomPanelHost />
        </div>
        
        <AgentDock />
      </div>

      {/* Bottom Layer */}
      <BottomTaskbar />
      
      {/* Overlays */}
      <SectionSettingsDrawer />
      <CommandPalette />
    </div>
  );
}
