"use client";

/**
 * Saved Layouts Management Modal for ATLAS Charts (Stage 74).
 *
 * Implements:
 * - Comprehensive view of user-owned saved chart layouts
 * - Instant name search & filtering
 * - Fast actions: Open, Rename, Set as Default, Duplicate, Export, Delete
 * - Safe two-step deletion confirmation
 */

import React, { useState } from "react";
import {
  Bookmark,
  Copy,
  Download,
  Edit2,
  FolderKanban,
  Layers,
  Search,
  Star,
  Trash2,
  X,
  Check,
  AlertCircle,
} from "lucide-react";
import { SavedLayoutSummary } from "@/lib/charts";

interface SavedLayoutsManagerDialogProps {
  isOpen: boolean;
  layouts: SavedLayoutSummary[];
  currentLayoutId?: string;
  onOpenLayout: (layoutId: string) => void;
  onRenameLayout: (layoutId: string, newName: string) => Promise<boolean>;
  onSetDefaultLayout: (layoutId: string, isDefault: boolean) => Promise<boolean>;
  onDuplicateLayout: (layoutId: string) => Promise<any>;
  onExportLayout: (layoutId: string) => void;
  onDeleteLayout: (layoutId: string) => Promise<boolean>;
  onClose: () => void;
}

export function SavedLayoutsManagerDialog({
  isOpen,
  layouts,
  currentLayoutId,
  onOpenLayout,
  onRenameLayout,
  onSetDefaultLayout,
  onDuplicateLayout,
  onExportLayout,
  onDeleteLayout,
  onClose,
}: SavedLayoutsManagerDialogProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  if (!isOpen) return null;

  const filtered = layouts.filter((l) =>
    l.name.toLowerCase().includes(searchTerm.toLowerCase().trim())
  );

  const startRename = (l: SavedLayoutSummary) => {
    setEditingId(l.id);
    setEditingName(l.name);
    setActionError(null);
  };

  const handleSaveRename = async (layoutId: string) => {
    if (!editingName.trim()) {
      setActionError("Name cannot be empty.");
      return;
    }
    const ok = await onRenameLayout(layoutId, editingName.trim());
    if (ok) {
      setEditingId(null);
    } else {
      setActionError("Failed to rename layout.");
    }
  };

  const confirmDelete = async (layoutId: string) => {
    setActionError(null);
    const ok = await onDeleteLayout(layoutId);
    if (ok) {
      setDeletingId(null);
    } else {
      setActionError("Failed to delete layout.");
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-150"
      role="dialog"
      aria-modal="true"
      aria-labelledby="manager-dialog-title"
    >
      <div className="w-full max-w-2xl bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden font-sans text-zinc-100 flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800 bg-zinc-900/50">
          <div className="flex items-center gap-2">
            <FolderKanban className="w-4 h-4 text-cyan-400" />
            <h2 id="manager-dialog-title" className="text-sm font-semibold tracking-tight font-mono text-zinc-100">
              SAVED CHART WORKSPACES ({layouts.length}/50)
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            aria-label="Close manager dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-4 border-b border-zinc-800/80 bg-zinc-900/20">
          <div className="relative">
            <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search workspaces by name..."
              className="w-full pl-9 pr-4 py-1.5 bg-zinc-900 border border-zinc-800 rounded text-xs text-zinc-100 placeholder:text-zinc-500 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
          {actionError && (
            <div className="mt-2 p-2 rounded bg-red-950/40 border border-red-800/60 text-xs text-red-300 flex items-center gap-2">
              <AlertCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
              <span>{actionError}</span>
            </div>
          )}
        </div>

        {/* Layouts List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {filtered.length === 0 ? (
            <div className="py-12 text-center text-zinc-500 font-mono text-xs">
              {layouts.length === 0
                ? "No saved layouts found. Save your current chart workspace to begin."
                : "No layouts match your search criteria."}
            </div>
          ) : (
            filtered.map((layout) => {
              const isCurrent = layout.id === currentLayoutId;
              const isEditing = layout.id === editingId;
              const isDeleting = layout.id === deletingId;

              return (
                <div
                  key={layout.id}
                  className={`p-3 rounded border transition-colors flex items-center justify-between gap-3 ${
                    isCurrent
                      ? "bg-cyan-950/20 border-cyan-800/60"
                      : "bg-zinc-900/60 border-zinc-800/80 hover:border-zinc-700"
                  }`}
                >
                  {/* Left: Info or Inline Rename */}
                  <div className="min-w-0 flex-1">
                    {isEditing ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          maxLength={100}
                          autoFocus
                          className="px-2 py-1 bg-zinc-950 border border-cyan-500 rounded text-xs font-mono text-zinc-100 focus:outline-none flex-1"
                        />
                        <button
                          onClick={() => handleSaveRename(layout.id)}
                          className="p-1 rounded bg-cyan-600 text-black hover:bg-cyan-500"
                          title="Save Name"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="p-1 rounded bg-zinc-800 text-zinc-300 hover:bg-zinc-700"
                          title="Cancel"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ) : (
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-semibold font-mono text-zinc-200">
                            {layout.name}
                          </span>
                          {layout.is_default && (
                            <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-amber-500/10 border border-amber-500/30 text-amber-300 flex items-center gap-0.5">
                              <Star className="w-2.5 h-2.5 fill-amber-400" />
                              <span>DEFAULT</span>
                            </span>
                          )}
                          {isCurrent && (
                            <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                              ACTIVE
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-3 mt-1 text-[11px] font-mono text-zinc-500">
                          <span className="flex items-center gap-1">
                            <Layers className="w-3 h-3 text-zinc-400" />
                            <span>
                              {layout.layout_type} ({layout.chart_count} charts)
                            </span>
                          </span>
                          <span>Rev {layout.revision}</span>
                          <span>
                            {new Date(layout.updated_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Right: Actions or Delete Confirmation */}
                  <div className="flex items-center gap-1 shrink-0">
                    {isDeleting ? (
                      <div className="flex items-center gap-2 bg-red-950/40 border border-red-800 px-2.5 py-1 rounded text-xs font-mono">
                        <span className="text-red-300 text-[11px]">Delete?</span>
                        <button
                          onClick={() => confirmDelete(layout.id)}
                          className="px-2 py-0.5 rounded bg-red-600 text-white hover:bg-red-500 text-[11px] font-semibold"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => setDeletingId(null)}
                          className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 hover:bg-zinc-700 text-[11px]"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => {
                            onOpenLayout(layout.id);
                            onClose();
                          }}
                          className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-mono font-medium transition-colors border border-zinc-700/80"
                          title="Open workspace"
                        >
                          Open
                        </button>

                        <button
                          onClick={() => onSetDefaultLayout(layout.id, !layout.is_default)}
                          className={`p-1.5 rounded transition-colors ${
                            layout.is_default
                              ? "text-amber-400 hover:bg-amber-950/40"
                              : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800"
                          }`}
                          title={layout.is_default ? "Remove default" : "Set as default"}
                        >
                          <Star className={`w-3.5 h-3.5 ${layout.is_default ? "fill-amber-400" : ""}`} />
                        </button>

                        <button
                          onClick={() => startRename(layout)}
                          className="p-1.5 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
                          title="Rename layout"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>

                        <button
                          onClick={() => onDuplicateLayout(layout.id)}
                          className="p-1.5 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
                          title="Duplicate layout"
                        >
                          <Copy className="w-3.5 h-3.5" />
                        </button>

                        <button
                          onClick={() => onExportLayout(layout.id)}
                          className="p-1.5 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
                          title="Export JSON"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </button>

                        <button
                          onClick={() => setDeletingId(layout.id)}
                          className="p-1.5 rounded text-zinc-500 hover:text-red-400 hover:bg-red-950/40 transition-colors"
                          title="Delete layout"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-zinc-800 bg-zinc-900/50 flex justify-between items-center text-xs font-mono text-zinc-500">
          <span>Max 50 persistent workspaces per user</span>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
