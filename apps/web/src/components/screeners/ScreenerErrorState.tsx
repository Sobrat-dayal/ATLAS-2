"use client";

import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface ScreenerErrorStateProps {
  error: string;
  onRetry: () => void;
}

export function ScreenerErrorState({ error, onRetry }: ScreenerErrorStateProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center p-12 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive border border-destructive/20">
        <AlertTriangle className="h-6 w-6" />
      </div>
      <h3 className="mt-4 text-sm font-semibold text-foreground">
        Screen Execution Failed
      </h3>
      <p className="mt-1 max-w-md text-xs text-muted-foreground font-mono bg-muted/40 p-2 rounded border border-border/60">
        {error}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-4 flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
      >
        <RefreshCw className="h-3.5 w-3.5" />
        <span>Retry Screening</span>
      </button>
    </div>
  );
}
