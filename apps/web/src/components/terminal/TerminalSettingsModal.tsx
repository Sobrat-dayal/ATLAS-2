"use client";

import React, { useState } from "react";
import { X, Settings2 } from "lucide-react";
import { TerminalCursorStyle, TerminalUserPreferences } from "@/lib/terminal/types";

interface TerminalSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  preferences: TerminalUserPreferences;
  onSavePreferences: (updated: Partial<TerminalUserPreferences>) => void;
}

export function TerminalSettingsModal({
  isOpen,
  onClose,
  preferences,
  onSavePreferences,
}: TerminalSettingsModalProps) {
  const [fontSize, setFontSize] = useState(preferences.font_size);
  const [fontFamily, setFontFamily] = useState(preferences.font_family);
  const [lineHeight, setLineHeight] = useState(preferences.line_height);
  const [cursorStyle, setCursorStyle] = useState<TerminalCursorStyle>(preferences.cursor_style);
  const [wordWrap, setWordWrap] = useState(preferences.word_wrap);
  const [scrollbackLimit, setScrollbackLimit] = useState(preferences.scrollback_limit);
  const [terminalHeight, setTerminalHeight] = useState(preferences.terminal_height);

  if (!isOpen) return null;

  const handleSave = () => {
    onSavePreferences({
      font_size: fontSize,
      font_family: fontFamily,
      line_height: lineHeight,
      cursor_style: cursorStyle,
      word_wrap: wordWrap,
      scrollback_limit: scrollbackLimit,
      terminal_height: terminalHeight,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-md rounded-lg border border-atlas-border-default bg-atlas-surface-1 shadow-2xl p-5 text-atlas-text-primary">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle mb-4">
          <div className="flex items-center gap-2">
            <Settings2 className="h-4 w-4 text-atlas-accent" />
            <h3 className="text-sm font-semibold uppercase tracking-wider">
              Terminal Preferences
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Form Body */}
        <div className="space-y-4 text-xs font-mono">
          <div>
            <label className="block text-atlas-text-muted mb-1">
              Terminal Drawer Height: {terminalHeight}px
            </label>
            <input
              type="range"
              min="200"
              max="700"
              step="10"
              value={terminalHeight}
              onChange={(e) => setTerminalHeight(Number(e.target.value))}
              className="w-full accent-atlas-accent"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-atlas-text-muted mb-1">Font Size (px)</label>
              <input
                type="number"
                min="9"
                max="24"
                value={fontSize}
                onChange={(e) => setFontSize(Number(e.target.value))}
                className="w-full bg-atlas-surface-0 border border-atlas-border-default rounded px-2.5 py-1 text-xs text-atlas-text-primary outline-none focus:border-atlas-accent"
              />
            </div>

            <div>
              <label className="block text-atlas-text-muted mb-1">Line Height</label>
              <input
                type="number"
                min="1.0"
                max="2.2"
                step="0.05"
                value={lineHeight}
                onChange={(e) => setLineHeight(Number(e.target.value))}
                className="w-full bg-atlas-surface-0 border border-atlas-border-default rounded px-2.5 py-1 text-xs text-atlas-text-primary outline-none focus:border-atlas-accent"
              />
            </div>
          </div>

          <div>
            <label className="block text-atlas-text-muted mb-1">Font Family</label>
            <input
              type="text"
              value={fontFamily}
              onChange={(e) => setFontFamily(e.target.value)}
              className="w-full bg-atlas-surface-0 border border-atlas-border-default rounded px-2.5 py-1 text-xs text-atlas-text-primary outline-none focus:border-atlas-accent"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-atlas-text-muted mb-1">Cursor Style</label>
              <select
                value={cursorStyle}
                onChange={(e) => setCursorStyle(e.target.value as TerminalCursorStyle)}
                className="w-full bg-atlas-surface-0 border border-atlas-border-default rounded px-2.5 py-1 text-xs text-atlas-text-primary outline-none focus:border-atlas-accent"
              >
                <option value="BLOCK">Block</option>
                <option value="LINE">Line</option>
                <option value="UNDERLINE">Underline</option>
              </select>
            </div>

            <div>
              <label className="block text-atlas-text-muted mb-1">Scrollback Buffer</label>
              <input
                type="number"
                min="500"
                max="10000"
                step="500"
                value={scrollbackLimit}
                onChange={(e) => setScrollbackLimit(Number(e.target.value))}
                className="w-full bg-atlas-surface-0 border border-atlas-border-default rounded px-2.5 py-1 text-xs text-atlas-text-primary outline-none focus:border-atlas-accent"
              />
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <input
              type="checkbox"
              id="pref-word-wrap"
              checked={wordWrap}
              onChange={(e) => setWordWrap(e.target.checked)}
              className="accent-atlas-accent"
            />
            <label htmlFor="pref-word-wrap" className="text-atlas-text-primary cursor-pointer">
              Enable Word Wrap
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 mt-6 pt-3 border-t border-atlas-border-subtle">
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1.5 rounded text-xs text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-4 py-1.5 rounded text-xs font-semibold bg-atlas-accent text-white hover:bg-atlas-accent/90 transition-colors shadow-sm"
          >
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
}

