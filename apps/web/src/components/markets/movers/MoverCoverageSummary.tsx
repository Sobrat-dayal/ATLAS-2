"use client";

import React, { useState } from "react";
import { AlertCircle, ChevronDown, ChevronUp, Info, ShieldCheck } from "lucide-react";
import {
  formatCoverageStatus,
  formatExclusionReason,
  MoverCoverage,
} from "@/lib/markets/movers";

export interface MoverCoverageSummaryProps {
  coverage: MoverCoverage | null;
  universeDisplayName?: string;
  metricLabel?: string;
}

export function MoverCoverageSummary({
  coverage,
  universeDisplayName,
}: MoverCoverageSummaryProps) {
  const [showExclusions, setShowExclusions] = useState(false);

  if (!coverage) return null;

  const statusInfo = formatCoverageStatus(coverage.coverage_status);
  const exclusionEntries = Object.entries(coverage.exclusion_reasons || {});
  const hasExclusions = coverage.excluded_count > 0 && exclusionEntries.length > 0;

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-lg p-3 my-3">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs">
          {/* Status Badge */}
          <span
            className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-medium border ${statusInfo.badgeClass}`}
          >
            <ShieldCheck className="h-3.5 w-3.5" />
            {statusInfo.label}
          </span>

          {/* Counts */}
          <div className="flex items-center gap-1.5 text-[var(--atlas-text-secondary)]">
            <span className="text-[var(--atlas-text-primary)] font-semibold font-mono">
              {coverage.qualified_count}
            </span>
            <span>of</span>
            <span className="text-[var(--atlas-text-primary)] font-semibold font-mono">
              {coverage.candidate_count}
            </span>
            <span>candidates qualified</span>
          </div>

          {coverage.excluded_count > 0 && (
            <div className="flex items-center gap-1 text-amber-400">
              <span className="font-mono font-semibold">
                ({coverage.excluded_count} excluded)
              </span>
            </div>
          )}

          {universeDisplayName && (
            <span className="hidden lg:inline text-[var(--atlas-text-tertiary)] border-l border-zinc-700/60 pl-3">
              Scope: {universeDisplayName}
            </span>
          )}
        </div>

        {hasExclusions && (
          <button
            type="button"
            onClick={() => setShowExclusions(!showExclusions)}
            className="inline-flex items-center gap-1 text-xs text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)] self-start md:self-auto transition-colors"
            aria-expanded={showExclusions}
          >
            <Info className="h-3.5 w-3.5" />
            <span>Exclusion Details</span>
            {showExclusions ? (
              <ChevronUp className="h-3.5 w-3.5" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5" />
            )}
          </button>
        )}
      </div>

      {/* Exclusion Details Dropdown/Drawer */}
      {showExclusions && hasExclusions && (
        <div className="mt-3 pt-3 border-t border-[var(--atlas-border-subtle)] text-xs">
          <div className="flex items-center gap-1.5 text-zinc-400 font-medium mb-2">
            <AlertCircle className="h-3.5 w-3.5 text-amber-400" />
            <span>Exclusion Breakdown (Data Quality &amp; Qualification Pipeline):</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {exclusionEntries.map(([reason, count]) => (
              <div
                key={reason}
                className="flex items-center justify-between px-2.5 py-1.5 rounded bg-zinc-900/60 border border-zinc-800 text-[11px]"
              >
                <span className="text-zinc-300">{formatExclusionReason(reason)}</span>
                <span className="font-mono font-semibold text-amber-400 ml-2">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
