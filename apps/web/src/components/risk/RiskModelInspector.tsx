"use client";

import React from "react";
import {
  AnnualizationPolicy,
  RiskMetricDefinitionDTO,
  RiskModelDefinitionDTO,
} from "@/lib/risk/types";
import { BookOpen, CheckCircle2, Code2, Info, ShieldAlert } from "lucide-react";

interface RiskModelInspectorProps {
  modelsCatalog: RiskModelDefinitionDTO[];
  metricsCatalog: RiskMetricDefinitionDTO[];
}

export function RiskModelInspector({
  modelsCatalog,
  metricsCatalog,
}: RiskModelInspectorProps) {
  return (
    <div className="space-y-6">
      {/* Models Section */}
      <div className="space-y-3">
        <div className="border-b border-atlas-border-default/40 pb-2">
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Institutional Risk Models & Methodologies
          </h3>
          <p className="text-xs text-atlas-text-muted">
            Approved production risk engines implementing mathematically rigorous financial risk algorithms.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {modelsCatalog.map((m) => (
            <div
              key={m.model_id}
              className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-atlas-text-primary">{m.display_name}</span>
                <span className="rounded bg-atlas-surface-2 px-2 py-0.5 font-mono text-[10px] text-atlas-accent-blue">
                  v{m.version}
                </span>
              </div>
              <p className="mt-2 text-xs text-atlas-text-secondary">{m.description}</p>

              <div className="mt-3">
                <div className="text-[11px] font-medium text-atlas-text-muted uppercase tracking-wider">
                  Allowed Metrics:
                </div>
                <div className="mt-1 flex flex-wrap gap-1.5">
                  {m.allowed_metrics.map((c) => (
                    <span
                      key={c}
                      className="rounded bg-atlas-surface-2 px-1.5 py-0.5 font-mono text-[10px] text-atlas-text-secondary"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              </div>

              {m.limitations.length > 0 && (
                <div className="mt-3 rounded bg-amber-500/5 border border-amber-500/20 p-2.5 text-[11px] text-amber-300">
                  <div className="font-semibold flex items-center gap-1">
                    <ShieldAlert className="h-3 w-3 text-amber-400" />
                    <span>Limitations & Assumptions:</span>
                  </div>
                  <ul className="mt-1 list-disc list-inside space-y-0.5 text-atlas-text-muted">
                    {m.limitations.map((lim, i) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Metrics Catalog Table */}
      <div className="space-y-3">
        <div className="border-b border-atlas-border-default/40 pb-2">
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Financial Risk Metric Taxonomy
          </h3>
          <p className="text-xs text-atlas-text-muted">
            Formal mathematical definitions, sampling frequencies, and annualization rules.
          </p>
        </div>

        <div className="overflow-hidden rounded border border-atlas-border-default/60 bg-atlas-surface-1">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2/60 text-[11px] font-medium text-atlas-text-secondary">
                  <th className="py-2.5 px-4 font-sans">Metric Code</th>
                  <th className="py-2.5 px-3 font-sans">Display Name</th>
                  <th className="py-2.5 px-3 font-sans">Category</th>
                  <th className="py-2.5 px-3 font-mono">Mathematical Formula</th>
                  <th className="py-2.5 px-3 font-sans">Annualization</th>
                  <th className="py-2.5 px-4 font-sans text-right">Units</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default/30 font-mono">
                {metricsCatalog.map((met) => (
                  <tr key={met.metric_code} className="transition hover:bg-atlas-surface-2/40">
                    <td className="py-2 px-4 font-semibold text-atlas-text-primary">
                      {met.metric_code}
                    </td>
                    <td className="py-2 px-3 font-sans text-atlas-text-primary">
                      {met.display_name}
                    </td>
                    <td className="py-2 px-3 font-sans text-atlas-text-secondary">
                      {met.category}
                    </td>
                    <td className="py-2 px-3 text-atlas-accent-gold text-[11px]">
                      {met.mathematical_formula}
                    </td>
                    <td className="py-2 px-3 font-sans text-atlas-text-muted">
                      {met.annualization_policy}
                    </td>
                    <td className="py-2 px-4 text-right font-sans text-atlas-text-secondary">
                      {met.units}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

