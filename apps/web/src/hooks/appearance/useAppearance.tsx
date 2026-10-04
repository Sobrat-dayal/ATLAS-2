"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";

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

  // Initial load
  useEffect(() => {
    setIsClient(true);
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (isValidAppearance(parsed)) {
          setPrefs(parsed);
          return;
        }
      }
    } catch (e) {
      console.warn("Failed to parse appearance state", e);
    }
    // Fallback to default if invalid/missing
    setPrefs(DEFAULT_APPEARANCE);
  }, []);

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

    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  }, [prefs, resolvedTheme, isClient]);

  const setTheme = (theme: AtlasTheme) => setPrefs((prev) => ({ ...prev, theme }));
  const setDensity = (density: AtlasDensity) => setPrefs((prev) => ({ ...prev, density }));
  const setAccent = (accent: AtlasAccent) => setPrefs((prev) => ({ ...prev, accent }));
  const resetAppearance = () => setPrefs(DEFAULT_APPEARANCE);

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
