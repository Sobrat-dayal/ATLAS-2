"use client";

import React, { useState } from "react";
import { Bookmark, X, Loader2 } from "lucide-react";
import { Button } from "@/design-system";

interface AtlasMapSaveViewDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string) => Promise<void>;
}

export function AtlasMapSaveViewDialog({
  isOpen,
  onClose,
  onSave,
}: AtlasMapSaveViewDialogProps) {
  const [name, setName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSaving(true);
    setError(null);
    try {
      await onSave(name.trim());
      setName("");
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to save map view");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="flex flex-col w-full max-w-md bg-atlas-surface-1 border border-atlas-border-default rounded shadow-2xl overflow-hidden font-mono text-xs">
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">Save Map View</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary p-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          <div>
            <label className="block text-[11px] text-atlas-text-muted mb-1 uppercase tracking-wider">
              View Name
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. European Monetary Analysis View"
              className="w-full h-8 px-2.5 bg-atlas-surface-2 border border-atlas-border-default rounded text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>

          <div className="text-[10px] text-atlas-text-muted">
            Saves current camera center, zoom, bearing, active layers, and selections into the Universal Saved Library (Stage 119) and Workspace Panels (Stage 120).
          </div>

          {error && <div className="text-rose-400 text-[11px] font-mono">{error}</div>}

          <div className="pt-2 flex justify-end gap-2 border-t border-atlas-border-default/40">
            <Button variant="ghost" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" disabled={isSaving || !name.trim()}>
              {isSaving ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                  Saving...
                </>
              ) : (
                "Save View"
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

