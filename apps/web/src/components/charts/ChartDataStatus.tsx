"use client";

/**
 * Historical Data Status & Audit Bar for ATLAS Charts V1 (Stage 66).
 *
 * Displays auditable data coverage, returned bars count, date range,
 * provider provenance, and data quality status.
 */

import React from "react";
import { CheckCircle2, Clock, Database, HelpCircle } from "lucide-react";
import { ChartCoverageDTO, ChartInstrumentMetadata, formatBarDate } from "@/lib/charts";

export interface ChartDataStatusProps {
  coverage: ChartCoverageDTO | null;
  instrument: ChartInstrumentMetadata | null;
  interval?: string;
  intervalSourceKind?: string;
  derivedSourceInterval?: string | null;
}

export function ChartDataStatus({
  coverage,
  instrument,
  interval = "1d",
  intervalSourceKind = "NATIVE",
  derivedSourceInterval,
}: ChartDataStatusProps) {
  if (!coverage || !instrument) return null;

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 px-3 py-2 bg-zinc-950/60 border border-zinc-800/80 rounded text-[11px] font-mono text-zinc-400">
      {/* Left: Quality status & Provider & Lineage */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1 text-emerald-400 font-semibold">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
          <span>DATA {coverage.source_status}</span>
        </div>

        <div className="flex items-center gap-1.5 text-zinc-400">
          <Database className="w-3 h-3 text-cyan-400" />
          <span>Source:</span>
          <span className="text-zinc-200">{instrument.provider_key}</span>
        </div>

        <div className="flex items-center gap-1.5 text-zinc-400">
          <span>Interval:</span>
          <span className="text-zinc-200 font-bold">{interval.toUpperCase()}</span>
          {intervalSourceKind === "DERIVED" ? (
            <span className="px-1.5 py-0.2 bg-cyan-950/60 border border-cyan-800/60 text-cyan-300 rounded text-[10px]">
              DERIVED ({derivedSourceInterval || "1d"})
            </span>
          ) : (
            <span className="px-1.5 py-0.2 bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 rounded text-[10px]">
              NATIVE
            </span>
          )}
        </div>

        {/* Range */}
        {coverage.earliest_available_bar && coverage.latest_available_bar && (
          <div className="flex items-center gap-1.5 text-zinc-400">
            <Clock className="w-3 h-3 text-zinc-500" />
            <span>Coverage:</span>
            <span className="text-zinc-300">
              {formatBarDate(coverage.earliest_available_bar)} —{" "}
              {formatBarDate(coverage.latest_available_bar)}
            </span>
          </div>
        )}
      </div>

      {/* Right: Bar counts & Stage 68 indicator */}
      <div className="flex items-center gap-4">
        <div>
          <span>Bars: </span>
          <span className="text-zinc-200 font-semibold">
            {coverage.returned_bars_count}
          </span>
          <span className="text-zinc-500"> / {coverage.total_bars_available} available</span>
        </div>

        <div
          className="flex items-center gap-1 text-zinc-400 hover:text-zinc-200 cursor-help"
          title="ATLAS Stage 68 Multi-Timeframe Charting Engine: Validated OHLCV aggregation, session boundaries, and 4 professional chart types."
        >
          <HelpCircle className="w-3 h-3 text-cyan-400" />
          <span className="text-zinc-400">Stage 68 Multi-Timeframe</span>
        </div>
      </div>
    </div>
  );
}
