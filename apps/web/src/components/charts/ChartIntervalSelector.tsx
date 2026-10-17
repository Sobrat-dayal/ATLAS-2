"use client";

/**
 * Professional Financial Chart Interval Selector for ATLAS Charts (Stage 68).
 *
 * Implements:
 * - High-density segmented controls for canonical intervals:
 *   1m, 5m, 15m, 30m, 1h, 4h, 1D, 1W, 1M.
 * - Dynamic availability states: AVAILABLE_NATIVE, AVAILABLE_DERIVED, UNAVAILABLE.
 * - Truthful visual feedback: disables unsupported timeframes with explanatory tooltips.
 * - Derived interval lineage indicators (e.g. "Derived from 1d daily bars").
 * - Full keyboard navigation and screen-reader accessibility.
 */

import React, { useState } from "react";
import { Info } from "lucide-react";
import { ChartIntervalOptionDTO } from "@/lib/charts";

export interface ChartIntervalSelectorProps {
  selectedInterval: string;
  intervals: ChartIntervalOptionDTO[];
  onSelectInterval: (interval: string) => void;
  isLoading?: boolean;
}

const CANONICAL_INTERVALS_FALLBACK = [
  { id: "1m", label: "1m" },
  { id: "5m", label: "5m" },
  { id: "15m", label: "15m" },
  { id: "30m", label: "30m" },
  { id: "1h", label: "1h" },
  { id: "4h", label: "4h" },
  { id: "1d", label: "1D" },
  { id: "1w", label: "1W" },
  { id: "1M", label: "1M" },
];

export function ChartIntervalSelector({
  selectedInterval,
  intervals,
  onSelectInterval,
  isLoading = false,
}: ChartIntervalSelectorProps) {
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);

  // Map interval options by interval_id
  const optionsMap = new Map<string, ChartIntervalOptionDTO>();
  for (const opt of intervals) {
    optionsMap.set(opt.interval_id.toLowerCase(), opt);
    // Also index case-sensitive 1M
    optionsMap.set(opt.interval_id, opt);
  }

  const normSelected = selectedInterval.trim();
  const activeOption =
    optionsMap.get(normSelected) || optionsMap.get(normSelected.toLowerCase());

  return (
    <div
      role="tablist"
      aria-label="Chart Timeframes"
      className="flex items-center gap-0.5 bg-zinc-950 border border-zinc-800/90 rounded p-0.5 text-xs select-none"
    >
      {CANONICAL_INTERVALS_FALLBACK.map(({ id, label }) => {
        // Resolve option matching id
        const opt = optionsMap.get(id) || optionsMap.get(id.toLowerCase());
        const isSupported = opt ? opt.is_supported : id === "1d";
        const isSelected =
          normSelected.toLowerCase() === id.toLowerCase() ||
          (id === "1M" && (normSelected === "1M" || normSelected.toLowerCase() === "1mo"));

        const isDerived = opt?.availability === "AVAILABLE_DERIVED";
        const isNative = opt?.availability === "AVAILABLE_NATIVE";
        const reason = opt?.unavailability_reason;

        return (
          <div key={id} className="relative">
            <button
              type="button"
              role="tab"
              aria-selected={isSelected}
              aria-disabled={!isSupported}
              disabled={!isSupported || isLoading}
              onClick={() => {
                if (isSupported) {
                  onSelectInterval(id);
                }
              }}
              onMouseEnter={() => {
                if (!isSupported && reason) {
                  setActiveTooltip(id);
                }
              }}
              onMouseLeave={() => {
                if (activeTooltip === id) {
                  setActiveTooltip(null);
                }
              }}
              className={`px-2 py-1 rounded font-mono text-[11px] font-semibold transition-all relative ${
                isSelected
                  ? "bg-zinc-800 text-cyan-300 shadow-sm border border-cyan-500/30"
                  : isSupported
                  ? "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900"
                  : "text-zinc-600 opacity-40 cursor-not-allowed line-through"
              }`}
              title={
                !isSupported && reason
                  ? `Unavailable: ${reason}`
                  : isDerived
                  ? `${label} (Derived from ${opt?.source_interval || "base"} bars)`
                  : isNative
                  ? `${label} (Native Provider feed)`
                  : label
              }
            >
              <span>{label}</span>
              {isDerived && (
                <span
                  aria-hidden="true"
                  className="absolute bottom-0.5 right-0.5 w-1 h-1 rounded-full bg-cyan-400"
                  title="Derived interval"
                />
              )}
            </button>

            {/* Custom accessible tooltip on hover for unavailable intervals */}
            {activeTooltip === id && reason && (
              <div
                role="tooltip"
                className="absolute top-full left-1/2 -translate-x-1/2 mt-1.5 w-52 p-2 bg-zinc-950 border border-zinc-800 rounded shadow-2xl text-[10px] text-zinc-300 z-50 pointer-events-none leading-tight"
              >
                <div className="font-semibold text-rose-400 mb-0.5 flex items-center gap-1">
                  <Info className="w-2.5 h-2.5" />
                  <span>{label} Unavailable</span>
                </div>
                <div className="text-zinc-400">{reason}</div>
              </div>
            )}
          </div>
        );
      })}

      {/* Lineage badge indicator for derived intervals */}
      {activeOption?.availability === "AVAILABLE_DERIVED" && (
        <div
          className="hidden sm:flex items-center gap-1 ml-1.5 px-1.5 py-0.5 bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 rounded text-[10px] font-mono"
          title={`Aggregated from genuine ${activeOption.source_interval || "1d"} observations.`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
          <span>Derived from {activeOption.source_interval || "1d"}</span>
        </div>
      )}
    </div>
  );
}
