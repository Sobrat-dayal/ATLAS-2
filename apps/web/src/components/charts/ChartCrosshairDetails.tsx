"use client";

/**
 * Crosshair Details Inspection Component for ATLAS Charts V1 (Stage 66).
 *
 * Displays exact OHLC values, volume, change %, and session date
 * of the currently hovered or latest historical bar.
 */

import React from "react";
import {
  ChartInstrumentMetadata,
  HoveredBarData,
  formatBarDate,
  formatPercentChange,
  formatPrice,
  formatVolume,
} from "@/lib/charts";

export interface ChartCrosshairDetailsProps {
  hoveredBar: HoveredBarData | null;
  instrument: ChartInstrumentMetadata | null;
}

export function ChartCrosshairDetails({
  hoveredBar,
  instrument,
}: ChartCrosshairDetailsProps) {
  if (!hoveredBar) {
    return (
      <div className="flex items-center gap-4 px-3 py-1.5 bg-zinc-950/70 border-b border-zinc-800/80 text-xs font-mono text-zinc-500">
        <span>Hover over chart candles to inspect exact OHLCV values.</span>
      </div>
    );
  }

  const precision = instrument?.asset_class === "fx" && instrument.display_symbol === "EURUSD" ? 4 : 2;
  const changeValue = hoveredBar.close - hoveredBar.open;
  const changePct = hoveredBar.changePercent ?? 0;
  const changeColor = changeValue > 0 ? "text-emerald-400" : changeValue < 0 ? "text-red-400" : "text-zinc-400";

  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-1 px-3 py-1.5 bg-zinc-950/90 border-b border-zinc-800/80 text-xs font-mono">
      {/* Date */}
      <div className="flex items-center gap-1.5 text-zinc-300">
        <span className="text-zinc-500">DATE:</span>
        <span className="font-semibold">{formatBarDate(hoveredBar.timestamp)}</span>
      </div>

      {/* Open */}
      <div className="flex items-center gap-1.5 text-zinc-300">
        <span className="text-zinc-500">O:</span>
        <span className="font-semibold text-zinc-100">{formatPrice(hoveredBar.open, precision)}</span>
      </div>

      {/* High */}
      <div className="flex items-center gap-1.5 text-zinc-300">
        <span className="text-zinc-500">H:</span>
        <span className="font-semibold text-zinc-100">{formatPrice(hoveredBar.high, precision)}</span>
      </div>

      {/* Low */}
      <div className="flex items-center gap-1.5 text-zinc-300">
        <span className="text-zinc-500">L:</span>
        <span className="font-semibold text-zinc-100">{formatPrice(hoveredBar.low, precision)}</span>
      </div>

      {/* Close */}
      <div className="flex items-center gap-1.5 text-zinc-300">
        <span className="text-zinc-500">C:</span>
        <span className={`font-semibold ${changeColor}`}>
          {formatPrice(hoveredBar.close, precision)}
        </span>
      </div>

      {/* Change & % Change */}
      <div className="flex items-center gap-1.5 font-semibold">
        <span className={changeColor}>
          {changeValue > 0 ? "+" : ""}
          {formatPrice(changeValue, precision)} ({formatPercentChange(changePct)})
        </span>
      </div>

      {/* Volume if present */}
      {instrument?.has_volume !== false && hoveredBar.volume !== null && (
        <div className="flex items-center gap-1.5 text-zinc-400">
          <span className="text-zinc-500">VOL:</span>
          <span className="text-zinc-200">{formatVolume(hoveredBar.volume)}</span>
        </div>
      )}
    </div>
  );
}
