"use client";

import React, { useState, useEffect, useRef } from "react";
import { ReplayEvent } from "@/lib/trading/backtesting/types";
import { formatCurrency } from "@/lib/trading/backtesting/formatters";
import {
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Clock,
  Layers,
  Activity,
  CheckCircle,
  AlertTriangle,
} from "lucide-react";

interface BacktestReplayProps {
  replayEvents?: ReplayEvent[];
}

export function BacktestReplay({ replayEvents = [] }: BacktestReplayProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const totalEvents = replayEvents.length;

  useEffect(() => {
    if (isPlaying) {
      const interval = Math.max(50, 400 / playbackSpeed);
      timerRef.current = setInterval(() => {
        setCurrentIndex((prev) => {
          if (prev >= totalEvents - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, interval);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, playbackSpeed, totalEvents]);

  const currentEvent = replayEvents[currentIndex];

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentIndex(0);
  };

  const handleStep = () => {
    if (currentIndex < totalEvents - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  if (totalEvents === 0) {
    return (
      <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-8 text-center text-neutral-400">
        <Clock className="w-8 h-8 mx-auto text-neutral-600 mb-2" />
        <p className="text-sm">No historical event replay stream attached to this run.</p>
        <p className="text-xs text-neutral-500 mt-1">
          Enable &apos;include_replay_events&apos; in configuration to capture trade-by-trade ticks.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 text-neutral-200 space-y-4">
      {/* Replay Controls Header */}
      <div className="flex flex-wrap items-center justify-between pb-4 border-b border-neutral-800 gap-3">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-neutral-100 flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-400" />
            Historical Event-Driven Replay Engine
          </h3>
          <p className="text-xs text-neutral-400 mt-0.5">
            Step-by-step playback of market arrival ticks and simulated execution state
          </p>
        </div>

        {/* Media Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            className="p-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-300"
            title="Reset"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-neutral-950 font-semibold text-xs flex items-center gap-1.5"
          >
            {isPlaying ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" /> Pause
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" /> Play
              </>
            )}
          </button>
          <button
            onClick={handleStep}
            disabled={isPlaying || currentIndex >= totalEvents - 1}
            className="p-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-300 disabled:opacity-40"
            title="Step Forward"
          >
            <SkipForward className="w-4 h-4" />
          </button>

          {/* Speed Selector */}
          <div className="flex items-center bg-neutral-950 border border-neutral-800 rounded-lg p-0.5 text-xs font-mono ml-2">
            {[1, 2, 5, 10].map((spd) => (
              <button
                key={spd}
                onClick={() => setPlaybackSpeed(spd)}
                className={`px-2 py-0.5 rounded ${
                  playbackSpeed === spd
                    ? "bg-neutral-800 text-amber-400 font-bold"
                    : "text-neutral-400 hover:text-neutral-200"
                }`}
              >
                {spd}x
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Progress Scrubber */}
      <div>
        <div className="flex items-center justify-between text-xs text-neutral-400 mb-1.5 font-mono">
          <span>
            Tick: {currentIndex + 1} / {totalEvents}
          </span>
          <span>Simulation Time: {currentEvent?.timestamp || "—"}</span>
        </div>
        <input
          type="range"
          min="0"
          max={totalEvents - 1}
          value={currentIndex}
          onChange={(e) => {
            setIsPlaying(false);
            setCurrentIndex(Number(e.target.value));
          }}
          className="w-full accent-amber-400 bg-neutral-800 h-1.5 rounded-lg cursor-pointer"
        />
      </div>

      {/* Current Replay Event Banner */}
      {currentEvent && (
        <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <span className="text-neutral-500 block">Event Type</span>
            <span className="font-semibold text-neutral-200 font-mono mt-0.5 block">
              {currentEvent.event_type}
            </span>
          </div>
          <div>
            <span className="text-neutral-500 block">Instrument & Price</span>
            <span className="font-semibold text-neutral-200 font-mono mt-0.5 block">
              {currentEvent.instrument_id} @ ${currentEvent.price.toFixed(2)}
            </span>
          </div>
          <div>
            <span className="text-neutral-500 block">Portfolio Equity</span>
            <span className="font-semibold text-emerald-400 font-mono mt-0.5 block">
              {formatCurrency(currentEvent.portfolio_equity)}
            </span>
          </div>
          <div>
            <span className="text-neutral-500 block">Unrealized P&L</span>
            <span
              className={`font-semibold font-mono mt-0.5 block ${
                currentEvent.unrealized_pnl >= 0 ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {formatCurrency(currentEvent.unrealized_pnl)}
            </span>
          </div>
          <div className="col-span-2 sm:col-span-4 pt-2 border-t border-neutral-900 text-neutral-300">
            <strong>Detail:</strong> {currentEvent.description}
          </div>
        </div>
      )}

      {/* Recent Event History Feed */}
      <div className="bg-neutral-950/60 rounded-xl border border-neutral-800 p-3 max-h-56 overflow-y-auto font-mono text-[11px] space-y-1.5">
        {replayEvents.slice(0, currentIndex + 1).map((ev, i) => (
          <div
            key={i}
            className={`flex items-center justify-between p-1.5 rounded transition-colors ${
              i === currentIndex ? "bg-amber-950/40 border border-amber-800/40 text-amber-200" : "text-neutral-400"
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="text-neutral-500">{ev.timestamp.split(" ")[1]}</span>
              <span className="font-semibold text-neutral-300">[{ev.event_type}]</span>
              <span>{ev.description}</span>
            </div>
            <span className="text-neutral-300">{formatCurrency(ev.portfolio_equity)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

