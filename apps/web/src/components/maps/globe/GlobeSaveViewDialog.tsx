/**
 * Save 3D Globe View Dialog (Stage 130).
 *
 * Persists genuine camera orientation, imagery provider, terrain source,
 * and layer states into the Universal Saved system.
 */

"use client";

import React, { useState } from "react";
import { AtlasGlobeCamera } from "@/lib/maps/globe/types";
import { saveGlobeView } from "@/lib/maps/globe/api";
import { Bookmark, X, Loader2 } from "lucide-react";

interface GlobeSaveViewDialogProps {
  isOpen: boolean;
  onClose: () => void;
  currentCamera: AtlasGlobeCamera;
  activeImageryId: string;
  activeTerrainId: string;
  activeLayerIds: string[];
  selectedFeatureId?: string | null;
  onSavedSuccess?: () => void;
}

export function GlobeSaveViewDialog({
  isOpen,
  onClose,
  currentCamera,
  activeImageryId,
  activeTerrainId,
  activeLayerIds,
  selectedFeatureId,
  onSavedSuccess,
}: GlobeSaveViewDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSaving(true);
    setError(null);
    try {
      await saveGlobeView({
        name: name.trim(),
        description: description.trim(),
        renderer_mode: "3D",
        cesium_camera: currentCamera,
        imagery_provider_id: activeImageryId,
        terrain_provider_id: activeTerrainId,
        visible_layer_references: activeLayerIds,
        selected_feature_id: selectedFeatureId,
        quality_profile: "balanced",
      });
      setIsSaving(false);
      setName("");
      setDescription("");
      if (onSavedSuccess) onSavedSuccess();
      onClose();
    } catch (err: any) {
      setIsSaving(false);
      setError(err?.message || "Failed to save globe view.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="save-globe-title"
        className="w-full max-w-md rounded-lg bg-atlas-surface-1 border border-atlas-border-default shadow-2xl p-5 text-atlas-text-primary"
      >
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-atlas-accent" />
            <h3 id="save-globe-title" className="text-sm font-semibold">
              Save 3D Globe View
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close dialog"
            className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-3.5">
          {error && (
            <div className="p-2.5 rounded bg-atlas-negative/10 border border-atlas-negative/20 text-atlas-negative text-xs">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-atlas-text-muted mb-1">
              View Name <span className="text-atlas-accent">*</span>
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., London Financial Core 3D"
              className="w-full px-3 py-1.5 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-hidden focus:border-atlas-accent"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-atlas-text-muted mb-1">
              Description (Optional)
            </label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Contextual notes on this 3D perspective"
              className="w-full px-3 py-1.5 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-hidden focus:border-atlas-accent resize-none"
            />
          </div>

          <div className="p-2.5 rounded bg-atlas-surface-2/40 border border-atlas-border-subtle/60 text-[11px] text-atlas-text-muted space-y-1">
            <div className="flex justify-between">
              <span>Longitude / Latitude:</span>
              <span className="font-mono text-atlas-text-primary">
                {currentCamera.longitude.toFixed(4)}°, {currentCamera.latitude.toFixed(4)}°
              </span>
            </div>
            <div className="flex justify-between">
              <span>Altitude:</span>
              <span className="font-mono text-atlas-text-primary">
                {Math.round(currentCamera.height_meters).toLocaleString()} m
              </span>
            </div>
            <div className="flex justify-between">
              <span>Imagery / Terrain:</span>
              <span className="font-mono text-atlas-text-primary">
                {activeImageryId} / {activeTerrainId}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-atlas-border-subtle">
            <button
              type="button"
              onClick={onClose}
              disabled={isSaving}
              className="px-3 py-1.5 rounded text-xs text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving || !name.trim()}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-atlas-accent hover:bg-atlas-accent-hover text-white text-xs font-medium transition-colors shadow-xs disabled:opacity-50 cursor-pointer"
            >
              {isSaving && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              <span>Save View</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
