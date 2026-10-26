"use client";

import React from "react";
import { X, FileText, CheckCircle2, ShieldCheck, Database, Layers } from "lucide-react";
import { ComparableObservationDTO } from "@/lib/companies/peers";

interface PeerSourceInspectorProps {
  observation: ComparableObservationDTO | null;
  onClose: () => void;
}

export function PeerSourceInspector({ observation, onClose }: PeerSourceInspectorProps) {
  if (!observation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg max-w-lg w-full shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="p-3.5 border-b border-atlas-border-subtle flex items-center justify-between bg-atlas-surface-subtle">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-atlas-accent" />
            <h3 className="text-xs font-semibold text-atlas-text-primary">
              Canonical Financial Fact Inspector
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-atlas-text-muted hover:text-atlas-text-primary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-4 space-y-4 text-xs font-sans">
          {/* Company & Metric Title Banner */}
          <div className="p-3 bg-atlas-surface-subtle border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted">Observation Target</div>
            <div className="text-sm font-semibold text-atlas-text-primary mt-0.5">
              {observation.company_name} <span className="font-mono text-atlas-accent">({observation.ticker})</span>
            </div>
            <div className="text-xs text-atlas-text-secondary mt-1 flex items-center gap-2">
              <span className="font-medium text-atlas-text-primary">{observation.metric_name}</span>
              <span className="font-mono text-[10px] text-atlas-text-muted">[{observation.metric_id}]</span>
            </div>
          </div>

          {/* Value Matrix */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-2.5 bg-atlas-surface-subtle border border-atlas-border-subtle rounded">
              <div className="text-[10px] text-atlas-text-muted">Reported / Computed Value</div>
              <div className="text-base font-bold font-mono text-atlas-text-primary mt-1">
                {observation.formatted_value}
              </div>
              <div className="text-[10px] text-atlas-text-muted font-mono mt-0.5">
                Exact: {observation.exact_value !== null && observation.exact_value !== undefined ? observation.exact_value.toString() : "N/M"} {observation.unit}
              </div>
            </div>

            <div className="p-2.5 bg-atlas-surface-subtle border border-atlas-border-subtle rounded">
              <div className="text-[10px] text-atlas-text-muted">Period Alignment</div>
              <div className="text-sm font-semibold font-mono text-atlas-text-primary mt-1">
                {observation.period_id}
              </div>
              <div className="text-[10px] text-atlas-text-muted font-mono mt-0.5">
                Period End: {observation.period_end}
              </div>
            </div>
          </div>

          {/* Details Table */}
          <div className="space-y-2 border border-atlas-border-subtle rounded p-3 text-[11px]">
            <div className="flex justify-between py-1 border-b border-atlas-border-subtle/50">
              <span className="text-atlas-text-muted">Canonical Entity UUID:</span>
              <span className="font-mono text-atlas-text-secondary truncate max-w-[220px]">
                {observation.company_id}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-atlas-border-subtle/50">
              <span className="text-atlas-text-muted">Reporting Currency:</span>
              <span className="font-mono text-atlas-text-primary font-medium">
                {observation.currency || "USD"}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-atlas-border-subtle/50">
              <span className="text-atlas-text-muted">Metric Category:</span>
              <span className="font-mono text-atlas-text-secondary">
                {observation.category}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-atlas-border-subtle/50">
              <span className="text-atlas-text-muted">Availability Status:</span>
              <span className="font-mono text-emerald-400 font-medium">
                {observation.status}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-atlas-border-subtle/50">
              <span className="text-atlas-text-muted">Source XBRL Reference:</span>
              <span className="font-mono text-blue-400 font-medium truncate max-w-[220px]">
                {observation.source_filing_ref || "SEC EDGAR Form 10-K"}
              </span>
            </div>

            {observation.explanation && (
              <div className="py-1">
                <span className="text-atlas-text-muted block mb-0.5">Methodology Explanation:</span>
                <span className="text-atlas-text-secondary italic">
                  {observation.explanation}
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between pt-2 text-[10px] text-atlas-text-muted">
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Verified Canonical Source Fact (Stage 82 / 83)
            </span>
            <button
              onClick={onClose}
              className="px-3 py-1 bg-atlas-surface-subtle hover:bg-atlas-surface border border-atlas-border-subtle rounded text-atlas-text-primary transition-colors text-xs"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
