"use client";

import { useState, useEffect, useCallback } from "react";
import { GeographicSearchResult } from "@/lib/maps/types";
import { searchGeographicPlaces } from "@/lib/maps/api";

export function useMapSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<GeographicSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setIsSearching(false);
      return;
    }

    const timer = setTimeout(() => {
      setIsSearching(true);
      searchGeographicPlaces(query.trim())
        .then((data) => {
          setResults(data);
          setIsSearching(false);
          setIsOpen(true);
        })
        .catch((err) => {
          console.error("Search failed:", err);
          setResults([]);
          setIsSearching(false);
        });
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  const clearSearch = useCallback(() => {
    setQuery("");
    setResults([]);
    setIsOpen(false);
  }, []);

  return {
    query,
    setQuery,
    results,
    isSearching,
    isOpen,
    setIsOpen,
    clearSearch,
  };
}

