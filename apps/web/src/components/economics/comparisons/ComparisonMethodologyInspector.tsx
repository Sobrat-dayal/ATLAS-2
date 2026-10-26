"use client";

import React from "react";
import { MatrixCellDTO } from "@/lib/economics/comparisons";
import { AlertCircle, CheckCircle2, FileText, Info, ShieldCheck, X } from "lucide-react";

interface ComparisonMethodologyInspectorProps {
  cell: MatrixCellDTO | null;
  onClose: () => void;
}

export function ComparisonMethodologyInspector({
  cell,
  onClose,
}: ComparisonMethodologyInspectorProps) {
  if (!cell) return null;

  const isQualified = cell.status === "comparable_with_qualification";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg shadow-2xl max-w-lg w-full overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="p-3.5 border-b border-atlas-border-subtle bg-atlas-surface/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-atlas-accent" />
            <span className="font-bold text-atlas-text-primary text-sm tracking-tight">
              Macro Observation Lineage & Methodology
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface/80 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-4 overflow-y-auto max-h-[80vh] flex flex-col gap-4 text-xs font-mono">
          {/* Headline Observation Card */}
          <div className="p-3 rounded bg-atlas-background border border-atlas-border-subtle flex items-center justify-between">
            <div>
              <span className="text-[10px] text-atlas-text-muted uppercase">Economy & Metric</span>
              <div className="text-sm font-bold text-atlas-text-primary">
                {cell.country_name} ({cell.iso_code}) — {cell.metric_kind}
              </div>
            </div>
            <div className="text-right">
              <span className="text-lg font-bold text-atlas-accent">{cell.formatted_value}</span>
              <div className="text-[10px] text-atlas-text-muted">{cell.reference_period}</div>
            </div>
          </div>

          {/* Lineage & Provenance Details */}
          <div className="grid grid-cols-2 gap-2.5">
            <div className="p-2.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-0.5">
              <span className="text-[10px] text-atlas-text-muted uppercase">Source Agency</span>
              <span className="font-semibold text-atlas-text-primary truncate">{cell.source_agency}</span>
            </div>
            <div className="p-2.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-0.5">
              <span className="text-[10px] text-atlas-text-muted uppercase">Source Series ID</span>
              <span className="font-semibold text-atlas-text-primary truncate">{cell.source_series_id || "OFFICIAL-CANONICAL"}</span>
            </div>
            <div className="p-2.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-0.5">
              <span className="text-[10px] text-atlas-text-muted uppercase">Unit & Scale</span>
              <span className="font-semibold text-atlas-text-primary">{cell.unit}</span>
            </div>
            <div className="p-2.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle flex flex-col gap-0.5">
              <span className="text-[10px] text-atlas-text-muted uppercase">Comparability Status</span>
              <div className="flex items-center gap-1 font-semibold text-atlas-text-primary">
                {isQualified ? (
                  <>
                    <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                    <span className="text-amber-300">Qualified</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-300">Directly Comparable</span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Methodological Caveats */}
          {cell.caveats.length > 0 && (
            <div className="p-3 rounded bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200/90 flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 font-semibold text-amber-300">
                <AlertCircle className="w-4 h-4 text-amber-400" />
                <span>Methodology Qualifications</span>
              </div>
              <ul className="list-disc list-inside space-y-1 text-[11px] text-amber-200/80">
                {cell.caveats.map((c, idx) => (
                  <li key={idx}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Institutional Compliance Notice */}
          <div className="p-2.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle text-[11px] text-atlas-text-muted flex items-start gap-2">
            <ShieldCheck className="w-4 h-4 text-atlas-accent shrink-0 mt-0.5" />
            <p>
              ATLAS preserves authoritative national accounting boundaries, currency denominations, and reference periods. Cross-country comparisons are verified against IMF, OECD, World Bank, and national statistical release standards.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-3 border-t border-atlas-border-subtle bg-atlas-surface/80 flex justify-end">
          <button
            onClick={onClose}
            className="px-3 py-1 rounded bg-atlas-surface border border-atlas-border-subtle text-xs text-atlas-text-primary hover:bg-atlas-surface/60 transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
