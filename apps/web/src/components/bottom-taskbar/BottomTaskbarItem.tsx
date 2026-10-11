"use client";

import React from "react";
import { BottomPanelDefinition, BottomPanelId } from "@/lib/bottom-taskbar";

export interface BottomTaskbarItemProps {
  panel: BottomPanelDefinition;
  isActive: boolean;
  onToggle: (id: BottomPanelId) => void;
  className?: string;
}

export function BottomTaskbarItem({
  panel,
  isActive,
  onToggle,
  className = "",
}: BottomTaskbarItemProps) {
  const Icon = panel.icon;

  return (
    <button
      type="button"
      onClick={() => onToggle(panel.id)}
      aria-label={`${isActive ? "Close" : "Open"} ${panel.label} panel`}
      aria-expanded={isActive}
      aria-controls={`bottom-panel-${panel.id}`}
      aria-pressed={isActive}
      title={`${panel.label} — ${panel.description}`}
      className={`group relative flex h-full items-center px-2.5 sm:px-3 text-[11px] font-medium uppercase tracking-wider transition-colors select-none focus:outline-none focus:ring-1 focus:ring-atlas-accent ${
        isActive
          ? "bg-atlas-surface-selected text-atlas-accent before:absolute before:top-0 before:left-0 before:right-0 before:h-[2px] before:bg-atlas-accent"
          : "text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
      } ${className}`}
    >
      <Icon className="mr-1.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
      <span className="truncate">{panel.label}</span>
    </button>
  );
}
