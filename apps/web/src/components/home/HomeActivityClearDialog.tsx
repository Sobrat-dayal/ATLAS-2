"use client";

import React, { useEffect, useRef } from "react";
import { AlertTriangle, Trash2, X } from "lucide-react";

interface HomeActivityClearDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isSubmitting?: boolean;
  mode: "clear" | "disable";
}

export function HomeActivityClearDialog({
  isOpen,
  onClose,
  onConfirm,
  isSubmitting = false,
  mode,
}: HomeActivityClearDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const isDisable = mode === "disable";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs"
      role="dialog"
      aria-modal="true"
      aria-labelledby="activity-dialog-title"
    >
      <div
        ref={dialogRef}
        className="relative w-full max-w-md p-5 rounded-lg border border-atlas-border-strong bg-atlas-surface-1 shadow-2xl animate-in fade-in zoom-in-95 duration-150"
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-full bg-atlas-error/10 border border-atlas-error/30 flex items-center justify-center text-atlas-error shrink-0">
              <AlertTriangle className="h-4 w-4" aria-hidden="true" />
            </div>
            <div>
              <h2
                id="activity-dialog-title"
                className="text-sm font-semibold text-atlas-text-primary"
              >
                {isDisable ? "Disable Activity History?" : "Clear Activity History?"}
              </h2>
              <p className="text-xs text-atlas-text-muted mt-0.5">
                {isDisable
                  ? "Workspace continuity will be disabled."
                  : "Permanent deletion of recorded interactions."}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary p-1 rounded hover:bg-atlas-surface-hover focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
            aria-label="Close dialog"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        <div className="my-4 text-xs text-atlas-text-secondary leading-relaxed">
          {isDisable ? (
            <p>
              Disabling activity history also securely erases your previously recorded Stage 53
              history under ATLAS&apos;s privacy-first policy. Normal navigation and entity selection will continue working.
            </p>
          ) : (
            <p>
              Clear all recorded ATLAS activity history? This will permanently delete your
              recorded module opens and entity selections. This will not delete your entities,
              settings, or other application data.
            </p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-atlas-border-subtle">
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="px-3 py-1.5 rounded text-xs font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-hover border border-atlas-border-subtle transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isSubmitting}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-semibold text-white bg-atlas-error hover:bg-atlas-error/90 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-error disabled:opacity-50 shadow-xs"
          >
            <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
            <span>{isSubmitting ? "Processing..." : isDisable ? "Disable & Clear" : "Clear History"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
