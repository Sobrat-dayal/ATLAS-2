"use client";

import React, { useRef } from "react";
import { Search, X, Loader2, Navigation, Landmark, Globe } from "lucide-react";
import { GeographicSearchResult } from "@/lib/maps/types";

interface AtlasMapSearchProps {
  query: string;
  onQueryChange: (q: string) => void;
  results: GeographicSearchResult[];
  isSearching: boolean;
  isOpen: boolean;
  onSelectResult: (result: GeographicSearchResult) => void;
  onClear: () => void;
  onClose: () => void;
}

export function AtlasMapSearch({
  query,
  onQueryChange,
  results,
  isSearching,
  isOpen,
  onSelectResult,
  onClear,
  onClose,
}: AtlasMapSearchProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const getPlaceIcon = (type: string) => {
    switch (type) {
      case "financial_center":
        return <Landmark className="w-3.5 h-3.5 text-blue-400 shrink-0" />;
      case "coordinates":
        return <Navigation className="w-3.5 h-3.5 text-emerald-400 shrink-0" />;
      default:
        return <Globe className="w-3.5 h-3.5 text-slate-400 shrink-0" />;
    }
  };

  return (
    <div className="relative w-64 md:w-80">
      <div className="relative flex items-center">
        <Search className="w-3.5 h-3.5 absolute left-2.5 text-atlas-text-muted pointer-events-none" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Search country, city, or coords..."
          className="w-full h-8 pl-8 pr-7 bg-atlas-surface-2 border border-atlas-border-default rounded text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none focus:border-blue-500 font-mono transition-colors"
        />
        {isSearching ? (
          <Loader2 className="w-3.5 h-3.5 absolute right-2.5 animate-spin text-atlas-text-muted" />
        ) : query ? (
          <button
            type="button"
            onClick={onClear}
            className="absolute right-2 text-atlas-text-muted hover:text-atlas-text-primary p-0.5"
          >
            <X className="w-3 h-3" />
          </button>
        ) : null}
      </div>

      {isOpen && results.length > 0 && (
        <div className="absolute top-9 left-0 right-0 z-50 bg-atlas-surface-1 border border-atlas-border-default rounded shadow-xl overflow-hidden max-h-72 overflow-y-auto font-mono text-xs">
          <div className="px-2.5 py-1 text-[10px] text-atlas-text-muted bg-atlas-surface-2/60 border-b border-atlas-border-default flex justify-between">
            <span>RESOLVED LOCATIONS ({results.length})</span>
            <button onClick={onClose} className="hover:text-atlas-text-primary">ESC</button>
          </div>
          {results.map((res) => (
            <button
              key={res.result_id}
              type="button"
              onClick={() => onSelectResult(res)}
              className="w-full text-left px-3 py-2 hover:bg-atlas-surface-2 flex items-start gap-2.5 border-b border-atlas-border-default/40 last:border-0 transition-colors"
            >
              {getPlaceIcon(res.place_type)}
              <div className="min-w-0 flex-1">
                <div className="font-medium text-atlas-text-primary truncate">
                  {res.label}
                </div>
                {res.disambiguation && (
                  <div className="text-[10px] text-atlas-text-muted truncate mt-0.5">
                    {res.disambiguation}
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

