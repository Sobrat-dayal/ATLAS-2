"use client";

import React from "react";
import Link from "next/link";
import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  Building,
  ExternalLink,
  LineChart,
  Plus,
} from "lucide-react";
import {
  ScreenerColumnDefinition,
  ScreenerResultRow,
  SortCriterion,
} from "@/lib/screeners/types";

interface ScreenerResultsTableProps {
  rows: ScreenerResultRow[];
  columns: ScreenerColumnDefinition[];
  sortCriteria: SortCriterion[];
  onToggleSort: (fieldId: string) => void;
  selectedRow: ScreenerResultRow | null;
  onSelectRow: (row: ScreenerResultRow) => void;
  loading: boolean;
}

export function ScreenerResultsTable({
  rows,
  columns,
  sortCriteria,
  onToggleSort,
  selectedRow,
  onSelectRow,
  loading,
}: ScreenerResultsTableProps) {
  const currentSort = sortCriteria[0];

  return (
    <div className="relative flex-1 overflow-x-auto overflow-y-auto">
      <table className="w-full border-collapse text-left text-xs">
        {/* Sticky Header */}
        <thead className="sticky top-0 z-10 border-b border-border/80 bg-muted/90 backdrop-blur font-medium text-muted-foreground select-none">
          <tr>
            {/* Row Number */}
            <th className="w-10 px-3 py-2.5 text-center font-mono text-[11px] text-muted-foreground/60">
              #
            </th>

            {/* Symbol - Sticky Column */}
            <th
              onClick={() => onToggleSort("symbol")}
              className="sticky left-0 z-20 cursor-pointer bg-muted/95 px-3 py-2.5 font-semibold text-foreground hover:text-primary transition-colors border-r border-border/40"
            >
              <div className="flex items-center gap-1.5">
                <span>Symbol</span>
                {currentSort?.field_id === "symbol" ? (
                  currentSort.direction === "desc" ? (
                    <ArrowDown className="h-3 w-3 text-primary" />
                  ) : (
                    <ArrowUp className="h-3 w-3 text-primary" />
                  )
                ) : (
                  <ArrowUpDown className="h-2.5 w-2.5 opacity-40" />
                )}
              </div>
            </th>

            {/* Configured Columns */}
            {columns
              .filter((c) => c.column_id !== "symbol")
              .map((col) => {
                const isSorted = currentSort?.field_id === col.column_id;
                const isNumeric = col.alignment === "right";
                return (
                  <th
                    key={col.column_id}
                    onClick={() => col.sortable && onToggleSort(col.column_id)}
                    className={`px-3 py-2.5 whitespace-nowrap transition-colors ${
                      col.sortable ? "cursor-pointer hover:text-foreground" : ""
                    } ${isNumeric ? "text-right" : "text-left"} ${
                      isSorted ? "text-foreground font-semibold" : ""
                    }`}
                  >
                    <div
                      className={`inline-flex items-center gap-1.5 ${
                        isNumeric ? "flex-row-reverse" : "flex-row"
                      }`}
                    >
                      <span>{col.display_label}</span>
                      {col.sortable && (
                        <span>
                          {isSorted ? (
                            currentSort.direction === "desc" ? (
                              <ArrowDown className="h-3 w-3 text-primary" />
                            ) : (
                              <ArrowUp className="h-3 w-3 text-primary" />
                            )
                          ) : (
                            <ArrowUpDown className="h-2.5 w-2.5 opacity-30" />
                          )}
                        </span>
                      )}
                    </div>
                  </th>
                );
              })}

            {/* Quick Actions Header */}
            <th className="w-20 px-3 py-2.5 text-right">Actions</th>
          </tr>
        </thead>

        {/* Table Body */}
        <tbody className="divide-y divide-border/40 bg-background font-mono text-xs">
          {rows.map((row, idx) => {
            const isSelected = selectedRow?.instrument_entity_id === row.instrument_entity_id;
            return (
              <tr
                key={`${row.instrument_entity_id}-${row.listing_id}`}
                onClick={() => onSelectRow(row)}
                className={`group cursor-pointer transition-colors ${
                  isSelected
                    ? "bg-primary/10 hover:bg-primary/15"
                    : "hover:bg-muted/40"
                }`}
              >
                {/* Index */}
                <td className="px-3 py-2 text-center text-muted-foreground/60 text-[11px]">
                  {idx + 1}
                </td>

                {/* Symbol - Sticky Column */}
                <td className={`sticky left-0 z-10 px-3 py-2 font-bold text-foreground border-r border-border/40 ${
                  isSelected ? "bg-primary/10" : "bg-background group-hover:bg-muted/40"
                }`}>
                  <div className="flex items-center gap-1.5">
                    <span>{row.ticker}</span>
                    {row.share_class_name && row.share_class_name !== "Common Stock" && (
                      <span className="rounded bg-muted px-1 text-[9px] text-muted-foreground font-sans">
                        {row.share_class_name}
                      </span>
                    )}
                  </div>
                </td>

                {/* Dynamically Rendered Metric Columns */}
                {columns
                  .filter((c) => c.column_id !== "symbol")
                  .map((col) => {
                    const cell = row.metrics[col.column_id];
                    const isRight = col.alignment === "right";
                    const isMissing = !cell || cell.status === "missing";
                    const isNM = cell?.status === "not_meaningful";

                    return (
                      <td
                        key={col.column_id}
                        className={`px-3 py-2 whitespace-nowrap tabular-nums ${
                          isRight ? "text-right" : "text-left"
                        } ${
                          isMissing
                            ? "text-muted-foreground/40 font-sans"
                            : isNM
                            ? "text-amber-500/80 font-sans text-[11px]"
                            : "text-foreground"
                        }`}
                      >
                        {cell?.display_value ?? "—"}
                      </td>
                    );
                  })}

                {/* Row Actions */}
                <td
                  className="px-3 py-2 text-right whitespace-nowrap"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-center justify-end gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                    {/* View Chart */}
                    <Link
                      href={`/charts?symbol=${encodeURIComponent(row.ticker)}`}
                      className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
                      title={`View ${row.ticker} Chart`}
                    >
                      <LineChart className="h-3.5 w-3.5" />
                    </Link>

                    {/* View Company */}
                    <Link
                      href={`/companies?id=${row.issuer_company_entity_id}`}
                      className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
                      title="View Company Profile"
                    >
                      <Building className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
