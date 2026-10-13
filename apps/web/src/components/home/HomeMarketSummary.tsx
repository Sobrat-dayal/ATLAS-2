"use client";

import React from "react";
import Link from "next/link";
import { ArrowUpRight, RefreshCw } from "lucide-react";
import { useHomeMarketSummary } from "@/hooks/home/useHomeMarketSummary";
import { HomeWidgetSurface } from "./HomeWidgetSurface";
import { MarketSummaryInstrumentCard } from "./MarketSummaryInstrumentCard";
import { MarketSummaryEmptyState } from "./MarketSummaryEmptyState";

export function HomeMarketSummary() {
  const { data, isLoading, isError, error, refetch, isRefetching } = useHomeMarketSummary();

  const coverage = data?.coverage;
  const items = data?.items || [];

  return (
    <HomeWidgetSurface
      id="home-market-summary"
      title="Market Summary"
      subtitle="Latest observations from connected market infrastructure"
      actions={
        <div className="flex items-center gap-2">
          {coverage && (
            <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-800/80 text-zinc-400 border border-zinc-700/50">
              {coverage.available_count}/{coverage.configured_count} Available
            </span>
          )}

          <button
            type="button"
            onClick={() => refetch()}
            disabled={isRefetching || isLoading}
            aria-label="Refresh market summary"
            className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60 transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 ${isRefetching ? "animate-spin text-emerald-400" : ""}`}
              aria-hidden="true"
            />
          </button>

          <Link
            href="/markets"
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <span>Open Markets</span>
            <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
          </Link>
        </div>
      }
    >
      {/* Loading Skeletons */}
      {isLoading && (
        <div
          role="status"
          aria-label="Loading market summary"
          className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3.5"
        >
          {Array.from({ length: 8 }).map((_, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-lg border border-zinc-800/60 bg-zinc-900/30 animate-pulse flex flex-col justify-between h-32"
            >
              <div className="flex justify-between items-start">
                <div className="space-y-1.5 w-2/3">
                  <div className="h-4 bg-zinc-800 rounded w-24" />
                  <div className="h-2.5 bg-zinc-800/60 rounded w-16" />
                </div>
                <div className="h-3 bg-zinc-800 rounded w-6" />
              </div>

              <div className="space-y-1.5 my-2">
                <div className="h-5 bg-zinc-800 rounded w-28" />
                <div className="h-3 bg-zinc-800/60 rounded w-20" />
              </div>

              <div className="h-2.5 bg-zinc-800/40 rounded w-full pt-2" />
            </div>
          ))}
        </div>
      )}

      {/* Error State */}
      {!isLoading && isError && (
        <MarketSummaryEmptyState
          title="Market Summary Feed Disconnected"
          description={error?.message || "Unable to reach ATLAS market summary endpoint."}
          isError={true}
          onRetry={refetch}
        />
      )}

      {/* Empty Configuration or Observations */}
      {!isLoading && !isError && items.length === 0 && (
        <MarketSummaryEmptyState
          title="No Instruments Configured"
          description="No market instruments are configured for this overview."
        />
      )}

      {/* Valid Observations Grid */}
      {!isLoading && !isError && items.length > 0 && (
        <div className="space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3.5">
            {items.map((item) => (
              <MarketSummaryInstrumentCard
                key={item.instrument_entity_id}
                item={item}
              />
            ))}
          </div>

          {/* Footer note */}
          <div className="flex items-center justify-between text-[11px] text-zinc-400 px-1 pt-1">
            <span>
              Observations originate from connected ATLAS market infrastructure. Performance changes require verified reference sessions.
            </span>
          </div>
        </div>
      )}
    </HomeWidgetSurface>
  );
}
