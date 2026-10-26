"use client";

import React, { useState } from "react";
import {
  ComparableIndicatorDTO,
  ComparisonMatrixResponseDTO,
  MatrixCellDTO,
} from "@/lib/economics/comparisons";
import { Info, AlertCircle, CheckCircle2 } from "lucide-react";

interface MacroComparisonMatrixProps {
  matrixData: ComparisonMatrixResponseDTO | null;
  indicators: ComparableIndicatorDTO[];
  onSelectCell: (cell: MatrixCellDTO) => void;
  isLoading: boolean;
}

export function MacroComparisonMatrix({
  matrixData,
  indicators,
  onSelectCell,
  isLoading,
}: MacroComparisonMatrixProps) {
  const [hoveredCellKey, setHoveredCellKey] = useState<string | null>(null);

  if (isLoading && !matrixData) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2">
        <div className="w-6 h-6 border-2 border-atlas-accent border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-mono">Generating Cross-Country Macroeconomic Matrix...</span>
      </div>
    );
  }

  if (!matrixData || matrixData.cells.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2 border border-dashed border-atlas-border-subtle rounded m-4">
        <Info className="w-8 h-8 text-atlas-text-muted/60" />
        <p className="text-sm font-medium text-atlas-text-primary">No Comparison Matrix Data</p>
        <p className="text-xs text-atlas-text-muted">
          Select at least two countries or cohorts to view comparative macroeconomic observations.
        </p>
      </div>
    );
  }

  // Group cells by country
  const countryRowsMap = new Map<string, { countryName: string; isoCode: string; cells: Map<string, MatrixCellDTO> }>();

  matrixData.cells.forEach((cell) => {
    if (!countryRowsMap.has(cell.geography_id)) {
      countryRowsMap.set(cell.geography_id, {
        countryName: cell.country_name,
        isoCode: cell.iso_code,
        cells: new Map<string, MatrixCellDTO>(),
      });
    }
    countryRowsMap.get(cell.geography_id)!.cells.set(cell.metric_kind, cell);
  });

  const countryRows = Array.from(countryRowsMap.entries());

  return (
    <div className="flex flex-col flex-1 h-full min-h-0 bg-atlas-background overflow-hidden">
      {/* Matrix Metadata Banner */}
      <div className="px-4 py-2 border-b border-atlas-border-subtle bg-atlas-surface/40 flex flex-wrap items-center justify-between text-xs gap-2">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-atlas-text-primary">
            Cross-Country Economic Matrix ({countryRows.length} Economies × {matrixData.metric_kinds.length} Metrics)
          </span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
            Policy: {matrixData.period_policy.replace(/_/g, " ")}
          </span>
        </div>
        <div className="flex items-center gap-2 text-atlas-text-muted text-[11px] font-mono">
          <span>Click any cell for source lineage & methodology audit</span>
        </div>
      </div>

      {/* High-density Scrollable Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse text-left text-xs font-mono">
          <thead className="sticky top-0 bg-atlas-surface border-b border-atlas-border-subtle z-10 shadow-xs">
            <tr>
              <th className="p-2.5 font-bold text-atlas-text-primary sticky left-0 bg-atlas-surface min-w-[140px] border-r border-atlas-border-subtle z-20">
                Country / Area
              </th>
              {matrixData.metric_kinds.map((metricKind) => {
                const def = indicators.find((i) => i.metric_kind === metricKind);
                return (
                  <th
                    key={metricKind}
                    className="p-2.5 font-semibold text-atlas-text-secondary min-w-[140px] max-w-[180px] border-r border-atlas-border-subtle/60 whitespace-nowrap"
                    title={def?.description}
                  >
                    <div className="flex flex-col gap-0.5">
                      <span className="text-atlas-text-primary truncate">{def?.name || metricKind}</span>
                      <span className="text-[10px] text-atlas-text-muted font-normal">
                        {def?.default_unit || "—"}
                      </span>
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle/40">
            {countryRows.map(([geoId, rowData]) => {
              const isEconomicArea = geoId === "geo-ea";
              return (
                <tr
                  key={geoId}
                  className="hover:bg-atlas-surface/50 transition-colors group"
                >
                  {/* Sticky Country Header Cell */}
                  <td className="p-2.5 font-semibold text-atlas-text-primary sticky left-0 bg-atlas-surface/90 backdrop-blur-xs border-r border-atlas-border-subtle z-10 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-atlas-background border border-atlas-border-subtle text-atlas-accent font-bold">
                        {rowData.isoCode}
                      </span>
                      <span className="truncate">{rowData.countryName}</span>
                      {isEconomicArea && (
                        <span className="text-[9px] uppercase px-1 py-0.2 rounded bg-amber-500/15 text-amber-300 font-normal">
                          AREA
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Metric Value Cells */}
                  {matrixData.metric_kinds.map((metricKind) => {
                    const cell = rowData.cells.get(metricKind);
                    const cellKey = `${geoId}-${metricKind}`;
                    const isHovered = hoveredCellKey === cellKey;

                    if (!cell || cell.raw_value === null || cell.raw_value === undefined) {
                      return (
                        <td
                          key={metricKind}
                          className="p-2.5 text-atlas-text-muted/40 text-center border-r border-atlas-border-subtle/40"
                        >
                          —
                        </td>
                      );
                    }

                    const isQualified = cell.status === "comparable_with_qualification";

                    return (
                      <td
                        key={metricKind}
                        onClick={() => onSelectCell(cell)}
                        onMouseEnter={() => setHoveredCellKey(cellKey)}
                        onMouseLeave={() => setHoveredCellKey(null)}
                        className={`p-2.5 border-r border-atlas-border-subtle/40 cursor-pointer transition-colors relative ${
                          isHovered ? "bg-atlas-accent/10" : ""
                        }`}
                        title="Click to view source methodology and lineage"
                      >
                        <div className="flex flex-col gap-0.5">
                          <div className="flex items-center justify-between gap-1">
                            <span className="font-bold text-atlas-text-primary text-[13px] tracking-tight">
                              {cell.formatted_value}
                            </span>
                            {isQualified && (
                              <span title="Methodological caveats apply">
                                <AlertCircle className="w-3 h-3 text-amber-400 shrink-0" />
                              </span>
                            )}
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-atlas-text-muted gap-1">
                            <span className="truncate">{cell.reference_period}</span>
                            <span className="text-[9px] uppercase tracking-wider text-atlas-text-muted/70 truncate">
                              {cell.source_agency}
                            </span>
                          </div>
                        </div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
