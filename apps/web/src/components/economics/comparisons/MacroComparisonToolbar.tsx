"use client";

import React from "react";
import {
  Table,
  BarChart3,
  Activity,
  LineChart,
  GitCompare,
  Grid,
  ShieldCheck,
  RefreshCw,
  Globe2,
  Filter,
} from "lucide-react";
import {
  MacroComparisonView,
  GeographyOption,
} from "@/hooks/economics/useMacroComparisons";
import {
  ComparableIndicatorDTO,
  ComparisonMetricKind,
  GeographicCohortDTO,
  PeriodAlignmentPolicy,
  WeightingPolicy,
} from "@/lib/economics/comparisons";

interface MacroComparisonToolbarProps {
  activeView: MacroComparisonView;
  setActiveView: (view: MacroComparisonView) => void;
  indicators: ComparableIndicatorDTO[];
  geographies: GeographyOption[];
  cohorts: GeographicCohortDTO[];
  selectedGeographyIds: string[];
  selectedCohortId: string | null;
  onSelectCohort: (cohortId: string | null) => void;
  onToggleCountry: (geoId: string) => void;
  onSelectAllCountries: () => void;
  selectedMetricKind: ComparisonMetricKind;
  onSelectMetricKind: (metric: ComparisonMetricKind) => void;
  periodPolicy: PeriodAlignmentPolicy;
  onChangePeriodPolicy: (policy: PeriodAlignmentPolicy) => void;
  weightingPolicy: WeightingPolicy;
  onChangeWeightingPolicy: (policy: WeightingPolicy) => void;
  basePeriod: string | null;
  onChangeBasePeriod: (base: string | null) => void;
  isLoading: boolean;
  onRefresh: () => void;
}

