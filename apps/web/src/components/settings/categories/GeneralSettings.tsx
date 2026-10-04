"use client";

import React from "react";
import { SettingsGroup, SettingsRow, SettingsFoundationState } from "../SettingsControls";
import { useGlobalPreferences } from "@/hooks/settings/useGlobalPreferences";
import { ATLAS_MODULES_LIST } from "@/config/atlas-modules";

export function GeneralSettings() {
  const { preferences, updatePreference } = useGlobalPreferences();

  return (
    <div className="space-y-6">
      <SettingsGroup title="Startup">
        <SettingsRow 
          label="Start Page" 
          description="The module that opens when launching ATLAS."
        >
          <select 
            value={preferences.startPage} 
            onChange={(e) => updatePreference("startPage", e.target.value)}
            className="bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent"
          >
            {ATLAS_MODULES_LIST.map(mod => (
              <option key={mod.id} value={mod.route}>{mod.label}</option>
            ))}
          </select>
        </SettingsRow>
        
        <SettingsRow 
          label="Restore Last Opened Module" 
          description="Automatically reopen the most recently used module after launch."
        >
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              className="sr-only peer" 
              checked={preferences.restoreLastModule}
              onChange={(e) => updatePreference("restoreLastModule", e.target.checked)}
            />
            <div className="w-9 h-5 bg-atlas-surface-2 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-atlas-accent"></div>
          </label>
        </SettingsRow>
      </SettingsGroup>

      <SettingsGroup title="Date & Time">
        <SettingsRow 
          label="Time Display" 
          description="Choose how times are displayed throughout the application."
        >
          <select 
            value={preferences.timeDisplay} 
            onChange={(e) => updatePreference("timeDisplay", e.target.value as "local" | "utc")}
            className="bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent"
          >
            <option value="local">Local Time</option>
            <option value="utc">UTC</option>
          </select>
        </SettingsRow>
      </SettingsGroup>
      
      <SettingsGroup title="Language & Region">
        <SettingsRow 
          label="Application Language" 
          description="Select the interface language."
        >
          <select 
            value={preferences.language} 
            onChange={(e) => updatePreference("language", e.target.value)}
            className="bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent"
          >
            <option value="en-US">English (US)</option>
          </select>
        </SettingsRow>
      </SettingsGroup>
    </div>
  );
}
