"use client";

import React from "react";
import { Layers, RotateCcw } from "lucide-react";

export interface CryptoEmptyStateProps {
  isFiltered?: boolean;
  onResetFilters?: () => void;
  message?: string;
}

export function CryptoEmptyState({
  isFiltered = false,
  onResetFilters,
  message,
}: CryptoEmptyStateProps) {
  if (isFiltered) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-[var(--atlas-border-subtle)] rounded-lg bg-[var(--atlas-surface-card)] my-4">
        <Layers className="h-10 w-10 text-[var(--atlas-text-tertiary)] opacity-50 mb-3" aria-hidden="true" />
        <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
          No matching cryptocurrency markets
        </h3>
        <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 max-w-sm">
          {message || "No spot markets matched your active search query or filter criteria."}
        </p>
        {onResetFilters && (
          <button
            type="button"
            onClick={onResetFilters}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 mt-4 text-xs font-medium text-amber-400 hover:text-amber-300 bg-amber-950/20 hover:bg-amber-950/40 border border-amber-800/40 rounded transition-colors"
          >
            <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Reset Filters</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-[var(--atlas-border-subtle)] rounded-lg bg-[var(--atlas-surface-card)] my-4">
      <Layers className="h-10 w-10 text-[var(--atlas-text-tertiary)] opacity-50 mb-3" aria-hidden="true" />
      <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
        No cryptocurrency spot markets configured
      </h3>
      <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 max-w-sm">
        The ATLAS market catalog does not currently contain supported cryptocurrency spot trading pairs.
      </p>
    </div>
  );
}
