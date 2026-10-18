"use client";

/**
 * Replay Start Dialog for ATLAS Charts (Stage 75).
 *
 * Allows users to configure and initialize an authenticated historical chart replay session:
 * - Displays instrument, interval, and verified historical bar coverage
 * - Allows picking starting date or bar offset
 * - Configures initial pre-cursor history window
 * - Discloses methodological notice regarding revised historical datasets
 */

import React, { useState, useEffect } from "react";
import {
  RotateCcw,
  X,
  AlertTriangle,
  Play,
  Calendar,
  Layers,
  Gauge,
  Clock,
  CheckCircle2,
} from "lucide-react";
import { useChartReplay } from "@/hooks/charts";
import { getReplayCapabilities, ReplayCapabilityResponse, ReplaySpeed } from "@/lib/charts/replay";

interface ReplayStartDialogProps {
  isOpen: boolean;
  panelId: string;
  symbol: string;
  interval: string;
  onClose: () => void;
}

export function ReplayStartDialog({
  isOpen,
  panelId,
  symbol,
  interval,
  onClose,
}: ReplayStartDialogProps) {
  const { startReplay } = useChartReplay();

  const [capabilities, setCapabilities] = useState<ReplayCapabilityResponse | null>(null);
  const [loadingCapabilities, setLoadingCapabilities] = useState(false);
  const [startMode, setStartMode] = useState<"offset" | "date">("offset");
  const [offsetBars, setOffsetBars] = useState<number>(50);
  const [startDateStr, setStartDateStr] = useState<string>("");
  const [historyWindow, setHistoryWindow] = useState<number>(100);
  const [initialSpeed, setInitialSpeed] = useState<ReplaySpeed>(1);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setError(null);
    setLoadingCapabilities(true);

    getReplayCapabilities(symbol, interval)
      .then((res: ReplayCapabilityResponse) => {
        setCapabilities(res);
        if (res.latest_available_bar) {
          // Default date to ~30 days prior if available
          try {
            const dateObj = new Date(res.latest_available_bar);
            dateObj.setDate(dateObj.getDate() - 30);
            setStartDateStr(dateObj.toISOString().split("T")[0]);
          } catch {
            setStartDateStr("");
          }
        }
      })
      .catch((err: any) => {
        setError(err.message || "Failed to load historical coverage.");
      })
      .finally(() => {
        setLoadingCapabilities(false);
      });
  }, [isOpen, symbol, interval]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsStarting(true);
    setError(null);

    try {
      let startIndex: number | null = null;
      let startTime: string | null = null;

      if (startMode === "offset") {
        if (capabilities && capabilities.total_bars_available > 0) {
          startIndex = Math.max(0, capabilities.total_bars_available - offsetBars);
        } else {
          startIndex = 50;
        }
      } else {
        if (!startDateStr) {
          setError("Please specify a valid starting date.");
          setIsStarting(false);
          return;
        }
        startTime = new Date(startDateStr).toISOString();
      }

      await startReplay({
        panel_id: panelId,
        symbol,
        interval,
        start_index: startIndex,
        start_time: startTime,
        history_window: historyWindow,
        playback_speed: initialSpeed,
      });

      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to start replay session.");
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-150"
      role="dialog"
      aria-modal="true"
      aria-labelledby="replay-start-dialog-title"
    >
      <div className="w-full max-w-lg bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden font-sans text-zinc-100">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/60">
          <div className="flex items-center gap-2">
            <RotateCcw className="w-4 h-4 text-amber-400" />
            <h2
              id="replay-start-dialog-title"
              className="text-sm font-semibold tracking-tight font-mono text-zinc-100"
            >
              INITIALIZE HISTORICAL CHART REPLAY
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="p-2.5 rounded bg-red-950/40 border border-red-800/60 text-xs text-red-300 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Instrument & Coverage Summary */}
          <div className="p-3 rounded bg-zinc-900/70 border border-zinc-800 space-y-2 text-xs font-mono">
            <div className="flex items-center justify-between text-zinc-400">
              <span>Target Series:</span>
              <span className="text-cyan-300 font-semibold">
                {symbol} ({interval})
              </span>
            </div>
            <div className="flex items-center justify-between text-zinc-400">
              <span>Target Panel:</span>
              <span className="text-zinc-200">{panelId}</span>
            </div>
            <div className="flex items-center justify-between text-zinc-400 border-t border-zinc-800/80 pt-1.5">
              <span>Historical Coverage:</span>
              {loadingCapabilities ? (
                <span className="text-zinc-500 animate-pulse">Checking coverage...</span>
              ) : capabilities ? (
                <span className="text-emerald-400 font-semibold">
                  {capabilities.total_bars_available} bars available
                </span>
              ) : (
                <span className="text-zinc-500">—</span>
              )}
            </div>
            {capabilities?.earliest_available_bar && (
              <div className="flex items-center justify-between text-[11px] text-zinc-500">
                <span>Earliest / Latest:</span>
                <span>
                  {capabilities.earliest_available_bar.substring(0, 10)} →{" "}
                  {capabilities.latest_available_bar?.substring(0, 10)}
                </span>
              </div>
            )}
          </div>

          {/* Starting Point Options */}
          <div className="space-y-2">
            <label className="block text-xs font-mono text-zinc-400 font-medium">
              Replay Starting Point
            </label>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <button
                type="button"
                onClick={() => setStartMode("offset")}
                className={`flex items-center justify-center gap-1.5 p-2 rounded border transition-colors ${
                  startMode === "offset"
                    ? "bg-amber-950/40 border-amber-600/80 text-amber-300 font-semibold"
                    : "bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200"
                }`}
              >
                <Clock className="w-3.5 h-3.5" />
                <span>Recent Offset</span>
              </button>
              <button
                type="button"
                onClick={() => setStartMode("date")}
                className={`flex items-center justify-center gap-1.5 p-2 rounded border transition-colors ${
                  startMode === "date"
                    ? "bg-amber-950/40 border-amber-600/80 text-amber-300 font-semibold"
                    : "bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200"
                }`}
              >
                <Calendar className="w-3.5 h-3.5" />
                <span>Calendar Date</span>
              </button>
            </div>

            {startMode === "offset" ? (
              <div className="space-y-1 pt-1">
                <div className="flex items-center justify-between text-[11px] text-zinc-400 font-mono">
                  <span>Start replay at:</span>
                  <span className="text-amber-300 font-semibold">{offsetBars} bars ago</span>
                </div>
                <input
                  type="range"
                  min={10}
                  max={Math.min(500, capabilities?.total_bars_available || 300)}
                  value={offsetBars}
                  onChange={(e) => setOffsetBars(Number(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer"
                />
              </div>
            ) : (
              <div className="space-y-1 pt-1">
                <input
                  type="date"
                  value={startDateStr}
                  onChange={(e) => setStartDateStr(e.target.value)}
                  className="w-full px-3 py-1.5 bg-zinc-900 border border-zinc-700/80 rounded text-xs text-zinc-100 font-mono focus:outline-none focus:border-amber-500"
                />
              </div>
            )}
          </div>

          {/* Initial History Window & Playback Speed */}
          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div className="space-y-1.5">
              <label className="block text-zinc-400 font-medium">History Window</label>
              <select
                value={historyWindow}
                onChange={(e) => setHistoryWindow(Number(e.target.value))}
                className="w-full px-2.5 py-1.5 bg-zinc-900 border border-zinc-700/80 rounded text-zinc-200 focus:outline-none focus:border-cyan-500"
              >
                <option value={50}>50 bars</option>
                <option value={100}>100 bars</option>
                <option value={200}>200 bars</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="block text-zinc-400 font-medium">Playback Speed</label>
              <select
                value={initialSpeed}
                onChange={(e) => setInitialSpeed(Number(e.target.value) as ReplaySpeed)}
                className="w-full px-2.5 py-1.5 bg-zinc-900 border border-zinc-700/80 rounded text-zinc-200 focus:outline-none focus:border-cyan-500"
              >
                <option value={0.5}>0.5 bars / sec</option>
                <option value={1}>1.0 bar / sec</option>
                <option value={2}>2.0 bars / sec</option>
                <option value={5}>5.0 bars / sec</option>
                <option value={10}>10.0 bars / sec</option>
              </select>
            </div>
          </div>

          {/* Methodological Notice */}
          <div className="p-2.5 rounded bg-amber-950/30 border border-amber-900/60 text-[11px] text-amber-300/90 font-mono space-y-1">
            <div className="flex items-center gap-1.5 font-semibold text-amber-200">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              <span>Methodological Transparency</span>
            </div>
            <p className="leading-relaxed">
              Historical playback uses the currently available revised/split-adjusted dataset and does
              not guarantee point-in-time information availability. No future observations leak
              beyond the replay cursor.
            </p>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              disabled={isStarting}
              className="px-3 py-1.5 rounded text-xs font-mono text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            >
              CANCEL
            </button>
            <button
              type="submit"
              disabled={isStarting || loadingCapabilities}
              className="flex items-center gap-1.5 px-4 py-1.5 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-zinc-950 text-xs font-mono font-semibold rounded shadow transition-colors"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{isStarting ? "STARTING..." : "START REPLAY"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
