"use client";

/**
 * Master Multi-Chart Workspace Container Component (Stage 72).
 *
 * Implements:
 * - 6 canonical financial layouts with resizable splitters:
 *   - single: 1 full workspace chart
 *   - two-columns: Horizontal split with 2 panels
 *   - two-rows: Vertical split with 2 panels
 *   - three-left-focus: Horizontal split (Left large panel + Right vertical split)
 *   - three-top-focus: Vertical split (Top large panel + Bottom horizontal split)
 *   - four-grid: 2x2 grid (Vertical split containing two horizontal splits)
 * - Minimum size constraints and keyboard-accessible resizing
 * - Mobile responsive tab fallback (<768px) preserving underlying workspace state
 * - Strict panel independence and stable component keys
 */

import React, { useEffect, useState } from "react";
import {
  AtlasPanel,
  AtlasResizeHandle,
  AtlasSplit,
} from "@/design-system/layout";
import { ChartLayoutId, ChartPanelState } from "@/lib/charts/workspace";
import { ChartPanel } from "./ChartPanel";
import { ChartPanelTabs } from "./ChartPanelTabs";

export interface MultiChartWorkspaceProps {
  layoutId: ChartLayoutId;
  panelIds: string[];
  activePanelId: string;
  panels: Record<string, ChartPanelState>;
  onActivatePanel: (panelId: string) => void;
  onUpdatePanelState?: (panelId: string, updates: Partial<ChartPanelState>) => void;
  className?: string;
}

