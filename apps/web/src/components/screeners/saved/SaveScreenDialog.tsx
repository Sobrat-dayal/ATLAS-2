"use client";

import React, { useState } from "react";
import {
  AlertCircle,
  Bookmark,
  Check,
  Layers,
  ListFilter,
  Loader2,
  Sparkles,
  X,
} from "lucide-react";
import {
  FilterCriterion,
  SavedScreener,
  SavedScreenerCreateRequest,
  SavedScreenerUpdateRequest,
  ScreenerRankingSpec,
  SortCriterion,
} from "@/lib/screeners/types";
import { createSavedScreener, updateSavedScreener } from "@/lib/screeners/api";

interface SaveScreenDialogProps {
  isOpen: boolean;
  onClose: () => void;
  isSaveAs: boolean;
  currentSavedScreen: SavedScreener | null;
  selectedUniverseId: string;
  selectedExchanges: string[];
  selectedCountries: string[];
  selectedSectors: string[];
  activeFilters: FilterCriterion[];
  sortCriteria: SortCriterion[];
  rankingSpec: ScreenerRankingSpec | null;
  visibleColumnIds: string[];
  onSaved: (screen: SavedScreener) => void;
}

export function SaveScreenDialog({
  isOpen,
  onClose,
  isSaveAs,
  currentSavedScreen,
  selectedUniverseId,
  selectedExchanges,
  selectedCountries,
  selectedSectors,
  activeFilters,
  sortCriteria,
  rankingSpec,
  visibleColumnIds,
  onSaved,
}: SaveScreenDialogProps) {
  const isUpdatingExisting = !isSaveAs && currentSavedScreen !== null;

  const [name, setName] = useState<string>(
    isSaveAs && currentSavedScreen
      ? `${currentSavedScreen.name} (Copy)`
      : currentSavedScreen?.name ?? ""
  );
  const [description, setDescription] = useState<string>(
    currentSavedScreen?.description ?? ""
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isConflict, setIsConflict] = useState<boolean>(false);

  // Sync state if modal reopens
  React.useEffect(() => {
    if (isOpen) {
      setName(
        isSaveAs && currentSavedScreen
          ? `${currentSavedScreen.name} (Copy)`
          : currentSavedScreen?.name ?? ""
      );
      setDescription(currentSavedScreen?.description ?? "");
      setError(null);
      setIsConflict(false);
    }
  }, [isOpen, isSaveAs, currentSavedScreen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Screen name is required.");
      return;
    }
    if (name.trim().length > 120) {
      setError("Screen name cannot exceed 120 characters.");
      return;
    }

    setLoading(true);
    setError(null);
    setIsConflict(false);

    try {
      if (isUpdatingExisting && currentSavedScreen) {
        const updatePayload: SavedScreenerUpdateRequest = {
          name: name.trim(),
          description: description.trim() || null,
          universe: {
            universe_id: selectedUniverseId,
            exchange_mics: selectedExchanges.length > 0 ? selectedExchanges : null,
            listing_country_codes: selectedCountries.length > 0 ? selectedCountries : null,
            sectors: selectedSectors.length > 0 ? selectedSectors : null,
          },
          filters: activeFilters,
          columns: visibleColumnIds,
          sort: sortCriteria,
          ranking: rankingSpec,
          expected_revision: currentSavedScreen.revision,
        };

        const updated = await updateSavedScreener(
          currentSavedScreen.saved_screen_id,
          updatePayload
        );
        onSaved(updated);
        onClose();
      } else {
        const createPayload: SavedScreenerCreateRequest = {
          name: name.trim(),
          description: description.trim() || null,
          universe: {
            universe_id: selectedUniverseId,
            exchange_mics: selectedExchanges.length > 0 ? selectedExchanges : null,
            listing_country_codes: selectedCountries.length > 0 ? selectedCountries : null,
            sectors: selectedSectors.length > 0 ? selectedSectors : null,
          },
          filters: activeFilters,
          columns: visibleColumnIds,
          sort: sortCriteria,
          ranking: rankingSpec,
        };

        const created = await createSavedScreener(createPayload);
        onSaved(created);
        onClose();
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save screener.";
      if (msg.includes("409") || msg.toLowerCase().includes("conflict") || msg.toLowerCase().includes("revision")) {
        setIsConflict(true);
        setError("Revision conflict: Another session updated this screener. Save as a new copy or reload the screen.");
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-lg border border-border bg-card shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/70 px-6 py-4 bg-muted/30">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary border border-primary/20">
              <Bookmark className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-foreground">
                {isUpdatingExisting ? "Update Saved Screen" : isSaveAs ? "Save Screen As Copy" : "Save Screener Strategy"}
              </h2>
              <p className="text-xs text-muted-foreground">
                Persist universe, multi-factor rules, sorting criteria, and quantitative rankings
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="flex items-start gap-2.5 rounded-md bg-destructive/10 border border-destructive/20 p-3 text-xs text-destructive">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <div className="flex-1">
                <span className="font-medium">{error}</span>
                {isConflict && (
                  <p className="mt-1 text-[11px] text-destructive/90">
                    To preserve your changes without overwriting the concurrent edit, choose a new name or save as copy.
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Name Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground flex items-center justify-between">
              <span>Strategy Name <span className="text-destructive">*</span></span>
              <span className="font-mono text-[10px] text-muted-foreground">{name.length}/120</span>
            </label>
            <input
              type="text"
              required
              maxLength={120}
              placeholder="e.g. S&P 500 High-Quality Momentum Screener"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="h-9 w-full rounded-md border border-border/80 bg-background px-3 text-xs font-medium text-foreground placeholder:text-muted-foreground/60 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Description Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground flex items-center justify-between">
              <span>Description (Optional)</span>
              <span className="font-mono text-[10px] text-muted-foreground">{description.length}/1000</span>
            </label>
            <textarea
              rows={2}
              maxLength={1000}
              placeholder="Summary of thesis, fundamental quality constraints, and quantitative factor scoring method..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-md border border-border/80 bg-background p-3 text-xs text-foreground placeholder:text-muted-foreground/60 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary resize-none"
            />
          </div>

          {/* Configuration Summary Card */}
          <div className="rounded-md border border-border/70 bg-muted/30 p-3.5 space-y-2 text-xs">
            <div className="font-semibold text-[11px] text-muted-foreground uppercase tracking-wider">
              Screen Specification Snapshot
            </div>
            <div className="grid grid-cols-2 gap-2 text-muted-foreground font-mono text-[11px]">
              <div className="flex items-center gap-1.5">
                <Layers className="h-3 w-3 text-primary" />
                <span>Universe:</span>
                <span className="font-semibold text-foreground truncate">{selectedUniverseId}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <ListFilter className="h-3 w-3 text-primary" />
                <span>Filters:</span>
                <span className="font-semibold text-foreground">{activeFilters.length} active</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span>Sort Keys:</span>
                <span className="font-semibold text-foreground">{sortCriteria.length} configured</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Sparkles className="h-3 w-3 text-primary" />
                <span>Ranking:</span>
                <span className="font-semibold text-foreground truncate">
                  {rankingSpec ? `${rankingSpec.mode}` : "None"}
                </span>
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-border/50">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Check className="h-3.5 w-3.5" />
                  <span>{isUpdatingExisting ? "Update Screen" : "Save Screen"}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
