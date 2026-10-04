"use client";

import * as React from "react";
import { Maximize2, Minimize2 } from "lucide-react";
import { IconButton } from "../components/IconButton";
import { useShellState } from "@/hooks/shell/useShellState";

export interface AtlasFullscreenProps {
  className?: string;
}

export function AtlasFullscreen({ className }: AtlasFullscreenProps) {
  const { moduleFullscreen, setModuleFullscreen } = useShellState();

  // Support Escape key to exit fullscreen
  React.useEffect(() => {
    if (!moduleFullscreen) return;
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setModuleFullscreen(false);
      }
    };
    
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [moduleFullscreen, setModuleFullscreen]);

  return (
    <IconButton 
      variant="ghost" 
      size="xs" 
      className={className}
      onClick={() => setModuleFullscreen(!moduleFullscreen)} 
      title={moduleFullscreen ? "Exit Fullscreen (Esc)" : "Enter Fullscreen"}
      aria-label={moduleFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
    >
      {moduleFullscreen ? (
        <Minimize2 className="w-4 h-4" />
      ) : (
        <Maximize2 className="w-4 h-4" />
      )}
    </IconButton>
  );
}
