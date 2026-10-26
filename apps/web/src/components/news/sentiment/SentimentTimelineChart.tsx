"use client";

import React from "react";
import { SentimentTimelineResponseDTO } from "@/lib/news/types";
import { Calendar, TrendingUp } from "lucide-react";

interface SentimentTimelineChartProps {
  timeline: SentimentTimelineResponseDTO | null;
  isLoading?: boolean;
}

export function SentimentTimelineChart({ timeline, isLoading }: SentimentTimelineChartProps) {
  if (isLoading) {
    return (
      <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 animate-pulse font-mono">
        <div className="h-4 w-40 bg-zinc-200 dark:bg-zinc-800 rounded mb-4" />
        <div className="h-32 bg-zinc-100 dark:bg-zinc-800/40 rounded" />
      </div>
    );
  }

  const buckets = timeline?.buckets || [];

  if (buckets.length === 0) {
    return (
      <div className="p-6 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono text-center">
        <Calendar className="w-6 h-6 text-zinc-400 mx-auto mb-2 opacity-60" />
        <p className="text-xs text-zinc-500">No chronological sentiment observations available for this window.</p>
      </div>
    );
  }

  // Calculate maximum total articles in a single bucket for proportional bar heights
  const maxVolume = Math.max(...buckets.map((b) => b.eligible_count), 1);

  return (
    <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-4 h-4 text-cyan-500" />
          <h3 className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider">
            Chronological Sentiment Trajectory ({timeline?.interval || "DAY"})
          </h3>
        </div>
        <div className="text-[11px] text-zinc-500">
          Total Observations: <strong className="text-zinc-700 dark:text-zinc-300">{timeline?.total_eligible}</strong>
        </div>
      </div>

      {/* Timeline Columns */}
      <div className="mt-4 pt-4 flex items-end justify-between gap-2 overflow-x-auto min-h-[140px] pb-2">
        {buckets.map((b, idx) => {
          const heightPct = Math.max(Math.round((b.eligible_count / maxVolume) * 100), 10);
          const netScore = b.net_sentiment;
          const barColor =
            netScore > 0.05
              ? "bg-emerald-500 hover:bg-emerald-400"
              : netScore < -0.05
              ? "bg-rose-500 hover:bg-rose-400"
              : "bg-zinc-400 hover:bg-zinc-300";

          return (
            <div
              key={idx}
              className="flex-1 flex flex-col items-center min-w-[38px] group relative cursor-pointer"
            >
              {/* Tooltip on hover */}
              <div className="absolute -top-16 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 bg-zinc-950 text-white text-[10px] p-1.5 rounded shadow-lg border border-zinc-700 whitespace-nowrap">
                <div className="font-bold">{b.label}</div>
                <div>Eligible: {b.eligible_count}</div>
                <div className="text-emerald-400">+{b.positive_count} | <span className="text-rose-400">-{b.negative_count}</span> | <span className="text-zinc-400">={b.neutral_count}</span></div>
                <div>Net: {b.net_sentiment > 0 ? `+${b.net_sentiment.toFixed(2)}` : b.net_sentiment.toFixed(2)}</div>
              </div>

              {/* Net score text badge above bar */}
              <div
                className={`text-[9px] font-bold mb-1 tabular-nums ${
                  netScore > 0 ? "text-emerald-500" : netScore < 0 ? "text-rose-500" : "text-zinc-400"
                }`}
              >
                {b.eligible_count > 0 ? (netScore > 0 ? `+${netScore.toFixed(1)}` : netScore.toFixed(1)) : "0"}
              </div>

              {/* Bar */}
              <div
                style={{ height: `${heightPct}px` }}
                className={`w-full max-w-[28px] rounded-t-sm transition-all duration-200 ${barColor}`}
              />

              {/* Date label */}
              <div className="text-[9px] text-zinc-500 mt-1 truncate max-w-[40px] text-center">
                {b.label.slice(5)}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-2 pt-2 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between text-[10px] text-zinc-500">
        <span>Bar height: eligible volume | Bar color: net sentiment polarity</span>
        <span>Publication timestamp-anchored (no look-ahead hindsight)</span>
      </div>
    </div>
  );
}
