"use client";

/**
 * Replay Status Badge for ATLAS Charts (Stage 75).
 *
 * Displays an institutional indicator when a chart panel is operating in
 * historical replay mode, showing playback status (PLAYING, PAUSED, END_OF_DATA).
 */

import React from "react";
import { ReplaySessionStatus } from "@/lib/charts/replay";

interface ReplayStatusBadgeProps {
  status: ReplaySessionStatus;
  playbackSpeed?: number;
  className?: string;
}

export function ReplayStatusBadge({
  status,
  playbackSpeed = 1,
  className = "",
}: ReplayStatusBadgeProps) {
  let statusText = "REPLAY: PAUSED";
  let dotColor = "bg-amber-400";
  let badgeClasses = "bg-amber-950/40 border-amber-800/80 text-amber-300";

  if (status === "PLAYING") {
    statusText = `REPLAY: PLAYING (${playbackSpeed}x)`;
    dotColor = "bg-emerald-400 animate-pulse";
    badgeClasses = "bg-emerald-950/40 border-emerald-800/80 text-emerald-300";
  } else if (status === "END_OF_DATA") {
    statusText = "REPLAY: END OF DATA";
    dotColor = "bg-zinc-400";
    badgeClasses = "bg-zinc-900 border-zinc-700 text-zinc-300";
  } else if (status === "INITIALIZING") {
    statusText = "REPLAY: LOADING";
    dotColor = "bg-cyan-400 animate-ping";
    badgeClasses = "bg-cyan-950/40 border-cyan-800/80 text-cyan-300";
  } else if (status === "ERROR") {
    statusText = "REPLAY: ERROR";
    dotColor = "bg-red-400";
    badgeClasses = "bg-red-950/40 border-red-800/80 text-red-300";
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-semibold border ${badgeClasses} ${className}`}
      role="status"
      aria-label={statusText}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      <span>{statusText}</span>
    </div>
  );
}
