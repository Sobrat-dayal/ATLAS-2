"use client";

import React from "react";
import { AlertCircle, RotateCcw } from "lucide-react";

export interface FxEmptyStateProps {
  isSearchOrFiltered: boolean;
  onResetFilters: () => void;
}

export function FxEmptyState({
  isSearchOrFiltered,
  onResetFilters,
}: FxEmptyStateProps) {
  if (isSearchOrFiltered) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md text-center">
        <AlertCircle className="h-8 w-8 text-amber-400 mb-3" />
        <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
          No matching currency pairs
        </h3>
        <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 mb-4 max-w-md">
          No configured currency pairs matched your current search filters. Try adjusting your query or resetting filters.
        </p>
        <button
          type="button"
          onClick={onResetFilters}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>Reset Filters</span>
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md text-center">
      <AlertCircle className="h-8 w-8 text-[var(--atlas-text-tertiary)] mb-3" />
      <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
        No FX pairs available
      </h3>
      <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 max-w-md">
        The ATLAS market catalog does not currently contain configured FX spot instruments.
      </p>
    </div>
  );
}
