"use client";

/**
 * React hook managing technical indicator catalog and active instance calculations (Stage 69).
 */

import { useCallback, useEffect, useRef, useState } from "react";
import {
  ChartInstrumentMetadata,
  IndicatorCalculationRequest,
  IndicatorCalculationResult,
  IndicatorDefinition,
  IndicatorInstanceConfig,
  calculateIndicators,
  fetchIndicatorCatalog,
} from "@/lib/charts";

const COLOR_PALETTE = [
  "#38bdf8", // Sky 400
  "#10b981", // Emerald 500
  "#f59e0b", // Amber 500
  "#ec4899", // Pink 500
  "#a855f7", // Purple 500
  "#6366f1", // Indigo 500
];

export interface UseIndicatorsProps {
  instrument: ChartInstrumentMetadata | null;
  interval: string;
  barsCount: number;
}

export function useIndicators({ instrument, interval, barsCount }: UseIndicatorsProps) {
  const [catalog, setCatalog] = useState<IndicatorDefinition[]>([]);
  const [isLoadingCatalog, setIsLoadingCatalog] = useState(true);
  const [activeInstances, setActiveInstances] = useState<IndicatorInstanceConfig[]>([]);
  const [results, setResults] = useState<IndicatorCalculationResult[]>([]);
  const [isCalculating, setIsCalculating] = useState(false);
  const [calculationError, setCalculationError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const nextInstanceIdRef = useRef<number>(1);

  // 1. Load indicator catalog on mount
  useEffect(() => {
    let isMounted = true;

    fetchIndicatorCatalog()
      .then((defs) => {
        if (isMounted) {
          setCatalog(defs);
          setIsLoadingCatalog(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          console.error("Failed to load indicator catalog:", err);
          setIsLoadingCatalog(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // 2. Add an indicator instance
  const addIndicator = useCallback(
    (indicatorId: string, initialParams?: Record<string, unknown>) => {
      const defn = catalog.find((d) => d.indicator_id === indicatorId);
      if (!defn) return;

      if (activeInstances.length >= 5) {
        alert("Maximum 5 active indicators allowed simultaneously.");
        return;
      }

      const instanceId = `${indicatorId.replace("atlas.", "")}-${nextInstanceIdRef.current++}`;

      // Assemble default parameters from definition
      const params: Record<string, unknown> = {};
      for (const p of defn.parameters) {
        params[p.name] = p.default;
      }
      if (initialParams) {
        Object.assign(params, initialParams);
      }

      // Assign round-robin color from palette
      const colorIndex = activeInstances.length % COLOR_PALETTE.length;
      const color = COLOR_PALETTE[colorIndex] || defn.default_color;

      const newInstance: IndicatorInstanceConfig = {
        instance_id: instanceId,
        indicator_id: defn.indicator_id,
        version: defn.version,
        parameters: params,
        visible: true,
        color,
        line_width: defn.default_line_width,
      };

      setActiveInstances((prev) => [...prev, newInstance]);
    },
    [catalog, activeInstances.length]
  );

  // 3. Update an existing indicator instance
  const updateInstance = useCallback(
    (instanceId: string, updates: Partial<IndicatorInstanceConfig>) => {
      setActiveInstances((prev) =>
        prev.map((inst) => (inst.instance_id === instanceId ? { ...inst, ...updates } : inst))
      );
    },
    []
  );

  // 4. Toggle visibility of an instance
  const toggleVisibility = useCallback((instanceId: string) => {
    setActiveInstances((prev) =>
      prev.map((inst) =>
        inst.instance_id === instanceId ? { ...inst, visible: !inst.visible } : inst
      )
    );
  }, []);

  // 5. Remove an indicator instance
  const removeInstance = useCallback((instanceId: string) => {
    setActiveInstances((prev) => prev.filter((inst) => inst.instance_id !== instanceId));
    setResults((prev) => prev.filter((r) => r.instance_id !== instanceId));
  }, []);

  // 6. Recalculate indicators when instances, instrument, interval, or bars change
  useEffect(() => {
    if (activeInstances.length === 0 || !instrument || barsCount === 0) {
      queueMicrotask(() => {
        setResults([]);
        setIsCalculating(false);
      });
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    queueMicrotask(() => {
      setIsCalculating(true);
      setCalculationError(null);
    });

    const request: IndicatorCalculationRequest = {
      instrument_id: instrument.entity_id,
      symbol: instrument.display_symbol,
      interval,
      instances: activeInstances,
    };

    calculateIndicators(request, abortController.signal)
      .then((response) => {
        if (!abortController.signal.aborted) {
          setResults(response.results);
          setIsCalculating(false);
        }
      })
      .catch((err) => {
        if (!abortController.signal.aborted) {
          console.error("Indicator calculation error:", err);
          setCalculationError(err instanceof Error ? err.message : String(err));
          setIsCalculating(false);
        }
      });

    return () => {
      abortController.abort();
    };
  }, [activeInstances, instrument, interval, barsCount]);

  return {
    catalog,
    isLoadingCatalog,
    activeInstances,
    results,
    isCalculating,
    calculationError,
    addIndicator,
    updateInstance,
    toggleVisibility,
    removeInstance,
  };
}
