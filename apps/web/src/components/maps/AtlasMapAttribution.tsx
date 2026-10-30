"use client";

import React from "react";
import { BASEMAP_ATTRIBUTION } from "@/lib/maps/styles";

interface AtlasMapAttributionProps {
  customAttribution?: string;
  className?: string;
}

export function AtlasMapAttribution({
  customAttribution,
  className = "",
}: AtlasMapAttributionProps) {
  const text = customAttribution || BASEMAP_ATTRIBUTION;

  return (
    <div
      className={`absolute bottom-2 right-2 z-10 px-2 py-0.5 bg-black/75 backdrop-blur-xs text-[10px] text-atlas-text-muted font-mono rounded border border-white/10 select-none pointer-events-auto ${className}`}
      title="Licensed basemap and spatial data attribution"
    >
      <span>{text}</span>
    </div>
  );
}

