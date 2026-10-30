"use client";

import React from "react";
import { ContextMode } from "@/lib/ai/context/types";

interface AiContextModeSelectorProps {
  mode: ContextMode;
  onChange: (mode: ContextMode) => void;
  disabled?: boolean;
}

const MODES: Array<{ key: ContextMode; label: string; tooltip: string }> = [
  { key: "OFF", label: "Off", tooltip: "Privacy mode: no page, workspace, or entity data is sent to AI." },
  { key: "FOCUSED", label: "Focused", tooltip: "Shares active entity and focused panel context only." },
  { key: "WORKSPACE", label: "Workspace", tooltip: "Shares full workspace panel inventory and linked channels." },
  { key: "CUSTOM", label: "Custom", tooltip: "Manually pinned financial entities and custom parameters." },
];

export function AiContextModeSelector({ mode, onChange, disabled }: AiContextModeSelectorProps) {
  return (
    <div
      role="group"
      aria-label="AI Context Mode"
      className="inline-flex rounded border border-atlas-border-subtle bg-atlas-bg-1 p-0.5 text-[11px]"
    >
      {MODES.map((m) => {
        const isActive = mode === m.key;
        return (
          <button
            key={m.key}
            type="button"
            title={m.tooltip}
            disabled={disabled}
            onClick={() => onChange(m.key)}
            className={`px-2 py-0.5 font-medium rounded transition-colors ${
              isActive
                ? "bg-atlas-accent text-white shadow-xs"
                : "text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-bg-2"
            } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
          >
            {m.label}
          </button>
        );
      })}
    </div>
  );
}

