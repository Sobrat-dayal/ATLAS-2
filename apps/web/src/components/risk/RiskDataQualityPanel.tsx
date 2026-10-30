"use client";

import React from "react";
import { getDataCoverageBadge } from "@/lib/risk/formatting";
import { RiskDataCoverageDTO, RiskInputManifestDTO } from "@/lib/risk/types";
import {
  AlertTriangle,
  Calendar,
  CheckCircle2,
  Database,
  FileCheck,
  Hash,
  ShieldAlert,
} from "lucide-react";

interface RiskDataQualityPanelProps {
  dataQuality: RiskDataCoverageDTO | null;
  inputManifest?: RiskInputManifestDTO | null;
}

export function RiskDataQualityPanel({
  dataQuality,
  inputManifest,
}: RiskDataQualityPanelProps) {
  if (!dataQuality) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-6 text-center text-xs text-atlas-text-muted">
        No data quality telemetry recorded for the current calculation.
      </div>
    );
  }

  const q = dataQuality;
  const badge = getDataCoverageBadge(q.status);

  return (
    <div className="space-y-4">
      {/* Top Health Summary Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-10 w-10 items-center justify-center rounded border ${badge.bgClass} ${badge.textClass} ${badge.borderClass}`}
          >
            <Database className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-semibold text-atlas-text-primary">
                Market Data Quality & Coverage Status
              </h4>
              <span
                className={`rounded border px-2 py-0.5 text-xs font-semibold ${badge.bgClass} ${badge.textClass} ${badge.borderClass}`}
              >
                {badge.label}
              </span>
            </div>
            <p className="mt-0.5 text-xs text-atlas-text-muted">
              Audit of return series completeness, pricing freshness, and benchmark synchronization.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div>
            <span className="text-atlas-text-muted">Required: </span>
            <span className="font-semibold text-atlas-text-primary">{q.required_observations}</span>
          </div>
          <div>
            <span className="text-atlas-text-muted">Available: </span>
            <span className="font-semibold text-atlas-text-primary">{q.available_observations}</span>
          </div>
          <div>
            <span className="text-atlas-text-muted">Matched: </span>
            <span className="font-semibold text-emerald-400">{q.matched_observations}</span>
          </div>
          <div>
            <span className="text-atlas-text-muted">Ratio: </span>
            <span className="font-bold text-atlas-accent-gold">
              {(q.coverage_ratio * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Audit Sections */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {/* Missing Intervals Audit */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-2.5">
            <Calendar className="h-4 w-4 text-atlas-text-secondary" />
            <h5 className="text-xs font-semibold text-atlas-text-primary">
              Missing Observation Intervals
            </h5>
          </div>

          <div className="mt-3">
            {q.missing_intervals.length === 0 ? (
              <div className="flex items-center gap-2 text-xs text-emerald-400">
                <CheckCircle2 className="h-4 w-4" />
                <span>Zero missing date intervals. Contiguous time series verified.</span>
              </div>
            ) : (
              <ul className="space-y-1.5 font-mono text-xs text-rose-400">
                {q.missing_intervals.map((inv, idx) => (
                  <li key={idx} className="flex items-center gap-1.5">
                    <AlertTriangle className="h-3 w-3 shrink-0 text-rose-400" />
                    <span>{inv}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Stale & Unsupported Instruments */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-2.5">
            <ShieldAlert className="h-4 w-4 text-atlas-text-secondary" />
            <h5 className="text-xs font-semibold text-atlas-text-primary">
              Pricing Freshness & Exclusions
            </h5>
          </div>

          <div className="mt-3 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-atlas-text-secondary">Stale Price Observations:</span>
              <span className="font-mono text-atlas-text-primary">{q.stale_observations}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-atlas-text-secondary">Unsupported Instruments:</span>
              <span className="font-mono text-atlas-text-primary">
                {q.unsupported_instruments.length > 0
                  ? q.unsupported_instruments.join(", ")
                  : "None (All supported)"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Input Audit Manifest */}
      {inputManifest && (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-2.5">
            <FileCheck className="h-4 w-4 text-atlas-accent-blue" />
            <h5 className="text-xs font-semibold text-atlas-text-primary">
              Reproducible Calculation Manifest & Input Hash
            </h5>
          </div>

          <div className="mt-3 grid grid-cols-1 gap-2 text-xs md:grid-cols-2">
            <div className="flex items-center justify-between rounded bg-atlas-surface-2 p-2 font-mono">
              <span className="text-atlas-text-secondary">Input Hash:</span>
              <span className="text-atlas-accent-gold truncate max-w-[200px]">
                {inputManifest.input_hash}
              </span>
            </div>
            <div className="flex items-center justify-between rounded bg-atlas-surface-2 p-2">
              <span className="text-atlas-text-secondary">Performance Run Ref:</span>
              <span className="font-mono text-atlas-text-primary">
                {inputManifest.performance_run_id || "Direct Accounting"}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

