"use client";

/**
 * Master Charts Workspace Page for ATLAS (Stage 72).
 *
 * Implements the institutional Bloomberg/TradingView-inspired multi-chart workspace at /charts,
 * integrating Stage 72 independent financial chart panels, resizable chart grids,
 * multi-instrument market analysis, per-panel technical indicators, drawing isolation,
 * shared live market data and high-performance chart workspace management.
 */

import React, { Suspense, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Activity, CandlestickChart, Layers } from "lucide-react";
import { useChartHistory, useChartIntervals, useIndicators, useLiveChart, useMultiChartWorkspace } from "@/hooks/charts";
import { ChartInstrumentHeader } from "./ChartInstrumentHeader";
import { ChartDataStatus } from "./ChartDataStatus";
import { HistoricalDataTable } from "./HistoricalDataTable";
import { LiveMarketDataStatus } from "./LiveMarketDataStatus";
import {
  ActiveIndicators,
  IndicatorInspectorTable,
  IndicatorPicker,
  IndicatorSubpane,
} from "./indicators";
import {
  ChartLoadingSkeleton,
} from "./ChartEmptyErrorStates";
import {
  ChartLayoutSelector,
  MultiChartWorkspace,
} from "./workspace";
import { ChartSyncButton } from "./sync";

function ChartsContent() {
  const searchParams = useSearchParams();
  const urlSymbol = searchParams.get("symbol") || searchParams.get("ticker");
  const urlInstrumentId = searchParams.get("instrument_id") || searchParams.get("id");
  const initialParam = urlInstrumentId || urlSymbol || "SPY";

  // Stage 72 Multi-Chart Workspace State Hook
  const {
    layoutId,
    panelIds,
    activePanelId,
    activePanel,
    panels,
    setLayoutId,
    setActivePanelId,
    updatePanel,
  } = useMultiChartWorkspace();

  // Sync initial URL param to active panel on mount
  useEffect(() => {
    if (initialParam && activePanel && activePanel.symbol !== initialParam) {
      updatePanel(activePanelId, { symbol: initialParam });
    }
  }, [initialParam]);

  // Active panel data resolution (powered by shared chartQueryCache)
  const activeSymbol = activePanel?.symbol || "SPY";
  const activeInterval = activePanel?.interval || "1d";

  const {
    selectedInstrument,
    interval,
    intervalSourceKind,
    derivedSourceInterval,
    bars,
    coverage,
    refreshHistory,
  } = useChartHistory(activeSymbol, activeInterval, { syncGlobalEntity: true });

  const { intervals } = useChartIntervals(selectedInstrument?.entity_id || activeSymbol);

  // Active panel live stream status (powered by sharedSubscriptionManager)
  const {
    quote: liveQuote,
    connectionState,
    freshnessStatus,
    delayStatus,
    liveCapability,
    provider: liveProvider,
    venue: liveVenue,
  } = useLiveChart(selectedInstrument);

  // Active panel indicators (for numerical inspection table)
  const {
    catalog,
    activeInstances,
    results: indicatorResults,
  } = useIndicators({
    instrument: selectedInstrument,
    interval: activeInterval,
    barsCount: bars.length,
  });

  const activePanelIndex = panelIds.indexOf(activePanelId);
  const activePanelDisplayIndex = activePanelIndex >= 0 ? activePanelIndex + 1 : 1;

  return (
    <div className="w-full flex flex-col gap-3 p-4 md:p-6 min-h-screen bg-black text-zinc-100 font-sans">
      {/* Workspace Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-zinc-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded bg-cyan-950/60 border border-cyan-800/60 flex items-center justify-center">
            <CandlestickChart className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold tracking-tight text-zinc-100 font-mono">
                CHARTS
              </h1>
              <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 rounded">
                STAGE 73
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 rounded flex items-center gap-1">
                <Activity className="w-3 h-3 text-emerald-400" />
                <span>PROFESSIONAL CHART SYNCHRONIZATION V1: LINKED CROSSHAIRS & TIME RANGES</span>
              </span>
              <span className="text-[10px] font-mono text-zinc-500 hidden sm:inline">
                [STAGE 68 MULTI-TIMEFRAME & ADVANCED TYPES | STAGE 69 TECHNICAL INDICATOR INFRASTRUCTURE | STAGE 70 PRODUCTION TECHNICAL ANALYSIS ENGINE (TA-LIB) | STAGE 71 DRAWING SUITE | STAGE 72 MULTI-CHART | STAGE 73 SYNCHRONIZATION]
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Institutional multi-chart financial workstation with linked crosshairs, synchronized time ranges, intelligent synchronization groups, multi-market calendar alignment and loop-free coordination.
            </p>
          </div>
        </div>

        {/* Top Controls: Active Panel Badge, Chart Sync Button & Layout Selector */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-zinc-900 border border-zinc-800 rounded text-xs font-mono">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-zinc-400">Active:</span>
            <span className="font-semibold text-cyan-300">
              P{activePanelDisplayIndex} ({activeSymbol})
            </span>
          </div>

          <ChartSyncButton
            workspaceState={{
              layoutId,
              panelIds,
              activePanelId,
              splitRatios: {},
              panels,
              isMobileTabMode: false,
              activeMobileTabId: activePanelId,
            }}
          />

          <ChartLayoutSelector
            currentLayout={layoutId}
            onSelectLayout={setLayoutId}
          />
        </div>
      </div>

      {/* Active Instrument Overview Header */}
      <ChartInstrumentHeader instrument={selectedInstrument} />

      {/* Master Multi-Chart Workspace Container (Single, 2-Columns, 2-Rows, 3-Focus, 4-Grid) */}
      <MultiChartWorkspace
        layoutId={layoutId}
        panelIds={panelIds}
        activePanelId={activePanelId}
        panels={panels}
        onActivatePanel={setActivePanelId}
        onUpdatePanelState={updatePanel}
      />

      {/* Active Chart Provenance & Market Data Freshness Footer Strip */}
      <div className="p-3 border border-zinc-800/80 rounded bg-zinc-950/90 flex flex-col gap-2">
        <div className="flex items-center justify-between pb-1 border-b border-zinc-900 text-xs font-mono">
          <span className="text-zinc-400 font-semibold uppercase tracking-wider text-[11px]">
            Active Panel Status: Panel {activePanelDisplayIndex} ({activeSymbol})
          </span>
          <span className="text-[10px] text-zinc-500">
            Independent per-panel data quality, coverage provenance & entitlements
          </span>
        </div>

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

      {/* Accessible Historical Data Table for Active Panel */}
      <HistoricalDataTable bars={bars} instrument={selectedInstrument} />

      {/* Stage 70 Accessible Technical Indicator Numerical Inspector Table for Active Panel */}
      <IndicatorInspectorTable
        bars={bars}
        catalog={catalog}
        instances={activeInstances}
        results={indicatorResults}
      />
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
