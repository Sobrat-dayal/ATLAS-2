"use client";

import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import { useAuth } from "@/hooks/auth/useAuth";
import { usePreferenceSync } from "@/hooks/preferences/PreferenceSyncProvider";


export type AtlasTheme = "system" | "dark" | "light" | "terminal";
export type AtlasDensity = "compact" | "default" | "comfortable";
export type AtlasAccent = "blue" | "cyan" | "emerald" | "amber";

export interface AppearancePreferences {
  version: number;
  theme: AtlasTheme;
  density: AtlasDensity;
  accent: AtlasAccent;
}

export interface AppearanceState extends AppearancePreferences {
  resolvedTheme: "dark" | "light" | "terminal";
  setTheme: (theme: AtlasTheme) => void;
  setDensity: (density: AtlasDensity) => void;
  setAccent: (accent: AtlasAccent) => void;
  resetAppearance: () => void;
}

export const DEFAULT_APPEARANCE: AppearancePreferences = {
  version: 1,
  theme: "dark",
  density: "compact",
  accent: "blue",
};

const AppearanceContext = createContext<AppearanceState | undefined>(undefined);

const STORAGE_KEY = "atlas.appearance.v1";

function resolveSystemTheme(): "dark" | "light" {
  if (typeof window === "undefined") return "dark";
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function isValidAppearance(parsed: any): parsed is AppearancePreferences {
  if (!parsed || typeof parsed !== "object") return false;
  if (parsed.version !== 1) return false;
  if (!["system", "dark", "light", "terminal"].includes(parsed.theme)) return false;
  if (!["compact", "default", "comfortable"].includes(parsed.density)) return false;
  if (!["blue", "cyan", "emerald", "amber"].includes(parsed.accent)) return false;
  return true;
}

export function AppearanceProvider({ children }: { children: ReactNode }) {
  const [prefs, setPrefs] = useState<AppearancePreferences>(DEFAULT_APPEARANCE);
  const [resolvedTheme, setResolvedTheme] = useState<"dark" | "light" | "terminal">("dark");
  const [isClient, setIsClient] = useState(false);
  const { session } = useAuth();
  const { preferences, syncPreference, isLoading } = usePreferenceSync();

  const userKey = session?.user?.id ? `atlas.user.${session.user.id}.appearance.v1` : STORAGE_KEY;
  const backendKey = "global.appearance";

  // Initial load from local cache or backend
  useEffect(() => {
    setIsClient(true);
    let loadedPrefs = DEFAULT_APPEARANCE;
    
    // 1. Try local storage first for immediate render
    try {
      const saved = localStorage.getItem(userKey) || localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (isValidAppearance(parsed)) {
          loadedPrefs = parsed;
        }
      }
    } catch (e) {
      console.warn("Failed to parse appearance state", e);
    }
    
    setPrefs(loadedPrefs);
  }, [userKey]);

  // Sync from backend when it loads
  useEffect(() => {
    if (!isLoading && preferences[backendKey]) {
      const payload = preferences[backendKey].payload;
      if (isValidAppearance(payload)) {
        setPrefs(payload);
      }
    }
  }, [preferences, isLoading]);

  // Update resolved theme when prefs change or OS theme changes
  useEffect(() => {
    if (!isClient) return;

    const updateResolvedTheme = () => {
      if (prefs.theme === "system") {
        setResolvedTheme(resolveSystemTheme());
      } else {
        setResolvedTheme(prefs.theme as "dark" | "light" | "terminal");
      }
    };

    updateResolvedTheme();

    if (prefs.theme === "system") {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: light)");
      const handler = () => updateResolvedTheme();
      mediaQuery.addEventListener("change", handler);
      return () => mediaQuery.removeEventListener("change", handler);
    }
  }, [prefs.theme, isClient]);

  // Apply to DOM & Save
  useEffect(() => {
    if (!isClient) return;
    const root = document.documentElement;
    root.setAttribute("data-theme", resolvedTheme);
    root.setAttribute("data-density", prefs.density);
    root.setAttribute("data-accent", prefs.accent);

    localStorage.setItem(userKey, JSON.stringify(prefs));
  }, [prefs, resolvedTheme, isClient, userKey]);
  
  // Custom setter that also syncs to backend
  const updatePrefs = useCallback((newPrefs: AppearancePreferences) => {
    setPrefs(newPrefs);
    if (session?.access_token) {
      syncPreference(backendKey, 1, newPrefs);
    }
  }, [session, syncPreference, backendKey]);

  const setTheme = useCallback((theme: AtlasTheme) => {
    updatePrefs({ ...prefs, theme });
  }, [prefs, updatePrefs]);
  
  const setDensity = useCallback((density: AtlasDensity) => {
    updatePrefs({ ...prefs, density });
  }, [prefs, updatePrefs]);
  
  const setAccent = useCallback((accent: AtlasAccent) => {
    updatePrefs({ ...prefs, accent });
  }, [prefs, updatePrefs]);
  
  const resetAppearance = useCallback(() => {
    updatePrefs(DEFAULT_APPEARANCE);
  }, [updatePrefs]);

  return (
    <AppearanceContext.Provider
      value={{
        ...prefs,
        resolvedTheme,
        setTheme,
        setDensity,
        setAccent,
        resetAppearance,
      }}
    >
      {children}
    </AppearanceContext.Provider>
  );
}

export function useAppearance() {
  const context = useContext(AppearanceContext);
  if (context === undefined) {
    throw new Error("useAppearance must be used within an AppearanceProvider");
  }
  return context;
}
