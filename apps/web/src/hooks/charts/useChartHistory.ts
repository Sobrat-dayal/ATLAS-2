"use client";

/**
 * Custom React hook managing multi-timeframe chart history, pagination,
 * interval switching, viewport backfill, and crosshair inspection for ATLAS Charts (Stage 68).
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
  setInterval: (newInterval: string) => void;
  renderMode: ChartRenderMode;
  setRenderMode: (mode: ChartRenderMode) => void;
  intervalSourceKind: string;
  derivedSourceInterval: string | null;
  bars: ChartBarDTO[];
  coverage: ChartCoverageDTO | null;
  pagination: ChartPaginationDTO | null;
  isLoading: boolean;
  isBackfilling: boolean;
  error: string | null;
  hoveredBar: HoveredBarData | null;
  selectInstrument: (symbolOrId: string) => void;
  loadOlderHistory: () => Promise<void>;
  refreshHistory: () => Promise<void>;
  setHoveredBar: (data: HoveredBarData | null) => void;
  availableInstruments: ChartInstrumentMetadata[];
  isSearching: boolean;
}

export function useChartHistory(
  initialSymbol: string = "SPY",
  initialInterval: string = "1d"
): UseChartHistoryReturn {
  const [selectedSymbol, setSelectedSymbol] = useState<string>(initialSymbol);
  const [selectedInstrument, setSelectedInstrument] = useState<ChartInstrumentMetadata | null>(null);
  const [interval, setIntervalState] = useState<string>(initialInterval);
  const [renderMode, setRenderMode] = useState<ChartRenderMode>("candlestick");
  const [intervalSourceKind, setIntervalSourceKind] = useState<string>("NATIVE");
  const [derivedSourceInterval, setDerivedSourceInterval] = useState<string | null>(null);

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

  // Sync state if initialSymbol changes externally
  const [prevInitialSymbol, setPrevInitialSymbol] = useState(initialSymbol);
  if (initialSymbol !== prevInitialSymbol) {
    setPrevInitialSymbol(initialSymbol);
    setSelectedSymbol(initialSymbol);
  }

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

  // Fetch history when selected symbol or interval changes
  const fetchHistory = useCallback(
    async (symbolOrId: string, targetInterval: string) => {
      // Abort previous in-flight request to prevent race conditions during rapid switching
      if (activeAbortRef.current) {
        activeAbortRef.current.abort();
      }
      const ac = new AbortController();
      activeAbortRef.current = ac;

      setIsLoading(true);
      setError(null);

      // Default requested bars count: 500 for intraday, 250 for daily/weekly/monthly
      const isIntraday = ["1m", "5m", "15m", "30m", "1h", "4h"].includes(targetInterval);
      const limit = isIntraday ? 500 : 250;

      try {
        const data: ChartHistoryResponse = await fetchChartHistory({
          symbol: symbolOrId,
          interval: targetInterval,
          limit,
          signal: ac.signal,
        });

        setSelectedInstrument(data.instrument);
        setSelectedSymbol(data.instrument.display_symbol);
        setBars(data.bars);
        setCoverage(data.coverage);
        setPagination(data.pagination ?? null);
        setIntervalSourceKind(data.interval_source_kind || "NATIVE");
        setDerivedSourceInterval(data.derived_source_interval || null);

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
          const volVal =
            last.volume !== null
              ? typeof last.volume === "string"
                ? parseFloat(last.volume)
                : Number(last.volume)
              : null;
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
        } else {
          setHoveredBar(null);
        }
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") {
          // Ignored: request was cleanly superseded by another interval/symbol switch
          return;
        }
        const msg = err instanceof Error ? err.message : "Failed to load historical chart bars.";
        setError(msg);
        setBars([]);
        setCoverage(null);
        setPagination(null);
      } finally {
        setIsLoading(false);
      }
    },
    [selectEntity]
  );

  // Trigger history fetch when symbol or interval changes
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchHistory(selectedSymbol, interval);
    return () => {
      if (activeAbortRef.current) {
        activeAbortRef.current.abort();
      }
    };
  }, [selectedSymbol, interval, fetchHistory]);

  // Select instrument handler
  const selectInstrument = useCallback((symbolOrId: string) => {
    setSelectedSymbol(symbolOrId);
  }, []);

  // Interval setter
  const setInterval = useCallback((newInterval: string) => {
    setIntervalState(newInterval);
  }, []);

  // Backfill older history
  const loadOlderHistory = useCallback(async () => {
    if (
      !pagination?.has_more ||
      !pagination.next_cursor ||
      isBackfillingRef.current ||
      !selectedSymbol
    ) {
      return;
    }

    isBackfillingRef.current = true;
    setIsBackfilling(true);

    try {
      const data = await fetchChartHistory({
        symbol: selectedSymbol,
        interval,
        before: pagination.next_cursor,
        limit: 150,
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
  }, [pagination, selectedSymbol, interval]);

  const refreshHistory = useCallback(async () => {
    await fetchHistory(selectedSymbol, interval);
  }, [fetchHistory, selectedSymbol, interval]);

  return {
    selectedSymbol,
    selectedInstrument,
    interval,
    setInterval,
    renderMode,
    setRenderMode,
    intervalSourceKind,
    derivedSourceInterval,
    bars,
    coverage,
    pagination,
    isLoading,
    isBackfilling,
    error,
    hoveredBar,
    selectInstrument,
    loadOlderHistory,
    refreshHistory,
    setHoveredBar,
    availableInstruments,
    isSearching,
  };
}
