"use client";

import React from "react";
import { AlertCircle, RotateCcw, Search, Sparkles } from "lucide-react";

export interface EquityEmptyStateProps {
  type: "loading" | "empty_search" | "empty_catalog" | "error";
  errorMessage?: string;
  onResetFilters?: () => void;
  onRetry?: () => void;
}

export function EquityEmptyState({
  type,
  errorMessage,
  onResetFilters,
  onRetry,
}: EquityEmptyStateProps) {
  if (type === "loading") {
    return (
      <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-6 space-y-4 animate-pulse">
        <div className="h-4 bg-zinc-800 rounded w-1/4"></div>
        <div className="space-y-2">
          <div className="h-8 bg-zinc-800/60 rounded"></div>
          <div className="h-8 bg-zinc-800/40 rounded"></div>
          <div className="h-8 bg-zinc-800/60 rounded"></div>
          <div className="h-8 bg-zinc-800/40 rounded"></div>
        </div>
      </div>
    );
  }

  if (type === "error") {
    return (
      <div className="bg-[var(--atlas-surface-card)] border border-rose-500/20 rounded-md p-8 text-center">
        <div className="inline-flex p-3 rounded-full bg-rose-500/10 text-rose-400 mb-3">
          <AlertCircle className="h-6 w-6" aria-hidden="true" />
        </div>
        <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)] mb-1">
          Equity Directory Unavailable
        </h3>
        <p className="text-xs text-[var(--atlas-text-secondary)] max-w-md mx-auto mb-4">
          {errorMessage ||
            "Unable to retrieve equity securities from the ATLAS Markets endpoint."}
        </p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded transition-colors"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Retry Connection</span>
          </button>
        )}
      </div>
    );
  }

  if (type === "empty_search") {
    return (
      <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-8 text-center">
        <div className="inline-flex p-3 rounded-full bg-zinc-800 text-zinc-400 mb-3">
          <Search className="h-6 w-6" aria-hidden="true" />
        </div>
        <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)] mb-1">
          No Matching Equities
        </h3>
        <p className="text-xs text-[var(--atlas-text-secondary)] max-w-md mx-auto mb-4">
          No canonical equity securities matched the current search query or applied venue filters.
        </p>
        {onResetFilters && (
          <button
            type="button"
            onClick={onResetFilters}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 rounded transition-colors"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset Filters</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-8 text-center">
      <div className="inline-flex p-3 rounded-full bg-zinc-800 text-zinc-400 mb-3">
        <Sparkles className="h-6 w-6" aria-hidden="true" />
      </div>
      <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)] mb-1">
        No Equities Available
      </h3>
      <p className="text-xs text-[var(--atlas-text-secondary)] max-w-md mx-auto">
        Equity securities have not yet been configured or indexed in the ATLAS instrument catalog.
      </p>
    </div>
  );
}
