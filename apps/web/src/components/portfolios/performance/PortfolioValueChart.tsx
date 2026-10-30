"use client";

import React, { useMemo, useState } from "react";
import { PerformanceSeriesPoint } from "@/lib/portfolios/performance/types";
import { formatCurrency } from "@/lib/portfolios/performance/formatting";

interface PortfolioValueChartProps {
  points: PerformanceSeriesPoint[];
  baseCurrency: string;
}

export function PortfolioValueChart({ points, baseCurrency }: PortfolioValueChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const parsed = useMemo(() => {
    if (!points || points.length === 0) return [];
    return points.map((p, idx) => ({
      index: idx,
      date: new Date(p.timestamp),
      dateStr: new Date(p.timestamp).toLocaleDateString(),
      portfolioValue: parseFloat(p.portfolio_value || "0.00"),
      cashFlowAmount: p.cash_flow_amount ? parseFloat(p.cash_flow_amount) : null,
      cashFlowType: p.cash_flow_type,
    }));
  }, [points]);

  if (parsed.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-sm border border-atlas-border-default/60 bg-atlas-surface-1 text-xs text-atlas-text-tertiary">
        No equity value points recorded for this period.
      </div>
    );
  }

  const values = parsed.map((p) => p.portfolioValue);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const range = maxVal - minVal || 1;

  const width = 800;
  const height = 260;
  const paddingX = 60;
  const paddingY = 30;
  const chartW = width - paddingX * 2;
  const chartH = height - paddingY * 2;

  const getX = (idx: number) => {
    if (parsed.length <= 1) return paddingX + chartW / 2;
    return paddingX + (idx / (parsed.length - 1)) * chartW;
  };

  const getY = (val: number) => {
    return height - paddingY - ((val - minVal) / range) * chartH;
  };

  const linePath = parsed
    .map((p, i) => `${i === 0 ? "M" : "L"} ${getX(i)} ${getY(p.portfolioValue)}`)
    .join(" ");

  const areaPath = `${linePath} L ${getX(parsed.length - 1)} ${height - paddingY} L ${getX(0)} ${height - paddingY} Z`;

  const activePoint = hoveredIndex !== null ? parsed[hoveredIndex] : parsed[parsed.length - 1];

  return (
    <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-4 shadow-xs">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default/40 pb-2.5">
        <div>
          <h4 className="text-xs font-semibold text-atlas-text-primary">
            Portfolio Historical Valuation (Monetary Equity Curve)
          </h4>
          <p className="text-[11px] text-atlas-text-secondary">
            Total marked portfolio valuation in {baseCurrency} across cash and security holdings.
          </p>
        </div>
        <div className="flex items-center gap-3 font-mono text-xs">
          <span className="text-atlas-text-secondary">Date:</span>
          <span className="text-atlas-text-primary">{activePoint?.dateStr}</span>
          <span className="text-atlas-border-default">|</span>
          <span className="text-atlas-text-secondary">Value:</span>
          <span className="text-base font-bold text-atlas-accent">
            {formatCurrency(activePoint?.portfolioValue, baseCurrency)}
          </span>
        </div>
      </div>

      <div className="relative mt-3">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="h-64 w-full overflow-visible font-mono text-[10px]"
        >
          <defs>
            <linearGradient id="valGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Area fill */}
          <path d={areaPath} fill="url(#valGrad)" />

          {/* Grid lines */}
          <line
            x1={paddingX}
            y1={paddingY}
            x2={width - paddingX}
            y2={paddingY}
            stroke="#334155"
            strokeDasharray="2 2"
            strokeWidth="0.5"
          />
          <text
            x={paddingX - 8}
            y={paddingY + 3}
            fill="#64748b"
            textAnchor="end"
            fontSize="10"
          >
            {formatCurrency(maxVal, baseCurrency, { decimals: 0 })}
          </text>

          <line
            x1={paddingX}
            y1={height - paddingY}
            x2={width - paddingX}
            y2={height - paddingY}
            stroke="#334155"
            strokeDasharray="2 2"
            strokeWidth="0.5"
          />
          <text
            x={paddingX - 8}
            y={height - paddingY + 3}
            fill="#64748b"
            textAnchor="end"
            fontSize="10"
          >
            {formatCurrency(minVal, baseCurrency, { decimals: 0 })}
          </text>

          {/* Main line */}
          <path
            d={linePath}
            fill="none"
            stroke="#38bdf8"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Nodes */}
          {parsed.map((p, idx) => {
            const cx = getX(idx);
            const cy = getY(p.portfolioValue);
            const isHovered = hoveredIndex === idx;

            return (
              <g
                key={idx}
                onMouseEnter={() => setHoveredIndex(idx)}
                onMouseLeave={() => setHoveredIndex(null)}
                className="cursor-pointer"
              >
                <circle
                  cx={cx}
                  cy={cy}
                  r={isHovered ? 4.5 : 2.5}
                  fill={isHovered ? "#ffffff" : "#38bdf8"}
                  stroke="#0f172a"
                  strokeWidth="1.5"
                />
                {isHovered && (
                  <line
                    x1={cx}
                    y1={paddingY}
                    x2={cx}
                    y2={height - paddingY}
                    stroke="#94a3b8"
                    strokeWidth="1"
                    strokeDasharray="3 3"
                  />
                )}
              </g>
            );
          })}
        </svg>

        <div className="flex justify-between px-14 text-[10px] font-mono text-atlas-text-tertiary">
          <span>{parsed[0]?.dateStr}</span>
          {parsed.length > 2 && (
            <span>{parsed[Math.floor(parsed.length / 2)]?.dateStr}</span>
          )}
          <span>{parsed[parsed.length - 1]?.dateStr}</span>
        </div>
      </div>
    </div>
  );
}

