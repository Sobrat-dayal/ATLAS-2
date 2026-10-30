"use client";

import { useEffect, useState } from "react";
import { fetchAiToolCalls } from "@/lib/ai/tools/api";
import { AiToolCall } from "@/lib/ai/tools/types";

export function useAiToolCalls(limit: number = 20) {
  const [calls, setCalls] = useState<AiToolCall[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAiToolCalls(limit);
      setCalls(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [limit]);

  return { calls, loading, error, refetch: load };
}

