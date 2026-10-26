"use client";

import React, { useMemo, useState } from "react";
import {
  Calendar,
  Layers,
  BarChart2,
  TrendingUp,
  ShieldCheck,
  Maximize2,
  RefreshCw,
} from "lucide-react";
import {
  DateRangePreset,
  EconomicObservationDTO,
  EconomicSeriesObservationsResponseDTO,
  TransformationType,
} from "@/lib/economics";

interface EconomicSeriesChartProps {
  seriesData: EconomicSeriesObservationsResponseDTO | null;
  isLoading?: boolean;
  activeDateRange: DateRangePreset;
  onSelectDateRange: (range: DateRangePreset) => void;
  activeTransformation: TransformationType;
  onSelectTransformation: (t: TransformationType) => void;
}

export function EconomicSeriesChart({
  seriesData,
  isLoading = false,
  activeDateRange,
  onSelectDateRange,
  activeTransformation,
  onSelectTransformation,
}: EconomicSeriesChartProps) {
  const [chartType, setChartType] = useState<"line" | "bar">("line");
  const [hoveredObs, setHoveredObs] = useState<EconomicObservationDTO | null>(null);

  // Filter observations based on activeDateRange preset
  const displayObservations = useMemo(() => {
    if (!seriesData || !seriesData.observations) return [];
    const obs = [...seriesData.observations];

    // Determine count to take based on frequency and preset
    let count = obs.length;
    const freq = seriesData.series.frequency;

    if (activeDateRange === "1Y") {
      count = freq === "MONTHLY" ? 12 : freq === "QUARTERLY" ? 4 : 2;
    } else if (activeDateRange === "3Y") {
      count = freq === "MONTHLY" ? 36 : freq === "QUARTERLY" ? 12 : 3;
    } else if (activeDateRange === "5Y") {
      count = freq === "MONTHLY" ? 60 : freq === "QUARTERLY" ? 20 : 5;
    } else if (activeDateRange === "10Y") {
      count = freq === "MONTHLY" ? 120 : freq === "QUARTERLY" ? 40 : 10;
    }

    return obs.slice(-count);
  }, [seriesData, activeDateRange]);

  // Compute SVG dimensions and scales
  const svgWidth = 800;
  const svgHeight = 280;
  const padding = { top: 20, right: 30, bottom: 40, left: 50 };

  const chartBounds = useMemo(() => {
    if (displayObservations.length === 0) {
      return { minVal: 0, maxVal: 1, zeroY: svgHeight / 2 };
    }
    const values = displayObservations.map((o) => o.value);
    let minVal = Math.min(...values);
    let maxVal = Math.max(...values);

    // If all positive or all negative, ensure 0 is in scale or pad gracefully
    if (minVal > 0) minVal = 0;
    if (maxVal < 0) maxVal = 0;

    const span = maxVal - minVal || 1;
    minVal -= span * 0.08;
    maxVal += span * 0.08;

    return { minVal, maxVal };
  }, [displayObservations, svgHeight]);

  const { minVal, maxVal } = chartBounds;

  const getY = (val: number) => {
    const ratio = (val - minVal) / (maxVal - minVal);
    return svgHeight - padding.bottom - ratio * (svgHeight - padding.top - padding.bottom);
  };

  const getX = (idx: number, total: number) => {
    if (total <= 1) return padding.left + (svgWidth - padding.left - padding.right) / 2;
    return (
      padding.left +
      (idx / (total - 1)) * (svgWidth - padding.left - padding.right)
    );
  };

  // Generate SVG Path for line
  const linePath = useMemo(() => {
    if (displayObservations.length < 2) return "";
    return displayObservations
      .map((obs, idx) => {
        const x = getX(idx, displayObservations.length);
        const y = getY(obs.value);
        return `${idx === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
      })
      .join(" ");
  }, [displayObservations, minVal, maxVal]);

  const zeroY = getY(0);

  if (isLoading) {
    return (
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded p-6 flex flex-col items-center justify-center min-h-[360px] text-atlas-text-muted text-xs">
        <RefreshCw className="w-5 h-5 animate-spin text-atlas-accent mb-2" />
        <span>Loading historical economic time-series observations...</span>
      </div>
    );
  }

  if (!seriesData) {
    return (
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded p-6 text-center text-atlas-text-muted text-xs">
        Select an economic series to display historical charts.
      </div>
    );
  }

  const { series, geography, indicator, effective_unit } = seriesData;

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded p-4 mb-6">
      {/* Chart Top Header & Metadata */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-3 border-b border-atlas-border-subtle mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-semibold px-1.5 py-0.5 rounded bg-atlas-accent/15 text-atlas-accent">
              {geography.iso_code}
            </span>
            <h3 className="text-sm font-bold text-atlas-text-primary">
              {series.series_name}
            </h3>
            <span className="text-[10px] font-mono bg-atlas-border-subtle/50 text-atlas-text-muted px-1.5 py-0.5 rounded">
              {series.frequency} &bull; {series.seasonal_adjustment === "SEASONALLY_ADJUSTED" ? "SA" : "NSA"}
            </span>
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-1 flex flex-wrap items-center gap-3">
            <span>Agency: {geography.statistical_agency}</span>
            <span>&bull;</span>
            <span>Provider: {series.source_provider_id}</span>
            <span>&bull;</span>
            <span>Unit: {effective_unit}</span>
            {series.index_base && (
              <>
                <span>&bull;</span>
                <span>Base: {series.index_base}</span>
              </>
            )}
          </div>
        </div>

        {/* Controls: Date Range, Transformations, Chart Type */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Transformation Selector */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-atlas-text-muted font-medium">Transform:</span>
            <select
              value={activeTransformation}
              onChange={(e) => onSelectTransformation(e.target.value as TransformationType)}
              className="text-xs bg-atlas-background border border-atlas-border-subtle rounded px-2 py-1 text-atlas-text-primary focus:outline-none focus:border-atlas-accent"
            >
              <option value="SOURCE_REPORTED">Source Reported (Raw)</option>
              <option value="YEAR_OVER_YEAR">Year-over-Year (YoY %)</option>
              <option value="MONTH_OVER_MONTH">Month-over-Month (MoM %)</option>
              <option value="QUARTER_OVER_QUARTER">Quarter-over-Quarter (QoQ %)</option>
              <option value="ANNUALIZED_QUARTERLY_GROWTH">Annualized QoQ Growth (%)</option>
              <option value="PERCENTAGE_POINT_CHANGE">Change (% Points)</option>
              <option value="BASIS_POINT_CHANGE">Change (Basis Points)</option>
            </select>
          </div>

          {/* Date Presets */}
          <div className="flex items-center bg-atlas-background border border-atlas-border-subtle rounded p-0.5 text-xs">
            {(["1Y", "3Y", "5Y", "10Y", "MAX"] as DateRangePreset[]).map((preset) => (
              <button
                key={preset}
                onClick={() => onSelectDateRange(preset)}
                className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                  activeDateRange === preset
                    ? "bg-atlas-accent text-white font-semibold"
                    : "text-atlas-text-muted hover:text-atlas-text-primary"
                }`}
              >
                {preset}
              </button>
            ))}
          </div>

          {/* Chart Type Toggle */}
          <div className="flex items-center bg-atlas-background border border-atlas-border-subtle rounded p-0.5">
            <button
              onClick={() => setChartType("line")}
              className={`p-1 rounded ${
                chartType === "line"
                  ? "bg-atlas-surface text-atlas-accent shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
              title="Line Chart"
            >
              <TrendingUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setChartType("bar")}
              className={`p-1 rounded ${
                chartType === "bar"
                  ? "bg-atlas-surface text-atlas-accent shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
              title="Bar Chart"
            >
              <BarChart2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Interactive SVG Chart Canvas */}
      <div className="relative w-full overflow-hidden">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto max-h-[320px] select-none"
        >
          {/* Horizontal Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, idx) => {
            const val = minVal + pct * (maxVal - minVal);
            const y = getY(val);
            return (
              <g key={idx}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={svgWidth - padding.right}
                  y2={y}
                  stroke="currentColor"
                  className="text-atlas-border-subtle/40"
                  strokeDasharray="2 2"
                />
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  textAnchor="end"
                  className="fill-atlas-text-muted text-[9px] font-mono"
                >
                  {val.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* Zero Baseline (if in range) */}
          {minVal <= 0 && maxVal >= 0 && (
            <line
              x1={padding.left}
              y1={zeroY}
              x2={svgWidth - padding.right}
              y2={zeroY}
              stroke="currentColor"
              className="text-atlas-text-muted/60"
              strokeWidth="1.2"
            />
          )}

          {/* Bar Chart Mode */}
          {chartType === "bar" &&
            displayObservations.map((obs, idx) => {
              const x = getX(idx, displayObservations.length);
              const barWidth = Math.max(3, (svgWidth - padding.left - padding.right) / (displayObservations.length * 1.8));
              const yVal = getY(obs.value);
              const isPositive = obs.value >= 0;
              const y = isPositive ? yVal : zeroY;
              const height = Math.abs(yVal - zeroY) || 1;

              return (
                <rect
                  key={obs.observation_id || idx}
                  x={x - barWidth / 2}
                  y={y}
                  width={barWidth}
                  height={height}
                  fill={isPositive ? "rgba(16, 185, 129, 0.75)" : "rgba(244, 63, 94, 0.75)"}
                  className="hover:opacity-100 cursor-pointer transition-opacity"
                  onMouseEnter={() => setHoveredObs(obs)}
                  onMouseLeave={() => setHoveredObs(null)}
                />
              );
            })}

          {/* Line Chart Mode */}
          {chartType === "line" && (
            <>
              <path
                d={linePath}
                fill="none"
                stroke="currentColor"
                className="text-atlas-accent"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              {displayObservations.map((obs, idx) => {
                const x = getX(idx, displayObservations.length);
                const y = getY(obs.value);
                return (
                  <circle
                    key={obs.observation_id || idx}
                    cx={x}
                    cy={y}
                    r={displayObservations.length > 50 ? 2 : 3}
                    className="fill-atlas-accent hover:fill-white cursor-pointer transition-colors"
                    onMouseEnter={() => setHoveredObs(obs)}
                    onMouseLeave={() => setHoveredObs(null)}
                  />
                );
              })}
            </>
          )}

          {/* Time Axis Labels (Every nth label to prevent overlap) */}
          {displayObservations.map((obs, idx) => {
            const step = Math.ceil(displayObservations.length / 8) || 1;
            if (idx % step !== 0 && idx !== displayObservations.length - 1) return null;
            const x = getX(idx, displayObservations.length);
            return (
              <text
                key={idx}
                x={x}
                y={svgHeight - padding.bottom + 16}
                textAnchor="middle"
                className="fill-atlas-text-muted text-[9px] font-mono"
              >
                {obs.reference_period}
              </text>
            );
          })}
        </svg>

        {/* Hover Observation Tooltip / Info Card */}
        {hoveredObs && (
          <div className="absolute top-2 right-2 bg-atlas-surface/95 backdrop-blur-xs border border-atlas-border-subtle rounded p-2.5 shadow-md pointer-events-none text-xs min-w-[200px]">
            <div className="flex items-center justify-between text-[11px] text-atlas-text-muted font-mono mb-1">
              <span>{hoveredObs.reference_period}</span>
              <span className="px-1 rounded bg-atlas-border-subtle/60 text-atlas-text-primary text-[10px]">
                {hoveredObs.status}
              </span>
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-lg font-bold font-mono text-atlas-text-primary">
                {hoveredObs.value.toFixed(3)}
              </span>
              <span className="text-[11px] font-mono text-atlas-text-muted">
                {effective_unit}
              </span>
            </div>
            {hoveredObs.published_at && (
              <div className="text-[10px] text-atlas-text-muted mt-1">
                Release: {hoveredObs.published_at.slice(0, 10)}
              </div>
            )}
            {hoveredObs.source_revision && (
              <div className="text-[10px] text-atlas-text-muted">
                Revision: {hoveredObs.source_revision}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between text-[11px] text-atlas-text-muted pt-2 border-t border-atlas-border-subtle/50 mt-1">
        <span>Displaying {displayObservations.length} historical observations ({series.earliest_period} &mdash; {series.latest_period})</span>
        <span className="font-mono text-emerald-400 flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5" />
          Authentic Sovereign Statistics
        </span>
      </div>
    </div>
  );
}
