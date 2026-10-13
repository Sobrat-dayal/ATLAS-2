"use client";

import React from "react";
import { CheckCircle2, Database, HelpCircle, Server } from "lucide-react";
import { MarketsOverviewCoverage } from "@/lib/markets/types";
import { formatMarketTimestamp } from "@/lib/markets/formatting";

export interface MarketsCoverageSummaryProps {
  coverage?: MarketsOverviewCoverage | null;
  generatedAt?: string | null;
  scope?: string | null;
}

export function MarketsCoverageSummary({
  coverage,
  generatedAt,
  scope,
}: MarketsCoverageSummaryProps) {
  if (!coverage) return null;

  return (
    <div
      role="region"
      aria-label="Market coverage statistics"
      className="flex flex-wrap items-center justify-between gap-3 p-2.5 rounded-lg border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] text-xs mb-4"
    >
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-1.5 text-[var(--atlas-text-secondary)]">
          <Database className="h-3.5 w-3.5 text-zinc-400" aria-hidden="true" />
          <span>Configured:</span>
          <span className="font-mono font-semibold text-[var(--atlas-text-primary)]">
            {coverage.configured_count}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-[var(--atlas-text-secondary)]">
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
          <span>Available:</span>
          <span className="font-mono font-semibold text-emerald-400">
            {coverage.available_count}
          </span>
        </div>

        {coverage.unavailable_count > 0 && (
          <div className="flex items-center gap-1.5 text-[var(--atlas-text-secondary)]">
            <HelpCircle className="h-3.5 w-3.5 text-amber-400" aria-hidden="true" />
            <span>Unavailable:</span>
            <span className="font-mono font-semibold text-amber-400">
              {coverage.unavailable_count}
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3 text-[11px] text-[var(--atlas-text-tertiary)] font-mono">
        {scope && (
          <span className="hidden md:inline-flex items-center gap-1">
            <Server className="h-3 w-3" aria-hidden="true" />
            Scope: {scope}
          </span>
        )}
        {generatedAt && (
          <span>Updated: {formatMarketTimestamp(generatedAt)} UTC</span>
        )}
      </div>
    </div>
  );
}
