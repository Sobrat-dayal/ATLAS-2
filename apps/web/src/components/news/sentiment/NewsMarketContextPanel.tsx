"use client";

import React from "react";
import { ObservedNewsMarketContextDTO } from "@/lib/news/types";
import { formatUtcTimestamp } from "@/lib/news/formatting";
import { AlertTriangle, Clock, TrendingUp, Info } from "lucide-react";

interface NewsMarketContextPanelProps {
  marketContext: ObservedNewsMarketContextDTO | null;
  isLoading?: boolean;
}

export function NewsMarketContextPanel({ marketContext, isLoading }: NewsMarketContextPanelProps) {
  if (isLoading) {
    return (
      <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono animate-pulse">
        <div className="h-4 w-48 bg-zinc-200 dark:bg-zinc-800 rounded mb-4" />
        <div className="h-24 bg-zinc-100 dark:bg-zinc-800/40 rounded" />
      </div>
    );
  }

  if (!marketContext) {
    return (
      <div className="p-4 rounded border border-dashed border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 font-mono text-center">
        <Clock className="w-6 h-6 text-zinc-400 mx-auto mb-2 opacity-50" />
        <h4 className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">
          No Market Reaction Observed
        </h4>
        <p className="text-[10px] text-zinc-500 mt-1 max-w-sm mx-auto">
          Click &ldquo;Observe Market Context&rdquo; on an article to view descriptive before/after price movements aligned with exchange trading calendars.
        </p>
      </div>
    );
  }

  const {
    ticker,
    market_id,
    window_type,
    publication_time,
    window_start_time,
    window_end_time,
    price_start,
    price_end,
    observed_return_pct,
    benchmark_id,
    benchmark_relative_return,
    currency,
    noncausal_disclaimer,
    limitations,
  } = marketContext;

  const returnColor =
    observed_return_pct > 0.0
      ? "text-emerald-500"
      : observed_return_pct < 0.0
      ? "text-rose-500"
      : "text-zinc-400";

  return (
    <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-4 h-4 text-cyan-500" />
          <h3 className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider">
            Observed Price Context ({ticker})
          </h3>
        </div>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 font-semibold">
          {market_id}
        </span>
      </div>

      {/* Mandatory Noncausal Disclaimer Banner */}
      <div className="p-2.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-500 text-[10px] flex items-start space-x-2">
        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold uppercase tracking-wider">Descriptive Only (Noncausal): </span>
          <span>{noncausal_disclaimer}</span>
        </div>
      </div>

      {/* Price Comparison Grid */}
      <div className="grid grid-cols-3 gap-2 text-xs">
        <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800">
          <div className="text-[10px] text-zinc-500">Window Start</div>
          <div className="text-sm font-bold text-zinc-900 dark:text-zinc-100 tabular-nums">
            {currency} {price_start.toFixed(2)}
          </div>
          <div className="text-[9px] text-zinc-500 mt-0.5 truncate">
            {formatUtcTimestamp(window_start_time)}
          </div>
        </div>

        <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800">
          <div className="text-[10px] text-zinc-500">Window End</div>
          <div className="text-sm font-bold text-zinc-900 dark:text-zinc-100 tabular-nums">
            {currency} {price_end.toFixed(2)}
          </div>
          <div className="text-[9px] text-zinc-500 mt-0.5 truncate">
            {formatUtcTimestamp(window_end_time)}
          </div>
        </div>

        <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800">
          <div className="text-[10px] text-zinc-500">Observed Return</div>
          <div className={`text-sm font-bold tabular-nums ${returnColor}`}>
            {observed_return_pct > 0 ? `+${observed_return_pct.toFixed(2)}%` : `${observed_return_pct.toFixed(2)}%`}
          </div>
          {benchmark_id && benchmark_relative_return !== null && benchmark_relative_return !== undefined && (
            <div className="text-[9px] text-zinc-500 mt-0.5">
              Rel vs {benchmark_id}: {benchmark_relative_return > 0 ? `+${benchmark_relative_return.toFixed(2)}%` : `${benchmark_relative_return.toFixed(2)}%`}
            </div>
          )}
        </div>
      </div>

      {/* Timing Details */}
      <div className="text-[10px] text-zinc-500 space-y-1 pt-1">
        <div>
          <span className="font-semibold text-zinc-400">Published:</span> {formatUtcTimestamp(publication_time)}
        </div>
        <div>
          <span className="font-semibold text-zinc-400">Window Type:</span> {window_type.replace(/_/g, " ")}
        </div>
      </div>

      {/* Analytical Limitations */}
      {limitations && limitations.length > 0 && (
        <div className="pt-2 border-t border-zinc-200 dark:border-zinc-800">
          <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider mb-1 flex items-center space-x-1">
            <Info className="w-3 h-3 text-zinc-400" />
            <span>Analytical Limitations</span>
          </div>
          <ul className="list-disc list-inside text-[10px] text-zinc-500 space-y-0.5">
            {limitations.map((lim, i) => (
              <li key={i}>{lim}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
