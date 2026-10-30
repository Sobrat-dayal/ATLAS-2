"use client";

import React, { useState } from "react";
import { Settings, Star, X } from "lucide-react";
import { Button } from "@/design-system";
import { Workspace } from "@/lib/workspaces/types";

interface WorkspaceSettingsDialogProps {
  isOpen: boolean;
  workspace: Workspace;
  onClose: () => void;
  onUpdateMetadata: (data: {
    name?: string;
    description?: string;
    is_favorite?: boolean;
    settings?: Record<string, unknown>;
  }) => Promise<any>;
}

export function WorkspaceSettingsDialog({
  isOpen,
  workspace,
  onClose,
  onUpdateMetadata,
}: WorkspaceSettingsDialogProps) {
  const [name, setName] = useState(workspace.name);
  const [description, setDescription] = useState(workspace.description || "");
  const [isFavorite, setIsFavorite] = useState(workspace.is_favorite);
  const [autosave, setAutosave] = useState<boolean>(
    workspace.settings?.autosave !== undefined ? Boolean(workspace.settings.autosave) : true
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsSubmitting(true);
    try {
      await onUpdateMetadata({
        name: name.trim(),
        description: description.trim() || undefined,
        is_favorite: isFavorite,
        settings: {
          ...workspace.settings,
          autosave,
        },
      });
      onClose();
    } catch (err: unknown) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="flex flex-col w-full max-w-md bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-2xl overflow-hidden font-mono text-xs">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Settings className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">Desk Settings</h3>
          </div>
          <button type="button" onClick={onClose} className="text-atlas-text-muted hover:text-atlas-text-primary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-bold text-atlas-text-muted">Desk Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-border-focus"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-bold text-atlas-text-muted">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Workspace thesis or objective..."
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-border-focus resize-none font-sans"
            />
          </div>

          <div className="pt-2 border-t border-atlas-border-subtle flex flex-col gap-2">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={isFavorite}
                onChange={(e) => setIsFavorite(e.target.checked)}
                className="rounded border-atlas-border-default"
              />
              <span className="text-xs text-atlas-text-primary flex items-center gap-1">
                <Star className={`w-3.5 h-3.5 ${isFavorite ? "text-amber-400 fill-amber-400" : "text-atlas-text-muted"}`} />
                Mark as Favorite Desk
              </span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={autosave}
                onChange={(e) => setAutosave(e.target.checked)}
                className="rounded border-atlas-border-default"
              />
              <span className="text-xs text-atlas-text-primary">
                Enable Real-Time Autosave (Debounced)
              </span>
            </label>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-2 pt-3 border-t border-atlas-border-default mt-4">
            <Button variant="ghost" size="xs" type="button" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button variant="primary" size="xs" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : "Save Settings"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

