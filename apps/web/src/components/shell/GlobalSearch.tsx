"use client";

import { useEffect, useRef, useState } from "react";
import { Search, Loader2, Building2, Globe, FileText, Box, ArrowRight } from "lucide-react";
import { useSelectedEntity } from "@/hooks/entity";

interface SearchResult {
  result_type: string;
  entity_id: string;
  entity_type: string;
  canonical_name: string;
  display_name: string;
  match_kind: string;
  matched_text: string;
  identifier_scheme_key?: string;
  alias_type_key?: string;
  scope_entity_id?: string;
  scope_display_name?: string;
}

export function GlobalSearch() {
  const [focused, setFocused] = useState(false);
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const { setSelectedEntityId } = useSelectedEntity();

  // Handle hotkeys and clicks outside
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape") {
        setFocused(false);
        inputRef.current?.blur();
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setFocused(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("mousedown", handleClickOutside);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Debounce query
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query);
    }, 250);
    return () => clearTimeout(handler);
  }, [query]);

  // Fetch results
  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setResults([]);
      setLoading(false);
      return;
    }

    let isSubscribed = true;
    setLoading(true);

    const fetchResults = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/api/v1/search/entities?q=${encodeURIComponent(debouncedQuery)}&limit=10`);
        if (res.ok) {
          const data = await res.json();
          if (isSubscribed) {
            setResults(data.results || []);
          }
        }
      } catch (err) {
        console.error("Failed to fetch search results", err);
      } finally {
        if (isSubscribed) {
          setLoading(false);
        }
      }
    };

    fetchResults();

    return () => {
      isSubscribed = false;
    };
  }, [debouncedQuery]);

  const handleSelect = (entityId: string) => {
    setSelectedEntityId(entityId);
    setFocused(false);
    setQuery("");
    inputRef.current?.blur();
  };

  const getIcon = (type?: string) => {
    switch (type?.toLowerCase()) {
      case "company":
      case "equity":
        return <Building2 className="h-4 w-4 text-atlas-text-muted" />;
      case "research_document":
        return <FileText className="h-4 w-4 text-atlas-text-muted" />;
      case "country":
      case "geographic_entity":
        return <Globe className="h-4 w-4 text-atlas-text-muted" />;
      default:
        return <Box className="h-4 w-4 text-atlas-text-muted" />;
    }
  };

  const humanizeType = (type?: string) => {
    if (!type) return "Unknown";
    return type
      .split("_")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  };

  return (
    <div ref={containerRef} className="relative flex max-w-lg flex-1 items-center">
      <div
        className={`flex w-full items-center rounded-sm border px-2 py-1 transition-colors relative z-50 ${
          focused ? "border-atlas-accent bg-atlas-surface-hover" : "border-atlas-border-default bg-atlas-surface-2"
        }`}
      >
        <Search className="mr-2 h-3.5 w-3.5 text-atlas-text-muted" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search companies, tickers, markets, news, research... (Ctrl+K)"
          className="w-full bg-transparent text-sm text-atlas-text-primary placeholder:text-atlas-text-muted outline-none"
          onFocus={() => setFocused(true)}
        />
        <div className="ml-2 flex items-center gap-1 rounded bg-atlas-surface-3 px-1.5 py-0.5 text-[10px] text-atlas-text-muted">
          <span>⌘K</span>
        </div>
      </div>

      {focused && query.trim() !== "" && (
        <div className="absolute top-full left-0 right-0 mt-1 rounded-md border border-atlas-border-default bg-atlas-surface-1 shadow-xl z-50 max-h-[400px] overflow-y-auto">
          {loading && results.length === 0 && (
            <div className="flex items-center justify-center p-4">
              <Loader2 className="h-5 w-5 animate-spin text-atlas-text-muted" />
            </div>
          )}
          
          {!loading && results.length === 0 && debouncedQuery && (
            <div className="p-4 text-center text-sm text-atlas-text-muted">
              No results found for "{debouncedQuery}"
            </div>
          )}

          {results.length > 0 && (
            <ul className="py-1">
              {results.map((res) => (
                <li
                  key={res.entity_id}
                  onClick={() => handleSelect(res.entity_id)}
                  className="flex cursor-pointer items-center justify-between px-3 py-2 hover:bg-atlas-surface-hover group"
                >
                  <div className="flex items-center gap-3 overflow-hidden">
                    {getIcon(res.entity_type)}
                    <div className="flex flex-col truncate">
                      <span className="truncate text-sm font-medium text-atlas-text-primary">
                        {res.display_name}
                      </span>
                      <div className="flex items-center gap-2 text-xs text-atlas-text-muted">
                        <span className="uppercase tracking-wider text-[10px] bg-atlas-surface-3 px-1 py-0.5 rounded">
                          {humanizeType(res.entity_type)}
                        </span>
                        {res.match_kind.includes("IDENTIFIER") && res.identifier_scheme_key && (
                          <span className="truncate">
                            {res.identifier_scheme_key}: <span className="text-atlas-text-primary">{res.matched_text}</span>
                          </span>
                        )}
                        {res.match_kind.includes("ALIAS") && res.alias_type_key && (
                          <span className="truncate">
                            Alias: <span className="text-atlas-text-primary">{res.matched_text}</span>
                          </span>
                        )}
                        {(!res.match_kind.includes("IDENTIFIER") && !res.match_kind.includes("ALIAS")) && res.matched_text !== res.display_name && (
                          <span className="truncate">
                            Matched: <span className="text-atlas-text-primary">{res.matched_text}</span>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-atlas-text-muted opacity-0 transition-opacity group-hover:opacity-100 shrink-0" />
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
