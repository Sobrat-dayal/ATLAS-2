"use client";

import React from "react";
import { SettingsGroup, SettingsRow } from "../SettingsControls";

export function KeyboardSettings() {
  const defaultShortcuts = [
    { label: "Focus Search / Command", keys: ["Ctrl/Cmd", "K"] },
    { label: "Close Overlay", keys: ["Esc"] },
    { label: "Toggle Sidebar", keys: ["Ctrl/Cmd", "\\"] },
    { label: "Open Settings", keys: ["Ctrl/Cmd", ","] },
  ];

  return (
    <div className="space-y-6">
      <SettingsGroup 
        title="Global Shortcuts" 
        description="Custom shortcut editing will be added later."
      >
        {defaultShortcuts.map((shortcut, idx) => (
          <SettingsRow 
            key={idx} 
            label={shortcut.label}
          >
            <div className="flex gap-1.5">
              {shortcut.keys.map(key => (
                <kbd key={key} className="px-2 py-1 bg-atlas-surface-2 border border-atlas-border-default rounded-sm text-xs font-mono text-atlas-text-secondary shadow-sm">
                  {key}
                </kbd>
              ))}
            </div>
          </SettingsRow>
        ))}
      </SettingsGroup>
    </div>
  );
}
