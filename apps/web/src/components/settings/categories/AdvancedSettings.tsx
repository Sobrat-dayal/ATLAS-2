"use client";

import React from "react";
import { SettingsGroup, SettingsRow, SettingsFoundationState } from "../SettingsControls";
import { Button } from "@/design-system/components/Button";
import { useGlobalPreferences } from "@/hooks/settings/useGlobalPreferences";
import { useAppearance } from "@/hooks/appearance";

export function AdvancedSettings() {
  const { resetPreferences } = useGlobalPreferences();
  const { resetAppearance } = useAppearance();

  const handleResetLocalPreferences = () => {
    if (confirm("Reset All Local Preferences?\n\nThis will reset global UI preferences (e.g., Theme, Density) and Settings preferences.\nIt will NOT delete your background assets, saved data, portfolios, or research.\n\nAre you sure?")) {
      resetPreferences();
      resetAppearance();
      // Add other store resets here if necessary
    }
  };

  return (
    <div className="space-y-6">
      <SettingsGroup title="Cache Behavior">
        <SettingsRow label="Data Cache" description="Local caching policy for financial data.">
          <SettingsFoundationState />
        </SettingsRow>
      </SettingsGroup>

      <SettingsGroup title="Diagnostics">
        <SettingsRow label="Provider Diagnostics" description="Run connection tests for connected data providers.">
          <SettingsFoundationState />
        </SettingsRow>
      </SettingsGroup>

      <SettingsGroup danger title="Dangerous Actions">
        <SettingsRow 
          label="Reset All Local Preferences" 
          description="Reset general and appearance settings to their default values. Background images are kept."
        >
          <Button variant="danger" size="sm" onClick={handleResetLocalPreferences}>
            Reset Preferences
          </Button>
        </SettingsRow>
        
        <SettingsRow 
          label="Reset Panel Layouts" 
          description="Restore the default workspace window sizes and positions."
        >
          <SettingsFoundationState message="Not implemented" />
        </SettingsRow>
      </SettingsGroup>
    </div>
  );
}
