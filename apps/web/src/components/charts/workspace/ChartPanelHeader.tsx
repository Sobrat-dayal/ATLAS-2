"use client";

/**
 * Compact Chart Panel Header for Multi-Chart Workspaces (Stage 72).
 *
 * Implements:
 * - Active panel identification badge and focus toggle
 * - Independent canonical instrument selection
 * - Independent interval selector
 * - Independent chart type selector
 * - Real-time live quote mini-pill with green/red price change
 * - Quick action controls (Go to latest, Reset view, Refresh)
 */

import React, { useState } from "react";
import {
  Activity,
  ArrowUpRight,
  ChevronDown,
  Link2,
  Maximize2,
  RefreshCw,
  RotateCcw,
  Search,
  Unlink,
} from "lucide-react";
import { useChartSync } from "@/hooks/charts";
import {
  ChartInstrumentMetadata,
  ChartIntervalOptionDTO,
  ChartRenderMode,
  LiveQuoteDTO,
  formatPrice,
  getAssetClassBadgeLabel,
  getAssetClassColor,
} from "@/lib/charts";
import { ChartIntervalSelector } from "../ChartIntervalSelector";
import { ChartTypeSelector } from "../ChartTypeSelector";
import { ReplayStatusBadge } from "../replay";
import { ReplaySessionStatus } from "@/lib/charts/replay";

export interface ChartPanelHeaderProps {
  panelId: string;
  panelIndex: number;
  isActive: boolean;
  instrument: ChartInstrumentMetadata | null;
  symbol: string;
  interval: string;
  intervals: ChartIntervalOptionDTO[];
  renderMode: ChartRenderMode;
  liveQuote?: LiveQuoteDTO | null;
  availableInstruments: ChartInstrumentMetadata[];
  isLoading: boolean;
  isReplaying?: boolean;
  replayStatus?: ReplaySessionStatus;
  playbackSpeed?: number;
  onActivate: () => void;
  onSelectInstrument: (symbol: string) => void;
  onSelectInterval: (interval: string) => void;
  onSelectRenderMode: (mode: ChartRenderMode) => void;
  onRefresh: () => void;
  onGoToLatest?: () => void;
  onResetView?: () => void;
  onOpenIndicators?: () => void;
  activeIndicatorCount?: number;
}

