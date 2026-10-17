"use client";

import React from "react";
import { RefreshCw, Activity, Layers } from "lucide-react";
import { formatTimestamp } from "@/lib/markets/heatmaps";

interface HeatmapsHeaderProps {
  universeName?: string;
  assetClass?: string;
  calculatedAt?: string;
  isLoading: boolean;
  isRefetching: boolean;
  onRefresh: () => void;
  showTable: boolean;
  onToggleTable: () => void;
}

export function HeatmapsHeader({
  universeName = "Covered US Equities",
  assetClass = "equity",
  calculatedAt,
  isLoading,
  isRefetching,
  onRefresh,
  showTable,
  onToggleTable,
}: HeatmapsHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[var(--atlas-border-subtle)]">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <h1 className="text-xl font-bold tracking-tight text-[var(--atlas-text-primary)]">
            Market Heatmaps
          </h1>
          <span className="px-2 py-0.5 text-[10px] font-mono uppercase rounded bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-secondary)] border border-[var(--atlas-border-subtle)]">
            Stage 64
          </span>
          <span className="px-2 py-0.5 text-[10px] font-mono uppercase rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/40">
            {assetClass}
          </span>
        </div>
        <p className="text-xs text-[var(--atlas-text-secondary)]">
          Institutional market visualization, sector & industry treemaps, and real-time market intelligence across {universeName}.
        </p>
      </div>

      <div className="flex items-center gap-3">
        {calculatedAt && (
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-[11px] font-mono text-[var(--atlas-text-tertiary)]">
            <Activity className="w-3.5 h-3.5 text-emerald-500 animate-pulse" />
            <span>Snapshot: {formatTimestamp(calculatedAt)}</span>
          </div>
        )}

        <button
          type="button"
          onClick={onToggleTable}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
            showTable
              ? "bg-[var(--atlas-accent-primary)] text-white border-transparent"
              : "bg-[var(--atlas-surface-card)] text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] border-[var(--atlas-border-subtle)]"
          }`}
          title="Toggle nonvisual accessible table view"
        >
          <Layers className="w-3.5 h-3.5" />
          <span>{showTable ? "Hide Table" : "Data Table"}</span>
        </button>

        <button
          type="button"
          onClick={onRefresh}
          disabled={isLoading || isRefetching}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] transition-colors disabled:opacity-50"
          title="Refresh calculation snapshot"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>
    </div>
  );
}
