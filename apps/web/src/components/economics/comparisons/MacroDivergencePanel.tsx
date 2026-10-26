"use client";

import React from "react";
import {
  ComparableIndicatorDTO,
  DivergenceAnalysisResponseDTO,
} from "@/lib/economics/comparisons";
import { GeographyOption } from "@/hooks/economics/useMacroComparisons";
import { ArrowRight, GitCompare, Info, Scale } from "lucide-react";

interface MacroDivergencePanelProps {
  divergenceData: DivergenceAnalysisResponseDTO | null;
  indicators: ComparableIndicatorDTO[];
  geographies: GeographyOption[];
  divergenceCountryA: string;
  onChangeCountryA: (geoId: string) => void;
  divergenceCountryB: string;
  onChangeCountryB: (geoId: string) => void;
  isLoading: boolean;
}

export function MacroDivergencePanel({
  divergenceData,
  indicators,
  geographies,
  divergenceCountryA,
  onChangeCountryA,
  divergenceCountryB,
  onChangeCountryB,
  isLoading,
}: MacroDivergencePanelProps) {
  if (isLoading && !divergenceData) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2">
        <div className="w-6 h-6 border-2 border-atlas-accent border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-mono">Computing Convergence & Divergence Differentials...</span>
      </div>
    );
  }

  if (!divergenceData || divergenceData.points.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2 border border-dashed border-atlas-border-subtle rounded m-4">
        <Info className="w-8 h-8 text-atlas-text-muted/60" />
        <p className="text-sm font-medium text-atlas-text-primary">No Overlapping Divergence Periods</p>
        <p className="text-xs text-atlas-text-muted">
          Select two countries with overlapping historical reporting periods.
        </p>
      </div>
    );
  }

  const indicatorDef = indicators.find((i) => i.metric_kind === divergenceData.metric_kind);
  const isBps = divergenceData.unit === "bps";

  return (
    <div className="flex flex-col flex-1 h-full min-h-0 bg-atlas-background overflow-y-auto p-4 gap-4">
      {/* Pair Selection Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded bg-atlas-surface/60 border border-atlas-border-subtle text-xs">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded bg-amber-500/15 text-amber-400">
            <GitCompare className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-bold text-atlas-text-primary text-sm tracking-tight">
              Convergence / Divergence Analysis
            </h2>
            <div className="flex items-center gap-2 text-atlas-text-muted text-[11px] font-mono">
              <span>Metric: {indicatorDef?.name || divergenceData.metric_kind}</span>
              <span>•</span>
              <span>Unit: {divergenceData.unit}</span>
            </div>
          </div>
        </div>

        {/* Pairwise Selectors */}
        <div className="flex items-center gap-2">
          <select
            value={divergenceCountryA}
            onChange={(e) => onChangeCountryA(e.target.value)}
            className="bg-atlas-surface border border-atlas-border-subtle rounded px-2.5 py-1 text-xs text-atlas-text-primary font-mono focus:outline-hidden"
          >
            {geographies.map((g) => (
              <option key={g.geography_id} value={g.geography_id} disabled={g.geography_id === divergenceCountryB}>
                {g.name} ({g.iso_code})
              </option>
            ))}
          </select>

          <ArrowRight className="w-3.5 h-3.5 text-atlas-text-muted" />

          <select
            value={divergenceCountryB}
            onChange={(e) => onChangeCountryB(e.target.value)}
            className="bg-atlas-surface border border-atlas-border-subtle rounded px-2.5 py-1 text-xs text-atlas-text-primary font-mono focus:outline-hidden"
          >
            {geographies.map((g) => (
              <option key={g.geography_id} value={g.geography_id} disabled={g.geography_id === divergenceCountryA}>
                {g.name} ({g.iso_code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Headline Differential Summary Card */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono">
        <div className="p-3.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-1">
          <span className="text-[10px] text-atlas-text-muted uppercase">
            Latest {divergenceData.country_a_name} Value
          </span>
          <span className="text-lg font-bold text-atlas-text-primary">
            {divergenceData.points[divergenceData.points.length - 1]?.country_a_value.toLocaleString(undefined, {
              maximumFractionDigits: 2,
            })}
          </span>
          <span className="text-[10px] text-atlas-text-muted/70">
            Period: {divergenceData.points[divergenceData.points.length - 1]?.reference_period}
          </span>
        </div>

        <div className="p-3.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-1">
          <span className="text-[10px] text-atlas-text-muted uppercase">
            Latest {divergenceData.country_b_name} Value
          </span>
          <span className="text-lg font-bold text-atlas-text-primary">
            {divergenceData.points[divergenceData.points.length - 1]?.country_b_value.toLocaleString(undefined, {
              maximumFractionDigits: 2,
            })}
          </span>
          <span className="text-[10px] text-atlas-text-muted/70">
            Period: {divergenceData.points[divergenceData.points.length - 1]?.reference_period}
          </span>
        </div>

        <div className="p-3.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-1">
          <span className="text-[10px] text-atlas-text-muted uppercase">
            Spread Differential ({divergenceData.country_a_name} − {divergenceData.country_b_name})
          </span>
          <span
            className={`text-lg font-bold ${
              divergenceData.latest_differential > 0
                ? "text-emerald-400"
                : divergenceData.latest_differential < 0
                ? "text-rose-400"
                : "text-atlas-text-primary"
            }`}
          >
            {divergenceData.latest_differential > 0 ? "+" : ""}
            {divergenceData.latest_differential.toLocaleString(undefined, { maximumFractionDigits: 2 })}{" "}
            {divergenceData.unit}
          </span>
          <span className="text-[10px] text-atlas-text-muted/70">
            {isBps ? "Basis points spread" : "Percentage points gap"}
          </span>
        </div>
      </div>

      {/* Historical Spread Table */}
      <div className="border border-atlas-border-subtle rounded bg-atlas-surface/20 overflow-auto">
        <table className="w-full border-collapse text-left text-xs font-mono">
          <thead className="bg-atlas-surface border-b border-atlas-border-subtle">
            <tr>
              <th className="p-2.5 font-bold text-atlas-text-primary">Reference Period</th>
              <th className="p-2.5 font-semibold text-atlas-text-secondary text-right">
                {divergenceData.country_a_name}
              </th>
              <th className="p-2.5 font-semibold text-atlas-text-secondary text-right">
                {divergenceData.country_b_name}
              </th>
              <th className="p-2.5 font-semibold text-atlas-text-secondary text-right">
                Differential ({divergenceData.unit})
              </th>
              {divergenceData.points.some((p) => p.ratio !== null) && (
                <th className="p-2.5 font-semibold text-atlas-text-secondary text-right">Ratio (A / B)</th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle/40">
            {divergenceData.points.map((pt) => (
              <tr key={pt.reference_period} className="hover:bg-atlas-surface/40">
                <td className="p-2.5 font-semibold text-atlas-text-primary">{pt.reference_period}</td>
                <td className="p-2.5 text-right font-medium text-atlas-text-primary">
                  {pt.country_a_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </td>
                <td className="p-2.5 text-right font-medium text-atlas-text-primary">
                  {pt.country_b_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </td>
                <td
                  className={`p-2.5 text-right font-bold ${
                    pt.differential_value > 0
                      ? "text-emerald-400"
                      : pt.differential_value < 0
                      ? "text-rose-400"
                      : "text-atlas-text-primary"
                  }`}
                >
                  {pt.differential_value > 0 ? "+" : ""}
                  {pt.differential_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </td>
                {pt.ratio !== null && pt.ratio !== undefined && (
                  <td className="p-2.5 text-right text-atlas-text-muted">
                    {pt.ratio.toFixed(2)}x
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Methodological qualification banner */}
      <div className="p-2.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle/60 text-[11px] text-atlas-text-muted flex items-start gap-2">
        <Scale className="w-4 h-4 text-atlas-accent shrink-0 mt-0.5" />
        <div className="flex flex-col gap-0.5">
          <span className="font-semibold text-atlas-text-primary">Spread Interpretation Notice</span>
          <p>
            Economic differentials are calculated on period-aligned observations without temporal interpolation. Interest rate differences in basis points reflect nominal policy spread and do not guarantee realized FX carry trade profitability.
          </p>
        </div>
      </div>
    </div>
  );
}
