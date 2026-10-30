"use client";

import { useState } from "react";
import {
  CheckSquare,
  FolderPlus,
  Pin,
  Star,
  Tag,
  Trash2,
  X,
} from "lucide-react";
import { Button } from "@/design-system";
import { SavedBulkActionType, SavedCollection } from "@/lib/saved/types";

interface SavedBulkToolbarProps {
  selectedCount: number;
  collections: SavedCollection[];
  onBulkAction: (action: SavedBulkActionType, collectionId?: string, tagName?: string) => void;
  onClearSelection: () => void;
}

export function SavedBulkToolbar({
  selectedCount,
  collections,
  onBulkAction,
  onClearSelection,
}: SavedBulkToolbarProps) {
  const [showColPicker, setShowColPicker] = useState(false);
  const [showTagPrompt, setShowTagPrompt] = useState(false);
  const [tagInput, setTagInput] = useState("");

  if (selectedCount === 0) return null;

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-2 bg-atlas-surface-2 border-b border-atlas-border-focus text-xs text-atlas-text-primary animate-in fade-in slide-in-from-top-1 shrink-0">
      <div className="flex items-center gap-2">
        <CheckSquare className="w-4 h-4 text-blue-400" />
        <span className="font-medium font-mono">{selectedCount}</span>
        <span className="text-atlas-text-muted">selected</span>
      </div>

      <div className="flex items-center gap-1.5 flex-wrap">
        <Button
          variant="secondary"
          size="xs"
          onClick={() => onBulkAction("FAVORITE")}
          className="text-xs h-7 flex items-center gap-1"
        >
          <Star className="w-3 h-3 text-amber-400 fill-amber-400/20" />
          Favorite
        </Button>

        <Button
          variant="secondary"
          size="xs"
          onClick={() => onBulkAction("PIN")}
          className="text-xs h-7 flex items-center gap-1"
        >
          <Pin className="w-3 h-3 text-purple-400" />
          Pin
        </Button>

        {/* Add to Collection dropdown */}
        <div className="relative">
          <Button
            variant="secondary"
            size="xs"
            onClick={() => setShowColPicker(!showColPicker)}
            className="text-xs h-7 flex items-center gap-1"
          >
            <FolderPlus className="w-3 h-3 text-blue-400" />
            Add to Collection
          </Button>

          {showColPicker && (
            <div className="absolute right-0 top-8 z-30 w-48 bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-xl p-1">
              <div className="text-[10px] uppercase font-semibold text-atlas-text-muted px-2 py-1">
                Select Collection
              </div>
              <div className="flex flex-col gap-0.5 max-h-40 overflow-y-auto">
                {collections.length === 0 ? (
                  <div className="text-[11px] text-atlas-text-muted px-2 py-1 italic">No collections</div>
                ) : (
                  collections.map((col) => (
                    <button
                      key={col.collection_id}
                      type="button"
                      onClick={() => {
                        onBulkAction("ADD_TO_COLLECTION", col.collection_id);
                        setShowColPicker(false);
                      }}
                      className="text-left text-xs px-2 py-1 rounded-sm text-atlas-text-primary hover:bg-atlas-surface-2 truncate"
                    >
                      {col.name}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Tag dialog prompt */}
        {showTagPrompt ? (
          <div className="flex items-center gap-1">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              placeholder="Tag name..."
              className="bg-atlas-surface-1 text-xs px-2 py-1 h-7 border border-atlas-border-default rounded-sm focus:outline-none focus:border-atlas-border-focus"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === "Enter" && tagInput.trim()) {
                  onBulkAction("ADD_TAG", undefined, tagInput.trim());
                  setShowTagPrompt(false);
                  setTagInput("");
                }
              }}
            />
            <Button
              variant="primary"
              size="xs"
              className="h-7 text-xs px-2"
              onClick={() => {
                if (tagInput.trim()) {
                  onBulkAction("ADD_TAG", undefined, tagInput.trim());
                  setShowTagPrompt(false);
                  setTagInput("");
                }
              }}
            >
              Apply
            </Button>
            <button
              type="button"
              onClick={() => setShowTagPrompt(false)}
              className="p-1 text-atlas-text-muted hover:text-atlas-text-primary"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <Button
            variant="secondary"
            size="xs"
            onClick={() => setShowTagPrompt(true)}
            className="text-xs h-7 flex items-center gap-1"
          >
            <Tag className="w-3 h-3 text-emerald-400" />
            Add Tag
          </Button>
        )}

        <Button
          variant="danger"
          size="xs"
          onClick={() => onBulkAction("DELETE")}
          className="text-xs h-7 flex items-center gap-1"
        >
          <Trash2 className="w-3 h-3" />
          Delete
        </Button>

        <button
          type="button"
          onClick={onClearSelection}
          className="text-xs text-atlas-text-muted hover:text-atlas-text-primary p-1 ml-1"
          title="Clear Selection"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
