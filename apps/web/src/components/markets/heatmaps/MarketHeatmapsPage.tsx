"use client";

import React, { useState } from "react";
import { MarketsNavigationTabs } from "@/components/markets/MarketsNavigationTabs";
import { useMarketHeatmap } from "@/hooks/markets/useMarketHeatmap";
import { HeatmapsHeader } from "./HeatmapsHeader";
import { HeatmapUniverseSelector } from "./HeatmapUniverseSelector";
import { HeatmapPeriodSelector } from "./HeatmapPeriodSelector";
import { HeatmapModeSelector } from "./HeatmapModeSelector";
import { HeatmapCoverageSummary } from "./HeatmapCoverageSummary";
import { HeatmapLegend } from "./HeatmapLegend";
import { HeatmapTreemap } from "./HeatmapTreemap";
import { HeatmapInspector } from "./HeatmapInspector";
import { HeatmapAccessibleTable } from "./HeatmapAccessibleTable";
import { HeatmapEmptyState, HeatmapErrorState, HeatmapLoadingState } from "./HeatmapEmptyErrorStates";

export function MarketHeatmapsPage() {
  const [showTable, setShowTable] = useState(false);

  const {
    data,
    universes,
    currentUniverse,
    nodes,
    groups,
    coverage,
    isLoading,
    isRefetching,
    isError,
    error,
    refetch,

    universeId,
    setUniverseId,
    visualizationMode,
    setVisualizationMode,
    hierarchyMode,
    setHierarchyMode,
    comparisonWindow,
    setComparisonWindow,
    drilldownSector,
    setDrilldownSector,
    selectedNode,
    setSelectedNode,
  } = useMarketHeatmap();

  const supportsMarketCap = currentUniverse?.supported_modes.includes("market_cap_weighted") ?? true;
  const supportsSector = currentUniverse?.supported_hierarchies.includes("sector") ?? true;

  // Flatten nodes for accessible table if in sector mode
  const allLeafNodes = React.useMemo(() => {
    if (nodes.length > 0) return nodes;
    return groups.flatMap((g) => g.children);
  }, [nodes, groups]);

  return (
    <div className="flex flex-col min-h-screen p-4 sm:p-6 max-w-[1600px] mx-auto space-y-4">
      {/* Module Navigation */}
      <MarketsNavigationTabs />

      {/* Heatmaps Header */}
      <HeatmapsHeader
        universeName={currentUniverse?.display_name}
        assetClass={currentUniverse?.asset_class}
        calculatedAt={data?.calculated_at}
        isLoading={isLoading}
        isRefetching={isRefetching}
        onRefresh={refetch}
        showTable={showTable}
        onToggleTable={() => setShowTable(!showTable)}
      />

      {/* Control Bar: Universe, Window, Weighting Mode, Hierarchy */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-3 rounded-lg bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
        <div className="flex flex-wrap items-center gap-4">
          <HeatmapUniverseSelector
            universes={universes}
            selectedUniverseId={universeId}
            onSelectUniverse={setUniverseId}
            disabled={isLoading}
          />

          <HeatmapPeriodSelector
            supportedWindows={currentUniverse?.supported_windows}
            selectedWindow={comparisonWindow}
            onSelectWindow={setComparisonWindow}
            disabled={isLoading}
          />
        </div>

        <HeatmapModeSelector
          visualizationMode={visualizationMode}
          onSelectVisualizationMode={setVisualizationMode}
          supportsMarketCapWeighted={supportsMarketCap}
          hierarchyMode={hierarchyMode}
          onSelectHierarchyMode={setHierarchyMode}
          supportsSectorHierarchy={supportsSector}
          disabled={isLoading}
        />
      </div>

      {/* Coverage Transparency Summary */}
      <HeatmapCoverageSummary
        coverage={coverage}
        weightUnit={currentUniverse?.weight_unit}
        weightLabel={currentUniverse?.weight_metric_label}
      />

      {/* Performance Color Scale Legend */}
      <HeatmapLegend />

      {/* Main Content Area */}
      {isLoading ? (
        <HeatmapLoadingState />
      ) : isError ? (
        <HeatmapErrorState error={error} onRetry={refetch} />
      ) : allLeafNodes.length === 0 ? (
        <HeatmapEmptyState />
      ) : (
        <div className="flex flex-col lg:flex-row gap-4 items-start w-full">
          {/* Main Visual Treemap */}
          <div className={`flex-1 w-full transition-all duration-200 ${selectedNode ? "lg:w-[70%]" : "w-full"}`}>
            {showTable ? (
              <HeatmapAccessibleTable
                nodes={allLeafNodes}
                selectedNode={selectedNode}
                onSelectNode={setSelectedNode}
                weightUnit={currentUniverse?.weight_unit}
              />
            ) : (
              <HeatmapTreemap
                nodes={nodes}
                groups={groups}
                hierarchyMode={hierarchyMode}
                selectedNode={selectedNode}
                onSelectNode={setSelectedNode}
                drilldownSector={drilldownSector}
                onDrilldownSector={setDrilldownSector}
                weightUnit={currentUniverse?.weight_unit}
              />
            )}
          </div>

          {/* Inspector Panel */}
          {selectedNode && (
            <div className="w-full lg:w-[30%] min-w-[320px] max-w-[420px] shrink-0 sticky top-4">
              <HeatmapInspector
                node={selectedNode}
                onClose={() => setSelectedNode(null)}
                weightLabel={currentUniverse?.weight_metric_label}
                weightUnit={currentUniverse?.weight_unit}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
