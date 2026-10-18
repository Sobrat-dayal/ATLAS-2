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
  IndicatorCalculationResult,
  IndicatorInstanceConfig,
  formatBarDate,
  formatPercentChange,
  formatPrice,
  formatVolume,
} from "@/lib/charts";

export interface ChartCrosshairDetailsProps {
  hoveredBar: HoveredBarData | null;
  instrument: ChartInstrumentMetadata | null;
  indicatorResults?: IndicatorCalculationResult[];
  activeIndicators?: IndicatorInstanceConfig[];
}

export function ChartCrosshairDetails({
  hoveredBar,
  instrument,
  indicatorResults = [],
  activeIndicators = [],
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

      {/* Stage 70 Active Technical Indicator Values at hovered bar */}
      {activeIndicators.map((inst) => {
        if (!inst.visible) return null;
        const res = indicatorResults.find((r) => r.instance_id === inst.instance_id);
        const barTimeUnix =
          typeof hoveredBar.timestamp === "number"
            ? hoveredBar.timestamp
            : !isNaN(Number(hoveredBar.timestamp))
              ? Number(hoveredBar.timestamp)
              : Math.floor(new Date(hoveredBar.timestamp).getTime() / 1000);

        const p = inst.parameters;
        let paramLabel = "";
        if (inst.indicator_id === "atlas.macd") {
          paramLabel = `(${p["fast_period"] ?? 12},${p["slow_period"] ?? 26},${p["signal_period"] ?? 9})`;
        } else if (inst.indicator_id === "atlas.stoch") {
          paramLabel = `(${p["fastk_period"] ?? 5},${p["slowk_period"] ?? 3},${p["slowd_period"] ?? 3})`;
        } else if (inst.indicator_id === "atlas.bbands") {
          paramLabel = `(${p["period"] ?? 20},${p["nbdevup"] ?? 2},${p["nbdevdn"] ?? 2})`;
        } else if (p["period"] != null) {
          paramLabel = `(${p["period"]})`;
        }

        const name = inst.indicator_id.replace("atlas.", "").toUpperCase();
        const label = `${name}${paramLabel}`;
        const color = inst.color || "#38bdf8";

        const seriesList = res?.series || [];

        return (
          <div key={inst.instance_id} className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: color }}
            />
            <span className="text-zinc-400 font-semibold">{label}:</span>

            {seriesList.length === 0 ? (
              <span className="text-zinc-600">—</span>
            ) : seriesList.length === 1 ? (
              (() => {
                const match = seriesList[0].points.find((pt) => Math.abs(pt.time_unix - barTimeUnix) <= 1);
                if (match && match.value !== null && match.value !== undefined) {
                  return (
                    <span className="font-semibold text-zinc-100">
                      {formatPrice(match.value, precision)}
                    </span>
                  );
                } else if (match?.status === "WARMUP") {
                  return <span className="text-zinc-500 italic text-[11px]">warmup</span>;
                }
                return <span className="text-zinc-600">—</span>;
              })()
            ) : (
              <div className="flex items-center gap-1.5">
                {seriesList.map((s) => {
                  const match = s.points.find((pt) => Math.abs(pt.time_unix - barTimeUnix) <= 1);
                  const sPrefix = s.name.slice(0, 1).toUpperCase();
                  return (
                    <span key={s.series_id} className="text-zinc-300 font-mono text-[11px]">
                      <span className="text-zinc-500 mr-0.5">{sPrefix}:</span>
                      {match && match.value !== null && match.value !== undefined ? (
                        <span className="font-semibold text-zinc-100">
                          {s.series_id === "histogram" && match.value >= 0 ? `+` : ""}
                          {formatPrice(match.value, 2)}
                        </span>
                      ) : (
                        <span className="text-zinc-600">—</span>
                      )}
                    </span>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
