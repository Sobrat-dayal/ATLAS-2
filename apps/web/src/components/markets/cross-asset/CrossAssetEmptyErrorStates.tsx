"use client";

import React from "react";
import { AlertTriangle, Compass, RefreshCw } from "lucide-react";

export function CrossAssetLoadingSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="h-20 bg-[var(--atlas-surface-card)] rounded border border-[var(--atlas-border-subtle)]" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        <div className="h-44 bg-[var(--atlas-surface-card)] rounded border border-[var(--atlas-border-subtle)]" />
        <div className="h-44 bg-[var(--atlas-surface-card)] rounded border border-[var(--atlas-border-subtle)]" />
        <div className="h-44 bg-[var(--atlas-surface-card)] rounded border border-[var(--atlas-border-subtle)]" />
      </div>
      <div className="h-64 bg-[var(--atlas-surface-card)] rounded border border-[var(--atlas-border-subtle)]" />
    </div>
  );
}

interface CrossAssetErrorStateProps {
  error: Error | null;
  onRetry: () => void;
}

export function CrossAssetErrorState({ error, onRetry }: CrossAssetErrorStateProps) {
  return (
    <div className="p-8 text-center rounded bg-[var(--atlas-surface-card)] border border-rose-900/40 text-xs space-y-3">
      <div className="w-10 h-10 rounded-full bg-rose-950/60 border border-rose-800/60 flex items-center justify-center mx-auto text-rose-400">
        <AlertTriangle className="w-5 h-5" />
      </div>
      <div className="space-y-1">
        <h3 className="font-semibold text-sm text-[var(--atlas-text-primary)]">
          Cross-Asset Data Retrieval Error
        </h3>
        <p className="text-[var(--atlas-text-secondary)] max-w-md mx-auto text-xs">
          {error?.message || "Failed to load multi-asset observations from the canonical market feed."}
        </p>
      </div>
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] hover:border-[var(--atlas-border-focus)] transition-colors text-xs font-medium"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        <span>Retry Connection</span>
      </button>
    </div>
  );
}

export function CrossAssetEmptyState() {
  return (
    <div className="p-8 text-center rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-xs space-y-2">
      <div className="w-10 h-10 rounded-full bg-[var(--atlas-surface-elevated)] border border-[var(--atlas-border-subtle)] flex items-center justify-center mx-auto text-[var(--atlas-text-tertiary)]">
        <Compass className="w-5 h-5" />
      </div>
      <h3 className="font-semibold text-sm text-[var(--atlas-text-primary)]">
        No Cross-Asset Observations Available
      </h3>
      <p className="text-[var(--atlas-text-secondary)] max-w-md mx-auto text-xs">
        No canonical instruments qualified under the selected universe and alignment criteria.
      </p>
    </div>
  );
}
