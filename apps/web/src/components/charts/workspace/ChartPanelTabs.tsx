"use client";

/**
 * Responsive Mobile Chart Panel Tabs for ATLAS Charts (Stage 72).
 *
 * Provides a clean tabbed switcher on mobile / narrow viewports (<768px),
 * allowing users to focus on one chart panel at a time at full readable resolution
 * without altering the underlying multi-chart layout state or destroying panel data.
 */

import React from "react";
import { ChartPanelState } from "@/lib/charts/workspace";

export interface ChartPanelTabsProps {
  panelIds: string[];
  panels: Record<string, ChartPanelState>;
  activeTabId: string;
  onSelectTab: (panelId: string) => void;
}

export function ChartPanelTabs({
  panelIds,
  panels,
  activeTabId,
  onSelectTab,
}: ChartPanelTabsProps) {
  if (panelIds.length <= 1) return null;

  return (
    <div className="flex items-center gap-1.5 p-1 bg-zinc-950 border-b border-zinc-800 overflow-x-auto select-none">
      <span className="text-[10px] font-mono font-semibold text-zinc-500 uppercase px-1">
        Charts:
      </span>
      {panelIds.map((id, index) => {
        const panel = panels[id];
        const isSelected = id === activeTabId;
        const symbol = panel?.symbol || `P${index + 1}`;

        return (
          <button
            key={id}
            type="button"
            onClick={() => onSelectTab(id)}
            className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono font-medium border transition-colors shrink-0 ${
              isSelected
                ? "bg-cyan-950/70 border-cyan-500/80 text-cyan-300"
                : "bg-zinc-900 border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <span className="px-1 py-0.2 text-[9px] bg-zinc-800 rounded text-zinc-400">
              P{index + 1}
            </span>
            <span className="font-semibold">{symbol}</span>
            {panel?.interval && (
              <span className="text-[10px] text-zinc-500 uppercase">
                {panel.interval}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
