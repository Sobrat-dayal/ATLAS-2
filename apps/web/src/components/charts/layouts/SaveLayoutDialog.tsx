"use client";

/**
 * Save / Save As Modal Dialog for ATLAS Chart Workspaces (Stage 74).
 */

import React, { useState, useEffect } from "react";
import { Bookmark, X, Check, AlertCircle } from "lucide-react";

interface SaveLayoutDialogProps {
  isOpen: boolean;
  isSaveAs?: boolean;
  initialName?: string;
  initialDescription?: string;
  initialIsDefault?: boolean;
  isSaving: boolean;
  error?: string | null;
  onSave: (name: string, description?: string, isDefault?: boolean) => Promise<boolean>;
  onClose: () => void;
}

export function SaveLayoutDialog({
  isOpen,
  isSaveAs = false,
  initialName = "",
  initialDescription = "",
  initialIsDefault = false,
  isSaving,
  error: serverError,
  onSave,
  onClose,
}: SaveLayoutDialogProps) {
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState(initialDescription);
  const [isDefault, setIsDefault] = useState(initialIsDefault);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setName(initialName || (isSaveAs ? "My Chart Workspace (Copy)" : "My Chart Workspace"));
      setDescription(initialDescription || "");
      setIsDefault(initialIsDefault);
      setLocalError(null);
    }
  }, [isOpen, initialName, initialDescription, initialIsDefault, isSaveAs]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setLocalError("Layout name cannot be empty.");
      return;
    }
    if (trimmed.length > 100) {
      setLocalError("Layout name must be 100 characters or fewer.");
      return;
    }

    setLocalError(null);
    const success = await onSave(trimmed, description.trim() || undefined, isDefault);
    if (success) {
      onClose();
    }
  };

  const displayError = localError || serverError;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-150"
      role="dialog"
      aria-modal="true"
      aria-labelledby="save-layout-dialog-title"
    >
      <div className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden font-sans text-zinc-100">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/50">
          <div className="flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-cyan-400" />
            <h2 id="save-layout-dialog-title" className="text-sm font-semibold tracking-tight font-mono text-zinc-100">
              {isSaveAs ? "SAVE AS NEW LAYOUT" : "SAVE CHART LAYOUT"}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {displayError && (
            <div className="p-2.5 rounded bg-red-950/40 border border-red-800/60 text-xs text-red-300 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <span>{displayError}</span>
            </div>
          )}

          <div className="space-y-1.5">
            <label htmlFor="layout-name-input" className="block text-xs font-mono text-zinc-400 font-medium">
              Layout Name <span className="text-cyan-400">*</span>
            </label>
            <input
              id="layout-name-input"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Intraday Equities, Macro Cross-Asset"
              maxLength={100}
              required
              autoFocus
              className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700/80 rounded text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 transition-colors font-mono"
            />
            <p className="text-[11px] text-zinc-500 font-mono">
              Unique name identifying this arrangement of charts, drawings, and indicators.
            </p>
          </div>

          <div className="space-y-1.5">
            <label htmlFor="layout-desc-input" className="block text-xs font-mono text-zinc-400 font-medium">
              Description (Optional)
            </label>
            <textarea
              id="layout-desc-input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional notes regarding this workspace setup..."
              maxLength={500}
              rows={2}
              className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700/80 rounded text-xs text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 transition-colors resize-none"
            />
          </div>

          <div className="flex items-center gap-2 pt-1">
            <input
              id="layout-default-checkbox"
              type="checkbox"
              checked={isDefault}
              onChange={(e) => setIsDefault(e.target.checked)}
              className="w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-cyan-500 focus:ring-0 focus:ring-offset-0 cursor-pointer"
            />
            <label htmlFor="layout-default-checkbox" className="text-xs text-zinc-300 font-mono cursor-pointer select-none">
              Set as my default layout for /charts
            </label>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-2 pt-3 border-t border-zinc-800/80">
            <button
              type="button"
              onClick={onClose}
              disabled={isSaving}
              className="px-3 py-1.5 rounded text-xs font-mono text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving || !name.trim()}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded text-xs font-mono font-semibold bg-cyan-600 hover:bg-cyan-500 text-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Check className="w-3.5 h-3.5" />
              <span>{isSaving ? "Saving..." : "Save Layout"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
