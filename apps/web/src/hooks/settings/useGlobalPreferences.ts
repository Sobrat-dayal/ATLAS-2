"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/hooks/auth/useAuth";
import { usePreferenceSync } from "@/hooks/preferences/PreferenceSyncProvider";

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
  
  const { session } = useAuth();
  const { preferences: syncPrefs, syncPreference, isLoading } = usePreferenceSync();
  
  const STORAGE_KEY = "atlas.preferences.general.v1";
  const userKey = session?.user?.id ? `atlas.user.${session.user.id}.preferences.general.v1` : STORAGE_KEY;
  const backendKey = "global.general";

  useEffect(() => {
    let loadedPrefs = DEFAULT_PREFERENCES;
    try {
      const saved = localStorage.getItem(userKey) || localStorage.getItem(STORAGE_KEY);
      if (saved) {
        loadedPrefs = { ...DEFAULT_PREFERENCES, ...JSON.parse(saved) };
      }
    } catch (e) {
      console.warn("Failed to load global preferences", e);
    } 
    setPreferences(loadedPrefs);
    setIsLoaded(true);
  }, [userKey]);

  useEffect(() => {
    if (!isLoading && syncPrefs[backendKey]) {
      const payload = syncPrefs[backendKey].payload;
      setPreferences(prev => ({ ...prev, ...payload }));
    }
  }, [syncPrefs, isLoading]);

  const updatePreference = useCallback(<K extends keyof GlobalPreferences>(key: K, value: GlobalPreferences[K]) => {
    setPreferences((prev) => {
      const next = { ...prev, [key]: value };
      try {
        localStorage.setItem(userKey, JSON.stringify(next));
      } catch (e) {
        console.error("Failed to save preference", e);
      }
      
      if (session?.access_token) {
        syncPreference(backendKey, 1, next);
      }
      
      return next;
    });
  }, [userKey, session, syncPreference]);

  const resetPreferences = useCallback(() => {
    setPreferences(DEFAULT_PREFERENCES);
    try {
      localStorage.removeItem(userKey);
    } catch (e) {
      console.error("Failed to reset preferences", e);
    }
    if (session?.access_token) {
      syncPreference(backendKey, 1, DEFAULT_PREFERENCES);
    }
  }, [userKey, session, syncPreference]);

  return { preferences, updatePreference, resetPreferences, isLoaded };
}

