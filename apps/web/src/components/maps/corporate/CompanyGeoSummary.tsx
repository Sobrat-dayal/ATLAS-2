"use client";

import React from "react";
import { Building2, Globe, Layers, ShieldCheck, ArrowRightLeft, AlertCircle } from "lucide-react";
import { CompanyFootprintSummary } from "@/lib/maps/corporate/types";
import { FACILITY_TYPE_STYLES } from "@/lib/maps/corporate/facilityStyles";

interface CompanyGeoSummaryProps {
  summary: CompanyFootprintSummary | null;
  onOpenCompare?: () => void;
  className?: string;
}

export function CompanyGeoSummary({ summary, onOpenCompare, className = "" }: CompanyGeoSummaryProps) {
  if (!summary) {
    return (
      <div className={`p-4 bg-zinc-950 border border-zinc-800 rounded text-center text-xs text-zinc-500 ${className}`}>
        Select a company to view verified corporate geographic footprint.
      </div>
    );
  }

  const topTypes = Object.entries(summary.facility_type_breakdown || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <div className={`p-3 bg-zinc-950 border border-zinc-800 rounded space-y-3 text-xs ${className}`}>
      {/* Header & Canonical Name */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2">
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-sky-400" />
          <div>
            <div className="font-bold text-zinc-100 flex items-center gap-1.5">
              <span>{summary.canonical_name}</span>
              {summary.ticker && (
                <span className="font-mono text-[10px] px-1 py-0.2 bg-zinc-800 text-sky-400 rounded">
                  {summary.ticker}
                </span>
              )}
            </div>
            <div className="text-[10px] text-zinc-500">
              Verified Corporate Geography Footprint
            </div>
          </div>
        </div>

        {onOpenCompare && (
          <button
            type="button"
            onClick={onOpenCompare}
            className="flex items-center gap-1 px-2 py-1 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700/60 rounded text-[10px] text-zinc-300 transition-colors"
          >
            <ArrowRightLeft className="w-3 h-3 text-sky-400" />
            <span>Compare</span>
          </button>
        )}
      </div>

      {/* 4 Key Stat Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        <div className="p-2 bg-zinc-900/60 rounded border border-zinc-800/60">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
            Distinct Facilities
          </div>
          <div className="text-base font-bold font-mono text-zinc-100 mt-0.5">
            {summary.distinct_facilities}
          </div>
          <div className="text-[9px] text-zinc-500">
            {summary.total_facilities} total records
          </div>
        </div>

        <div className="p-2 bg-zinc-900/60 rounded border border-zinc-800/60">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
            Countries
          </div>
          <div className="text-base font-bold font-mono text-sky-400 mt-0.5">
            {summary.countries_count}
          </div>
          <div className="text-[9px] text-zinc-500">Global jurisdictions</div>
        </div>

        <div className="p-2 bg-zinc-900/60 rounded border border-zinc-800/60">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
            Direct vs Subsidiary
          </div>
          <div className="text-sm font-bold font-mono text-zinc-200 mt-0.5 flex items-center gap-1.5">
            <span className="text-emerald-400">{summary.direct_facilities_count}</span>
            <span className="text-zinc-600">/</span>
            <span className="text-indigo-400">{summary.subsidiary_facilities_count}</span>
          </div>
          <div className="text-[9px] text-zinc-500">Direct / Sub sites</div>
        </div>

        <div className="p-2 bg-zinc-900/60 rounded border border-zinc-800/60">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
            Sources & Audits
          </div>
          <div className="text-sm font-bold font-mono text-emerald-400 mt-0.5 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Verified</span>
          </div>
          <div className="text-[9px] text-zinc-500">
            {summary.source_coverage?.sources_count || 1} documented sources
          </div>
        </div>
      </div>

      {/* Facility Type Breakdown Badges */}
      {topTypes.length > 0 && (
        <div>
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
            <Layers className="w-2.5 h-2.5" />
            <span>Top Facility Types</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {topTypes.map(([typeKey, count]) => {
              const style = FACILITY_TYPE_STYLES[typeKey as keyof typeof FACILITY_TYPE_STYLES];
              return (
                <span
                  key={typeKey}
                  className="inline-flex items-center gap-1 px-1.5 py-0.5 bg-zinc-900 border border-zinc-800 rounded text-[10px] text-zinc-300"
                >
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: style?.color || "#71717a" }}
                  />
                  <span>{style?.label || typeKey}:</span>
                  <span className="font-mono font-bold text-zinc-100">{count}</span>
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Unresolved Location Disclaimer */}
      {summary.unresolved_locations_count > 0 && (
        <div className="flex items-start gap-1.5 p-1.5 bg-amber-950/20 border border-amber-900/30 rounded text-[10px] text-amber-400">
          <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <span>
            {summary.unresolved_locations_count} recorded facilities have approximate or unresolved coordinates and are excluded from site-precision map markers.
          </span>
        </div>
      )}
    </div>
  );
}

