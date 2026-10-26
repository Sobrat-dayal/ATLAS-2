"use client";

import React from "react";
import {
  ComparableIndicatorDTO,
  DistributionSummaryDTO,
  WeightingPolicy,
} from "@/lib/economics/comparisons";
import { Activity, BarChart2, Info, PieChart, ShieldAlert } from "lucide-react";

interface MacroDistributionPanelProps {
  distributionData: DistributionSummaryDTO | null;
  indicators: ComparableIndicatorDTO[];
  weightingPolicy: WeightingPolicy;
  onChangeWeightingPolicy: (policy: WeightingPolicy) => void;
  isLoading: boolean;
}

export function MacroDistributionPanel({
  distributionData,
  indicators,
  weightingPolicy,
  onChangeWeightingPolicy,
  isLoading,
}: MacroDistributionPanelProps) {
  if (isLoading && !distributionData) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2">
        <div className="w-6 h-6 border-2 border-atlas-accent border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-mono">Calculating Descriptive Statistical Distributions...</span>
      </div>
    );
  }

  if (!distributionData || distributionData.sample_size === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2 border border-dashed border-atlas-border-subtle rounded m-4">
        <Info className="w-8 h-8 text-atlas-text-muted/60" />
        <p className="text-sm font-medium text-atlas-text-primary">No Distribution Sample Available</p>
        <p className="text-xs text-atlas-text-muted">
          At least two eligible country observations are required to calculate distribution statistics.
        </p>
      </div>
    );
  }

  const indicatorDef = indicators.find((i) => i.metric_kind === distributionData.metric_kind);
  const iqr = distributionData.q3 - distributionData.q1;
  const range = distributionData.maximum - distributionData.minimum;

  return (
    <div className="flex flex-col flex-1 h-full min-h-0 bg-atlas-background overflow-y-auto p-4 gap-4">
      {/* Distribution Header & Weighting Control */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded bg-atlas-surface/60 border border-atlas-border-subtle text-xs">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded bg-emerald-500/15 text-emerald-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-bold text-atlas-text-primary text-sm tracking-tight">
              Statistical Distribution: {indicatorDef?.name || distributionData.metric_kind}
            </h2>
            <div className="flex items-center gap-2 text-atlas-text-muted text-[11px] font-mono">
              <span>Period: {distributionData.reference_period}</span>
              <span>•</span>
              <span>Unit: {distributionData.unit}</span>
              <span>•</span>
              <span>Sample N = {distributionData.sample_size}</span>
            </div>
          </div>
        </div>

        {/* Weighting Selector */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] uppercase font-mono text-atlas-text-muted">Weighting Mode:</span>
          <select
            value={weightingPolicy}
            onChange={(e) => onChangeWeightingPolicy(e.target.value as WeightingPolicy)}
            className="bg-atlas-surface border border-atlas-border-subtle rounded px-2.5 py-1 text-xs text-atlas-text-primary focus:outline-hidden"
          >
            <option value="equal_weight">Equal Country Weights (Unweighted)</option>
            <option value="population_weighted">Population-Weighted (Demographic)</option>
            <option value="gdp_weighted">GDP-Weighted (Economic Size)</option>
          </select>
        </div>
      </div>

      {/* Primary Statistical Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono">
        <div className="p-3 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-1">
          <span className="text-[10px] text-atlas-text-muted uppercase">Mean (Average)</span>
          <span className="text-lg font-bold text-atlas-text-primary">
            {distributionData.mean.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </span>
          <span className="text-[10px] text-atlas-text-muted/70">{distributionData.unit}</span>
        </div>

        <div className="p-3 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-1">
          <span className="text-[10px] text-atlas-text-muted uppercase">Median (50th %ile)</span>
          <span className="text-lg font-bold text-emerald-400">
            {distributionData.median.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </span>
          <span className="text-[10px] text-atlas-text-muted/70">{distributionData.unit}</span>
        </div>

        <div className="p-3 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-1">
          <span className="text-[10px] text-atlas-text-muted uppercase">Std Deviation (σ)</span>
          <span className="text-lg font-bold text-indigo-400">
            {distributionData.standard_deviation.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </span>
          <span className="text-[10px] text-atlas-text-muted/70">Sample dispersion</span>
        </div>

        <div className="p-3 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-1">
          <span className="text-[10px] text-atlas-text-muted uppercase">Min / Max</span>
          <span className="text-sm font-bold text-atlas-text-primary">
            {distributionData.minimum.toLocaleString(undefined, { maximumFractionDigits: 1 })} /{" "}
            {distributionData.maximum.toLocaleString(undefined, { maximumFractionDigits: 1 })}
          </span>
          <span className="text-[10px] text-atlas-text-muted/70">Range: {range.toFixed(1)}</span>
        </div>

        <div className="p-3 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-1">
          <span className="text-[10px] text-atlas-text-muted uppercase">Quartiles (Q1 / Q3)</span>
          <span className="text-sm font-bold text-atlas-text-primary">
            {distributionData.q1.toLocaleString(undefined, { maximumFractionDigits: 1 })} /{" "}
            {distributionData.q3.toLocaleString(undefined, { maximumFractionDigits: 1 })}
          </span>
          <span className="text-[10px] text-atlas-text-muted/70">IQR: {iqr.toFixed(1)}</span>
        </div>

        <div className="p-3 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-1">
          <span className="text-[10px] text-atlas-text-muted uppercase">Sample Size</span>
          <span className="text-lg font-bold text-atlas-accent">
            {distributionData.sample_size} of {distributionData.total_eligible_geographies}
          </span>
          <span className="text-[10px] text-atlas-text-muted/70">
            Excluded: {distributionData.excluded_geography_ids.length}
          </span>
        </div>
      </div>

      {/* Visual Quantile Box-Range Diagram */}
      <div className="p-4 rounded bg-atlas-surface/30 border border-atlas-border-subtle flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs">
          <span className="font-semibold text-atlas-text-primary">Sample Dispersion Diagram</span>
          <span className="text-[11px] font-mono text-atlas-text-muted">
            Min ({distributionData.minimum.toFixed(1)}) → Q1 ({distributionData.q1.toFixed(1)}) → Median (
            {distributionData.median.toFixed(1)}) → Q3 ({distributionData.q3.toFixed(1)}) → Max (
            {distributionData.maximum.toFixed(1)})
          </span>
        </div>

        {/* Quantile Gradient Rail */}
        <div className="h-6 w-full rounded bg-atlas-surface border border-atlas-border-subtle relative overflow-hidden flex items-center px-2">
          {/* Box area for Q1 to Q3 */}
          <div
            className="absolute top-1 bottom-1 bg-emerald-500/20 border-x-2 border-emerald-500/60 rounded-xs"
            style={{
              left: `${Math.max(0, Math.min(100, range > 0 ? ((distributionData.q1 - distributionData.minimum) / range) * 100 : 0))}%`,
              width: `${Math.max(4, Math.min(100, range > 0 ? (iqr / range) * 100 : 100))}%`,
            }}
          />
          {/* Median needle */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-emerald-400 z-10"
            style={{
              left: `${Math.max(0, Math.min(100, range > 0 ? ((distributionData.median - distributionData.minimum) / range) * 100 : 50))}%`,
            }}
          />
        </div>

        <div className="flex items-center justify-between text-[11px] font-mono text-atlas-text-muted">
          <span>Min: {distributionData.minimum.toLocaleString()}</span>
          <span>IQR: [ {distributionData.q1.toLocaleString()} - {distributionData.q3.toLocaleString()} ]</span>
          <span>Max: {distributionData.maximum.toLocaleString()}</span>
        </div>
      </div>

      {/* Excluded Geographies Notice */}
      {distributionData.excluded_geography_ids.length > 0 && (
        <div className="p-3 rounded bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200/90 flex items-start gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="flex flex-col gap-0.5">
            <span className="font-semibold text-amber-300">Sample Exclusions Disclosed</span>
            <p>
              {distributionData.excluded_geography_ids.length} countries were excluded from this distribution due to missing observations in the reference period ({distributionData.reference_period}). ATLAS never treats absent observations as zero.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
