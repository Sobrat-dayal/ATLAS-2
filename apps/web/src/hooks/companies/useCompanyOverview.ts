"use client";

import { useCallback, useEffect, useState } from "react";
import { getCompanyOverview } from "@/lib/companies/api";
import { CompanyOverviewResponse } from "@/lib/companies/types";

export interface UseCompanyOverviewResult {
  data: CompanyOverviewResponse | null;
  loading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
}

export function useCompanyOverview(companyId: string | null): UseCompanyOverviewResult {
  const [data, setData] = useState<CompanyOverviewResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(Boolean(companyId));
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!companyId) return;

    let isMounted = true;
    const controller = new AbortController();

    getCompanyOverview(companyId, controller.signal)
      .then((result) => {
        if (!isMounted) return;
        setData(result);
        setError(null);
      })
      .catch((err: unknown) => {
        if (!isMounted) return;
        if (err instanceof Error && err.name === "AbortError") return;
        setError(err instanceof Error ? err : new Error(String(err)));
        setData(null);
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [companyId]);

  const refresh = useCallback(async () => {
    if (!companyId) return;
    setLoading(true);
    try {
      const result = await getCompanyOverview(companyId);
      setData(result);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  return {
    data: companyId ? data : null,
    loading: companyId ? loading : false,
    error: companyId ? error : null,
    refresh,
  };
}
