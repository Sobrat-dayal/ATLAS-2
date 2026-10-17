"use client";

import React from "react";
import { RefreshCw, Activity, HelpCircle } from "lucide-react";
import { formatIsoTime } from "@/lib/markets/cross-asset";

interface CrossAssetHeaderProps {
  universeName?: string;
  calculatedAt?: string;
  snapshotId?: string;
  isLoading: boolean;
  isRefetching: boolean;
  onRefresh: () => void;
  showMethodology: boolean;
  onToggleMethodology: () => void;
}

export function CrossAssetHeader({
  universeName = "Global Macro Cross-Asset Universe",
  calculatedAt,
  snapshotId,
  isLoading,
  isRefetching,
  onRefresh,
  showMethodology,
  onToggleMethodology,
}: CrossAssetHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[var(--atlas-border-subtle)]">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <h1 className="text-xl font-bold tracking-tight text-[var(--atlas-text-primary)]">
            Cross-Asset Markets
          </h1>
          <span className="px-2 py-0.5 text-[10px] font-mono uppercase rounded bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-secondary)] border border-[var(--atlas-border-subtle)]">
            Stage 65
          </span>
          <span className="px-2 py-0.5 text-[10px] font-mono uppercase rounded bg-indigo-950/80 text-indigo-400 border border-indigo-800/40">
            Multi-Asset
          </span>
        </div>
        <p className="text-xs text-[var(--atlas-text-secondary)]">
          Compare qualified observations across supported financial markets with explicit native conventions and common-window temporal alignment in {universeName}.
        </p>
      </div>

      <div className="flex items-center gap-2.5">
        {calculatedAt && (
          <div
            className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-[11px] font-mono text-[var(--atlas-text-tertiary)]"
            title={snapshotId ? `Snapshot ID: ${snapshotId}` : undefined}
          >
            <Activity className="w-3.5 h-3.5 text-emerald-500 animate-pulse" />
            <span>As Of: {formatIsoTime(calculatedAt)}</span>
          </div>
        )}

        <button
          type="button"
          onClick={onToggleMethodology}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
            showMethodology
              ? "bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] border-[var(--atlas-border-focus)]"
              : "bg-[var(--atlas-surface-card)] text-[var(--atlas-text-secondary)] border-[var(--atlas-border-subtle)] hover:text-[var(--atlas-text-primary)]"
          }`}
          title="Toggle alignment and qualification methodology disclosures"
        >
          <HelpCircle className="w-3.5 h-3.5" />
          <span>Methodology</span>
        </button>

        <button
          type="button"
          onClick={onRefresh}
          disabled={isLoading || isRefetching}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-[var(--atlas-surface-card)] text-[var(--atlas-text-secondary)] border border-[var(--atlas-border-subtle)] hover:text-[var(--atlas-text-primary)] hover:border-[var(--atlas-border-base)] transition-colors disabled:opacity-50"
          title="Refresh multi-asset market snapshot"
        >
          <RefreshCw
            className={`w-3.5 h-3.5 ${isRefetching ? "animate-spin text-emerald-400" : ""}`}
          />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>
    </div>
  );
}
