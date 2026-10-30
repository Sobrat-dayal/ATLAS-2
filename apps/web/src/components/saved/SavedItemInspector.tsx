"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  Clock,
  ExternalLink,
  FolderPlus,
  Pin,
  Save,
  Shield,
  Star,
  Tag as TagIcon,
  Trash2,
  X,
} from "lucide-react";
import { Badge, Button } from "@/design-system";
import {
  formatTargetTypeLabel,
  getAvailabilityBadgeVariant,
  getTargetTypeBadgeVariant,
} from "@/lib/saved/deepLinks";
import { SavedCollection, SavedItem } from "@/lib/saved/types";

interface SavedItemInspectorProps {
  item: SavedItem | null;
  collections: SavedCollection[];
  onClose: () => void;
  onToggleFavorite: (item: SavedItem) => void;
  onTogglePin: (item: SavedItem) => void;
  onUpdateNote: (saved_item_id: string, note: string) => Promise<void>;
  onAssignTag: (saved_item_id: string, tagName: string) => Promise<void>;
  onRemoveTag: (saved_item_id: string, tagId: string) => Promise<void>;
  onAddItemToCollection: (collection_id: string, saved_item_id: string) => Promise<void>;
  onRemoveItemFromCollection: (collection_id: string, saved_item_id: string) => Promise<void>;
  onDeleteItem: (item: SavedItem) => void;
}

