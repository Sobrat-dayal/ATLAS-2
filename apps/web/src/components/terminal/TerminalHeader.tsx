"use client";

import React from "react";
import { Terminal, Minus, Square, Minimize2, X, Settings2 } from "lucide-react";
import { useGlobalContext } from "@/hooks/context/useGlobalContext";

interface TerminalHeaderProps {
  workspaceName?: string;
  isMaximized: boolean;
  onToggleMaximize: () => void;
  onMinimize: () => void;
  onClose: () => void;
  onOpenSettings: () => void;
}

export function TerminalHeader({
  workspaceName,
  isMaximized,
  onToggleMaximize,
  onMinimize,
  onClose,
  onOpenSettings,
}: TerminalHeaderProps) {
  const { activeChannel } = useGlobalContext();

  const currentTicker =
    activeChannel?.context_snapshot?.INSTRUMENT ||
    activeChannel?.context_snapshot?.COMPANY ||
    null;

  return (
    <div className="flex h-8 shrink-0 items-center justify-between border-b border-atlas-border-default bg-atlas-surface-2 px-3 select-none text-atlas-text-primary">
      {/* Left: Title & Roadmap Badge */}
      <div className="flex items-center gap-2">
        <Terminal className="h-3.5 w-3.5 text-atlas-accent" />
        <span className="text-xs font-semibold uppercase tracking-wider">
          ATLAS Terminal
        </span>
        <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-atlas-accent/15 text-atlas-accent border border-atlas-accent/30 font-semibold">
          STAGE 122
        </span>

        {/* Global Context Indicator */}
        <div className="hidden md:flex items-center gap-1.5 ml-2 text-[10px] font-mono text-atlas-text-muted border-l border-atlas-border-subtle pl-2.5">
          <span>Desk: {workspaceName || "Default Desk"}</span>
          {currentTicker && (
            <>
              <span className="text-atlas-border-default">&bull;</span>
              <span className="text-atlas-text-primary font-semibold">
                Context: {String(currentTicker)}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Right: Window controls */}
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={onOpenSettings}
          title="Terminal Settings"
          aria-label="Terminal Settings"
          className="rounded p-1 text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors focus:outline-none"
        >
          <Settings2 className="h-3.5 w-3.5" />
        </button>

        <button
          type="button"
          onClick={onMinimize}
          title="Minimize Terminal"
          aria-label="Minimize Terminal"
          className="rounded p-1 text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors focus:outline-none"
        >
          <Minus className="h-3.5 w-3.5" />
        </button>

        <button
          type="button"
          onClick={onToggleMaximize}
          title={isMaximized ? "Restore Terminal size" : "Maximize Terminal"}
          aria-label={isMaximized ? "Restore Terminal size" : "Maximize Terminal"}
          className="rounded p-1 text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors focus:outline-none"
        >
          {isMaximized ? (
            <Minimize2 className="h-3.5 w-3.5" />
          ) : (
            <Square className="h-3 w-3" />
          )}
        </button>

        <button
          type="button"
          onClick={onClose}
          title="Close Terminal (Esc)"
          aria-label="Close Terminal"
          className="rounded p-1 text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors focus:outline-none"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