export function MultiChartWorkspace({
  layoutId,
  panelIds,
  activePanelId,
  panels,
  onActivatePanel,
  onUpdatePanelState,
  className = "",
}: MultiChartWorkspaceProps) {
  // Responsive mobile tab detection
  const [isMobile, setIsMobile] = useState<boolean>(false);

  useEffect(() => {
    function handleResize() {
      setIsMobile(window.innerWidth < 768);
    }
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const renderPanel = (panelId: string, index: number) => {
    const state = panels[panelId];
    return (
      <ChartPanel
        key={panelId}
        panelId={panelId}
        panelIndex={index}
        initialSymbol={state?.symbol || "SPY"}
        initialInterval={state?.interval || "1d"}
        initialRenderMode={state?.renderMode || "candlestick"}
        isActive={panelId === activePanelId}
        onActivate={() => onActivatePanel(panelId)}
        onUpdateState={(updates) => {
          if (onUpdatePanelState) {
            onUpdatePanelState(panelId, updates);
          }
        }}
      />
    );
  };

  // If on mobile or narrow viewport (<768px), display responsive single-active-chart tab view
  if (isMobile && panelIds.length > 1) {
    const activeIndex = panelIds.indexOf(activePanelId);
    const safeIndex = activeIndex >= 0 ? activeIndex : 0;
    const currentId = panelIds[safeIndex] || panelIds[0];

    return (
      <div className={`w-full flex flex-col h-[650px] min-h-[500px] border border-zinc-800 rounded overflow-hidden ${className}`}>
        <ChartPanelTabs
          panelIds={panelIds}
          panels={panels}
          activeTabId={currentId}
          onSelectTab={onActivatePanel}
        />
        <div className="flex-1 w-full h-full p-0.5">
          {renderPanel(currentId, safeIndex)}
        </div>
      </div>
    );
  }

  // Dynamic Workspace Height calculation:
  // Single/Two-Cols: ~620px
  // Rows/Grid/Focus: ~850px to ensure each chart has comfortable >=350px height
  const containerHeightClass =
    layoutId === "single" || layoutId === "two-columns"
      ? "h-[620px] min-h-[500px]"
      : "h-[860px] min-h-[700px]";

  // 1. Single Chart Layout
  if (layoutId === "single" || panelIds.length === 1) {
    return (
      <div className={`w-full ${containerHeightClass} border border-zinc-800/80 rounded overflow-hidden ${className}`}>
        {renderPanel(panelIds[0] || "panel-1", 0)}
      </div>
    );
  }

  // 2. Two Columns Layout (Horizontal Split)
  if (layoutId === "two-columns") {
    return (
      <div className={`w-full ${containerHeightClass} border border-zinc-800/80 rounded overflow-hidden ${className}`}>
        <AtlasSplit id="layout-two-columns" direction="horizontal" className="w-full h-full">
          <AtlasPanel id="panel-slot-1" minSize={20} className="p-0.5">
            {renderPanel(panelIds[0], 0)}
          </AtlasPanel>
          <AtlasResizeHandle withHandleIcon />
          <AtlasPanel id="panel-slot-2" minSize={20} className="p-0.5">
            {renderPanel(panelIds[1], 1)}
          </AtlasPanel>
        </AtlasSplit>
      </div>
    );
  }

  // 3. Two Rows Layout (Vertical Split)
  if (layoutId === "two-rows") {
    return (
      <div className={`w-full ${containerHeightClass} border border-zinc-800/80 rounded overflow-hidden ${className}`}>
        <AtlasSplit id="layout-two-rows" direction="vertical" className="w-full h-full">
          <AtlasPanel id="panel-slot-1" minSize={20} className="p-0.5">
            {renderPanel(panelIds[0], 0)}
          </AtlasPanel>
          <AtlasResizeHandle withHandleIcon />
          <AtlasPanel id="panel-slot-2" minSize={20} className="p-0.5">
            {renderPanel(panelIds[1], 1)}
          </AtlasPanel>
        </AtlasSplit>
      </div>
    );
  }

  // 4. Three Charts - Left Focus
  if (layoutId === "three-left-focus") {
    return (
      <div className={`w-full ${containerHeightClass} border border-zinc-800/80 rounded overflow-hidden ${className}`}>
        <AtlasSplit id="layout-three-left" direction="horizontal" className="w-full h-full">
          {/* Large Left Chart */}
          <AtlasPanel id="panel-slot-left" minSize={35} className="p-0.5">
            {renderPanel(panelIds[0], 0)}
          </AtlasPanel>
          <AtlasResizeHandle withHandleIcon />
          {/* Two Vertically Stacked Right Charts */}
          <AtlasPanel id="panel-slot-right-group" minSize={25} className="p-0">
            <AtlasSplit id="layout-three-right-inner" direction="vertical" className="w-full h-full">
              <AtlasPanel id="panel-slot-right-top" minSize={20} className="p-0.5">
                {renderPanel(panelIds[1], 1)}
              </AtlasPanel>
              <AtlasResizeHandle withHandleIcon />
              <AtlasPanel id="panel-slot-right-bottom" minSize={20} className="p-0.5">
                {renderPanel(panelIds[2], 2)}
              </AtlasPanel>
            </AtlasSplit>
          </AtlasPanel>
        </AtlasSplit>
      </div>
    );
  }

  // 5. Three Charts - Top Focus
  if (layoutId === "three-top-focus") {
    return (
      <div className={`w-full ${containerHeightClass} border border-zinc-800/80 rounded overflow-hidden ${className}`}>
        <AtlasSplit id="layout-three-top" direction="vertical" className="w-full h-full">
          {/* Large Top Chart */}
          <AtlasPanel id="panel-slot-top" minSize={35} className="p-0.5">
            {renderPanel(panelIds[0], 0)}
          </AtlasPanel>
          <AtlasResizeHandle withHandleIcon />
          {/* Two Horizontally Split Bottom Charts */}
          <AtlasPanel id="panel-slot-bottom-group" minSize={25} className="p-0">
            <AtlasSplit id="layout-three-bottom-inner" direction="horizontal" className="w-full h-full">
              <AtlasPanel id="panel-slot-bottom-left" minSize={20} className="p-0.5">
                {renderPanel(panelIds[1], 1)}
              </AtlasPanel>
              <AtlasResizeHandle withHandleIcon />
              <AtlasPanel id="panel-slot-bottom-right" minSize={20} className="p-0.5">
                {renderPanel(panelIds[2], 2)}
              </AtlasPanel>
            </AtlasSplit>
          </AtlasPanel>
        </AtlasSplit>
      </div>
    );
  }

  // 6. Four Grid (2x2)
  return (
    <div className={`w-full ${containerHeightClass} border border-zinc-800/80 rounded overflow-hidden ${className}`}>
      <AtlasSplit id="layout-four-grid-v" direction="vertical" className="w-full h-full">
        {/* Top Row: Panel 1 & Panel 2 */}
        <AtlasPanel id="slot-row-1" minSize={25} className="p-0">
          <AtlasSplit id="layout-four-top-h" direction="horizontal" className="w-full h-full">
            <AtlasPanel id="slot-r1-c1" minSize={20} className="p-0.5">
              {renderPanel(panelIds[0], 0)}
            </AtlasPanel>
            <AtlasResizeHandle withHandleIcon />
            <AtlasPanel id="slot-r1-c2" minSize={20} className="p-0.5">
              {renderPanel(panelIds[1], 1)}
            </AtlasPanel>
          </AtlasSplit>
        </AtlasPanel>
        <AtlasResizeHandle withHandleIcon />
        {/* Bottom Row: Panel 3 & Panel 4 */}
        <AtlasPanel id="slot-row-2" minSize={25} className="p-0">
          <AtlasSplit id="layout-four-bottom-h" direction="horizontal" className="w-full h-full">
            <AtlasPanel id="slot-r2-c1" minSize={20} className="p-0.5">
              {renderPanel(panelIds[2], 2)}
            </AtlasPanel>
            <AtlasResizeHandle withHandleIcon />
            <AtlasPanel id="slot-r2-c2" minSize={20} className="p-0.5">
              {renderPanel(panelIds[3], 3)}
            </AtlasPanel>
          </AtlasSplit>
        </AtlasPanel>
      </AtlasSplit>
    </div>
  );
}
