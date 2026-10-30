"use client";

import React, { useState } from "react";
import { GitCompare, Calendar, ArrowRight, ShieldCheck } from "lucide-react";
import { DocumentComparisonResponse } from "@/lib/ai/research/types";
import { formatPublicationDate } from "@/lib/ai/research/sourceFormatting";
import { AiResearchCitationViewer } from "./AiResearchCitationViewer";

interface AiResearchComparisonProps {
  comparison: DocumentComparisonResponse;
}

export function AiResearchComparison({ comparison }: AiResearchComparisonProps) {
  const [selectedCitation, setSelectedCitation] = useState<Record<string, any> | null>(null);

  return (
    <div className="space-y-4 text-xs">
      {/* Comparison Header */}
      <div className="p-3 rounded-lg bg-atlas-surface-2 border border-atlas-border-default space-y-2">
        <div className="flex items-center gap-2 text-atlas-accent font-semibold">
          <GitCompare className="h-4 w-4" />
          <span>Cross-Document Financial Comparison</span>
        </div>

        <div className="grid grid-cols-2 gap-3 pt-1 border-t border-atlas-border-default/60">
          <div className="space-y-0.5">
            <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider block">Document A</span>
            <div className="font-medium text-atlas-text-primary truncate">{comparison.document_a_title}</div>
            <div className="flex items-center gap-1 text-[10px] text-atlas-text-secondary">
              <Calendar className="h-2.5 w-2.5" />
              {formatPublicationDate(comparison.document_a_date)}
            </div>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider block">Document B</span>
            <div className="font-medium text-atlas-text-primary truncate">{comparison.document_b_title}</div>
            <div className="flex items-center gap-1 text-[10px] text-atlas-text-secondary">
              <Calendar className="h-2.5 w-2.5" />
              {formatPublicationDate(comparison.document_b_date)}
            </div>
          </div>
        </div>
      </div>

      {/* Identified Differences Cards */}
      {comparison.differences && comparison.differences.length > 0 && (
        <div className="space-y-2.5">
          <span className="text-[11px] font-semibold text-atlas-text-muted uppercase tracking-wider block">
            Identified Material Variances
          </span>

          {comparison.differences.map((diff, idx) => (
            <div
              key={idx}
              className="p-3 rounded-lg bg-atlas-surface-1 border border-atlas-border-default space-y-2 shadow-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-atlas-text-primary">{diff.aspect}</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-atlas-surface-3 font-mono text-atlas-accent border border-atlas-border-default">
                  {diff.difference_text}
                </span>
              </div>

              <div className="flex items-center justify-between text-[11px] bg-atlas-surface-2 p-2 rounded">
                <div className="flex items-center gap-1.5">
                  <span className="text-atlas-text-muted">Doc A:</span>
                  <span className="font-mono text-atlas-text-primary font-medium">{diff.doc_a_value}</span>
                </div>
                <ArrowRight className="h-3 w-3 text-atlas-text-muted" />
                <div className="flex items-center gap-1.5">
                  <span className="text-atlas-text-muted">Doc B:</span>
                  <span className="font-mono text-atlas-text-primary font-medium">{diff.doc_b_value}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary Text */}
      <div className="p-3 rounded-lg bg-atlas-surface-1 border border-atlas-border-default space-y-1.5 leading-relaxed text-atlas-text-secondary">
        <span className="text-[10px] font-semibold text-atlas-text-muted uppercase tracking-wider block">
          Analytical Summary
        </span>
        <p className="select-text text-atlas-text-primary">{comparison.summary_text}</p>
      </div>

      <AiResearchCitationViewer
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
}
