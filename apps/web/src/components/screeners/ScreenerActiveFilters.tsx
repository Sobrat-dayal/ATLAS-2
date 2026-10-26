"use client";

import React from "react";
import { Filter, X } from "lucide-react";
import { FilterCriterion, ScreenerFilterDefinition } from "@/lib/screeners/types";
import { formatCompactCurrency, formatMultiple, formatPercent, formatPrice } from "@/lib/screeners/formatting";

interface ScreenerActiveFiltersProps {
  activeFilters: FilterCriterion[];
  filtersRegistry: ScreenerFilterDefinition[];
  selectedExchanges: string[];
  selectedCountries: string[];
  selectedSectors: string[];
  onRemoveFilter: (filterId: string) => void;
  onClearFilters: () => void;
}

export function ScreenerActiveFilters({
  activeFilters,
  filtersRegistry,
  selectedExchanges,
  selectedCountries,
  selectedSectors,
  onRemoveFilter,
  onClearFilters,
}: ScreenerActiveFiltersProps) {
  const hasActiveConditions =
    activeFilters.length > 0 ||
    selectedExchanges.length > 0 ||
    selectedCountries.length > 0 ||
    selectedSectors.length > 0;

  if (!hasActiveConditions) return null;

  const formatFilterValue = (crit: FilterCriterion, def?: ScreenerFilterDefinition) => {
    const num = Number(crit.value);
    const opSym =
      crit.operator === "gte"
        ? "≥"
        : crit.operator === "lte"
        ? "≤"
        : crit.operator === "gt"
        ? ">"
        : crit.operator === "lt"
        ? "<"
        : crit.operator === "eq"
        ? "="
        : crit.operator === "ne"
        ? "≠"
        : crit.operator === "between"
        ? "BETWEEN"
        : crit.operator;

    let displayVal = String(crit.value);
    if (!isNaN(num) && def) {
      if (def.filter_id === "market_cap" || def.filter_id === "revenue" || def.filter_id === "net_income") {
        displayVal = formatCompactCurrency(num);
      } else if (def.filter_id === "last_price") {
        displayVal = formatPrice(num);
      } else if (def.unit_kind === "percent") {
        displayVal = formatPercent(num);
      } else if (def.unit_kind === "multiple") {
        displayVal = formatMultiple(num);
      }
    }

    if (crit.operator === "between" && crit.secondary_value !== undefined) {
      let secDisplay = String(crit.secondary_value);
      const secNum = Number(crit.secondary_value);
      if (!isNaN(secNum) && def) {
        if (def.filter_id === "market_cap" || def.filter_id === "revenue" || def.filter_id === "net_income") {
          secDisplay = formatCompactCurrency(secNum);
        } else if (def.filter_id === "last_price") {
          secDisplay = formatPrice(secNum);
        }
      }
      return `${opSym} ${displayVal} AND ${secDisplay}`;
    }

    return `${opSym} ${displayVal}`;
  };

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-border/50 bg-muted/10 px-6 py-2">
      <div className="flex items-center gap-1 text-[11px] font-medium text-muted-foreground mr-1">
        <Filter className="h-3 w-3" />
        <span>Active Filters ({activeFilters.length}):</span>
      </div>

      {activeFilters.map((crit) => {
        const def = filtersRegistry.find((f) => f.filter_id === crit.filter_id);
        const name = def?.display_name || crit.filter_id;
        return (
          <span
            key={crit.filter_id}
            className="inline-flex items-center gap-1.5 rounded border border-border bg-background px-2.5 py-1 text-xs font-medium text-foreground shadow-xs"
          >
            <span className="text-muted-foreground">{name}:</span>
            <span className="font-mono font-semibold text-primary">
              {formatFilterValue(crit, def)}
            </span>
            <button
              type="button"
              onClick={() => onRemoveFilter(crit.filter_id)}
              className="ml-0.5 rounded p-0.5 text-muted-foreground hover:bg-muted hover:text-foreground"
              title="Remove filter"
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        );
      })}

      <button
        type="button"
        onClick={onClearFilters}
        className="ml-auto text-[11px] font-medium text-muted-foreground hover:text-destructive transition-colors"
      >
        Clear All
      </button>
    </div>
  );
}
