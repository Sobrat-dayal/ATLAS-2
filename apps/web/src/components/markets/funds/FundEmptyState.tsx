"use client";

import React from "react";
import { FilterX, Layers } from "lucide-react";

export interface FundEmptyStateProps {
  isSearchOrFiltered: boolean;
  onResetFilters?: () => void;
}

export function FundEmptyState({
  isSearchOrFiltered,
  onResetFilters,
}: FundEmptyStateProps) {
  if (isSearchOrFiltered) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md text-center">
        <div className="p-3 rounded-full bg-zinc-800 text-[var(--atlas-text-secondary)] mb-3">
          <FilterX className="h-6 w-6 text-zinc-400" aria-hidden="true" />
        </div>
        <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
          No matching funds found
        </h3>
        <p className="text-xs text-[var(--atlas-text-secondary)] max-w-sm mt-1 mb-4">
          No investment funds or ETFs in the canonical directory matched your search or filter parameters.
        </p>
        {onResetFilters && (
          <button
            type="button"
            onClick={onResetFilters}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <span>Reset filters</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md text-center">
      <div className="p-3 rounded-full bg-zinc-800 text-[var(--atlas-text-secondary)] mb-3">
        <Layers className="h-6 w-6 text-zinc-400" aria-hidden="true" />
      </div>
      <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
        No funds available
      </h3>
      <p className="text-xs text-[var(--atlas-text-secondary)] max-w-sm mt-1">
        The ATLAS fund directory does not currently contain supported fund instruments.
      </p>
    </div>
  );
}
