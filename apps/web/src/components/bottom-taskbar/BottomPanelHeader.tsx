"use client";

import React from "react";
import { X, RotateCcw } from "lucide-react";
import { BottomPanelDefinition } from "@/lib/bottom-taskbar";

export interface BottomPanelHeaderProps {
  panel: BottomPanelDefinition;
  onClose: () => void;
  onResetHeight?: () => void;
}

export function BottomPanelHeader({
  panel,
  onClose,
  onResetHeight,
}: BottomPanelHeaderProps) {
  const Icon = panel.icon;

  return (
    <div className="flex h-8 shrink-0 items-center justify-between border-b border-atlas-border-default bg-atlas-surface-2 px-3 select-none">
      <div className="flex items-center gap-2">
        <Icon className="h-3.5 w-3.5 text-atlas-accent" />
        <h3 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
          {panel.label}
        </h3>
        <span className="hidden sm:inline-block text-[11px] text-atlas-text-muted">
          &mdash; {panel.description}
        </span>
      </div>

      <div className="flex items-center gap-1">
        {onResetHeight && (
          <button
            type="button"
            onClick={onResetHeight}
            title="Restore default panel height (280px)"
            aria-label="Restore default panel height"
            className="rounded p-1 text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors focus:outline-none focus:ring-1 focus:ring-atlas-accent"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
        )}

        <button
          type="button"
          onClick={onClose}
          title="Close panel (Esc)"
          aria-label={`Close ${panel.label} panel`}
          className="rounded p-1 text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors focus:outline-none focus:ring-1 focus:ring-atlas-accent"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
