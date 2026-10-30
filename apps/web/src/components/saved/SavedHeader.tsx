"use client";

import { Bookmark, FolderPlus, RefreshCw, Star, Tag, Clock, Folder } from "lucide-react";
import { Badge, Button, IconButton } from "@/design-system";
import { SavedLibrarySummary } from "@/lib/saved/types";

interface SavedHeaderProps {
  summary: SavedLibrarySummary | null;
  isLoading: boolean;
  onRefresh: () => void;
  onCreateCollection: () => void;
}

export function SavedHeader({
  summary,
  isLoading,
  onRefresh,
  onCreateCollection,
}: SavedHeaderProps) {
  return (
    <div className="flex flex-col gap-3 pb-3 border-b border-atlas-border-default shrink-0">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-atlas-text-primary" />
            <h1 className="text-xl font-bold tracking-tight text-atlas-text-primary">
              SAVED LIBRARY
            </h1>
            <Badge variant="outline" className="text-xs uppercase font-mono tracking-wider">
              Cross-Module Persistence
            </Badge>
          </div>
          <p className="text-xs text-atlas-text-muted mt-0.5">
            Institutional repository for bookmarked instruments, research reports, portfolios, risk calculations, and analytical view configurations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <IconButton
            aria-label="Refresh library"
            variant="ghost"
            size="xs"
            onClick={onRefresh}
            className={isLoading ? "animate-spin" : ""}
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </IconButton>
          <Button
            variant="primary"
            size="xs"
            onClick={onCreateCollection}
            className="flex items-center gap-1.5 text-xs font-medium"
          >
            <FolderPlus className="w-3.5 h-3.5" />
            New Collection
          </Button>
        </div>
      </div>

      {/* KPI Summary Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-sm bg-atlas-surface-1 border border-atlas-border-default">
          <Bookmark className="w-3.5 h-3.5 text-atlas-text-muted" />
          <div className="flex flex-col">
            <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider">Saved Items</span>
            <span className="text-sm font-semibold font-mono text-atlas-text-primary">
              {summary ? summary.total_saved_items : 0}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-sm bg-atlas-surface-1 border border-atlas-border-default">
          <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400/20" />
          <div className="flex flex-col">
            <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider">Favorites</span>
            <span className="text-sm font-semibold font-mono text-atlas-text-primary">
              {summary ? summary.favorite_count : 0}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-sm bg-atlas-surface-1 border border-atlas-border-default">
          <Folder className="w-3.5 h-3.5 text-blue-400" />
          <div className="flex flex-col">
            <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider">Collections</span>
            <span className="text-sm font-semibold font-mono text-atlas-text-primary">
              {summary ? summary.collection_count : 0}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-sm bg-atlas-surface-1 border border-atlas-border-default">
          <Tag className="w-3.5 h-3.5 text-emerald-400" />
          <div className="flex flex-col">
            <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider">Active Tags</span>
            <span className="text-sm font-semibold font-mono text-atlas-text-primary">
              {summary ? summary.tag_count : 0}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-sm bg-atlas-surface-1 border border-atlas-border-default">
          <Clock className="w-3.5 h-3.5 text-purple-400" />
          <div className="flex flex-col">
            <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider">Recent (7d)</span>
            <span className="text-sm font-semibold font-mono text-atlas-text-primary">
              {summary ? summary.recent_saves_count : 0}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
