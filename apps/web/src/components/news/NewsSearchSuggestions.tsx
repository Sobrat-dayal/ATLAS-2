"use client";

import React, { useEffect, useRef, useState } from "react";
import { NewsSearchSuggestionDTO } from "@/lib/news/types";

interface NewsSearchSuggestionsProps {
  query: string;
  onQueryChange: (q: string) => void;
  suggestions: NewsSearchSuggestionDTO[];
  isLoading: boolean;
  onSelectSuggestion: (s: NewsSearchSuggestionDTO) => void;
  onSearchSubmit?: () => void;
}

export function NewsSearchSuggestions({
  query,
  onQueryChange,
  suggestions,
  isLoading,
  onSelectSuggestion,
  onSearchSubmit,
}: NewsSearchSuggestionsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!isOpen && suggestions.length > 0) {
        setIsOpen(true);
        setActiveIndex(0);
      } else {
        setActiveIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === "Enter") {
      if (isOpen && activeIndex >= 0 && activeIndex < suggestions.length) {
        e.preventDefault();
        onSelectSuggestion(suggestions[activeIndex]);
        setIsOpen(false);
      } else if (onSearchSubmit) {
        onSearchSubmit();
        setIsOpen(false);
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  const getBadgeStyle = (type: string) => {
    switch (type) {
      case "TICKER":
        return "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/20";
      case "COMPANY":
        return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";
      case "TOPIC":
        return "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20";
      case "PUBLISHER":
        return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20";
      default:
        return "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20";
    }
  };

  return (
    <div ref={wrapperRef} className="relative w-full">
      <div className="relative flex items-center">
        <svg
          className="absolute left-3 w-4 h-4 text-zinc-400 pointer-events-none"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            onQueryChange(e.target.value);
            setIsOpen(true);
            setActiveIndex(-1);
          }}
          onFocus={() => {
            if (suggestions.length > 0) setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder='Search headlines, tickers (e.g. AAPL), topics ("Earnings"), or exact phrases...'
          className="w-full pl-9 pr-8 py-1.5 text-xs bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded font-mono text-zinc-800 dark:text-zinc-200 placeholder-zinc-400 focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 transition-colors shadow-inner"
        />

        {isLoading ? (
          <div className="absolute right-2.5 w-3.5 h-3.5 border-2 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
        ) : query ? (
          <button
            onClick={() => {
              onQueryChange("");
              setIsOpen(false);
              inputRef.current?.focus();
            }}
            className="absolute right-2.5 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
            title="Clear search"
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        ) : null}
      </div>

      {/* Autocomplete Dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div className="absolute z-50 left-0 right-0 mt-1 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-lg overflow-hidden py-1 max-h-72 overflow-y-auto font-mono text-xs">
          <div className="px-2.5 py-1 text-[10px] font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500 border-b border-zinc-100 dark:border-zinc-800/60">
            Suggested Matches
          </div>
          {suggestions.map((s, idx) => (
            <div
              key={`${s.suggestion_type}-${s.key}`}
              onClick={() => {
                onSelectSuggestion(s);
                setIsOpen(false);
              }}
              onMouseEnter={() => setActiveIndex(idx)}
              className={`flex items-center justify-between px-3 py-1.5 cursor-pointer transition-colors ${
                idx === activeIndex
                  ? "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100"
                  : "text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800/50"
              }`}
            >
              <div className="flex items-center space-x-2 min-w-0">
                <span
                  className={`text-[9px] px-1.5 py-0.5 rounded border font-semibold ${getBadgeStyle(
                    s.suggestion_type
                  )}`}
                >
                  {s.suggestion_type}
                </span>
                <span className="font-medium truncate">{s.label}</span>
                {s.secondary_label && (
                  <span className="text-[10px] text-zinc-400 truncate">
                    ({s.secondary_label})
                  </span>
                )}
              </div>
              {s.category && (
                <span className="text-[10px] text-zinc-400 dark:text-zinc-500 capitalize ml-2 shrink-0">
                  {s.category.toLowerCase().replace(/_/g, " ")}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
