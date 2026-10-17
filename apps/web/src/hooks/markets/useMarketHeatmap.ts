"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  getHeatmapUniverses,
  getMarketHeatmap,
  HeatmapComparisonWindow,
  HeatmapCoverage,
  HeatmapGroupNode,
  HeatmapHierarchyMode,
  HeatmapLeafNode,
  HeatmapUniverseDefinition,
  HeatmapVisualizationMode,
  MarketHeatmapResponse,
} from "@/lib/markets/heatmaps";

export interface UseMarketHeatmapOptions {
  initialUniverseId?: string;
  initialMode?: HeatmapVisualizationMode;
  initialHierarchy?: HeatmapHierarchyMode;
  initialWindow?: HeatmapComparisonWindow;
  initialSector?: string;
}

export interface UseMarketHeatmapResult {
  data: MarketHeatmapResponse | null;
  universes: HeatmapUniverseDefinition[];
  currentUniverse: HeatmapUniverseDefinition | null;
  nodes: HeatmapLeafNode[];
  groups: HeatmapGroupNode[];
  coverage: HeatmapCoverage | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;

  // Selected state & drilldown
  universeId: string;
  setUniverseId: (id: string) => void;
  visualizationMode: HeatmapVisualizationMode;
  setVisualizationMode: (mode: HeatmapVisualizationMode) => void;
  hierarchyMode: HeatmapHierarchyMode;
  setHierarchyMode: (mode: HeatmapHierarchyMode) => void;
  comparisonWindow?: HeatmapComparisonWindow;
  setComparisonWindow: (win?: HeatmapComparisonWindow) => void;
  selectedSector: string;
  setSelectedSector: (sector: string) => void;
  drilldownSector: string | null;
  setDrilldownSector: (sector: string | null) => void;
  selectedNode: HeatmapLeafNode | null;
  setSelectedNode: (node: HeatmapLeafNode | null) => void;
  hoveredNode: HeatmapLeafNode | null;
  setHoveredNode: (node: HeatmapLeafNode | null) => void;
  resetFilters: () => void;
}

export function useMarketHeatmap(
  options?: UseMarketHeatmapOptions
): UseMarketHeatmapResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [universes, setUniverses] = useState<HeatmapUniverseDefinition[]>([]);
  const [universeId, setUniverseId] = useState<string>(
    options?.initialUniverseId || "univ_us_equities"
  );
  const [visualizationMode, setVisualizationMode] = useState<HeatmapVisualizationMode>(
    options?.initialMode || "market_cap_weighted"
  );
  const [hierarchyMode, setHierarchyMode] = useState<HeatmapHierarchyMode>(
    options?.initialHierarchy || "sector"
  );
  const [comparisonWindow, setComparisonWindow] = useState<HeatmapComparisonWindow | undefined>(
    options?.initialWindow
  );
  const [selectedSector, setSelectedSector] = useState<string>(
    options?.initialSector || "all"
  );
  const [drilldownSector, setDrilldownSector] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<HeatmapLeafNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<HeatmapLeafNode | null>(null);

  const [data, setData] = useState<MarketHeatmapResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefetching, setIsRefetching] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  // Load universes catalog once
  useEffect(() => {
    let isMounted = true;
    async function loadUniverses() {
      try {
        const res = await getHeatmapUniverses({ token });
        if (isMounted) {
          setUniverses(res.universes);
        }
      } catch (err) {
        console.warn("Failed to load heatmap universes catalog:", err);
      }
    }
    loadUniverses();
    return () => {
      isMounted = false;
    };
  }, [token]);

  // Adjust defaults when universe changes
  useEffect(() => {
    const targetUniv = universes.find((u) => u.universe_id === universeId);
    if (targetUniv) {
      if (!targetUniv.supported_modes.includes(visualizationMode)) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setVisualizationMode(targetUniv.default_mode);
      }
      if (!targetUniv.supported_hierarchies.includes(hierarchyMode)) {
        setHierarchyMode(targetUniv.default_hierarchy);
      }
      if (comparisonWindow && !targetUniv.supported_windows.includes(comparisonWindow)) {
        setComparisonWindow(targetUniv.default_window);
      }
      setDrilldownSector(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [universeId, universes]);

  const fetchData = useCallback(
    async (isBackground = false) => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      if (!isBackground) {
        setIsLoading(true);
      } else {
        setIsRefetching(true);
      }
      setIsError(false);
      setError(null);

      // Active sector filter: either manual filter or drilldown sector
      const effectiveSector = drilldownSector || (selectedSector !== "all" ? selectedSector : undefined);

      try {
        const res = await getMarketHeatmap({
          universe_id: universeId,
          visualization_mode: visualizationMode,
          hierarchy_mode: hierarchyMode,
          comparison_window: comparisonWindow,
          sector: effectiveSector,
          token,
          signal: controller.signal,
        });

        setData(res);
        setIsLoading(false);
        setIsRefetching(false);
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        setIsError(true);
        setError(err instanceof Error ? err : new Error(String(err)));
        setIsLoading(false);
        setIsRefetching(false);
      }
    },
    [universeId, visualizationMode, hierarchyMode, comparisonWindow, selectedSector, drilldownSector, token]
  );

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData();
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData]);

  const resetFilters = useCallback(() => {
    const targetUniv = universes.find((u) => u.universe_id === universeId);
    setVisualizationMode(targetUniv?.default_mode || "market_cap_weighted");
    setHierarchyMode(targetUniv?.default_hierarchy || "sector");
    setComparisonWindow(targetUniv?.default_window);
    setSelectedSector("all");
    setDrilldownSector(null);
    setSelectedNode(null);
  }, [universeId, universes]);

  const currentUniverse = universes.find((u) => u.universe_id === universeId) || null;

  return {
    data,
    universes,
    currentUniverse,
    nodes: data?.nodes || [],
    groups: data?.groups || [],
    coverage: data?.coverage || null,
    isLoading,
    isError,
    error,
    refetch: () => fetchData(true),
    isRefetching,

    universeId,
    setUniverseId,
    visualizationMode,
    setVisualizationMode,
    hierarchyMode,
    setHierarchyMode,
    comparisonWindow,
    setComparisonWindow,
    selectedSector,
    setSelectedSector,
    drilldownSector,
    setDrilldownSector,
    selectedNode,
    setSelectedNode,
    hoveredNode,
    setHoveredNode,
    resetFilters,
  };
}
