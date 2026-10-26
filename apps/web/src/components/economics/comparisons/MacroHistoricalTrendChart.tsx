"use client";

import React from "react";
import {
  ComparableIndicatorDTO,
  HistoricalTrendsResponseDTO,
} from "@/lib/economics/comparisons";
import { Info, LineChart, TrendingUp } from "lucide-react";

interface MacroHistoricalTrendChartProps {
  trendsData: HistoricalTrendsResponseDTO | null;
  indicators: ComparableIndicatorDTO[];
  basePeriod: string | null;
  onToggleBasePeriod: (period: string | null) => void;
  isLoading: boolean;
}

const COUNTRY_COLORS = [
  "#38bdf8", // Sky blue
  "#818cf8", // Indigo
  "#34d399", // Emerald
  "#fbbf24", // Amber
  "#f472b6", // Rose
  "#a78bfa", // Purple
  "#2dd4bf", // Teal
  "#fb923c", // Orange
];

export function MacroHistoricalTrendChart({
  trendsData,
  indicators,
  basePeriod,
  onToggleBasePeriod,
  isLoading,
}: MacroHistoricalTrendChartProps) {
  if (isLoading && !trendsData) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2">
        <div className="w-6 h-6 border-2 border-atlas-accent border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-mono">Aligning Multi-Country Historical Observations...</span>
      </div>
    );
  }

  if (!trendsData || trendsData.points.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2 border border-dashed border-atlas-border-subtle rounded m-4">
        <Info className="w-8 h-8 text-atlas-text-muted/60" />
        <p className="text-sm font-medium text-atlas-text-primary">No Time-Series Data Available</p>
        <p className="text-xs text-atlas-text-muted">
          Select countries that possess overlapping historical reporting periods.
        </p>
      </div>
    );
  }

  const indicatorDef = indicators.find((i) => i.metric_kind === trendsData.metric_kind);

  // Group points by country
  const countrySeriesMap = new Map<string, { countryName: string; points: Array<{ period: string; value: number }> }>();

  trendsData.points.forEach((pt) => {
    if (!countrySeriesMap.has(pt.geography_id)) {
      countrySeriesMap.set(pt.geography_id, {
        countryName: pt.country_name,
        points: [],
      });
    }
    const val = basePeriod && pt.indexed_value !== null && pt.indexed_value !== undefined ? pt.indexed_value : pt.raw_value;
    countrySeriesMap.get(pt.geography_id)!.points.push({
      period: pt.reference_period,
      value: val,
    });
  });

  const seriesEntries = Array.from(countrySeriesMap.entries());

  // Find overall min and max for scaling
  let minVal = Infinity;
  let maxVal = -Infinity;
  seriesEntries.forEach(([, s]) => {
    s.points.forEach((p) => {
      if (p.value < minVal) minVal = p.value;
      if (p.value > maxVal) maxVal = p.value;
    });
  });

  if (minVal === Infinity) minVal = 0;
  if (maxVal === -Infinity) maxVal = 100;
  const padding = (maxVal - minVal) * 0.1 || 10;
  const chartMin = minVal - padding;
  const chartMax = maxVal + padding;
  const chartRange = chartMax - chartMin || 1;

  return (
    <div className="flex flex-col flex-1 h-full min-h-0 bg-atlas-background overflow-y-auto p-4 gap-4">
      {/* Chart Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded bg-atlas-surface/60 border border-atlas-border-subtle text-xs">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded bg-purple-500/15 text-purple-400">
            <LineChart className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-bold text-atlas-text-primary text-sm tracking-tight">
              Historical Multi-Country Trend: {indicatorDef?.name || trendsData.metric_kind}
            </h2>
            <div className="flex items-center gap-2 text-atlas-text-muted text-[11px] font-mono">
              <span>{basePeriod ? `Indexed to Base Period ${basePeriod} = 100` : `Unit: ${indicatorDef?.default_unit || "—"}`}</span>
              <span>•</span>
              <span>Periods: {trendsData.common_periods.join(", ")}</span>
            </div>
          </div>
        </div>

        {/* Base Period Index Rebase Toggle */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onToggleBasePeriod(basePeriod ? null : trendsData.common_periods[0] || "2021")}
            className={`px-2.5 py-1 rounded text-xs font-medium border transition-colors flex items-center gap-1.5 ${
              basePeriod
                ? "bg-purple-500/20 border-purple-500/40 text-purple-300"
                : "bg-atlas-surface border-atlas-border-subtle text-atlas-text-muted hover:text-atlas-text-primary"
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5" />
            <span>{basePeriod ? `Rebased (Base: ${basePeriod})` : "Rebase to Index 100"}</span>
          </button>
        </div>
      </div>

      {/* SVG Aligned Chart */}
      <div className="p-4 rounded bg-atlas-surface/30 border border-atlas-border-subtle flex flex-col gap-3">
        <div className="h-64 w-full relative">
          <svg className="w-full h-full overflow-visible" viewBox="0 0 600 200" preserveAspectRatio="none">
            {/* Horizontal Grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((pct, idx) => {
              const y = 200 - pct * 180 - 10;
              const val = chartMin + pct * chartRange;
              return (
                <g key={idx}>
                  <line x1="40" y1={y} x2="590" y2={y} stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
                  <text x="35" y={y + 3} fill="rgba(255,255,255,0.4)" fontSize="9" textAnchor="end" fontFamily="monospace">
                    {val.toFixed(basePeriod ? 0 : 1)}
                  </text>
                </g>
              );
            })}

            {/* Country Polylines */}
            {seriesEntries.map(([geoId, series], sIdx) => {
              const color = COUNTRY_COLORS[sIdx % COUNTRY_COLORS.length];
              const pts = series.points
                .map((p, pIdx) => {
                  const x = 50 + (pIdx / Math.max(1, trendsData.common_periods.length - 1)) * 530;
                  const y = 200 - ((p.value - chartMin) / chartRange) * 180 - 10;
                  return `${x},${y}`;
                })
                .join(" ");

              return (
                <g key={geoId}>
                  <polyline fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={pts} />
                  {/* Point Dots */}
                  {series.points.map((p, pIdx) => {
                    const x = 50 + (pIdx / Math.max(1, trendsData.common_periods.length - 1)) * 530;
                    const y = 200 - ((p.value - chartMin) / chartRange) * 180 - 10;
                    return (
                      <circle key={pIdx} cx={x} cy={y} r="3.5" fill="#0d1117" stroke={color} strokeWidth="2" />
                    );
                  })}
                </g>
              );
            })}

            {/* Period X-axis Labels */}
            {trendsData.common_periods.map((period, pIdx) => {
              const x = 50 + (pIdx / Math.max(1, trendsData.common_periods.length - 1)) * 530;
              return (
                <text key={period} x={x} y="198" fill="rgba(255,255,255,0.5)" fontSize="10" textAnchor="middle" fontFamily="monospace">
                  {period}
                </text>
              );
            })}
          </svg>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2 border-t border-atlas-border-subtle/50 text-xs font-mono">
          {seriesEntries.map(([geoId, series], sIdx) => {
            const color = COUNTRY_COLORS[sIdx % COUNTRY_COLORS.length];
            return (
              <div key={geoId} className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-atlas-text-primary font-medium">{series.countryName}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Numerical Time-Series Data Table */}
      <div className="border border-atlas-border-subtle rounded bg-atlas-surface/20 overflow-auto">
        <table className="w-full border-collapse text-left text-xs font-mono">
          <thead className="bg-atlas-surface border-b border-atlas-border-subtle">
            <tr>
              <th className="p-2.5 font-bold text-atlas-text-primary">Country</th>
              {trendsData.common_periods.map((p) => (
                <th key={p} className="p-2.5 font-semibold text-atlas-text-secondary text-right">
                  {p}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle/40">
            {seriesEntries.map(([geoId, series]) => (
              <tr key={geoId} className="hover:bg-atlas-surface/40">
                <td className="p-2.5 font-semibold text-atlas-text-primary">{series.countryName}</td>
                {series.points.map((pt) => (
                  <td key={pt.period} className="p-2.5 text-right font-medium text-atlas-text-primary">
                    {pt.value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