export function MacroComparisonToolbar({
  activeView,
  setActiveView,
  indicators,
  geographies,
  cohorts,
  selectedGeographyIds,
  selectedCohortId,
  onSelectCohort,
  onToggleCountry,
  onSelectAllCountries,
  selectedMetricKind,
  onSelectMetricKind,
  periodPolicy,
  onChangePeriodPolicy,
  weightingPolicy,
  onChangeWeightingPolicy,
  basePeriod,
  onChangeBasePeriod,
  isLoading,
  onRefresh,
}: MacroComparisonToolbarProps) {
  const views: Array<{ id: MacroComparisonView; label: string; icon: React.ReactNode }> = [
    { id: "matrix", label: "Comparison Matrix", icon: <Table className="w-3.5 h-3.5 text-blue-400" /> },
    { id: "rankings", label: "Sovereign Rankings", icon: <BarChart3 className="w-3.5 h-3.5 text-indigo-400" /> },
    { id: "distributions", label: "Distributions", icon: <Activity className="w-3.5 h-3.5 text-emerald-400" /> },
    { id: "trends", label: "Historical Trends", icon: <LineChart className="w-3.5 h-3.5 text-purple-400" /> },
    { id: "divergence", label: "Convergence & Divergence", icon: <GitCompare className="w-3.5 h-3.5 text-amber-400" /> },
    { id: "correlations", label: "Correlations", icon: <Grid className="w-3.5 h-3.5 text-rose-400" /> },
    { id: "coverage", label: "Coverage & Sources", icon: <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" /> },
  ];

  return (
    <div className="flex flex-col gap-2.5 p-3 bg-atlas-surface/60 border-b border-atlas-border-subtle">
      {/* Top Row: Subview Tabs & Refresh */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
          {views.map((v) => (
            <button
              key={v.id}
              onClick={() => setActiveView(v.id)}
              className={`px-2.5 py-1.5 rounded text-xs font-medium transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                activeView === v.id
                  ? "bg-atlas-surface text-atlas-text-primary border border-atlas-border-subtle shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface/40"
              }`}
            >
              {v.icon}
              <span>{v.label}</span>
            </button>
          ))}
        </div>

        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="px-2.5 py-1.5 rounded bg-atlas-surface border border-atlas-border-subtle text-xs text-atlas-text-muted hover:text-atlas-text-primary transition-colors flex items-center gap-1.5 self-end sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-atlas-accent" : ""}`} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>

      {/* Middle Row: Cohort Presets & Country Selector Chips */}
      <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-atlas-border-subtle/50 text-xs">
        <div className="flex items-center gap-1.5 text-atlas-text-muted">
          <Globe2 className="w-3.5 h-3.5 text-atlas-accent" />
          <span className="font-semibold text-atlas-text-primary uppercase tracking-wider text-[10px]">
            Cohorts:
          </span>
        </div>

        <button
          onClick={onSelectAllCountries}
          className={`px-2 py-0.5 rounded text-[11px] font-mono border transition-colors ${
            !selectedCohortId && selectedGeographyIds.length === geographies.length
              ? "bg-atlas-accent/20 border-atlas-accent/40 text-atlas-accent font-semibold"
              : "bg-atlas-surface/80 border-atlas-border-subtle text-atlas-text-muted hover:text-atlas-text-primary"
          }`}
        >
          ALL ({geographies.length})
        </button>

        {cohorts.map((c) => {
          const isActive = selectedCohortId === c.cohort_id;
          return (
            <button
              key={c.cohort_id}
              onClick={() => onSelectCohort(isActive ? null : c.cohort_id)}
              className={`px-2 py-0.5 rounded text-[11px] font-mono border transition-colors ${
                isActive
                  ? "bg-atlas-accent/20 border-atlas-accent/40 text-atlas-accent font-semibold"
                  : "bg-atlas-surface/80 border-atlas-border-subtle text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
              title={c.description}
            >
              {c.name}
            </button>
          );
        })}

        <div className="h-4 w-px bg-atlas-border-subtle mx-1" />

        {/* Country Multi-Select Chips */}
        <div className="flex flex-wrap items-center gap-1">
          {geographies.map((geo) => {
            const isSelected = selectedGeographyIds.includes(geo.geography_id);
            return (
              <button
                key={geo.geography_id}
                onClick={() => onToggleCountry(geo.geography_id)}
                className={`px-1.5 py-0.5 rounded text-[11px] font-mono border transition-colors flex items-center gap-1 ${
                  isSelected
                    ? "bg-blue-500/15 border-blue-500/30 text-blue-300 font-medium"
                    : "bg-atlas-surface/30 border-atlas-border-subtle/50 text-atlas-text-muted/60 hover:text-atlas-text-muted"
                }`}
                title={geo.name}
              >
                <span>{geo.iso_code}</span>
                {geo.is_economic_area && (
                  <span className="text-[9px] uppercase px-0.5 rounded bg-amber-500/20 text-amber-300">
                    AREA
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Bottom Row: Context Controls (Active Metric, Alignment Policy, Base Period, Weighting) */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-atlas-border-subtle/50 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          {/* Active Metric Dropdown (Visible on non-matrix views) */}
          {activeView !== "matrix" && (
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] uppercase font-mono text-atlas-text-muted">Metric:</span>
              <select
                value={selectedMetricKind}
                onChange={(e) => onSelectMetricKind(e.target.value as ComparisonMetricKind)}
                className="bg-atlas-surface border border-atlas-border-subtle rounded px-2 py-1 text-xs text-atlas-text-primary focus:outline-hidden focus:border-atlas-accent"
              >
                {indicators.map((ind) => (
                  <option key={ind.metric_kind} value={ind.metric_kind}>
                    [{ind.category}] {ind.name} ({ind.default_unit})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Period Policy Selector */}
          {activeView === "matrix" && (
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] uppercase font-mono text-atlas-text-muted">Alignment:</span>
              <select
                value={periodPolicy}
                onChange={(e) => onChangePeriodPolicy(e.target.value as PeriodAlignmentPolicy)}
                className="bg-atlas-surface border border-atlas-border-subtle rounded px-2 py-1 text-xs text-atlas-text-primary focus:outline-hidden focus:border-atlas-accent"
              >
                <option value="latest_per_country">Latest Available per Country</option>
                <option value="latest_common_period">Latest Common Period (Synchronized)</option>
              </select>
            </div>
          )}

          {/* Historical Trends: Base Period Index Toggle */}
          {activeView === "trends" && (
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] uppercase font-mono text-atlas-text-muted">Index Rebase:</span>
              <button
                onClick={() => onChangeBasePeriod(basePeriod ? null : "2021")}
                className={`px-2 py-1 rounded text-xs border transition-colors ${
                  basePeriod
                    ? "bg-purple-500/20 border-purple-500/40 text-purple-300 font-medium"
                    : "bg-atlas-surface border-atlas-border-subtle text-atlas-text-muted hover:text-atlas-text-primary"
                }`}
              >
                {basePeriod ? `Indexed (Base = ${basePeriod} = 100)` : "Raw Series (Off)"}
              </button>
            </div>
          )}

          {/* Distributions: Weighting Policy */}
          {activeView === "distributions" && (
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] uppercase font-mono text-atlas-text-muted">Weighting:</span>
              <select
                value={weightingPolicy}
                onChange={(e) => onChangeWeightingPolicy(e.target.value as WeightingPolicy)}
                className="bg-atlas-surface border border-atlas-border-subtle rounded px-2 py-1 text-xs text-atlas-text-primary focus:outline-hidden focus:border-atlas-accent"
              >
                <option value="equal_weight">Equal Country Weights (Unweighted)</option>
                <option value="population_weighted">Population-Weighted (Demographic)</option>
                <option value="gdp_weighted">GDP-Weighted (Economic Size)</option>
              </select>
            </div>
          )}
        </div>

        {/* Selected Economies Count Badge */}
        <div className="flex items-center gap-2 text-[11px] font-mono text-atlas-text-muted ml-auto">
          <span>Selected:</span>
          <span className="px-1.5 py-0.5 rounded bg-atlas-surface border border-atlas-border-subtle text-atlas-text-primary font-bold">
            {selectedGeographyIds.length} of {geographies.length}
          </span>
        </div>
      </div>
    </div>
  );
}
