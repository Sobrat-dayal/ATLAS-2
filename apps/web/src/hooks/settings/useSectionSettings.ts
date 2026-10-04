import { create } from "zustand";
import { AtlasModuleId } from "@/config/atlas-modules";
import { SECTION_SETTINGS_REGISTRY } from "@/config/section-settings";

interface SectionSettingsDrawerState {
  isOpen: boolean;
  activeModuleId: AtlasModuleId | null;
  openDrawer: (moduleId: AtlasModuleId) => void;
  closeDrawer: () => void;
}

export const useSectionSettingsDrawer = create<SectionSettingsDrawerState>((set) => ({
  isOpen: false,
  activeModuleId: null,
  openDrawer: (moduleId) => set({ isOpen: true, activeModuleId: moduleId }),
  closeDrawer: () => set({ isOpen: false }),
}));

// Local Storage structure for a module
export type ModuleSettingsData = Record<string, unknown>;

function getStorageKey(moduleId: AtlasModuleId) {
  const def = SECTION_SETTINGS_REGISTRY[moduleId];
  if (!def) return null;
  return def.storageNamespace;
}

function loadModuleSettings(moduleId: AtlasModuleId): ModuleSettingsData {
  if (typeof window === "undefined") return {};
  const key = getStorageKey(moduleId);
  if (!key) return {};
  
  try {
    const raw = localStorage.getItem(key);
    if (raw) {
      return JSON.parse(raw) as ModuleSettingsData;
    }
  } catch (e) {
    console.error(`Failed to parse section settings for ${moduleId}`, e);
  }
  return {};
}

function saveModuleSettings(moduleId: AtlasModuleId, data: ModuleSettingsData) {
  if (typeof window === "undefined") return;
  const key = getStorageKey(moduleId);
  if (!key) return;

  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (e) {
    console.error(`Failed to save section settings for ${moduleId}`, e);
  }
}

// Global store for in-memory reactive settings
interface SectionSettingsStore {
  data: Record<string, ModuleSettingsData>;
  getResolvedSetting: (moduleId: AtlasModuleId, settingId: string) => unknown;
  setSetting: (moduleId: AtlasModuleId, settingId: string, value: unknown) => void;
  resetSettings: (moduleId: AtlasModuleId) => void;
  _hydrate: (moduleId: AtlasModuleId) => void;
}

export const useSectionSettingsStore = create<SectionSettingsStore>((set, get) => ({
  data: {},
  
  getResolvedSetting: (moduleId, settingId) => {
    const moduleData = get().data[moduleId];
    if (moduleData && moduleData[settingId] !== undefined) {
      return moduleData[settingId];
    }
    
    // Fallback to default
    const def = SECTION_SETTINGS_REGISTRY[moduleId];
    if (!def) return undefined;
    
    for (const group of def.groups) {
      for (const setting of group.settings) {
        if (setting.id === settingId) {
          return setting.defaultValue;
        }
      }
    }
    
    return undefined;
  },
  
  setSetting: (moduleId, settingId, value) => {
    set((state) => {
      const currentData = state.data[moduleId] || loadModuleSettings(moduleId);
      const newData = { ...currentData, [settingId]: value };
      saveModuleSettings(moduleId, newData);
      return {
        data: {
          ...state.data,
          [moduleId]: newData
        }
      };
    });
  },
  
  resetSettings: (moduleId) => {
    set((state) => {
      saveModuleSettings(moduleId, {});
      return {
        data: {
          ...state.data,
          [moduleId]: {}
        }
      };
    });
  },

  _hydrate: (moduleId) => {
    set((state) => {
      if (state.data[moduleId]) return state; // Already hydrated
      return {
        data: {
          ...state.data,
          [moduleId]: loadModuleSettings(moduleId)
        }
      };
    });
  }
}));

// Hook for components to use settings easily
export function useSectionSetting<T = unknown>(moduleId: AtlasModuleId, settingId: string) {
  // Ensure we are hydrated for this module
  useSectionSettingsStore(state => state._hydrate)(moduleId);
  
  const value = useSectionSettingsStore(state => state.getResolvedSetting(moduleId, settingId)) as T;
  const setSetting = useSectionSettingsStore(state => state.setSetting);
  
  return [value, (val: T) => setSetting(moduleId, settingId, val)] as const;
}

// Hook to access the whole module's settings (reactive)
export function useModuleSettings(moduleId: AtlasModuleId) {
  useSectionSettingsStore(state => state._hydrate)(moduleId);
  
  const data = useSectionSettingsStore(state => state.data[moduleId]) || {};
  const setSetting = useSectionSettingsStore(state => state.setSetting);
  const resetSettings = useSectionSettingsStore(state => state.resetSettings);
  const getResolvedSetting = useSectionSettingsStore(state => state.getResolvedSetting);
  
  return {
    data,
    setSetting: (settingId: string, value: unknown) => setSetting(moduleId, settingId, value),
    resetSettings: () => resetSettings(moduleId),
    getResolvedSetting: (settingId: string) => getResolvedSetting(moduleId, settingId),
  };
}
