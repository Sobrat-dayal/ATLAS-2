"use client";

import React from "react";
import {
  formatDate,
  formatSignedPercent,
  formatVolPercent,
  getCalculationStatusBadge,
  getModelTypeLabel,
} from "@/lib/risk/formatting";
import { RiskCalculationRunDTO } from "@/lib/risk/types";
import { CheckCircle2, History } from "lucide-react";

interface RiskRunHistoryProps {
  runsList: RiskCalculationRunDTO[];
  selectedRunId?: string;
  onSelectRun?: (run: RiskCalculationRunDTO) => void;
}

export function RiskRunHistory({
  runsList,
  selectedRunId,
  onSelectRun,
}: RiskRunHistoryProps) {
  if (!runsList || runsList.length === 0) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-6 text-center text-xs text-atlas-text-muted">
        No previous risk calculation runs recorded. Run a model to generate historical audit records.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded border border-atlas-border-default/60 bg-atlas-surface-1">
      <div className="border-b border-atlas-border-default/40 px-4 py-3">
        <div className="flex items-center gap-2">
          <History className="h-4 w-4 text-atlas-text-secondary" />
          <h4 className="text-sm font-semibold text-atlas-text-primary">
            Risk Calculation Audit Trail & Reproducible Snapshots
          </h4>
        </div>
        <p className="mt-0.5 text-xs text-atlas-text-muted">
          Persisted risk snapshots with immutable inputs, methodology versions, and audit hashes.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2/60 text-[11px] font-medium text-atlas-text-secondary">
              <th className="py-2.5 px-4 font-sans">Run ID</th>
              <th className="py-2.5 px-3">Calculation As-Of</th>
              <th className="py-2.5 px-3 font-sans">Model Engine</th>
              <th className="py-2.5 px-3 text-right">Hist Vol</th>
              <th className="py-2.5 px-3 text-right">Model Vol</th>
              <th className="py-2.5 px-3 text-right">Max Drawdown</th>
              <th className="py-2.5 px-3 font-sans text-center">Status</th>
              <th className="py-2.5 px-4 font-sans text-right">Input Hash</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/30">
            {runsList.map((r) => {
              const badge = getCalculationStatusBadge(r.status);
              const isSelected = selectedRunId === r.risk_run_id;
              return (
                <tr
                  key={r.risk_run_id}
                  onClick={() => onSelectRun?.(r)}
                  className={`cursor-pointer transition hover:bg-atlas-surface-2/50 ${
                    isSelected ? "bg-atlas-surface-2" : ""
                  }`}
                >
                  <td className="py-2.5 px-4 font-bold text-atlas-accent-blue">
                    {r.risk_run_id.substring(0, 16)}...
                  </td>
                  <td className="py-2.5 px-3 text-atlas-text-primary">
                    {formatDate(r.calculation_as_of)}
                  </td>
                  <td className="py-2.5 px-3 font-sans text-atlas-text-secondary">
                    {getModelTypeLabel(r.model_type)} (v{r.model_version})
                  </td>
                  <td className="py-2.5 px-3 text-right text-atlas-text-primary">
                    {formatVolPercent(r.historical_volatility, 2)}
                  </td>
                  <td className="py-2.5 px-3 text-right text-blue-400 font-semibold">
                    {formatVolPercent(r.model_estimated_volatility, 2)}
                  </td>
                  <td className="py-2.5 px-3 text-right text-rose-400 font-semibold">
                    {formatSignedPercent(r.max_drawdown, 2)}
                  </td>
                  <td className="py-2.5 px-3 text-center font-sans">
                    <span
                      className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 text-[10px] font-semibold ${badge.bgClass} ${badge.textClass} ${badge.borderClass}`}
                    >
                      <CheckCircle2 className="h-2.5 w-2.5" />
                      {badge.label}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-right text-atlas-text-muted truncate max-w-[120px]">
                    {r.input_manifest?.input_hash ? r.input_manifest.input_hash.substring(0, 10) : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

