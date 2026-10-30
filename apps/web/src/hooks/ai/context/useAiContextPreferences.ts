"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchContextPreferences, updateContextPreferences } from "@/lib/ai/context/api";
import {
  AiContextPreferences,
  ContextMode,
  UpdateAiContextPreferencesRequest,
} from "@/lib/ai/context/types";

export function useAiContextPreferences() {
  const [preferences, setPreferences] = useState<AiContextPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPreferences = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchContextPreferences();
      setPreferences(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);

  const updatePreferences = useCallback(
    async (payload: UpdateAiContextPreferencesRequest) => {
      setError(null);
      try {
        const updated = await updateContextPreferences(payload);
        setPreferences(updated);
        return updated;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        throw err;
      }
    },
    []
  );

  const setContextMode = useCallback(
    async (mode: ContextMode) => {
      return updatePreferences({ context_mode: mode });
    },
    [updatePreferences]
  );

  const toggleWorkspaceContext = useCallback(async () => {
    if (!preferences) return;
    return updatePreferences({
      allow_workspace_context: !preferences.allow_workspace_context,
    });
  }, [preferences, updatePreferences]);

  const togglePortfolioHoldings = useCallback(async () => {
    if (!preferences) return;
    return updatePreferences({
      allow_portfolio_holdings_context: !preferences.allow_portfolio_holdings_context,
    });
  }, [preferences, updatePreferences]);

  const toggleResearchDrafts = useCallback(async () => {
    if (!preferences) return;
    return updatePreferences({
      allow_research_drafts_context: !preferences.allow_research_drafts_context,
    });
  }, [preferences, updatePreferences]);

  const toggleProviderDisclosure = useCallback(async () => {
    if (!preferences) return;
    return updatePreferences({
      provider_disclosure_enabled: !preferences.provider_disclosure_enabled,
    });
  }, [preferences, updatePreferences]);

  return {
    preferences,
    isLoading,
    error,
    refreshPreferences: loadPreferences,
    updatePreferences,
    setContextMode,
    toggleWorkspaceContext,
    togglePortfolioHoldings,
    toggleResearchDrafts,
    toggleProviderDisclosure,
  };
}

