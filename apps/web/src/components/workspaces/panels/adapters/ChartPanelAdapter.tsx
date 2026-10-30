"use client";

import React, { useEffect, useState } from "react";
import { ChartPanel } from "@/components/charts/workspace/ChartPanel";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";

interface ChartPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

export function ChartPanelAdapter({
  panel,
  context,
  onUpdateContext,
  onUpdateConfig,
}: ChartPanelAdapterProps) {
  // Config or linked context
  const initialSymbol =
    (!panel.independent_mode && (context.INSTRUMENT as string)) ||
    (panel.configuration?.symbol as string) ||
    "AAPL";

  const [currentSymbol, setCurrentSymbol] = useState<string>(initialSymbol);
  const [currentInterval, setCurrentInterval] = useState<string>(
    (!panel.independent_mode && (context.TIMEFRAME as string)) ||
    (panel.configuration?.timeframe as string) ||
    "1d"
  );

  useEffect(() => {
    if (!panel.independent_mode) {
      if (context.INSTRUMENT && typeof context.INSTRUMENT === "string") {
        setCurrentSymbol(context.INSTRUMENT);
      }
      if (context.TIMEFRAME && typeof context.TIMEFRAME === "string") {
        setCurrentInterval(context.TIMEFRAME);
      }
    }
  }, [context.INSTRUMENT, context.TIMEFRAME, panel.independent_mode]);

  const handleUpdateState = (updates: { symbol?: string; interval?: string }) => {
    if (updates.symbol && updates.symbol !== currentSymbol) {
      setCurrentSymbol(updates.symbol);
      onUpdateConfig({ symbol: updates.symbol });
      if (!panel.independent_mode) {
        onUpdateContext({ INSTRUMENT: updates.symbol, COMPANY: updates.symbol });
      }
    }
    if (updates.interval && updates.interval !== currentInterval) {
      setCurrentInterval(updates.interval);
      onUpdateConfig({ timeframe: updates.interval });
      if (!panel.independent_mode) {
        onUpdateContext({ TIMEFRAME: updates.interval });
      }
    }
  };

  return (
    <div className="w-full h-full relative overflow-hidden bg-atlas-surface-0">
      <ChartPanel
        panelId={panel.panel_instance_id}
        panelIndex={0}
        initialSymbol={currentSymbol}
        initialInterval={currentInterval}
        initialRenderMode="candlestick"
        isActive={true}
        onActivate={() => {}}
        onUpdateState={handleUpdateState}
      />
    </div>
  );
}

