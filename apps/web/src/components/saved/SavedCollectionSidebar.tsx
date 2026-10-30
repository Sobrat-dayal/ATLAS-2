"use client";

import { useState } from "react";
import {
  Bookmark,
  ChevronDown,
  ChevronRight,
  Clock,
  Edit2,
  Folder,
  FolderPlus,
  Star,
  Tag as TagIcon,
  Trash2,
} from "lucide-react";
import { Badge, Button } from "@/design-system";
import { SavedWorkspaceTab } from "@/hooks/saved/useSavedTerminal";
import { SavedCollection, SavedCollectionTree, SavedTag } from "@/lib/saved/types";

interface SavedCollectionSidebarProps {
  activeTab: SavedWorkspaceTab;
  onSelectTab: (tab: SavedWorkspaceTab) => void;
  collections: SavedCollection[];
  collectionTree: SavedCollectionTree[];
  selectedCollectionId: string | null;
  onSelectCollection: (collectionId: string | null) => void;
  tags: SavedTag[];
  selectedTag: string | null;
  onSelectTag: (tagName: string | null) => void;
  onCreateCollection: () => void;
  onEditCollection: (col: SavedCollection) => void;
  onDeleteCollection: (collectionId: string) => void;
}

export function SavedCollectionSidebar({
  activeTab,
  onSelectTab,
  collections,
  collectionTree,
  selectedCollectionId,
  onSelectCollection,
  tags,
  selectedTag,
  onSelectTag,
  onCreateCollection,
  onEditCollection,
  onDeleteCollection,
}: SavedCollectionSidebarProps) {
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedNodes((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const renderTreeNode = (node: SavedCollectionTree, depth = 0) => {
    const isSelected = selectedCollectionId === node.collection.collection_id;
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = !!expandedNodes[node.collection.collection_id];

    return (
      <div key={node.collection.collection_id} className="flex flex-col">
        <div
          role="button"
          tabIndex={0}
          onClick={() => {
            onSelectCollection(isSelected ? null : node.collection.collection_id);
            if (activeTab !== "collections") onSelectTab("collections");
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              onSelectCollection(isSelected ? null : node.collection.collection_id);
            }
          }}
          className={`group flex items-center justify-between px-2 py-1.5 text-xs rounded-sm cursor-pointer transition-colors ${
            isSelected
              ? "bg-atlas-surface-2 text-atlas-text-primary font-medium"
              : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-1"
          }`}
          style={{ paddingLeft: `${8 + depth * 14}px` }}
        >
          <div className="flex items-center gap-1.5 truncate">
            {hasChildren ? (
              <span
                onClick={(e) => toggleExpand(node.collection.collection_id, e)}
                className="p-0.5 rounded-sm hover:bg-atlas-surface-2 text-atlas-text-muted"
              >
                {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
              </span>
            ) : (
              <span className="w-3" />
            )}
            <Folder className={`w-3.5 h-3.5 shrink-0 ${isSelected ? "text-blue-400" : "text-atlas-text-muted"}`} />
            <span className="truncate">{node.collection.name}</span>
          </div>

          <div className="flex items-center gap-1 shrink-0">
            <span className="text-[10px] font-mono text-atlas-text-muted/70 mr-1">
              {node.collection.item_count}
            </span>
            <div className="hidden group-hover:flex items-center gap-0.5">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onEditCollection(node.collection);
                }}
                className="p-0.5 text-atlas-text-muted hover:text-atlas-text-primary rounded"
                title="Edit Collection"
              >
                <Edit2 className="w-3 h-3" />
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteCollection(node.collection.collection_id);
                }}
                className="p-0.5 text-atlas-text-muted hover:text-rose-400 rounded"
                title="Delete Collection"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>

        {hasChildren && isExpanded && (
          <div className="flex flex-col">
            {node.children.map((child) => renderTreeNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col bg-atlas-surface-1 border-r border-atlas-border-default select-none overflow-y-auto">
      {/* Primary Views */}
      <div className="p-2 flex flex-col gap-0.5 border-b border-atlas-border-default">
        <button
          type="button"
          onClick={() => {
            onSelectTab("all");
            onSelectCollection(null);
            onSelectTag(null);
          }}
          className={`flex items-center justify-between w-full px-2.5 py-1.5 text-xs rounded-sm transition-colors ${
            activeTab === "all" && !selectedCollectionId && !selectedTag
              ? "bg-atlas-surface-2 text-atlas-text-primary font-medium"
              : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-1"
          }`}
        >
          <div className="flex items-center gap-2">
            <Bookmark className="w-3.5 h-3.5 text-atlas-text-primary" />
            <span>All Saved</span>
          </div>
        </button>

        <button
          type="button"
          onClick={() => {
            onSelectTab("favorites");
            onSelectCollection(null);
            onSelectTag(null);
          }}
          className={`flex items-center justify-between w-full px-2.5 py-1.5 text-xs rounded-sm transition-colors ${
            activeTab === "favorites"
              ? "bg-atlas-surface-2 text-atlas-text-primary font-medium"
              : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-1"
          }`}
        >
          <div className="flex items-center gap-2">
            <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400/20" />
            <span>Favorites</span>
          </div>
        </button>

        <button
          type="button"
          onClick={() => {
            onSelectTab("recent");
            onSelectCollection(null);
            onSelectTag(null);
          }}
          className={`flex items-center justify-between w-full px-2.5 py-1.5 text-xs rounded-sm transition-colors ${
            activeTab === "recent"
              ? "bg-atlas-surface-2 text-atlas-text-primary font-medium"
              : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-1"
          }`}
        >
          <div className="flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-purple-400" />
            <span>Recent Saves</span>
          </div>
        </button>
      </div>

      {/* Collections Tree Section */}
      <div className="flex-1 p-2 flex flex-col min-h-[160px]">
        <div className="flex items-center justify-between px-2 py-1 mb-1">
          <span className="text-[10px] uppercase font-semibold tracking-wider text-atlas-text-muted">
            Collections ({collections.length})
          </span>
          <button
            type="button"
            onClick={onCreateCollection}
            className="text-atlas-text-muted hover:text-atlas-text-primary p-0.5 rounded"
            title="Create Collection"
          >
            <FolderPlus className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex flex-col gap-0.5 overflow-y-auto max-h-[300px]">
          {collectionTree.length === 0 ? (
            <div className="px-2 py-3 text-center text-xs text-atlas-text-muted/60 italic">
              No collections yet. Click + to organize items.
            </div>
          ) : (
            collectionTree.map((node) => renderTreeNode(node, 0))
          )}
        </div>

        {/* User Tags Section */}
        <div className="mt-4 pt-3 border-t border-atlas-border-default">
          <div className="flex items-center justify-between px-2 py-1 mb-1.5">
            <span className="text-[10px] uppercase font-semibold tracking-wider text-atlas-text-muted">
              Tags ({tags.length})
            </span>
            {selectedTag && (
              <button
                type="button"
                onClick={() => onSelectTag(null)}
                className="text-[10px] text-blue-400 hover:underline"
              >
                Clear
              </button>
            )}
          </div>

          <div className="flex flex-wrap gap-1 px-1 max-h-[160px] overflow-y-auto">
            {tags.length === 0 ? (
              <div className="px-1 text-xs text-atlas-text-muted/60 italic">No tags created yet.</div>
            ) : (
              tags.map((tag) => {
                const isTagActive = selectedTag === tag.name;
                return (
                  <button
                    key={tag.tag_id}
                    type="button"
                    onClick={() => onSelectTag(isTagActive ? null : tag.name)}
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono border transition-colors ${
                      isTagActive
                        ? "bg-atlas-surface-3 text-atlas-text-primary border-atlas-border-focus font-medium"
                        : "bg-atlas-surface-1 text-atlas-text-muted border-atlas-border-default hover:text-atlas-text-primary"
                    }`}
                  >
                    <TagIcon className="w-2.5 h-2.5" />
                    <span>{tag.name}</span>
                    <span className="opacity-60">({tag.item_count})</span>
                  </button>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

