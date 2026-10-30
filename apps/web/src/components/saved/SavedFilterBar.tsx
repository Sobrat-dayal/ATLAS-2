"use client";

import {
  Filter,
  Grid,
  List,
  Search,
  X,
} from "lucide-react";
import { SavedSortOption, SavedTargetType } from "@/lib/saved/types";

interface SavedFilterBarProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedTargetType: SavedTargetType | null;
  onSelectTargetType: (t: SavedTargetType | null) => void;
  selectedModule: string | null;
  onSelectModule: (m: string | null) => void;
  sortBy: SavedSortOption;
  onSortChange: (s: SavedSortOption) => void;
  viewMode: "table" | "cards";
  onViewModeChange: (m: "table" | "cards") => void;
  totalCount: number;
}

const CATEGORY_TABS: Array<{ label: string; value: SavedTargetType | null }> = [
  { label: "All Types", value: null },
  { label: "Instruments", value: "INSTRUMENT" },
  { label: "Companies", value: "COMPANY" },
  { label: "Charts", value: "CHART_CONFIG" },
  { label: "Screeners", value: "SCREENER_CONFIG" },
  { label: "Portfolios", value: "PORTFOLIO_REFERENCE" },
  { label: "Risk Runs", value: "RISK_RUN" },
  { label: "Research", value: "RESEARCH_REPORT" },
  { label: "Economics", value: "ECONOMIC_SERIES" },
  { label: "News", value: "NEWS_ARTICLE" },
];

const MODULE_OPTIONS: Array<{ label: string; value: string | null }> = [
  { label: "All Modules", value: null },
  { label: "Markets", value: "markets" },
  { label: "Companies", value: "companies" },
  { label: "Charts", value: "charts" },
  { label: "Screeners", value: "screeners" },
  { label: "Watchlists", value: "watchlists" },
  { label: "Portfolios", value: "portfolios" },
  { label: "Risk", value: "risk" },
  { label: "Research", value: "research" },
  { label: "Economics", value: "economics" },
  { label: "News", value: "news" },
  { label: "Maps", value: "maps" },
  { label: "Data", value: "data" },
];

export function SavedFilterBar({
  searchQuery,
  onSearchChange,
  selectedTargetType,
  onSelectTargetType,
  selectedModule,
  onSelectModule,
  sortBy,
  onSortChange,
  viewMode,
  onViewModeChange,
  totalCount,
}: SavedFilterBarProps) {
  const hasActiveFilters = !!searchQuery || !!selectedTargetType || !!selectedModule;

  return (
    <div className="flex flex-col gap-2 p-2 bg-atlas-surface-0 border-b border-atlas-border-default shrink-0">
      <div className="flex flex-wrap items-center justify-between gap-2">
        {/* Search input */}
        <div className="relative flex-1 min-w-[220px] max-w-md">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-atlas-text-muted pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search saved resources, titles, notes, tags..."
            className="w-full bg-atlas-surface-1 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted/60 pl-8 pr-7 py-1.5 rounded-sm border border-atlas-border-default focus:border-atlas-border-focus focus:outline-none"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => onSearchChange("")}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-atlas-text-muted hover:text-atlas-text-primary"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Controls: Module filter, Sort, Layout Toggle */}
        <div className="flex items-center gap-2">
          {/* Module Select */}
          <div className="flex items-center gap-1.5 bg-atlas-surface-1 border border-atlas-border-default rounded-sm px-2 py-1 text-xs text-atlas-text-muted">
            <Filter className="w-3 h-3 text-atlas-text-muted" />
            <select
              value={selectedModule || ""}
              onChange={(e) => onSelectModule(e.target.value || null)}
              className="bg-transparent text-xs text-atlas-text-primary border-none focus:outline-none cursor-pointer"
            >
              {MODULE_OPTIONS.map((m) => (
                <option key={m.label} value={m.value || ""} className="bg-atlas-surface-1 text-atlas-text-primary">
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          {/* Sort Select */}
          <div className="flex items-center gap-1 bg-atlas-surface-1 border border-atlas-border-default rounded-sm px-2 py-1 text-xs">
            <span className="text-[10px] text-atlas-text-muted uppercase">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => onSortChange(e.target.value as SavedSortOption)}
              className="bg-transparent text-xs text-atlas-text-primary border-none focus:outline-none cursor-pointer"
            >
              <option value="RECENTLY_SAVED" className="bg-atlas-surface-1 text-atlas-text-primary">Recently Saved</option>
              <option value="RECENTLY_UPDATED" className="bg-atlas-surface-1 text-atlas-text-primary">Recently Updated</option>
              <option value="NAME_ASC" className="bg-atlas-surface-1 text-atlas-text-primary">Name (A-Z)</option>
              <option value="NAME_DESC" className="bg-atlas-surface-1 text-atlas-text-primary">Name (Z-A)</option>
              <option value="RESOURCE_TYPE" className="bg-atlas-surface-1 text-atlas-text-primary">Resource Type</option>
            </select>
          </div>

          {/* Layout Toggle */}
          <div className="flex items-center border border-atlas-border-default rounded-sm p-0.5 bg-atlas-surface-1">
            <button
              type="button"
              onClick={() => onViewModeChange("table")}
              className={`p-1 rounded-sm text-xs transition-colors ${
                viewMode === "table"
                  ? "bg-atlas-surface-2 text-atlas-text-primary font-medium"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
              title="Table View"
            >
              <List className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => onViewModeChange("cards")}
              className={`p-1 rounded-sm text-xs transition-colors ${
                viewMode === "cards"
                  ? "bg-atlas-surface-2 text-atlas-text-primary font-medium"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
              title="Card Grid View"
            >
              <Grid className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Target Type Filter Pills */}
      <div className="flex items-center justify-between gap-2 overflow-x-auto pt-1">
        <div className="flex items-center gap-1">
          {CATEGORY_TABS.map((tab) => {
            const isActive = selectedTargetType === tab.value;
            return (
              <button
                key={tab.label}
                type="button"
                onClick={() => onSelectTargetType(isActive ? null : tab.value)}
                className={`px-2 py-0.5 rounded-sm text-[11px] whitespace-nowrap transition-colors border ${
                  isActive
                    ? "bg-atlas-surface-2 text-atlas-text-primary border-atlas-border-focus font-medium"
                    : "bg-atlas-surface-1 text-atlas-text-muted border-transparent hover:text-atlas-text-primary hover:bg-atlas-surface-2"
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="text-[11px] text-atlas-text-muted shrink-0 pl-2">
          {totalCount} {totalCount === 1 ? "item" : "items"}
        </div>
      </div>
    </div>
  );
}

