"use client";

import React from "react";
import { AlertCircle, SlidersHorizontal, Sparkles } from "lucide-react";
import {
  CountryOption,
  ExchangeOption,
  FilterCriterion,
  FilterOperator,
  ScreenerFilterDefinition,
  ScreenerUniverseDefinition,
  SectorOption,
} from "@/lib/screeners/types";
import { useVisualFilterBuilder } from "@/hooks/screeners/useVisualFilterBuilder";
import { FilterLibrary } from "./FilterLibrary";
import { ActiveConditionCanvas } from "./ActiveConditionCanvas";
import { VisualBuilderToolbar } from "./VisualBuilderToolbar";
import { FilterDefinitionInspector } from "./FilterDefinitionInspector";
import { VisualQueryPreview } from "./VisualQueryPreview";

interface VisualScreenerBuilderProps {
  filtersRegistry: ScreenerFilterDefinition[];
  universes: ScreenerUniverseDefinition[];
  selectedUniverseId: string;
  exchanges: ExchangeOption[];
  geographies: CountryOption[];
  industries: SectorOption[];
  appliedFilters: FilterCriterion[];
  onApplyFilters: (criteria: FilterCriterion[]) => void;
  isLoading?: boolean;
}

const PRESET_SCREENS = [
  {
    label: "Mega-Cap (>$100B)",
    filterId: "market_cap",
    operator: "gte" as FilterOperator,
    value: "100",
    magnitude: "BILLIONS" as const,
  },
  {
    label: "Low P/E (<25x)",
    filterId: "pe_ratio",
    operator: "lte" as FilterOperator,
    value: "25.0",
  },
  {
    label: "Growth YoY (>10%)",
    filterId: "revenue_growth_yoy",
    operator: "gte" as FilterOperator,
    value: "10.0",
  },
  {
    label: "Above 200 SMA",
    filterId: "price_above_sma200",
    operator: "eq" as FilterOperator,
    value: "true",
  },
  {
    label: "RSI Momentum (<70)",
    filterId: "rsi_14",
    operator: "lte" as FilterOperator,
    value: "70.0",
  },
  {
    label: "Positive FCF (>$0)",
    filterId: "fcf",
    operator: "gt" as FilterOperator,
    value: "0",
  },
  {
    label: "High Operating Margin (>20%)",
    filterId: "operating_margin",
    operator: "gte" as FilterOperator,
    value: "20.0",
  },
];

