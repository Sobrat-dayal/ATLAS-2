"use client";

import { useEffect, useState } from "react";
import { create } from "zustand";

interface CommandPaletteStore {
  isOpen: boolean;
  openCommandPalette: () => void;
  closeCommandPalette: () => void;
  toggleCommandPalette: () => void;
  searchFocusTrigger: number;
  triggerSearchFocus: () => void;
}

export const useCommandPalette = create<CommandPaletteStore>((set) => ({
  isOpen: false,
  openCommandPalette: () => set({ isOpen: true }),
  closeCommandPalette: () => set({ isOpen: false }),
  toggleCommandPalette: () => set((state) => ({ isOpen: !state.isOpen })),
  searchFocusTrigger: 0,
  triggerSearchFocus: () =>
    set((state) => ({ searchFocusTrigger: state.searchFocusTrigger + 1 })),
}));

/**
 * Checks if the event target is within an active rich text / editor context
 * where Cmd/Ctrl+K should not be intercepted (e.g. Monaco editor, textarea, contenteditable).
 */
export function isEditingContext(target: EventTarget | null): boolean {
  if (!target || !(target instanceof HTMLElement)) return false;

  // Monaco editor or explicitly excluded editor containers
  if (
    target.closest(".monaco-editor") ||
    target.closest('[data-skip-command-palette="true"]')
  ) {
    return true;
  }

  // Multiline text areas and rich contenteditable nodes
  if (target.isContentEditable) return true;
  if (target.tagName === "TEXTAREA") return true;

  return false;
}

/**
 * Hook to listen for global Cmd+K (macOS) / Ctrl+K (Windows/Linux) shortcuts.
 */
export function useCommandPaletteShortcut() {
  const { toggleCommandPalette, closeCommandPalette, isOpen } = useCommandPalette();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Close on Escape if open
      if (e.key === "Escape" && isOpen) {
        e.preventDefault();
        closeCommandPalette();
        return;
      }

      // Check for Cmd+K / Ctrl+K
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        if (isEditingContext(e.target)) {
          return;
        }

        e.preventDefault();
        toggleCommandPalette();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [toggleCommandPalette, closeCommandPalette, isOpen]);
}

/**
 * Detects whether the current platform is macOS for platform-aware display badges.
 */
export function usePlatformShortcut(): { isMac: boolean; shortcutLabel: string } {
  const [isMac, setIsMac] = useState(false);

  useEffect(() => {
    if (typeof navigator !== "undefined") {
      const platform =
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (navigator as any).userAgentData?.platform || navigator.platform || "";
      setIsMac(/Mac|iPhone|iPad|iPod/i.test(platform));
    }
  }, []);

  return {
    isMac,
    shortcutLabel: isMac ? "⌘K" : "Ctrl+K",
  };
}