export function ChartPanelHeader({
  panelId,
  panelIndex,
  isActive,
  instrument,
  symbol,
  interval,
  intervals,
  renderMode,
  liveQuote,
  availableInstruments,
  isLoading,
  isReplaying = false,
  replayStatus,
  playbackSpeed = 1,
  onActivate,
  onSelectInstrument,
  onSelectInterval,
  onSelectRenderMode,
  onRefresh,
  onGoToLatest,
  onResetView,
  onOpenIndicators,
  activeIndicatorCount = 0,
}: ChartPanelHeaderProps) {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");

  const filtered = availableInstruments.filter((inst) => {
    if (!searchFilter.trim()) return true;
    const q = searchFilter.trim().toUpperCase();
    return (
      inst.display_symbol.includes(q) ||
      inst.display_name.toUpperCase().includes(q) ||
      inst.asset_class.toUpperCase().includes(q)
    );
  });

  const lastPrice = liveQuote?.last_price ?? null;
  const isGenuineLast = liveQuote?.has_genuine_last ?? false;

  const { getPanelGroup } = useChartSync();
  const group = getPanelGroup(panelId);

  return (
    <div
      onClick={onActivate}
      className={`flex items-center justify-between gap-1.5 px-2.5 py-1.5 border-b text-xs transition-colors select-none ${
        isActive
          ? "bg-zinc-900 border-cyan-500/80 text-zinc-100"
          : "bg-zinc-950/90 border-zinc-800/80 text-zinc-400 hover:text-zinc-200"
      }`}
    >
      {/* Left section: Active badge + Instrument + Interval + Mode */}
      <div className="flex items-center gap-1.5 flex-wrap min-w-0">
        {/* Active Panel Badge */}
        <button
          type="button"
          onClick={onActivate}
          className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase transition-colors ${
            isActive
              ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
              : "bg-zinc-800/60 text-zinc-500 border border-zinc-700/50 hover:text-zinc-300"
          }`}
          title={isActive ? `Panel ${panelIndex + 1} (Active)` : `Click to activate Panel ${panelIndex + 1}`}
        >
          P{panelIndex + 1}
        </button>

        {/* Sync Group Badge */}
        {group && group.enabled ? (
          <div
            className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-semibold border shadow-xs"
            style={{
              borderColor: `${group.color}60`,
              backgroundColor: `${group.color}15`,
              color: group.color,
            }}
            title={`Synchronized in ${group.name} (${group.memberPanelIds.length} panels)`}
          >
            <Link2 className="w-2.5 h-2.5" />
            <span>LINK {group.name.replace("Group ", "")}</span>
          </div>
        ) : (
          <div
            className="flex items-center gap-0.5 px-1 py-0.5 rounded text-[9px] font-mono text-zinc-500 border border-zinc-800 bg-zinc-900/50"
            title="Independent Chart Panel"
          >
            <Unlink className="w-2.5 h-2.5 text-zinc-600" />
            <span>IND</span>
          </div>
        )}

        {/* Instrument Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setIsSearchOpen(!isSearchOpen);
            }}
            className="flex items-center gap-1 px-1.5 py-0.5 bg-zinc-950 border border-zinc-700/70 hover:border-zinc-500 rounded font-mono font-semibold text-zinc-100 text-xs transition-colors"
          >
            <Search className="w-3 h-3 text-zinc-400" />
            <span className="truncate max-w-[90px]">{symbol}</span>
            <ChevronDown className="w-3 h-3 text-zinc-400" />
          </button>

          {isSearchOpen && (
            <div
              onClick={(e) => e.stopPropagation()}
              className="absolute top-full left-0 mt-1 w-64 max-h-72 bg-zinc-950 border border-zinc-800 rounded shadow-2xl z-50 overflow-hidden flex flex-col"
            >
              <div className="p-1.5 border-b border-zinc-800">
                <input
                  type="text"
                  placeholder="Search symbol..."
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
                      setIsSearchOpen(false);
                      setSearchFilter("");
                    }}
                    className={`w-full px-2.5 py-1.5 text-left hover:bg-zinc-900 flex items-center justify-between text-xs transition-colors ${
                      inst.display_symbol === symbol ? "bg-zinc-900" : ""
                    }`}
                  >
                    <div>
                      <div className="font-mono font-semibold text-zinc-100">
                        {inst.display_symbol}
                      </div>
                      <div className="text-[10px] text-zinc-400 truncate max-w-[140px]">
                        {inst.display_name}
                      </div>
                    </div>
                    <span
                      className={`px-1 py-0.2 text-[8px] font-mono rounded border ${getAssetClassColor(
                        inst.asset_class
                      )}`}
                    >
                      {getAssetClassBadgeLabel(inst.asset_class)}
                    </span>
                  </button>
                ))}

                {filtered.length === 0 && (
                  <div className="p-3 text-center text-zinc-500 text-[11px]">
                    No instruments found.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Asset Class Badge */}
        {instrument && (
          <span
            className={`hidden sm:inline-block px-1.5 py-0.2 text-[9px] font-mono rounded border ${getAssetClassColor(
              instrument.asset_class
            )}`}
          >
            {getAssetClassBadgeLabel(instrument.asset_class)}
          </span>
        )}

        {/* Interval Selector */}
        <ChartIntervalSelector
          selectedInterval={interval}
          intervals={intervals}
          onSelectInterval={onSelectInterval}
          isLoading={isLoading}
        />

        {/* Chart Type Selector */}
        <ChartTypeSelector selectedMode={renderMode} onSelectMode={onSelectRenderMode} />

        {/* Indicators Trigger */}
        {onOpenIndicators && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onOpenIndicators();
            }}
            className={`flex items-center gap-1 px-1.5 py-0.5 rounded font-mono text-[11px] border transition-colors ${
              activeIndicatorCount > 0
                ? "bg-cyan-950/60 border-cyan-700/80 text-cyan-300"
                : "bg-zinc-950 border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200"
            }`}
            title="Open Technical Indicators for this panel"
          >
            <Activity className="w-3 h-3 text-cyan-400" />
            <span className="hidden md:inline">Ind</span>
            {activeIndicatorCount > 0 && (
              <span className="px-1 text-[9px] font-bold bg-cyan-500/20 text-cyan-300 rounded-full">
                {activeIndicatorCount}
              </span>
            )}
          </button>
        )}
      </div>

      {/* Right section: Live price badge / Replay badge & panel actions */}
      <div className="flex items-center gap-1.5 shrink-0">
        {/* Real-time Last Price Mini-pill OR Replay Status Badge */}
        {isReplaying ? (
          <ReplayStatusBadge
            status={replayStatus || "PAUSED"}
            playbackSpeed={playbackSpeed}
          />
        ) : lastPrice !== null ? (
          <div className="hidden sm:flex items-center gap-1.5 px-2 py-0.5 rounded bg-zinc-950 border border-zinc-800 text-[11px] font-mono">
            <span className="text-zinc-100 font-semibold">{formatPrice(lastPrice)}</span>
            {isGenuineLast && (
              <span className="px-1 text-[9px] font-bold bg-emerald-500/20 text-emerald-300 rounded">
                LIVE
              </span>
            )}
          </div>
        ) : null}

        {onGoToLatest && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onGoToLatest();
            }}
            className="p-1 hover:bg-zinc-800 rounded text-zinc-400 hover:text-zinc-100 transition-colors"
            title="Go to Latest Bar"
          >
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        )}

        {onResetView && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onResetView();
            }}
            className="p-1 hover:bg-zinc-800 rounded text-zinc-400 hover:text-zinc-100 transition-colors"
            title="Reset Time Scale"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        )}

        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRefresh();
          }}
          disabled={isLoading}
          className="p-1 hover:bg-zinc-800 rounded text-zinc-400 hover:text-zinc-100 transition-colors disabled:opacity-50"
          title="Refresh Historical Bars"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${isLoading ? "animate-spin" : ""}`} />
        </button>
      </div>
    </div>
  );
}
