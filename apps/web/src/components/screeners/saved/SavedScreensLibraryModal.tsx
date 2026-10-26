"use client";

import React, { useEffect, useState } from "react";
import {
  Bookmark,
  Calendar,
  Copy,
  FolderOpen,
  Layers,
  ListFilter,
  Loader2,
  Play,
  RotateCw,
  Search,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import { SavedScreener } from "@/lib/screeners/types";
import {
  deleteSavedScreener,
  duplicateSavedScreener,
  fetchSavedScreeners,
} from "@/lib/screeners/api";

interface SavedScreensLibraryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoadScreen: (screen: SavedScreener) => void;
  onOpenSaveDialog: () => void;
  currentScreenId?: string | null;
}

export function SavedScreensLibraryModal({
  isOpen,
  onClose,
  onLoadScreen,
  onOpenSaveDialog,
  currentScreenId,
}: SavedScreensLibraryModalProps) {
  const [screens, setScreens] = useState<SavedScreener[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadScreens = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSavedScreeners(undefined, 1, 100);
      setScreens(data.items);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load saved screens.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadScreens();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const filteredScreens = screens.filter((s) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      s.name.toLowerCase().includes(q) ||
      (s.description && s.description.toLowerCase().includes(q)) ||
      s.universe.universe_id.toLowerCase().includes(q)
    );
  });

  const handleDuplicate = async (screenId: string) => {
    setActionLoadingId(screenId);
    try {
      await duplicateSavedScreener(screenId);
      await loadScreens();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to duplicate screen.";
      setError(msg);
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDelete = async (screenId: string) => {
    setActionLoadingId(screenId);
    try {
      await deleteSavedScreener(screenId);
      setDeleteConfirmId(null);
      await loadScreens();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete screen.";
      setError(msg);
    } finally {
      setActionLoadingId(null);
    }
  };

  const formatDate = (isoString?: string | null) => {
    if (!isoString) return "Never";
    const d = new Date(isoString);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
      <div className="flex h-[80vh] w-full max-w-4xl flex-col rounded-lg border border-border bg-card shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/70 px-6 py-4 bg-muted/30">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary border border-primary/20">
              <FolderOpen className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-foreground">
                Saved Screener Strategies
              </h2>
              <p className="text-xs text-muted-foreground">
                Institutional Reusable Queries, Multi-Factor Rules, Ranking & Display Configurations
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onOpenSaveDialog}
              className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <Bookmark className="h-3.5 w-3.5" />
              <span>Save Current Screen</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
              aria-label="Close"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Toolbar & Search */}
        <div className="flex items-center justify-between gap-3 border-b border-border/50 bg-background px-6 py-2.5">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search saved screens by name, description, universe..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 w-full rounded-md border border-border/80 bg-background pl-8 pr-3 text-xs placeholder:text-muted-foreground/60 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>
              {filteredScreens.length} {filteredScreens.length === 1 ? "screen" : "screens"} available
            </span>
            <button
              type="button"
              onClick={loadScreens}
              disabled={loading}
              className="flex h-7 items-center gap-1 rounded border border-border/70 px-2 hover:bg-muted transition-colors disabled:opacity-50"
              title="Refresh saved screens"
            >
              <RotateCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        {/* Error Notice */}
        {error && (
          <div className="px-6 py-2 bg-destructive/10 border-b border-destructive/20 text-xs text-destructive flex items-center justify-between">
            <span>{error}</span>
            <button type="button" onClick={() => setError(null)} className="text-[11px] underline">
              Dismiss
            </button>
          </div>
        )}

        {/* List Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {loading && screens.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-muted-foreground gap-2">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
              <span className="text-xs">Loading institutional saved screens...</span>
            </div>
          ) : filteredScreens.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-center text-muted-foreground p-6 rounded-lg border border-dashed border-border/80">
              <FolderOpen className="h-8 w-8 text-muted-foreground/40 mb-2" />
              <p className="text-sm font-medium text-foreground">No saved screener strategies found</p>
              <p className="text-xs text-muted-foreground mt-1 max-w-sm">
                Save your active universe, filters, sorting criteria, and quantitative rankings to run reproducible institutional screens anytime.
              </p>
              <button
                type="button"
                onClick={onOpenSaveDialog}
                className="mt-4 flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                <Bookmark className="h-3.5 w-3.5" />
                <span>Save Current Screen Now</span>
              </button>
            </div>
          ) : (
            filteredScreens.map((screen) => {
              const isCurrent = screen.saved_screen_id === currentScreenId;
              const isActing = actionLoadingId === screen.saved_screen_id;
              const isDeleting = deleteConfirmId === screen.saved_screen_id;

              return (
                <div
                  key={screen.saved_screen_id}
                  className={`flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-lg border transition-all ${
                    isCurrent
                      ? "border-primary/50 bg-primary/5 shadow-sm"
                      : "border-border/70 bg-card hover:border-border hover:bg-muted/20"
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-sm text-foreground truncate">
                        {screen.name}
                      </span>
                      {isCurrent && (
                        <span className="rounded bg-primary/15 text-primary text-[10px] font-medium px-2 py-0.5 border border-primary/20">
                          Active Screen
                        </span>
                      )}
                      <span className="font-mono text-[10px] text-muted-foreground/70 bg-muted px-1.5 py-0.5 rounded border border-border/40">
                        rev:{screen.revision} · v{screen.query_schema_version}
                      </span>
                    </div>

                    {screen.description && (
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
                        {screen.description}
                      </p>
                    )}

                    <div className="flex flex-wrap items-center gap-3 mt-2 text-[11px] text-muted-foreground font-mono">
                      <span className="flex items-center gap-1 bg-muted/60 px-2 py-0.5 rounded border border-border/50">
                        <Layers className="h-3 w-3 text-muted-foreground/70" />
                        <span className="font-medium text-foreground">{screen.universe.universe_id}</span>
                      </span>

                      <span className="flex items-center gap-1 bg-muted/60 px-2 py-0.5 rounded border border-border/50">
                        <ListFilter className="h-3 w-3 text-muted-foreground/70" />
                        <span>{screen.filters.length} {screen.filters.length === 1 ? "filter" : "filters"}</span>
                      </span>

                      {screen.ranking && (
                        <span className="flex items-center gap-1 bg-primary/10 text-primary px-2 py-0.5 rounded border border-primary/20 font-sans font-medium">
                          <Sparkles className="h-3 w-3" />
                          <span>Rank: {screen.ranking.mode}</span>
                        </span>
                      )}

                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3 opacity-60" />
                        <span>Updated: {formatDate(screen.updated_at)}</span>
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                    {isDeleting ? (
                      <div className="flex items-center gap-1.5 bg-destructive/10 p-1 rounded border border-destructive/20 animate-in fade-in">
                        <span className="text-[11px] text-destructive px-1 font-medium">Delete screen?</span>
                        <button
                          type="button"
                          onClick={() => handleDelete(screen.saved_screen_id)}
                          disabled={isActing}
                          className="rounded bg-destructive px-2 py-1 text-[11px] font-medium text-destructive-foreground hover:bg-destructive/90"
                        >
                          Confirm
                        </button>
                        <button
                          type="button"
                          onClick={() => setDeleteConfirmId(null)}
                          className="rounded bg-muted px-2 py-1 text-[11px] font-medium text-foreground hover:bg-muted/80"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          type="button"
                          onClick={() => {
                            onLoadScreen(screen);
                            onClose();
                          }}
                          className="flex items-center gap-1 rounded-md bg-primary/10 hover:bg-primary/20 text-primary px-3 py-1.5 text-xs font-medium border border-primary/20 transition-colors"
                          title="Open & run this saved screen"
                        >
                          <Play className="h-3 w-3" />
                          <span>Open</span>
                        </button>

                        <button
                          type="button"
                          onClick={() => handleDuplicate(screen.saved_screen_id)}
                          disabled={isActing}
                          className="p-1.5 rounded-md border border-border/80 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors disabled:opacity-50"
                          title="Duplicate Screen"
                          aria-label="Duplicate"
                        >
                          <Copy className="h-3.5 w-3.5" />
                        </button>

                        <button
                          type="button"
                          onClick={() => setDeleteConfirmId(screen.saved_screen_id)}
                          disabled={isActing}
                          className="p-1.5 rounded-md border border-border/80 text-muted-foreground hover:bg-destructive/10 hover:border-destructive/30 hover:text-destructive transition-colors disabled:opacity-50"
                          title="Delete Screen"
                          aria-label="Delete"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
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
        <div className="flex items-center justify-between border-t border-border/70 px-6 py-3 bg-muted/20 text-xs text-muted-foreground">
          <span>Max 100 persistent screens per user · Tenant isolated with revision protection</span>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-border bg-background px-3 py-1 text-xs font-medium hover:bg-muted transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
