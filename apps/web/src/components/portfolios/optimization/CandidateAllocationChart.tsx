"use client";

import React, { useMemo, useState } from "react";
import { CurrentVsCandidateItemDTO } from "@/lib/portfolios/optimization/types";
import { formatPercent, formatWeightPercent } from "@/lib/portfolios/optimization/formatting";
import { Layers, PieChart } from "lucide-react";

interface CandidateAllocationChartProps {
  comparisons: CurrentVsCandidateItemDTO[];
  cashWeight?: string;
  baseCurrency?: string;
}

interface AggregatedCategory {
  category: string;
  currentWeight: number;
  candidateWeight: number;
  delta: number;
  symbols: string[];
}

export function CandidateAllocationChart({
  comparisons,
  cashWeight = "0.0",
}: CandidateAllocationChartProps) {
  const [viewMode, setViewMode] = useState<"category" | "security">("category");

  // Aggregate comparisons by category
  const categories = useMemo(() => {
    const map = new Map<string, AggregatedCategory>();

    comparisons.forEach((item) => {
      const cat = item.category_label || item.category_id || "Unclassified";
      const cur = parseFloat(item.current_weight) || 0;
      const cand = parseFloat(item.candidate_weight) || 0;

      if (!map.has(cat)) {
        map.set(cat, {
          category: cat,
          currentWeight: 0,
          candidateWeight: 0,
          delta: 0,
          symbols: [],
        });
      }
      const entry = map.get(cat)!;
      entry.currentWeight += cur;
      entry.candidateWeight += cand;
      entry.delta = entry.candidateWeight - entry.currentWeight;
      entry.symbols.push(item.symbol);
    });

    // Add cash if present
    const cashVal = parseFloat(cashWeight) || 0;
    if (cashVal > 0.0001 && !map.has("Cash & Equivalents")) {
      map.set("Cash & Equivalents", {
        category: "Cash & Equivalents",
        currentWeight: 0,
        candidateWeight: cashVal,
        delta: cashVal,
        symbols: ["CASH"],
      });
    }

    return Array.from(map.values()).sort(
      (a, b) => Math.max(b.candidateWeight, b.currentWeight) - Math.max(a.candidateWeight, a.currentWeight)
    );
  }, [comparisons, cashWeight]);

  // Max weight for scaling bars
  const maxWeight = useMemo(() => {
    let max = 0.2;
    if (viewMode === "category") {
      categories.forEach((c) => {
        if (c.currentWeight > max) max = c.currentWeight;
        if (c.candidateWeight > max) max = c.candidateWeight;
      });
    } else {
      comparisons.forEach((item) => {
        const cur = parseFloat(item.current_weight) || 0;
        const cand = parseFloat(item.candidate_weight) || 0;
        if (cur > max) max = cur;
        if (cand > max) max = cand;
      });
    }
    return Math.min(1.0, max * 1.15); // Add 15% headroom
  }, [categories, comparisons, viewMode]);

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
      {/* Header & View Mode Switch */}
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <PieChart className="h-4 w-4 text-atlas-accent" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
              Allocation Shifts: Current vs Candidate
            </h3>
          </div>
          <p className="mt-0.5 text-xs text-atlas-text-muted">
            Structural portfolio rebalancing across sectors and security weights.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Legend */}
          <div className="flex items-center gap-3 text-xs text-atlas-text-secondary mr-2">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-sm bg-slate-500" />
              <span>Current</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-sm bg-cyan-400" />
              <span>Candidate</span>
            </div>
          </div>

          <div className="inline-flex rounded border border-atlas-border-default/60 bg-atlas-surface-2 p-0.5 text-xs">
            <button
              onClick={() => setViewMode("category")}
              className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "category"
                  ? "bg-atlas-surface-1 text-atlas-text-primary shadow-sm"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              By Sector
            </button>
            <button
              onClick={() => setViewMode("security")}
              className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "security"
                  ? "bg-atlas-surface-1 text-atlas-text-primary shadow-sm"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              By Security
            </button>
          </div>
        </div>
      </div>

      {/* Bar Comparison List */}
      <div className="space-y-3">
        {viewMode === "category" ? (
          categories.map((cat) => {
            const curWidth = `${Math.min(100, (cat.currentWeight / maxWeight) * 100)}%`;
            const candWidth = `${Math.min(100, (cat.candidateWeight / maxWeight) * 100)}%`;
            const delta = cat.delta;

            return (
              <div key={cat.category} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium text-atlas-text-primary">{cat.category}</span>
                    <span className="text-[10px] text-atlas-text-muted">
                      ({cat.symbols.join(", ")})
                    </span>
                  </div>
                  <div className="flex items-center gap-3 font-mono text-xs">
                    <span className="text-slate-400">{formatWeightPercent(cat.currentWeight)}</span>
                    <span className="text-atlas-text-muted">→</span>
                    <span className="font-semibold text-cyan-300">
                      {formatWeightPercent(cat.candidateWeight)}
                    </span>
                    <span
                      className={`text-[11px] font-semibold ${
                        delta > 0.0001
                          ? "text-emerald-400"
                          : delta < -0.0001
                          ? "text-rose-400"
                          : "text-atlas-text-muted"
                      }`}
                    >
                      {delta > 0.0001 ? "+" : ""}
                      {(delta * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>

                <div className="space-y-1">
                  {/* Current Bar */}
                  <div className="h-2 w-full rounded-sm bg-atlas-surface-2 overflow-hidden">
                    <div
                      className="h-full rounded-sm bg-slate-500 transition-all duration-300"
                      style={{ width: curWidth }}
                    />
                  </div>
                  {/* Candidate Bar */}
                  <div className="h-2 w-full rounded-sm bg-atlas-surface-2 overflow-hidden">
                    <div
                      className="h-full rounded-sm bg-cyan-400 transition-all duration-300"
                      style={{ width: candWidth }}
                    />
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          comparisons.map((item) => {
            const cur = parseFloat(item.current_weight) || 0;
            const cand = parseFloat(item.candidate_weight) || 0;
            const delta = parseFloat(item.weight_delta) || 0;
            const curWidth = `${Math.min(100, (cur / maxWeight) * 100)}%`;
            const candWidth = `${Math.min(100, (cand / maxWeight) * 100)}%`;

            return (
              <div key={item.symbol} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono font-bold text-atlas-text-primary">
                      {item.symbol}
                    </span>
                    <span className="truncate text-atlas-text-muted max-w-[180px]">
                      {item.name}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 font-mono text-xs">
                    <span className="text-slate-400">{formatWeightPercent(cur)}</span>
                    <span className="text-atlas-text-muted">→</span>
                    <span className="font-semibold text-cyan-300">
                      {formatWeightPercent(cand)}
                    </span>
                    <span
                      className={`text-[11px] font-semibold ${
                        delta > 0.0001
                          ? "text-emerald-400"
                          : delta < -0.0001
                          ? "text-rose-400"
                          : "text-atlas-text-muted"
                      }`}
                    >
                      {delta > 0.0001 ? "+" : ""}
                      {(delta * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>

                <div className="space-y-1">
                  {/* Current Bar */}
                  <div className="h-2 w-full rounded-sm bg-atlas-surface-2 overflow-hidden">
                    <div
                      className="h-full rounded-sm bg-slate-500 transition-all duration-300"
                      style={{ width: curWidth }}
                    />
                  </div>
                  {/* Candidate Bar */}
                  <div className="h-2 w-full rounded-sm bg-atlas-surface-2 overflow-hidden">
                    <div
                      className="h-full rounded-sm bg-cyan-400 transition-all duration-300"
                      style={{ width: candWidth }}
                    />
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
