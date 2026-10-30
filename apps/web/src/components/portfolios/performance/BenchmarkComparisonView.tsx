"use client";

import React from "react";
import { formatRate } from "@/lib/portfolios/performance/formatting";
import {
  BenchmarkComparisonDTO,
  BenchmarkDefinitionDTO,
} from "@/lib/portfolios/performance/types";
import { AlertTriangle, Award, CheckCircle2, TrendingUp } from "lucide-react";

interface BenchmarkComparisonViewProps {
  comparison: BenchmarkComparisonDTO | null | undefined;
  benchmarks: BenchmarkDefinitionDTO[];
  selectedBenchmarkId: string;
  onSelectBenchmark: (id: string) => void;
}

export function BenchmarkComparisonView({
  comparison,
  benchmarks,
  selectedBenchmarkId,
  onSelectBenchmark,
}: BenchmarkComparisonViewProps) {
  const currentBenchDef = benchmarks.find((b) => b.benchmark_id === selectedBenchmarkId);

  return (
    <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-4 shadow-xs space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default/40 pb-3">
        <div>
          <h4 className="text-xs font-semibold text-atlas-text-primary">
            Market Benchmark Comparison & Relative Performance
          </h4>
          <p className="text-[11px] text-atlas-text-secondary">
            Arithmetic relative comparison against canonical institutional market indices.
          </p>
        </div>

        {/* Benchmark Selector */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-atlas-text-tertiary">Select Benchmark:</label>
          <select
            value={selectedBenchmarkId}
            onChange={(e) => onSelectBenchmark(e.target.value)}
            className="rounded-sm border border-atlas-border-default bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
          >
            <option value="NONE">None (Absolute Return Only)</option>
            {benchmarks.map((b) => (
              <option key={b.benchmark_id} value={b.benchmark_id}>
                {b.name} ({b.symbol}) - {b.return_basis}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!comparison || selectedBenchmarkId === "NONE" ? (
        <div className="rounded-sm border border-dashed border-atlas-border-default/60 p-6 text-center text-xs text-atlas-text-tertiary">
          Select a canonical benchmark from the dropdown above to display comparative performance metrics.
        </div>
      ) : (
        <div className="space-y-4">
          {/* Compliance Basis Warning Banner if applicable */}
          {comparison.warning && (
            <div className="flex items-start gap-2.5 rounded-sm border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-300">
              <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
              <div>
                <span className="font-semibold text-amber-200">Return Basis Notice: </span>
                {comparison.warning}
              </div>
            </div>
          )}

          {/* Head to Head Comparison Cards */}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {/* Portfolio Card */}
            <div className="rounded-sm border border-atlas-border-default/60 bg-atlas-surface-2/40 p-3">
              <div className="text-[11px] text-atlas-text-tertiary">Portfolio TWR Return</div>
              <div className="mt-1 text-xl font-bold font-mono text-atlas-accent">
                {formatRate(comparison.portfolio_return)}
              </div>
              <div className="mt-1 text-[11px] text-atlas-text-secondary">
                Rebased End: <span className="font-mono text-atlas-text-primary">{comparison.rebased_portfolio_index_end}</span>
              </div>
            </div>

            {/* Benchmark Card */}
            <div className="rounded-sm border border-atlas-border-default/60 bg-atlas-surface-2/40 p-3">
              <div className="text-[11px] text-atlas-text-tertiary">
                {comparison.benchmark_name} ({comparison.return_basis})
              </div>
              <div className="mt-1 text-xl font-bold font-mono text-amber-400">
                {formatRate(comparison.benchmark_return)}
              </div>
              <div className="mt-1 text-[11px] text-atlas-text-secondary">
                Rebased End: <span className="font-mono text-atlas-text-primary">{comparison.rebased_benchmark_index_end}</span>
              </div>
            </div>

            {/* Arithmetic Difference / Alpha Card */}
            {(() => {
              const diff = parseFloat(comparison.arithmetic_difference);
              const isPositive = diff > 0;
              return (
                <div className="rounded-sm border border-atlas-border-default/60 bg-atlas-surface-2/40 p-3">
                  <div className="text-[11px] text-atlas-text-tertiary">Relative Performance (&Delta;R)</div>
                  <div
                    className={`mt-1 text-xl font-bold font-mono ${
                      isPositive
                        ? "text-emerald-400"
                        : diff < 0
                        ? "text-rose-400"
                        : "text-atlas-text-primary"
                    }`}
                  >
                    {isPositive ? `+${formatRate(diff, { showSign: false })}` : formatRate(diff)}
                  </div>
                  <div className="mt-1 text-[11px] text-atlas-text-secondary">
                    {isPositive ? "Outperformed benchmark" : "Underperformed benchmark"}
                  </div>
                </div>
              );
            })()}
          </div>

          {/* Benchmark Details & Methodology Footer */}
          {currentBenchDef && (
            <div className="rounded-sm border border-atlas-border-default/40 bg-atlas-surface-1 p-3 text-xs text-atlas-text-secondary space-y-1">
              <div className="font-semibold text-atlas-text-primary flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                Benchmark Identity: {currentBenchDef.name} ({currentBenchDef.symbol})
              </div>
              <p className="text-[11px] text-atlas-text-tertiary">
                {currentBenchDef.description}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

