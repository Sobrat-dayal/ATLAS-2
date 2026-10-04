"use client";

import React from "react";
import { SettingsGroup, SettingsRow, SettingsFoundationState } from "../SettingsControls";
import { useGlobalPreferences } from "@/hooks/settings/useGlobalPreferences";

export function AccessibilitySettings() {
  const { preferences, updatePreference } = useGlobalPreferences();

  return (
    <div className="space-y-6">
      <SettingsGroup title="Visual Adjustments">
        <SettingsRow 
          label="Reduced Motion" 
          description="Minimize UI animations and transitions."
        >
          <select 
            value={preferences.reducedMotion} 
            onChange={(e) => updatePreference("reducedMotion", e.target.value as any)}
            className="bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent"
          >
            <option value="system">System Preference</option>
            <option value="on">On</option>
            <option value="off">Off</option>
          </select>
        </SettingsRow>
        
        <SettingsRow 
          label="High Contrast" 
          description="Increase contrast for better readability."
        >
          <SettingsFoundationState />
        </SettingsRow>
        
        <SettingsRow 
          label="Color Vision Assistance" 
          description="Apply color filters for color blindness."
        >
          <SettingsFoundationState />
        </SettingsRow>
      </SettingsGroup>
    </div>
  );
}
