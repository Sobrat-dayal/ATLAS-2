"use client";

import React from "react";
import { Database, RefreshCw, ShieldCheck } from "lucide-react";
import { NewsFreshnessResponseDTO } from "@/lib/news/types";
import { formatRelativeTime } from "@/lib/news/formatting";

interface NewsHeaderProps {
  status: NewsFreshnessResponseDTO | null;
  totalArticles: number;
  isRefreshing: boolean;
  onRefresh: () => void;
  onOpenCoverage: () => void;
}

export function NewsHeader({
  status,
  totalArticles,
  isRefreshing,
  onRefresh,
  onOpenCoverage,
}: NewsHeaderProps) {
  const isHealthy = status?.status === "HEALTHY";
  const relativeFetch = status?.last_successful_fetch
    ? formatRelativeTime(status.last_successful_fetch)
    : "Live";

  return (
    <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-zinc-200 dark:border-zinc-800 pb-4">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 font-mono">
            NEWS
          </h1>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700">
            STAGE 99 V1
          </span>
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-mono bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                isHealthy ? "bg-emerald-500 animate-pulse" : "bg-amber-500"
              }`}
            />
            <span>{status?.latency_class || "NEAR_REALTIME"}</span>
          </div>
        </div>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
          Source-verified global market news, canonical entity linking, and publisher provenance.
        </p>
      </div>

      <div className="flex items-center gap-2 self-stretch sm:self-auto">
        <button
          onClick={onOpenCoverage}
          className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors shadow-sm"
          title="Inspect permitted news sources and coverage"
        >
          <Database className="w-3.5 h-3.5 text-zinc-500" />
          <span>Sources & Coverage</span>
          <span className="ml-1 px-1.5 py-0.2 rounded bg-zinc-100 dark:bg-zinc-800 text-[10px] text-zinc-500 font-mono">
            {totalArticles}
          </span>
        </button>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors shadow-sm disabled:opacity-50"
          title="Refresh canonical news feed"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-zinc-400" : "text-zinc-500"}`} />
          <span className="hidden sm:inline">Refresh</span>
          {relativeFetch && (
            <span className="text-[10px] text-zinc-400 font-mono hidden md:inline">
              ({relativeFetch})
            </span>
          )}
        </button>
      </div>
    </header>
  );
}
