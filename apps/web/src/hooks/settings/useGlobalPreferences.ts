"use client";

import { useState, useEffect } from "react";

export interface GlobalPreferences {
  startPage: string;
  restoreLastModule: boolean;
  timeDisplay: "local" | "utc";
  language: string;
  reducedMotion: "system" | "on" | "off";
}

const DEFAULT_PREFERENCES: GlobalPreferences = {
  startPage: "/home",
  restoreLastModule: false,
  timeDisplay: "local",
  language: "en-US",
  reducedMotion: "system",
};

export function useGlobalPreferences() {
  const [preferences, setPreferences] = useState<GlobalPreferences>(DEFAULT_PREFERENCES);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("atlas.preferences.general.v1");
      if (saved) {
        setPreferences((prev) => ({ ...prev, ...JSON.parse(saved) }));
      }
    } catch (e) {
      console.warn("Failed to load global preferences", e);
    } finally {
      setIsLoaded(true);
    }
  }, []);

  const updatePreference = <K extends keyof GlobalPreferences>(key: K, value: GlobalPreferences[K]) => {
    setPreferences((prev) => {
      const next = { ...prev, [key]: value };
      try {
        localStorage.setItem("atlas.preferences.general.v1", JSON.stringify(next));
      } catch (e) {
        console.error("Failed to save preference", e);
      }
      return next;
    });
  };

  const resetPreferences = () => {
    setPreferences(DEFAULT_PREFERENCES);
    try {
      localStorage.removeItem("atlas.preferences.general.v1");
    } catch (e) {
      console.error("Failed to reset preferences", e);
    }
  };

  return { preferences, updatePreference, resetPreferences, isLoaded };
}
