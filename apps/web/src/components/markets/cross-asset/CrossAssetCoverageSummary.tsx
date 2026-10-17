"use client";

import React from "react";
import {
  CrossAssetCoverage,
  CrossAssetMode,
  CrossAssetWindow,
  formatIsoTime,
} from "@/lib/markets/cross-asset";
import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

interface CrossAssetCoverageSummaryProps {
  coverage: CrossAssetCoverage | null;
  mode: CrossAssetMode;
  window: CrossAssetWindow;
  requestedStart?: string;
  requestedEnd?: string;
}

export function CrossAssetCoverageSummary({
  coverage,
  mode,
  window,
  requestedStart,
  requestedEnd,
}: CrossAssetCoverageSummaryProps) {
  if (!coverage) return null;

  const isAligned = mode === "aligned_performance";

  const getStatusBadge = () => {
    switch (coverage.completeness_status) {
      case "COMPLETE_FOR_DEFINED_SET":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Complete for Defined Set</span>
          </span>
        );
      case "PARTIAL":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-amber-950/60 text-amber-400 border border-amber-800/40">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Partial Qualified Coverage</span>
          </span>
        );
      case "DEGRADED":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-orange-950/60 text-orange-400 border border-orange-800/40">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Degraded Coverage</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-rose-950/60 text-rose-400 border border-rose-800/40">
            <XCircle className="w-3.5 h-3.5" />
            <span>Unavailable</span>
          </span>
        );
    }
  };

  return (
    <div className="p-3.5 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
      <div className="flex flex-wrap items-center gap-3">
        {getStatusBadge()}

        <div className="flex items-center gap-2 text-[var(--atlas-text-secondary)] font-mono">
          <span>
            Universe: <strong className="text-[var(--atlas-text-primary)]">{coverage.requested_members}</strong>
          </span>
          <span className="text-[var(--atlas-border-subtle)]">|</span>
          <span>
            Evaluated: <strong className="text-[var(--atlas-text-primary)]">{coverage.evaluated_members}</strong>
          </span>
          <span className="text-[var(--atlas-border-subtle)]">|</span>
          <span>
            {isAligned ? "Comparable: " : "Reporting: "}
            <strong className="text-emerald-400">{coverage.qualified_members}</strong>
          </span>
          {coverage.excluded_members > 0 && (
            <>
              <span className="text-[var(--atlas-border-subtle)]">|</span>
              <span>
                Excluded: <strong className="text-amber-400">{coverage.excluded_members}</strong>
              </span>
            </>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {isAligned && requestedStart && requestedEnd && (
          <div className="text-[11px] font-mono text-[var(--atlas-text-tertiary)] bg-[var(--atlas-surface-elevated)] px-2 py-1 rounded border border-[var(--atlas-border-subtle)]">
            UTC Window ({window}): {formatIsoTime(requestedStart)} → {formatIsoTime(requestedEnd)}
          </div>
        )}

        {Object.entries(coverage.exclusions_by_reason || {}).map(([reason, count]) => (
          <span
            key={reason}
            className="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-800/80 text-zinc-400 border border-zinc-700/50"
            title={`Exclusion reason: ${reason}`}
          >
            {count} {reason}
          </span>
        ))}
      </div>
    </div>
  );
}
