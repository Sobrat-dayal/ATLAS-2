"use client";

import React from "react";
import { Building2, Coins, FileCheck2, Percent } from "lucide-react";
import { BondCoverageSummary as CoverageSummaryType } from "@/lib/markets/bonds";

export interface BondCoverageSummaryProps {
  coverage: CoverageSummaryType | null | undefined;
  isLoading: boolean;
}

export function BondCoverageSummary({
  coverage,
  isLoading,
}: BondCoverageSummaryProps) {
  if (isLoading && !coverage) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-20 bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded p-3 animate-pulse"
          />
        ))}
      </div>
    );
  }

  const totalBonds = coverage?.total_bonds ?? 0;
  const totalIssuers = coverage?.total_issuers ?? 0;
  const withPrices = coverage?.bonds_with_prices ?? 0;
  const withYields = coverage?.bonds_with_yields ?? 0;
  const currencies = coverage?.currencies ?? ["USD", "EUR", "GBP", "JPY"];

  return (
    <section aria-label="Bond market coverage summary" className="mb-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Card 1: Total Bonds */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[var(--atlas-text-tertiary)]">
            <span className="text-xs font-medium">Bonds in Catalog</span>
            <FileCheck2 className="h-4 w-4 text-emerald-400" aria-hidden="true" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl sm:text-2xl font-bold font-mono tracking-tight text-[var(--atlas-text-primary)]">
              {totalBonds}
            </span>
            <span className="text-[11px] text-[var(--atlas-text-tertiary)]">Securities</span>
          </div>
        </div>

        {/* Card 2: Legal Issuers */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[var(--atlas-text-tertiary)]">
            <span className="text-xs font-medium">Verified Issuers</span>
            <Building2 className="h-4 w-4 text-blue-400" aria-hidden="true" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl sm:text-2xl font-bold font-mono tracking-tight text-[var(--atlas-text-primary)]">
              {totalIssuers}
            </span>
            <span className="text-[11px] text-[var(--atlas-text-tertiary)]">Sovereign &amp; Corp</span>
          </div>
        </div>

        {/* Card 3: Price Observations */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[var(--atlas-text-tertiary)]">
            <span className="text-xs font-medium">Clean / Dirty Prices</span>
            <Coins className="h-4 w-4 text-amber-400" aria-hidden="true" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl sm:text-2xl font-bold font-mono tracking-tight text-[var(--atlas-text-primary)]">
              {withPrices}
            </span>
            <span className="text-[11px] text-[var(--atlas-text-tertiary)]">Active Quotes</span>
          </div>
        </div>

        {/* Card 4: Yields Available */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-[var(--atlas-text-tertiary)]">
            <span className="text-xs font-medium">Yield Observations</span>
            <Percent className="h-4 w-4 text-cyan-400" aria-hidden="true" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl sm:text-2xl font-bold font-mono tracking-tight text-[var(--atlas-text-primary)]">
              {withYields}
            </span>
            <span className="text-[11px] text-[var(--atlas-text-tertiary)]">YTM &amp; Discount</span>
          </div>
        </div>
      </div>

      {currencies.length > 0 && (
        <div className="flex items-center gap-1.5 mt-2.5 text-xs text-[var(--atlas-text-tertiary)]">
          <span className="font-medium">Active Currencies:</span>
          <div className="flex items-center gap-1">
            {currencies.map((c) => (
              <span
                key={c}
                className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-800 text-zinc-300 border border-zinc-700/50"
              >
                {c}
              </span>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
