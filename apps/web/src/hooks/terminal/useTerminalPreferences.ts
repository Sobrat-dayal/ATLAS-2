"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchTerminalPreferences, updateTerminalPreferences } from "@/lib/terminal/api";
import { TerminalUserPreferences } from "@/lib/terminal/types";

const DEFAULT_PREFERENCES: TerminalUserPreferences = {
  user_id: "default",
  font_size: 12,
  font_family: "JetBrains Mono, Fira Code, Menlo, monospace",
  line_height: 1.45,
  scrollback_limit: 2000,
  cursor_style: "BLOCK",
  word_wrap: true,
  terminal_height: 320,
  default_tab_type: "ATLAS_CLI",
  restore_previous_tabs: true,
  timestamp_display: true,
  updated_at: new Date().toISOString(),
};

export function useTerminalPreferences() {
  const [preferences, setPreferences] = useState<TerminalUserPreferences>(DEFAULT_PREFERENCES);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetchTerminalPreferences()
      .then((data) => {
        setPreferences(data);
        setLoaded(true);
      })
      .catch((err) => {
        console.warn("Could not fetch remote preferences, using defaults:", err);
        setLoaded(true);
      });
  }, []);

  const handleUpdate = useCallback(async (partial: Partial<TerminalUserPreferences>) => {
    setPreferences((prev) => ({ ...prev, ...partial }));
    try {
      const updated = await updateTerminalPreferences(partial);
      setPreferences(updated);
    } catch (err: unknown) {
      console.warn("Failed to persist terminal preferences:", err);
    }
  }, []);

  return {
    preferences,
    loaded,
    updatePreferences: handleUpdate,
  };
}

