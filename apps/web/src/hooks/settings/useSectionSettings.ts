import { useEffect } from "react";
import { create } from "zustand";
import { AtlasModuleId } from "@/config/atlas-modules";
import { SECTION_SETTINGS_REGISTRY } from "@/config/section-settings";
import { useAuth } from "@/hooks/auth/useAuth";
import { usePreferenceSync } from "@/hooks/preferences/PreferenceSyncProvider";

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

function loadModuleSettings(moduleId: AtlasModuleId, userId?: string): ModuleSettingsData {
  if (typeof window === "undefined") return {};
  const baseKey = getStorageKey(moduleId);
  if (!baseKey) return {};
  const key = userId ? `atlas.user.${userId}.${baseKey}` : baseKey;
  
  try {
    // Try user scoped first, fallback to anon
    let raw = localStorage.getItem(key);
    if (!raw && userId) {
       raw = localStorage.getItem(baseKey);
    }
    if (raw) {
      return JSON.parse(raw) as ModuleSettingsData;
    }
  } catch (e) {
    console.error(`Failed to parse section settings for ${moduleId}`, e);
  }
  return {};
}

function saveModuleSettings(moduleId: AtlasModuleId, data: ModuleSettingsData, userId?: string) {
  if (typeof window === "undefined") return;
  const baseKey = getStorageKey(moduleId);
  if (!baseKey) return;
  const key = userId ? `atlas.user.${userId}.${baseKey}` : baseKey;

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
  setSetting: (moduleId: AtlasModuleId, settingId: string, value: unknown, userId?: string) => void;
  resetSettings: (moduleId: AtlasModuleId, userId?: string) => void;
  _hydrate: (moduleId: AtlasModuleId, userId?: string) => void;
  _setFullData: (moduleId: AtlasModuleId, payload: ModuleSettingsData, userId?: string) => void;
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
  
  setSetting: (moduleId, settingId, value, userId) => {
    set((state) => {
      const currentData = state.data[moduleId] || loadModuleSettings(moduleId, userId);
      const newData = { ...currentData, [settingId]: value };
      saveModuleSettings(moduleId, newData, userId);
      return {
        data: {
          ...state.data,
          [moduleId]: newData
        }
      };
    });
  },
  
  resetSettings: (moduleId, userId) => {
    set((state) => {
      saveModuleSettings(moduleId, {}, userId);
      return {
        data: {
          ...state.data,
          [moduleId]: {}
        }
      };
    });
  },

  _hydrate: (moduleId, userId) => {
    set((state) => {
      if (state.data[moduleId]) return state; // Already hydrated
      return {
        data: {
          ...state.data,
          [moduleId]: loadModuleSettings(moduleId, userId)
        }
      };
    });
  },
  
  _setFullData: (moduleId, payload, userId) => {
     set((state) => {
       saveModuleSettings(moduleId, payload, userId);
       return {
         data: {
           ...state.data,
           [moduleId]: payload
         }
       };
     });
  }
}));

// Hook to access the whole module's settings (reactive)
export function useModuleSettings(moduleId: AtlasModuleId) {
  const { session } = useAuth();
  const userId = session?.user?.id;
  
  useSectionSettingsStore(state => state._hydrate)(moduleId, userId);
  
  const data = useSectionSettingsStore(state => state.data[moduleId]) || {};
  const setSettingStore = useSectionSettingsStore(state => state.setSetting);
  const resetSettingsStore = useSectionSettingsStore(state => state.resetSettings);
  const getResolvedSetting = useSectionSettingsStore(state => state.getResolvedSetting);
  const _setFullData = useSectionSettingsStore(state => state._setFullData);
  
  const { preferences, syncPreference, isLoading } = usePreferenceSync();
  const backendKey = `section.${moduleId}`;
  
  // Sync from backend
  useEffect(() => {
    if (!isLoading && preferences[backendKey]) {
      const payload = preferences[backendKey].payload;
      if (JSON.stringify(payload) !== JSON.stringify(data)) {
        _setFullData(moduleId, payload, userId);
      }
    }
  }, [preferences, isLoading, backendKey, moduleId, data, _setFullData, userId]);
  
  const setSetting = (settingId: string, value: unknown) => {
    setSettingStore(moduleId, settingId, value, userId);
    if (session?.access_token) {
      const newData = { ...data, [settingId]: value };
      syncPreference(backendKey, 1, newData);
    }
  };

  const resetSettings = () => {
    resetSettingsStore(moduleId, userId);
    if (session?.access_token) {
      syncPreference(backendKey, 1, {});
    }
  };
  
  return {
    data,
    setSetting,
    resetSettings,
    getResolvedSetting: (settingId: string) => getResolvedSetting(moduleId, settingId),
  };
}

// Hook for components to use settings easily
export function useSectionSetting<T = unknown>(moduleId: AtlasModuleId, settingId: string) {
  const { getResolvedSetting, setSetting } = useModuleSettings(moduleId);
  const value = getResolvedSetting(settingId) as T;
  
  return [value, (val: T) => setSetting(settingId, val)] as const;
}
