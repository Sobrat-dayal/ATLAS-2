"use client";

import React from "react";
import { FilterX, RotateCcw } from "lucide-react";

interface ScreenerEmptyStateProps {
  onReset: () => void;
}

export function ScreenerEmptyState({ onReset }: ScreenerEmptyStateProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center p-12 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted text-muted-foreground border border-border/80">
        <FilterX className="h-6 w-6" />
      </div>
      <h3 className="mt-4 text-sm font-semibold text-foreground">
        No Matching Securities Found
      </h3>
      <p className="mt-1 max-w-sm text-xs text-muted-foreground">
        No canonical financial instruments satisfied all the active screening criteria simultaneously.
        Try relaxing threshold bounds or removing restrictive sector/exchange filters.
      </p>
      <button
        type="button"
        onClick={onReset}
        className="mt-4 flex items-center gap-1.5 rounded-md bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:bg-secondary/80 transition-colors"
      >
        <RotateCcw className="h-3.5 w-3.5" />
        <span>Reset Filters</span>
      </button>
    </div>
  );
}
