"use client";

import React from "react";
import { Filter, RotateCcw } from "lucide-react";

export interface MoverFiltersProps {
  exchangeScope: string[];
  selectedExchange: string;
  onSelectExchange: (exchange: string) => void;
  onReset: () => void;
  disabled?: boolean;
}

export function MoverFilters({
  exchangeScope,
  selectedExchange,
  onSelectExchange,
  onReset,
  disabled,
}: MoverFiltersProps) {
  const hasActiveFilters = selectedExchange !== "all";

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 py-2">
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)] font-medium">
          <Filter className="h-3.5 w-3.5 text-zinc-400" />
          <span>Venue:</span>
        </div>

        <select
          value={selectedExchange}
          onChange={(e) => onSelectExchange(e.target.value)}
          disabled={disabled}
          className="h-7 px-2.5 text-xs bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          aria-label="Filter by venue or exchange"
        >
          <option value="all">All Venues</option>
          {exchangeScope.map((venue) => (
            <option key={venue} value={venue}>
              {venue}
            </option>
          ))}
        </select>
      </div>

      {hasActiveFilters && (
        <button
          type="button"
          onClick={onReset}
          disabled={disabled}
          className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)] hover:bg-zinc-800/40 rounded transition-colors"
        >
          <RotateCcw className="h-3 w-3" />
          <span>Reset Filters</span>
        </button>
      )}
    </div>
  );
}
