"use client";

import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface AiResearchErrorStateProps {
  error: string;
  onRetry?: () => void;
}

export function AiResearchErrorState({ error, onRetry }: AiResearchErrorStateProps) {
  return (
    <div className="p-4 rounded-lg bg-red-950/20 border border-red-500/30 text-xs space-y-2.5">
      <div className="flex items-start gap-2.5">
        <AlertTriangle className="h-4 w-4 shrink-0 text-red-400 mt-0.5" />
        <div className="space-y-1 flex-1">
          <span className="font-semibold text-red-300 block">Research Retrieval Error</span>
          <p className="text-[11px] text-red-200/80 leading-relaxed select-text">{error}</p>
        </div>
      </div>

      {onRetry && (
        <div className="pl-6.5 pt-1">
          <button
            type="button"
            onClick={onRetry}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-red-950/50 hover:bg-red-950/80 border border-red-500/40 text-red-300 text-[11px] font-medium transition-colors"
          >
            <RefreshCw className="h-3 w-3" />
            <span>Retry Query</span>
          </button>
        </div>
      )}
    </div>
  );
}

