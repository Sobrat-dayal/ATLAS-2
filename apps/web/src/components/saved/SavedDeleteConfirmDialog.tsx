"use client";

import { AlertTriangle, Trash2, X } from "lucide-react";
import { Button } from "@/design-system";
import { SavedItem } from "@/lib/saved/types";

interface SavedDeleteConfirmDialogProps {
  isOpen: boolean;
  item: SavedItem | null;
  bulkCount: number;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

export function SavedDeleteConfirmDialog({
  isOpen,
  item,
  bulkCount,
  onClose,
  onConfirm,
}: SavedDeleteConfirmDialogProps) {
  if (!isOpen) return null;

  const isBulk = !item && bulkCount > 0;
  const targetLabel = item
    ? `"${item.display_title}"`
    : `${bulkCount} selected saved items`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in">
      <div className="w-full max-w-sm bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b border-atlas-border-default bg-atlas-surface-2 text-rose-400">
          <div className="flex items-center gap-2">
            <Trash2 className="w-4 h-4" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Remove Saved Reference
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-atlas-text-muted hover:text-atlas-text-primary rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 flex flex-col gap-3 text-xs">
          <div className="flex items-start gap-2.5 p-2 rounded-sm bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[11px]">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>
              This will remove {targetLabel} from your personal library.
              The underlying canonical resource (instrument, portfolio, or report) will <strong>not</strong> be modified or deleted.
            </span>
          </div>

          <p className="text-atlas-text-muted text-[11px]">
            Soft-deleted bookmarks can be restored at any time via the API or support tools within the retention window.
          </p>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-atlas-border-default mt-1">
            <Button variant="ghost" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="danger" size="sm" onClick={onConfirm}>
              Confirm Remove
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

