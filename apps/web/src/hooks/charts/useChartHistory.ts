"use client";

/**
 * Custom React hook managing historical chart data, pagination, viewport backfill,
 * and crosshair inspection for ATLAS Charts V1 (Stage 66).
 */

import { useCallback, useEffect, useRef, useState } from "react";
import {
  ChartBarDTO,
  ChartCoverageDTO,
  ChartHistoryResponse,
  ChartInstrumentMetadata,
  ChartPaginationDTO,
  ChartRenderMode,
  HoveredBarData,
  fetchChartHistory,
  fetchChartInstruments,
} from "@/lib/charts";
import { useSelectedEntity } from "@/hooks/entity";

export interface UseChartHistoryReturn {
  selectedSymbol: string;
  selectedInstrument: ChartInstrumentMetadata | null;
  interval: string;
  renderMode: ChartRenderMode;
  bars: ChartBarDTO[];
  coverage: ChartCoverageDTO | null;
  pagination: ChartPaginationDTO | null;
  isLoading: boolean;
  isBackfilling: boolean;
  error: string | null;
  hoveredBar: HoveredBarData | null;
  selectInstrument: (symbolOrId: string) => void;
  setRenderMode: (mode: ChartRenderMode) => void;
  loadOlderHistory: () => Promise<void>;
  refreshHistory: () => Promise<void>;
  setHoveredBar: (data: HoveredBarData | null) => void;
  availableInstruments: ChartInstrumentMetadata[];
  isSearching: boolean;
}

export function useChartHistory(initialSymbol: string = "SPY"): UseChartHistoryReturn {
  const [selectedSymbol, setSelectedSymbol] = useState<string>(initialSymbol);
  const [selectedInstrument, setSelectedInstrument] = useState<ChartInstrumentMetadata | null>(null);
  const [interval] = useState<string>("1d"); // Baseline interval for Stage 66
  const [renderMode, setRenderMode] = useState<ChartRenderMode>("candlestick");
  const [bars, setBars] = useState<ChartBarDTO[]>([]);
  const [coverage, setCoverage] = useState<ChartCoverageDTO | null>(null);
  const [pagination, setPagination] = useState<ChartPaginationDTO | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isBackfilling, setIsBackfilling] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hoveredBar, setHoveredBar] = useState<HoveredBarData | null>(null);

  // Available instruments catalog for fast switching
  const [availableInstruments, setAvailableInstruments] = useState<ChartInstrumentMetadata[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);

  const { selectEntity } = useSelectedEntity();
  const activeAbortRef = useRef<AbortController | null>(null);
  const isBackfillingRef = useRef<boolean>(false);

  // Sync state if initialSymbol changes externally (e.g. via deep-linking query param)
  useEffect(() => {
    if (initialSymbol) {
      setSelectedSymbol(initialSymbol);
    }
  }, [initialSymbol]);

  // Load available canonical instruments on mount
  useEffect(() => {
    let unmounted = false;
    async function loadCatalog() {
      setIsSearching(true);
      try {
        const res = await fetchChartInstruments();
        if (!unmounted && res.results.length > 0) {
          setAvailableInstruments(res.results);
        }
      } catch (err) {
        console.warn("Could not load chart catalog:", err);
      } finally {
        if (!unmounted) setIsSearching(false);
      }
    }
    loadCatalog();
    return () => {
      unmounted = true;
    };
  }, []);

  // Fetch initial history when selected symbol/instrument changes
  const fetchHistory = useCallback(async (symbolOrId: string) => {
    if (activeAbortRef.current) {
      activeAbortRef.current.abort();
    }
    const ac = new AbortController();
    activeAbortRef.current = ac;

    setIsLoading(true);
    setError(null);

    try {
      const data: ChartHistoryResponse = await fetchChartHistory({
        symbol: symbolOrId,
        interval: "1d",
        limit: 250,
        signal: ac.signal,
      });

      setSelectedInstrument(data.instrument);
      setSelectedSymbol(data.instrument.display_symbol);
      setBars(data.bars);
      setCoverage(data.coverage);
      setPagination(data.pagination ?? null);

      // Inform global context of selected entity
      if (selectEntity && data.instrument.entity_id) {
        selectEntity(data.instrument.entity_id);
      }

      // Initialize default hovered bar with latest bar
      if (data.bars.length > 0) {
        const last = data.bars[data.bars.length - 1];
        const openVal = typeof last.open === "string" ? parseFloat(last.open) : Number(last.open);
        const closeVal = typeof last.close === "string" ? parseFloat(last.close) : Number(last.close);
        const highVal = typeof last.high === "string" ? parseFloat(last.high) : Number(last.high);
        const lowVal = typeof last.low === "string" ? parseFloat(last.low) : Number(last.low);
        const volVal = last.volume !== null ? (typeof last.volume === "string" ? parseFloat(last.volume) : Number(last.volume)) : null;
        const pct = openVal !== 0 ? ((closeVal - openVal) / openVal) * 100 : 0;

        setHoveredBar({
          time_unix: last.time_unix,
          timestamp: last.timestamp,
          open: openVal,
          high: highVal,
          low: lowVal,
          close: closeVal,
          volume: volVal,
          changePercent: pct,
        });
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to load chart history.");
      setBars([]);
      setCoverage(null);
      setPagination(null);
    } finally {
      setIsLoading(false);
    }
  }, [selectEntity]);

  // Initial trigger
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchHistory(selectedSymbol);
    return () => {
      if (activeAbortRef.current) {
        activeAbortRef.current.abort();
      }
    };
  }, [selectedSymbol, fetchHistory]);

  // Select instrument handler
  const selectInstrument = useCallback((symbolOrId: string) => {
    setSelectedSymbol(symbolOrId);
  }, []);

  // Backfill older history
  const loadOlderHistory = useCallback(async () => {
    if (!pagination?.has_more || !pagination.next_cursor || isBackfillingRef.current || !selectedSymbol) {
      return;
    }

    isBackfillingRef.current = true;
    setIsBackfilling(true);

    try {
      const data = await fetchChartHistory({
        symbol: selectedSymbol,
        interval: "1d",
        before: pagination.next_cursor,
        limit: 100,
      });

      if (data.bars.length > 0) {
        // Prepend older bars
        setBars((prev) => {
          const existingIds = new Set(prev.map((b) => b.timestamp));
          const newUnique = data.bars.filter((b) => !existingIds.has(b.timestamp));
          return [...newUnique, ...prev];
        });
        setPagination(data.pagination ?? null);
      } else {
        // No more older bars
        setPagination((prev) => (prev ? { ...prev, has_more: false } : null));
      }
    } catch (err) {
      console.warn("Failed to backfill older chart history:", err);
    } finally {
      isBackfillingRef.current = false;
      setIsBackfilling(false);
    }
  }, [pagination, selectedSymbol]);

  const refreshHistory = useCallback(async () => {
    await fetchHistory(selectedSymbol);
  }, [fetchHistory, selectedSymbol]);

  return {
    selectedSymbol,
    selectedInstrument,
    interval,
    renderMode,
    bars,
    coverage,
    pagination,
    isLoading,
    isBackfilling,
    error,
    hoveredBar,
    selectInstrument,
    setRenderMode,
    loadOlderHistory,
    refreshHistory,
    setHoveredBar,
    availableInstruments,
    isSearching,
  };
}
