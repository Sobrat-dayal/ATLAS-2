"use client";

import React from "react";
import {
  FileText,
  ShieldCheck,
  ExternalLink,
  History,
  Layers,
  Database,
  Calendar,
  AlertCircle,
  Tag,
} from "lucide-react";
import {
  EconomicSeriesObservationsResponseDTO,
  EconomicVintageDTO,
} from "@/lib/economics";

interface EconomicSourceInspectorProps {
  seriesData: EconomicSeriesObservationsResponseDTO | null;
  vintages: EconomicVintageDTO[];
}

export function EconomicSourceInspector({ seriesData, vintages }: EconomicSourceInspectorProps) {
  if (!seriesData) return null;

  const { series, geography, indicator, effective_unit } = seriesData;

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded p-4 mb-6">
      <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle mb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <h4 className="text-xs font-semibold text-atlas-text-primary">
            Statistical Source Provenance & Revision Inspector
          </h4>
        </div>
        {series.source_url && (
          <a
            href={series.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs flex items-center gap-1 text-atlas-accent hover:underline"
          >
            <span>Official Agency Portal</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs mb-4">
        {/* 1. Canonical Indicator & Identity */}
        <div className="p-2.5 bg-atlas-background/60 rounded border border-atlas-border-subtle/50">
          <div className="text-[10px] text-atlas-text-muted font-medium uppercase mb-1">
            Canonical Identity
          </div>
          <div className="font-semibold text-atlas-text-primary">{indicator.display_name}</div>
          <div className="font-mono text-[11px] text-atlas-text-muted mt-0.5">
            Code: {indicator.canonical_code}
          </div>
          <div className="text-[10px] text-atlas-text-secondary mt-1">
            Category: {indicator.category} &bull; Methodology v{indicator.methodology_version}
          </div>
        </div>

        {/* 2. Source Series & Provider */}
        <div className="p-2.5 bg-atlas-background/60 rounded border border-atlas-border-subtle/50">
          <div className="text-[10px] text-atlas-text-muted font-medium uppercase mb-1">
            Source Provider Specification
          </div>
          <div className="font-semibold text-atlas-text-primary">{series.source_provider_id}</div>
          <div className="font-mono text-[11px] text-atlas-text-muted mt-0.5">
            Series Code: {series.source_series_code}
          </div>
          <div className="text-[10px] text-atlas-text-secondary mt-1">
            Authority: {geography.statistical_agency} ({geography.iso_code})
          </div>
        </div>

        {/* 3. Measurement Semantics */}
        <div className="p-2.5 bg-atlas-background/60 rounded border border-atlas-border-subtle/50">
          <div className="text-[10px] text-atlas-text-muted font-medium uppercase mb-1">
            Measurement Semantics
          </div>
          <div className="font-semibold text-atlas-text-primary">{series.unit}</div>
          <div className="text-[11px] text-atlas-text-muted mt-0.5">
            Adj: {series.seasonal_adjustment}
          </div>
          <div className="text-[10px] text-atlas-text-secondary mt-1">
            Basis: {series.price_basis} {series.index_base ? `(Base: ${series.index_base})` : ""}
          </div>
        </div>
      </div>

      {/* Official Definition Box */}
      <div className="p-2.5 bg-atlas-background/40 rounded border border-atlas-border-subtle/50 mb-3 text-xs">
        <span className="font-semibold text-atlas-text-secondary block mb-0.5">
          Official Agency Definition:
        </span>
        <p className="text-atlas-text-muted leading-relaxed text-[11px]">
          {series.source_definition}
        </p>
      </div>

      {/* Official Revision Vintages (if available) */}
      {vintages && vintages.length > 0 && (
        <div className="mt-3 pt-3 border-t border-atlas-border-subtle/50">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-atlas-text-primary mb-2">
            <History className="w-3.5 h-3.5 text-blue-400" />
            <span>Official Publication Vintages ({vintages[0].reference_period})</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {vintages.map((v) => (
              <div
                key={v.vintage_id}
                className="p-2 bg-atlas-background/70 border border-atlas-border-subtle/60 rounded text-[11px]"
              >
                <div className="flex items-center justify-between text-atlas-text-muted mb-0.5">
                  <span className="font-medium text-atlas-text-primary">{v.estimate_label}</span>
                  <span className="text-[10px] font-mono">{v.status}</span>
                </div>
                <div className="text-sm font-bold font-mono text-atlas-accent">
                  {v.value.toFixed(2)}%
                </div>
                <div className="text-[10px] text-atlas-text-muted mt-1">
                  Released: {v.published_at.slice(0, 10)} &bull; Rev: {v.source_revision}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
