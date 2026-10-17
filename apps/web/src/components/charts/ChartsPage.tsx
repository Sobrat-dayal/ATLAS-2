"use client";

/**
 * Master Charts Workspace Page for ATLAS (Stage 67).
 *
 * Implements the institutional Bloomberg/TradingView-inspired workspace at /charts,
 * integrating Stage 66 historical OHLCV candles with Stage 67 live market data
 * streaming, genuine Last-price overlay, transport/freshness status, and controls.
 */

import React, { Suspense, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Activity, CandlestickChart } from "lucide-react";
import { useChartHistory, useChartIntervals, useLiveChart } from "@/hooks/charts";
import { ChartInstrumentHeader } from "./ChartInstrumentHeader";
import { ChartToolbar } from "./ChartToolbar";
import { ChartCrosshairDetails } from "./ChartCrosshairDetails";
import { HistoricalChart } from "./HistoricalChart";
import { ChartDataStatus } from "./ChartDataStatus";
import { HistoricalDataTable } from "./HistoricalDataTable";
import { LiveMarketDataStatus } from "./LiveMarketDataStatus";
import { LiveChartControls } from "./LiveChartControls";
import { LatestQuoteDetails } from "./LatestQuoteDetails";
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
    setInterval,
    renderMode,
    setRenderMode,
    intervalSourceKind,
    derivedSourceInterval,
    bars,
    coverage,
    pagination,
    isLoading,
    isBackfilling,
    error,
    hoveredBar,
    selectInstrument,
    loadOlderHistory,
    refreshHistory,
    setHoveredBar,
    availableInstruments,
  } = useChartHistory(initialParam);

  const { intervals } = useChartIntervals(selectedInstrument?.entity_id || selectedSymbol);

  const {
    quote: liveQuote,
    connectionState,
    freshnessStatus,
    delayStatus,
    liveCapability,
    isPaused,
    isFollowingLatest,
    provider: liveProvider,
    venue: liveVenue,
    togglePause,
    setFollowingLatest,
  } = useLiveChart(selectedInstrument);

  const chartActionsRef = useRef<{ goToLatest: () => void } | null>(null);

  const handleGoToLatest = () => {
    if (chartActionsRef.current) {
      chartActionsRef.current.goToLatest();
    }
    setFollowingLatest(true);
  };

  const liveControls = (
    <LiveChartControls
      isPaused={isPaused}
      isFollowingLatest={isFollowingLatest}
      liveCapability={liveCapability}
      onTogglePause={togglePause}
      onGoToLatest={handleGoToLatest}
    />
  );

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
                STAGE 68
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 rounded flex items-center gap-1">
                <Activity className="w-3 h-3 text-emerald-400" />
                <span>MULTI-TIMEFRAME & ADVANCED TYPES</span>
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Multi-timeframe financial charting, verified OHLCV aggregation, session-aware time axes, 4 chart types and live streaming.
            </p>
          </div>
        </div>
      </div>

      {/* Instrument Overview Header */}
      <ChartInstrumentHeader instrument={selectedInstrument} />

      {/* Main Chart Card */}
      <div className="flex flex-col bg-zinc-950/90 border border-zinc-800/80 rounded overflow-hidden shadow-2xl">
        {/* Toolbar with Interval & Chart Type Selectors & Live Controls */}
        <ChartToolbar
          selectedSymbol={selectedSymbol}
          availableInstruments={availableInstruments}
          interval={interval}
          onSelectInterval={setInterval}
          intervals={intervals}
          renderMode={renderMode}
          isLoading={isLoading}
          onSelectInstrument={selectInstrument}
          onSelectRenderMode={setRenderMode}
          onRefresh={refreshHistory}
          liveControls={liveControls}
        />

        {/* Detailed Live Quote Metrics Strip */}
        <LatestQuoteDetails quote={liveQuote} instrument={selectedInstrument} />

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
              liveQuote={liveQuote}
              onHoverBar={setHoveredBar}
              onBackfill={loadOlderHistory}
              hasMore={pagination?.has_more}
              isBackfilling={isBackfilling}
              onUserPan={() => setFollowingLatest(false)}
              onAtLatest={() => setFollowingLatest(true)}
              chartActionsRef={chartActionsRef}
            />
          )}
        </div>

        {/* Live Market Data Status & Coverage Provenance Footer */}
        <div className="p-2 border-t border-zinc-800/80 bg-zinc-950 flex flex-col gap-2">
          <LiveMarketDataStatus
            connectionState={connectionState}
            freshnessStatus={freshnessStatus}
            delayStatus={delayStatus}
            liveCapability={liveCapability}
            quote={liveQuote}
            instrument={selectedInstrument}
            provider={liveProvider}
            venue={liveVenue}
          />
          <div className="border-t border-zinc-900 pt-2">
            <ChartDataStatus
              coverage={coverage}
              instrument={selectedInstrument}
              interval={interval}
              intervalSourceKind={intervalSourceKind}
              derivedSourceInterval={derivedSourceInterval}
            />
          </div>
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
