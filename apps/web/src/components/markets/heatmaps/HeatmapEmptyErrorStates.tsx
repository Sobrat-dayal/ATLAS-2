"use client";

import React from "react";
import { AlertTriangle, RefreshCw, BarChart2 } from "lucide-react";

interface HeatmapErrorStateProps {
  error: Error | null;
  onRetry: () => void;
}

export function HeatmapErrorState({ error, onRetry }: HeatmapErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-lg bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] space-y-3">
      <div className="p-3 rounded-full bg-red-950/50 text-red-400 border border-red-800/40">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
        Failed to load market heatmap snapshot
      </h3>
      <p className="text-xs text-[var(--atlas-text-secondary)] max-w-md">
        {error?.message || "An unexpected error occurred while calculating heatmap observations."}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-[var(--atlas-accent-primary)] text-white hover:opacity-90 transition-opacity"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        <span>Retry</span>
      </button>
    </div>
  );
}

export function HeatmapEmptyState() {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-lg bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] space-y-3">
      <div className="p-3 rounded-full bg-zinc-900 text-zinc-400 border border-zinc-700">
        <BarChart2 className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
        No qualifying performance observations
      </h3>
      <p className="text-xs text-[var(--atlas-text-secondary)] max-w-md">
        No active instruments in this universe satisfy the required price observation and comparison window rules.
      </p>
    </div>
  );
}

export function HeatmapLoadingState() {
  return (
    <div className="flex flex-col items-center justify-center p-20 text-center rounded-lg bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] space-y-3 min-h-[450px]">
      <RefreshCw className="w-6 h-6 text-[var(--atlas-accent-primary)] animate-spin" />
      <span className="text-xs text-[var(--atlas-text-secondary)] font-medium">
        Calculating coherent market heatmap snapshot...
      </span>
    </div>
  );
}
