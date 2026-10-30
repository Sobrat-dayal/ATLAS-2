/**
 * React hook for inspecting authorized SQL sources and schema metadata.
 */

import { useCallback, useEffect, useState } from "react";
import { executionApi } from "@/lib/terminal/executionApi";
import type { SqlSource, SqlValidateResponse } from "@/lib/terminal/executionTypes";

export function useSqlSources() {
  const [sources, setSources] = useState<SqlSource[]>([]);
  const [selectedSourceId, setSelectedSourceId] = useState<string>("test_prices");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSources = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const list = await executionApi.getSqlSources();
      setSources(list);
      if (list.length > 0 && !list.some((s) => s.source_id === selectedSourceId)) {
        setSelectedSourceId(list[0].source_id);
      }
    } catch (err: any) {
      setError(err?.message || "Failed to load SQL sources.");
      // Fallback baseline
      setSources([
        {
          source_id: "test_prices",
          display_name: "Test Financial Prices (Controlled Fixture)",
          source_type: "in_memory_fixture",
          allowed_schemas: ["public"],
          allowed_views: ["test_prices"],
          is_read_only: true,
          default_row_limit: 500,
          timeout_seconds: 15,
          description: "Controlled isolated test pricing relation with AAA, BBB, CCC fixtures.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [selectedSourceId]);

  const validateQuery = useCallback(async (sqlText: string): Promise<SqlValidateResponse> => {
    return executionApi.validateSql(sqlText);
  }, []);

  useEffect(() => {
    loadSources();
  }, [loadSources]);

  return {
    sources,
    selectedSourceId,
    setSelectedSourceId,
    isLoading,
    error,
    validateQuery,
    reloadSources: loadSources,
  };
}

