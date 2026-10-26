"use client";

import React, { useMemo, useState } from "react";
import { PeerComparisonResponseDTO } from "@/lib/companies/peers";
import { ScatterChart, HelpCircle } from "lucide-react";

interface PeerScatterPlotProps {
  comparison: PeerComparisonResponseDTO | null;
  isLoading: boolean;
}

export function PeerScatterPlot({ comparison, isLoading }: PeerScatterPlotProps) {
  const [hoveredCompany, setHoveredCompany] = useState<any | null>(null);

  const plotData = useMemo(() => {
    if (!comparison) return [];
    const growthObs = comparison.observations["growth.revenue_growth"] || {};
    const marginObs = comparison.observations["profitability.operating_margin"] || {};
    const mcapObs = comparison.observations["scale.market_cap"] || {};

    return comparison.companies
      .map((c) => {
        const g = growthObs[c.company_id];
        const m = marginObs[c.company_id];
        const cap = mcapObs[c.company_id];

        if (
          g?.exact_value === undefined ||
          g?.exact_value === null ||
          m?.exact_value === undefined ||
          m?.exact_value === null
        ) {
          return null;
        }

        return {
          company_id: c.company_id,
          display_name: c.display_name,
          ticker: c.ticker,
          is_subject: c.is_subject,
          growth: Number(g.exact_value),
          growthFormatted: g.formatted_value,
          margin: Number(m.exact_value),
          marginFormatted: m.formatted_value,
          marketCap: cap?.exact_value ? Number(cap.exact_value) : 1e11,
          marketCapFormatted: cap?.formatted_value || "N/A",
        };
      })
      .filter(Boolean) as any[];
  }, [comparison]);

  // Medians for quadrant reference
  const medianGrowth = comparison?.statistics["growth.revenue_growth"]?.median ?? 0;
  const medianMargin = comparison?.statistics["profitability.operating_margin"]?.median ?? 0;

  if (isLoading || !comparison) return null;
  if (plotData.length < 2) return null;

  const width = 760;
  const height = 320;
  const margin = { top: 30, right: 40, bottom: 50, left: 60 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Extents
  const minX = Math.min(...plotData.map((d) => d.growth), 0) - 4;
  const maxX = Math.max(...plotData.map((d) => d.growth), 20) + 4;
  const minY = Math.min(...plotData.map((d) => d.margin), 0) - 4;
  const maxY = Math.max(...plotData.map((d) => d.margin), 40) + 4;

  const getX = (val: number) => ((val - minX) / (maxX - minX)) * innerWidth;
  const getY = (val: number) => innerHeight - ((val - minY) / (maxY - minY)) * innerHeight;

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded p-4 mb-4">
      <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle mb-4">
        <div>
          <h4 className="text-xs font-semibold text-atlas-text-primary flex items-center gap-1.5">
            <ScatterChart className="w-4 h-4 text-atlas-accent" />
            Competitive Positioning Matrix: Growth vs Operating Margin
          </h4>
          <p className="text-[11px] text-atlas-text-muted mt-0.5">
            Bubble size proportional to Market Capitalization. Dashed crosshairs indicate peer median benchmarks.
          </p>
        </div>

        {hoveredCompany && (
          <div className="text-right text-xs bg-atlas-surface-subtle px-2.5 py-1 rounded border border-atlas-border-subtle">
            <span className="font-semibold text-atlas-text-primary">{hoveredCompany.display_name}</span>{" "}
            <span className="font-mono text-atlas-accent">({hoveredCompany.ticker})</span>:{" "}
            <span className="text-atlas-text-muted">Growth:</span>{" "}
            <span className="font-mono text-emerald-400 font-medium">{hoveredCompany.growthFormatted}</span> |{" "}
            <span className="text-atlas-text-muted">Op Margin:</span>{" "}
            <span className="font-mono text-purple-400 font-medium">{hoveredCompany.marginFormatted}</span> |{" "}
            <span className="text-atlas-text-muted">Cap:</span>{" "}
            <span className="font-mono text-atlas-text-secondary">{hoveredCompany.marketCapFormatted}</span>
          </div>
        )}
      </div>

      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[650px] font-mono text-[10px]">
          <g transform={`translate(${margin.left}, ${margin.top})`}>
            {/* Median Reference Crosshairs */}
            <line
              x1={getX(Number(medianGrowth))}
              y1={0}
              x2={getX(Number(medianGrowth))}
              y2={innerHeight}
              stroke="currentColor"
              strokeDasharray="4 4"
              className="text-atlas-border-subtle opacity-70"
            />
            <line
              x1={0}
              y1={getY(Number(medianMargin))}
              x2={innerWidth}
              y2={getY(Number(medianMargin))}
              stroke="currentColor"
              strokeDasharray="4 4"
              className="text-atlas-border-subtle opacity-70"
            />

            {/* Quadrant labels */}
            <text x={innerWidth - 10} y={15} textAnchor="end" className="text-atlas-text-muted fill-current opacity-40 text-[9px] font-sans">
              HIGH GROWTH / HIGH MARGIN
            </text>
            <text x={10} y={innerHeight - 10} textAnchor="start" className="text-atlas-text-muted fill-current opacity-40 text-[9px] font-sans">
              LOW GROWTH / LOW MARGIN
            </text>

            {/* X-axis ticks */}
            {[-10, 0, 10, 20, 30].filter((val) => val >= minX && val <= maxX).map((val) => (
              <g key={val} transform={`translate(${getX(val)}, ${innerHeight})`}>
                <line y2={5} stroke="currentColor" className="text-atlas-border-subtle" />
                <text y={18} textAnchor="middle" fill="currentColor" className="text-atlas-text-muted">
                  {val}%
                </text>
              </g>
            ))}

            {/* Y-axis ticks */}
            {[0, 10, 20, 30, 40].filter((val) => val >= minY && val <= maxY).map((val) => (
              <g key={val} transform={`translate(0, ${getY(val)})`}>
                <line x2={-5} stroke="currentColor" className="text-atlas-border-subtle" />
                <text x={-10} y={3} textAnchor="end" fill="currentColor" className="text-atlas-text-muted">
                  {val}%
                </text>
              </g>
            ))}

            {/* Axis Titles */}
            <text x={innerWidth / 2} y={innerHeight + 35} textAnchor="middle" fill="currentColor" className="text-atlas-text-secondary font-medium font-sans text-[11px]">
              Revenue Growth YoY (%)
            </text>
            <text transform="rotate(-90)" x={-innerHeight / 2} y={-40} textAnchor="middle" fill="currentColor" className="text-atlas-text-secondary font-medium font-sans text-[11px]">
              Operating Margin (%)
            </text>

            {/* Data Bubbles */}
            {plotData.map((d) => {
              const cx = getX(d.growth);
              const cy = getY(d.margin);
              // Radius scaled by sqrt of market cap (normalized between 7 and 18 px)
              const r = Math.max(7, Math.min(22, Math.sqrt(d.marketCap / 1e9) * 0.35 + 6));

              return (
                <g
                  key={d.company_id}
                  className="cursor-pointer transition-transform"
                  onMouseEnter={() => setHoveredCompany(d)}
                  onMouseLeave={() => setHoveredCompany(null)}
                >
                  <circle
                    cx={cx}
                    cy={cy}
                    r={r}
                    fill={d.is_subject ? "#38bdf8" : "#818cf8"}
                    fillOpacity={d.is_subject ? 0.85 : 0.55}
                    stroke={d.is_subject ? "#ffffff" : "#4f46e5"}
                    strokeWidth={d.is_subject ? 2.5 : 1.5}
                  />
                  <text
                    x={cx}
                    y={cy - r - 4}
                    textAnchor="middle"
                    fill="currentColor"
                    className={`text-[10px] font-bold ${
                      d.is_subject ? "text-atlas-accent" : "text-atlas-text-secondary"
                    }`}
                  >
                    {d.ticker}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>
    </div>
  );
}
