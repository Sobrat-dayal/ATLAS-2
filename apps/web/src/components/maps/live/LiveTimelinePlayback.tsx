"use client";

import React from "react";
import {
  Play,
  Pause,
  RotateCcw,
  FastForward,
  Clock,
  Radio,
} from "lucide-react";
import { LivePlaybackState } from "@/lib/maps/live/types";

interface LiveTimelinePlaybackProps {
  playbackState: LivePlaybackState;
  onModeChange: (mode: "LIVE" | "PAUSED" | "HISTORICAL") => void;
  onTimeChange: (timeIso: string) => void;
  onSpeedChange: (speed: number) => void;
}

const SPEED_OPTIONS = [1, 5, 15, 60];

export function LiveTimelinePlayback({
  playbackState,
  onModeChange,
  onTimeChange,
  onSpeedChange,
}: LiveTimelinePlaybackProps) {
  const isLive = playbackState.mode === "LIVE";
  const isPaused = playbackState.mode === "PAUSED";
  const isHistorical = playbackState.mode === "HISTORICAL";

  return (
    <div className="bg-zinc-950/95 border border-zinc-800 rounded-lg shadow-2xl backdrop-blur-md px-4 py-2.5 flex items-center gap-4 font-mono text-xs text-zinc-300">
      {/* Live Indicator / Toggle */}
      <div className="flex items-center gap-2 pr-3 border-r border-zinc-800">
        <button
          onClick={() => onModeChange("LIVE")}
          className={`flex items-center gap-2 px-2.5 py-1 rounded transition-all font-semibold ${
            isLive
              ? "bg-emerald-500/20 border border-emerald-500/40 text-emerald-400"
              : "bg-zinc-900 text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isLive ? "bg-emerald-400 animate-pulse" : "bg-zinc-600"
            }`}
          />
          <Radio className="w-3.5 h-3.5" />
          <span>LIVE</span>
        </button>

        <button
          onClick={() => onModeChange(isPaused ? "LIVE" : "PAUSED")}
          className={`p-1.5 rounded transition-all ${
            isPaused
              ? "bg-amber-500/20 border border-amber-500/40 text-amber-400"
              : "bg-zinc-900 text-zinc-400 hover:text-zinc-200"
          }`}
          title={isPaused ? "Resume Live" : "Pause Live Stream"}
        >
          {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Scrubbing & Clock Display */}
      <div className="flex items-center gap-3 flex-1 min-w-[320px]">
        <div className="flex items-center gap-1.5 text-zinc-400 text-[11px] shrink-0">
          <Clock className="w-3.5 h-3.5 text-zinc-500" />
          <span>As Of (UTC):</span>
          <span className="text-zinc-100 font-semibold">
            {playbackState.playbackTimeUtc
              ? new Date(playbackState.playbackTimeUtc).toUTCString().replace("GMT", "UTC")
              : "Live Streaming"}
          </span>
        </div>

        {/* Temporal Slider */}
        <input
          type="range"
          min="-86400"
          max="0"
          step="60"
          defaultValue="0"
          onChange={(e) => {
            const offsetSec = parseInt(e.target.value, 10);
            if (offsetSec === 0) {
              onModeChange("LIVE");
            } else {
              const targetDate = new Date(Date.now() + offsetSec * 1000);
              onModeChange("HISTORICAL");
              onTimeChange(targetDate.toISOString());
            }
          }}
          className="w-full accent-emerald-500 h-1.5 bg-zinc-800 rounded-lg cursor-pointer"
        />
      </div>

      {/* Speed Multiplier & Reset */}
      <div className="flex items-center gap-2 pl-3 border-l border-zinc-800 shrink-0">
        <span className="text-[10px] text-zinc-500">Speed:</span>
        <div className="flex items-center gap-1 bg-zinc-900 p-0.5 rounded border border-zinc-800">
          {SPEED_OPTIONS.map((spd) => (
            <button
              key={spd}
              onClick={() => onSpeedChange(spd)}
              className={`px-1.5 py-0.5 rounded text-[10px] transition-colors ${
                playbackState.speedMultiplier === spd
                  ? "bg-emerald-500/20 text-emerald-400 font-bold"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {spd}x
            </button>
          ))}
        </div>

        {isHistorical && (
          <button
            onClick={() => onModeChange("LIVE")}
            className="flex items-center gap-1 px-2 py-1 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 rounded transition-colors text-[11px]"
            title="Jump back to Live"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset</span>
          </button>
        )}
      </div>
    </div>
  );
}
