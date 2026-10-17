"use client";

/**
 * Live Chart Streaming Controls for ATLAS Charts (Stage 67).
 *
 * Implements:
 * - Functional Pause / Resume Live Updates toggle
 * - "Go to Latest" viewport recenter button without data mutation
 * - Clear Follow-Live status indicator
 * - High accessibility with keyboard controls and descriptive aria labels
 */

import React from "react";
import { ArrowRightToLine, Pause, Play, Radio } from "lucide-react";
import { ChartLiveCapability } from "@/lib/charts";

export interface LiveChartControlsProps {
  isPaused: boolean;
  isFollowingLatest: boolean;
  liveCapability: ChartLiveCapability;
  onTogglePause: () => void;
  onGoToLatest: () => void;
}

export function LiveChartControls({
  isPaused,
  isFollowingLatest,
  liveCapability,
  onTogglePause,
  onGoToLatest,
}: LiveChartControlsProps) {
  const isHistoricalOnly = liveCapability === "HISTORICAL_ONLY";

  return (
    <div
      role="toolbar"
      aria-label="Live Chart Controls"
      className="flex items-center gap-2"
    >
      {/* Pause / Resume Button */}
      <button
        type="button"
        disabled={isHistoricalOnly}
        onClick={onTogglePause}
        aria-label={
          isPaused ? "Resume real-time market data updates" : "Pause live market data updates"
        }
        aria-pressed={isPaused}
        className={`px-2.5 py-1 text-xs font-mono font-medium rounded border transition-colors flex items-center gap-1.5 focus:outline-none focus:ring-1 focus:ring-cyan-500 ${
          isHistoricalOnly
            ? "bg-zinc-900 border-zinc-800 text-zinc-600 cursor-not-allowed"
            : isPaused
            ? "bg-amber-500/10 border-amber-500/40 text-amber-300 hover:bg-amber-500/20"
            : "bg-zinc-900 border-zinc-700/80 text-zinc-200 hover:bg-zinc-800 hover:text-white"
        }`}
        title={
          isHistoricalOnly
            ? "Live streaming unavailable for this OTC feed"
            : isPaused
            ? "Resume live market data streaming (Space)"
            : "Pause live market data streaming"
        }
      >
        {isPaused ? (
          <>
            <Play className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
            <span>RESUME LIVE</span>
          </>
        ) : (
          <>
            <Pause className="w-3.5 h-3.5 text-zinc-400" />
            <span>PAUSE LIVE</span>
          </>
        )}
      </button>

      {/* Go to Latest Button */}
      <button
        type="button"
        onClick={onGoToLatest}
        aria-label="Recenter viewport to latest historical and live observations"
        className={`px-2.5 py-1 text-xs font-mono font-medium rounded border transition-colors flex items-center gap-1.5 focus:outline-none focus:ring-1 focus:ring-cyan-500 ${
          isFollowingLatest
            ? "bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200"
            : "bg-cyan-950/40 border-cyan-700/60 text-cyan-300 hover:bg-cyan-900/40 shadow-sm"
        }`}
        title="Recenter chart viewport to the latest market observation"
      >
        <ArrowRightToLine className="w-3.5 h-3.5 text-cyan-400" />
        <span>GO TO LATEST</span>
      </button>

      {/* Follow-Live Indicator Pill */}
      <div
        className={`hidden lg:flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono border ${
          isFollowingLatest && !isPaused
            ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
            : "bg-zinc-900 border-zinc-800 text-zinc-500"
        }`}
        title={
          isFollowingLatest
            ? "Chart viewport is locked to real-time incoming observations"
            : "User has manually panned historical history. Click 'Go to Latest' to return."
        }
      >
        <Radio
          className={`w-2.5 h-2.5 ${
            isFollowingLatest && !isPaused ? "text-emerald-400 animate-pulse" : "text-zinc-600"
          }`}
        />
        <span>{isFollowingLatest ? "FOLLOWING LIVE" : "HISTORICAL VIEW"}</span>
      </div>
    </div>
  );
}
