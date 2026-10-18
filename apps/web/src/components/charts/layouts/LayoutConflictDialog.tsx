"use client";

/**
 * Concurrency Conflict Dialog for ATLAS Chart Workspaces (Stage 74).
 *
 * Implements:
 * - Clear warning when another browser session or device has updated the layout
 * - Displays server revision vs local expected revision
 * - Non-destructive recovery options:
 *   1. Save As New Layout (preserves current working changes under a copy)
 *   2. Reload Server Version (reloads the newer version from database)
 *   3. Keep Editing Unsaved (retains unsaved local copy)
 */

import React from "react";
import { AlertTriangle, Copy, RotateCcw, X } from "lucide-react";
import { LayoutConflictState } from "@/lib/charts";

interface LayoutConflictDialogProps {
  conflictState: LayoutConflictState | null;
  onSaveAsNew: () => void;
  onReloadServer: (layoutId: string) => void;
  onDismiss: () => void;
}

export function LayoutConflictDialog({
  conflictState,
  onSaveAsNew,
  onReloadServer,
  onDismiss,
}: LayoutConflictDialogProps) {
  if (!conflictState) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-150"
      role="dialog"
      aria-modal="true"
      aria-labelledby="conflict-dialog-title"
    >
      <div className="w-full max-w-md bg-zinc-950 border border-amber-600/70 rounded-lg shadow-2xl overflow-hidden font-sans text-zinc-100">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-amber-950/30">
          <div className="flex items-center gap-2 text-amber-400">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <h2 id="conflict-dialog-title" className="text-sm font-semibold tracking-tight font-mono">
              CONCURRENCY CONFLICT DETECTED
            </h2>
          </div>
          <button
            onClick={onDismiss}
            className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            aria-label="Dismiss conflict alert"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-3">
          <p className="text-xs text-zinc-300 leading-relaxed">
            Layout <strong className="text-zinc-100 font-mono">"{conflictState.layoutName}"</strong> was modified and saved
            by another session or authorized device.
          </p>

          <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800 text-xs font-mono space-y-1">
            <div className="flex justify-between text-zinc-400">
              <span>Your local version revision:</span>
              <span className="text-amber-300 font-semibold">{conflictState.expectedRevision}</span>
            </div>
            <div className="flex justify-between text-zinc-400">
              <span>Database server revision:</span>
              <span className="text-cyan-300 font-semibold">{conflictState.serverRevision}</span>
            </div>
          </div>

          <p className="text-[11px] text-zinc-400">
            To prevent silent overwrites or data loss, select how you would like to proceed:
          </p>

          {/* Action Buttons */}
          <div className="pt-2 space-y-2">
            <button
              onClick={onSaveAsNew}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded text-xs font-mono font-semibold bg-cyan-600 hover:bg-cyan-500 text-black transition-colors"
            >
              <Copy className="w-3.5 h-3.5" />
              <span>Save My Changes As New Layout</span>
            </button>

            <button
              onClick={() => onReloadServer(conflictState.layoutId)}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded text-xs font-mono font-semibold bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors border border-zinc-700"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Discard Local Changes & Reload Server Version</span>
            </button>

            <button
              onClick={onDismiss}
              className="w-full py-1.5 rounded text-xs font-mono text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition-colors"
            >
              Keep Editing Unsaved (Do Not Save Now)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