export function SavedItemInspector({
  item,
  collections,
  onClose,
  onToggleFavorite,
  onTogglePin,
  onUpdateNote,
  onAssignTag,
  onRemoveTag,
  onAddItemToCollection,
  onRemoveItemFromCollection,
  onDeleteItem,
}: SavedItemInspectorProps) {
  const [noteText, setNoteText] = useState("");
  const [isSavingNote, setIsSavingNote] = useState(false);
  const [newTagInput, setNewTagInput] = useState("");
  const [selectedColToAdd, setSelectedColToAdd] = useState("");

  useEffect(() => {
    if (item) {
      setNoteText(item.user_note || "");
    }
  }, [item]);

  if (!item) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center text-atlas-text-muted bg-atlas-surface-1 border-l border-atlas-border-default">
        <Shield className="w-8 h-8 text-atlas-text-muted/40 mb-2" />
        <p className="text-xs font-medium text-atlas-text-primary">Resource Inspector</p>
        <p className="text-[11px] text-atlas-text-muted mt-0.5">Select an item from the library to inspect details and edit notes.</p>
      </div>
    );
  }

  const handleSaveNote = async () => {
    setIsSavingNote(true);
    try {
      await onUpdateNote(item.saved_item_id, noteText);
    } finally {
      setIsSavingNote(false);
    }
  };

  const handleAddTag = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newTagInput.trim()) {
      await onAssignTag(item.saved_item_id, newTagInput.trim());
      setNewTagInput("");
    }
  };

  const handleAddCollection = async () => {
    if (selectedColToAdd) {
      await onAddItemToCollection(selectedColToAdd, item.saved_item_id);
      setSelectedColToAdd("");
    }
  };

  return (
    <div className="h-full flex flex-col bg-atlas-surface-1 border-l border-atlas-border-default overflow-y-auto">
      {/* Header */}
      <div className="p-3 border-b border-atlas-border-default flex items-start justify-between gap-2 shrink-0">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-1">
            <Badge variant={getTargetTypeBadgeVariant(item.target_type)} className="text-[9px]">
              {formatTargetTypeLabel(item.target_type)}
            </Badge>
            <Badge variant={getAvailabilityBadgeVariant(item.availability_status)} className="text-[9px]">
              {item.availability_status.replace(/_/g, " ")}
            </Badge>
          </div>
          <h2 className="text-xs font-bold text-atlas-text-primary truncate">
            {item.display_title}
          </h2>
          <p className="text-[10px] text-atlas-text-muted font-mono truncate">
            {item.canonical_title}
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="p-1 text-atlas-text-muted hover:text-atlas-text-primary rounded shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Warnings Banner if any */}
      {item.warnings && item.warnings.length > 0 && (
        <div className="p-2.5 bg-amber-500/10 border-b border-amber-500/20 text-amber-400 text-xs flex items-start gap-2 shrink-0">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <div className="flex flex-col gap-0.5">
            {item.warnings.map((w) => (
              <span key={w} className="text-[11px] leading-tight">
                {w}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Content Sections */}
      <div className="p-3 flex flex-col gap-4 flex-1">
        {/* Open Action */}
        <Link
          href={item.safe_deep_link}
          className="flex items-center justify-center gap-1.5 w-full py-1.5 px-3 bg-blue-600 hover:bg-blue-500 text-white rounded-sm text-xs font-medium transition-colors shadow-sm"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          Open in {item.target_module.toUpperCase()}
        </Link>

        {/* Canonical Reference Metadata */}
        <div className="flex flex-col gap-1.5 p-2 bg-atlas-surface-0 rounded-sm border border-atlas-border-default/60 text-xs">
          <div className="text-[10px] uppercase font-semibold text-atlas-text-muted tracking-wider">
            Canonical Identity
          </div>
          <div className="grid grid-cols-2 gap-y-1 gap-x-2 text-[11px]">
            <span className="text-atlas-text-muted">Target ID:</span>
            <span className="font-mono text-atlas-text-primary truncate">{item.target_id}</span>

            <span className="text-atlas-text-muted">Module:</span>
            <span className="font-mono text-atlas-text-primary capitalize">{item.target_module}</span>

            <span className="text-atlas-text-muted">Semantics:</span>
            <span className="font-mono text-atlas-text-primary text-[10px]">{item.semantics}</span>

            {item.target_revision_id && (
              <>
                <span className="text-atlas-text-muted">Revision:</span>
                <span className="font-mono text-atlas-text-primary">{item.target_revision_id}</span>
              </>
            )}

            <span className="text-atlas-text-muted">Saved At:</span>
            <span className="font-mono text-atlas-text-muted text-[10px]">
              {new Date(item.saved_at).toLocaleString()}
            </span>
          </div>
        </div>

        {/* Private Notes Editor */}
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-semibold text-atlas-text-muted tracking-wider">
              Private Note
            </span>
            <span className="text-[10px] text-atlas-text-muted font-mono">{noteText.length} / 5000</span>
          </div>

          <textarea
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            placeholder="Add personal investment thesis, risks, or key takeaway notes..."
            rows={4}
            maxLength={5000}
            className="w-full bg-atlas-surface-0 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted/60 p-2 rounded-sm border border-atlas-border-default focus:border-atlas-border-focus focus:outline-none resize-y"
          />

          <Button
            variant="secondary"
            size="xs"
            onClick={handleSaveNote}
            disabled={isSavingNote || noteText === (item.user_note || "")}
            className="self-end text-xs flex items-center gap-1"
          >
            <Save className="w-3 h-3" />
            {isSavingNote ? "Saving..." : "Save Note"}
          </Button>
        </div>

        {/* Collections Assigner */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] uppercase font-semibold text-atlas-text-muted tracking-wider">
            Collections
          </span>
          <div className="flex flex-wrap gap-1">
            {item.collection_ids.length === 0 ? (
              <span className="text-[11px] text-atlas-text-muted italic">Not in any collection.</span>
            ) : (
              item.collection_ids.map((cid) => {
                const col = collections.find((c) => c.collection_id === cid);
                return (
                  <span
                    key={cid}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-sm bg-atlas-surface-2 text-atlas-text-primary text-[10px] font-mono border border-atlas-border-default"
                  >
                    <span>{col?.name || cid}</span>
                    <button
                      type="button"
                      onClick={() => onRemoveItemFromCollection(cid, item.saved_item_id)}
                      className="text-atlas-text-muted hover:text-rose-400"
                    >
                      <X className="w-2.5 h-2.5" />
                    </button>
                  </span>
                );
              })
            )}
          </div>

          {/* Add to collection dropdown */}
          <div className="flex items-center gap-1 mt-1">
            <select
              value={selectedColToAdd}
              onChange={(e) => setSelectedColToAdd(e.target.value)}
              className="flex-1 bg-atlas-surface-0 text-xs text-atlas-text-primary p-1.5 rounded-sm border border-atlas-border-default focus:outline-none"
            >
              <option value="">Select collection to add...</option>
              {collections
                .filter((c) => !item.collection_ids.includes(c.collection_id))
                .map((c) => (
                  <option key={c.collection_id} value={c.collection_id}>
                    {c.name}
                  </option>
                ))}
            </select>
            <Button
              variant="secondary"
              size="xs"
              onClick={handleAddCollection}
              disabled={!selectedColToAdd}
              className="text-xs"
            >
              <FolderPlus className="w-3 h-3" />
            </Button>
          </div>
        </div>

        {/* Tags Assigner */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] uppercase font-semibold text-atlas-text-muted tracking-wider">
            Tags
          </span>
          <div className="flex flex-wrap gap-1">
            {item.tags.length === 0 ? (
              <span className="text-[11px] text-atlas-text-muted italic">No tags assigned.</span>
            ) : (
              item.tags.map((t) => (
                <span
                  key={t}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-atlas-surface-2 text-atlas-text-primary text-[10px] font-mono border border-atlas-border-default"
                >
                  <TagIcon className="w-2.5 h-2.5 text-atlas-text-muted" />
                  <span>{t}</span>
                </span>
              ))
            )}
          </div>

          <form onSubmit={handleAddTag} className="flex items-center gap-1 mt-1">
            <input
              type="text"
              value={newTagInput}
              onChange={(e) => setNewTagInput(e.target.value)}
              placeholder="Add tag..."
              className="flex-1 bg-atlas-surface-0 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted/60 px-2 py-1.5 rounded-sm border border-atlas-border-default focus:border-atlas-border-focus focus:outline-none"
            />
            <Button variant="secondary" size="xs" type="submit" disabled={!newTagInput.trim()} className="text-xs">
              Add
            </Button>
          </form>
        </div>

        {/* Secondary Toggles & Deletion */}
        <div className="mt-4 pt-3 border-t border-atlas-border-default flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => onToggleFavorite(item)}
              className={`p-1.5 rounded-sm border text-xs flex items-center gap-1 ${
                item.favorite
                  ? "bg-amber-400/10 border-amber-400/30 text-amber-400"
                  : "bg-atlas-surface-0 border-atlas-border-default text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              <Star className={`w-3.5 h-3.5 ${item.favorite ? "fill-amber-400" : ""}`} />
              <span>{item.favorite ? "Favorited" : "Favorite"}</span>
            </button>

            <button
              type="button"
              onClick={() => onTogglePin(item)}
              className={`p-1.5 rounded-sm border text-xs flex items-center gap-1 ${
                item.pinned
                  ? "bg-purple-400/10 border-purple-400/30 text-purple-400"
                  : "bg-atlas-surface-0 border-atlas-border-default text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              <Pin className={`w-3.5 h-3.5 ${item.pinned ? "fill-purple-400/20" : ""}`} />
              <span>{item.pinned ? "Pinned" : "Pin"}</span>
            </button>
          </div>

          <button
            type="button"
            onClick={() => onDeleteItem(item)}
            className="p-1.5 rounded-sm text-xs text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 flex items-center gap-1"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Remove</span>
          </button>
        </div>
      </div>
    </div>
  );
}
