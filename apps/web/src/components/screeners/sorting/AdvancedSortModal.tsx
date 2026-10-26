"use client";

import React, { useState } from "react";
import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  Check,
  ChevronDown,
  ChevronUp,
  Info,
  Plus,
  RotateCcw,
  Trash2,
  X,
} from "lucide-react";
import {
  ScreenerColumnDefinition,
  SortCriterion,
  SortDirection,
  SortNullOrder,
} from "@/lib/screeners/types";

interface AdvancedSortModalProps {
  isOpen: boolean;
  onClose: () => void;
  sortCriteria: SortCriterion[];
  columnsRegistry: ScreenerColumnDefinition[];
  onApplySort: (criteria: SortCriterion[]) => void;
}

const MAX_SORT_KEYS = 5;

const DEFAULT_SORT: SortCriterion[] = [
  { field_id: "market_cap", direction: "desc", null_order: "nulls_last" },
];

export function AdvancedSortModal({
  isOpen,
  onClose,
  sortCriteria,
  columnsRegistry,
  onApplySort,
}: AdvancedSortModalProps) {
  const [localCriteria, setLocalCriteria] = useState<SortCriterion[]>(
    sortCriteria.length > 0 ? sortCriteria : DEFAULT_SORT
  );

  React.useEffect(() => {
    if (isOpen) {
      setLocalCriteria(sortCriteria.length > 0 ? sortCriteria : DEFAULT_SORT);
    }
  }, [isOpen, sortCriteria]);

  if (!isOpen) return null;

  const sortableColumns = columnsRegistry.filter((c) => c.sortable);

  const handleAddCriterion = () => {
    if (localCriteria.length >= MAX_SORT_KEYS) return;
    // Find first column not already in localCriteria
    const available = sortableColumns.find(
      (c) => !localCriteria.some((sc) => sc.field_id === c.column_id)
    );
    const fieldId = available ? available.column_id : sortableColumns[0]?.column_id ?? "market_cap";

    setLocalCriteria((prev) => [
      ...prev,
      { field_id: fieldId, direction: "desc", null_order: "nulls_last" },
    ]);
  };

  const handleRemoveCriterion = (index: number) => {
    setLocalCriteria((prev) => {
      const copy = [...prev];
      copy.splice(index, 1);
      return copy.length > 0 ? copy : DEFAULT_SORT;
    });
  };

  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    setLocalCriteria((prev) => {
      const copy = [...prev];
      const temp = copy[index - 1];
      copy[index - 1] = copy[index];
      copy[index] = temp;
      return copy;
    });
  };

  const handleMoveDown = (index: number) => {
    if (index >= localCriteria.length - 1) return;
    setLocalCriteria((prev) => {
      const copy = [...prev];
      const temp = copy[index + 1];
      copy[index + 1] = copy[index];
      copy[index] = temp;
      return copy;
    });
  };

  const handleUpdateCriterion = (
    index: number,
    field_id?: string,
    direction?: SortDirection,
    null_order?: SortNullOrder
  ) => {
    setLocalCriteria((prev) => {
      const copy = [...prev];
      copy[index] = {
        field_id: field_id ?? copy[index].field_id,
        direction: direction ?? copy[index].direction,
        null_order: null_order ?? copy[index].null_order,
      };
      return copy;
    });
  };

  const handleReset = () => {
    setLocalCriteria(DEFAULT_SORT);
  };

  const handleApply = () => {
    onApplySort(localCriteria);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl rounded-lg border border-border bg-card shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150 flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/70 px-6 py-4 bg-muted/30">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary border border-primary/20">
              <ArrowUpDown className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-foreground">
                Advanced Multi-Column Sorting
              </h2>
              <p className="text-xs text-muted-foreground">
                Deterministic Server-Side Sorting Across All Filtered Securities Prior to Pagination
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 overflow-y-auto flex-1">
          {/* Explanation Alert */}
          <div className="flex items-start gap-2.5 rounded-md bg-primary/5 border border-primary/20 p-3 text-xs text-muted-foreground">
            <Info className="h-4 w-4 text-primary shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p>
                <strong className="text-foreground">Hierarchical Multi-Column Evaluation:</strong> Sorting rules are evaluated in priority order. If securities have identical values for Rule 1, Rule 2 resolves the tie. A canonical security identifier is appended as an immutable final tie-breaker.
              </p>
              <p className="text-[11px] text-muted-foreground/80">
                Supports up to {MAX_SORT_KEYS} typed sort keys with explicit null ordering (<code className="text-foreground">NULLS_LAST</code> / <code className="text-foreground">NULLS_FIRST</code>).
              </p>
            </div>
          </div>

          {/* Sort Rules List */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-muted-foreground px-1">
              <span>Configured Sort Criteria ({localCriteria.length}/{MAX_SORT_KEYS})</span>
              <button
                type="button"
                onClick={handleReset}
                className="flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground transition-colors"
              >
                <RotateCcw className="h-3 w-3" />
                <span>Reset to Default</span>
              </button>
            </div>

            {localCriteria.map((criterion, idx) => {
              const selectedCol = columnsRegistry.find((c) => c.column_id === criterion.field_id);

              return (
                <div
                  key={`${criterion.field_id}-${idx}`}
                  className="flex items-center gap-2 p-3 rounded-md border border-border/70 bg-muted/20"
                >
                  {/* Priority Indicator */}
                  <span className="flex h-6 w-6 items-center justify-center rounded bg-muted text-muted-foreground font-mono text-[11px] font-bold">
                    #{idx + 1}
                  </span>

                  {/* Field Selector */}
                  <div className="flex-1 min-w-0">
                    <select
                      aria-label={`Sort Field ${idx + 1}`}
                      value={criterion.field_id}
                      onChange={(e) => handleUpdateCriterion(idx, e.target.value)}
                      className="h-8 w-full rounded border border-border/80 bg-background px-2.5 text-xs font-medium text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    >
                      {sortableColumns.map((col) => (
                        <option key={col.column_id} value={col.column_id}>
                          {col.display_label} ({col.data_type})
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Direction Selector */}
                  <div className="flex items-center rounded border border-border/80 bg-background overflow-hidden">
                    <button
                      type="button"
                      onClick={() => handleUpdateCriterion(idx, undefined, "desc")}
                      className={`flex h-8 items-center gap-1 px-2.5 text-xs font-medium transition-colors ${
                        criterion.direction === "desc"
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:text-foreground"
                      }`}
                      title="Sort Descending (High to Low)"
                    >
                      <ArrowDown className="h-3 w-3" />
                      <span>DESC</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleUpdateCriterion(idx, undefined, "asc")}
                      className={`flex h-8 items-center gap-1 px-2.5 text-xs font-medium transition-colors border-l border-border/60 ${
                        criterion.direction === "asc"
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:text-foreground"
                      }`}
                      title="Sort Ascending (Low to High)"
                    >
                      <ArrowUp className="h-3 w-3" />
                      <span>ASC</span>
                    </button>
                  </div>

                  {/* Null Order Selector */}
                  <select
                    aria-label={`Null Ordering ${idx + 1}`}
                    value={criterion.null_order ?? "nulls_last"}
                    onChange={(e) =>
                      handleUpdateCriterion(
                        idx,
                        undefined,
                        undefined,
                        e.target.value as SortNullOrder
                      )
                    }
                    className="h-8 rounded border border-border/80 bg-background px-2 text-[11px] font-mono text-muted-foreground focus:border-primary focus:outline-none"
                    title="Where missing/null values should be placed"
                  >
                    <option value="nulls_last">Nulls Last</option>
                    <option value="nulls_first">Nulls First</option>
                  </select>

                  {/* Priority Order Buttons */}
                  <div className="flex items-center gap-0.5">
                    <button
                      type="button"
                      onClick={() => handleMoveUp(idx)}
                      disabled={idx === 0}
                      className="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted disabled:opacity-30 transition-colors"
                      title="Increase priority"
                    >
                      <ChevronUp className="h-3.5 w-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleMoveDown(idx)}
                      disabled={idx === localCriteria.length - 1}
                      className="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted disabled:opacity-30 transition-colors"
                      title="Decrease priority"
                    >
                      <ChevronDown className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  {/* Remove Button */}
                  <button
                    type="button"
                    onClick={() => handleRemoveCriterion(idx)}
                    className="p-1.5 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                    title="Remove sort criterion"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })}
          </div>

          {/* Add Rule Button */}
          {localCriteria.length < MAX_SORT_KEYS && (
            <button
              type="button"
              onClick={handleAddCriterion}
              className="flex w-full items-center justify-center gap-1.5 py-2.5 rounded-md border border-dashed border-border/80 text-xs font-medium text-muted-foreground hover:border-primary/50 hover:text-primary transition-colors bg-background"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>Add Secondary Sort Rule ({localCriteria.length}/{MAX_SORT_KEYS})</span>
            </button>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-border/70 px-6 py-3 bg-muted/20">
          <span className="text-xs text-muted-foreground">
            Appends canonical identifier tie-breaker automatically.
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleApply}
              className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <Check className="h-3.5 w-3.5" />
              <span>Apply Sort</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
