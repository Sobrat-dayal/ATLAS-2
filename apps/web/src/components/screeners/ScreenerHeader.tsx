"use client";

import React from "react";
import {
  ArrowUpDown,
  Bookmark,
  Columns,
  Database,
  Download,
  FolderOpen,
  Play,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import { SavedScreener, ScreenerUniverseDefinition } from "@/lib/screeners/types";

interface ScreenerHeaderProps {
  universes: ScreenerUniverseDefinition[];
  selectedUniverseId: string;
  onSelectUniverse: (id: string) => void;
  matchingCount: number;
  totalEvaluated: number;
  loading: boolean;
  onRunScreener: () => void;
  onReset: () => void;
  onToggleColumns: () => void;
  onToggleCoverage: () => void;
  isCoverageOpen: boolean;
  // Stage 97 props
  currentSavedScreen: SavedScreener | null;
  isDirtyFromSaved: boolean;
  onOpenSavedScreens: () => void;
  onOpenSaveDialog: () => void;
  onOpenAdvancedSort: () => void;
  sortCount: number;
  onOpenRanking: () => void;
  isRankingActive: boolean;
  onOpenExport: () => void;
}

export function ScreenerHeader({
  universes,
  selectedUniverseId,
  onSelectUniverse,
  matchingCount,
  totalEvaluated,
  loading,
  onRunScreener,
  onReset,
  onToggleColumns,
  onToggleCoverage,
  isCoverageOpen,
  currentSavedScreen,
  isDirtyFromSaved,
  onOpenSavedScreens,
  onOpenSaveDialog,
  onOpenAdvancedSort,
  sortCount,
  onOpenRanking,
  isRankingActive,
  onOpenExport,
}: ScreenerHeaderProps) {
  const currentUniverse = universes.find((u) => u.universe_id === selectedUniverseId);

  return (
    <div className="flex flex-col gap-3 border-b border-border/60 bg-background/95 px-6 py-4 backdrop-blur">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Title and Universe Badge */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary border border-primary/20">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-semibold tracking-tight text-foreground">
                  Financial Screeners
                </h1>
                <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[11px] text-muted-foreground border border-border/50">
                  V1 · STAGE 98
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                Natural-Language Screener Translation, Factor Discovery, Visual Filters & Saved Strategies
              </p>
            </div>
          </div>

          {/* Universe Selector Dropdown */}
          <div className="relative">
            <select
              aria-label="Screening Universe"
              value={selectedUniverseId}
              onChange={(e) => onSelectUniverse(e.target.value)}
              className="h-8 rounded-md border border-border/80 bg-background px-3 text-xs font-medium text-foreground transition-colors hover:border-primary/50 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            >
              {universes.map((u) => (
                <option key={u.universe_id} value={u.universe_id}>
                  {u.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Result Count Stat */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded border border-border/50 bg-muted/40 font-mono text-xs">
            <span className="text-muted-foreground">Matching:</span>
            <span className="font-semibold text-foreground">
              {loading ? "..." : matchingCount}
            </span>
            <span className="text-muted-foreground/60">/ {totalEvaluated}</span>
          </div>

          {/* 1. My Saved Screens Button */}
          <button
            type="button"
            onClick={onOpenSavedScreens}
            className={`flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium border transition-colors ${
              currentSavedScreen
                ? "bg-primary/10 border-primary text-primary"
                : "bg-background border-border hover:bg-muted/60 text-muted-foreground hover:text-foreground"
            }`}
            title="Open Saved Screens Library"
          >
            <FolderOpen className="h-3.5 w-3.5" />
            <span className="hidden lg:inline truncate max-w-[130px]">
              {currentSavedScreen ? currentSavedScreen.name : "My Screens"}
            </span>
            {currentSavedScreen && isDirtyFromSaved && (
              <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" title="Unsaved modifications" />
            )}
          </button>

          {/* 2. Save Screen Button */}
          <button
            type="button"
            onClick={onOpenSaveDialog}
            className="flex h-8 items-center gap-1.5 rounded-md border border-border bg-background px-2.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground"
            title={currentSavedScreen ? "Update or Save As Screener" : "Save Current Screener"}
          >
            <Bookmark className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Save</span>
          </button>

          {/* 3. Advanced Multi-Column Sort */}
          <button
            type="button"
            onClick={onOpenAdvancedSort}
            className={`flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium border transition-colors ${
              sortCount > 1
                ? "bg-primary/10 border-primary text-primary"
                : "bg-background border-border hover:bg-muted/60 text-muted-foreground hover:text-foreground"
            }`}
            title="Configure Advanced Multi-Column Sort Rules"
          >
            <ArrowUpDown className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Sort</span>
            {sortCount > 0 && (
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-muted font-mono text-[10px] text-muted-foreground">
                {sortCount}
              </span>
            )}
          </button>

          {/* 4. Quantitative Ranking Button */}
          <button
            type="button"
            onClick={onOpenRanking}
            className={`flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium border transition-colors ${
              isRankingActive
                ? "bg-primary/15 border-primary text-primary shadow-sm font-semibold"
                : "bg-background border-border hover:bg-muted/60 text-muted-foreground hover:text-foreground"
            }`}
            title="Configure Quantitative Factor Rankings"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Rank</span>
            {isRankingActive && (
              <span className="flex h-2 w-2 rounded-full bg-primary" />
            )}
          </button>

          {/* 5. Export Button */}
          <button
            type="button"
            onClick={onOpenExport}
            className="flex h-8 items-center gap-1.5 rounded-md border border-border bg-background px-2.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground"
            title="Export Screener Results to CSV / Excel"
          >
            <Download className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Export</span>
          </button>

          {/* 6. Columns Selector Toggle */}
          <button
            type="button"
            onClick={onToggleColumns}
            className="flex h-8 items-center gap-1.5 rounded-md border border-border bg-background px-2.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground"
            title="Configure Table Columns"
          >
            <Columns className="h-3.5 w-3.5" />
            <span className="hidden lg:inline">Columns</span>
          </button>

          {/* 7. Coverage Audit Toggle */}
          <button
            type="button"
            onClick={onToggleCoverage}
            className={`flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium border transition-colors ${
              isCoverageOpen
                ? "bg-primary/10 border-primary text-primary"
                : "bg-background border-border hover:bg-muted/60 text-muted-foreground hover:text-foreground"
            }`}
            title="Inspect Data Coverage & Freshness"
          >
            <Database className="h-3.5 w-3.5" />
            <span className="hidden lg:inline">Coverage</span>
          </button>

          {/* 8. Reset Filters */}
          <button
            type="button"
            onClick={onReset}
            className="flex h-8 items-center gap-1.5 rounded-md border border-border bg-background px-2.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground"
            title="Reset Filters to Default"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Reset</span>
          </button>

          {/* 9. Run Screener Button */}
          <button
            type="button"
            onClick={onRunScreener}
            disabled={loading}
            className="flex h-8 items-center gap-1.5 rounded-md bg-primary px-3 text-xs font-medium text-primary-foreground shadow-sm transition-all hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1 disabled:opacity-50"
          >
            <Play className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>{loading ? "Screening..." : "Run Screener"}</span>
          </button>
        </div>
      </div>

      {currentUniverse && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="font-medium text-foreground">{currentUniverse.name}:</span>
          <span>{currentUniverse.description}</span>
        </div>
      )}
    </div>
  );
}
