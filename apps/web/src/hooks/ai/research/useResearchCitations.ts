"use client";

import { useState } from "react";
import { resolveResearchCitation } from "@/lib/ai/research/api";

export function useResearchCitations() {
  const [activeCitation, setActiveCitation] = useState<Record<string, any> | null>(null);
  const [isResolving, setIsResolving] = useState(false);
  const [resolutionError, setResolutionError] = useState<string | null>(null);

  const inspectCitation = async (citationId: string) => {
    setIsResolving(true);
    setResolutionError(null);
    try {
      const data = await resolveResearchCitation(citationId);
      setActiveCitation(data);
      return data;
    } catch (err: any) {
      setResolutionError(err?.message || "Failed to resolve citation source.");
      setActiveCitation(null);
    } finally {
      setIsResolving(false);
    }
  };

  const closeCitation = () => {
    setActiveCitation(null);
    setResolutionError(null);
  };

  return {
    activeCitation,
    isResolving,
    resolutionError,
    inspectCitation,
    closeCitation,
  };
}

