"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useMemo,
  useRef,
  ReactNode,
} from "react";
import { useAuth } from "@/hooks/auth/useAuth";
import { 
  AtlasApplicationContextValue, 
  AtlasApplicationContextState,
  AtlasTimeRangePreset,
  AtlasTimeRange,
  AtlasMapContext,
  AtlasGlobalFilters
} from "./types";
import { EntitySummary, SelectedEntityStatus } from "../entity/SelectedEntityProvider";
import { createDefaultApplicationContext } from "./defaults";
import { readApplicationContextStorage, writeApplicationContextStorage, clearApplicationContextStorage } from "./storage";

const GlobalApplicationContext = createContext<AtlasApplicationContextValue | undefined>(undefined);

function isValidUUID(uuid: string) {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

export function GlobalApplicationContextProvider({ children }: { children: ReactNode }) {
  const { session } = useAuth();
  
  // Base State
  const [state, setState] = useState<AtlasApplicationContextState>(createDefaultApplicationContext());
  
  // Derived Entity State
  const [selectedEntity, setSelectedEntity] = useState<EntitySummary | null>(null);
  const [selectedEntityStatus, setSelectedEntityStatus] = useState<SelectedEntityStatus>("idle");
  const [selectedEntityError, setSelectedEntityError] = useState<Error | null>(null);

  const lastUserIdRef = useRef<string | null>(null);
  const activeFetchIdRef = useRef<string | null>(null);
  const mountedRef = useRef(false);

  // 1. Initial Mount & Session Restore
  useEffect(() => {
    const restoredState = readApplicationContextStorage();
    setState(restoredState);
    mountedRef.current = true;
  }, []);

  // Sync state to storage whenever it changes (after mount)
  useEffect(() => {
    if (mountedRef.current) {
      writeApplicationContextStorage(state);
    }
  }, [state]);

  // 2. Auth Lifecycle Handlers
  useEffect(() => {
    const currentUserId = session?.user?.id || null;
    if (lastUserIdRef.current !== null && currentUserId !== lastUserIdRef.current) {
      // Account switch or logout occurred -> clear semantic context
      const defaults = createDefaultApplicationContext();
      setState(defaults);
      setSelectedEntity(null);
      setSelectedEntityStatus("idle");
      setSelectedEntityError(null);
      clearApplicationContextStorage();
    }
    lastUserIdRef.current = currentUserId;
  }, [session]);

  // 3. Entity Data Fetching
  const fetchEntity = useCallback(async (entityId: string, forceRefetch = false) => {
    if (!session?.access_token) return;

    if (!forceRefetch && selectedEntity?.entity_id === entityId) {
      return;
    }

    activeFetchIdRef.current = entityId;
    setSelectedEntityStatus("loading");
    setSelectedEntityError(null);

    try {
      const res = await fetch(`/api/v1/entities/${entityId}`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (activeFetchIdRef.current !== entityId) return;

      if (res.ok) {
        const data = await res.json();
        setSelectedEntity(data);
        setSelectedEntityStatus("ready");
      } else if (res.status === 404) {
        // Stale or invalid entity ID
        setState(prev => ({ ...prev, selectedEntityId: null }));
        setSelectedEntity(null);
        setSelectedEntityStatus("idle");
      } else if (res.status === 401 || res.status === 403) {
        throw new Error(`Authorization failed: ${res.status}`);
      } else {
        throw new Error(`Failed to load entity: ${res.status}`);
      }
    } catch (err) {
      if (activeFetchIdRef.current === entityId) {
        setSelectedEntityError(err instanceof Error ? err : new Error("Network or server error"));
        setSelectedEntityStatus("error");
      }
    }
  }, [session?.access_token, selectedEntity?.entity_id]);

  useEffect(() => {
    if (state.selectedEntityId) {
      fetchEntity(state.selectedEntityId);
    } else {
      setSelectedEntity(null);
      setSelectedEntityStatus("idle");
      setSelectedEntityError(null);
      activeFetchIdRef.current = null;
    }
  }, [state.selectedEntityId, fetchEntity]);

  // 4. Public Actions - Entity
  const selectEntity = useCallback((entityId: string) => {
    if (!isValidUUID(entityId)) return;
    setState(prev => prev.selectedEntityId === entityId ? prev : { ...prev, selectedEntityId: entityId });
  }, []);

  const clearSelectedEntity = useCallback(() => {
    setState(prev => prev.selectedEntityId === null ? prev : { ...prev, selectedEntityId: null });
  }, []);

  const refreshSelectedEntity = useCallback(async () => {
    if (state.selectedEntityId) {
      await fetchEntity(state.selectedEntityId, true);
    }
  }, [state.selectedEntityId, fetchEntity]);

  // 5. Public Actions - Time Range
  const setTimeRangePreset = useCallback((preset: AtlasTimeRangePreset) => {
    setState(prev => ({
      ...prev,
      timeRange: { mode: "preset", preset, start: null, end: null }
    }));
  }, []);

  const setCustomTimeRange = useCallback((start: string, end: string) => {
    if (new Date(start) > new Date(end)) return; // Validation
    setState(prev => ({
      ...prev,
      timeRange: { mode: "custom", preset: null, start, end }
    }));
  }, []);

  const resetTimeRange = useCallback(() => {
    setState(prev => ({
      ...prev,
      timeRange: createDefaultApplicationContext().timeRange
    }));
  }, []);

  // 6. Public Actions - Portfolio Foundation
  const setSelectedPortfolioId = useCallback((id: string) => {
    setState(prev => ({ ...prev, selectedPortfolioId: id }));
  }, []);
  const clearSelectedPortfolio = useCallback(() => {
    setState(prev => ({ ...prev, selectedPortfolioId: null }));
  }, []);

  // 7. Public Actions - Workspace Foundation
  const setSelectedWorkspaceId = useCallback((id: string) => {
    setState(prev => ({ ...prev, selectedWorkspaceId: id }));
  }, []);
  const clearSelectedWorkspace = useCallback(() => {
    setState(prev => ({ ...prev, selectedWorkspaceId: null }));
  }, []);

  // 8. Public Actions - Map Foundation
  const setMapViewport = useCallback((center: { latitude: number; longitude: number }, zoom?: number, bearing?: number, pitch?: number) => {
    if (center.latitude < -90 || center.latitude > 90) return;
    if (center.longitude < -180 || center.longitude > 180) return;
    setState(prev => ({
      ...prev,
      mapContext: {
        ...prev.mapContext,
        center,
        ...(zoom !== undefined && { zoom }),
        ...(bearing !== undefined && { bearing }),
        ...(pitch !== undefined && { pitch })
      }
    }));
  }, []);
  const setMapActiveLayers = useCallback((layerIds: string[]) => {
    setState(prev => ({
      ...prev,
      mapContext: { ...prev.mapContext, activeLayerIds: layerIds }
    }));
  }, []);
  const resetMapContext = useCallback(() => {
    setState(prev => ({ ...prev, mapContext: createDefaultApplicationContext().mapContext }));
  }, []);

  // 9. Public Actions - Filters Foundation
  const setGlobalEntityTypeFilter = useCallback((entityTypes: string[]) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, entityTypes }
    }));
  }, []);
  const setGlobalAssetClassFilter = useCallback((assetClasses: string[]) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, assetClasses }
    }));
  }, []);
  const resetGlobalFilters = useCallback(() => {
    setState(prev => ({ ...prev, filters: createDefaultApplicationContext().filters }));
  }, []);

  // 10. Public Actions - Selected Object Foundation
  const setSelectedObject = useCallback((kind: string, id: string) => {
    setState(prev => ({ ...prev, selectedObject: { kind, id } }));
  }, []);
  const clearSelectedObject = useCallback(() => {
    setState(prev => ({ ...prev, selectedObject: null }));
  }, []);

  // 11. Reset Application Context
  const resetApplicationContext = useCallback(() => {
    const defaults = createDefaultApplicationContext();
    setState(defaults);
    setSelectedEntity(null);
    setSelectedEntityStatus("idle");
    setSelectedEntityError(null);
  }, []);

  const value = useMemo<AtlasApplicationContextValue>(() => ({
    snapshot: { ...state },
    
    selectedEntityId: state.selectedEntityId,
    selectedEntity,
    selectedEntityStatus,
    selectedEntityError,
    selectEntity,
    clearSelectedEntity,
    refreshSelectedEntity,

    timeRange: state.timeRange,
    setTimeRangePreset,
    setCustomTimeRange,
    resetTimeRange,

    selectedPortfolioId: state.selectedPortfolioId,
    setSelectedPortfolioId,
    clearSelectedPortfolio,

    selectedWorkspaceId: state.selectedWorkspaceId,
    setSelectedWorkspaceId,
    clearSelectedWorkspace,

    mapContext: state.mapContext,
    setMapViewport,
    setMapActiveLayers,
    resetMapContext,

    filters: state.filters,
    setGlobalEntityTypeFilter,
    setGlobalAssetClassFilter,
    resetGlobalFilters,

    selectedObject: state.selectedObject,
    setSelectedObject,
    clearSelectedObject,

    resetApplicationContext
  }), [
    state, selectedEntity, selectedEntityStatus, selectedEntityError,
    selectEntity, clearSelectedEntity, refreshSelectedEntity,
    setTimeRangePreset, setCustomTimeRange, resetTimeRange,
    setSelectedPortfolioId, clearSelectedPortfolio,
    setSelectedWorkspaceId, clearSelectedWorkspace,
    setMapViewport, setMapActiveLayers, resetMapContext,
    setGlobalEntityTypeFilter, setGlobalAssetClassFilter, resetGlobalFilters,
    setSelectedObject, clearSelectedObject,
    resetApplicationContext
  ]);

  return (
    <GlobalApplicationContext.Provider value={value}>
      {children}
    </GlobalApplicationContext.Provider>
  );
}

export function useAtlasApplicationContext(): AtlasApplicationContextValue {
  const context = useContext(GlobalApplicationContext);
  if (context === undefined) {
    throw new Error("useAtlasApplicationContext must be used within a GlobalApplicationContextProvider");
  }
  return context;
}
