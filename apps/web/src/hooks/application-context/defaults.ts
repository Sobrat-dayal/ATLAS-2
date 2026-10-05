import { AtlasApplicationContextState, AtlasTimeRange, AtlasMapContext, AtlasGlobalFilters } from "./types";

export const ATLAS_APPLICATION_CONTEXT_VERSION = 1;

export function createDefaultTimeRange(): AtlasTimeRange {
  return {
    mode: "preset",
    preset: "1m", // Canonical default
    start: null,
    end: null,
  };
}

export function createDefaultMapContext(): AtlasMapContext {
  return {
    center: null,
    zoom: null,
    bearing: null,
    pitch: null,
    activeLayerIds: [],
  };
}

export function createDefaultFilters(): AtlasGlobalFilters {
  return {
    entityTypes: [],
    assetClasses: [],
    regions: [],
    tags: [],
  };
}

export function createDefaultApplicationContext(): AtlasApplicationContextState {
  return {
    version: ATLAS_APPLICATION_CONTEXT_VERSION,
    selectedEntityId: null,
    timeRange: createDefaultTimeRange(),
    selectedPortfolioId: null,
    selectedWorkspaceId: null,
    mapContext: createDefaultMapContext(),
    filters: createDefaultFilters(),
    selectedObject: null,
  };
}
