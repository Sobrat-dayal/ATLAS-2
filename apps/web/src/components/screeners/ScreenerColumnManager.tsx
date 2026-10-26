"use client";

import React from "react";
import { Check, RotateCcw, X } from "lucide-react";
import { ScreenerColumnDefinition } from "@/lib/screeners/types";

interface ScreenerColumnManagerProps {
  isOpen: boolean;
  onClose: () => void;
  columnsRegistry: ScreenerColumnDefinition[];
  visibleColumnIds: string[];
  onToggleColumn: (columnId: string) => void;
  onResetColumns: () => void;
}

export function ScreenerColumnManager({
  isOpen,
  onClose,
  columnsRegistry,
  visibleColumnIds,
  onToggleColumn,
  onResetColumns,
}: ScreenerColumnManagerProps) {
  if (!isOpen) return null;

  const categories = Array.from(new Set(columnsRegistry.map((c) => c.category)));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4 backdrop-blur-xs">
      <div className="flex max-h-[85vh] w-full max-w-xl flex-col rounded-lg border border-border bg-card shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-5 py-3.5">
          <div>
            <h2 className="text-sm font-semibold text-foreground">
              Configure Table Columns
            </h2>
            <p className="text-xs text-muted-foreground">
              Select metrics and attributes to display in the screener table
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content list grouped by category */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {categories.map((cat) => {
            const cols = columnsRegistry.filter((c) => c.category === cat);
            const catLabel =
              cat === "market_data"
                ? "Market Data & Quotes"
                : cat === "fundamentals"
                ? "Fundamental Metrics"
                : cat === "valuation"
                ? "Valuation Multiples"
                : cat === "profitability"
                ? "Profitability & Returns"
                : cat.toUpperCase();

            return (
              <div key={cat} className="space-y-2">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {catLabel}
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {cols.map((col) => {
                    const isVisible = visibleColumnIds.includes(col.column_id);
                    return (
                      <label
                        key={col.column_id}
                        className={`flex items-center gap-2.5 rounded-md border p-2 text-xs cursor-pointer transition-colors ${
                          isVisible
                            ? "border-primary/50 bg-primary/5 text-foreground"
                            : "border-border/60 hover:bg-muted/40 text-muted-foreground"
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isVisible}
                          onChange={() => onToggleColumn(col.column_id)}
                          className="rounded border-border text-primary focus:ring-primary h-3.5 w-3.5"
                        />
                        <span className="font-medium">{col.display_label}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-border px-5 py-3 bg-muted/20">
          <button
            type="button"
            onClick={onResetColumns}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Restore Defaults</span>
          </button>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md bg-primary px-3.5 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90"
          >
            Apply Columns
          </button>
        </div>
      </div>
    </div>
  );
}
