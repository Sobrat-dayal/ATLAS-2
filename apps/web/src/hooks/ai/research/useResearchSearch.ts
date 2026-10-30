"use client";

import { useState } from "react";
import { searchResearchPassages } from "@/lib/ai/research/api";
import { ResearchPassageDTO, ResearchSearchRequest } from "@/lib/ai/research/types";

export function useResearchSearch() {
  const [query, setQuery] = useState("");
  const [passages, setPassages] = useState<ResearchPassageDTO[]>([]);
  const [totalHits, setTotalHits] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = async (req?: Partial<ResearchSearchRequest>) => {
    const q = req?.query !== undefined ? req.query : query;
    if (!q.trim()) return;

    setIsSearching(true);
    setError(null);
    try {
      const res = await searchResearchPassages({
        query: q,
        symbols: req?.symbols,
        document_types: req?.document_types,
        historical_as_of: req?.historical_as_of,
        retrieval_strategy: req?.retrieval_strategy || "HYBRID_FUSION",
        limit: req?.limit || 5,
      });
      setPassages(res.passages);
      setTotalHits(res.total_hits);
    } catch (err: any) {
      setError(err?.message || "Passage search failed.");
    } finally {
      setIsSearching(false);
    }
  };

  const clear = () => {
    setQuery("");
    setPassages([]);
    setTotalHits(0);
    setError(null);
  };

  return {
    query,
    setQuery,
    passages,
    totalHits,
    isSearching,
    error,
    search,
    clear,
  };
}

