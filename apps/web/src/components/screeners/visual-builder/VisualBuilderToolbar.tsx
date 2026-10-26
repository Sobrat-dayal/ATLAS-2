"use client";

import React from "react";
import {
  Check,
  Eye,
  Play,
  RotateCcw,
  SlidersHorizontal,
  Trash2,
} from "lucide-react";

interface VisualBuilderToolbarProps {
  conditionsCount: number;
  maxConditions?: number;
  isDirty: boolean;
  isValid: boolean;
  isLoading: boolean;
  isLibraryOpen: boolean;
  onToggleLibrary: () => void;
  onApply: () => void;
  onDiscard: () => void;
  onClear: () => void;
  onReviewLogic: () => void;
}

export function VisualBuilderToolbar({
  conditionsCount,
  maxConditions = 20,
  isDirty,
  isValid,
  isLoading,
  isLibraryOpen,
  onToggleLibrary,
  onApply,
  onDiscard,
  onClear,
  onReviewLogic,
}: VisualBuilderToolbarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border/60 bg-muted/20 px-4 py-2.5 text-xs">
      {/* Left side: Library toggle & Condition limit & Dirty Badge */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleLibrary}
          aria-expanded={isLibraryOpen}
          className={`inline-flex items-center gap-1.5 rounded border px-2.5 py-1 font-medium transition-colors ${
            isLibraryOpen
              ? "border-primary/60 bg-primary/10 text-primary"
              : "border-border/60 bg-background text-muted-foreground hover:bg-muted hover:text-foreground"
          }`}
        >
          <SlidersHorizontal className="h-3.5 w-3.5" />
          <span>{isLibraryOpen ? "Hide Catalog" : "Add Metric"}</span>
        </button>

        <span className="font-mono text-[11px] text-muted-foreground">
          {conditionsCount} / {maxConditions} filters
        </span>

        {isDirty && (
          <span className="inline-flex items-center gap-1 rounded bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium text-amber-500 border border-amber-500/20 animate-pulse">
            Changes not applied
          </span>
        )}
      </div>

      {/* Right side: Review Logic, Clear, Discard, Apply */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onReviewLogic}
          className="inline-flex items-center gap-1.5 rounded border border-border/60 bg-background px-2.5 py-1 font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <Eye className="h-3.5 w-3.5 text-primary" />
          <span>Review Logic</span>
        </button>

        {conditionsCount > 0 && (
          <button
            type="button"
            onClick={onClear}
            className="inline-flex items-center gap-1 rounded px-2 py-1 font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Clear</span>
          </button>
        )}

        {isDirty && (
          <button
            type="button"
            onClick={onDiscard}
            className="inline-flex items-center gap-1 rounded px-2 py-1 font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Discard</span>
          </button>
        )}

        {/* Apply Filters (Primary) */}
        <button
          type="button"
          onClick={onApply}
          disabled={!isValid || isLoading || (!isDirty && conditionsCount === 0)}
          className={`inline-flex items-center gap-1.5 rounded px-3 py-1 font-medium transition-colors shadow-xs ${
            !isValid || isLoading || (!isDirty && conditionsCount === 0)
              ? "bg-muted text-muted-foreground cursor-not-allowed opacity-60"
              : "bg-primary text-primary-foreground hover:bg-primary/90"
          }`}
        >
          <Play className="h-3.5 w-3.5 fill-current" />
          <span>Apply Filters</span>
        </button>
      </div>
    </div>
  );
}
