"use client";

import React from "react";
import { CrossAssetMode, CrossAssetWindow } from "@/lib/markets/cross-asset";
import { Calendar } from "lucide-react";

interface CrossAssetWindowSelectorProps {
  window: CrossAssetWindow;
  onSelectWindow: (window: CrossAssetWindow) => void;
  mode: CrossAssetMode;
  isLoading: boolean;
}

export function CrossAssetWindowSelector({
  window,
  onSelectWindow,
  mode,
  isLoading,
}: CrossAssetWindowSelectorProps) {
  const isAligned = mode === "aligned_performance";

  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-[11px] font-medium text-[var(--atlas-text-secondary)] uppercase tracking-wider flex items-center gap-1.5">
        <Calendar className="w-3.5 h-3.5 text-emerald-400" />
        <span>Comparison Period</span>
        {!isAligned && (
          <span className="text-[10px] text-[var(--atlas-text-tertiary)] lowercase font-normal">
            (aligned mode only)
          </span>
        )}
      </span>

      <div
        role="tablist"
        aria-label="Comparison window selector"
        className={`inline-flex p-0.5 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] ${
          !isAligned ? "opacity-60 pointer-events-none" : ""
        }`}
      >
        <button
          type="button"
          role="tab"
          aria-selected={window === "last_24h"}
          onClick={() => onSelectWindow("last_24h")}
          disabled={isLoading || !isAligned}
          className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
            window === "last_24h"
              ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] shadow-sm border border-[var(--atlas-border-subtle)] font-mono"
              : "text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-secondary)]"
          }`}
        >
          24H
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={window === "last_7d"}
          onClick={() => onSelectWindow("last_7d")}
          disabled={isLoading || !isAligned}
          className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
            window === "last_7d"
              ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] shadow-sm border border-[var(--atlas-border-subtle)] font-mono"
              : "text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-secondary)]"
          }`}
        >
          7D
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={window === "last_30d"}
          onClick={() => onSelectWindow("last_30d")}
          disabled={isLoading || !isAligned}
          className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
            window === "last_30d"
              ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] shadow-sm border border-[var(--atlas-border-subtle)] font-mono"
              : "text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-secondary)]"
          }`}
        >
          30D
        </button>
      </div>
    </div>
  );
}
