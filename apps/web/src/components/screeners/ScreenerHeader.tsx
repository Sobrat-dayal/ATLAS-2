"use client";

import React from "react";
import {
  Columns,
  Database,
  FilterX,
  Play,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import { ScreenerUniverseDefinition } from "@/lib/screeners/types";

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
                  V1 · STAGE 94
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                Canonical Security Discovery & Source-Verified Multi-Metric Filtering
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
        <div className="flex items-center gap-2">
          {/* Result Count Stat */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded border border-border/50 bg-muted/40 font-mono text-xs">
            <span className="text-muted-foreground">Matching:</span>
            <span className="font-semibold text-foreground">
              {loading ? "..." : matchingCount}
            </span>
            <span className="text-muted-foreground/60">/ {totalEvaluated}</span>
          </div>

          {/* Coverage Audit Toggle */}
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
            <span className="hidden md:inline">Coverage</span>
          </button>

          {/* Columns Selector Toggle */}
          <button
            type="button"
            onClick={onToggleColumns}
            className="flex h-8 items-center gap-1.5 rounded-md border border-border bg-background px-2.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground"
            title="Configure Table Columns"
          >
            <Columns className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Columns</span>
          </button>

          {/* Reset Filters */}
          <button
            type="button"
            onClick={onReset}
            className="flex h-8 items-center gap-1.5 rounded-md border border-border bg-background px-2.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground"
            title="Reset Filters to Default"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Reset</span>
          </button>

          {/* Run Screener Button */}
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
