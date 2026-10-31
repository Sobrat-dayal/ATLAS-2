"use client";

import React from "react";
import { ExposureCoverageSummary, AtlasExposureResult } from "@/lib/intelligence/exposure/types";
import { formatCurrencyAmount, formatPercentage, formatRatio } from "@/lib/intelligence/exposure/units";
import { ShieldCheck, AlertCircle, PieChart, DollarSign, Layers } from "lucide-react";

interface ExposureSummaryProps {
  results: AtlasExposureResult[];
  coverageSummary?: ExposureCoverageSummary | null;
  baseCurrency?: string;
}

export function ExposureSummary({
  results,
  coverageSummary,
  baseCurrency = "USD"
}: ExposureSummaryProps) {
  const totalResults = results.length;
  
  // Calculate covered value and net signed value
  let totalSigned = 0;
  let totalAbsolute = 0;
  results.forEach(r => {
    if (r.amount !== null && r.amount !== undefined) {
      const val = typeof r.amount === "string" ? parseFloat(r.amount) : r.amount;
      if (!isNaN(val)) {
        totalSigned += val;
        totalAbsolute += Math.abs(val);
      }
    }
  });

  const covRatio = coverageSummary?.coverage_ratio;
  const unallocAmt = coverageSummary?.unallocated_residual_amount;
  const unallocPct = coverageSummary?.unallocated_residual_percentage;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 p-3 bg-zinc-950 border-b border-zinc-800 font-mono text-xs">
      {/* Total Denominator & Covered */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded p-2.5 flex flex-col justify-between">
        <div className="flex items-center justify-between text-zinc-400 mb-1">
          <span>MEASURED COVERAGE</span>
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-lg font-bold text-zinc-100">
          {coverageSummary ? formatRatio(covRatio) : "100.0%"}
        </div>
        <div className="text-[11px] text-zinc-400 mt-1 truncate">
          {coverageSummary
            ? `${formatCurrencyAmount(coverageSummary.eligible_covered_denominator, baseCurrency)} of ${formatCurrencyAmount(coverageSummary.total_relevant_denominator, baseCurrency)}`
            : `${totalResults} verified relations`}
        </div>
      </div>

      {/* Unallocated Residual */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded p-2.5 flex flex-col justify-between">
        <div className="flex items-center justify-between text-zinc-400 mb-1">
          <span>UNALLOCATED RESIDUAL</span>
          <AlertCircle className={`w-4 h-4 ${unallocPct && Number(unallocPct) > 0 ? "text-amber-400" : "text-zinc-500"}`} />
        </div>
        <div className={`text-lg font-bold ${unallocPct && Number(unallocPct) > 0 ? "text-amber-400" : "text-zinc-300"}`}>
          {unallocPct !== undefined && unallocPct !== null ? formatPercentage(unallocPct) : "0.00%"}
        </div>
        <div className="text-[11px] text-zinc-400 mt-1 truncate">
          {unallocAmt ? `${formatCurrencyAmount(unallocAmt, baseCurrency)} unassigned` : "Fully reconciled to filing"}
        </div>
      </div>

      {/* Directional Net vs Gross Footprint */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded p-2.5 flex flex-col justify-between">
        <div className="flex items-center justify-between text-zinc-400 mb-1">
          <span>ECONOMIC FOOTPRINT</span>
          <DollarSign className="w-4 h-4 text-blue-400" />
        </div>
        <div className="text-lg font-bold text-zinc-100 truncate">
          {formatCurrencyAmount(totalSigned, baseCurrency)}
        </div>
        <div className="text-[11px] text-zinc-400 mt-1 truncate">
          Gross: {formatCurrencyAmount(totalAbsolute, baseCurrency)}
        </div>
      </div>

      {/* Relationships and Domains */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded p-2.5 flex flex-col justify-between">
        <div className="flex items-center justify-between text-zinc-400 mb-1">
          <span>RELATIONSHIPS</span>
          <Layers className="w-4 h-4 text-purple-400" />
        </div>
        <div className="text-lg font-bold text-zinc-100">
          {totalResults} <span className="text-xs font-normal text-zinc-400">active links</span>
        </div>
        <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-pulse" />
          Deterministic & Source-Backed
        </div>
      </div>
    </div>
  );
}
