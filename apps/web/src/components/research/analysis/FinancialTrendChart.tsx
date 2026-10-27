"use client";

import React from "react";
import { AnalyticalObservationRow, AnalyticalSummaryStatistics } from "@/lib/research/types";
import { formatCAGR, formatPercentageDelta } from "@/lib/research/formatting";
import { Badge } from "@/design-system";

interface FinancialTrendChartProps {
  observations: AnalyticalObservationRow[];
  summaryStatistics?: AnalyticalSummaryStatistics;
  currency?: string | null;
  unit?: string;
  metricLabel: string;
}

export function FinancialTrendChart({
  observations,
  summaryStatistics,
  currency = "USD",
  unit = "$M",
  metricLabel,
}: FinancialTrendChartProps) {
  const validObservations = observations.filter((o) => !o.is_missing && o.raw_value != null);

  if (validObservations.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center rounded-sm border border-atlas-border-subtle bg-atlas-surface-0 text-xs text-atlas-text-muted">
        No numeric observations recorded for this analytical trend.
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
              {metricLabel} Historical Trend
            </h3>
            <Badge variant="outline" className="font-mono text-[10px]">
              {unit || currency || "UNITS"}
            </Badge>
          </div>
          <p className="text-xs text-atlas-text-muted">
            Chronological financial statement observations grounded in official regulatory filings.
          </p>
        </div>

        {summaryStatistics?.cagr_percentage != null && (
          <div className="flex items-center gap-2 rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 px-2.5 py-1 text-xs">
            <span className="text-atlas-text-muted">CAGR:</span>
            <span className="font-mono font-medium text-atlas-accent">
              {formatCAGR(summaryStatistics.cagr_percentage)}
            </span>
          </div>
        )}
      </div>

      {/* Bar Chart Visualization */}
      <div className="flex h-44 items-end gap-3 pt-4">
        {observations.map((obs, idx) => {
          if (obs.is_missing || obs.raw_value == null) {
            return (
              <div
                key={obs.period_label || idx}
                className="flex flex-1 flex-col items-center justify-end h-full group relative"
              >
                <div className="w-full rounded-t-xs border border-dashed border-atlas-border-default bg-atlas-surface-1 flex items-center justify-center text-[10px] text-atlas-text-muted h-10">
                  N/A
                </div>
                <div className="mt-2 text-center text-[11px] font-mono text-atlas-text-muted">
                  {obs.period_label}
                </div>
              </div>
            );
          }

          const heightPct = Math.max(12, Math.min(100, ((obs.raw_value - minVal) / range) * 80 + 15));
          const isPositive = obs.raw_value >= 0;

          return (
            <div
              key={obs.period_label || idx}
              className="flex flex-1 flex-col items-center justify-end h-full group relative"
            >
              {/* Tooltip on hover */}
              <div className="pointer-events-none absolute -top-12 z-20 hidden rounded-xs border border-atlas-border-default bg-atlas-surface-2 px-2 py-1 text-xs shadow-md group-hover:block whitespace-nowrap">
                <div className="font-semibold text-atlas-text-primary">
                  {obs.period_label}: {obs.display_value} {obs.unit}
                </div>
                {obs.period_delta != null && (
                  <div className="text-[10px] text-atlas-text-muted">
                    Δ: {obs.period_delta > 0 ? "+" : ""}{obs.period_delta.toLocaleString()} | %Δ: {formatPercentageDelta(obs.percentage_growth)}
                  </div>
                )}
                {obs.is_restated && (
                  <div className="text-[9px] text-amber-500 font-medium">Restated in subsequent filing</div>
                )}
              </div>

              {/* Bar Value Header */}
              <div className="mb-1 text-[10px] font-mono font-medium text-atlas-text-secondary truncate max-w-full">
                {obs.display_value}
              </div>

              {/* Bar Fill */}
              <div
                style={{ height: `${heightPct}%` }}
                className={`w-full rounded-t-xs transition-all duration-300 ${
                  isPositive ? "bg-atlas-accent/80 hover:bg-atlas-accent" : "bg-rose-500/80 hover:bg-rose-500"
                } ${obs.is_restated ? "ring-1 ring-amber-400" : ""}`}
              />

              {/* Period Label */}
              <div className="mt-2 text-center text-[11px] font-mono font-medium text-atlas-text-primary">
                {obs.period_label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
