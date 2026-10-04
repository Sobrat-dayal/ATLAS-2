"use client";

import React, { useEffect } from "react";
import { X, RotateCcw } from "lucide-react";
import { useSectionSettingsDrawer, useModuleSettings } from "@/hooks/settings/useSectionSettings";
import { SECTION_SETTINGS_REGISTRY, SectionSettingDefinition } from "@/config/section-settings";
import { Button } from "@/design-system/components/Button";
import { SettingsFoundationState, SettingsRow } from "./SettingsControls";

// An internal control renderer based on the definition type
function SettingControl({ 
  definition, 
  value, 
  onChange 
}: { 
  definition: SectionSettingDefinition; 
  value: unknown; 
  onChange: (val: unknown) => void;
}) {
  if (definition.type === "foundation" || definition.availability === "foundation") {
    return <SettingsFoundationState message="Foundation" />;
  }

  if (definition.type === "boolean") {
    return (
      <label className="relative inline-flex items-center cursor-pointer">
        <input 
          type="checkbox" 
          className="sr-only peer" 
          checked={Boolean(value)}
          onChange={(e) => onChange(e.target.checked)}
        />
        <div className="w-9 h-5 bg-atlas-surface-2 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-atlas-accent"></div>
      </label>
    );
  }

  if (definition.type === "select" && definition.options) {
    return (
      <select 
        value={String(value)} 
        onChange={(e) => {
          // try to convert numbers if necessary
          const val = e.target.value;
          const isNumeric = !isNaN(Number(val)) && val.trim() !== '';
          onChange(isNumeric ? Number(val) : val);
        }}
        className="bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent"
      >
        {definition.options.map((opt, i) => (
          <option key={i} value={String(opt.value)}>{opt.label}</option>
        ))}
      </select>
    );
  }
  
  if (definition.type === "number") {
    return (
      <input 
        type="number"
        value={Number(value)}
        onChange={(e) => onChange(Number(e.target.value))}
        min={definition.min}
        max={definition.max}
        step={definition.step}
        className="bg-atlas-bg-0 border border-atlas-border-default rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent w-24"
      />
    );
  }

  return <div className="text-xs text-atlas-text-muted">Unsupported type</div>;
}

export function SectionSettingsDrawer() {
  const { isOpen, activeModuleId, closeDrawer } = useSectionSettingsDrawer();

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        closeDrawer();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, closeDrawer]);

  if (!isOpen || !activeModuleId) return null;

  const def = SECTION_SETTINGS_REGISTRY[activeModuleId];
  if (!def) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/40 z-50 transition-opacity"
        onClick={closeDrawer}
      />
      
      {/* Drawer */}
      <div className="fixed inset-y-0 right-0 w-full max-w-sm bg-atlas-bg-0 border-l border-atlas-border-subtle shadow-2xl z-50 flex flex-col transform transition-transform duration-200 ease-in-out">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-atlas-border-subtle shrink-0">
          <div>
            <h2 className="text-lg font-semibold text-atlas-text-primary">{def.title}</h2>
            <p className="text-xs text-atlas-text-muted mt-0.5">{def.description}</p>
          </div>
          <button 
            onClick={closeDrawer}
            className="p-2 -mr-2 text-atlas-text-muted hover:text-atlas-text-primary rounded-md hover:bg-atlas-surface-1 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          <ModuleSettingsContent moduleId={activeModuleId} />
        </div>
      </div>
    </>
  );
}

// Separate component to hook into the specific module store efficiently
function ModuleSettingsContent({ moduleId }: { moduleId: keyof typeof SECTION_SETTINGS_REGISTRY }) {
  const def = SECTION_SETTINGS_REGISTRY[moduleId];
  const { getResolvedSetting, setSetting, resetSettings } = useModuleSettings(moduleId);

  return (
    <>
      {def.groups.map(group => (
        <div key={group.id} className="space-y-3">
          <h3 className="text-sm font-medium text-atlas-text-primary mb-3">
            {group.label}
          </h3>
          <div className="bg-atlas-surface-1 border border-atlas-border-subtle rounded-md divide-y divide-atlas-border-subtle overflow-hidden">
            {group.settings.map(setting => (
              <SettingsRow 
                key={setting.id} 
                label={setting.label}
                description={setting.description}
                className="bg-transparent border-0 rounded-none p-4"
              >
                <SettingControl 
                  definition={setting} 
                  value={getResolvedSetting(setting.id)} 
                  onChange={(val) => setSetting(setting.id, val)}
                />
              </SettingsRow>
            ))}
          </div>
        </div>
      ))}
      
      <div className="pt-4 pb-2 border-t border-atlas-border-subtle">
        <Button 
          variant="secondary" 
          className="w-full justify-center text-sm"
          onClick={() => {
            if (confirm(`Reset all ${def.title} to their default values?`)) {
              resetSettings();
            }
          }}
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset {def.title}
        </Button>
      </div>
    </>
  );
}