export function VisualScreenerBuilder({
  filtersRegistry,
  universes,
  selectedUniverseId,
  exchanges,
  geographies,
  industries,
  appliedFilters,
  onApplyFilters,
  isLoading = false,
}: VisualScreenerBuilderProps) {
  const {
    conditions,
    isDirty,
    isValid,
    issues,
    warnings,
    queryPreview,
    isLibraryOpen,
    selectedFilterForInspect,
    isPreviewOpen,
    toggleLibrary,
    setInspectFilter,
    setIsPreviewOpen,
    addCondition,
    updateCondition,
    removeCondition,
    duplicateCondition,
    clearConditions,
    discardChanges,
    applyFilters,
  } = useVisualFilterBuilder({
    filtersRegistry,
    universes,
    selectedUniverseId,
    appliedFilters,
    onApplyQuery: onApplyFilters,
    isLoading,
  });

  const handleApplyPreset = (preset: (typeof PRESET_SCREENS)[0]) => {
    addCondition(preset.filterId);
    // Find newly added condition and set preset values
    setTimeout(() => {
      // Small timeout to allow state insertion
      const lastCond = conditions[conditions.length - 1];
      if (lastCond) {
        updateCondition(lastCond.conditionId, {
          operator: preset.operator,
          value: preset.value,
          magnitude: preset.magnitude || "UNITS",
        });
      }
    }, 50);
  };

  const contradictions = issues.filter(
    (i) => i.code === "SCREENER_CONTRADICTORY_CONDITIONS"
  );

  return (
    <div className="flex flex-col border-b border-border/60 bg-background/60">
      {/* Presets Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/40 px-6 py-2 bg-muted/10 text-xs">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="flex items-center gap-1 text-[11px] font-medium text-muted-foreground mr-1">
            <Sparkles className="h-3 w-3 text-primary" />
            Quick Presets:
          </span>
          {PRESET_SCREENS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              onClick={() => handleApplyPreset(preset)}
              className="rounded-full border border-border/60 bg-background/80 px-2 py-0.5 text-[10px] font-medium text-foreground/90 transition-colors hover:border-primary/50 hover:bg-muted"
            >
              + {preset.label}
            </button>
          ))}
        </div>

        {/* Catalog Toggle quick link */}
        <button
          type="button"
          onClick={toggleLibrary}
          className="inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
        >
          <SlidersHorizontal className="h-3 w-3" />
          <span>{isLibraryOpen ? "Close Metric Catalog" : "Browse All Metrics"}</span>
        </button>
      </div>

      {/* Main Builder Panel (Catalog + Canvas) */}
      <div className="flex max-h-[380px] min-h-[140px] w-full overflow-hidden">
        {/* Metric Catalog (Left Drawer) */}
        <FilterLibrary
          filtersRegistry={filtersRegistry}
          onAddCondition={addCondition}
          onInspectFilter={setInspectFilter}
          isOpen={isLibraryOpen}
          onClose={toggleLibrary}
        />

        {/* Active Conditions Canvas (Center Workspace) */}
        <div className="flex flex-1 flex-col overflow-hidden p-4">
          {/* Contradiction Warning Alert */}
          {contradictions.length > 0 && (
            <div className="mb-3 flex items-start gap-2 rounded border border-destructive/60 bg-destructive/10 p-2.5 text-xs text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <div>
                <span className="font-semibold">Contradictory Conditions:</span>
                <ul className="mt-0.5 list-disc pl-4 text-[11px] space-y-0.5">
                  {contradictions.map((c, i) => (
                    <li key={i}>{c.message}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Universe Incompatibility Warnings */}
          {warnings.length > 0 && (
            <div className="mb-3 flex items-start gap-2 rounded border border-amber-500/50 bg-amber-500/10 p-2.5 text-xs text-amber-500">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <div>
                <span className="font-semibold">Filter Dependency Notice:</span>
                <p className="mt-0.5 text-[11px] leading-relaxed text-amber-500/90">
                  {warnings[0]}
                </p>
              </div>
            </div>
          )}

          {/* Canvas Rows */}
          <ActiveConditionCanvas
            conditions={conditions}
            filtersRegistry={filtersRegistry}
            exchanges={exchanges}
            geographies={geographies}
            industries={industries}
            onUpdateCondition={updateCondition}
            onRemoveCondition={removeCondition}
            onDuplicateCondition={duplicateCondition}
            onInspectFilter={setInspectFilter}
            onOpenLibrary={() => toggleLibrary()}
          />
        </div>
      </div>

      {/* Builder Toolbar (Bottom Bar) */}
      <VisualBuilderToolbar
        conditionsCount={conditions.length}
        maxConditions={20}
        isDirty={isDirty}
        isValid={isValid}
        isLoading={isLoading}
        isLibraryOpen={isLibraryOpen}
        onToggleLibrary={toggleLibrary}
        onApply={applyFilters}
        onDiscard={discardChanges}
        onClear={clearConditions}
        onReviewLogic={() => setIsPreviewOpen(true)}
      />

      {/* Metric Inspector Modal */}
      <FilterDefinitionInspector
        filter={selectedFilterForInspect}
        onClose={() => setInspectFilter(null)}
        onAddCondition={addCondition}
      />

      {/* Query Review Logic Modal */}
      <VisualQueryPreview
        summary={queryPreview}
        isOpen={isPreviewOpen}
        onClose={() => setIsPreviewOpen(false)}
      />
    </div>
  );
}
