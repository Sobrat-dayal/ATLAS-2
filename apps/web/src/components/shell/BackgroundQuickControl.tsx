"use client";

import { useState, useRef, useEffect } from "react";
import { Layers, X, Settings2, Image as ImageIcon, Upload } from "lucide-react";
import { useBackground, AtlasBackgroundSettings } from "@/hooks/background";
import { Button } from "@/design-system/components/Button";

export function BackgroundQuickControl() {
  const { 
    settings, 
    draftSettings, 
    updateDraftSettings, 
    applyDraft, 
    cancelDraft, 
    resetSettings,
    assets,
    uploadImage,
    deleteImage
  } = useBackground();
  
  const [open, setOpen] = useState(false);
  const [advanced, setAdvanced] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Derive active settings
  const active = draftSettings || settings;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        if (draftSettings) cancelDraft();
        setOpen(false);
      }
    };
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open, draftSettings, cancelDraft]);

  const handleToggle = () => {
    if (open && draftSettings) {
      cancelDraft();
    }
    setOpen(!open);
  };

  const handleApply = () => {
    applyDraft();
    setOpen(false);
  };

  const handleSliderChange = (key: keyof AtlasBackgroundSettings, value: number) => {
    updateDraftSettings({ [key]: value });
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
    <div className="relative" ref={ref}>
      <button
        onClick={handleToggle}
        className="flex h-6 w-6 items-center justify-center rounded-sm text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
        title="Background"
        aria-label="Background"
      >
        <Layers className="h-3.5 w-3.5" />
      </button>

      {open && (
        <div className="absolute right-0 top-8 z-50 w-[320px] rounded-md border border-atlas-border-default bg-atlas-surface-1 shadow-xl flex flex-col max-h-[80vh]">
          {/* Header */}
          <div className="flex shrink-0 items-center justify-between border-b border-atlas-border-default px-4 py-3">
            <h3 className="text-xs font-semibold uppercase text-atlas-text-primary flex items-center">
              <ImageIcon className="mr-2 h-3.5 w-3.5" />
              Background
            </h3>
            <button 
              onClick={() => {
                if (draftSettings) cancelDraft();
                setOpen(false);
              }} 
              className="text-atlas-text-muted hover:text-atlas-text-primary"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-5">
            {/* Enable Toggle */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-atlas-text-primary">Enable Background</span>
              <button 
                onClick={() => updateDraftSettings({ enabled: !active.enabled })}
                className={`w-9 h-5 rounded-full transition-colors flex items-center ${active.enabled ? "bg-atlas-positive" : "bg-atlas-surface-3"}`}
              >
                <div className={`w-3.5 h-3.5 rounded-full bg-white mx-0.5 transition-transform ${active.enabled ? "translate-x-4" : ""}`} />
              </button>
            </div>

            {/* Quick Presets / Selection */}
            {active.enabled && (
              <>
                <div>
                  <label className="text-xs font-medium text-atlas-text-secondary mb-2 block">Image</label>
                  {assets.length === 0 ? (
                    <div className="border border-dashed border-atlas-border-default rounded-sm p-4 flex flex-col items-center justify-center text-center">
                      <ImageIcon className="h-6 w-6 text-atlas-text-muted mb-2" />
                      <p className="text-xs text-atlas-text-muted mb-3">No images uploaded</p>
                      <input 
                        type="file" 
                        accept="image/png,image/jpeg,image/webp,image/avif"
                        className="hidden" 
                        ref={fileInputRef}
                        onChange={handleUpload}
                      />
                      <Button variant="secondary" size="xs" onClick={() => fileInputRef.current?.click()}>
                        <Upload className="h-3 w-3 mr-1.5" /> Upload Image
                      </Button>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-2">
                      <select 
                        className="w-full bg-atlas-surface-2 border border-atlas-border-default rounded-sm px-2 py-1.5 text-xs text-atlas-text-primary outline-none focus:ring-1 focus:ring-atlas-accent"
                        value={active.imageId || ""}
                        onChange={(e) => updateDraftSettings({ imageId: e.target.value })}
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
                        <Button variant="secondary" size="xs" onClick={() => fileInputRef.current?.click()} className="flex-1">
                          Upload New
                        </Button>
                        {active.imageId && (
                          <Button variant="danger" size="xs" onClick={() => deleteImage(active.imageId!)}>
                            Delete
                          </Button>
                        )}
                      </div>
                      <div className="flex justify-between text-xs mt-2">
                        <Button 
                          variant="ghost" 
                          size="xs" 
                          className="text-atlas-text-muted hover:text-atlas-text-primary"
                          onClick={() => {
                            updateDraftSettings({
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
                      </div>
                    </div>
                  )}
                </div>

                <div className="space-y-4 pt-2 border-t border-atlas-border-default">
                  {/* Common sliders */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-atlas-text-secondary">Opacity</span>
                      <span className="text-atlas-text-muted font-mono">{active.opacity}%</span>
                    </div>
                    <input 
                      type="range" min="0" max="100" value={active.opacity}
                      onChange={(e) => handleSliderChange('opacity', parseInt(e.target.value))}
                      className="w-full h-1 bg-atlas-surface-3 rounded-full appearance-none outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-atlas-accent"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-atlas-text-secondary">Overlay Readability</span>
                      <span className="text-atlas-text-muted font-mono">{active.overlayOpacity}%</span>
                    </div>
                    <input 
                      type="range" min="0" max="100" value={active.overlayOpacity}
                      onChange={(e) => handleSliderChange('overlayOpacity', parseInt(e.target.value))}
                      className="w-full h-1 bg-atlas-surface-3 rounded-full appearance-none outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-atlas-accent"
                    />
                  </div>
                  
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-atlas-text-secondary">Blur</span>
                      <span className="text-atlas-text-muted font-mono">{active.blur}px</span>
                    </div>
                    <input 
                      type="range" min="0" max="20" value={active.blur}
                      onChange={(e) => handleSliderChange('blur', parseInt(e.target.value))}
                      className="w-full h-1 bg-atlas-surface-3 rounded-full appearance-none outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-atlas-accent"
                    />
                  </div>
                </div>

                {/* Advanced Mode Toggle */}
                <button 
                  onClick={() => setAdvanced(!advanced)}
                  className="flex items-center text-xs text-atlas-text-muted hover:text-atlas-text-primary transition-colors py-1"
                >
                  <Settings2 className="w-3.5 h-3.5 mr-1.5" />
                  {advanced ? "Hide Advanced" : "Show Advanced"}
                </button>

                {advanced && (
                  <div className="space-y-4 pt-2 border-t border-atlas-border-default animate-in slide-in-from-top-2 duration-200">
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="text-atlas-text-secondary">Brightness</span>
                        <span className="text-atlas-text-muted font-mono">{active.brightness}%</span>
                      </div>
                      <input 
                        type="range" min="0" max="150" value={active.brightness}
                        onChange={(e) => handleSliderChange('brightness', parseInt(e.target.value))}
                        className="w-full h-1 bg-atlas-surface-3 rounded-full appearance-none outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-atlas-accent"
                      />
                    </div>
                    
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="text-atlas-text-secondary">Saturation</span>
                        <span className="text-atlas-text-muted font-mono">{active.saturation}%</span>
                      </div>
                      <input 
                        type="range" min="0" max="150" value={active.saturation}
                        onChange={(e) => handleSliderChange('saturation', parseInt(e.target.value))}
                        className="w-full h-1 bg-atlas-surface-3 rounded-full appearance-none outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-atlas-accent"
                      />
                    </div>
                    
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="text-atlas-text-secondary">Grayscale</span>
                        <span className="text-atlas-text-muted font-mono">{active.grayscale}%</span>
                      </div>
                      <input 
                        type="range" min="0" max="100" value={active.grayscale}
                        onChange={(e) => handleSliderChange('grayscale', parseInt(e.target.value))}
                        className="w-full h-1 bg-atlas-surface-3 rounded-full appearance-none outline-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-atlas-accent"
                      />
                    </div>
                    
                    <div className="space-y-1.5">
                      <span className="text-xs text-atlas-text-secondary block mb-1">Fit</span>
                      <select 
                        className="w-full bg-atlas-surface-2 border border-atlas-border-default rounded-sm px-2 py-1 text-xs text-atlas-text-primary outline-none"
                        value={active.fit}
                        onChange={(e) => updateDraftSettings({ fit: e.target.value as any })}
                      >
                        <option value="cover">Cover</option>
                        <option value="contain">Contain</option>
                        <option value="stretch">Stretch</option>
                        <option value="tile">Tile</option>
                      </select>
                    </div>

                    <div className="space-y-1.5">
                      <span className="text-xs text-atlas-text-secondary block mb-1">Position</span>
                      <select 
                        className="w-full bg-atlas-surface-2 border border-atlas-border-default rounded-sm px-2 py-1 text-xs text-atlas-text-primary outline-none"
                        value={active.position}
                        onChange={(e) => updateDraftSettings({ position: e.target.value as any })}
                      >
                        <option value="center">Center</option>
                        <option value="top">Top</option>
                        <option value="bottom">Bottom</option>
                        <option value="left">Left</option>
                        <option value="right">Right</option>
                        <option value="top-left">Top Left</option>
                        <option value="top-right">Top Right</option>
                        <option value="bottom-left">Bottom Left</option>
                        <option value="bottom-right">Bottom Right</option>
                      </select>
                    </div>
                    <div className="space-y-1.5 flex items-center justify-between">
                      <span className="text-xs font-medium text-atlas-text-secondary">Lock Settings</span>
                      <button 
                        onClick={() => updateDraftSettings({ locked: !active.locked })}
                        className={`w-9 h-5 rounded-full transition-colors flex items-center ${active.locked ? "bg-atlas-positive" : "bg-atlas-surface-3"}`}
                      >
                        <div className={`w-3.5 h-3.5 rounded-full bg-white mx-0.5 transition-transform ${active.locked ? "translate-x-4" : ""}`} />
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Footer Actions */}
          <div className="p-3 border-t border-atlas-border-default bg-atlas-surface-2 flex items-center justify-between shrink-0 rounded-b-md">
            <button 
              onClick={resetSettings}
              className="text-xs text-atlas-text-muted hover:text-atlas-text-primary transition-colors"
            >
              Reset
            </button>
            <div className="flex gap-2">
              {draftSettings && (
                <Button variant="ghost" size="xs" onClick={cancelDraft}>
                  Cancel
                </Button>
              )}
              <Button variant="primary" size="xs" onClick={handleApply} disabled={!draftSettings}>
                Apply
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
