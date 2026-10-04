"use client";

import React, { useRef } from "react";
import { useAppearance } from "@/hooks/appearance";
import { useBackground, AtlasBackgroundSettings } from "@/hooks/background";
import { SettingsGroup, SettingsRow } from "../SettingsControls";
import { Button } from "@/design-system/components/Button";
import { ImageIcon, Upload } from "lucide-react";

export function AppearanceSettings() {
  const { theme, setTheme, density, setDensity, accent, setAccent, resetAppearance } = useAppearance();

  return (
    <div className="space-y-6">
      <SettingsGroup title="Global Theme">
        <SettingsRow 
          label="Theme" 
          description="Choose the global ATLAS interface theme."
        >
          <select 
            value={theme} 
            onChange={(e) => setTheme(e.target.value as any)}
            className="bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent min-w-[150px]"
          >
            <option value="system">System</option>
            <option value="dark">Dark</option>
            <option value="light">Light</option>
            <option value="terminal">Terminal</option>
          </select>
        </SettingsRow>
        
        <SettingsRow 
          label="Density" 
          description="Reduce spacing to display more information."
        >
          <select 
            value={density} 
            onChange={(e) => setDensity(e.target.value as any)}
            className="bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent min-w-[150px]"
          >
            <option value="compact">Compact</option>
            <option value="default">Default</option>
            <option value="comfortable">Comfortable</option>
          </select>
        </SettingsRow>

        <SettingsRow 
          label="Accent Color" 
          description="Select the primary accent color."
        >
          <select 
            value={accent} 
            onChange={(e) => setAccent(e.target.value as any)}
            className="bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent min-w-[150px]"
          >
            <option value="blue">ATLAS Blue</option>
            <option value="cyan">Cyan</option>
            <option value="emerald">Emerald</option>
            <option value="amber">Amber</option>
          </select>
        </SettingsRow>
      </SettingsGroup>

      <BackgroundSettingsSection />

      <SettingsGroup danger title="Reset">
        <SettingsRow 
          label="Reset Appearance" 
          description="Restore theme, density, and accent to default values."
        >
          <Button variant="danger" size="sm" onClick={() => resetAppearance()}>
            Reset Appearance
          </Button>
        </SettingsRow>
      </SettingsGroup>
    </div>
  );
}

function BackgroundSettingsSection() {
  const { 
    settings, 
    updateDraftSettings, 
    applyDraft, 
    cancelDraft, 
    resetSettings,
    assets,
    uploadImage,
    deleteImage
  } = useBackground();
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // We are bypassing draft mode in the full settings page and just updating settings directly, 
  // or applying draft immediately since it's the "immediate apply" pattern.
  // Actually, useBackground applies drafts when applyDraft is called.
  // We can just call updateDraftSettings and applyDraft immediately.
  const handleUpdate = (updates: Partial<AtlasBackgroundSettings>) => {
    updateDraftSettings(updates);
    // Use setTimeout to allow state to propagate if necessary, or just apply immediately
    setTimeout(() => {
      applyDraft();
    }, 10);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await uploadImage(file);
    } catch (err: any) {
      alert(err.message || "Failed to upload image");
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <SettingsGroup title="Background & Watermark">
      <SettingsRow 
        label="Enable Background" 
        description="Show a custom background image or watermark behind ATLAS."
      >
        <label className="relative inline-flex items-center cursor-pointer">
          <input 
            type="checkbox" 
            className="sr-only peer" 
            checked={settings.enabled}
            onChange={(e) => handleUpdate({ enabled: e.target.checked })}
          />
          <div className="w-9 h-5 bg-atlas-surface-2 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-atlas-accent"></div>
        </label>
      </SettingsRow>

      {settings.enabled && (
        <SettingsRow label="Image Source" vertical>
          {assets.length === 0 ? (
            <div className="border border-dashed border-atlas-border-default rounded-sm p-6 flex flex-col items-center justify-center text-center bg-atlas-surface-1">
              <ImageIcon className="h-8 w-8 text-atlas-text-muted mb-3" />
              <p className="text-sm text-atlas-text-muted mb-4">No images uploaded</p>
              <input 
                type="file" 
                accept="image/png,image/jpeg,image/webp,image/avif"
                className="hidden" 
                ref={fileInputRef}
                onChange={handleUpload}
              />
              <Button variant="secondary" onClick={() => fileInputRef.current?.click()}>
                <Upload className="h-4 w-4 mr-2" /> Upload Image
              </Button>
            </div>
          ) : (
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
              <select 
                className="flex-1 min-w-[200px] bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent"
                value={settings.imageId || ""}
                onChange={(e) => handleUpdate({ imageId: e.target.value })}
              >
                <option value="" disabled>Select an image...</option>
                {assets.map(a => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
              
              <div className="flex gap-2">
                <input 
                  type="file" 
                  accept="image/png,image/jpeg,image/webp,image/avif"
                  className="hidden" 
                  ref={fileInputRef}
                  onChange={handleUpload}
                />
                <Button variant="secondary" onClick={() => fileInputRef.current?.click()}>
                  Upload New
                </Button>
                {settings.imageId && (
                  <Button variant="danger" onClick={() => deleteImage(settings.imageId!)}>
                    Delete
                  </Button>
                )}
              </div>
            </div>
          )}
        </SettingsRow>
      )}

      {settings.enabled && (
        <>
          <SettingsRow label="Opacity" description="Visibility of the background image (0-100%).">
            <input 
              type="range" min="0" max="100" value={settings.opacity}
              onChange={(e) => handleUpdate({ opacity: parseInt(e.target.value) })}
              className="w-full max-w-[200px] h-1.5 bg-atlas-surface-3 rounded-full appearance-none outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-atlas-accent"
            />
          </SettingsRow>
          
          <SettingsRow label="Blur" description="Blur amount applied to the image.">
            <input 
              type="range" min="0" max="20" value={settings.blur}
              onChange={(e) => handleUpdate({ blur: parseInt(e.target.value) })}
              className="w-full max-w-[200px] h-1.5 bg-atlas-surface-3 rounded-full appearance-none outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-atlas-accent"
            />
          </SettingsRow>

          <SettingsRow label="Overlay Readability" description="Opacity of the overlay protecting text readability.">
            <input 
              type="range" min="0" max="100" value={settings.overlayOpacity}
              onChange={(e) => handleUpdate({ overlayOpacity: parseInt(e.target.value) })}
              className="w-full max-w-[200px] h-1.5 bg-atlas-surface-3 rounded-full appearance-none outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-atlas-accent"
            />
          </SettingsRow>
          
          <SettingsRow label="Presets" description="Quickly apply predefined visual filters.">
            <Button 
              variant="secondary" 
              size="sm"
              onClick={() => {
                handleUpdate({
                  opacity: 8,
                  blur: 0,
                  brightness: 70,
                  contrast: 100,
                  saturation: 40,
                  grayscale: 0,
                  fit: "contain",
                  position: "center",
                  overlayOpacity: 50,
                  overlayTone: "dark",
                });
              }}
            >
              Apply Watermark Preset
            </Button>
          </SettingsRow>
        </>
      )}
    </SettingsGroup>
  );
}
