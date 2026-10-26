"use client";

import React, { useState } from "react";
import { AlertCircle, Check, Copy, FileText, Globe, Layers, X } from "lucide-react";
import { QueryPreviewSummary } from "@/lib/screeners/types";

interface VisualQueryPreviewProps {
  summary: QueryPreviewSummary;
  isOpen: boolean;
  onClose: () => void;
}

export function VisualQueryPreview({
  summary,
  isOpen,
  onClose,
}: VisualQueryPreviewProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const copyToClipboard = () => {
    const textLines = [
      `ATLAS SCREENER QUERY SPECIFICATION`,
      `Universe: ${summary.universeName} (${summary.universeId})`,
      `Reporting Basis: ${summary.periodPolicy}`,
      `Currency Basis: ${summary.currencyPolicy}`,
      `Active Conditions (${summary.conditionsCount}):`,
      ...summary.plainEnglishPredicates.map((p, idx) =>
        idx === 0 ? `  ${p}` : `  AND ${p}`
      ),
    ];
    navigator.clipboard.writeText(textLines.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in-0"
      onClick={onClose}
    >
      <div
        className="relative max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-lg border border-border/80 bg-card p-6 shadow-2xl animate-in zoom-in-95 text-xs"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="preview-logic-title"
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b border-border/60 pb-3">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-primary" />
            <h2 id="preview-logic-title" className="text-sm font-semibold text-foreground">
              Review Screening Logic
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Close query review"
            className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        <div className="mt-4 space-y-4">
          {/* Universe Scoping */}
          <div className="rounded border border-border/60 bg-muted/20 p-3">
            <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
              Selected Universe
            </span>
            <div className="mt-1 flex items-center gap-2">
              <Globe className="h-3.5 w-3.5 text-primary" />
              <span className="font-semibold text-foreground">{summary.universeName}</span>
            </div>
          </div>

          {/* Predicates */}
          <div>
            <div className="flex items-center justify-between pb-1.5">
              <span className="font-medium text-muted-foreground">
                Composed Conditions ({summary.conditionsCount})
              </span>
              <span className="text-[10px] font-mono text-muted-foreground">
                Logical Conjunction: AND
              </span>
            </div>

            {summary.plainEnglishPredicates.length === 0 ? (
              <div className="rounded border border-dashed border-border/60 p-4 text-center text-muted-foreground">
                No active conditions. Universe unfiltered.
              </div>
            ) : (
              <div className="rounded border border-border/60 bg-background/80 divide-y divide-border/40 font-mono text-[11px]">
                {summary.plainEnglishPredicates.map((predicate, idx) => (
                  <div key={idx} className="flex items-start gap-2 p-2.5">
                    <span className="font-semibold text-primary/80 shrink-0 select-none">
                      {idx === 0 ? "WHERE" : "  AND"}
                    </span>
                    <span className="text-foreground leading-relaxed">{predicate}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Validation Status */}
          {summary.contradictionsDetected && (
            <div className="flex items-start gap-2 rounded border border-destructive/50 bg-destructive/10 p-3 text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <div>
                <span className="font-semibold">Contradictory Conditions Detected</span>
                <p className="mt-0.5 text-[11px] leading-relaxed text-destructive/90">
                  One or more conditions contradict each other. No securities can satisfy this query. Review highlighted boundaries.
                </p>
              </div>
            </div>
          )}

          {/* Reporting & Currency Policies */}
          <div className="grid grid-cols-2 gap-2 text-[10px] text-muted-foreground pt-1 border-t border-border/40 font-mono">
            <div>
              <span>Reporting: </span>
              <span className="text-foreground font-medium">{summary.periodPolicy}</span>
            </div>
            <div>
              <span>Currency: </span>
              <span className="text-foreground font-medium">{summary.currencyPolicy}</span>
            </div>
          </div>
        </div>

        {/* Footer actions */}
        <div className="mt-6 flex items-center justify-between border-t border-border/60 pt-3">
          <button
            type="button"
            onClick={copyToClipboard}
            className="inline-flex items-center gap-1.5 rounded border border-border px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? "Copied" : "Copy Query Logic"}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="rounded bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
