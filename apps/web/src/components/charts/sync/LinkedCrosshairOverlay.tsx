"use client";

/**
 * Linked Crosshair Ghost Overlay Component for ATLAS Charts (Stage 73).
 *
 * Implements:
 * - Precision vertical time guide at canonical UTC timestamp
 * - Synchronized timestamp label badge at the bottom of the time scale
 * - Clear visual distinction from local active pointer (cyan/emerald dashed guide)
 * - Strict financial data integrity: NO fabricated OHLC tooltip
 * - Accessible numerical timestamp readout
 * - Automatic removal on crosshair leave or source pointer exit
 */

import React from "react";

export interface LinkedCrosshairOverlayProps {
  xPx: number | null;
  timestamp: string | null;
  sourceSymbol?: string;
  sourceInterval?: string;
  color?: string;
}

export function LinkedCrosshairOverlay({
  xPx,
  timestamp,
  sourceSymbol,
  sourceInterval,
  color = "#06b6d4", // Cyan 500 default
}: LinkedCrosshairOverlayProps) {
  if (xPx === null || !timestamp) return null;

  return (
    <div
      className="absolute inset-0 pointer-events-none z-20 overflow-hidden"
      aria-hidden="true"
    >
      {/* Vertical Time Guide Line */}
      <div
        className="absolute top-0 bottom-6 border-l border-dashed transition-all duration-75"
        style={{
          left: `${xPx}px`,
          borderColor: color,
          opacity: 0.85,
        }}
      />

      {/* Synchronized Timestamp Tag Badge at bottom time axis */}
      <div
        className="absolute bottom-1 -translate-x-1/2 px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold shadow-md border flex items-center gap-1 backdrop-blur-sm transition-all duration-75"
        style={{
          left: `${xPx}px`,
          backgroundColor: "#09090b",
          borderColor: color,
          color: "#f4f4f5",
        }}
      >
        <span
          className="w-1.5 h-1.5 rounded-full"
          style={{ backgroundColor: color }}
        />
        <span>{timestamp}</span>
        {sourceSymbol && (
          <span className="text-zinc-400 text-[9px]">
            [{sourceSymbol}{sourceInterval ? ` ${sourceInterval}` : ""}]
          </span>
        )}
      </div>
    </div>
  );
}
