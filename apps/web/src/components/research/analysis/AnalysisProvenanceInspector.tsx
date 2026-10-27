"use client";

import React from "react";
import { ResearchAnalysisResult } from "@/lib/research/types";
import { Badge } from "@/design-system";

interface AnalysisProvenanceInspectorProps {
  result?: ResearchAnalysisResult | null;
  provenanceData?: Record<string, unknown> | null;
}

export function AnalysisProvenanceInspector({
  result,
  provenanceData,
}: AnalysisProvenanceInspectorProps) {
  if (!result) {
    return (
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-8 text-center text-xs text-atlas-text-muted">
        No active execution run selected. Run an analysis to inspect its cryptographic provenance and source manifest.
      </div>
    );
  }

  const manifest = result.source_data_manifest || [];
  const formulas = (provenanceData?.formula_definitions || {}) as Record<
    string,
    { label?: string; formula: string; description?: string }
  >;

  return (
    <div className="space-y-4">
      {/* Run Provenance Meta */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <div className="mb-3 border-b border-atlas-border-subtle pb-3">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Cryptographic Analytical Provenance & Lineage
            </h3>
            <Badge variant="outline" className="font-mono text-[10px]">
              AUDIT READY
            </Badge>
          </div>
          <p className="text-xs text-atlas-text-muted">
            Strict reproducibility audit trail linking computed values back to exact filing accession watermarks.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
          <div className="rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 p-2">
            <div className="text-[10px] text-atlas-text-muted uppercase">Execution Run ID</div>
            <div className="font-semibold text-atlas-text-primary truncate">{result.run_id}</div>
          </div>

          <div className="rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 p-2">
            <div className="text-[10px] text-atlas-text-muted uppercase">Reproducibility Hash</div>
            <div className="font-semibold text-atlas-accent truncate" title={result.reproducibility_hash}>
              {result.reproducibility_hash}
            </div>
          </div>

          <div className="rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 p-2">
            <div className="text-[10px] text-atlas-text-muted uppercase">Execution Timestamp</div>
            <div className="font-semibold text-atlas-text-primary">
              {new Date(result.executed_at).toLocaleString()}
            </div>
          </div>

          <div className="rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 p-2">
            <div className="text-[10px] text-atlas-text-muted uppercase">Status</div>
            <div className="font-semibold text-emerald-500">{result.execution_status}</div>
          </div>
        </div>

        {result.methodology_description && (
          <div className="mt-3 rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 p-2.5 text-xs">
            <span className="font-semibold text-atlas-text-secondary">Methodology Specification: </span>
            <span className="text-atlas-text-muted">{result.methodology_description}</span>
          </div>
        )}
      </div>

      {/* Source Data Manifest */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <div className="mb-3 border-b border-atlas-border-subtle pb-2">
          <h4 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
            Source Observations Watermark Manifest ({manifest.length} Records)
          </h4>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="border-b border-atlas-border-default bg-atlas-surface-1 text-[11px] text-atlas-text-secondary uppercase">
              <tr>
                <th className="px-3 py-2">Period</th>
                <th className="px-3 py-2">Entity ID</th>
                <th className="px-3 py-2">Filing Accession</th>
                <th className="px-3 py-2">Document Type</th>
                <th className="px-3 py-2">Observation Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle text-atlas-text-primary">
              {manifest.map((m, i) => (
                <tr key={i} className="hover:bg-atlas-surface-1/50">
                  <td className="px-3 py-2 font-semibold text-atlas-accent">{String(m.period || m.period_label || "—")}</td>
                  <td className="px-3 py-2">{String(m.entity_id || result.primary_subject_id)}</td>
                  <td className="px-3 py-2 text-atlas-text-secondary truncate max-w-xs" title={String(m.accession || "")}>
                    {String(m.accession || "CANONICAL_RATIO_REGISTRY")}
                  </td>
                  <td className="px-3 py-2 text-atlas-text-muted">{String(m.document_type || "SEC_FORM_10K")}</td>
                  <td className="px-3 py-2 text-atlas-text-muted">{String(m.observed_date || "—")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Formula Contracts */}
      {Object.keys(formulas).length > 0 && (
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
          <div className="mb-3 border-b border-atlas-border-subtle pb-2">
            <h4 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
              Versioned Calculation Formulas
            </h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono">
            {Object.entries(formulas).map(([key, f]) => (
              <div key={key} className="rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 p-2.5">
                <div className="font-semibold text-atlas-accent">{f.label || key}</div>
                <div className="text-[11px] text-atlas-text-primary mt-1 font-mono bg-atlas-surface-2 p-1 rounded-xs">
                  {f.formula}
                </div>
                <div className="text-[10px] text-atlas-text-muted mt-1">{f.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
