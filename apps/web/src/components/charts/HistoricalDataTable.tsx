"use client";

/**
 * Accessible Historical OHLCV Data Table for ATLAS Charts V1 (Stage 66).
 *
 * Implements a semantic, keyboard-navigable, screen-reader accessible table
 * presenting the exact numerical values of loaded historical market bars.
 */

import React, { useState } from "react";
import { ChevronLeft, ChevronRight, ChevronUp, ChevronDown, Table as TableIcon } from "lucide-react";
import {
  ChartBarDTO,
  ChartInstrumentMetadata,
  formatBarDate,
  formatPercentChange,
  formatPrice,
  formatVolume,
} from "@/lib/charts";

export interface HistoricalDataTableProps {
  bars: ChartBarDTO[];
  instrument: ChartInstrumentMetadata | null;
}

export function HistoricalDataTable({ bars, instrument }: HistoricalDataTableProps) {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 15;

  if (bars.length === 0) return null;

  // Newest bars first for tabular exploration
  const sortedBars = [...bars].reverse();
  const totalPages = Math.ceil(sortedBars.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const pageBars = sortedBars.slice(startIndex, startIndex + pageSize);

  const precision = instrument?.asset_class === "fx" && instrument.display_symbol === "EURUSD" ? 4 : 2;

  return (
    <div className="w-full bg-zinc-950 border border-zinc-800/80 rounded overflow-hidden">
      {/* Header bar / Toggle */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-zinc-900/60 hover:bg-zinc-900 text-left transition-colors"
        aria-expanded={isExpanded}
        aria-controls="historical-data-table"
      >
        <div className="flex items-center gap-2 text-xs font-mono font-medium text-zinc-300">
          <TableIcon className="w-4 h-4 text-cyan-400" />
          <span>Historical OHLCV Data Table</span>
          <span className="text-zinc-500 font-normal">
            ({bars.length} bars loaded)
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
        <div id="historical-data-table" className="p-4 border-t border-zinc-800/80 space-y-3">
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono text-left border-collapse">
              <thead>
                <tr className="border-b border-zinc-800 text-zinc-400 text-[11px] uppercase tracking-wider">
                  <th scope="col" className="py-2 px-3">Date (UTC)</th>
                  <th scope="col" className="py-2 px-3 text-right">Open</th>
                  <th scope="col" className="py-2 px-3 text-right">High</th>
                  <th scope="col" className="py-2 px-3 text-right">Low</th>
                  <th scope="col" className="py-2 px-3 text-right">Close</th>
                  <th scope="col" className="py-2 px-3 text-right">Change %</th>
                  {instrument?.has_volume !== false && (
                    <th scope="col" className="py-2 px-3 text-right">Volume</th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-900">
                {pageBars.map((bar) => {
                  const openVal = typeof bar.open === "string" ? parseFloat(bar.open) : Number(bar.open);
                  const closeVal = typeof bar.close === "string" ? parseFloat(bar.close) : Number(bar.close);
                  const pct = openVal !== 0 ? ((closeVal - openVal) / openVal) * 100 : 0;
                  const isUp = closeVal >= openVal;

                  return (
                    <tr
                      key={bar.timestamp}
                      className="hover:bg-zinc-900/40 transition-colors"
                    >
                      <td className="py-2 px-3 text-zinc-300 font-medium">
                        {formatBarDate(bar.timestamp)}
                      </td>
                      <td className="py-2 px-3 text-right text-zinc-200 tabular-nums">
                        {formatPrice(bar.open, precision)}
                      </td>
                      <td className="py-2 px-3 text-right text-zinc-200 tabular-nums">
                        {formatPrice(bar.high, precision)}
                      </td>
                      <td className="py-2 px-3 text-right text-zinc-200 tabular-nums">
                        {formatPrice(bar.low, precision)}
                      </td>
                      <td className="py-2 px-3 text-right text-zinc-100 font-semibold tabular-nums">
                        {formatPrice(bar.close, precision)}
                      </td>
                      <td
                        className={`py-2 px-3 text-right font-medium tabular-nums ${
                          isUp ? "text-emerald-400" : "text-red-400"
                        }`}
                      >
                        {formatPercentChange(pct)}
                      </td>
                      {instrument?.has_volume !== false && (
                        <td className="py-2 px-3 text-right text-zinc-400 tabular-nums">
                          {formatVolume(bar.volume)}
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Table Pagination */}
          <div className="flex items-center justify-between text-xs font-mono text-zinc-400 pt-2 border-t border-zinc-900">
            <div>
              Showing {startIndex + 1}–{Math.min(startIndex + pageSize, sortedBars.length)} of {sortedBars.length} bars
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
