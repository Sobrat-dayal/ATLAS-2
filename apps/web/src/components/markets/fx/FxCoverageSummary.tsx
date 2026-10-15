"use client";

import React from "react";
import { FxPairCoverageSummary } from "@/lib/markets/fx";
import { CheckCircle2, DollarSign, Layers, ShieldCheck, TrendingUp } from "lucide-react";

export interface FxCoverageSummaryProps {
  coverage?: FxPairCoverageSummary;
}

export function FxCoverageSummary({ coverage }: FxCoverageSummaryProps) {
  if (!coverage) return null;

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3 sm:p-4 mb-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[var(--atlas-border-subtle)] pb-2.5 mb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" aria-hidden="true" />
          <span className="text-xs font-semibold uppercase tracking-wider text-[var(--atlas-text-secondary)]">
            FX Coverage & Market Data Status
          </span>
        </div>
        <div className="text-[11px] font-mono text-[var(--atlas-text-tertiary)] flex items-center gap-2">
          <span>Scope: {coverage.scope}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Total Pairs */}
        <div className="bg-[var(--atlas-surface-card)]/60 border border-[var(--atlas-border-subtle)]/70 rounded p-2.5">
          <div className="flex items-center gap-1.5 text-[11px] text-[var(--atlas-text-secondary)] mb-1">
            <Layers className="h-3.5 w-3.5 text-sky-400" aria-hidden="true" />
            <span>Configured Pairs</span>
          </div>
          <div className="text-base sm:text-lg font-bold font-mono text-[var(--atlas-text-primary)]">
            {coverage.total_pairs}
          </div>
        </div>

        {/* Base Currencies */}
        <div className="bg-[var(--atlas-surface-card)]/60 border border-[var(--atlas-border-subtle)]/70 rounded p-2.5">
          <div className="flex items-center gap-1.5 text-[11px] text-[var(--atlas-text-secondary)] mb-1">
            <DollarSign className="h-3.5 w-3.5 text-indigo-400" aria-hidden="true" />
            <span>Base Currencies</span>
          </div>
          <div className="text-base sm:text-lg font-bold font-mono text-[var(--atlas-text-primary)]">
            {coverage.base_currencies_count}
          </div>
        </div>

        {/* Quote Currencies */}
        <div className="bg-[var(--atlas-surface-card)]/60 border border-[var(--atlas-border-subtle)]/70 rounded p-2.5">
          <div className="flex items-center gap-1.5 text-[11px] text-[var(--atlas-text-secondary)] mb-1">
            <DollarSign className="h-3.5 w-3.5 text-purple-400" aria-hidden="true" />
            <span>Quote Currencies</span>
          </div>
          <div className="text-base sm:text-lg font-bold font-mono text-[var(--atlas-text-primary)]">
            {coverage.quote_currencies_count}
          </div>
        </div>

        {/* Rates Available */}
        <div className="bg-[var(--atlas-surface-card)]/60 border border-[var(--atlas-border-subtle)]/70 rounded p-2.5">
          <div className="flex items-center gap-1.5 text-[11px] text-[var(--atlas-text-secondary)] mb-1">
            <TrendingUp className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>Rates Observed</span>
          </div>
          <div className="text-base sm:text-lg font-bold font-mono text-emerald-400">
            {coverage.pairs_with_quotes}
          </div>
        </div>

        {/* Bid/Ask Available */}
        <div className="bg-[var(--atlas-surface-card)]/60 border border-[var(--atlas-border-subtle)]/70 rounded p-2.5">
          <div className="flex items-center gap-1.5 text-[11px] text-[var(--atlas-text-secondary)] mb-1">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>Bid/Ask Active</span>
          </div>
          <div className="text-base sm:text-lg font-bold font-mono text-emerald-400">
            {coverage.pairs_with_bid_ask}
          </div>
        </div>

        {/* Spread Computed */}
        <div className="bg-[var(--atlas-surface-card)]/60 border border-[var(--atlas-border-subtle)]/70 rounded p-2.5">
          <div className="flex items-center gap-1.5 text-[11px] text-[var(--atlas-text-secondary)] mb-1">
            <CheckCircle2 className="h-3.5 w-3.5 text-amber-400" aria-hidden="true" />
            <span>Spread Computed</span>
          </div>
          <div className="text-base sm:text-lg font-bold font-mono text-amber-400">
            {coverage.pairs_with_spread}
          </div>
        </div>
      </div>
    </div>
  );
}
