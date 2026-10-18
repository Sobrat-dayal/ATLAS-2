"use client";

/**
 * Accessible Technical Indicator Numerical Inspector Table (Stage 70).
 *
 * Implements a semantic, keyboard-navigable, screen-reader accessible table
 * presenting the exact numerical values of active technical indicators time-aligned
 * to historical market observations.
 */

import React, { useState } from "react";
import { ChevronDown, ChevronLeft, ChevronRight, ChevronUp, Sliders } from "lucide-react";
import {
  ChartBarDTO,
  formatBarDate,
  formatPrice,
  IndicatorCalculationResult,
  IndicatorDefinition,
  IndicatorInstanceConfig,
} from "@/lib/charts";

export interface IndicatorInspectorTableProps {
  bars: ChartBarDTO[];
  catalog?: IndicatorDefinition[];
  instances: IndicatorInstanceConfig[];
  results: IndicatorCalculationResult[];
}

export function IndicatorInspectorTable({
  bars,
  catalog = [],
  instances,
  results,
}: IndicatorInspectorTableProps) {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 15;

  if (instances.length === 0 || bars.length === 0) return null;

  // Newest bars first for tabular exploration
  const sortedBars = [...bars].reverse();
  const totalPages = Math.ceil(sortedBars.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const pageBars = sortedBars.slice(startIndex, startIndex + pageSize);

  // Collect active series columns
  const columns: {
    instanceId: string;
    seriesId: string;
    header: string;
    color: string;
    points: { time_unix: number; value: number | null; status: string }[];
  }[] = [];

  for (const inst of instances) {
    if (!inst.visible) continue;
    const defn = catalog.find((d) => d.indicator_id === inst.indicator_id);
    const res = results.find((r) => r.instance_id === inst.instance_id);
    if (!res || !res.series) continue;

    const baseName = defn?.display_name || inst.indicator_id.replace("atlas.", "").toUpperCase();

    for (const s of res.series) {
      const header = res.series.length > 1 ? `${baseName} (${s.name})` : baseName;
      columns.push({
        instanceId: inst.instance_id,
        seriesId: s.series_id,
        header,
        color: s.color || inst.color || "#38bdf8",
        points: s.points,
      });
    }
  }

  if (columns.length === 0) return null;

  return (
    <div className="w-full bg-zinc-950 border border-zinc-800/80 rounded overflow-hidden">
      {/* Header bar / Toggle */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-zinc-900/60 hover:bg-zinc-900 text-left transition-colors"
        aria-expanded={isExpanded}
        aria-controls="indicator-inspector-table"
      >
        <div className="flex items-center gap-2 text-xs font-mono font-medium text-zinc-300">
          <Sliders className="w-4 h-4 text-cyan-400" />
          <span>Technical Indicator Numerical Inspector</span>
          <span className="text-zinc-500 font-normal">
            ({columns.length} active output series)
          </span>
        </div>

        <div className="flex items-center gap-1 text-xs text-zinc-400">
          <span>{isExpanded ? "Collapse" : "Expand Table"}</span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-zinc-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-zinc-400" />
          )}
        </div>
      </button>

      {/* Expanded Table Content */}
      {isExpanded && (
        <div id="indicator-inspector-table" className="p-4 border-t border-zinc-800/80 space-y-3">
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono text-left border-collapse">
              <thead>
                <tr className="border-b border-zinc-800 text-zinc-400 text-[11px] uppercase tracking-wider">
                  <th scope="col" className="py-2 px-3">Date (UTC)</th>
                  <th scope="col" className="py-2 px-3 text-right">Close</th>
                  {columns.map((col) => (
                    <th key={`${col.instanceId}_${col.seriesId}`} scope="col" className="py-2 px-3 text-right" style={{ color: col.color }}>
                      {col.header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-900">
                {pageBars.map((bar) => {
                  const closeVal = typeof bar.close === "string" ? parseFloat(bar.close) : Number(bar.close);

                  return (
                    <tr
                      key={bar.timestamp}
                      className="hover:bg-zinc-900/40 transition-colors"
                    >
                      <td className="py-2 px-3 text-zinc-300 font-medium">
                        {formatBarDate(bar.timestamp)}
                      </td>
                      <td className="py-2 px-3 text-right text-zinc-300 tabular-nums font-semibold">
                        {formatPrice(closeVal, 2)}
                      </td>
                      {columns.map((col) => {
                        const pt = col.points.find((p) => Math.abs(p.time_unix - bar.time_unix) <= 1);
                        return (
                          <td
                            key={`${col.instanceId}_${col.seriesId}`}
                            className="py-2 px-3 text-right tabular-nums font-semibold"
                          >
                            {pt && pt.value != null ? (
                              <span style={{ color: col.color }}>{pt.value.toFixed(2)}</span>
                            ) : pt?.status === "WARMUP" ? (
                              <span className="text-zinc-600 italic text-[10px]">warmup</span>
                            ) : pt?.status === "MISSING_VOLUME" ? (
                              <span className="text-amber-500/80 text-[10px]">no vol</span>
                            ) : (
                              <span className="text-zinc-600">—</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Table Pagination */}
          <div className="flex items-center justify-between text-xs font-mono text-zinc-400 pt-2 border-t border-zinc-900">
            <div>
              Showing {startIndex + 1}–{Math.min(startIndex + pageSize, sortedBars.length)} of {sortedBars.length} observations
            </div>

            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1 rounded bg-zinc-900 border border-zinc-800 hover:border-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed text-zinc-300"
                aria-label="Previous Page"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <span className="px-2 text-zinc-300 font-semibold">
                Page {currentPage} of {totalPages}
              </span>

              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-1 rounded bg-zinc-900 border border-zinc-800 hover:border-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed text-zinc-300"
                aria-label="Next Page"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
