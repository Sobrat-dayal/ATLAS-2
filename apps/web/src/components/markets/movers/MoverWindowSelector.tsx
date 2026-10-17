"use client";

import React from "react";
import { Calendar, Clock } from "lucide-react";
import { ComparisonWindow } from "@/lib/markets/movers";

export interface MoverWindowSelectorProps {
  supportedWindows: ComparisonWindow[];
  selectedWindow?: ComparisonWindow;
  defaultWindow: ComparisonWindow;
  onSelectWindow: (window: ComparisonWindow) => void;
  disabled?: boolean;
}

function formatWindowLabel(window: ComparisonWindow): string {
  switch (window) {
    case "previous_regular_session":
      return "Prev Regular Session";
    case "rolling_24h":
      return "Rolling 24h";
    case "previous_session_settlement":
      return "Prior Settlement";
    case "current_session":
      return "Current Session";
    default:
      return window;
  }
}

export function MoverWindowSelector({
  supportedWindows,
  selectedWindow,
  defaultWindow,
  onSelectWindow,
  disabled,
}: MoverWindowSelectorProps) {
  if (!supportedWindows || supportedWindows.length <= 1) {
    // If only 1 window is supported, display static informative badge
    const win = supportedWindows?.[0] || defaultWindow;
    return (
      <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)]">
        <Clock className="h-3.5 w-3.5 text-zinc-400" />
        <span>Window:</span>
        <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)]">
          {formatWindowLabel(win)}
        </span>
      </div>
    );
  }

  const current = selectedWindow || defaultWindow;

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)] font-medium">
        <Calendar className="h-3.5 w-3.5 text-zinc-400" />
        <span>Window:</span>
      </div>

      <div
        role="group"
        aria-label="Select comparison window"
        className="flex items-center gap-1 p-0.5 bg-[var(--atlas-surface-card)] rounded border border-[var(--atlas-border-subtle)]"
      >
        {supportedWindows.map((win) => {
          const isSelected = win === current;
          return (
            <button
              key={win}
              type="button"
              disabled={disabled}
              onClick={() => onSelectWindow(win)}
              className={`px-2.5 py-1 text-xs font-medium rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50 ${
                isSelected
                  ? "bg-zinc-800 text-[var(--atlas-text-primary)] font-semibold shadow-sm border border-zinc-700"
                  : "text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] border border-transparent"
              } disabled:opacity-40 disabled:cursor-not-allowed`}
            >
              {formatWindowLabel(win)}
            </button>
          );
        })}
      </div>
    </div>
  );
}
