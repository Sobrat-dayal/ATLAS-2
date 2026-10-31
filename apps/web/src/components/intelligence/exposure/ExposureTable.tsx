"use client";

import React from "react";
import { AtlasExposureResult } from "@/lib/intelligence/exposure/types";
import { formatExposureAmount, formatPercentage } from "@/lib/intelligence/exposure/units";
import { Info, ExternalLink, CheckCircle2, AlertTriangle, HelpCircle } from "lucide-react";

interface ExposureTableProps {
  results: AtlasExposureResult[];
  selectedExposureId?: string | null;
  onSelectExposure: (exposure: AtlasExposureResult) => void;
}

export function ExposureTable({
  results,
  selectedExposureId,
  onSelectExposure
}: ExposureTableProps) {
  if (results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center text-zinc-500 font-mono text-sm">
        <Info className="w-8 h-8 mb-2 text-zinc-600" />
        <p>No verified exposure relations for the current selection and filter criteria.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto w-full font-mono text-xs">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-zinc-800 bg-zinc-900/80 text-zinc-400 select-none">
            <th className="py-2.5 px-3 font-semibold">TARGET ENTITY</th>
            <th className="py-2.5 px-3 font-semibold">DOMAIN & TYPE</th>
            <th className="py-2.5 px-3 font-semibold text-right">EXPOSURE AMOUNT</th>
            <th className="py-2.5 px-3 font-semibold text-right">SHARE / WEIGHT</th>
            <th className="py-2.5 px-3 font-semibold">DENOMINATOR REF</th>
            <th className="py-2.5 px-3 font-semibold">EVIDENCE CLASS</th>
            <th className="py-2.5 px-3 font-semibold text-center">ACTION</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800/60">
          {results.map((row) => {
            const isSelected = selectedExposureId === row.exposure_id;
            const isUnavailable = row.evidence_class === "UNAVAILABLE";

            return (
              <tr
                key={row.exposure_id}
                onClick={() => onSelectExposure(row)}
                className={`cursor-pointer transition-colors ${
                  isSelected
                    ? "bg-sky-950/40 text-zinc-100 border-l-2 border-sky-500"
                    : "hover:bg-zinc-900/50 text-zinc-300"
                }`}
              >
                {/* Target Entity */}
                <td className="py-2 px-3">
                  <div className="flex items-center gap-2">
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-zinc-800 text-zinc-300 font-semibold uppercase">
                      {row.target_entity_ref.node_type}
                    </span>
                    <span className="font-medium text-zinc-200">
                      {row.target_entity_ref.canonical_name}
                    </span>
                    {row.target_entity_ref.country_code && (
                      <span className="text-[10px] text-zinc-500">
                        [{row.target_entity_ref.country_code}]
                      </span>
                    )}
                  </div>
                </td>

                {/* Domain & Type */}
                <td className="py-2 px-3">
                  <div className="text-zinc-200">{row.exposure_domain}</div>
                  <div className="text-[10px] text-zinc-500 truncate max-w-[220px]">
                    {row.exposure_type.replace(/_/g, " ")}
                  </div>
                </td>

                {/* Amount */}
                <td className="py-2 px-3 text-right font-medium">
                  {isUnavailable ? (
                    <span className="text-zinc-500 italic">UNAVAILABLE</span>
                  ) : (
                    <span className={Number(row.amount) < 0 ? "text-rose-400" : "text-zinc-100"}>
                      {formatExposureAmount(row.amount, row.unit, row.currency || "USD")}
                    </span>
                  )}
                </td>

                {/* Share / Weight */}
                <td className="py-2 px-3 text-right">
                  {row.percentage !== null && row.percentage !== undefined ? (
                    <span className="px-1.5 py-0.5 rounded bg-zinc-800/80 font-bold text-sky-400">
                      {formatPercentage(row.percentage)}
                    </span>
                  ) : (
                    <span className="text-zinc-600">—</span>
                  )}
                </td>

                {/* Denominator Reference */}
                <td className="py-2 px-3 text-zinc-400 max-w-[180px] truncate">
                  {row.denominator_reference || (row.denominator_value ? `${row.denominator_value} ${row.currency || ""}` : "—")}
                </td>

                {/* Evidence Class */}
                <td className="py-2 px-3">
                  <div className="flex items-center gap-1.5">
                    {row.evidence_class === "REPORTED" || row.evidence_class === "DETERMINISTICALLY_CALCULATED" ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    ) : row.evidence_class === "USER_DEFINED_SCENARIO" ? (
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    ) : (
                      <HelpCircle className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                    )}
                    <span className="text-[11px] text-zinc-300">
                      {row.evidence_class}
                    </span>
                  </div>
                </td>

                {/* Action */}
                <td className="py-2 px-3 text-center">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectExposure(row);
                    }}
                    className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
                    title="Inspect calculation lineage and evidence"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
