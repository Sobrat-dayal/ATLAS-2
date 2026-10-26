"use client";

import React, { useState } from "react";
import { Plus, SlidersHorizontal, Sparkles } from "lucide-react";
import {
  FilterCriterion,
  FilterOperator,
  ScreenerFilterDefinition,
} from "@/lib/screeners/types";

interface ScreenerFilterBuilderProps {
  filtersRegistry: ScreenerFilterDefinition[];
  activeFilterCount: number;
  onAddFilter: (criterion: FilterCriterion) => void;
}

const PRESET_SCREENS = [
  {
    label: "Mega-Cap (>$100B)",
    filter_id: "market_cap",
    operator: "gte" as FilterOperator,
    value: "100000000000",
  },
  {
    label: "Low P/E (<25x)",
    filter_id: "pe_ratio",
    operator: "lte" as FilterOperator,
    value: "25.0",
  },
  {
    label: "High Dividend (>2%)",
    filter_id: "dividend_yield",
    operator: "gte" as FilterOperator,
    value: "2.0",
  },
  {
    label: "High Revenue (>$50B)",
    filter_id: "revenue",
    operator: "gte" as FilterOperator,
    value: "50000000000",
  },
  {
    label: "Active Volume (>10M)",
    filter_id: "volume_20d_avg",
    operator: "gte" as FilterOperator,
    value: "10000000",
  },
];

export function ScreenerFilterBuilder({
  filtersRegistry,
  activeFilterCount,
  onAddFilter,
}: ScreenerFilterBuilderProps) {
  const [selectedFilterId, setSelectedFilterId] = useState<string>("market_cap");
  const [operator, setOperator] = useState<FilterOperator>("gte");
  const [val, setVal] = useState<string>("10000000000");
  const [secondaryVal, setSecondaryVal] = useState<string>("");

  const currentFilter = filtersRegistry.find((f) => f.filter_id === selectedFilterId);

  const handleMetricChange = (metricId: string) => {
    setSelectedFilterId(metricId);
    const def = filtersRegistry.find((f) => f.filter_id === metricId);
    if (def) {
      setOperator(def.default_operator);
      // Sensible defaults
      if (metricId === "market_cap") setVal("10000000000");
      else if (metricId === "last_price") setVal("50");
      else if (metricId === "pe_ratio") setVal("25");
      else if (metricId === "dividend_yield") setVal("2");
      else if (metricId === "revenue") setVal("10000000000");
      else if (metricId === "net_income") setVal("1000000000");
      else setVal("0");
    }
  };

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!val || !val.trim()) return;

    onAddFilter({
      filter_id: selectedFilterId,
      operator,
      value: val.trim(),
      secondary_value: operator === "between" ? secondaryVal.trim() : null,
    });
  };

  const isLimitReached = activeFilterCount >= 20;

  return (
    <div className="border-b border-border/50 bg-background/50 px-6 py-3">
      <div className="flex flex-col gap-2.5">
        {/* Preset Chips */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="flex items-center gap-1 text-[11px] font-medium text-muted-foreground mr-1">
            <Sparkles className="h-3 w-3 text-primary" />
            Presets:
          </span>
          {PRESET_SCREENS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              onClick={() =>
                onAddFilter({
                  filter_id: preset.filter_id,
                  operator: preset.operator,
                  value: preset.value,
                })
              }
              disabled={isLimitReached}
              className="rounded border border-border/60 bg-muted/30 px-2 py-0.5 text-[11px] text-muted-foreground transition-colors hover:border-primary/50 hover:bg-primary/5 hover:text-foreground disabled:opacity-50"
            >
              {preset.label}
            </button>
          ))}
        </div>

        {/* Builder Form */}
        <form onSubmit={handleAdd} className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <SlidersHorizontal className="h-3.5 w-3.5" />
            <span className="font-medium text-foreground">Add Condition:</span>
          </div>

          {/* Metric Selector */}
          <select
            aria-label="Filter Metric"
            value={selectedFilterId}
            onChange={(e) => handleMetricChange(e.target.value)}
            className="h-8 rounded-md border border-border bg-background px-2.5 text-xs font-medium text-foreground focus:border-primary focus:outline-none"
          >
            <optgroup label="Market Data">
              {filtersRegistry
                .filter((f) => f.category === "market_data")
                .map((f) => (
                  <option key={f.filter_id} value={f.filter_id}>
                    {f.display_name}
                  </option>
                ))}
            </optgroup>
            <optgroup label="Fundamentals">
              {filtersRegistry
                .filter((f) => f.category === "fundamentals")
                .map((f) => (
                  <option key={f.filter_id} value={f.filter_id}>
                    {f.display_name}
                  </option>
                ))}
            </optgroup>
            <optgroup label="Valuation">
              {filtersRegistry
                .filter((f) => f.category === "valuation")
                .map((f) => (
                  <option key={f.filter_id} value={f.filter_id}>
                    {f.display_name}
                  </option>
                ))}
            </optgroup>
            <optgroup label="Profitability">
              {filtersRegistry
                .filter((f) => f.category === "profitability")
                .map((f) => (
                  <option key={f.filter_id} value={f.filter_id}>
                    {f.display_name}
                  </option>
                ))}
            </optgroup>
          </select>

          {/* Operator Selector */}
          <select
            aria-label="Comparison Operator"
            value={operator}
            onChange={(e) => setOperator(e.target.value as FilterOperator)}
            className="h-8 rounded-md border border-border bg-background px-2.5 text-xs font-mono font-medium text-foreground focus:border-primary focus:outline-none"
          >
            {currentFilter?.allowed_operators.map((op) => (
              <option key={op} value={op}>
                {op === "gte"
                  ? "≥ (GTE)"
                  : op === "lte"
                  ? "≤ (LTE)"
                  : op === "gt"
                  ? "> (GT)"
                  : op === "lt"
                  ? "< (LT)"
                  : op === "eq"
                  ? "= (EQ)"
                  : op === "ne"
                  ? "≠ (NE)"
                  : op === "between"
                  ? "BETWEEN"
                  : op}
              </option>
            ))}
          </select>

          {/* Primary Value Input */}
          <input
            type="text"
            aria-label="Filter Threshold Value"
            value={val}
            onChange={(e) => setVal(e.target.value)}
            placeholder="Threshold"
            className="h-8 w-28 rounded-md border border-border bg-background px-2.5 font-mono text-xs text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none"
          />

          {/* Secondary Value Input for BETWEEN */}
          {operator === "between" && (
            <>
              <span className="text-xs text-muted-foreground">and</span>
              <input
                type="text"
                aria-label="Filter Range Upper Bound"
                value={secondaryVal}
                onChange={(e) => setSecondaryVal(e.target.value)}
                placeholder="Upper Bound"
                className="h-8 w-28 rounded-md border border-border bg-background px-2.5 font-mono text-xs text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none"
              />
            </>
          )}

          {/* Add Button */}
          <button
            type="submit"
            disabled={isLimitReached}
            className="flex h-8 items-center gap-1 rounded-md bg-secondary px-3 text-xs font-medium text-secondary-foreground transition-colors hover:bg-secondary/80 disabled:opacity-50"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>Add Filter</span>
          </button>
        </form>
      </div>
    </div>
  );
}
