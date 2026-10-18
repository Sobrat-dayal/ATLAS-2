"use client";

/**
 * Self-Contained Financial Chart Panel Component for ATLAS Multi-Chart Workspaces (Stage 72 & 73).
 *
 * Implements:
 * - Independent instrument & market series selection
 * - Independent interval & chart-type selection
 * - Independent viewport, pan, zoom, and crosshair inspection
 * - Stage 73 Chart Synchronization Adapter integration:
 *   - Linked crosshairs & precision time guides with coalesced animation frames
 *   - Synchronized visible time ranges (horizontal pan & zoom) with clamping and loop suppression
 *   - Linked canonical financial instrument and interval selection
 *   - Linked chart render modes (candlestick, bar, line, area)
 * - Independent TA-Lib indicator calculations & oscillator subpanes
 * - Independent drawing session store & coordinate mapping (via panelId)
 * - Shared historical data query caching (via chartQueryCache)
 * - Shared live market data streaming with reference-counted deduplication (via sharedSubscriptionManager)
 * - Active panel keyboard focus and outline highlight
 * - Robust error boundary isolation
 */

import React, { useEffect, useRef, useState } from "react";
import {
  ChartInstrumentMetadata,
  ChartRenderMode,
  IndicatorInstanceConfig,
  LiveQuoteDTO,
  LiveChartStatus,
  HoveredBarData,
} from "@/lib/charts";
import { sharedSubscriptionManager } from "@/lib/charts/workspace";
import {
  chartSyncController,
  clampVisibleTimeRange,
  ChartSynchronizationAdapter,
  loopPreventionCoordinator,
} from "@/lib/charts/sync";
import {
  useChartHistory,
  useChartIntervals,
  useChartSync,
  useIndicators,
  useChartReplay,
} from "@/hooks/charts";
import { ReplayToolbar } from "../replay";
import {
  HistoricalChart,
  ChartImperativeActions,
  SynchronizedCrosshairState,
} from "../HistoricalChart";
import { ChartCrosshairDetails } from "../ChartCrosshairDetails";
import {
  ActiveIndicators,
  IndicatorParameterEditor,
  IndicatorPicker,
  IndicatorSubpane,
} from "../indicators";
import {
  ChartEmptyState,
  ChartErrorState,
  ChartLoadingSkeleton,
} from "../ChartEmptyErrorStates";
import { ChartPanelHeader } from "./ChartPanelHeader";
import { ChartPanelErrorBoundary } from "./ChartPanelErrorBoundary";

export interface ChartPanelProps {
  panelId: string;
  panelIndex: number;
  initialSymbol?: string;
  initialInterval?: string;
  initialRenderMode?: ChartRenderMode;
  isActive: boolean;
  onActivate: () => void;
  onRemove?: () => void;
  onUpdateState?: (updates: {
    symbol?: string;
    instrument?: ChartInstrumentMetadata | null;
    interval?: string;
    renderMode?: ChartRenderMode;
  }) => void;
}

