"use client";

/**
 * Master Charts V1 Workspace Page for ATLAS (Stage 66).
 *
 * Implements the institutional Bloomberg/TradingView-inspired workspace at /charts.
 */

import React, { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Activity, CandlestickChart } from "lucide-react";
import { useChartHistory } from "@/hooks/charts";
import { ChartInstrumentHeader } from "./ChartInstrumentHeader";
import { ChartToolbar } from "./ChartToolbar";
import { ChartCrosshairDetails } from "./ChartCrosshairDetails";
import { HistoricalChart } from "./HistoricalChart";
import { ChartDataStatus } from "./ChartDataStatus";
import { HistoricalDataTable } from "./HistoricalDataTable";
import {
  ChartEmptyState,
  ChartErrorState,
  ChartLoadingSkeleton,
} from "./ChartEmptyErrorStates";

function ChartsContent() {
  const searchParams = useSearchParams();
  const urlSymbol = searchParams.get("symbol") || searchParams.get("ticker");
  const urlInstrumentId = searchParams.get("instrument_id") || searchParams.get("id");
  const initialParam = urlInstrumentId || urlSymbol || "SPY";

  const {
    selectedSymbol,
    selectedInstrument,
    interval,
    renderMode,
    bars,
    coverage,
    pagination,
    isLoading,
    isBackfilling,
    error,
    hoveredBar,
    selectInstrument,
    setRenderMode,
    loadOlderHistory,
    refreshHistory,
    setHoveredBar,
    availableInstruments,
  } = useChartHistory(initialParam);

  return (
    <div className="w-full flex flex-col gap-3 p-4 md:p-6 min-h-screen bg-black text-zinc-100 font-sans">
      {/* Workspace Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-zinc-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded bg-cyan-950/60 border border-cyan-800/60 flex items-center justify-center">
            <CandlestickChart className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-zinc-100 font-mono">
                CHARTS
              </h1>
              <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 rounded">
                STAGE 66
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 rounded flex items-center gap-1">
                <Activity className="w-3 h-3 text-emerald-400" />
                <span>CANONICAL OHLCV</span>
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Institutional financial charting workspace, historical candlestick engine and market exploration.
            </p>
          </div>
        </div>
      </div>

      {/* Instrument Overview Header */}
      <ChartInstrumentHeader instrument={selectedInstrument} />

      {/* Main Chart Card */}
      <div className="flex flex-col bg-zinc-950/90 border border-zinc-800/80 rounded overflow-hidden shadow-2xl">
        {/* Toolbar */}
        <ChartToolbar
          selectedSymbol={selectedSymbol}
          availableInstruments={availableInstruments}
          interval={interval}
          renderMode={renderMode}
          isLoading={isLoading}
          onSelectInstrument={selectInstrument}
          onSelectRenderMode={setRenderMode}
          onRefresh={refreshHistory}
        />

        {/* Dynamic Crosshair Details Bar */}
        <ChartCrosshairDetails
          hoveredBar={hoveredBar}
          instrument={selectedInstrument}
        />

        {/* Primary Chart Viewport */}
        <div className="w-full h-[540px] relative p-1">
          {isLoading && bars.length === 0 ? (
            <ChartLoadingSkeleton />
          ) : error && bars.length === 0 ? (
            <ChartErrorState error={error} onRetry={refreshHistory} />
          ) : bars.length === 0 ? (
            <ChartEmptyState onSelectDefault={() => selectInstrument("SPY")} />
          ) : (
            <HistoricalChart
              bars={bars}
              renderMode={renderMode}
              instrument={selectedInstrument}
              onHoverBar={setHoveredBar}
              onBackfill={loadOlderHistory}
              hasMore={pagination?.has_more}
              isBackfilling={isBackfilling}
            />
          )}
        </div>

        {/* Data Status & Provenance Bar */}
        <div className="p-2 border-t border-zinc-800/80 bg-zinc-950">
          <ChartDataStatus coverage={coverage} instrument={selectedInstrument} />
        </div>
      </div>

      {/* Accessible Historical Data Table */}
      <HistoricalDataTable bars={bars} instrument={selectedInstrument} />
    </div>
  );
}

export function ChartsPage() {
  return (
    <Suspense fallback={<ChartLoadingSkeleton />}>
      <ChartsContent />
    </Suspense>
  );
}
