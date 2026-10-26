"use client";

import React from "react";
import { Search, X, Filter } from "lucide-react";
import { NewsPublisherDTO, NewsSourceDTO } from "@/lib/news/types";

interface NewsFilterBarProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedSource: string;
  onSourceChange: (s: string) => void;
  selectedPublisher: string;
  onPublisherChange: (p: string) => void;
  selectedGeography: string;
  onGeographyChange: (g: string) => void;
  sources: NewsSourceDTO[];
  publishers: NewsPublisherDTO[];
  onClearFilters: () => void;
}

const GEOGRAPHIES = [
  { code: "", label: "All Regions" },
  { code: "US", label: "United States (US)" },
  { code: "EU", label: "European Union (EU)" },
  { code: "GB", label: "United Kingdom (GB)" },
  { code: "IN", label: "India (IN)" },
  { code: "JP", label: "Japan (JP)" },
];

export function NewsFilterBar({
  searchQuery,
  onSearchChange,
  selectedSource,
  onSourceChange,
  selectedPublisher,
  onPublisherChange,
  selectedGeography,
  onGeographyChange,
  sources,
  publishers,
  onClearFilters,
}: NewsFilterBarProps) {
  const hasActiveFilters =
    Boolean(searchQuery) ||
    Boolean(selectedSource) ||
    Boolean(selectedPublisher) ||
    Boolean(selectedGeography);

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 py-2">
      <div className="flex flex-wrap items-center gap-2 flex-1 min-w-[280px]">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[220px] max-w-md">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search headlines and authorized excerpts..."
            className="w-full pl-8 pr-8 py-1.5 text-xs rounded border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 focus:outline-none focus:ring-1 focus:ring-zinc-900 dark:focus:ring-zinc-100"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Source Provider Select */}
        <select
          value={selectedSource}
          onChange={(e) => onSourceChange(e.target.value)}
          className="px-2.5 py-1.5 text-xs rounded border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 focus:outline-none focus:ring-1 focus:ring-zinc-900 dark:focus:ring-zinc-100"
        >
          <option value="">All Sources</option>
          {sources.map((s) => (
            <option key={s.source_id} value={s.source_id}>
              {s.provider_name}
            </option>
          ))}
        </select>

        {/* Publisher Select */}
        <select
          value={selectedPublisher}
          onChange={(e) => onPublisherChange(e.target.value)}
          className="px-2.5 py-1.5 text-xs rounded border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 focus:outline-none focus:ring-1 focus:ring-zinc-900 dark:focus:ring-zinc-100"
        >
          <option value="">All Publishers</option>
          {publishers.map((p) => (
            <option key={p.publisher_id} value={p.publisher_id}>
              {p.canonical_name}
            </option>
          ))}
        </select>

        {/* Geography Select */}
        <select
          value={selectedGeography}
          onChange={(e) => onGeographyChange(e.target.value)}
          className="px-2.5 py-1.5 text-xs rounded border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 focus:outline-none focus:ring-1 focus:ring-zinc-900 dark:focus:ring-zinc-100"
        >
          {GEOGRAPHIES.map((g) => (
            <option key={g.code} value={g.code}>
              {g.label}
            </option>
          ))}
        </select>
      </div>

      {/* Clear Filters Button */}
      {hasActiveFilters && (
        <button
          onClick={onClearFilters}
          className="flex items-center gap-1.5 px-2 py-1 text-xs text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded transition-colors"
        >
          <X className="w-3.5 h-3.5" />
          <span>Clear Filters</span>
        </button>
      )}
    </div>
  );
}
