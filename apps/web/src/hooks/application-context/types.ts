import { EntitySummary, SelectedEntityStatus } from "../entity/SelectedEntityProvider";

export type AtlasTimeRangePreset = 
  | "1d" | "5d" | "1m" | "3m" | "6m" | "ytd" | "1y" | "5y" | "max" | "today";

export interface AtlasTimeRange {
  mode: "preset" | "custom";
  preset: AtlasTimeRangePreset | null;
  start: string | null;
  end: string | null;
}

export interface AtlasMapContext {
  center: { latitude: number; longitude: number } | null;
  zoom: number | null;
  bearing: number | null;
  pitch: number | null;
  activeLayerIds: string[];
}

export interface AtlasGlobalFilters {
  entityTypes?: string[];
  regions?: string[];
  assetClasses?: string[];
  tags?: string[];
}

export interface AtlasSelectedObjectRef {
  kind: string;
  id: string;
}

export interface AtlasApplicationContextState {
  version: number;
  selectedEntityId: string | null;
  timeRange: AtlasTimeRange;
  selectedPortfolioId: string | null;
  selectedWorkspaceId: string | null;
  mapContext: AtlasMapContext;
  filters: AtlasGlobalFilters;
  selectedObject: AtlasSelectedObjectRef | null;
}

export interface AtlasApplicationContextSnapshot extends AtlasApplicationContextState {
  activeModuleId?: string;
}

export interface AtlasApplicationContextValue {
  // Snapshot
  snapshot: AtlasApplicationContextSnapshot;
  
  // Entity Slice
  selectedEntityId: string | null;
  selectedEntity: EntitySummary | null;
  selectedEntityStatus: SelectedEntityStatus;
  selectedEntityError: Error | null;
  selectEntity: (entityId: string) => void;
  clearSelectedEntity: () => void;
  refreshSelectedEntity: () => Promise<void>;

  // Time Range Slice
  timeRange: AtlasTimeRange;
  setTimeRangePreset: (preset: AtlasTimeRangePreset) => void;
  setCustomTimeRange: (start: string, end: string) => void;
  resetTimeRange: () => void;

  // Portfolio Foundation
  selectedPortfolioId: string | null;
  setSelectedPortfolioId: (id: string) => void;
  clearSelectedPortfolio: () => void;

  // Workspace Foundation
  selectedWorkspaceId: string | null;
  setSelectedWorkspaceId: (id: string) => void;
  clearSelectedWorkspace: () => void;

  // Map Foundation
  mapContext: AtlasMapContext;
  setMapViewport: (center: { latitude: number; longitude: number }, zoom?: number, bearing?: number, pitch?: number) => void;
  setMapActiveLayers: (layerIds: string[]) => void;
  resetMapContext: () => void;

  // Filter Foundation
  filters: AtlasGlobalFilters;
  setGlobalEntityTypeFilter: (entityTypes: string[]) => void;
  setGlobalAssetClassFilter: (assetClasses: string[]) => void;
  resetGlobalFilters: () => void;

  // Selected Object Foundation
  selectedObject: AtlasSelectedObjectRef | null;
  setSelectedObject: (kind: string, id: string) => void;
  clearSelectedObject: () => void;

  // Global Actions
  resetApplicationContext: () => void;
}
