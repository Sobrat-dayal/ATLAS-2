"use client";

import React, { useState } from "react";
import { useCrossAssetOverview } from "@/hooks/markets/useCrossAssetOverview";
import { CrossAssetHeader } from "./CrossAssetHeader";
import { CrossAssetUniverseSelector } from "./CrossAssetUniverseSelector";
import { CrossAssetModeSelector } from "./CrossAssetModeSelector";
import { CrossAssetWindowSelector } from "./CrossAssetWindowSelector";
import { CrossAssetCoverageSummary } from "./CrossAssetCoverageSummary";
import { AssetClassOverviewGrid } from "./AssetClassOverviewGrid";
import { CrossAssetComparisonTable } from "./CrossAssetComparisonTable";
import { CrossAssetInspector } from "./CrossAssetInspector";
import { AlignmentMethodologyPanel } from "./AlignmentMethodologyPanel";
import {
  CrossAssetEmptyState,
  CrossAssetErrorState,
  CrossAssetLoadingSkeleton,
} from "./CrossAssetEmptyErrorStates";

export function CrossAssetMarketsPage() {
  const [showMethodology, setShowMethodology] = useState<boolean>(false);

  const {
    data,
    universes,
    currentUniverse,
    members,
    sections,
    coverage,
    isLoading,
    isError,
    error,
    refetch,
    isRefetching,
    universeId,
    setUniverseId,
    mode,
    setMode,
    window,
    setWindow,
    selectedMember,
    setSelectedMember,
  } = useCrossAssetOverview();

  return (
    <div className="space-y-5">
      {/* 1. Header */}
      <CrossAssetHeader
        universeName={currentUniverse?.display_name}
        calculatedAt={data?.calculated_at}
        snapshotId={data?.snapshot_id}
        isLoading={isLoading}
        isRefetching={isRefetching}
        onRefresh={refetch}
        showMethodology={showMethodology}
        onToggleMethodology={() => setShowMethodology((prev) => !prev)}
      />

      {/* 2. Interactive Controls Bar */}
      <div className="p-3.5 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4">
          <CrossAssetUniverseSelector
            universes={universes}
            selectedUniverseId={universeId}
            onSelectUniverse={setUniverseId}
            isLoading={isLoading}
          />

          <CrossAssetModeSelector
            mode={mode}
            onSelectMode={setMode}
            isLoading={isLoading}
          />

          <CrossAssetWindowSelector
            window={window}
            onSelectWindow={setWindow}
            mode={mode}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* 3. Methodology Disclosures (Collapsible) */}
      {showMethodology && (
        <AlignmentMethodologyPanel onClose={() => setShowMethodology(false)} />
      )}

      {/* 4. Main Content Area */}
      {isLoading && !data ? (
        <CrossAssetLoadingSkeleton />
      ) : isError ? (
        <CrossAssetErrorState error={error} onRetry={refetch} />
      ) : members.length === 0 ? (
        <CrossAssetEmptyState />
      ) : (
        <div className="space-y-5">
          {/* Coverage & Completeness Summary */}
          <CrossAssetCoverageSummary
            coverage={coverage}
            mode={mode}
            window={window}
            requestedStart={data?.requested_start}
            requestedEnd={data?.requested_end}
          />

          {/* Asset-Class Overview Grid (in Native mode or overview) */}
          {mode === "native_overview" && sections.length > 0 && (
            <AssetClassOverviewGrid
              sections={sections}
              selectedMember={selectedMember}
              onSelectMember={setSelectedMember}
            />
          )}

          {/* Master Comparison Table & Inspector Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 items-start">
            <div className={selectedMember ? "lg:col-span-2 space-y-4" : "lg:col-span-3 space-y-4"}>
              <CrossAssetComparisonTable
                members={members}
                mode={mode}
                selectedMember={selectedMember}
                onSelectMember={setSelectedMember}
              />
            </div>

            {selectedMember && (
              <div className="lg:col-span-1 sticky top-4">
                <CrossAssetInspector
                  member={selectedMember}
                  onClose={() => setSelectedMember(null)}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
