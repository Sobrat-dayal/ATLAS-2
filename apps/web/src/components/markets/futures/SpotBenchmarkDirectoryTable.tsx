"use client";

import React from "react";
import { AlertCircle, TrendingUp } from "lucide-react";
import {
  CommoditySpotBenchmarkView,
  formatFuturesPrice,
  formatPriceChange,
  formatPriceChangeClass,
} from "@/lib/markets/futures";

export interface SpotBenchmarkDirectoryTableProps {
  benchmarks: CommoditySpotBenchmarkView[];
  isLoading: boolean;
}

export function SpotBenchmarkDirectoryTable({
  benchmarks,
  isLoading,
}: SpotBenchmarkDirectoryTableProps) {
  if (isLoading && benchmarks.length === 0) {
    return (
      <div className="rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] p-4 animate-pulse">
        <div className="h-6 bg-[var(--atlas-surface-subtle)] rounded w-1/4 mb-4" />
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-10 bg-[var(--atlas-surface-subtle)] rounded w-full" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Information Banner */}
      <div className="p-3 rounded bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] flex items-start gap-2.5 text-xs text-[var(--atlas-text-secondary)]">
        <AlertCircle className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" aria-hidden="true" />
        <div>
          <span className="font-semibold text-[var(--atlas-text-primary)]">
            Physical Spot Benchmarks vs Exchange Futures:
          </span>{" "}
          Physical commodity benchmarks represent assessed cash-market transfer prices at specific pipeline or physical terminal delivery locations. They are distinct financial instruments from exchange-traded Futures contracts and are never substituted for or synthesized from expiring futures contracts.
        </div>
      </div>

      {/* Table */}
      <div className="rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)] select-none">
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Spot Benchmark
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Underlying Commodity
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Assessment Location
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Methodology &amp; Standard
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-right">
                  Latest Price
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-right">
                  Change
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  As-Of Date
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Provider
                </th>
              </tr>
            </thead>
            <tbody>
              {benchmarks.map((b) => {
                const priceFormatted = formatFuturesPrice(
                  b.latest_price,
                  b.quote_unit,
                  b.currency
                );
                const changeFormatted = formatPriceChange(
                  b.change_absolute,
                  b.change_percent,
                  b.quote_unit
                );
                const changeClass = formatPriceChangeClass(b.change_absolute);

                return (
                  <tr
                    key={b.benchmark_entity_id}
                    className="hover:bg-[var(--atlas-surface-hover)] border-b border-[var(--atlas-border-subtle)] transition-colors"
                  >
                    <td className="px-3 py-2.5 font-medium text-[var(--atlas-text-primary)]">
                      <div className="flex items-center gap-1.5">
                        <TrendingUp className="h-3.5 w-3.5 text-emerald-400 shrink-0" aria-hidden="true" />
                        <span>{b.name}</span>
                      </div>
                      <div className="text-[10px] text-[var(--atlas-text-tertiary)] pl-5 truncate max-w-xs">
                        {b.grade}
                      </div>
                    </td>

                    <td className="px-3 py-2.5">
                      <span className="text-[var(--atlas-text-secondary)] font-medium">
                        {b.commodity_name}
                      </span>
                    </td>

                    <td className="px-3 py-2.5 font-mono text-[var(--atlas-text-secondary)]">
                      {b.location}
                    </td>

                    <td className="px-3 py-2.5 text-[var(--atlas-text-tertiary)] max-w-xs truncate" title={b.assessment_methodology}>
                      {b.assessment_methodology}
                    </td>

                    <td className="px-3 py-2.5 font-mono font-bold text-right text-[var(--atlas-text-primary)]">
                      {priceFormatted}
                    </td>

                    <td className={`px-3 py-2.5 font-mono text-right font-medium ${changeClass}`}>
                      {changeFormatted}
                    </td>

                    <td className="px-3 py-2.5 font-mono text-[var(--atlas-text-secondary)]">
                      {b.as_of_date}
                    </td>

                    <td className="px-3 py-2.5 font-mono text-[10px] text-[var(--atlas-text-secondary)]">
                      <span className="px-1.5 py-0.5 rounded bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)]">
                        {b.provider}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="p-3 border-t border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)] text-xs text-[var(--atlas-text-secondary)]">
          Total physical spot benchmarks: <span className="font-mono font-medium text-[var(--atlas-text-primary)]">{benchmarks.length}</span>
        </div>
      </div>
    </div>
  );
}
