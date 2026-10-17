"use client";

import React from "react";
import { CrossAssetMode } from "@/lib/markets/cross-asset";
import { BarChart3, Clock, Compass } from "lucide-react";

interface CrossAssetModeSelectorProps {
  mode: CrossAssetMode;
  onSelectMode: (mode: CrossAssetMode) => void;
  isLoading: boolean;
}

export function CrossAssetModeSelector({
  mode,
  onSelectMode,
  isLoading,
}: CrossAssetModeSelectorProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-[11px] font-medium text-[var(--atlas-text-secondary)] uppercase tracking-wider flex items-center gap-1.5">
        <Compass className="w-3.5 h-3.5 text-blue-400" />
        <span>Analytical Mode</span>
      </span>

      <div
        role="tablist"
        aria-label="Analytical comparison mode selector"
        className="inline-flex p-0.5 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]"
      >
        <button
          type="button"
          role="tab"
          aria-selected={mode === "native_overview"}
          onClick={() => onSelectMode("native_overview")}
          disabled={isLoading}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded transition-colors ${
            mode === "native_overview"
              ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] shadow-sm border border-[var(--atlas-border-subtle)]"
              : "text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-secondary)]"
          }`}
          title="Shows each asset class adhering strictly to its native financial quotation convention (yields in bps, rates in pair units, futures in settlement points)."
        >
          <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Native Overview</span>
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={mode === "aligned_performance"}
          onClick={() => onSelectMode("aligned_performance")}
          disabled={isLoading}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded transition-colors ${
            mode === "aligned_performance"
              ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] shadow-sm border border-[var(--atlas-border-subtle)]"
              : "text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-secondary)]"
          }`}
          title="Strictly synchronized price return comparison across a common UTC window with zero look-ahead bias. Excludes non-price series like bond yields."
        >
          <Clock className="w-3.5 h-3.5 text-emerald-400" />
          <span>Aligned Performance</span>
        </button>
      </div>
    </div>
  );
}
