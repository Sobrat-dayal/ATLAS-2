"use client";

import React from "react";
import {
  Users,
  Briefcase,
  TrendingUp,
  Award,
  GraduationCap,
  Calendar,
  Info,
  ShieldCheck,
} from "lucide-react";
import { CountryLaborSummaryDTO } from "@/lib/economics/countries";

interface CountryLaborPanelProps {
  labor: CountryLaborSummaryDTO | null;
}

export function CountryLaborPanel({ labor }: CountryLaborPanelProps) {
  if (!labor) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded">
        No official labor market or employment survey data available for this country.
      </div>
    );
  }

  const formatPct = (val?: number | null) => {
    if (val === undefined || val === null) return "—";
    const sign = val > 0 ? "+" : "";
    return `${sign}${val.toFixed(1)}%`;
  };

  return (
    <div className="space-y-4">
      {/* Labor Market Banner */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                Labor Market Intelligence & Employment Surveys
              </h3>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-amber-400 border border-atlas-border-subtle">
                {labor.reference_period}
              </span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-atlas-text-secondary border border-atlas-border-subtle">
                {labor.age_scope}
              </span>
            </div>
            <p className="text-xs text-atlas-text-muted mt-1">
              {labor.survey_methodology} — Sovereign household labor force surveys and payroll benchmarks.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-atlas-background border border-atlas-border-subtle text-emerald-400 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>ILO Survey Standard</span>
            </span>
          </div>
        </div>

        {/* Primary Labor Statistics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 pt-4 border-t border-atlas-border-subtle">
          {/* Card 1: Unemployment Rate */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Unemployment Rate</span>
              <span className="font-mono text-[10px]">% Labor Force</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {labor.unemployment_rate !== null && labor.unemployment_rate !== undefined
                ? `${labor.unemployment_rate.toFixed(1)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Active jobseekers without employment
            </div>
          </div>

          {/* Card 2: Labor Force Participation */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Labor Force Participation</span>
              <span className="font-mono text-[10px]">% Working Age</span>
            </div>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
              {labor.labor_force_participation_rate !== null && labor.labor_force_participation_rate !== undefined
                ? `${labor.labor_force_participation_rate.toFixed(1)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Employed + actively seeking work
            </div>
          </div>

          {/* Card 3: Employment to Population Ratio */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Employment / Population</span>
              <span className="font-mono text-[10px]">Ratio</span>
            </div>
            <div className="text-xl font-bold font-mono text-blue-400 mt-1">
              {labor.employment_to_population_ratio !== null && labor.employment_to_population_ratio !== undefined
                ? `${labor.employment_to_population_ratio.toFixed(1)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Direct civilian employment share
            </div>
          </div>

          {/* Card 4: Total Employment Level */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Employed Persons</span>
              <span className="font-mono text-[10px]">Headcount</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {labor.employment_level_thousands !== null && labor.employment_level_thousands !== undefined
                ? `${(labor.employment_level_thousands / 1000).toFixed(1)}M`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              {labor.employment_level_thousands ? `${labor.employment_level_thousands.toLocaleString()} thousand` : "—"}
            </div>
          </div>
        </div>
      </div>

      {/* Wage Growth & Youth Unemployment Sub-Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Wages */}
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
              Wage Dynamics & Income Growth
            </h4>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div className="p-2.5 rounded bg-atlas-background/50 border border-atlas-border-subtle flex items-center justify-between">
              <span className="text-atlas-text-muted">Nominal Wage Growth YoY:</span>
              <span className="font-bold text-atlas-text-primary">
                {formatPct(labor.nominal_wage_growth_yoy)}
              </span>
            </div>
            <div className="p-2.5 rounded bg-atlas-background/50 border border-atlas-border-subtle flex items-center justify-between">
              <span className="text-atlas-text-muted">Real (Inflation-Adjusted) Wage Growth:</span>
              <span className={`font-bold ${(labor.real_wage_growth_yoy || 0) < 0 ? "text-rose-400" : "text-emerald-400"}`}>
                {formatPct(labor.real_wage_growth_yoy)}
              </span>
            </div>
          </div>
          <p className="text-[11px] text-atlas-text-muted mt-3">
            Real wages are deflated using official headline CPI to measure true purchasing power gains.
          </p>
        </div>

        {/* Youth & Demographics Scope */}
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <GraduationCap className="w-4 h-4 text-purple-400" />
            <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
              Demographic Labor Cohorts & Youth Unemployment
            </h4>
          </div>
          <div className="space-y-3 font-mono text-xs">
            <div className="p-2.5 rounded bg-atlas-background/50 border border-atlas-border-subtle flex items-center justify-between">
              <span className="text-atlas-text-muted">Youth Unemployment Rate (15–24 / 16–24):</span>
              <span className="font-bold text-amber-400">
                {labor.youth_unemployment_rate !== null && labor.youth_unemployment_rate !== undefined
                  ? `${labor.youth_unemployment_rate.toFixed(1)}%`
                  : "—"}
              </span>
            </div>
            <div className="p-2.5 rounded bg-atlas-background/50 border border-atlas-border-subtle flex items-center justify-between">
              <span className="text-atlas-text-muted">Survey Population Coverage:</span>
              <span className="font-bold text-atlas-text-secondary">
                {labor.age_scope}
              </span>
            </div>
          </div>
          <p className="text-[11px] text-atlas-text-muted mt-3">
            Youth unemployment captures friction in school-to-work transitions under ILO definitions.
          </p>
        </div>
      </div>

      {labor.notes && (
        <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded-lg text-[11px] text-atlas-text-muted flex items-start gap-2">
          <Info className="w-3.5 h-3.5 shrink-0 text-atlas-accent mt-0.5" />
          <span>{labor.notes}</span>
        </div>
      )}
    </div>
  );
}
