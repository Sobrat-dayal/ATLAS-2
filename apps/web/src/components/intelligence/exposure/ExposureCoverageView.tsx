"use client";

import React from "react";
import { ExposureCoverageSummary } from "@/lib/intelligence/exposure/types";
import { formatCurrencyAmount, formatPercentage, formatRatio } from "@/lib/intelligence/exposure/units";
import { ShieldCheck, AlertCircle, CheckCircle2, HelpCircle } from "lucide-react";

interface ExposureCoverageViewProps {
  coverageSummary: ExposureCoverageSummary | null | undefined;
  baseCurrency?: string;
}

export function ExposureCoverageView({
  coverageSummary,
  baseCurrency = "USD"
}: ExposureCoverageViewProps) {
  if (!coverageSummary) {
    return (
      <div className="p-8 text-center text-zinc-500 font-mono text-xs">
        <HelpCircle className="w-8 h-8 mx-auto mb-2 text-zinc-600" />
        No coverage summary available for current dataset.
      </div>
    );
  }

  const covRatioNum = typeof coverageSummary.coverage_ratio === "string"
    ? parseFloat(coverageSummary.coverage_ratio)
    : coverageSummary.coverage_ratio;
  const covPct = (covRatioNum * 100).toFixed(1);
  const unallocPct = coverageSummary.unallocated_residual_percentage
    ? Number(coverageSummary.unallocated_residual_percentage).toFixed(1)
    : "0.0";

  return (
    <div className="p-4 font-mono text-xs space-y-4">
      {/* Visual Coverage Progress Bar */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-zinc-200">POPULATION COVERAGE BREAKDOWN</span>
          <span className="text-zinc-400">
            Status: <span className="text-emerald-400 font-bold uppercase">{coverageSummary.coverage_status}</span>
          </span>
        </div>

        {/* Multi-segment bar */}
        <div className="h-5 w-full bg-zinc-950 rounded overflow-hidden flex border border-zinc-800">
          <div
            style={{ width: `${Math.min(100, Math.max(0, covRatioNum * 100))}%` }}
            className="bg-emerald-600 h-full transition-all flex items-center justify-center text-[10px] text-white font-bold"
            title={`Covered: ${covPct}%`}
          >
            {covRatioNum > 0.15 ? `${covPct}% Covered` : ""}
          </div>
          {Number(unallocPct) > 0 && (
            <div
              style={{ width: `${Math.min(100, Math.max(0, Number(unallocPct)))}%` }}
              className="bg-amber-600 h-full transition-all flex items-center justify-center text-[10px] text-white font-bold"
              title={`Unallocated Residual: ${unallocPct}%`}
            >
              {Number(unallocPct) > 0.15 ? `${unallocPct}% Unallocated` : ""}
            </div>
          )}
        </div>

        <div className="flex items-center justify-between text-[11px] text-zinc-400 pt-1">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-emerald-600 rounded-sm inline-block" />
            <span>Eligible Disclosed Components: {formatCurrencyAmount(coverageSummary.eligible_covered_denominator, baseCurrency)}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-amber-600 rounded-sm inline-block" />
            <span>Unallocated Residual: {coverageSummary.unallocated_residual_amount ? formatCurrencyAmount(coverageSummary.unallocated_residual_amount, baseCurrency) : "$0.00"}</span>
          </div>
        </div>
      </div>

      {/* Verified Covered Dimensions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-zinc-900/40 border border-zinc-800 rounded p-3 space-y-2">
          <div className="text-[10px] text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>COVERED DIMENSIONS ({coverageSummary.covered_dimensions.length})</span>
          </div>
          <ul className="space-y-1">
            {coverageSummary.covered_dimensions.map((dim, idx) => (
              <li key={idx} className="p-1.5 bg-zinc-950/60 rounded border border-zinc-800/80 text-zinc-200">
                {dim}
              </li>
            ))}
          </ul>
        </div>

        {/* Uncovered or Residual Dimensions */}
        <div className="bg-zinc-900/40 border border-zinc-800 rounded p-3 space-y-2">
          <div className="text-[10px] text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
            <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
            <span>UNCOVERED / UNDISCLOSED RESIDUALS</span>
          </div>
          {coverageSummary.uncovered_dimensions.length > 0 ? (
            <ul className="space-y-1">
              {coverageSummary.uncovered_dimensions.map((dim, idx) => (
                <li key={idx} className="p-1.5 bg-zinc-950/60 rounded border border-zinc-800/80 text-amber-300">
                  {dim}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-zinc-500 italic p-2">
              No explicitly missing dimensions identified.
            </div>
          )}

          {coverageSummary.notes.length > 0 && (
            <div className="mt-3 p-2 rounded bg-zinc-950 border border-zinc-800 text-[11px] text-zinc-400 space-y-1">
              <span className="text-[10px] text-zinc-500 block uppercase font-semibold">METHODOLOGICAL NOTES</span>
              {coverageSummary.notes.map((note, idx) => (
                <p key={idx} className="leading-relaxed">{note}</p>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
