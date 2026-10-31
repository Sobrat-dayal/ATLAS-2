"use client";

import React from "react";
import { FactorContribution } from "@/lib/intelligence/scoring/types";
import { Info, AlertCircle, CheckCircle2 } from "lucide-react";

interface IntelligenceFactorBreakdownProps {
  contributions: FactorContribution[];
  scoreValue?: number | null;
}

export function IntelligenceFactorBreakdown({
  contributions,
  scoreValue,
}: IntelligenceFactorBreakdownProps) {
  if (!contributions || contributions.length === 0) {
    return (
      <div className="p-4 border border-zinc-800 rounded bg-zinc-950 text-zinc-500 font-mono text-xs">
        No factor contributions available for this record.
      </div>
    );
  }

  return (
    <div className="space-y-3 font-mono text-xs select-none">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
        <span className="text-zinc-400 font-semibold uppercase text-[10px] tracking-wider">
          FACTOR CONTRIBUTION DECOMPOSITION
        </span>
        <span className="text-zinc-300 font-bold">
          Total Score: {scoreValue !== null && scoreValue !== undefined ? `${scoreValue.toFixed(1)} / 100` : "N/A"}
        </span>
      </div>

      <div className="space-y-2">
        {contributions.map((factor) => {
          const contribPct = Math.min(Math.max(factor.contribution_points, 0), 100);
          return (
            <div key={factor.factor_id} className="p-2.5 bg-zinc-900 border border-zinc-800 rounded space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  {factor.is_missing ? (
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  )}
                  <span className="font-semibold text-zinc-200">{factor.factor_name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-zinc-400 font-mono">
                    Weight: {(factor.weight * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs font-bold text-emerald-400 font-mono">
                    +{factor.contribution_points.toFixed(1)} pts
                  </span>
                </div>
              </div>

              {/* Progress contribution bar */}
              <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className={`h-full ${factor.is_missing ? "bg-amber-600/50" : "bg-emerald-500"}`}
                  style={{ width: `${contribPct}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[10px] text-zinc-500">
                <span>{factor.explanation}</span>
                <span>Transformed: {(factor.transformed_value * 100).toFixed(0)}%</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-2 border border-zinc-800 rounded bg-zinc-950/80 text-[10px] text-zinc-400 flex items-start gap-1.5">
        <Info className="w-3.5 h-3.5 text-sky-400 shrink-0 mt-0.5" />
        <span>
          Mathematical explainability guarantee: Individual factor contribution points sum exactly to the final 0–100 review priority index without residual discrepancy.
        </span>
      </div>
    </div>
  );
}
