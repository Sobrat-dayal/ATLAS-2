"use client";

import React from "react";
import {
  CorrelationAnalysisResponseDTO,
  CorrelationMethod,
} from "@/lib/economics/comparisons";
import { AlertTriangle, Grid, Info, ShieldAlert } from "lucide-react";

interface MacroCorrelationMatrixProps {
  correlationData: CorrelationAnalysisResponseDTO | null;
  correlationMethod: CorrelationMethod;
  onChangeMethod: (method: CorrelationMethod) => void;
  isLoading: boolean;
}

export function MacroCorrelationMatrix({
  correlationData,
  correlationMethod,
  onChangeMethod,
  isLoading,
}: MacroCorrelationMatrixProps) {
  if (isLoading && !correlationData) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2">
        <div className="w-6 h-6 border-2 border-atlas-accent border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-mono">Aligning Paired Samples & Computing Correlations...</span>
      </div>
    );
  }

  if (!correlationData || correlationData.results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2 border border-dashed border-atlas-border-subtle rounded m-4">
        <Info className="w-8 h-8 text-atlas-text-muted/60" />
        <p className="text-sm font-medium text-atlas-text-primary">No Correlation Pairs Available</p>
        <p className="text-xs text-atlas-text-muted">
          Select at least two countries with aligned historical reporting periods.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 h-full min-h-0 bg-atlas-background overflow-y-auto p-4 gap-4">
      {/* Header & Method Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded bg-atlas-surface/60 border border-atlas-border-subtle text-xs">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded bg-rose-500/15 text-rose-400">
            <Grid className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-bold text-atlas-text-primary text-sm tracking-tight">
              Cross-Country Statistical Correlation
            </h2>
            <div className="flex items-center gap-2 text-atlas-text-muted text-[11px] font-mono">
              <span>Method: {correlationMethod.toUpperCase()}</span>
              <span>•</span>
              <span>Pairs Calculated: {correlationData.results.length}</span>
            </div>
          </div>
        </div>

        {/* Method Toggle */}
        <div className="flex items-center bg-atlas-background border border-atlas-border-subtle rounded p-0.5">
          <button
            onClick={() => onChangeMethod("pearson")}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              correlationMethod === "pearson"
                ? "bg-atlas-surface text-atlas-text-primary shadow-xs"
                : "text-atlas-text-muted hover:text-atlas-text-primary"
            }`}
          >
            Pearson (Linear)
          </button>
          <button
            onClick={() => onChangeMethod("spearman")}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              correlationMethod === "spearman"
                ? "bg-atlas-surface text-atlas-text-primary shadow-xs"
                : "text-atlas-text-muted hover:text-atlas-text-primary"
            }`}
          >
            Spearman (Rank)
          </button>
        </div>
      </div>

      {/* Correlation Pairs Grid / Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 font-mono">
        {correlationData.results.map((res, idx) => {
          const coeff = res.coefficient;
          const isPositive = coeff > 0;
          const strength = Math.abs(coeff);

          return (
            <div
              key={idx}
              className="p-3.5 rounded bg-atlas-surface/30 border border-atlas-border-subtle flex flex-col gap-2"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-atlas-text-primary">
                  {res.country_a_name} vs {res.country_b_name}
                </span>
                <span className="text-[10px] text-atlas-text-muted px-1.5 py-0.5 rounded bg-atlas-surface border border-atlas-border-subtle">
                  N = {res.sample_size}
                </span>
              </div>

              {/* Coefficient Banner */}
              <div className="flex items-baseline justify-between pt-1">
                <span className="text-2xl font-bold text-atlas-text-primary">
                  {isPositive ? "+" : ""}
                  {coeff.toFixed(3)}
                </span>
                <span
                  className={`text-[11px] font-semibold uppercase px-1.5 py-0.5 rounded ${
                    strength > 0.7
                      ? "bg-blue-500/20 text-blue-300"
                      : strength > 0.4
                      ? "bg-emerald-500/20 text-emerald-300"
                      : "bg-atlas-surface text-atlas-text-muted"
                  }`}
                >
                  {strength > 0.7 ? "Strong" : strength > 0.4 ? "Moderate" : "Weak / None"}
                </span>
              </div>

              {/* Warnings / Caveats */}
              {res.warnings.length > 0 && (
                <div className="pt-2 border-t border-atlas-border-subtle/50 flex flex-col gap-1 text-[10px] text-amber-300/80">
                  {res.warnings.map((w, wIdx) => (
                    <div key={wIdx} className="flex items-start gap-1">
                      <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />
                      <span>{w}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Mandatory Statistical Interpretation Warnings */}
      <div className="p-3 rounded bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200/90 flex items-start gap-2.5">
        <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="flex flex-col gap-1">
          <span className="font-semibold text-amber-300">Statistical Caveats & Limitations</span>
          <ul className="list-disc list-inside space-y-0.5 text-[11px] text-amber-200/80">
            <li>Statistical correlation does not establish macroeconomic causality.</li>
            <li>Trending macroeconomic levels are subject to nonstationarity and spurious correlation.</li>
            <li>Coefficients are calculated strictly on pairwise complete, period-aligned observations without interpolation.</li>
            <li>ATLAS does not derive trading signals or financial execution recommendations from correlation statistics.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
