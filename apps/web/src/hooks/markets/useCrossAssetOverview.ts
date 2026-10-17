"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  AssetClassSummarySection,
  CrossAssetCoverage,
  CrossAssetMember,
  CrossAssetMode,
  CrossAssetOverviewResponse,
  CrossAssetUniverseDefinition,
  CrossAssetWindow,
  getCrossAssetOverview,
  getCrossAssetUniverses,
} from "@/lib/markets/cross-asset";

export interface UseCrossAssetOverviewOptions {
  initialUniverseId?: string;
  initialMode?: CrossAssetMode;
  initialWindow?: CrossAssetWindow;
  initialSymbols?: string[];
}

export interface UseCrossAssetOverviewResult {
  data: CrossAssetOverviewResponse | null;
  universes: CrossAssetUniverseDefinition[];
  currentUniverse: CrossAssetUniverseDefinition | null;
  members: CrossAssetMember[];
  sections: AssetClassSummarySection[];
  coverage: CrossAssetCoverage | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;

  // State & Filters
  universeId: string;
  setUniverseId: (id: string) => void;
  mode: CrossAssetMode;
  setMode: (mode: CrossAssetMode) => void;
  window: CrossAssetWindow;
  setWindow: (window: CrossAssetWindow) => void;
  selectedMember: CrossAssetMember | null;
  setSelectedMember: (member: CrossAssetMember | null) => void;
  customSymbols: string[];
  setCustomSymbols: (symbols: string[]) => void;
  toggleCustomSymbol: (symbol: string) => void;
  clearCustomSymbols: () => void;
}

export function useCrossAssetOverview(
  options?: UseCrossAssetOverviewOptions
): UseCrossAssetOverviewResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [universeId, setUniverseIdState] = useState<string>(
    options?.initialUniverseId || "univ_cross_asset_macro"
  );
  const [mode, setModeState] = useState<CrossAssetMode>(
    options?.initialMode || "native_overview"
  );
  const [window, setWindowState] = useState<CrossAssetWindow>(
    options?.initialWindow || "last_24h"
  );
  const [customSymbols, setCustomSymbolsState] = useState<string[]>(
    options?.initialSymbols || []
  );

  const [universes, setUniverses] = useState<CrossAssetUniverseDefinition[]>([]);
  const [data, setData] = useState<CrossAssetOverviewResponse | null>(null);
  const [selectedMember, setSelectedMember] = useState<CrossAssetMember | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefetching, setIsRefetching] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  // 1. Fetch available universes on mount
  useEffect(() => {
    let isCancelled = false;

    async function loadUniverses() {
      try {
        const resp = await getCrossAssetUniverses({ token });
        if (!isCancelled && resp.universes) {
          setUniverses(resp.universes);
        }
      } catch (err) {
        console.warn("Failed to load cross-asset universes:", err);
      }
    }

    loadUniverses();

    return () => {
      isCancelled = true;
    };
  }, [token]);

  // 2. Fetch cross-asset snapshot
  const fetchOverview = useCallback(
    async (isRefetch = false) => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      if (isRefetch) {
        setIsRefetching(true);
      } else {
        setIsLoading(true);
      }
      setIsError(false);
      setError(null);

      try {
        const symbolsParam = customSymbols.length > 0 ? customSymbols.join(",") : undefined;
        const res = await getCrossAssetOverview(
          {
            universe_id: universeId,
            mode,
            window,
            symbols: symbolsParam,
          },
          {
            token,
            signal: controller.signal,
          }
        );

        setData(res);

        // Keep or update selected member if still present
        if (selectedMember) {
          const updated = res.comparison_members.find(
            (m) => m.symbol === selectedMember.symbol
          );
          setSelectedMember(updated || (res.comparison_members[0] ?? null));
        } else if (res.comparison_members.length > 0) {
          setSelectedMember(res.comparison_members[0]);
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }
        setIsError(true);
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setIsLoading(false);
        setIsRefetching(false);
      }
    },
    [universeId, mode, window, customSymbols, token, selectedMember]
  );

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchOverview(false);
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [universeId, mode, window, customSymbols, fetchOverview]);

  const currentUniverse =
    universes.find((u) => u.universe_id === universeId) || universes[0] || null;

  const toggleCustomSymbol = useCallback((symbol: string) => {
    const symUpper = symbol.toUpperCase();
    setCustomSymbolsState((prev) => {
      if (prev.includes(symUpper)) {
        return prev.filter((s) => s !== symUpper);
      }
      if (prev.length >= 12) {
        return prev;
      }
      return [...prev, symUpper];
    });
  }, []);

  const clearCustomSymbols = useCallback(() => {
    setCustomSymbolsState([]);
  }, []);

  return {
    data,
    universes,
    currentUniverse,
    members: data?.comparison_members || [],
    sections: data?.asset_class_sections || [],
    coverage: data?.coverage || null,
    isLoading,
    isError,
    error,
    refetch: () => fetchOverview(true),
    isRefetching,

    universeId,
    setUniverseId: setUniverseIdState,
    mode,
    setMode: setModeState,
    window,
    setWindow: setWindowState,
    selectedMember,
    setSelectedMember,
    customSymbols,
    setCustomSymbols: setCustomSymbolsState,
    toggleCustomSymbol,
    clearCustomSymbols,
  };
}
