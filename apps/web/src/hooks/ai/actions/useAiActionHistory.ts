"use client";

import { useCallback, useEffect, useState } from "react";
import { getActionHistory } from "@/lib/ai/actions/api";
import { formatActionError } from "@/lib/ai/actions/errors";
import { ActionHistoryItemDTO } from "@/lib/ai/actions/types";

export function useAiActionHistory() {
  const [history, setHistory] = useState<ActionHistoryItemDTO[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadHistory = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await getActionHistory();
      setHistory(resp.history);
    } catch (err: any) {
      setError(formatActionError(err.code, err.message));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  return {
    history,
    isLoading,
    error,
    refreshHistory: loadHistory,
  };
}

