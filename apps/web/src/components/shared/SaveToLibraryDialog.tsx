"use client";

import { useEffect, useState } from "react";
import { Bookmark, Check, FolderPlus, Star, Tag, X } from "lucide-react";
import { Button } from "@/design-system";
import { listCollections, saveItem } from "@/lib/saved/api";
import { formatTargetTypeLabel } from "@/lib/saved/deepLinks";
import { SavedCollection, SavedTargetType } from "@/lib/saved/types";

interface SaveToLibraryDialogProps {
  isOpen: boolean;
  targetType: SavedTargetType;
  targetId: string;
  defaultTitle?: string;
  targetRevisionId?: string;
  viewConfigurationId?: string;
  onClose: () => void;
  onSuccess?: () => void;
}

export function SaveToLibraryDialog({
  isOpen,
  targetType,
  targetId,
  defaultTitle,
  targetRevisionId,
  viewConfigurationId,
  onClose,
  onSuccess,
}: SaveToLibraryDialogProps) {
  const [titleOverride, setTitleOverride] = useState("");
  const [userNote, setUserNote] = useState("");
  const [favorite, setFavorite] = useState(false);
  const [tagsInput, setTagsInput] = useState("");
  const [selectedColIds, setSelectedColIds] = useState<string[]>([]);
  const [availableCollections, setAvailableCollections] = useState<SavedCollection[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setTitleOverride(defaultTitle || "");
      setUserNote("");
      setFavorite(false);
      setTagsInput("");
      setSelectedColIds([]);
      setErrorMessage(null);

      listCollections()
        .then((cols) => setAvailableCollections(cols))
        .catch(() => {});
    }
  }, [isOpen, defaultTitle]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const tags = tagsInput
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);

      await saveItem({
        target_type: targetType,
        target_id: targetId,
        target_revision_id: targetRevisionId,
        display_title_override: titleOverride.trim() || undefined,
        user_note: userNote.trim() || undefined,
        favorite,
        collection_ids: selectedColIds,
        tags,
        view_configuration_id: viewConfigurationId,
      });

      onSuccess?.();
      onClose();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to save item.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleCollection = (cid: string) => {
    setSelectedColIds((prev) =>
      prev.includes(cid) ? prev.filter((id) => id !== cid) : [...prev, cid]
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in">
      <div className="w-full max-w-md bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-blue-400" />
            <h3 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
              Save {formatTargetTypeLabel(targetType)} to Library
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

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-4 flex flex-col gap-3 text-xs">
          {errorMessage && (
            <div className="p-2 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded text-xs">
              {errorMessage}
            </div>
          )}

          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-semibold text-atlas-text-muted">
              Display Title
            </label>
            <input
              type="text"
              value={titleOverride}
              onChange={(e) => setTitleOverride(e.target.value)}
              placeholder="Custom title (optional)..."
              maxLength={200}
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-border-focus focus:outline-none"
            />
            <span className="text-[10px] text-atlas-text-muted font-mono truncate">
              Target ID: {targetId}
            </span>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-semibold text-atlas-text-muted">
              Private Note
            </label>
            <textarea
              value={userNote}
              onChange={(e) => setUserNote(e.target.value)}
              placeholder="Investment thesis, key observations, or reference notes..."
              rows={3}
              maxLength={5000}
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm p-2 text-xs text-atlas-text-primary focus:border-atlas-border-focus focus:outline-none resize-none"
            />
          </div>

          {/* Collections selection */}
          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-semibold text-atlas-text-muted flex items-center gap-1">
              <FolderPlus className="w-3 h-3 text-blue-400" />
              Add to Collections
            </label>
            <div className="max-h-28 overflow-y-auto border border-atlas-border-default rounded-sm p-1.5 bg-atlas-surface-0 flex flex-col gap-1">
              {availableCollections.length === 0 ? (
                <span className="text-[11px] text-atlas-text-muted italic">No collections available.</span>
              ) : (
                availableCollections.map((col) => {
                  const isChecked = selectedColIds.includes(col.collection_id);
                  return (
                    <label
                      key={col.collection_id}
                      className="flex items-center gap-2 px-1.5 py-1 rounded hover:bg-atlas-surface-1 cursor-pointer text-xs"
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleCollection(col.collection_id)}
                        className="rounded border-atlas-border-default"
                      />
                      <span className="text-atlas-text-primary truncate">{col.name}</span>
                    </label>
                  );
                })
              )}
            </div>
          </div>

          {/* Tags input */}
          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-semibold text-atlas-text-muted flex items-center gap-1">
              <Tag className="w-3 h-3 text-emerald-400" />
              Tags (comma separated)
            </label>
            <input
              type="text"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              placeholder="e.g. Core, LongTerm, HighBeta, Tech"
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-border-focus focus:outline-none"
            />
          </div>

          {/* Favorite Toggle */}
          <label className="flex items-center gap-2 pt-1 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={favorite}
              onChange={(e) => setFavorite(e.target.checked)}
              className="rounded border-atlas-border-default"
            />
            <span className="text-xs text-atlas-text-primary flex items-center gap-1">
              <Star className={`w-3.5 h-3.5 ${favorite ? "text-amber-400 fill-amber-400" : "text-atlas-text-muted"}`} />
              Add to Favorites
            </span>
          </label>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-atlas-border-default mt-2">
            <Button variant="ghost" size="xs" type="button" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button variant="primary" size="xs" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : "Save to Library"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
