"use client";

import React from "react";
import { FileQuestion, RotateCcw } from "lucide-react";

export interface FuturesEmptyStateProps {
  title?: string;
  description?: string;
  onReset?: () => void;
}

export function FuturesEmptyState({
  title = "No Futures Contracts Available",
  description = "No exchange-traded futures contracts match the requested parameters or are currently cataloged.",
  onReset,
}: FuturesEmptyStateProps) {
  return (
    <div
      role="status"
      aria-label="No data available"
      className="flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] my-4"
    >
      <div className="p-3 rounded-full bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-tertiary)] mb-3 border border-[var(--atlas-border-subtle)]">
        <FileQuestion className="h-6 w-6" aria-hidden="true" />
      </div>

      <h3 className="text-sm sm:text-base font-semibold text-[var(--atlas-text-primary)] mb-1">
        {title}
      </h3>

      <p className="text-xs text-[var(--atlas-text-secondary)] max-w-md mb-4 leading-relaxed">
        {description}
      </p>

      {onReset && (
        <button
          type="button"
          onClick={onReset}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-[var(--atlas-surface-subtle)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] text-[var(--atlas-text-primary)] transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
        >
          <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Reset All Filters</span>
        </button>
      )}
    </div>
  );
}
