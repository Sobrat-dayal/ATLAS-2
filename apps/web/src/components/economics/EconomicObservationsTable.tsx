"use client";

import React, { useState } from "react";
import {
  Table,
  Calendar,
  Download,
  Copy,
  Check,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import {
  EconomicObservationDTO,
  EconomicSeriesObservationsResponseDTO,
} from "@/lib/economics";

interface EconomicObservationsTableProps {
  seriesData: EconomicSeriesObservationsResponseDTO | null;
}

export function EconomicObservationsTable({ seriesData }: EconomicObservationsTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [copied, setCopied] = useState(false);
  const pageSize = 15;

  if (!seriesData || !seriesData.observations || seriesData.observations.length === 0) {
    return null;
  }

  const { observations, series, effective_unit, transformation_applied } = seriesData;
  // Sort descending by reference period (latest first)
  const sorted = [...observations].reverse();
  const totalPages = Math.ceil(sorted.length / pageSize);
  const pagedObs = sorted.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const handleCopyCSV = () => {
    const headers = ["Reference Period", "Value", "Unit", "Status", "Published At", "Revision"];
    const rows = sorted.map((o) => [
      o.reference_period,
      o.value,
      effective_unit,
      o.status,
      o.published_at || "",
      o.source_revision || "",
    ]);
    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    navigator.clipboard.writeText(csvContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded overflow-hidden mb-6">
      <div className="px-4 py-3 border-b border-atlas-border-subtle flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-atlas-accent" />
          <h4 className="text-xs font-semibold text-atlas-text-primary">
            Historical Observations Table ({observations.length} records)
          </h4>
          {transformation_applied !== "SOURCE_REPORTED" && (
            <span className="text-[10px] font-mono bg-atlas-accent/15 text-atlas-accent px-1.5 py-0.5 rounded">
              Transformed: {transformation_applied}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyCSV}
            className="text-xs flex items-center gap-1 px-2.5 py-1 bg-atlas-background hover:bg-atlas-surface-hover border border-atlas-border-subtle rounded text-atlas-text-secondary transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? "Copied CSV" : "Copy CSV"}</span>
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-subtle bg-atlas-background/50 text-atlas-text-muted font-medium">
              <th className="py-2.5 px-3">Reference Period</th>
              <th className="py-2.5 px-3">Exact Observation Value</th>
              <th className="py-2.5 px-3">Unit</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3">Official Publication</th>
              <th className="py-2.5 px-3">Source Revision</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle/50 font-mono">
            {pagedObs.map((obs) => (
              <tr key={obs.observation_id} className="hover:bg-atlas-surface-hover transition-colors">
                <td className="py-2.5 px-3 font-semibold text-atlas-text-primary">
                  {obs.reference_period}
                </td>
                <td className="py-2.5 px-3">
                  <span
                    className={
                      obs.value < 0 ? "text-rose-400 font-semibold" : "text-atlas-text-primary font-semibold"
                    }
                  >
                    {obs.value.toFixed(3)}
                  </span>
                </td>
                <td className="py-2.5 px-3 text-atlas-text-muted text-[11px]">
                  {effective_unit}
                </td>
                <td className="py-2.5 px-3">
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-sans uppercase font-medium ${
                      obs.status === "FINAL"
                        ? "bg-emerald-500/10 text-emerald-400"
                        : obs.status === "REVISED"
                        ? "bg-blue-500/10 text-blue-400"
                        : "bg-amber-500/10 text-amber-400"
                    }`}
                  >
                    {obs.status}
                  </span>
                </td>
                <td className="py-2.5 px-3 text-atlas-text-muted text-[11px]">
                  {obs.published_at ? obs.published_at.slice(0, 10) : "&mdash;"}
                </td>
                <td className="py-2.5 px-3 text-atlas-text-secondary text-[11px]">
                  {obs.source_revision || "Initial Release"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="px-4 py-2.5 bg-atlas-background/40 border-t border-atlas-border-subtle flex items-center justify-between text-xs text-atlas-text-muted">
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <div className="flex items-center gap-1.5">
            <button
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="p-1 rounded border border-atlas-border-subtle hover:bg-atlas-surface disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="p-1 rounded border border-atlas-border-subtle hover:bg-atlas-surface disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
