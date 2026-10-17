"use client";

import React from "react";
import { HeatmapComparisonWindow } from "@/lib/markets/heatmaps";

interface HeatmapPeriodSelectorProps {
  supportedWindows?: HeatmapComparisonWindow[];
  selectedWindow?: HeatmapComparisonWindow;
  onSelectWindow: (win?: HeatmapComparisonWindow) => void;
  disabled?: boolean;
}

const WINDOW_LABELS: Record<HeatmapComparisonWindow, string> = {
  previous_regular_session: "Prev Regular Session Close",
  rolling_24h: "Rolling 24 Hours",
  previous_session_settlement: "Prev Session Settlement",
};

export function HeatmapPeriodSelector({
  supportedWindows = ["previous_regular_session"],
  selectedWindow,
  onSelectWindow,
  disabled = false,
}: HeatmapPeriodSelectorProps) {
  return (
    <div className="flex flex-col gap-1">
      <label
        htmlFor="heatmap-period-select"
        className="text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)]"
      >
        Comparison Window
      </label>
      <select
        id="heatmap-period-select"
        value={selectedWindow || supportedWindows[0]}
        onChange={(e) => onSelectWindow(e.target.value as HeatmapComparisonWindow)}
        disabled={disabled}
        className="h-8 px-2.5 text-xs font-medium rounded bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] hover:border-[var(--atlas-border-default)] focus:outline-none focus:ring-1 focus:ring-[var(--atlas-accent-primary)] cursor-pointer disabled:opacity-50"
      >
        {supportedWindows.map((w) => (
          <option key={w} value={w}>
            {WINDOW_LABELS[w] || w}
          </option>
        ))}
      </select>
    </div>
  );
}
