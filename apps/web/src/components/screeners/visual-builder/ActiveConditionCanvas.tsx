"use client";

import React from "react";
import { Filter, Layers, Plus, Sparkles } from "lucide-react";
import {
  CountryOption,
  ExchangeOption,
  FilterCategory,
  ScreenerFilterDefinition,
  SectorOption,
  VisualFilterCondition,
} from "@/lib/screeners/types";
import { VisualConditionRow } from "./VisualConditionRow";

interface ActiveConditionCanvasProps {
  conditions: VisualFilterCondition[];
  filtersRegistry: ScreenerFilterDefinition[];
  exchanges: ExchangeOption[];
  geographies: CountryOption[];
  industries: SectorOption[];
  onUpdateCondition: (conditionId: string, updates: Partial<VisualFilterCondition>) => void;
  onRemoveCondition: (conditionId: string) => void;
  onDuplicateCondition: (conditionId: string) => void;
  onInspectFilter: (filter: ScreenerFilterDefinition) => void;
  onOpenLibrary: () => void;
}

export function ActiveConditionCanvas({
  conditions,
  filtersRegistry,
  exchanges,
  geographies,
  industries,
  onUpdateCondition,
  onRemoveCondition,
  onDuplicateCondition,
  onInspectFilter,
  onOpenLibrary,
}: ActiveConditionCanvasProps) {
  if (conditions.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center rounded-lg border border-dashed border-border/80 p-8 text-center bg-card/20">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary mb-3">
          <Filter className="h-6 w-6 stroke-[1.5]" />
        </div>
        <h3 className="text-sm font-semibold text-foreground">No active screening conditions</h3>
        <p className="mt-1 max-w-sm text-xs text-muted-foreground leading-relaxed">
          Build professional institutional screens by selecting financial metrics, valuation ratios, fundamentals, or market filters.
        </p>
        <button
          type="button"
          onClick={onOpenLibrary}
          className="mt-4 inline-flex items-center gap-1.5 rounded bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-xs"
        >
          <Plus className="h-3.5 w-3.5" />
          Open Metric Catalog
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col overflow-y-auto pr-1 space-y-2">
      {conditions.map((condition, idx) => {
        const isLast = idx === conditions.length - 1;
        return (
          <React.Fragment key={condition.conditionId}>
            <VisualConditionRow
              condition={condition}
              index={idx}
              totalConditions={conditions.length}
              filtersRegistry={filtersRegistry}
              exchanges={exchanges}
              geographies={geographies}
              industries={industries}
              onUpdate={onUpdateCondition}
              onRemove={onRemoveCondition}
              onDuplicate={onDuplicateCondition}
              onInspect={onInspectFilter}
            />

            {/* Explicit Institutional AND Logic Connector */}
            {!isLast && (
              <div className="flex items-center justify-center py-0.5">
                <div className="flex items-center gap-1.5 rounded-full border border-border/60 bg-muted/60 px-2 py-0.5 text-[9px] font-mono font-semibold uppercase tracking-wider text-muted-foreground select-none">
                  AND
                </div>
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
