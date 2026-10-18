"use client";

/**
 * Replay Trigger Button for ATLAS Charts Header / Toolbar (Stage 75).
 *
 * Toggles the Replay Start Dialog or highlights active replay state.
 */

import React, { useState } from "react";
import { RotateCcw } from "lucide-react";
import { useChartReplay } from "@/hooks/charts";
import { ReplayStartDialog } from "./ReplayStartDialog";

interface ReplayButtonProps {
  panelId?: string;
  symbol?: string;
  interval?: string;
  className?: string;
}

export function ReplayButton({
  panelId = "panel-1",
  symbol = "SPY",
  interval = "1D",
  className = "",
}: ReplayButtonProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { isReplayActive, activeReplayPanelId, isPlaying } = useChartReplay();

  const isCurrentPanelReplaying =
    isReplayActive && activeReplayPanelId === panelId;

  return (
    <>
      <button
        onClick={() => setIsDialogOpen(true)}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono font-medium transition-all ${
          isCurrentPanelReplaying
            ? "bg-amber-950/60 border border-amber-500/80 text-amber-300 shadow-sm shadow-amber-950/50"
            : "bg-zinc-900 hover:bg-zinc-800 border border-zinc-700/80 text-zinc-300 hover:text-zinc-100"
        } ${className}`}
        title={
          isCurrentPanelReplaying
            ? `Replay Active on ${panelId} (${isPlaying ? "Playing" : "Paused"})`
            : "Open Historical Chart Replay"
        }
        aria-label="Historical Chart Replay"
      >
        <RotateCcw
          className={`w-3.5 h-3.5 ${
            isCurrentPanelReplaying
              ? "text-amber-400" + (isPlaying ? " animate-spin" : "")
              : "text-zinc-400"
          }`}
          style={{ animationDuration: "3s" }}
        />
        <span>REPLAY</span>
        {isCurrentPanelReplaying && (
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
        )}
      </button>

      {isDialogOpen && (
        <ReplayStartDialog
          isOpen={isDialogOpen}
          panelId={panelId}
          symbol={symbol}
          interval={interval}
          onClose={() => setIsDialogOpen(false)}
        />
      )}
    </>
  );
}
