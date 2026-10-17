"use client";

/**
 * Master Charts Workspace Page for ATLAS (Stage 67).
 *
 * Implements the institutional Bloomberg/TradingView-inspired workspace at /charts,
 * integrating Stage 66 historical OHLCV candles with Stage 67 live market data
 * streaming, genuine Last-price overlay, transport/freshness status, and controls.
 */

import React, { Suspense, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Activity, CandlestickChart } from "lucide-react";
import { useChartHistory, useChartIntervals, useIndicators, useLiveChart } from "@/hooks/charts";
import { IndicatorInstanceConfig } from "@/lib/charts";
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
  ActiveIndicators,
  IndicatorParameterEditor,
  IndicatorPicker,
} from "./indicators";
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

  // Stage 69 Technical Indicator State & Calculations
  const [isIndicatorPickerOpen, setIsIndicatorPickerOpen] = useState(false);
  const [editingIndicator, setEditingIndicator] = useState<IndicatorInstanceConfig | null>(null);

  const {
    catalog,
    isLoadingCatalog,
    activeInstances,
    results: indicatorResults,
    isCalculating: isIndicatorsCalculating,
    calculationError: indicatorsError,
    addIndicator,
    updateInstance,
    toggleVisibility,
    removeInstance,
  } = useIndicators({
    instrument: selectedInstrument,
    interval,
    barsCount: bars.length,
  });

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
                STAGE 69
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 rounded flex items-center gap-1">
                <Activity className="w-3 h-3 text-emerald-400" />
                <span>TECHNICAL INDICATOR INFRASTRUCTURE</span>
              </span>
              <span className="text-[10px] font-mono text-zinc-500 hidden sm:inline">
                [STAGE 68 MULTI-TIMEFRAME & ADVANCED TYPES]
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Multi-timeframe financial charting, verified OHLCV aggregation, extensible technical indicators, deterministic calculations, and chart overlays.
            </p>
          </div>
        </div>
      </div>

      {/* Instrument Overview Header */}
      <ChartInstrumentHeader instrument={selectedInstrument} />

      {/* Main Chart Card */}
      <div className="flex flex-col bg-zinc-950/90 border border-zinc-800/80 rounded overflow-hidden shadow-2xl">
        {/* Toolbar with Interval & Chart Type Selectors, Indicators & Live Controls */}
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
          onOpenIndicators={() => setIsIndicatorPickerOpen(true)}
          activeIndicatorCount={activeInstances.length}
        />

        {/* Detailed Live Quote Metrics Strip */}
        <LatestQuoteDetails quote={liveQuote} instrument={selectedInstrument} />

        {/* Dynamic Crosshair Details Bar (with real-time indicator inspection) */}
        <ChartCrosshairDetails
          hoveredBar={hoveredBar}
          instrument={selectedInstrument}
          indicatorResults={indicatorResults}
          activeIndicators={activeInstances}
        />

        {/* Active Indicators Legend Strip */}
        {activeInstances.length > 0 && (
          <ActiveIndicators
            instances={activeInstances}
            catalog={catalog}
            results={indicatorResults}
            onToggleVisibility={toggleVisibility}
            onConfigure={(inst) => setEditingIndicator(inst)}
            onRemove={removeInstance}
          />
        )}

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
              indicatorResults={indicatorResults}
              activeIndicators={activeInstances}
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

      {/* Stage 69 Indicator Modals */}
      <IndicatorPicker
        isOpen={isIndicatorPickerOpen}
        catalog={catalog}
        isLoading={isLoadingCatalog}
        activeCount={activeInstances.length}
        onClose={() => setIsIndicatorPickerOpen(false)}
        onSelect={(indicatorId: string) => {
          addIndicator(indicatorId);
        }}
      />

      {editingIndicator && (
        <IndicatorParameterEditor
          isOpen={!!editingIndicator}
          instance={editingIndicator}
          definition={catalog.find((d) => d.indicator_id === editingIndicator.indicator_id)}
          onClose={() => setEditingIndicator(null)}
          onSave={(instanceId, updates) => {
            updateInstance(instanceId, updates);
            setEditingIndicator(null);
          }}
        />
      )}
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
