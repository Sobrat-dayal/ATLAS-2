"use client";

/**
 * Indicator Subpane Container Component (Stage 69).
 *
 * Provides the architectural foundation for indicators requiring an independent
 * vertical scale (e.g. future Stage 70 oscillators such as RSI, MACD, or Stochastic),
 * maintaining time-scale synchronization with the primary chart.
 */

import React, { useEffect, useRef } from "react";
import {
  IndicatorCalculationResult,
  IndicatorInstanceConfig,
} from "@/lib/charts";

export interface IndicatorSubpaneProps {
  instance: IndicatorInstanceConfig;
  result?: IndicatorCalculationResult;
  height?: number;
  onRemove?: () => void;
  onToggleVisibility?: () => void;
}

export function IndicatorSubpane({
  instance,
  result,
  height = 120,
}: IndicatorSubpaneProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Stage 69 sets up the subpane container contract.
    // Stage 70 will mount dedicated Lightweight Charts subpane / oscillator series here.
  }, [instance, result]);

  if (!instance.visible) return null;

  return (
    <div
      ref={containerRef}
      style={{ height: `${height}px` }}
      className="w-full relative border-t border-zinc-800/80 bg-zinc-950/95 flex flex-col justify-between p-2 text-xs font-mono select-none"
    >
      <div className="flex items-center justify-between text-[11px] text-zinc-400">
        <div className="flex items-center gap-1.5">
          <span
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: instance.color || "#38bdf8" }}
          />
          <span className="font-semibold text-zinc-200">
            {instance.indicator_id.toUpperCase()} ({String(instance.parameters["period"] || "")})
          </span>
          <span className="text-zinc-500">[Subpane Infrastructure]</span>
        </div>
        <div className="text-[10px] text-zinc-500">
          Scale: Independent (0-100 or Oscillator)
        </div>
      </div>

      <div className="flex items-center justify-center text-zinc-600 text-[11px]">
        {result?.status === "INSUFFICIENT_HISTORY" ? (
          <span className="text-rose-400">Insufficient historical observations</span>
        ) : (
          <span>Time-aligned subpane adapter ready for Stage 70 TA-Lib oscillators</span>
        )}
      </div>

      <div className="flex items-center justify-between text-[9px] text-zinc-600">
        <span>Aligned to primary time-scale</span>
        <span>Stage 69 Foundation</span>
      </div>
    </div>
  );
}
