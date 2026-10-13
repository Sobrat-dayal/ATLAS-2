"use client";

import React from "react";
import { Clock } from "lucide-react";

export interface HomeReservedStateProps {
  stage: number;
  featureName: string;
  description: string;
  icon?: React.ReactNode;
}

export function HomeReservedState({
  stage,
  featureName,
  description,
  icon,
}: HomeReservedStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center p-6 bg-atlas-surface-2/30 border border-dashed border-atlas-border-subtle rounded-sm">
      <div className="h-8 w-8 rounded-full bg-atlas-surface-3 border border-atlas-border-default flex items-center justify-center text-atlas-text-secondary mb-3">
        {icon || <Clock className="h-4 w-4" aria-hidden="true" />}
      </div>
      <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-medium uppercase tracking-wider bg-atlas-surface-3 text-atlas-text-secondary border border-atlas-border-subtle mb-2">
        <span>Roadmap Stage {stage}</span>
      </div>
      <h3 className="text-xs font-semibold text-atlas-text-primary">
        {featureName}
      </h3>
      <p className="text-[11px] text-atlas-text-muted mt-1 max-w-sm">
        {description}
      </p>
    </div>
  );
}
