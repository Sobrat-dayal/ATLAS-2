"use client";

import React, { useMemo, useState, useRef, useEffect } from "react";
import {
  Info,
  Plus,
  Search,
  Tag,
  SlidersHorizontal,
  Layers,
  ChevronRight,
} from "lucide-react";
import { FilterCategory, ScreenerFilterDefinition } from "@/lib/screeners/types";

interface FilterLibraryProps {
  filtersRegistry: ScreenerFilterDefinition[];
  onAddCondition: (filterId: string) => void;
  onInspectFilter: (filter: ScreenerFilterDefinition) => void;
  isOpen: boolean;
  onClose?: () => void;
}

const CATEGORY_TABS: Array<{ id: "ALL" | FilterCategory; label: string }> = [
  { id: "ALL", label: "All Metrics" },
  { id: "market_data", label: "Market Data" },
  { id: "fundamentals", label: "Fundamentals" },
  { id: "valuation", label: "Valuation" },
  { id: "profitability", label: "Profitability" },
  { id: "listing", label: "Listing & Venue" },
  { id: "geography", label: "Geography" },
  { id: "industry", label: "Sector & Industry" },
];

export function FilterLibrary({
  filtersRegistry,
  onAddCondition,
  onInspectFilter,
  isOpen,
  onClose,
}: FilterLibraryProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<"ALL" | FilterCategory>("ALL");
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Focus search input when library opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  // Compute category counts
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { ALL: filtersRegistry.length };
    for (const f of filtersRegistry) {
      counts[f.category] = (counts[f.category] || 0) + 1;
    }
    return counts;
  }, [filtersRegistry]);

  // Filtered metrics list
  const filteredMetrics = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return filtersRegistry.filter((f) => {
      // Category match
      if (selectedCategory !== "ALL" && f.category !== selectedCategory) {
        return false;
      }
      if (!q) return true;

      // Search match across name, filter_id, aliases, description
      const nameMatch = f.display_name.toLowerCase().includes(q);
      const idMatch = f.filter_id.toLowerCase().includes(q);
      const descMatch = f.description.toLowerCase().includes(q);
      const aliasMatch = f.aliases?.some((a) => a.toLowerCase().includes(q));

      return nameMatch || idMatch || descMatch || aliasMatch;
    });
  }, [filtersRegistry, selectedCategory, searchQuery]);

  if (!isOpen) return null;

  return (
    <div className="flex h-full w-80 shrink-0 flex-col border-r border-border/60 bg-card/60 backdrop-blur-xs text-xs">
      {/* Header & Search */}
      <div className="flex flex-col gap-2.5 border-b border-border/60 p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 font-semibold text-foreground">
            <SlidersHorizontal className="h-3.5 w-3.5 text-primary" />
            <span>Metric Catalog</span>
            <span className="rounded-full bg-muted px-1.5 py-0.2 text-[10px] font-mono text-muted-foreground">
              {filtersRegistry.length}
            </span>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-[11px] font-medium text-muted-foreground hover:text-foreground"
            >
              Hide
            </button>
          )}
        </div>

        {/* Search input with shortcut hint */}
        <div className="relative flex items-center">
          <Search className="absolute left-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search metric, alias (e.g. pe, mcap)..."
            aria-label="Search filter metric library"
            className="h-7 w-full rounded border border-border/60 bg-background/80 pl-8 pr-7 text-xs placeholder:text-muted-foreground/70 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary/40 font-mono"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-2 text-muted-foreground hover:text-foreground text-[10px]"
            >
              ESC
            </button>
          )}
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex gap-1 overflow-x-auto border-b border-border/40 p-2 scrollbar-none">
        {CATEGORY_TABS.map((tab) => {
          const isSelected = selectedCategory === tab.id;
          const count = categoryCounts[tab.id] || 0;
          return (
            <button
              key={tab.id}
              onClick={() => setSelectedCategory(tab.id)}
              className={`flex shrink-0 items-center gap-1 rounded px-2 py-1 text-[11px] font-medium transition-colors ${
                isSelected
                  ? "bg-primary text-primary-foreground shadow-xs"
                  : "bg-muted/40 text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              <span>{tab.label}</span>
              <span className="opacity-70 text-[9px] font-mono">({count})</span>
            </button>
          );
        })}
      </div>

      {/* Metric List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {filteredMetrics.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground">
            <Layers className="mx-auto mb-1.5 h-5 w-5 opacity-40" />
            <p className="text-[11px]">No matching metrics found.</p>
          </div>
        ) : (
          filteredMetrics.map((filter) => (
            <div
              key={filter.filter_id}
              className="group flex flex-col rounded border border-border/40 bg-background/50 p-2 transition-colors hover:border-primary/50 hover:bg-muted/30"
            >
              <div className="flex items-start justify-between gap-1">
                <div className="flex-1 truncate">
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium text-foreground truncate">
                      {filter.display_name}
                    </span>
                    <span className="rounded bg-muted/70 px-1 py-0.2 text-[9px] font-mono uppercase text-muted-foreground">
                      {filter.unit_kind}
                    </span>
                  </div>
                  <p className="mt-0.5 line-clamp-1 text-[10px] text-muted-foreground">
                    {filter.description}
                  </p>
                </div>

                {/* Inspect button */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onInspectFilter(filter);
                  }}
                  title="Inspect methodology and provenance"
                  aria-label={`Inspect ${filter.display_name} definition`}
                  className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
                >
                  <Info className="h-3.5 w-3.5" />
                </button>
              </div>

              {/* Add condition button */}
              <div className="mt-2 flex items-center justify-between pt-1 border-t border-border/30">
                <span className="text-[9px] font-mono text-muted-foreground/80">
                  {filter.filter_id}
                </span>
                <button
                  type="button"
                  onClick={() => onAddCondition(filter.filter_id)}
                  className="inline-flex items-center gap-1 rounded bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary hover:bg-primary hover:text-primary-foreground transition-colors"
                >
                  <Plus className="h-2.5 w-2.5" />
                  Add Filter
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
