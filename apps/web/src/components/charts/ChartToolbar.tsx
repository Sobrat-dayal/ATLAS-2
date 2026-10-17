"use client";

/**
 * Chart Toolbar Component for ATLAS Charts V1 (Stage 66).
 *
 * Controls:
 * - Canonical instrument selector and symbol disambiguation.
 * - Single verified baseline interval badge ('1D').
 * - Foundational render mode switcher (Candlesticks vs Close Line).
 * - Viewport controls (Reset View, Fit Content, Refresh).
 */

import React, { useState } from "react";
import {
  Calendar,
  CandlestickChart,
  ChevronDown,
  Info,
  LineChart,
  Maximize2,
  RefreshCw,
  RotateCcw,
  Search,
} from "lucide-react";
import {
  ChartInstrumentMetadata,
  ChartRenderMode,
  getAssetClassBadgeLabel,
  getAssetClassColor,
} from "@/lib/charts";

export interface ChartToolbarProps {
  selectedSymbol: string;
  availableInstruments: ChartInstrumentMetadata[];
  interval: string;
  renderMode: ChartRenderMode;
  isLoading: boolean;
  onSelectInstrument: (symbol: string) => void;
  onSelectRenderMode: (mode: ChartRenderMode) => void;
  onRefresh: () => void;
  onResetView?: () => void;
  onFitContent?: () => void;
}

export function ChartToolbar({
  selectedSymbol,
  availableInstruments,
  interval,
  renderMode,
  isLoading,
  onSelectInstrument,
  onSelectRenderMode,
  onRefresh,
  onResetView,
  onFitContent,
}: ChartToolbarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [showIntervalInfo, setShowIntervalInfo] = useState(false);

  const filtered = availableInstruments.filter((inst) => {
    if (!searchFilter.trim()) return true;
    const q = searchFilter.trim().toUpperCase();
    return (
      inst.display_symbol.includes(q) ||
      inst.display_name.toUpperCase().includes(q) ||
      inst.asset_class.toUpperCase().includes(q)
    );
  });

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-2 bg-zinc-900/60 border border-zinc-800/80 rounded text-xs">
      {/* Left controls: Instrument selector & Interval */}
      <div className="flex items-center gap-2">
        {/* Instrument Selector Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-2 px-2.5 py-1.5 bg-zinc-950 border border-zinc-700/80 hover:border-zinc-500 rounded text-zinc-100 font-mono font-medium transition-colors"
          >
            <Search className="w-3.5 h-3.5 text-zinc-400" />
            <span>{selectedSymbol}</span>
            <ChevronDown className="w-3.5 h-3.5 text-zinc-400" />
          </button>

          {isOpen && (
            <div className="absolute top-full left-0 mt-1 w-72 max-h-80 bg-zinc-950 border border-zinc-800 rounded shadow-2xl z-50 overflow-hidden flex flex-col">
              <div className="p-2 border-b border-zinc-800">
                <input
                  type="text"
                  placeholder="Search symbols or names..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  className="w-full px-2 py-1 bg-zinc-900 border border-zinc-800 rounded text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-cyan-500"
                  autoFocus
                />
              </div>

              <div className="overflow-y-auto flex-1 divide-y divide-zinc-900">
                {filtered.map((inst) => (
                  <button
                    key={inst.entity_id}
                    type="button"
                    onClick={() => {
                      onSelectInstrument(inst.display_symbol);
                      setIsOpen(false);
                      setSearchFilter("");
                    }}
                    className={`w-full px-3 py-2 text-left hover:bg-zinc-900/80 flex items-center justify-between transition-colors ${
                      inst.display_symbol === selectedSymbol ? "bg-zinc-900" : ""
                    }`}
                  >
                    <div>
                      <div className="font-mono font-semibold text-zinc-100">
                        {inst.display_symbol}
                      </div>
                      <div className="text-[11px] text-zinc-400 truncate max-w-[170px]">
                        {inst.display_name}
                      </div>
                    </div>
                    <span
                      className={`px-1.5 py-0.5 text-[9px] font-mono rounded border ${getAssetClassColor(
                        inst.asset_class
                      )}`}
                    >
                      {getAssetClassBadgeLabel(inst.asset_class)}
                    </span>
                  </button>
                ))}

                {filtered.length === 0 && (
                  <div className="p-4 text-center text-zinc-500 text-xs">
                    No matching instruments found.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Baseline Interval Badge */}
        <div className="relative flex items-center">
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-zinc-950 border border-zinc-800 rounded text-zinc-200 font-mono font-semibold">
            <Calendar className="w-3.5 h-3.5 text-cyan-400" />
            <span>{interval.toUpperCase()}</span>
            <button
              type="button"
              onClick={() => setShowIntervalInfo(!showIntervalInfo)}
              className="text-zinc-500 hover:text-zinc-300 ml-0.5"
              title="Baseline Interval Policy"
            >
              <Info className="w-3 h-3" />
            </button>
          </div>

          {showIntervalInfo && (
            <div className="absolute top-full left-0 mt-1 w-64 p-2.5 bg-zinc-950 border border-zinc-800 rounded shadow-xl text-[11px] text-zinc-300 z-50 leading-relaxed">
              <div className="font-semibold text-zinc-100 mb-1">
                Baseline Interval: 1D
              </div>
              Stage 66 enforces the single verified baseline interval (&apos;1d&apos; daily bars).
              Expanded intraday timeframes (1m, 5m, 1h) and multi-resolution intervals belong to Stage 68.
            </div>
          )}
        </div>

        {/* Render Mode Toggle: Candlestick vs Line */}
        <div className="flex items-center bg-zinc-950 border border-zinc-800 rounded p-0.5">
          <button
            type="button"
            onClick={() => onSelectRenderMode("candlestick")}
            className={`flex items-center gap-1 px-2 py-1 rounded transition-colors ${
              renderMode === "candlestick"
                ? "bg-zinc-800 text-zinc-100 font-medium"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
            title="Candlestick Chart Mode"
          >
            <CandlestickChart className="w-3.5 h-3.5 text-emerald-400" />
            <span>Candles</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectRenderMode("line")}
            className={`flex items-center gap-1 px-2 py-1 rounded transition-colors ${
              renderMode === "line"
                ? "bg-zinc-800 text-zinc-100 font-medium"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
            title="Close Line Chart Mode"
          >
            <LineChart className="w-3.5 h-3.5 text-sky-400" />
            <span>Line</span>
          </button>
        </div>
      </div>

      {/* Right controls: Viewport & Refresh */}
      <div className="flex items-center gap-2">
        {onResetView && (
          <button
            type="button"
            onClick={onResetView}
            className="flex items-center gap-1 px-2 py-1 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-zinc-100 rounded transition-colors"
            title="Reset Time Scale"
          >
            <RotateCcw className="w-3 h-3 text-zinc-400" />
            <span>Reset</span>
          </button>
        )}

        {onFitContent && (
          <button
            type="button"
            onClick={onFitContent}
            className="flex items-center gap-1 px-2 py-1 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-zinc-100 rounded transition-colors"
            title="Fit All Loaded Bars to Viewport"
          >
            <Maximize2 className="w-3 h-3 text-zinc-400" />
            <span>Fit</span>
          </button>
        )}

        <button
          type="button"
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center gap-1 px-2.5 py-1 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-zinc-100 rounded transition-colors disabled:opacity-50"
          title="Refresh Historical Stored Bars"
        >
          <RefreshCw className={`w-3 h-3 text-cyan-400 ${isLoading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>
    </div>
  );
}
