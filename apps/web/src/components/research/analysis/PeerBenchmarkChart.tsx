"use client";

import React from "react";
import { AnalyticalObservationRow, AnalyticalSummaryStatistics } from "@/lib/research/types";
import { Badge } from "@/design-system";

interface PeerBenchmarkChartProps {
  observations: AnalyticalObservationRow[];
  summaryStatistics?: AnalyticalSummaryStatistics;
  comparabilityWarnings?: string[];
  metricLabel: string;
}

export function PeerBenchmarkChart({
  observations,
  summaryStatistics,
  comparabilityWarnings = [],
  metricLabel,
}: PeerBenchmarkChartProps) {
  const validObservations = observations.filter((o) => !o.is_missing && o.raw_value != null);

  if (validObservations.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center rounded-sm border border-atlas-border-subtle bg-atlas-surface-0 text-xs text-atlas-text-muted">
        No peer observations available for cross-sectional benchmarking.
      </div>
    );
  }

  const values = validObservations.map((o) => o.raw_value as number);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal === 0 ? 1 : maxVal - minVal;
  const median = summaryStatistics?.median;

  return (
    <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-subtle pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              {metricLabel} Peer Benchmarking
            </h3>
            <Badge variant="outline" className="font-mono text-[10px]">
              CROSS-SECTIONAL
            </Badge>
          </div>
          <p className="text-xs text-atlas-text-muted">
            Comparative analysis across verified industry peer companies.
          </p>
        </div>

        {median != null && (
          <div className="flex items-center gap-3 rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 px-3 py-1 text-xs">
            <span className="text-atlas-text-muted">Peer Median:</span>
            <span className="font-mono font-semibold text-atlas-text-primary">
              {median.toFixed(2)}%
            </span>
            {summaryStatistics?.sample_size_n && (
              <span className="text-[10px] text-atlas-text-muted font-mono">
                (N={summaryStatistics.sample_size_n})
              </span>
            )}
          </div>
        )}
      </div>

      {/* Cross-Sectional Bar Chart */}
      <div className="flex h-48 items-end gap-3 pt-6">
        {observations.map((obs, idx) => {
          if (obs.is_missing || obs.raw_value == null) return null;
          const heightPct = Math.max(12, Math.min(100, ((obs.raw_value - minVal) / range) * 80 + 15));
          const isAboveMedian = median != null ? obs.raw_value >= median : true;

          return (
            <div
              key={obs.metric_id || idx}
              className="flex flex-1 flex-col items-center justify-end h-full group relative"
            >
              {/* Tooltip */}
              <div className="pointer-events-none absolute -top-12 z-20 hidden rounded-xs border border-atlas-border-default bg-atlas-surface-2 px-2 py-1 text-xs shadow-md group-hover:block whitespace-nowrap">
                <div className="font-semibold text-atlas-text-primary">
                  {obs.metric_name}: {obs.display_value} {obs.unit}
                </div>
                {median != null && (
                  <div className="text-[10px] text-atlas-text-muted">
                    Vs Median: {obs.raw_value >= median ? "+" : ""}{(obs.raw_value - median).toFixed(2)}%
                  </div>
                )}
              </div>

              <div className="mb-1 text-[10px] font-mono font-medium text-atlas-text-secondary truncate max-w-full">
                {obs.display_value}
              </div>

              <div
                style={{ height: `${heightPct}%` }}
                className={`w-full rounded-t-xs transition-all duration-300 ${
                  isAboveMedian ? "bg-emerald-600/80 hover:bg-emerald-600" : "bg-sky-600/80 hover:bg-sky-600"
                }`}
              />

              <div className="mt-2 text-center text-[11px] font-mono font-medium text-atlas-text-primary truncate max-w-full">
                {obs.period_label || obs.metric_name}
              </div>
            </div>
          );
        })}
      </div>

      {/* Comparability Warnings */}
      {comparabilityWarnings.length > 0 && (
        <div className="mt-4 rounded-xs border border-amber-500/20 bg-amber-500/5 p-2 text-xs text-amber-600">
          <div className="font-semibold text-[11px] uppercase tracking-wider mb-1">
            Comparability Disclosures:
          </div>
          <ul className="list-disc list-inside space-y-0.5 text-[11px]">
            {comparabilityWarnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
