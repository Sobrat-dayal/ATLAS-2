"use client";

import { useEffect, useRef, useState, useId } from "react";
import {
  Search,
  Loader2,
  Building2,
  Globe,
  FileText,
  Box,
  TrendingUp,
  Landmark,
  Radio,
  User,
  AlertCircle,
} from "lucide-react";
import { useSelectedEntity } from "@/hooks/entity";
import { searchEntities, GlobalSearchEntityResult } from "@/lib/search";
import { useCommandPalette, usePlatformShortcut } from "@/hooks/commands";

export function GlobalSearch() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [results, setResults] = useState<GlobalSearchEntityResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);

  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const listboxId = useId();

  const { selectEntity } = useSelectedEntity();
  const { searchFocusTrigger, openCommandPalette } = useCommandPalette();
  const { shortcutLabel } = usePlatformShortcut();

  // Focus and open search when commanded by the Command Palette
  useEffect(() => {
    if (searchFocusTrigger > 0) {
      setIsOpen(true);
      inputRef.current?.focus();
    }
  }, [searchFocusTrigger]);

  // Click-outside and Escape hotkey
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsOpen(false);
        inputRef.current?.blur();
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("mousedown", handleClickOutside);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Debounce query (200ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query);
    }, 200);
    return () => clearTimeout(handler);
  }, [query]);

  // Fetch results with cancellation (AbortController)
  useEffect(() => {
    const trimmed = debouncedQuery.trim();
    if (!trimmed) {
      setResults([]);
      setLoading(false);
      setError(null);
      setHighlightedIndex(-1);
      return;
    }

    const abortController = new AbortController();
    setLoading(true);
    setError(null);

    searchEntities({ query: trimmed, limit: 15, signal: abortController.signal })
      .then((data) => {
        setResults(data.results || []);
        setHighlightedIndex(data.results && data.results.length > 0 ? 0 : -1);
      })
      .catch((err) => {
        if (err.name === "AbortError") {
          return;
        }
        setError("Search temporarily unavailable");
        setResults([]);
      })
      .finally(() => {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      });

    return () => {
      abortController.abort();
    };
  }, [debouncedQuery]);

  const handleSelect = (entityId: string) => {
    selectEntity(entityId);
    setIsOpen(false);
    setQuery("");
    setResults([]);
    setHighlightedIndex(-1);
    inputRef.current?.blur();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || results.length === 0) {
      if (e.key === "ArrowDown" && query.trim() !== "") {
        setIsOpen(true);
      }
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev + 1 < results.length ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : results.length - 1));
    } else if (e.key === "Home") {
      e.preventDefault();
      setHighlightedIndex(0);
    } else if (e.key === "End") {
      e.preventDefault();
      setHighlightedIndex(results.length - 1);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (highlightedIndex >= 0 && highlightedIndex < results.length) {
        handleSelect(results[highlightedIndex].entity_id);
      }
    } else if (e.key === "Escape") {
      e.preventDefault();
      setIsOpen(false);
      inputRef.current?.blur();
    }
  };

  const getIcon = (type?: string) => {
    switch (type?.toLowerCase()) {
      case "company":
        return <Building2 className="h-4 w-4 text-atlas-text-muted shrink-0" />;
      case "security":
      case "equity":
      case "etf":
      case "fund":
      case "bond":
        return <TrendingUp className="h-4 w-4 text-atlas-text-muted shrink-0" />;
      case "exchange":
        return <Landmark className="h-4 w-4 text-atlas-text-muted shrink-0" />;
      case "economic_series":
        return <Radio className="h-4 w-4 text-atlas-text-muted shrink-0" />;
      case "research_document":
        return <FileText className="h-4 w-4 text-atlas-text-muted shrink-0" />;
      case "country":
      case "geographic_entity":
        return <Globe className="h-4 w-4 text-atlas-text-muted shrink-0" />;
      case "person":
        return <User className="h-4 w-4 text-atlas-text-muted shrink-0" />;
      default:
        return <Box className="h-4 w-4 text-atlas-text-muted shrink-0" />;
    }
  };

  const humanizeType = (type?: string) => {
    if (!type) return "Entity";
    return type
      .split("_")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  };

  const renderMatchContext = (res: GlobalSearchEntityResult) => {
    const isIdentifier = res.match_kind.includes("IDENTIFIER");
    const isAlias = res.match_kind.includes("ALIAS");
    const isFuzzy = res.match_kind.startsWith("FUZZY");

    if (isIdentifier && res.identifier_scheme_key) {
      return (
        <span className="truncate">
          <span className="text-atlas-text-secondary">{res.identifier_scheme_key.toUpperCase()}:</span>{" "}
          <span className="text-atlas-text-primary font-mono">{res.matched_text}</span>
          {res.scope_display_name ? (
            <span className="text-atlas-text-muted"> · {res.scope_display_name}</span>
          ) : null}
        </span>
      );
    }

    if (isAlias) {
      return (
        <span className="truncate">
          <span className="text-atlas-text-secondary">
            Alias{res.alias_type_key ? ` (${res.alias_type_key})` : ""}:
          </span>{" "}
          <span className="text-atlas-text-primary">{res.matched_text}</span>
        </span>
      );
    }

    if (isFuzzy) {
      return (
        <span className="truncate">
          <span className="text-atlas-text-secondary">Fuzzy match:</span>{" "}
          <span className="text-atlas-text-primary">{res.matched_text}</span>
        </span>
      );
    }

    if (res.matched_text && res.matched_text !== res.display_name) {
      return (
        <span className="truncate">
          <span className="text-atlas-text-secondary">Matched:</span>{" "}
          <span className="text-atlas-text-primary">{res.matched_text}</span>
        </span>
      );
    }

    return (
      <span className="text-atlas-text-muted truncate">
        {res.match_kind.startsWith("EXACT") ? "Exact Name" : "Prefix Name"}
      </span>
    );
  };

  const renderSafeHighlightedText = (text: string, queryText: string) => {
    const trimmed = queryText.trim();
    if (!trimmed) return <span>{text}</span>;

    // Safe regex-escaped split
    const escaped = trimmed.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const parts = text.split(new RegExp(`(${escaped})`, "gi"));

    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === trimmed.toLowerCase() ? (
            <span key={i} className="text-atlas-accent font-semibold">
              {part}
            </span>
          ) : (
            <span key={i}>{part}</span>
          )
        )}
      </span>
    );
  };

  const showDropdown = isOpen && query.trim() !== "";

  return (
    <div ref={containerRef} className="relative flex max-w-lg flex-1 items-center">
      <div
        className={`flex w-full items-center rounded-sm border px-2 py-1 transition-colors relative z-50 ${
          isOpen ? "border-atlas-accent bg-atlas-surface-hover" : "border-atlas-border-default bg-atlas-surface-2"
        }`}
      >
        <Search className="mr-2 h-3.5 w-3.5 text-atlas-text-muted shrink-0" aria-hidden="true" />
        <input
          ref={inputRef}
          type="text"
          role="combobox"
          aria-expanded={showDropdown}
          aria-haspopup="listbox"
          aria-autocomplete="list"
          aria-controls={showDropdown ? listboxId : undefined}
          aria-activedescendant={
            highlightedIndex >= 0 ? `${listboxId}-option-${highlightedIndex}` : undefined
          }
          aria-label="Global search entities"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (!isOpen) setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsOpen(true)}
          placeholder="Search entities, companies, securities, countries..."
          className="w-full bg-transparent text-sm text-atlas-text-primary placeholder:text-atlas-text-muted outline-none"
        />
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(false);
            openCommandPalette();
          }}
          title={`Open Command Palette (${shortcutLabel})`}
          className="ml-2 flex items-center gap-1 rounded bg-atlas-surface-3 px-1.5 py-0.5 text-[10px] text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors shrink-0 cursor-pointer"
        >
          <span>{shortcutLabel}</span>
        </button>
      </div>

      {showDropdown && (
        <div
          id={listboxId}
          role="listbox"
          aria-label="Search results"
          className="absolute top-full left-0 right-0 mt-1 rounded-md border border-atlas-border-default bg-atlas-surface-1 shadow-xl z-50 max-h-[380px] overflow-y-auto"
        >
          {loading && results.length === 0 && (
            <div className="flex items-center justify-center p-4">
              <Loader2 className="h-5 w-5 animate-spin text-atlas-text-muted" />
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center gap-2 p-4 text-xs text-atlas-error">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!loading && !error && results.length === 0 && debouncedQuery && (
            <div className="p-4 text-center text-sm text-atlas-text-muted">
              No matching ATLAS entities
            </div>
          )}

          {results.length > 0 && (
            <ul className="py-1">
              {results.map((res, index) => {
                const isHighlighted = index === highlightedIndex;
                return (
                  <li
                    key={res.entity_id}
                    id={`${listboxId}-option-${index}`}
                    role="option"
                    aria-selected={isHighlighted}
                    onMouseEnter={() => setHighlightedIndex(index)}
                    onClick={() => handleSelect(res.entity_id)}
                    className={`flex cursor-pointer items-center justify-between px-3 py-2 transition-colors ${
                      isHighlighted ? "bg-atlas-surface-hover" : "hover:bg-atlas-surface-hover"
                    }`}
                  >
                    <div className="flex items-center gap-3 overflow-hidden min-w-0">
                      {getIcon(res.entity_type)}
                      <div className="flex flex-col truncate min-w-0">
                        <span className="truncate text-sm font-medium text-atlas-text-primary">
                          {renderSafeHighlightedText(res.display_name, debouncedQuery)}
                        </span>
                        <div className="flex items-center gap-2 text-xs text-atlas-text-muted min-w-0">
                          <span className="uppercase tracking-wider text-[10px] bg-atlas-surface-3 px-1 py-0.5 rounded shrink-0">
                            {humanizeType(res.entity_type)}
                          </span>
                          {renderMatchContext(res)}
                        </div>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
