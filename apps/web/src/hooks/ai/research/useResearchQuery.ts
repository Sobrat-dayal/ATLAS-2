"use client";

import { useState } from "react";
import { executeResearchQuery } from "@/lib/ai/research/api";
import { ResearchAnswerResponse, ResearchQueryRequest } from "@/lib/ai/research/types";

export function useResearchQuery() {
  const [result, setResult] = useState<ResearchAnswerResponse | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runQuery = async (req: ResearchQueryRequest) => {
    setIsExecuting(true);
    setError(null);
    try {
      const res = await executeResearchQuery(req);
      setResult(res);
      return res;
    } catch (err: any) {
      const msg = err?.message || "Failed to execute grounded research query.";
      setError(msg);
      throw err;
    } finally {
      setIsExecuting(false);
    }
  };

  const clearResult = () => {
    setResult(null);
    setError(null);
  };

  return {
    result,
    isExecuting,
    error,
    runQuery,
    clearResult,
  };
}

