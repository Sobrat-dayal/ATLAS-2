"use client";

import { useEffect, useState } from "react";
import { fetchAiTools } from "@/lib/ai/tools/api";
import { AiToolDescriptor } from "@/lib/ai/tools/types";

export function useAiTools(category?: string) {
  const [tools, setTools] = useState<AiToolDescriptor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAiTools(category);
      setTools(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [category]);

  return { tools, loading, error, refetch: load };
}

