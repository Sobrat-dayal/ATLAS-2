"use client";

import React from "react";
import { MacroCoverageSummaryDTO } from "@/lib/economics/comparisons";
import { CheckCircle2, Database, Globe2, Info, Layers, Scale, ShieldCheck } from "lucide-react";

interface ComparisonCoveragePanelProps {
  coverageData: MacroCoverageSummaryDTO | null;
  isLoading: boolean;
}

export function ComparisonCoveragePanel({
  coverageData,
  isLoading,
}: ComparisonCoveragePanelProps) {
  if (isLoading && !coverageData) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2">
        <div className="w-6 h-6 border-2 border-atlas-accent border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-mono">Loading Macro Coverage Metadata...</span>
      </div>
    );
  }

  if (!coverageData) {
    return null;
  }

  return (
    <div className="flex flex-col flex-1 h-full min-h-0 bg-atlas-background overflow-y-auto p-4 gap-4 text-xs font-mono">
      {/* Header Banner */}
      <div className="p-3.5 rounded bg-atlas-surface/60 border border-atlas-border-subtle flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded bg-cyan-500/15 text-cyan-400">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-bold text-atlas-text-primary text-sm tracking-tight">
              Macroeconomic Benchmarking Coverage & Sources
            </h2>
            <p className="text-[11px] text-atlas-text-muted">
              Source-qualified sovereign statistical data and harmonization registry
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-atlas-surface border border-atlas-border-subtle text-atlas-accent font-bold">
            {coverageData.total_observations_count} Total Observations
          </span>
        </div>
      </div>

      {/* Coverage Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Geographies & Cohorts */}
        <div className="p-3.5 rounded bg-atlas-surface/30 border border-atlas-border-subtle flex flex-col gap-2">
          <div className="flex items-center gap-1.5 font-bold text-atlas-text-primary text-xs">
            <Globe2 className="w-3.5 h-3.5 text-atlas-accent" />
            <span>Sovereign Economies ({coverageData.supported_geographies.length})</span>
          </div>
          <div className="flex flex-wrap gap-1 pt-1">
            {coverageData.supported_geographies.map((geo) => (
              <span
                key={geo}
                className="px-1.5 py-0.5 rounded bg-atlas-surface border border-atlas-border-subtle text-atlas-text-primary text-[10px]"
              >
                {geo}
              </span>
            ))}
          </div>
          <div className="pt-2 border-t border-atlas-border-subtle/50 flex flex-col gap-1">
            <span className="text-[10px] text-atlas-text-muted uppercase">Canonical Cohorts:</span>
            <div className="flex flex-wrap gap-1">
              {coverageData.cohorts.map((cohort) => (
                <span
                  key={cohort}
                  className="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20 text-[10px]"
                >
                  {cohort}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Indicators Covered */}
        <div className="p-3.5 rounded bg-atlas-surface/30 border border-atlas-border-subtle flex flex-col gap-2">
          <div className="flex items-center gap-1.5 font-bold text-atlas-text-primary text-xs">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>Comparable Metrics ({coverageData.supported_metrics.length})</span>
          </div>
          <div className="flex flex-col gap-1 max-h-48 overflow-y-auto pr-1">
            {coverageData.supported_metrics.map((m) => (
              <div key={m} className="flex items-center gap-1 text-[11px] text-atlas-text-primary">
                <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                <span className="truncate">{m}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Official Statistical Agencies */}
        <div className="p-3.5 rounded bg-atlas-surface/30 border border-atlas-border-subtle flex flex-col gap-2">
          <div className="flex items-center gap-1.5 font-bold text-atlas-text-primary text-xs">
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span>Authoritative Data Sources ({coverageData.harmonized_sources.length})</span>
          </div>
          <div className="flex flex-col gap-1 max-h-48 overflow-y-auto pr-1">
            {coverageData.harmonized_sources.map((s) => (
              <div key={s} className="flex items-center gap-1 text-[11px] text-atlas-text-primary">
                <CheckCircle2 className="w-3 h-3 text-cyan-400 shrink-0" />
                <span className="truncate">{s}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Core Methodological Principles & Prohibitions */}
      <div className="p-4 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-2.5">
        <div className="flex items-center gap-2 font-bold text-atlas-text-primary text-xs">
          <Scale className="w-4 h-4 text-atlas-accent" />
          <span>Institutional Methodology & Safeguards</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] text-atlas-text-muted leading-relaxed">
          {coverageData.methodology_qualifications.map((qual, idx) => (
            <div key={idx} className="flex items-start gap-1.5 p-2 rounded bg-atlas-surface/40 border border-atlas-border-subtle/50">
              <span className="w-1.5 h-1.5 rounded-full bg-atlas-accent shrink-0 mt-1.5" />
              <span>{qual}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
