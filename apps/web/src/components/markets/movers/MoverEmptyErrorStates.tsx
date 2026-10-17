"use client";

import React from "react";
import { AlertTriangle, RefreshCw, TrendingUp } from "lucide-react";

export interface MoverEmptyStateProps {
  universeDisplayName?: string;
  categoryLabel?: string;
  onResetFilters?: () => void;
}

export function MoverEmptyState({
  universeDisplayName,
  categoryLabel = "market movers",
  onResetFilters,
}: MoverEmptyStateProps) {
  return (
    <div className="w-full bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-lg p-8 flex flex-col items-center justify-center text-center min-h-[260px]">
      <div className="h-10 w-10 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-3 text-zinc-500">
        <TrendingUp className="h-5 w-5" />
      </div>
      <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
        No qualifying {categoryLabel}
      </h3>
      <p className="text-xs text-[var(--atlas-text-secondary)] max-w-md mt-1 mb-4">
        No instruments in {universeDisplayName || "the selected universe"} currently meet
        the data qualification criteria for this ranking metric and comparison window.
      </p>
      {onResetFilters && (
        <button
          type="button"
          onClick={onResetFilters}
          className="px-3 py-1.5 text-xs font-medium rounded bg-zinc-800 hover:bg-zinc-700 text-[var(--atlas-text-primary)] transition-colors border border-zinc-700"
        >
          Reset Venue Filters
        </button>
      )}
    </div>
  );
}

export interface MoverErrorStateProps {
  error: Error | null;
  onRetry: () => void;
}

export function MoverErrorState({ error, onRetry }: MoverErrorStateProps) {
  return (
    <div className="w-full bg-[var(--atlas-surface-card)] border border-rose-900/40 rounded-lg p-8 flex flex-col items-center justify-center text-center min-h-[260px]">
      <div className="h-10 w-10 rounded-full bg-rose-950/60 border border-rose-800/60 flex items-center justify-center mb-3 text-rose-400">
        <AlertTriangle className="h-5 w-5" />
      </div>
      <h3 className="text-sm font-semibold text-rose-300">
        Failed to load market mover rankings
      </h3>
      <p className="text-xs text-rose-400/80 max-w-md mt-1 mb-4 font-mono">
        {error?.message || "An unexpected error occurred while querying mover metrics."}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-rose-900/60 hover:bg-rose-800/80 text-rose-200 transition-colors border border-rose-700/60"
      >
        <RefreshCw className="h-3.5 w-3.5" />
        <span>Retry Query</span>
      </button>
    </div>
  );
}
