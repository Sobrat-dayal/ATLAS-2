"use client";

import React from "react";
import {
  Users,
  Building,
  Baby,
  HeartPulse,
  Scale,
  Calendar,
  Info,
} from "lucide-react";
import { CountryDemographicsSummaryDTO } from "@/lib/economics/countries";

interface CountryDemographicsPanelProps {
  demographics: CountryDemographicsSummaryDTO | null;
}

export function CountryDemographicsPanel({ demographics }: CountryDemographicsPanelProps) {
  if (!demographics) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded">
        No demographic or structural population data available for this country.
      </div>
    );
  }

  const formatPct = (val?: number | null) => {
    if (val === undefined || val === null) return "—";
    const sign = val > 0 ? "+" : "";
    return `${sign}${val.toFixed(2)}%`;
  };

  return (
    <div className="space-y-4">
      {/* Demographics Header Banner */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                Demographics, Age Cohorts & Population Structure
              </h3>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-purple-400 border border-atlas-border-subtle">
                {demographics.reference_period}
              </span>
            </div>
            <p className="text-xs text-atlas-text-muted mt-1">
              Official national census benchmarks, working-age cohort proportions, dependency ratios, and urbanization.
            </p>
          </div>
        </div>

        {/* Primary Demographic Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 pt-4 border-t border-atlas-border-subtle">
          {/* Card 1: Total Population */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-purple-400" />
                Total Population
              </span>
              <span className="font-mono text-[10px]">Headcount</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {demographics.total_population_millions
                ? `${demographics.total_population_millions.toFixed(1)}M`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Growth: {formatPct(demographics.population_growth_rate_yoy)} YoY
            </div>
          </div>

          {/* Card 2: Working-Age Population */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-blue-400" />
                Working Age (15–64)
              </span>
              <span className="font-mono text-[10px]">% Total</span>
            </div>
            <div className="text-xl font-bold font-mono text-blue-400 mt-1">
              {demographics.working_age_population_pct !== null && demographics.working_age_population_pct !== undefined
                ? `${demographics.working_age_population_pct.toFixed(1)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Core productive economic labor base
            </div>
          </div>

          {/* Card 3: Age Dependency Ratio */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Scale className="w-3.5 h-3.5 text-amber-400" />
                Age Dependency Ratio
              </span>
              <span className="font-mono text-[10px]">Ratio</span>
            </div>
            <div className="text-xl font-bold font-mono text-amber-400 mt-1">
              {demographics.age_dependency_ratio !== null && demographics.age_dependency_ratio !== undefined
                ? demographics.age_dependency_ratio.toFixed(1)
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Dependents per 100 working-age
            </div>
          </div>

          {/* Card 4: Urbanization Rate */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5 text-emerald-400" />
                Urbanization Rate
              </span>
              <span className="font-mono text-[10px]">% Total</span>
            </div>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
              {demographics.urbanization_rate_pct !== null && demographics.urbanization_rate_pct !== undefined
                ? `${demographics.urbanization_rate_pct.toFixed(1)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Share in urban agglomerations
            </div>
          </div>
        </div>
      </div>

      {/* Age Cohorts Distribution Table */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-atlas-border-subtle flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-purple-400" />
            <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
              Demographic Age Cohorts Breakdown
            </h4>
          </div>
          <span className="text-[11px] font-mono text-atlas-text-muted">
            Official Census / Statistical Bureau Registry
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-atlas-background/50 border-b border-atlas-border-subtle text-[11px] font-mono text-atlas-text-muted uppercase">
                <th className="py-2.5 px-4 font-semibold">Age Cohort</th>
                <th className="py-2.5 px-4 font-semibold text-center">Age Bracket</th>
                <th className="py-2.5 px-4 font-semibold text-right">Share of Population (%)</th>
                <th className="py-2.5 px-4 font-semibold text-right">Economic Demographic Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle font-mono">
              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary flex items-center gap-2">
                  <Baby className="w-3.5 h-3.5 text-blue-400" />
                  Youth Population
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    Ages 0–14
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-atlas-text-primary">
                  {demographics.youth_population_pct !== null && demographics.youth_population_pct !== undefined
                    ? `${demographics.youth_population_pct.toFixed(1)}%`
                    : "—"}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Future workforce generation & education demand
                </td>
              </tr>

              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary flex items-center gap-2">
                  <Users className="w-3.5 h-3.5 text-emerald-400" />
                  Working-Age Population
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    Ages 15–64
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-emerald-400">
                  {demographics.working_age_population_pct !== null && demographics.working_age_population_pct !== undefined
                    ? `${demographics.working_age_population_pct.toFixed(1)}%`
                    : "—"}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Prime productive age bracket driving GDP output
                </td>
              </tr>

              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary flex items-center gap-2">
                  <HeartPulse className="w-3.5 h-3.5 text-rose-400" />
                  Elderly Population
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    Ages 65+
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-amber-400">
                  {demographics.elderly_population_pct !== null && demographics.elderly_population_pct !== undefined
                    ? `${demographics.elderly_population_pct.toFixed(1)}%`
                    : "—"}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Pensions, healthcare & sovereign entitlement demand
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="p-3 bg-atlas-background/40 border-t border-atlas-border-subtle text-[11px] text-atlas-text-muted flex items-start gap-2">
          <Info className="w-3.5 h-3.5 shrink-0 text-atlas-accent mt-0.5" />
          <span>
            {demographics.notes ||
              "Demographic observations are benchmarked to annual national census estimates. Historical population revisions occur post-decennial census."}
          </span>
        </div>
      </div>
    </div>
  );
}
