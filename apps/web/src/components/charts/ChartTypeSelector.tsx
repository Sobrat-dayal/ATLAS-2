"use client";

/**
 * Professional Financial Chart Type Selector for ATLAS Charts (Stage 68).
 *
 * Implements switching across 4 foundational financial renderers:
 * 1. Candlestick (Real Open, High, Low, Close with true wicks & bodies)
 * 2. OHLC Bar (Traditional High-Low vertical spine with left Open and right Close ticks)
 * 3. Line (Qualified Close price series)
 * 4. Area (Qualified Close series with subtle translucent baseline gradient)
 */

import React from "react";
import { Activity, BarChart2, CandlestickChart, LineChart } from "lucide-react";
import { ChartRenderMode } from "@/lib/charts";

export interface ChartTypeSelectorProps {
  selectedMode: ChartRenderMode;
  onSelectMode: (mode: ChartRenderMode) => void;
  hasOhlc?: boolean;
}

interface TypeOption {
  mode: ChartRenderMode;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  requiresOhlc: boolean;
  tooltip: string;
}

const TYPE_OPTIONS: TypeOption[] = [
  {
    mode: "candlestick",
    label: "Candles",
    icon: CandlestickChart,
    requiresOhlc: true,
    tooltip: "Japanese Candlestick Chart (Open, High, Low, Close)",
  },
  {
    mode: "bar",
    label: "OHLC",
    icon: BarChart2,
    requiresOhlc: true,
    tooltip: "Traditional Financial OHLC Bars (Left Open tick, Right Close tick)",
  },
  {
    mode: "line",
    label: "Line",
    icon: LineChart,
    requiresOhlc: false,
    tooltip: "Close Price Line Chart",
  },
  {
    mode: "area",
    label: "Area",
    icon: Activity,
    requiresOhlc: false,
    tooltip: "Area Chart (Close price with filled baseline gradient)",
  },
];

export function ChartTypeSelector({
  selectedMode,
  onSelectMode,
  hasOhlc = true,
}: ChartTypeSelectorProps) {
  return (
    <div
      role="group"
      aria-label="Chart Type Selector"
      className="flex items-center gap-0.5 bg-zinc-950 border border-zinc-800/90 rounded p-0.5 text-xs select-none"
    >
      {TYPE_OPTIONS.map(({ mode, label, icon: Icon, requiresOhlc, tooltip }) => {
        const isSelected = selectedMode === mode;
        const isDisabled = requiresOhlc && !hasOhlc;

        return (
          <button
            key={mode}
            type="button"
            role="button"
            aria-pressed={isSelected}
            disabled={isDisabled}
            onClick={() => {
              if (!isDisabled) {
                onSelectMode(mode);
              }
            }}
            className={`flex items-center gap-1.5 px-2 py-1 rounded transition-colors text-[11px] font-medium ${
              isSelected
                ? "bg-zinc-800 text-zinc-100 shadow-sm border border-zinc-700/80"
                : isDisabled
                ? "text-zinc-600 opacity-40 cursor-not-allowed"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
            }`}
            title={isDisabled ? "OHLC data not available for this series" : tooltip}
          >
            <Icon
              className={`w-3.5 h-3.5 ${
                mode === "candlestick"
                  ? "text-emerald-400"
                  : mode === "bar"
                  ? "text-amber-400"
                  : mode === "line"
                  ? "text-sky-400"
                  : "text-cyan-400"
              }`}
            />
            <span className="hidden sm:inline">{label}</span>
          </button>
        );
      })}
    </div>
  );
}
