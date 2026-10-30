"use client";

import React from "react";
import { Badge } from "@/design-system";
import { getCompletenessBadge } from "@/lib/portfolios/performance/formatting";
import { PerformanceDataQualityDTO } from "@/lib/portfolios/performance/types";
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Database,
  FileCheck2,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

interface PerformanceDataQualityPanelProps {
  dataQuality: PerformanceDataQualityDTO | null | undefined;
}

export function PerformanceDataQualityPanel({
  dataQuality,
}: PerformanceDataQualityPanelProps) {
  if (!dataQuality) {
    return (
      <div className="rounded-sm border border-atlas-border-default/60 bg-atlas-surface-1 p-4 text-xs text-atlas-text-tertiary">
        No data quality audit available.
      </div>
    );
  }

  const badge = getCompletenessBadge(dataQuality.completeness);

  return (
    <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-4 shadow-xs space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default/40 pb-3">
        <div>
          <h4 className="text-xs font-semibold text-atlas-text-primary">
            Data Quality & Valuation Completeness Audit
          </h4>
          <p className="text-[11px] text-atlas-text-secondary">
            System diagnostics on market marks, FX currency rates, and subperiod cash flow integrity.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={badge.variant}>
            {badge.label}
          </Badge>
        </div>
      </div>

      {/* Description Banner */}
      <div className="rounded-sm border border-atlas-border-default/50 bg-atlas-surface-2/40 p-3 text-xs text-atlas-text-secondary flex items-start gap-2.5">
        <ShieldCheck className="h-4 w-4 shrink-0 text-atlas-accent mt-0.5" />
        <div>
          <div className="font-semibold text-atlas-text-primary">{badge.label}</div>
          <div className="text-[11px] text-atlas-text-tertiary mt-0.5">{badge.description}</div>
        </div>
      </div>

      {/* Audit Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 font-mono text-xs">
        <div className="rounded-sm border border-atlas-border-default/60 bg-atlas-surface-2/30 p-2.5">
          <div className="text-[11px] text-atlas-text-tertiary">Missing Prices</div>
          <div
            className={`mt-1 text-base font-bold ${
              dataQuality.missing_market_prices > 0 ? "text-rose-400" : "text-emerald-400"
            }`}
          >
            {dataQuality.missing_market_prices}
          </div>
          <div className="text-[10px] text-atlas-text-secondary mt-0.5">Holding marks</div>
        </div>

        <div className="rounded-sm border border-atlas-border-default/60 bg-atlas-surface-2/30 p-2.5">
          <div className="text-[11px] text-atlas-text-tertiary">Missing FX Rates</div>
          <div
            className={`mt-1 text-base font-bold ${
              dataQuality.missing_fx_rates > 0 ? "text-rose-400" : "text-emerald-400"
            }`}
          >
            {dataQuality.missing_fx_rates}
          </div>
          <div className="text-[10px] text-atlas-text-secondary mt-0.5">Conversion pairs</div>
        </div>

        <div className="rounded-sm border border-atlas-border-default/60 bg-atlas-surface-2/30 p-2.5">
          <div className="text-[11px] text-atlas-text-tertiary">Stale Marks</div>
          <div
            className={`mt-1 text-base font-bold ${
              dataQuality.stale_market_prices > 0 ? "text-amber-400" : "text-emerald-400"
            }`}
          >
            {dataQuality.stale_market_prices}
          </div>
          <div className="text-[10px] text-atlas-text-secondary mt-0.5">Previous-close used</div>
        </div>

        <div className="rounded-sm border border-atlas-border-default/60 bg-atlas-surface-2/30 p-2.5">
          <div className="text-[11px] text-atlas-text-tertiary">Missing Valuations</div>
          <div
            className={`mt-1 text-base font-bold ${
              dataQuality.missing_valuations > 0 ? "text-rose-400" : "text-emerald-400"
            }`}
          >
            {dataQuality.missing_valuations}
          </div>
          <div className="text-[10px] text-atlas-text-secondary mt-0.5">Boundary marks</div>
        </div>
      </div>

      {/* Warnings List */}
      {dataQuality.warnings && dataQuality.warnings.length > 0 && (
        <div className="space-y-2">
          <h5 className="text-[11px] font-semibold text-atlas-text-primary flex items-center gap-1.5">
            <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
            Calculation Diagnostics & Footnotes ({dataQuality.warnings.length})
          </h5>
          <div className="space-y-1.5 rounded-sm border border-amber-500/30 bg-amber-500/5 p-3">
            {dataQuality.warnings.map((w, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-amber-300">
                <span className="font-mono text-amber-500">&bull;</span>
                <span>{w}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Manifest Overview */}
      {dataQuality.source_manifest && Object.keys(dataQuality.source_manifest).length > 0 && (
        <div className="space-y-2">
          <h5 className="text-[11px] font-semibold text-atlas-text-primary flex items-center gap-1.5">
            <Database className="h-3.5 w-3.5 text-atlas-accent" />
            Input Source Manifest
          </h5>
          <pre className="max-h-36 overflow-x-auto rounded-sm border border-atlas-border-default/50 bg-atlas-surface-2/40 p-3 font-mono text-[11px] text-atlas-text-secondary">
            {JSON.stringify(dataQuality.source_manifest, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
