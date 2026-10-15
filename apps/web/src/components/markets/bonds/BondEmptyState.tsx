"use client";

import React from "react";
import { AlertTriangle, FileText, RotateCcw } from "lucide-react";

export interface BondEmptyStateProps {
  type: "no_data" | "no_matches" | "error";
  errorMessage?: string;
  onResetFilters?: () => void;
  onRetry?: () => void;
}

export function BondEmptyState({
  type,
  errorMessage,
  onResetFilters,
  onRetry,
}: BondEmptyStateProps) {
  if (type === "error") {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded my-4">
        <div className="p-2.5 rounded-full bg-rose-500/10 text-rose-400 mb-3 border border-rose-500/20">
          <AlertTriangle className="h-6 w-6" aria-hidden="true" />
        </div>
        <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
          Failed to load bond market data
        </h3>
        <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 max-w-sm">
          {errorMessage || "An unexpected error occurred while communicating with the backend API."}
        </p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 rounded transition-colors"
          >
            Retry Request
          </button>
        )}
      </div>
    );
  }

  if (type === "no_matches") {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded my-4">
        <div className="p-2.5 rounded-full bg-zinc-800 text-zinc-400 mb-3 border border-zinc-700">
          <FileText className="h-6 w-6" aria-hidden="true" />
        </div>
        <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
          No matching bond securities
        </h3>
        <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 max-w-sm">
          No fixed-income debt instruments match your current combination of filters and search keywords.
        </p>
        {onResetFilters && (
          <button
            type="button"
            onClick={onResetFilters}
            className="mt-4 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-subtle)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors"
          >
            <RotateCcw className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>Reset All Filters</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded my-4">
      <div className="p-2.5 rounded-full bg-zinc-800 text-zinc-400 mb-3 border border-zinc-700">
        <FileText className="h-6 w-6" aria-hidden="true" />
      </div>
      <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
        No bond securities available
      </h3>
      <p className="text-xs text-[var(--atlas-text-secondary)] mt-1 max-w-sm">
        The ATLAS instrument catalog does not currently contain supported fixed-income securities.
      </p>
    </div>
  );
}
