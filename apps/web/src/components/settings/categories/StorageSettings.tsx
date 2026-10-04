"use client";

import React, { useState } from "react";
import { SettingsGroup, SettingsRow } from "../SettingsControls";
import { useBackground } from "@/hooks/background";
import { Button } from "@/design-system/components/Button";

export function StorageSettings() {
  const { assets, deleteImage } = useBackground();
  const [clearing, setClearing] = useState(false);

  const handleClearBackgrounds = async () => {
    if (confirm("This will remove all custom background images stored in this browser.\n\nYour other ATLAS data will not be affected.\n\nAre you sure?")) {
      setClearing(true);
      try {
        for (const asset of assets) {
          await deleteImage(asset.id);
        }
      } catch (e) {
        console.error("Failed to clear backgrounds", e);
      } finally {
        setClearing(false);
      }
    }
  };

  return (
    <div className="space-y-6">
      <SettingsGroup title="Local Browser Data">
        <SettingsRow 
          label="Background Images" 
          description={`${assets.length} image(s) stored in IndexedDB.`}
        />
        <SettingsRow 
          label="Appearance Preferences" 
          description="Stored in localStorage."
        />
        <SettingsRow 
          label="Layout Preferences" 
          description="Stored in localStorage."
        />
      </SettingsGroup>

      <SettingsGroup danger title="Dangerous Actions">
        <SettingsRow 
          label="Clear Background Assets" 
          description="Remove all uploaded background images from local storage."
        >
          <Button 
            variant="danger" 
            size="sm" 
            onClick={handleClearBackgrounds}
            disabled={assets.length === 0 || clearing}
          >
            {clearing ? "Clearing..." : "Clear Backgrounds"}
          </Button>
        </SettingsRow>
      </SettingsGroup>
    </div>
  );
}
