import { AtlasApplicationContextState } from "./types";
import { createDefaultApplicationContext, ATLAS_APPLICATION_CONTEXT_VERSION } from "./defaults";

const STORAGE_KEY = "atlas.applicationContext.v1";
const OLD_ENTITY_STORAGE_KEY = "atlas.selectedEntity.v1";

function isValidUUID(uuid: string) {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

export function writeApplicationContextStorage(state: AtlasApplicationContextState) {
  if (typeof sessionStorage === "undefined") return;
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    console.warn("Failed to persist application context to sessionStorage", e);
  }
}

export function clearApplicationContextStorage() {
  if (typeof sessionStorage === "undefined") return;
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch (e) {
    console.warn("Failed to clear application context from sessionStorage", e);
  }
}

export function readApplicationContextStorage(): AtlasApplicationContextState {
  const defaults = createDefaultApplicationContext();
  
  if (typeof sessionStorage === "undefined") {
    return defaults;
  }

  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    
    // Migration: If no new key, check old key
    if (!raw) {
      const oldRaw = sessionStorage.getItem(OLD_ENTITY_STORAGE_KEY);
      if (oldRaw) {
        try {
          const oldParsed = JSON.parse(oldRaw);
          if (oldParsed.version === 1 && oldParsed.entityId && isValidUUID(oldParsed.entityId)) {
            const migrated = {
              ...defaults,
              selectedEntityId: oldParsed.entityId
            };
            writeApplicationContextStorage(migrated);
            sessionStorage.removeItem(OLD_ENTITY_STORAGE_KEY);
            return migrated;
          }
        } catch (e) {
          // Ignore corrupt old storage
        }
        sessionStorage.removeItem(OLD_ENTITY_STORAGE_KEY);
      }
      return defaults;
    }

    const parsed = JSON.parse(raw);
    
    if (parsed.version !== ATLAS_APPLICATION_CONTEXT_VERSION) {
      clearApplicationContextStorage();
      return defaults;
    }

    // Partial recovery validation
    const state: AtlasApplicationContextState = { ...defaults };
    
    if (parsed.selectedEntityId === null || (typeof parsed.selectedEntityId === "string" && isValidUUID(parsed.selectedEntityId))) {
      state.selectedEntityId = parsed.selectedEntityId;
    }

    if (parsed.timeRange && typeof parsed.timeRange === "object") {
      if (parsed.timeRange.mode === "preset" || parsed.timeRange.mode === "custom") {
        state.timeRange.mode = parsed.timeRange.mode;
        state.timeRange.preset = parsed.timeRange.preset;
        state.timeRange.start = parsed.timeRange.start;
        state.timeRange.end = parsed.timeRange.end;
      }
    }

    if (parsed.selectedPortfolioId === null || typeof parsed.selectedPortfolioId === "string") {
      state.selectedPortfolioId = parsed.selectedPortfolioId;
    }
    
    if (parsed.selectedWorkspaceId === null || typeof parsed.selectedWorkspaceId === "string") {
      state.selectedWorkspaceId = parsed.selectedWorkspaceId;
    }

    if (parsed.mapContext && typeof parsed.mapContext === "object") {
      if (parsed.mapContext.center && typeof parsed.mapContext.center.latitude === "number" && typeof parsed.mapContext.center.longitude === "number") {
         if (parsed.mapContext.center.latitude >= -90 && parsed.mapContext.center.latitude <= 90 &&
             parsed.mapContext.center.longitude >= -180 && parsed.mapContext.center.longitude <= 180) {
             state.mapContext.center = parsed.mapContext.center;
         }
      }
      if (typeof parsed.mapContext.zoom === "number") state.mapContext.zoom = parsed.mapContext.zoom;
      if (typeof parsed.mapContext.bearing === "number") state.mapContext.bearing = parsed.mapContext.bearing;
      if (typeof parsed.mapContext.pitch === "number") state.mapContext.pitch = parsed.mapContext.pitch;
      if (Array.isArray(parsed.mapContext.activeLayerIds)) {
        state.mapContext.activeLayerIds = parsed.mapContext.activeLayerIds.filter((id: unknown) => typeof id === "string");
      }
    }

    if (parsed.filters && typeof parsed.filters === "object") {
      if (Array.isArray(parsed.filters.entityTypes)) state.filters.entityTypes = parsed.filters.entityTypes;
      if (Array.isArray(parsed.filters.assetClasses)) state.filters.assetClasses = parsed.filters.assetClasses;
      if (Array.isArray(parsed.filters.regions)) state.filters.regions = parsed.filters.regions;
      if (Array.isArray(parsed.filters.tags)) state.filters.tags = parsed.filters.tags;
    }

    if (parsed.selectedObject && typeof parsed.selectedObject === "object") {
      if (typeof parsed.selectedObject.kind === "string" && typeof parsed.selectedObject.id === "string") {
        state.selectedObject = parsed.selectedObject;
      }
    }

    return state;

  } catch (e) {
    // Corrupt root payload
    clearApplicationContextStorage();
    return defaults;
  }
}
