"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import { useAuth } from "@/hooks/auth/useAuth";

export interface PreferenceData {
  preference_key: string;
  schema_version: number;
  revision: number;
  payload: Record<string, any>;
  updated_at: string;
}

interface PreferenceSyncState {
  preferences: Record<string, PreferenceData>;
  isLoading: boolean;
  syncPreference: (key: string, schema_version: number, payload: Record<string, any>) => Promise<void>;
}

const PreferenceSyncContext = createContext<PreferenceSyncState | undefined>(undefined);

export function PreferenceSyncProvider({ children }: { children: ReactNode }) {
  const { session } = useAuth();
  const [preferences, setPreferences] = useState<Record<string, PreferenceData>>({});
  const [isLoading, setIsLoading] = useState(true);

  const fetchPreferences = useCallback(async () => {
    if (!session?.access_token) {
      setPreferences({});
      setIsLoading(false);
      return;
    }

    try {
      const res = await fetch("/api/v1/preferences", {
        headers: {
          Authorization: `Bearer ${session.access_token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        const prefMap: Record<string, PreferenceData> = {};
        for (const p of data.preferences) {
          prefMap[p.preference_key] = p;
        }
        setPreferences(prefMap);
      }
    } catch (e) {
      console.error("Failed to fetch preferences:", e);
    } finally {
      setIsLoading(false);
    }
  }, [session]);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  const syncPreference = useCallback(async (key: string, schema_version: number, payload: Record<string, any>) => {
    if (!session?.access_token) return; // Only sync if authenticated

    const expected_revision = preferences[key]?.revision;

    try {
      const res = await fetch(`/api/v1/preferences/${key}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          schema_version,
          expected_revision,
          payload
        })
      });

      if (res.ok) {
        const updatedPref = await res.json();
        setPreferences(prev => ({
          ...prev,
          [key]: updatedPref
        }));
      } else if (res.status === 409) {
        // Conflict - server has newer version. Re-fetch all to get in sync.
        console.warn(`Conflict syncing preference ${key}, refreshing...`);
        fetchPreferences();
      } else {
        console.error(`Failed to sync preference ${key}: ${res.statusText}`);
      }
    } catch (e) {
      console.error(`Error syncing preference ${key}:`, e);
    }
  }, [session, preferences, fetchPreferences]);

  return (
    <PreferenceSyncContext.Provider value={{ preferences, isLoading, syncPreference }}>
      {children}
    </PreferenceSyncContext.Provider>
  );
}

export function usePreferenceSync() {
  const context = useContext(PreferenceSyncContext);
  if (context === undefined) {
    throw new Error("usePreferenceSync must be used within a PreferenceSyncProvider");
  }
  return context;
}
