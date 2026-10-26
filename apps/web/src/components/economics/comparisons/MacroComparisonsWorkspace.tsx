"use client";

import React from "react";
import { useMacroComparisons } from "@/hooks/economics/useMacroComparisons";
import { MacroComparisonToolbar } from "./MacroComparisonToolbar";
import { MacroComparisonMatrix } from "./MacroComparisonMatrix";
import { MacroRankingTable } from "./MacroRankingTable";
import { MacroDistributionPanel } from "./MacroDistributionPanel";
import { MacroHistoricalTrendChart } from "./MacroHistoricalTrendChart";
import { MacroDivergencePanel } from "./MacroDivergencePanel";
import { MacroCorrelationMatrix } from "./MacroCorrelationMatrix";
import { ComparisonCoveragePanel } from "./ComparisonCoveragePanel";
import { ComparisonMethodologyInspector } from "./ComparisonMethodologyInspector";
import { AlertTriangle } from "lucide-react";

export function MacroComparisonsWorkspace() {
  const {
    activeView,
    setActiveView,
    selectedGeographyIds,
    selectedCohortId,
    handleSelectCohort,
    handleToggleCountry,
    handleSelectAllCountries,
    selectedMetricKind,
    setSelectedMetricKind,
    periodPolicy,
    setPeriodPolicy,
    rankingDirection,
    setRankingDirection,
    tiePolicy,
    setTiePolicy,
    weightingPolicy,
    setWeightingPolicy,
    basePeriod,
    setBasePeriod,
    divergenceCountryA,
    setDivergenceCountryA,
    divergenceCountryB,
    setDivergenceCountryB,
    correlationMethod,
    setCorrelationMethod,
    inspectedCell,
    setInspectedCell,
    indicators,
    geographies,
    cohorts,
    matrixData,
    rankingsData,
    distributionData,
    trendsData,
    divergenceData,
    correlationData,
    coverageData,
    isLoading,
    error,
    refreshCurrentView,
  } = useMacroComparisons();

  return (
    <div className="flex flex-col flex-1 h-full min-h-0 bg-atlas-background overflow-hidden">
      {/* Comparison Workspace Toolbar */}
      <MacroComparisonToolbar
        activeView={activeView}
        setActiveView={setActiveView}
        indicators={indicators}
        geographies={geographies}
        cohorts={cohorts}
        selectedGeographyIds={selectedGeographyIds}
        selectedCohortId={selectedCohortId}
        onSelectCohort={handleSelectCohort}
        onToggleCountry={handleToggleCountry}
        onSelectAllCountries={handleSelectAllCountries}
        selectedMetricKind={selectedMetricKind}
        onSelectMetricKind={setSelectedMetricKind}
        periodPolicy={periodPolicy}
        onChangePeriodPolicy={setPeriodPolicy}
        weightingPolicy={weightingPolicy}
        onChangeWeightingPolicy={setWeightingPolicy}
        basePeriod={basePeriod}
        onChangeBasePeriod={setBasePeriod}
        isLoading={isLoading}
        onRefresh={refreshCurrentView}
      />

      {/* Error Banner */}
      {error && (
        <div className="p-3 bg-rose-500/10 border-b border-rose-500/20 text-rose-300 text-xs flex items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={refreshCurrentView}
            className="px-2 py-0.5 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Active Subview Viewport */}
      <div className="flex-1 min-h-0 overflow-hidden flex flex-col">
        {activeView === "matrix" && (
          <MacroComparisonMatrix
            matrixData={matrixData}
            indicators={indicators}
            onSelectCell={setInspectedCell}
            isLoading={isLoading}
          />
        )}

        {activeView === "rankings" && (
          <MacroRankingTable
            rankingsData={rankingsData}
            indicators={indicators}
            direction={rankingDirection}
            onChangeDirection={setRankingDirection}
            tiePolicy={tiePolicy}
            onChangeTiePolicy={setTiePolicy}
            isLoading={isLoading}
          />
        )}

        {activeView === "distributions" && (
          <MacroDistributionPanel
            distributionData={distributionData}
            indicators={indicators}
            weightingPolicy={weightingPolicy}
            onChangeWeightingPolicy={setWeightingPolicy}
            isLoading={isLoading}
          />
        )}

        {activeView === "trends" && (
          <MacroHistoricalTrendChart
            trendsData={trendsData}
            indicators={indicators}
            basePeriod={basePeriod}
            onToggleBasePeriod={setBasePeriod}
            isLoading={isLoading}
          />
        )}

        {activeView === "divergence" && (
          <MacroDivergencePanel
            divergenceData={divergenceData}
            indicators={indicators}
            geographies={geographies}
            divergenceCountryA={divergenceCountryA}
            onChangeCountryA={setDivergenceCountryA}
            divergenceCountryB={divergenceCountryB}
            onChangeCountryB={setDivergenceCountryB}
            isLoading={isLoading}
          />
        )}

        {activeView === "correlations" && (
          <MacroCorrelationMatrix
            correlationData={correlationData}
            correlationMethod={correlationMethod}
            onChangeMethod={setCorrelationMethod}
            isLoading={isLoading}
          />
        )}

        {activeView === "coverage" && (
          <ComparisonCoveragePanel
            coverageData={coverageData}
            isLoading={isLoading}
          />
        )}
      </div>

      {/* Cell Methodology / Lineage Inspector Modal */}
      {inspectedCell && (
        <ComparisonMethodologyInspector
          cell={inspectedCell}
          onClose={() => setInspectedCell(null)}
        />
      )}
    </div>
  );
}
