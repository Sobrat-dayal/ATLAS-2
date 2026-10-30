"use client";

import { Bot, Sparkles } from "lucide-react";
import { useAiOverlayStore } from "@/hooks/ai/useAiOverlay";

export function AtlasAiTrigger() {
  const { isOpen, toggleOverlay } = useAiOverlayStore();

  return (
    <button
      onClick={toggleOverlay}
      className={`group relative flex items-center gap-1.5 rounded-sm px-2.5 py-1 text-xs font-medium transition-all ${
        isOpen
          ? "bg-atlas-accent text-white shadow-sm shadow-atlas-accent/20"
          : "bg-atlas-surface-selected text-atlas-accent hover:bg-atlas-surface-hover hover:text-atlas-text-primary border border-atlas-accent/30"
      }`}
      title="Toggle ATLAS AI Assistant (Ctrl+Alt+A)"
    >
      <div className="relative">
        <Bot className="h-3.5 w-3.5 transition-transform group-hover:scale-110" />
        <span className="absolute -top-1 -right-1 flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-atlas-accent opacity-75"></span>
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-atlas-accent"></span>
        </span>
      </div>

      <span className="hidden sm:inline font-semibold tracking-wide">ATLAS AI</span>
      <span className="hidden md:inline-block text-[10px] opacity-70 font-mono ml-1 px-1 py-0.2 rounded bg-black/20">
        ^⌥A
      </span>
    </button>
  );
}

