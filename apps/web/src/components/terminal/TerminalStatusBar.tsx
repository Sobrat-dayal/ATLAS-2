"use client";

import React from "react";
import { TerminalSession, TerminalUserPreferences } from "@/lib/terminal/types";
import { ShieldAlert } from "lucide-react";

interface TerminalStatusBarProps {
  activeSession: TerminalSession | null;
  preferences: TerminalUserPreferences;
  lineCount?: number;
}

export function TerminalStatusBar({
  activeSession,
  preferences,
  lineCount,
}: TerminalStatusBarProps) {
  if (!activeSession) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "READY":
      case "CONNECTED":
        return "bg-emerald-500";
      case "INPUT_ONLY":
        return "bg-amber-500";
      case "READ_ONLY":
        return "bg-sky-500";
      case "ERROR":
        return "bg-rose-500";
      default:
        return "bg-zinc-500";
    }
  };

  return (
    <div className="flex h-5 shrink-0 items-center justify-between border-t border-atlas-border-subtle bg-atlas-surface-0 px-2.5 text-[10px] font-mono select-none text-atlas-text-muted">
      {/* Left: Session Status & Stage 122 Boundary */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className={`w-1.5 h-1.5 rounded-full ${getStatusColor(activeSession.status)}`} />
          <span className="font-semibold text-atlas-text-primary uppercase tracking-wider">
            {activeSession.terminal_type.replace("_", " ")}
          </span>
          <span>&bull;</span>
          <span className="uppercase">{activeSession.status}</span>
        </div>

        <div className="hidden sm:flex items-center gap-1 text-amber-400 bg-amber-400/10 px-1.5 py-0.2 rounded border border-amber-400/20">
          <ShieldAlert className="h-2.5 w-2.5" />
          <span>STAGE 122: EXECUTION DISABLED</span>
        </div>
      </div>

      {/* Right: Metrics & preferences */}
      <div className="flex items-center gap-3">
        {lineCount !== undefined && (
          <div>
            <span>Lines: {lineCount}</span>
          </div>
        )}
        <div>
          <span>Font: {preferences.font_size}px</span>
        </div>
        <div className="hidden md:block">
          <span>Wrap: {preferences.word_wrap ? "ON" : "OFF"}</span>
        </div>
        <div>
          <span>UTF-8</span>
        </div>
      </div>
    </div>
  );
}

