"use client";

/**
 * Replay Playback Toolbar for ATLAS Charts (Stage 75).
 *
 * Provides institutional playback controls:
 * - Play / Pause toggle
 * - Step Forward (+1 bar) / Step Backward (-1 bar)
 * - Restart replay session to start index
 * - Monotonic bars/sec speed selection (0.5x, 1x, 2x, 5x, 10x)
 * - Revealed progress indicator and cursor bar timestamp/price
 * - Safe Exit Replay button with state restoration
 * - Keyboard shortcuts: Space (Play/Pause), ArrowRight (Step Forward), ArrowLeft (Step Backward), Home (Restart)
 */

import React, { useEffect, useCallback } from "react";
import {
  Play,
  Pause,
  SkipBack,
  ChevronLeft,
  ChevronRight,
  X,
  Gauge,
  Calendar,
  AlertCircle,
} from "lucide-react";
import { useChartReplay } from "@/hooks/charts";
import { ReplaySpeed } from "@/lib/charts/replay";

interface ReplayToolbarProps {
  className?: string;
  onExit?: () => void;
}

const SPEED_OPTIONS: ReplaySpeed[] = [0.5, 1, 2, 5, 10];

export function ReplayToolbar({ className = "", onExit }: ReplayToolbarProps) {
  const {
    isReplayActive,
    isPlaying,
    status,
    playbackSpeed,
    session,
    cursorBar,
    play,
    pause,
    stepForward,
    stepBackward,
    restart,
    setSpeed,
    exitReplay,
  } = useChartReplay();

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isReplayActive) return;
      // Don't hijack keystrokes inside text inputs or textareas
      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      ) {
        return;
      }

      if (e.code === "Space") {
        e.preventDefault();
        if (isPlaying) {
          pause();
        } else {
          play();
        }
      } else if (e.code === "ArrowRight") {
        e.preventDefault();
        stepForward();
      } else if (e.code === "ArrowLeft") {
        e.preventDefault();
        stepBackward();
      } else if (e.code === "Home") {
        e.preventDefault();
        restart();
      }
    },
    [isReplayActive, isPlaying, play, pause, stepForward, stepBackward, restart]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  if (!isReplayActive || !session) return null;

  const handleExit = async () => {
    await exitReplay();
    onExit?.();
  };

  const cursorDateStr = cursorBar
    ? cursorBar.timestamp
      ? cursorBar.timestamp.replace("T", " ").substring(0, 19)
      : cursorBar.time_unix
      ? new Date(cursorBar.time_unix * 1000).toISOString().replace("T", " ").substring(0, 19)
      : "—"
    : "—";

  const cursorPriceStr =
    cursorBar?.close != null ? Number(cursorBar.close).toFixed(2) : "—";

  const progressFraction = `${
    session.cursor_index != null ? session.cursor_index + 1 : 0
  } / ${session.total_bars}`;

  return (
    <div
      className={`flex flex-wrap items-center justify-between gap-2 px-3 py-2 bg-zinc-950/95 border-b border-amber-900/40 backdrop-blur-md font-mono text-xs text-zinc-200 select-none ${className}`}
      role="region"
      aria-label="Historical Chart Replay Controls"
    >
      {/* Left: Mode Badge & Cursor Info */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-950/40 border border-amber-800/80 text-amber-300 font-semibold text-[11px]">
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isPlaying
                ? "bg-emerald-400 animate-pulse"
                : status === "END_OF_DATA"
                ? "bg-zinc-400"
                : "bg-amber-400"
            }`}
          />
          <span>REPLAY</span>
          <span className="text-zinc-500">|</span>
          <span className="text-zinc-300">{session.display_symbol}</span>
          <span className="text-zinc-500">({session.interval})</span>
        </div>

        {/* Cursor Info */}
        <div className="hidden sm:flex items-center gap-3 text-zinc-400 text-[11px]">
          <div className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-zinc-200">{cursorDateStr}</span>
          </div>
          <div>
            Close: <span className="text-cyan-300 font-semibold">{cursorPriceStr}</span>
          </div>
          <div className="text-zinc-500">
            Bar: <span className="text-zinc-300">{progressFraction}</span>
          </div>
        </div>
      </div>

      {/* Center: Playback Buttons */}
      <div className="flex items-center gap-1">
        {/* Restart */}
        <button
          onClick={() => restart()}
          title="Restart replay to start index (Home)"
          aria-label="Restart replay"
          className="p-1.5 rounded hover:bg-zinc-800 text-zinc-300 hover:text-white transition-colors"
        >
          <SkipBack className="w-4 h-4" />
        </button>

        {/* Step Backward */}
        <button
          onClick={() => stepBackward()}
          disabled={session.cursor_index <= 0}
          title="Step backward one bar (Left Arrow)"
          aria-label="Step backward one bar"
          className="p-1.5 rounded hover:bg-zinc-800 text-zinc-300 hover:text-white disabled:opacity-40 disabled:hover:bg-transparent transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        {/* Play / Pause */}
        <button
          onClick={() => (isPlaying ? pause() : play())}
          title={isPlaying ? "Pause playback (Space)" : "Start playback (Space)"}
          aria-label={isPlaying ? "Pause playback" : "Start playback"}
          className={`flex items-center gap-1 px-3 py-1.5 rounded font-semibold transition-colors ${
            isPlaying
              ? "bg-amber-600/80 hover:bg-amber-500 text-zinc-950"
              : "bg-cyan-600/80 hover:bg-cyan-500 text-zinc-950"
          }`}
        >
          {isPlaying ? (
            <>
              <Pause className="w-3.5 h-3.5 fill-current" />
              <span>PAUSE</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>PLAY</span>
            </>
          )}
        </button>

        {/* Step Forward */}
        <button
          onClick={() => stepForward()}
          disabled={status === "END_OF_DATA" || session.cursor_index >= session.total_bars - 1}
          title="Step forward one bar (Right Arrow)"
          aria-label="Step forward one bar"
          className="p-1.5 rounded hover:bg-zinc-800 text-zinc-300 hover:text-white disabled:opacity-40 disabled:hover:bg-transparent transition-colors"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Right: Speed & Exit Controls */}
      <div className="flex items-center gap-2">
        {/* Speed Selector */}
        <div className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 rounded px-1.5 py-0.5">
          <Gauge className="w-3.5 h-3.5 text-zinc-500" />
          {SPEED_OPTIONS.map((speed) => (
            <button
              key={speed}
              onClick={() => setSpeed(speed)}
              className={`px-1.5 py-0.5 rounded text-[10px] font-mono transition-colors ${
                playbackSpeed === speed
                  ? "bg-cyan-900/60 text-cyan-300 font-bold"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
              title={`${speed} bars per second`}
            >
              {speed}x
            </button>
          ))}
        </div>

        {/* End of Data Notice */}
        {status === "END_OF_DATA" && (
          <span className="hidden md:inline-flex items-center gap-1 text-[11px] text-amber-400">
            <AlertCircle className="w-3 h-3" />
            End of data
          </span>
        )}

        {/* Exit Replay */}
        <button
          onClick={handleExit}
          title="Exit historical chart replay"
          aria-label="Exit Replay"
          className="flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-900 hover:bg-red-950/60 border border-zinc-700/80 hover:border-red-700/80 text-zinc-300 hover:text-red-300 text-xs transition-colors"
        >
          <X className="w-3.5 h-3.5" />
          <span>EXIT</span>
        </button>
      </div>
    </div>
  );
}
