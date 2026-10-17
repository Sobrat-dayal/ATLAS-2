"use client";

import React from "react";
import { HeatmapCoverage, describeCoverageStatus, formatMarketCap } from "@/lib/markets/heatmaps";
import { ShieldCheck, AlertCircle, PieChart, Database } from "lucide-react";

interface HeatmapCoverageSummaryProps {
  coverage: HeatmapCoverage | null;
  weightUnit?: string | null;
  weightLabel?: string | null;
}

export function HeatmapCoverageSummary({
  coverage,
  weightUnit = "USD",
  weightLabel = "Market Cap",
}: HeatmapCoverageSummaryProps) {
  if (!coverage) return null;

  const statusDesc = describeCoverageStatus(coverage.coverage_status);

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-xs">
      <div className="flex flex-wrap items-center gap-4 sm:gap-6">
        <div className="flex items-center gap-2">
          <Database className="w-3.5 h-3.5 text-[var(--atlas-text-tertiary)]" />
          <span className="text-[var(--atlas-text-secondary)]">Universe:</span>
          <span className="font-semibold text-[var(--atlas-text-primary)] font-mono">
            {coverage.candidate_count}
          </span>
          <span className="text-[var(--atlas-text-tertiary)]">candidates</span>
        </div>

        <div className="flex items-center gap-2">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
          <span className="text-[var(--atlas-text-secondary)]">Qualified:</span>
          <span className="font-semibold text-emerald-400 font-mono">
            {coverage.qualified_count}
          </span>
          <span className="text-[var(--atlas-text-tertiary)]">
            ({((coverage.qualified_count / (coverage.candidate_count || 1)) * 100).toFixed(0)}%)
          </span>
        </div>

        {coverage.missing_returns > 0 && (
          <div className="flex items-center gap-1.5 text-amber-400">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Missing Returns:</span>
            <span className="font-mono font-semibold">{coverage.missing_returns}</span>
          </div>
        )}

        {coverage.missing_weights > 0 && (
          <div className="flex items-center gap-1.5 text-amber-400">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Missing Weights:</span>
            <span className="font-mono font-semibold">{coverage.missing_weights}</span>
          </div>
        )}

        {coverage.total_qualified_weight && (
          <div className="flex items-center gap-2">
            <PieChart className="w-3.5 h-3.5 text-[var(--atlas-text-tertiary)]" />
            <span className="text-[var(--atlas-text-secondary)]">{weightLabel}:</span>
            <span className="font-semibold text-[var(--atlas-text-primary)] font-mono">
              {formatMarketCap(coverage.total_qualified_weight, weightUnit || "USD")}
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        <span
          className={`px-2 py-0.5 rounded text-[10px] font-medium border ${statusDesc.badgeClass}`}
          title={statusDesc.description}
        >
          {statusDesc.label} Coverage
        </span>
      </div>
    </div>
  );
}