export function ChartPanel({
  panelId,
  panelIndex,
  initialSymbol = "SPY",
  initialInterval = "1d",
  initialRenderMode = "candlestick",
  isActive,
  onActivate,
  onRemove,
  onUpdateState,
}: ChartPanelProps) {
  const chartActionsRef = useRef<ChartImperativeActions | null>(null);
  const [linkedCrosshair, setLinkedCrosshair] = useState<SynchronizedCrosshairState | null>(null);

  // 1. Independent historical chart data hook (with shared cache deduplication)
  const {
    selectedSymbol,
    selectedInstrument,
    interval,
    setInterval,
    renderMode,
    setRenderMode,
    bars,
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
  } = useChartHistory(initialSymbol, initialInterval, {
    syncGlobalEntity: isActive,
  });

  // Stage 73 Chart Synchronization Hook
  const {
    getPanelGroup,
    syncCrosshair,
    syncVisibleRange,
    syncInstrument,
    syncInterval,
    syncChartType,
  } = useChartSync();
  const group = getPanelGroup(panelId);

  // Keep parent workspace store in sync with local panel changes without infinite render loops
  const onUpdateStateRef = useRef(onUpdateState);
  useEffect(() => {
    onUpdateStateRef.current = onUpdateState;
  });

  const lastEmittedStateRef = useRef<{
    symbol?: string;
    interval?: string;
    renderMode?: string;
    instrumentId?: string;
  }>({});

  useEffect(() => {
    const last = lastEmittedStateRef.current;
    if (
      last.symbol === selectedSymbol &&
      last.interval === interval &&
      last.renderMode === renderMode &&
      last.instrumentId === selectedInstrument?.entity_id
    ) {
      return;
    }

    lastEmittedStateRef.current = {
      symbol: selectedSymbol,
      interval,
      renderMode,
      instrumentId: selectedInstrument?.entity_id,
    };

    onUpdateStateRef.current?.({
      symbol: selectedSymbol,
      instrument: selectedInstrument,
      interval,
      renderMode,
    });
  }, [selectedSymbol, selectedInstrument, interval, renderMode]);

  // 2. Independent intervals available for this panel's selected instrument
  const { intervals } = useChartIntervals(selectedInstrument?.entity_id || selectedSymbol);

  // 3. Shared reference-counted live market data streaming
  const [liveQuote, setLiveQuote] = useState<LiveQuoteDTO | null>(null);
  const [liveStatus, setLiveStatus] = useState<LiveChartStatus | null>(null);
  const [isFollowingLatest, setIsFollowingLatest] = useState<boolean>(true);

  useEffect(() => {
    if (!selectedInstrument) return;

    // Subscribe panel to shared subscription manager
    const unsubscribe = sharedSubscriptionManager.subscribe(
      panelId,
      selectedInstrument,
      (quote, status) => {
        setLiveQuote(quote);
        setLiveStatus(status);
      },
      (status) => {
        setLiveStatus(status);
      }
    );

    return () => {
      unsubscribe();
    };
  }, [panelId, selectedInstrument]);

  // Stage 75 Historical Chart Replay Hook
  const {
    isPanelInReplay,
    revealedBars,
    cursorBar,
    status: replayStatus,
    playbackSpeed,
  } = useChartReplay();
  const inReplay = isPanelInReplay(panelId);
  const effectiveBars = inReplay ? revealedBars : bars;
  const effectiveLiveQuote = inReplay ? null : liveQuote;

  // 4. Independent TA-Lib indicators for this panel
  const [isIndicatorPickerOpen, setIsIndicatorPickerOpen] = useState(false);
  const [editingIndicator, setEditingIndicator] = useState<IndicatorInstanceConfig | null>(null);

  const {
    catalog,
    isLoadingCatalog,
    activeInstances,
    results: indicatorResults,
    addIndicator,
    updateInstance,
    toggleVisibility,
    removeInstance,
  } = useIndicators({
    instrument: selectedInstrument,
    interval,
    barsCount: effectiveBars.length,
  });

  // 5. Stage 73 Panel Synchronization Adapter Registration
  useEffect(() => {
    const adapter: ChartSynchronizationAdapter = {
      panelId,
      generation: loopPreventionCoordinator.getPanelGeneration(panelId),
      getInstrument: () => selectedInstrument,
      getInterval: () => interval,
      getChartType: () => renderMode,
      getVisibleTimeRange: () => chartActionsRef.current?.getVisibleRange() ?? null,

      applyCrosshair: (payload) => {
        if (payload.timestampSeconds === null) {
          setLinkedCrosshair(null);
          chartActionsRef.current?.clearCrosshairPosition();
          return { panelId, property: "crosshair", result: "APPLIED" };
        }

        // Future isolation: never allow crosshair from external panel to reveal beyond current replay cursor
        if (inReplay && cursorBar) {
          const cursorTimeSec =
            cursorBar.time_unix || Math.floor(new Date(cursorBar.timestamp).getTime() / 1000);
          if (payload.timestampSeconds > cursorTimeSec) {
            return { panelId, property: "crosshair", result: "UNCHANGED", reason: "Replay future isolation" };
          }
        }

        setLinkedCrosshair({
          timestampSeconds: payload.timestampSeconds,
          isoTime: payload.isoTime || new Date(payload.timestampSeconds * 1000).toISOString(),
          sourceSymbol: payload.sourceSymbol,
          sourceInterval: payload.sourceInterval,
          color: group?.color || "#06b6d4",
        });

        if (chartActionsRef.current && payload.price !== undefined) {
          chartActionsRef.current.setCrosshairPosition(payload.price ?? null, payload.timestampSeconds);
        }

        return { panelId, property: "crosshair", result: "APPLIED" };
      },

      clearCrosshair: () => {
        setLinkedCrosshair(null);
        chartActionsRef.current?.clearCrosshairPosition();
      },

      applyVisibleTimeRange: (payload) => {
        if (!chartActionsRef.current) {
          return { panelId, property: "visibleTimeRange", result: "NOT_READY" };
        }
        const minTime = effectiveBars.length > 0 ? effectiveBars[0].time_unix : null;
        const maxTime = effectiveBars.length > 0 ? effectiveBars[effectiveBars.length - 1].time_unix : null;
        const clamped = clampVisibleTimeRange(payload.from, payload.to, minTime, maxTime);

        const ok = chartActionsRef.current.setVisibleRange({
          from: clamped.from,
          to: clamped.to,
        });
        return {
          panelId,
          property: "visibleTimeRange",
          result: ok ? "APPLIED" : "ERROR",
        };
      },

      applyInstrument: async (payload) => {
        if (inReplay) {
          // Replay session is bound to its selected canonical instrument
          return { panelId, property: "instrument", result: "UNCHANGED", reason: "Replay panel isolated" };
        }
        selectInstrument(payload.symbol);
        return { panelId, property: "instrument", result: "APPLIED" };
      },

      applyInterval: async (payload) => {
        if (inReplay) {
          // Replay session is bound to its selected interval
          return { panelId, property: "interval", result: "UNCHANGED", reason: "Replay panel isolated" };
        }
        setInterval(payload.intervalId);
        return { panelId, property: "interval", result: "APPLIED" };
      },

      applyChartType: (payload) => {
        setRenderMode(payload.renderMode);
        return { panelId, property: "chartType", result: "APPLIED" };
      },

      getCapabilities: () => ({
        canSyncCrosshair: true,
        canSyncTimeRange: true,
        canSyncInstrument: true,
        canSyncInterval: true,
        canSyncChartType: true,
        canSyncDrawings: false,
        supportedIntervals: intervals.map((i) => i.interval_id),
        supportedChartTypes: ["candlestick", "bar", "line", "area"],
        hasOHLC: true,
      }),

      isReady: () => !isLoading && bars.length > 0,
    };

    chartSyncController.registerAdapter(adapter);

    return () => {
      chartSyncController.unregisterAdapter(panelId);
    };
  }, [
    panelId,
    selectedInstrument,
    interval,
    renderMode,
    bars,
    isLoading,
    intervals,
    selectInstrument,
    setInterval,
    setRenderMode,
    group?.color,
  ]);

  // Stage 73 Synchronization Interaction Handlers
  const handleHoverBar = (data: HoveredBarData | null) => {
    setHoveredBar(data);
    if (group && group.enabled && group.settings.crosshair) {
      if (data) {
        syncCrosshair(panelId, {
          timestampSeconds: data.time_unix,
          isoTime: data.timestamp,
          sourceInterval: interval,
          price: data.close,
          sourceSymbol: selectedSymbol,
        });
      } else {
        syncCrosshair(panelId, {
          timestampSeconds: null,
          isoTime: null,
          sourceInterval: interval,
          price: null,
          sourceSymbol: selectedSymbol,
        });
      }
    }
  };

  const handleCrosshairLeave = () => {
    setHoveredBar(null);
    if (group && group.enabled && group.settings.crosshair) {
      syncCrosshair(panelId, {
        timestampSeconds: null,
        isoTime: null,
        sourceInterval: interval,
        price: null,
        sourceSymbol: selectedSymbol,
      });
    }
  };

  const handleVisibleTimeRangeChange = (range: { from: number; to: number }) => {
    if (group && group.enabled && group.settings.visibleTimeRange) {
      syncVisibleRange(panelId, {
        from: range.from,
        to: range.to,
        sourceBarsCount: bars.length,
      });
    }
  };

  const handleSelectInstrument = (sym: string) => {
    selectInstrument(sym);
    if (group && group.enabled && group.settings.instrument) {
      const inst = availableInstruments.find((i) => i.display_symbol === sym);
      if (inst) {
        syncInstrument(panelId, {
          canonicalInstrumentId: inst.entity_id,
          symbol: inst.display_symbol,
          assetClass: inst.asset_class,
          currency: inst.price_currency,
          venue: inst.market_or_venue,
          instrument: inst,
        });
      }
    }
  };

  const handleSelectInterval = (intv: string) => {
    setInterval(intv);
    if (group && group.enabled && group.settings.interval) {
      syncInterval(panelId, { intervalId: intv });
    }
  };

  const handleSelectRenderMode = (mode: ChartRenderMode) => {
    setRenderMode(mode);
    if (group && group.enabled && group.settings.chartType) {
      syncChartType(panelId, { renderMode: mode });
    }
  };

  const handleUserPan = () => {
    setIsFollowingLatest(false);
  };

  const handleAtLatest = () => {
    setIsFollowingLatest(true);
  };

  const handleGoToLatest = () => {
    if (chartActionsRef.current) {
      chartActionsRef.current.goToLatest();
    }
    setIsFollowingLatest(true);
  };

  return (
    <ChartPanelErrorBoundary panelId={panelId} onReset={refreshHistory}>
      <div
        tabIndex={0}
        onFocus={onActivate}
        onClick={onActivate}
        className={`w-full h-full flex flex-col bg-zinc-950/95 border rounded overflow-hidden select-none transition-all outline-none ${
          isActive
            ? "border-cyan-500/80 shadow-[0_0_12px_rgba(6,182,212,0.15)] ring-1 ring-cyan-500/40"
            : "border-zinc-800/80 hover:border-zinc-700/80"
        }`}
      >
        {/* Compact Header for this chart panel */}
        <ChartPanelHeader
          panelId={panelId}
          panelIndex={panelIndex}
          isActive={isActive}
          instrument={selectedInstrument}
          symbol={selectedSymbol}
          interval={interval}
          intervals={intervals}
          renderMode={renderMode}
          liveQuote={effectiveLiveQuote}
          availableInstruments={availableInstruments}
          isLoading={isLoading}
          isReplaying={inReplay}
          replayStatus={replayStatus}
          playbackSpeed={playbackSpeed}
          onActivate={onActivate}
          onSelectInstrument={handleSelectInstrument}
          onSelectInterval={handleSelectInterval}
          onSelectRenderMode={handleSelectRenderMode}
          onRefresh={refreshHistory}
          onGoToLatest={handleGoToLatest}
          onResetView={handleGoToLatest}
          onOpenIndicators={() => setIsIndicatorPickerOpen(true)}
          activeIndicatorCount={activeInstances.length}
        />

        {/* Stage 75: Institutional Replay Playback Toolbar when panel is in replay mode */}
        {inReplay && <ReplayToolbar />}

        {/* Dynamic Crosshair Details Strip */}
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

        {/* Primary Chart Viewport (with panelId passed for Drawing Isolation & Sync) */}
        <div className="w-full flex-1 min-h-[180px] relative p-1 bg-black">
          {isLoading && effectiveBars.length === 0 ? (
            <ChartLoadingSkeleton />
          ) : error && effectiveBars.length === 0 ? (
            <ChartErrorState error={error} onRetry={refreshHistory} />
          ) : effectiveBars.length === 0 ? (
            <ChartEmptyState onSelectDefault={() => selectInstrument("SPY")} />
          ) : (
            <HistoricalChart
              bars={effectiveBars}
              renderMode={renderMode}
              instrument={selectedInstrument}
              liveQuote={effectiveLiveQuote}
              indicatorResults={indicatorResults}
              activeIndicators={activeInstances}
              onHoverBar={handleHoverBar}
              onCrosshairLeave={handleCrosshairLeave}
              onVisibleTimeRangeChange={handleVisibleTimeRangeChange}
              synchronizedCrosshair={linkedCrosshair}
              onBackfill={inReplay ? undefined : loadOlderHistory}
              hasMore={inReplay ? false : pagination?.has_more}
              isBackfilling={isBackfilling}
              onUserPan={handleUserPan}
              onAtLatest={handleAtLatest}
              chartActionsRef={chartActionsRef}
              panelId={panelId}
            />
          )}
        </div>

        {/* Attached Oscillator Subpanes (RSI, MACD, etc.) */}
        {activeInstances.map((inst) => {
          const defn = catalog.find((d) => d.indicator_id === inst.indicator_id);
          const res = indicatorResults.find((r) => r.instance_id === inst.instance_id);
          if (res?.rendering_target !== "INDICATOR_PANE" && defn?.rendering_target !== "INDICATOR_PANE") {
            return null;
          }
          return (
            <IndicatorSubpane
              key={inst.instance_id}
              instance={inst}
              definition={defn}
              result={res}
              hoveredBar={hoveredBar}
              onToggleVisibility={() => toggleVisibility(inst.instance_id)}
              onConfigure={() => setEditingIndicator(inst)}
              onRemove={() => removeInstance(inst.instance_id)}
            />
          );
        })}

        {/* Per-panel Indicator Modals */}
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
    </ChartPanelErrorBoundary>
  );
}
