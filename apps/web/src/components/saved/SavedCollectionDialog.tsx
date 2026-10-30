"use client";

import { useEffect, useState } from "react";
import { Folder, X } from "lucide-react";
import { Button } from "@/design-system";
import { SavedCollection } from "@/lib/saved/types";

interface SavedCollectionDialogProps {
  isOpen: boolean;
  collection: SavedCollection | null; // null if creating new
  allCollections: SavedCollection[];
  onClose: () => void;
  onSubmit: (data: {
    name: string;
    description?: string;
    parent_collection_id?: string | null;
  }) => Promise<void>;
}

export function SavedCollectionDialog({
  isOpen,
  collection,
  allCollections,
  onClose,
  onSubmit,
}: SavedCollectionDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [parentId, setParentId] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (collection) {
      setName(collection.name);
      setDescription(collection.description || "");
      setParentId(collection.parent_collection_id || "");
    } else {
      setName("");
      setDescription("");
      setParentId("");
    }
    setErrorMessage(null);
  }, [collection, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setErrorMessage("Collection name is required.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      await onSubmit({
        name: name.trim(),
        description: description.trim() || undefined,
        parent_collection_id: parentId || null,
      });
      onClose();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to save collection.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Prevent selecting self as parent
  const eligibleParents = allCollections.filter(
    (c) => !collection || c.collection_id !== collection.collection_id
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in">
      <div className="w-full max-w-md bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-2xl overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-3 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Folder className="w-4 h-4 text-blue-400" />
            <h3 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
              {collection ? "Edit Collection" : "Create New Collection"}
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
              Collection Name <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Q4 Earnings Watch, Sovereign Curves, Tech Thesis..."
              maxLength={100}
              required
              autoFocus
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted/60 focus:border-atlas-border-focus focus:outline-none"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-semibold text-atlas-text-muted">
              Parent Collection (Optional Hierarchy)
            </label>
            <select
              value={parentId}
              onChange={(e) => setParentId(e.target.value)}
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-border-focus focus:outline-none"
            >
              <option value="">None (Top-Level Collection)</option>
              {eligibleParents.map((c) => (
                <option key={c.collection_id} value={c.collection_id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-semibold text-atlas-text-muted">
              Description (Optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief summary of research or portfolio objective for this folder..."
              rows={3}
              maxLength={500}
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm p-2 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted/60 focus:border-atlas-border-focus focus:outline-none resize-none"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-atlas-border-default mt-2">
            <Button variant="ghost" size="xs" type="button" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button variant="primary" size="xs" type="submit" disabled={isSubmitting || !name.trim()}>
              {isSubmitting ? "Saving..." : collection ? "Save Changes" : "Create Collection"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
