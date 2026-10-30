"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import { AttributionBenchmarkSummaryDTO, AttributionRunDTO } from "@/lib/portfolios/attribution/types";
import { Check, CheckCircle2, Compass, Layers, ShieldCheck } from "lucide-react";

interface BenchmarkInspectorPanelProps {
  run: AttributionRunDTO;
  benchmarks: AttributionBenchmarkSummaryDTO[];
  selectedBenchmark: string;
  onSelectBenchmark: (id: string) => void;
  onApplyBenchmark: (id: string) => void;
  calculating: boolean;
}

export function BenchmarkInspectorPanel({
  run,
  benchmarks,
  selectedBenchmark,
  onSelectBenchmark,
  onApplyBenchmark,
  calculating,
}: BenchmarkInspectorPanelProps) {
  return (
    <div className="space-y-4">
      {/* Active Benchmark Summary Header */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Compass className="h-4 w-4 text-atlas-accent" />
              <h3 className="text-sm font-semibold text-atlas-text-primary">
                Active Benchmark: {run.benchmark_name} ({run.benchmark_id.replace("BENCHMARK_", "")})
              </h3>
            </div>
            <p className="mt-1 text-xs text-atlas-text-secondary">
              Point-in-time constituent snapshot with sector-level weighting and return series.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="rounded bg-atlas-surface-2 px-2 py-1 text-atlas-text-secondary">
              Return Basis: Total Return (Gross)
            </span>
            <span className="rounded bg-atlas-surface-2 px-2 py-1 text-atlas-text-secondary">
              Currency: {run.reporting_currency}
            </span>
          </div>
        </div>
      </div>

      {/* Benchmark Selection Grid */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {benchmarks.map((b) => {
          const isCurrentActive = run.benchmark_id === b.benchmark_id;
          const isSelected = selectedBenchmark === b.benchmark_id;

          return (
            <div
              key={b.benchmark_id}
              onClick={() => onSelectBenchmark(b.benchmark_id)}
              className={`cursor-pointer rounded border p-4 transition-all ${
                isSelected
                  ? "border-atlas-accent bg-atlas-accent/5 ring-1 ring-atlas-accent/40"
                  : "border-atlas-border-default/60 bg-atlas-surface-1 hover:border-atlas-border-default hover:bg-atlas-surface-2/40"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-1.5 font-bold text-atlas-text-primary">
                    <span>{b.symbol}</span>
                    {isCurrentActive && (
                      <span className="rounded bg-emerald-500/20 px-1 text-[10px] text-emerald-400 font-sans font-medium">
                        Active
                      </span>
                    )}
                  </div>
                  <div className="mt-0.5 text-xs font-medium text-atlas-text-secondary">
                    {b.name}
                  </div>
                </div>
                {isSelected && <Check className="h-4 w-4 text-atlas-accent" />}
              </div>

              <div className="mt-3 text-[11px] text-atlas-text-muted leading-relaxed line-clamp-2">
                {b.description}
              </div>

              <div className="mt-3 flex items-center justify-between border-t border-atlas-border-default/40 pt-2 text-[10px] text-atlas-text-muted font-mono">
                <span>{b.benchmark_type}</span>
                <span className="flex items-center gap-1 text-emerald-400">
                  <CheckCircle2 className="h-3 w-3" /> Constituents
                </span>
              </div>

              {isSelected && !isCurrentActive && (
                <div className="mt-3">
                  <Button
                    size="sm"
                    variant="primary"
                    disabled={calculating}
                    onClick={(e) => {
                      e.stopPropagation();
                      onApplyBenchmark(b.benchmark_id);
                    }}
                    className="w-full h-7 text-xs"
                  >
                    {calculating ? "Calculating..." : "Apply Benchmark"}
                  </Button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

