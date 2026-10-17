"use client";

import React from "react";
import { HeatmapHierarchyMode, HeatmapVisualizationMode } from "@/lib/markets/heatmaps";
import { Grid, Network, Boxes, Square } from "lucide-react";

interface HeatmapModeSelectorProps {
  visualizationMode: HeatmapVisualizationMode;
  onSelectVisualizationMode: (mode: HeatmapVisualizationMode) => void;
  supportsMarketCapWeighted: boolean;
  hierarchyMode: HeatmapHierarchyMode;
  onSelectHierarchyMode: (hierarchy: HeatmapHierarchyMode) => void;
  supportsSectorHierarchy: boolean;
  disabled?: boolean;
}

export function HeatmapModeSelector({
  visualizationMode,
  onSelectVisualizationMode,
  supportsMarketCapWeighted,
  hierarchyMode,
  onSelectHierarchyMode,
  supportsSectorHierarchy,
  disabled = false,
}: HeatmapModeSelectorProps) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      {/* Visualization Mode: Equal-Size vs Market-Cap Weighted */}
      <div className="flex flex-col gap-1">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)]">
          Weighting Mode
        </span>
        <div className="inline-flex h-8 p-0.5 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
          <button
            type="button"
            onClick={() => onSelectVisualizationMode("equal_size")}
            disabled={disabled}
            className={`flex items-center gap-1.5 px-3 rounded text-xs font-medium transition-colors ${
              visualizationMode === "equal_size"
                ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] shadow-sm font-semibold"
                : "text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-secondary)]"
            }`}
            title="Every qualified security receives an equal tile area. Area has no financial weight meaning."
          >
            <Square className="w-3.5 h-3.5" />
            <span>Equal-Size</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectVisualizationMode("market_cap_weighted")}
            disabled={disabled || !supportsMarketCapWeighted}
            className={`flex items-center gap-1.5 px-3 rounded text-xs font-medium transition-colors ${
              visualizationMode === "market_cap_weighted"
                ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] shadow-sm font-semibold"
                : supportsMarketCapWeighted
                ? "text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-secondary)]"
                : "text-[var(--atlas-text-tertiary)] opacity-40 cursor-not-allowed"
            }`}
            title={
              supportsMarketCapWeighted
                ? "Tile area strictly represents verified market capitalization."
                : "Market-cap weighting unavailable: verified capitalization weights are not supported for this universe."
            }
          >
            <Boxes className="w-3.5 h-3.5" />
            <span>Market-Cap Weighted</span>
          </button>
        </div>
      </div>

      {/* Hierarchy Mode: Flat vs Sector Grouped */}
      <div className="flex flex-col gap-1">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)]">
          Hierarchy
        </span>
        <div className="inline-flex h-8 p-0.5 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
          <button
            type="button"
            onClick={() => onSelectHierarchyMode("sector")}
            disabled={disabled || !supportsSectorHierarchy}
            className={`flex items-center gap-1.5 px-3 rounded text-xs font-medium transition-colors ${
              hierarchyMode === "sector"
                ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] shadow-sm font-semibold"
                : supportsSectorHierarchy
                ? "text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-secondary)]"
                : "text-[var(--atlas-text-tertiary)] opacity-40 cursor-not-allowed"
            }`}
            title="Group constituents by verified GICS sectors"
          >
            <Network className="w-3.5 h-3.5" />
            <span>Sector Grouped</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectHierarchyMode("none")}
            disabled={disabled}
            className={`flex items-center gap-1.5 px-3 rounded text-xs font-medium transition-colors ${
              hierarchyMode === "none"
                ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] shadow-sm font-semibold"
                : "text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-secondary)]"
            }`}
            title="Flat ungrouped layout"
          >
            <Grid className="w-3.5 h-3.5" />
            <span>Flat</span>
          </button>
        </div>
      </div>
    </div>
  );
}
