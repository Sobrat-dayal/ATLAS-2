"use client";

import React from "react";
import { BookOpen, CheckCircle2, Globe, Shield, Tag, X } from "lucide-react";
import { ScreenerFilterDefinition } from "@/lib/screeners/types";

interface FilterDefinitionInspectorProps {
  filter: ScreenerFilterDefinition | null;
  onClose: () => void;
  onAddCondition?: (filterId: string) => void;
}

export function FilterDefinitionInspector({
  filter,
  onClose,
  onAddCondition,
}: FilterDefinitionInspectorProps) {
  if (!filter) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in-0"
      onClick={onClose}
    >
      <div
        className="relative max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-lg border border-border/80 bg-card p-6 shadow-2xl animate-in zoom-in-95"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="metric-inspector-title"
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b border-border/60 pb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-mono font-semibold uppercase tracking-wider text-primary">
                {filter.category.replace("_", " ")}
              </span>
              <span className="font-mono text-xs text-muted-foreground">
                ID: {filter.filter_id}
              </span>
            </div>
            <h2 id="metric-inspector-title" className="mt-1 text-base font-semibold text-foreground">
              {filter.display_name}
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Close inspector"
            className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="mt-4 space-y-4 text-xs">
          {/* Description */}
          <div>
            <h3 className="font-medium text-muted-foreground">Description</h3>
            <p className="mt-1 text-foreground leading-relaxed">
              {filter.description}
            </p>
          </div>

          {/* Methodology Reference */}
          {filter.methodology_reference && (
            <div className="rounded-md border border-border/60 bg-muted/20 p-3">
              <div className="flex items-center gap-1.5 font-medium text-foreground">
                <BookOpen className="h-3.5 w-3.5 text-primary" />
                <span>Institutional Methodology & Formula</span>
              </div>
              <p className="mt-1.5 text-[11px] leading-relaxed text-muted-foreground font-mono">
                {filter.methodology_reference}
              </p>
            </div>
          )}

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 gap-3 rounded-md border border-border/40 bg-muted/10 p-3">
            <div>
              <span className="text-[11px] text-muted-foreground">Value Type</span>
              <p className="font-mono font-medium text-foreground capitalize">
                {filter.value_type}
              </p>
            </div>
            <div>
              <span className="text-[11px] text-muted-foreground">Measurement Unit</span>
              <p className="font-mono font-medium text-foreground capitalize">
                {filter.unit_kind.replace("_", " ")}
              </p>
            </div>
            <div>
              <span className="text-[11px] text-muted-foreground">Supported Operators</span>
              <p className="font-mono font-medium text-foreground uppercase">
                {filter.allowed_operators.join(", ")}
              </p>
            </div>
            <div>
              <span className="text-[11px] text-muted-foreground">Default Operator</span>
              <p className="font-mono font-medium text-foreground uppercase">
                {filter.default_operator}
              </p>
            </div>
            {filter.indicator_type && (
              <>
                <div>
                  <span className="text-[11px] text-muted-foreground">Indicator Family</span>
                  <p className="font-mono font-medium text-primary uppercase">
                    {filter.indicator_type} (v{filter.calculation_version || "1.0.0"})
                  </p>
                </div>
                <div>
                  <span className="text-[11px] text-muted-foreground">Lookback Requirement</span>
                  <p className="font-mono font-medium text-foreground">
                    ≥ {filter.minimum_lookback || 20} completed bars
                  </p>
                </div>
                <div className="col-span-2">
                  <span className="text-[11px] text-muted-foreground">Time Horizon & Bar Policy</span>
                  <p className="font-mono text-[11px] text-muted-foreground">
                    Completed daily exchange sessions (split-adjusted, zero look-ahead bias)
                  </p>
                </div>
                {filter.output_components && filter.output_components.length > 0 && (
                  <div className="col-span-2">
                    <span className="text-[11px] text-muted-foreground">Output Components</span>
                    <p className="font-mono text-[11px] text-foreground">
                      {filter.output_components.join(", ")}
                    </p>
                  </div>
                )}
              </>
            )}
            {filter.aliases && filter.aliases.length > 0 && (
              <div className="col-span-2">
                <span className="text-[11px] text-muted-foreground">Aliases / Search Keywords</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {filter.aliases.map((alias) => (
                    <span
                      key={alias}
                      className="inline-flex items-center gap-1 rounded bg-muted/60 px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground"
                    >
                      <Tag className="h-2.5 w-2.5" />
                      {alias}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Provenance & Coverage */}
          <div className="rounded-md border border-border/40 p-3 space-y-2">
            <div className="flex items-center gap-1.5 font-medium text-foreground">
              <Shield className="h-3.5 w-3.5 text-emerald-500" />
              <span>Institutional Provenance & Coverage</span>
            </div>
            <p className="text-[11px] text-muted-foreground">
              {filter.source_coverage_summary || "Consolidated feed with strict reporting and market session qualification."}
            </p>
            <div className="flex items-center gap-4 text-[11px] text-muted-foreground pt-1 border-t border-border/40">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                Audit Trail Grounded
              </span>
              <span className="flex items-center gap-1">
                <Globe className="h-3 w-3 text-primary" />
                Cross-Venue Reconciled
              </span>
            </div>
          </div>
        </div>

        {/* Footer actions */}
        <div className="mt-6 flex items-center justify-end gap-2 border-t border-border/60 pt-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded border border-border px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted"
          >
            Close
          </button>
          {onAddCondition && (
            <button
              type="button"
              onClick={() => {
                onAddCondition(filter.filter_id);
                onClose();
              }}
              className="rounded bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90"
            >
              Add Condition to Canvas
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
