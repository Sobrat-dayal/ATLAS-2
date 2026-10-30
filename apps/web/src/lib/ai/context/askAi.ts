/**
 * Global "Ask AI About This" context handoff helper for ATLAS modules.
 */

import { useAiOverlayStore } from "@/hooks/ai/useAiOverlay";

export interface AskAiOptions {
  type: string;
  targetId: string;
  title?: string;
  initialQuery?: string;
  parameters?: Record<string, unknown>;
}

export const ASK_AI_EVENT = "atlas:ask-ai-context";

export function askAiAboutThis(options: AskAiOptions): void {
  // 1. Open the AI Overlay
  try {
    const store = useAiOverlayStore.getState?.();
    if (store && typeof store.openOverlay === "function") {
      store.openOverlay();
    }
  } catch {
    // In headless or test environments
  }

  // 2. Dispatch global event with target details for the context hook & composer
  if (typeof window !== "undefined") {
    const event = new CustomEvent(ASK_AI_EVENT, { detail: options });
    window.dispatchEvent(event);
  }
}
