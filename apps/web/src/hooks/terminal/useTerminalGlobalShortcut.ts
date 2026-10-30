"use client";

import { useEffect } from "react";
import { useBottomPanel } from "@/hooks/bottom-taskbar";
import { isEditingContext } from "@/hooks/commands/useCommandPalette";

/**
 * Hook to listen for global Ctrl+` (or Cmd+`) shortcut to toggle the Terminal drawer.
 */
export function useTerminalGlobalShortcut() {
  const { togglePanel } = useBottomPanel();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check for Ctrl+` or Cmd+`
      if ((e.metaKey || e.ctrlKey) && (e.key === "`" || e.key === "~")) {
        // If user is inside an editor, allow toggling terminal
        e.preventDefault();
        togglePanel("terminal");
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [togglePanel]);
}

