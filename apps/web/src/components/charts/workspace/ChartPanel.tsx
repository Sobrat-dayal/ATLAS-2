"use client";

/**
 * Self-Contained Financial Chart Panel Component for ATLAS Multi-Chart Workspaces (Stage 72).
 *
 * Implements:
 * - Independent instrument & market series selection
 * - Independent interval & chart-type selection
 * - Independent viewport, pan, zoom, and crosshair inspection
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
} from "@/lib/charts";
import { sharedSubscriptionManager } from "@/lib/charts/workspace";
import {
  useChartHistory,
  useChartIntervals,
  useIndicators,
} from "@/hooks/charts";
import { HistoricalChart } from "../HistoricalChart";
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
  const chartActionsRef = useRef<{ goToLatest: () => void } | null>(null);

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

  // Keep parent workspace store in sync with local panel changes
  useEffect(() => {
    if (onUpdateState) {
      onUpdateState({
        symbol: selectedSymbol,
        instrument: selectedInstrument,
        interval,
        renderMode,
      });
    }
  }, [selectedSymbol, selectedInstrument, interval, renderMode, onUpdateState]);

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
    barsCount: bars.length,
  });

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
          liveQuote={liveQuote}
          availableInstruments={availableInstruments}
          isLoading={isLoading}
          onActivate={onActivate}
          onSelectInstrument={selectInstrument}
          onSelectInterval={setInterval}
          onSelectRenderMode={setRenderMode}
          onRefresh={refreshHistory}
          onGoToLatest={handleGoToLatest}
          onResetView={handleGoToLatest}
          onOpenIndicators={() => setIsIndicatorPickerOpen(true)}
          activeIndicatorCount={activeInstances.length}
        />

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

        {/* Primary Chart Viewport (with panelId passed for Drawing Isolation) */}
        <div className="w-full flex-1 min-h-[180px] relative p-1 bg-black">
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
