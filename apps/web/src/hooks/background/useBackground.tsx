"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useAuth } from "@/hooks/auth/useAuth";
import { AtlasBackgroundSettings, DEFAULT_BACKGROUND_SETTINGS, AtlasBackgroundAsset } from "./types";
import { getBackgroundAsset, listBackgroundAssets, saveBackgroundAsset, deleteBackgroundAsset } from "@/lib/background-db";

const BACKGROUND_STORAGE_KEY = "atlas.background.v1";

interface BackgroundContextState {
  settings: AtlasBackgroundSettings;
  draftSettings: AtlasBackgroundSettings | null; // For previewing before applying
  activeImageUrl: string | null;
  assets: AtlasBackgroundAsset[];
  
  updateSettings: (newSettings: Partial<AtlasBackgroundSettings>) => void;
  updateDraftSettings: (newSettings: Partial<AtlasBackgroundSettings>) => void;
  applyDraft: () => void;
  cancelDraft: () => void;
  resetSettings: () => void;
  
  uploadImage: (file: File) => Promise<void>;
  deleteImage: (id: string) => Promise<void>;
}

const BackgroundContext = createContext<BackgroundContextState | null>(null);

export function BackgroundProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<AtlasBackgroundSettings>(DEFAULT_BACKGROUND_SETTINGS);
  const [draftSettings, setDraftSettings] = useState<AtlasBackgroundSettings | null>(null);
  const [activeImageUrl, setActiveImageUrl] = useState<string | null>(null);
  const [assets, setAssets] = useState<AtlasBackgroundAsset[]>([]);

  const { session } = useAuth();
  const userId = session?.user?.id;
  const storageKey = userId ? `atlas.user.${userId}.${BACKGROUND_STORAGE_KEY}` : BACKGROUND_STORAGE_KEY;

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey) || (!userId ? null : localStorage.getItem(BACKGROUND_STORAGE_KEY));
      if (stored) {
        setSettings({ ...DEFAULT_BACKGROUND_SETTINGS, ...JSON.parse(stored) });
      }
    } catch (e) {
      console.warn("Failed to load background settings from localStorage", e);
    }
    
    // Load asset list
    listBackgroundAssets().then(setAssets).catch(console.error);
  }, [storageKey, userId]);

  // Save to localStorage when settings change
  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(storageKey, JSON.stringify(settings));
    }
  }, [settings, storageKey]);

  // Load image blob URL when active image ID changes
  useEffect(() => {
    const activeSettings = draftSettings || settings;
    let url: string | null = null;
    let cancelled = false;

    if (activeSettings.enabled && activeSettings.imageId) {
      getBackgroundAsset(activeSettings.imageId).then(record => {
        if (cancelled) return;
        if (record && record.blob) {
          url = URL.createObjectURL(record.blob);
          setActiveImageUrl(url);
        } else {
          setActiveImageUrl(null);
        }
      }).catch(err => {
        console.error("Failed to load background image blob", err);
        if (!cancelled) setActiveImageUrl(null);
      });
    } else {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setActiveImageUrl(null);
    }

    return () => {
      cancelled = true;
      if (url) {
        URL.revokeObjectURL(url);
      }
    };
  }, [settings, draftSettings]); // Dependency on draftSettings to support live preview

  const updateSettings = (updates: Partial<AtlasBackgroundSettings>) => {
    setSettings(prev => ({ ...prev, ...updates }));
  };

  const updateDraftSettings = (updates: Partial<AtlasBackgroundSettings>) => {
    setDraftSettings(prev => prev ? { ...prev, ...updates } : { ...settings, ...updates });
  };

  const applyDraft = () => {
    if (draftSettings) {
      setSettings(draftSettings);
      setDraftSettings(null);
    }
  };

  const cancelDraft = () => {
    setDraftSettings(null);
  };

  const resetSettings = () => {
    setSettings(DEFAULT_BACKGROUND_SETTINGS);
    setDraftSettings(null);
  };

  const uploadImage = async (file: File) => {
    if (file.size > 20 * 1024 * 1024) { // 20MB limit
      throw new Error("File too large. Maximum size is 20MB.");
    }

    const id = crypto.randomUUID();
    
    // Create image element to get dimensions
    const url = URL.createObjectURL(file);
    const img = new Image();
    
    await new Promise<void>((resolve, reject) => {
      img.onload = () => resolve();
      img.onerror = () => reject(new Error("Failed to decode image"));
      img.src = url;
    });

    URL.revokeObjectURL(url);

    // Basic validation / dimension warning could go here
    const asset: AtlasBackgroundAsset = {
      id,
      name: file.name,
      mimeType: file.type,
      size: file.size,
      width: img.width,
      height: img.height,
      createdAt: Date.now()
    };

    // For thumbnail, we could draw to canvas and export, but let's keep it simple and just use the full image 
    // or not store a separate thumbnail blob to save time, unless performance demands it.
    await saveBackgroundAsset(asset, file);
    
    const updatedAssets = await listBackgroundAssets();
    setAssets(updatedAssets);
    
    // Auto-select
    setSettings(prev => ({
      ...prev,
      imageId: id,
      enabled: true
    }));
  };

  const deleteImage = async (id: string) => {
    await deleteBackgroundAsset(id);
    const updatedAssets = await listBackgroundAssets();
    setAssets(updatedAssets);
    
    if (settings.imageId === id) {
      setSettings(prev => ({ ...prev, imageId: undefined, enabled: false }));
    }
    if (draftSettings?.imageId === id) {
      setDraftSettings(prev => prev ? { ...prev, imageId: undefined, enabled: false } : null);
    }
  };

  return (
    <BackgroundContext.Provider
      value={{
        settings,
        draftSettings,
        activeImageUrl,
        assets,
        updateSettings,
        updateDraftSettings,
        applyDraft,
        cancelDraft,
        resetSettings,
        uploadImage,
        deleteImage
      }}
    >
      {children}
    </BackgroundContext.Provider>
  );
}

export function useBackground() {
  const context = useContext(BackgroundContext);
  if (!context) {
    throw new Error("useBackground must be used within a BackgroundProvider");
  }
  return context;
}
