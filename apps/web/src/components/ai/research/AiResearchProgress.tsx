"use client";

import React from "react";
import { Loader2, Search, Sparkles, CheckCircle2 } from "lucide-react";

interface AiResearchProgressProps {
  status?: string;
  message?: string;
}

export function AiResearchProgress({
  status = "Searching",
  message = "Performing hybrid retrieval across authorized documents...",
}: AiResearchProgressProps) {
  return (
    <div className="p-4 rounded-lg bg-atlas-surface-1 border border-atlas-border-default space-y-2.5 text-xs animate-in fade-in duration-150">
      <div className="flex items-center gap-2 text-atlas-accent font-medium">
        <Loader2 className="h-4 w-4 animate-spin shrink-0" />
        <span>{status}</span>
      </div>

      <p className="text-[11px] text-atlas-text-secondary pl-6 leading-relaxed">
        {message}
      </p>

      {/* Pipeline Stages Mini Tracker */}
      <div className="grid grid-cols-4 gap-1.5 pt-1 pl-6 text-[10px] text-atlas-text-muted">
        <div className="flex items-center gap-1 text-emerald-400 font-mono">
          <CheckCircle2 className="h-2.5 w-2.5" />
          <span>1. Plan</span>
        </div>
        <div className="flex items-center gap-1 text-atlas-accent font-mono">
          <Search className="h-2.5 w-2.5 animate-pulse" />
          <span>2. Retrieve</span>
        </div>
        <div className="flex items-center gap-1 font-mono">
          <span>3. Synthesize</span>
        </div>
        <div className="flex items-center gap-1 font-mono">
          <span>4. Cite</span>
        </div>
      </div>
    </div>
  );
}

