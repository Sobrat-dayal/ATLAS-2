"use client";

import { useEffect, useState } from "react";
import { fetchResearchSources } from "@/lib/ai/research/api";
import { ResearchSourceDTO } from "@/lib/ai/research/types";

export function useResearchSources() {
  const [sources, setSources] = useState<ResearchSourceDTO[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSources = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchResearchSources();
      setSources(data);
    } catch (err: any) {
      setError(err?.message || "Failed to load research sources.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSources();
  }, []);

  return {
    sources,
    isLoading,
    error,
    refreshSources: loadSources,
  };
}
