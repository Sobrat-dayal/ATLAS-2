"use client";

import React, { useState } from "react";
import { SettingsGroup, SettingsRow, SettingsFoundationState } from "../SettingsControls";

export function DeveloperSettings() {
  const [devMode, setDevMode] = useState(false);

  return (
    <div className="space-y-6">
      <SettingsGroup title="Developer Tools">
        <SettingsRow 
          label="Developer Mode" 
          description="Enable internal debug UI and experimental features."
        >
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              className="sr-only peer" 
              checked={devMode}
              onChange={(e) => setDevMode(e.target.checked)}
            />
            <div className="w-9 h-5 bg-atlas-surface-2 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-atlas-accent"></div>
          </label>
        </SettingsRow>
      </SettingsGroup>

      {devMode && (
        <SettingsGroup title="Diagnostics">
          <SettingsRow 
            label="ATLAS Version" 
            description="Current build version."
          >
            <span className="text-sm font-mono text-atlas-text-muted">v0.1.0-alpha</span>
          </SettingsRow>
          
          <SettingsRow 
            label="Environment" 
          >
            <span className="text-sm font-mono text-atlas-text-muted">development</span>
          </SettingsRow>
          
          <SettingsRow 
            label="Storage Availability" 
          >
            <span className="text-sm font-mono text-atlas-positive">Available</span>
          </SettingsRow>
        </SettingsGroup>
      )}
      
      <SettingsGroup title="Experimental Features">
        <SettingsRow label="Feature Flags" description="Enable or disable features in development.">
          <SettingsFoundationState message="No active experiments" />
        </SettingsRow>
      </SettingsGroup>
    </div>
  );
}
