"use client";

import React from "react";
import { AnalyticalObservationRow, AnalyticalSummaryStatistics } from "@/lib/research/types";
import { Badge } from "@/design-system";

interface EconomicResearchChartProps {
  observations: AnalyticalObservationRow[];
  summaryStatistics?: AnalyticalSummaryStatistics;
  indicatorLabel: string;
}

export function EconomicResearchChart({
  observations,
  summaryStatistics,
  indicatorLabel,
}: EconomicResearchChartProps) {
  const validObservations = observations.filter((o) => !o.is_missing && o.raw_value != null);

  if (validObservations.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center rounded-sm border border-atlas-border-subtle bg-atlas-surface-0 text-xs text-atlas-text-muted">
        No macroeconomic observations available in this series.
      </div>
    );
  }

  const values = validObservations.map((o) => o.raw_value as number);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal === 0 ? 1 : maxVal - minVal;

  return (
    <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-subtle pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              {indicatorLabel} Macro Time Series
            </h3>
            <Badge variant="outline" className="font-mono text-[10px]">
              CANONICAL MACRO
            </Badge>
          </div>
          <p className="text-xs text-atlas-text-muted">
            Official central bank and government statistical publication series.
          </p>
        </div>

        {summaryStatistics?.mean != null && (
          <div className="flex items-center gap-2 rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 px-3 py-1 text-xs">
            <span className="text-atlas-text-muted">Series Mean:</span>
            <span className="font-mono font-medium text-atlas-text-primary">
              {summaryStatistics.mean.toFixed(2)}
            </span>
          </div>
        )}
      </div>

      {/* SVG Trend Line / Points */}
      <div className="flex h-44 items-end gap-2 pt-4">
        {observations.map((obs, idx) => {
          if (obs.is_missing || obs.raw_value == null) return null;
          const heightPct = Math.max(10, Math.min(100, ((obs.raw_value - minVal) / range) * 80 + 15));

          return (
            <div
              key={obs.period_label || idx}
              className="flex flex-1 flex-col items-center justify-end h-full group relative"
            >
              {/* Tooltip */}
              <div className="pointer-events-none absolute -top-12 z-20 hidden rounded-xs border border-atlas-border-default bg-atlas-surface-2 px-2 py-1 text-xs shadow-md group-hover:block whitespace-nowrap">
                <div className="font-semibold text-atlas-text-primary">
                  {obs.period_label}: {obs.display_value} {obs.unit}
                </div>
                {obs.publication_cutoff && (
                  <div className="text-[10px] text-atlas-text-muted">
                    Vintage Cutoff: {obs.publication_cutoff}
                  </div>
                )}
              </div>

              <div className="mb-1 text-[10px] font-mono font-medium text-atlas-text-secondary truncate max-w-full">
                {obs.display_value}
              </div>

              <div
                style={{ height: `${heightPct}%` }}
                className="w-full rounded-t-xs bg-indigo-600/80 hover:bg-indigo-600 transition-all duration-300"
              />

              <div className="mt-2 text-center text-[11px] font-mono font-medium text-atlas-text-primary truncate max-w-full">
                {obs.period_label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
