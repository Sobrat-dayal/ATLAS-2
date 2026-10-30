"use client";

import { useEffect } from "react";
import { create } from "zustand";

interface AiOverlayState {
  isOpen: boolean;
  activeConversationId: string | null;
  overlayWidth: number;
  isHistoryDrawerOpen: boolean;
  dockSide: "right" | "left";
  toggleOverlay: () => void;
  openOverlay: (conversationId?: string) => void;
  closeOverlay: () => void;
  setActiveConversationId: (id: string | null) => void;
  setOverlayWidth: (width: number) => void;
  toggleHistoryDrawer: () => void;
  setHistoryDrawerOpen: (open: boolean) => void;
  setDockSide: (side: "right" | "left") => void;
}

export const useAiOverlayStore = create<AiOverlayState>((set) => ({
  isOpen: false,
  activeConversationId: null,
  overlayWidth: 440,
  isHistoryDrawerOpen: false,
  dockSide: "right",

  toggleOverlay: () => set((state) => ({ isOpen: !state.isOpen })),
  openOverlay: (conversationId) =>
    set({
      isOpen: true,
      activeConversationId: conversationId || null,
    }),
  closeOverlay: () => set({ isOpen: false }),
  setActiveConversationId: (id) => set({ activeConversationId: id }),
  setOverlayWidth: (width) =>
    set({ overlayWidth: Math.max(340, Math.min(800, width)) }),
  toggleHistoryDrawer: () =>
    set((state) => ({ isHistoryDrawerOpen: !state.isHistoryDrawerOpen })),
  setHistoryDrawerOpen: (open) => set({ isHistoryDrawerOpen: open }),
  setDockSide: (side) => set({ dockSide: side }),
}));

/**
 * Global keyboard shortcut hook: Ctrl+Alt+A (or Cmd+Alt+A) toggles AI overlay.
 */
export function useAiOverlayShortcut() {
  const { toggleOverlay } = useAiOverlayStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+Alt+A or Cmd+Alt+A
      if ((e.ctrlKey || e.metaKey) && e.altKey && (e.key === "a" || e.key === "A")) {
        e.preventDefault();
        toggleOverlay();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [toggleOverlay]);
}

