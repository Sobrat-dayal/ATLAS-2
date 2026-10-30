"use client";

import React, { useState, useEffect } from "react";
import { Bookmark, X, Trash2, ExternalLink, Calendar, Layers, Loader2 } from "lucide-react";
import { UserMapView } from "@/lib/maps/types";
import { listSavedMapViews, deleteMapView } from "@/lib/maps/api";
import { Button } from "@/design-system";

interface AtlasMapViewListModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRestoreView: (view: UserMapView) => void;
  workspaceId?: string;
}

export function AtlasMapViewListModal({
  isOpen,
  onClose,
  onRestoreView,
  workspaceId,
}: AtlasMapViewListModalProps) {
  const [views, setViews] = useState<UserMapView[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadViews = () => {
    setIsLoading(true);
    listSavedMapViews(workspaceId)
      .then((data) => {
        setViews(data);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    if (isOpen) {
      loadViews();
    }
  }, [isOpen, workspaceId]);

  if (!isOpen) return null;

  const handleDelete = async (viewId: string) => {
    try {
      await deleteMapView(viewId);
      setViews((prev) => prev.filter((v) => v.map_view_id !== viewId));
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="flex flex-col w-full max-w-lg bg-atlas-surface-1 border border-atlas-border-default rounded shadow-2xl overflow-hidden font-mono text-xs max-h-[80vh]">
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Saved Map Views ({views.length})
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary p-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {isLoading ? (
            <div className="flex items-center justify-center p-8 text-atlas-text-muted gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
              <span>Loading saved views...</span>
            </div>
          ) : error ? (
            <div className="text-rose-400 text-center p-4">{error}</div>
          ) : views.length === 0 ? (
            <div className="text-center p-8 text-atlas-text-muted">
              No saved map views found. Use &quot;Save View&quot; on the toolbar to persist your map state.
            </div>
          ) : (
            views.map((v) => (
              <div
                key={v.map_view_id}
                className="p-3 rounded bg-atlas-surface-2/60 border border-atlas-border-default/60 hover:border-atlas-border-default flex items-center justify-between gap-3 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <div className="font-semibold text-atlas-text-primary truncate">{v.name}</div>
                  <div className="text-[10px] text-atlas-text-muted flex items-center gap-3 mt-1">
                    <span className="flex items-center gap-1">
                      <Layers className="w-3 h-3 text-blue-400" />
                      <span>{v.basemap_style_id}</span>
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-slate-400" />
                      <span>{v.updated_at.split("T")[0]}</span>
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => {
                      onRestoreView(v);
                      onClose();
                    }}
                    className="flex items-center gap-1 text-[11px] h-7"
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span>Open</span>
                  </Button>
                  <button
                    type="button"
                    onClick={() => handleDelete(v.map_view_id)}
                    className="p-1.5 text-atlas-text-muted hover:text-rose-400 rounded transition-colors"
                    title="Delete View"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

