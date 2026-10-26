"use client";

import React, { useState, useMemo } from "react";
import {
  HistoricalComparisonResponseDTO,
  HistoricalPeerTrendSeriesDTO,
} from "@/lib/companies/peers";
import { TrendingUp, BarChart2, Calendar, HelpCircle } from "lucide-react";

interface PeerHistoricalChartsProps {
  historical: HistoricalComparisonResponseDTO | null;
  isLoading: boolean;
}

const PEER_COLORS: Record<number, string> = {
  0: "#38bdf8", // Subject - Bright Sky
  1: "#10b981", // Peer 1 - Emerald
  2: "#a855f7", // Peer 2 - Purple
  3: "#f59e0b", // Peer 3 - Amber
  4: "#ec4899", // Peer 4 - Pink
  5: "#6366f1", // Peer 5 - Indigo
  6: "#14b8a6", // Peer 6 - Teal
};

export function PeerHistoricalCharts({ historical, isLoading }: PeerHistoricalChartsProps) {
  const [selectedMetricId, setSelectedMetricId] = useState<string>("profitability.operating_margin");

  const availableMetrics = [
    { id: "scale.revenue", name: "Total Revenue ($B)" },
    { id: "growth.revenue_growth", name: "Revenue Growth YoY (%)" },
    { id: "profitability.operating_margin", name: "Operating Margin (%)" },
    { id: "valuation.pe", name: "P/E Multiple (x)" },
  ];

  const seriesForMetric = useMemo(() => {
    if (!historical) return [];
    return historical.series.filter((s) => s.metric_id === selectedMetricId);
  }, [historical, selectedMetricId]);

  // Extract distinct periods across series (e.g., FY2021, FY2022, FY2023, FY2024)
  const periods = useMemo(() => {
    if (seriesForMetric.length === 0) return [];
    const allPeriods = new Set<string>();
    seriesForMetric.forEach((s) => s.points.forEach((p) => allPeriods.add(p.period_id)));
    return Array.from(allPeriods).sort();
  }, [seriesForMetric]);

  // Calculate min and max values for scaling
  const { minY, maxY } = useMemo(() => {
    let min = Infinity;
    let max = -Infinity;
    seriesForMetric.forEach((s) => {
      s.points.forEach((p) => {
        if (p.value !== null && p.value !== undefined) {
          const num = Number(p.value);
          if (num < min) min = num;
          if (num > max) max = num;
        }
      });
    });

    if (min === Infinity || max === -Infinity) {
      return { minY: 0, maxY: 100 };
    }
    // Add 10% padding
    const padding = (max - min) * 0.1 || 5;
    return {
      minY: min < 0 ? min - padding : Math.max(0, min - padding),
      maxY: max + padding,
    };
  }, [seriesForMetric]);

  if (isLoading || !historical) {
    return (
      <div className="p-8 text-center bg-atlas-surface border border-atlas-border-subtle rounded text-xs text-atlas-text-muted">
        Loading multi-year historical trend comparisons...
      </div>
    );
  }

  // SVG dimensions
  const svgWidth = 800;
  const svgHeight = 280;
  const margin = { top: 20, right: 30, bottom: 40, left: 60 };
  const innerWidth = svgWidth - margin.left - margin.right;
  const innerHeight = svgHeight - margin.top - margin.bottom;

  const getX = (index: number) => {
    if (periods.length <= 1) return innerWidth / 2;
    return (index / (periods.length - 1)) * innerWidth;
  };

  const getY = (val: number) => {
    if (maxY === minY) return innerHeight / 2;
    return innerHeight - ((val - minY) / (maxY - minY)) * innerHeight;
  };

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col p-4">
      {/* Chart Header & Metric Selector */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-atlas-border-subtle mb-4">
        <div>
          <h3 className="text-sm font-semibold text-atlas-text-primary flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-atlas-accent" />
            Historical Cross-Company Performance Trends
          </h3>
          <p className="text-xs text-atlas-text-muted mt-0.5">
            Normalized annual fiscal periods (FY2021 – FY2024). Source restatements preserved without look-ahead bias.
          </p>
        </div>

        {/* Metric Selector Tabs */}
        <div className="flex items-center gap-1 bg-atlas-surface-subtle p-1 rounded border border-atlas-border-subtle">
          {availableMetrics.map((m) => (
            <button
              key={m.id}
              onClick={() => setSelectedMetricId(m.id)}
              className={`px-2.5 py-1 text-xs rounded transition-colors ${
                selectedMetricId === m.id
                  ? "bg-atlas-accent text-white font-medium"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              {m.name}
            </button>
          ))}
        </div>
      </div>

      {/* SVG Multi-Line Chart */}
      <div className="w-full overflow-x-auto mb-4">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto min-w-[650px] font-mono text-[10px]"
        >
          <g transform={`translate(${margin.left}, ${margin.top})`}>
            {/* Grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((pct, idx) => {
              const yVal = minY + (maxY - minY) * (1 - pct);
              const yPos = innerHeight * pct;
              return (
                <g key={idx}>
                  <line
                    x1={0}
                    y1={yPos}
                    x2={innerWidth}
                    y2={yPos}
                    stroke="currentColor"
                    strokeDasharray="3 3"
                    className="text-atlas-border-subtle opacity-60"
                  />
                  <text
                    x={-10}
                    y={yPos + 3}
                    textAnchor="end"
                    fill="currentColor"
                    className="text-atlas-text-muted text-[10px]"
                  >
                    {selectedMetricId === "scale.revenue"
                      ? `$${(yVal / 1e9).toFixed(0)}B`
                      : selectedMetricId.includes("growth") || selectedMetricId.includes("margin")
                      ? `${yVal.toFixed(1)}%`
                      : `${yVal.toFixed(1)}x`}
                  </text>
                </g>
              );
            })}

            {/* X-axis ticks */}
            {periods.map((period, idx) => {
              const xPos = getX(idx);
              return (
                <g key={period}>
                  <line
                    x1={xPos}
                    y1={0}
                    x2={xPos}
                    y2={innerHeight}
                    stroke="currentColor"
                    strokeDasharray="2 2"
                    className="text-atlas-border-subtle/30"
                  />
                  <text
                    x={xPos}
                    y={innerHeight + 20}
                    textAnchor="middle"
                    fill="currentColor"
                    className="text-atlas-text-secondary font-medium"
                  >
                    {period}
                  </text>
                </g>
              );
            })}

            {/* Series Lines & Circles */}
            {seriesForMetric.map((series, sIdx) => {
              const color = series.is_subject ? PEER_COLORS[0] : PEER_COLORS[(sIdx % 6) + 1];
              const pointsWithCoords = series.points
                .map((p) => {
                  const pIdx = periods.indexOf(p.period_id);
                  if (pIdx === -1 || p.value === null || p.value === undefined) return null;
                  return {
                    x: getX(pIdx),
                    y: getY(Number(p.value)),
                    p,
                  };
                })
                .filter(Boolean) as { x: number; y: number; p: any }[];

              if (pointsWithCoords.length === 0) return null;

              const pathData = pointsWithCoords.reduce((acc, pt, idx) => {
                return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
              }, "");

              return (
                <g key={series.company_id}>
                  {/* Line */}
                  <path
                    d={pathData}
                    fill="none"
                    stroke={color}
                    strokeWidth={series.is_subject ? 3 : 1.8}
                    opacity={series.is_subject ? 1 : 0.75}
                  />

                  {/* Points */}
                  {pointsWithCoords.map((pt, ptIdx) => (
                    <circle
                      key={ptIdx}
                      cx={pt.x}
                      cy={pt.y}
                      r={series.is_subject ? 4.5 : 3}
                      fill={color}
                      stroke="#0d1117"
                      strokeWidth={1.5}
                    >
                      <title>{`${series.company_name} (${series.ticker}) - ${pt.p.period_id}: ${pt.p.formatted_value}`}</title>
                    </circle>
                  ))}
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      {/* Series Legend */}
      <div className="flex flex-wrap items-center gap-4 pt-3 border-t border-atlas-border-subtle text-xs">
        {seriesForMetric.map((series, sIdx) => {
          const color = series.is_subject ? PEER_COLORS[0] : PEER_COLORS[(sIdx % 6) + 1];
          return (
            <div key={series.company_id} className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
              <span className={`font-medium ${series.is_subject ? "text-atlas-text-primary font-semibold" : "text-atlas-text-secondary"}`}>
                {series.company_name}
              </span>
              <span className="font-mono text-[10px] text-atlas-text-muted">
                ({series.ticker}){series.is_subject ? " ★" : ""}
              </span>
            </div>
          );
        })}
      </div>

      {/* Historical Observations Table */}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse font-mono">
          <thead>
            <tr className="border-b border-atlas-border-subtle text-[11px] font-semibold text-atlas-text-muted bg-atlas-surface-subtle">
              <th className="py-2 px-3">Company</th>
              {periods.map((p) => (
                <th key={p} className="py-2 px-3 text-right">
                  {p}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle text-[11px]">
            {seriesForMetric.map((series) => {
              return (
                <tr
                  key={series.company_id}
                  className={`hover:bg-atlas-surface-subtle transition-colors ${
                    series.is_subject ? "bg-atlas-accent/5 font-semibold text-atlas-text-primary" : "text-atlas-text-secondary"
                  }`}
                >
                  <td className="py-2 px-3 font-sans">
                    {series.company_name} <span className="font-mono text-[10px] text-atlas-accent">({series.ticker})</span>
                  </td>
                  {periods.map((period) => {
                    const pt = series.points.find((p) => p.period_id === period);
                    return (
                      <td key={period} className="py-2 px-3 text-right">
                        {pt ? pt.formatted_value : "—"}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
