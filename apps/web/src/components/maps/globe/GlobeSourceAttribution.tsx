/**
 * Visible Legal Attribution Overlay for 3D Globe (Stage 130).
 *
 * Enforces mandatory licensing attribution credits across OpenStreetMap,
 * CARTO, Natural Earth, Copernicus Sentinel, and OGC 3D Tilesets.
 */

"use client";

import React from "react";

interface GlobeSourceAttributionProps {
  attributionText: string;
}

export function GlobeSourceAttribution({ attributionText }: GlobeSourceAttributionProps) {
  if (!attributionText) return null;

  return (
    <div
      aria-label="Geospatial Data Attribution"
      className="absolute bottom-2 right-2 z-10 px-2.5 py-1 rounded bg-atlas-bg-0/80 backdrop-blur-sm border border-atlas-border-subtle/80 text-[10px] text-atlas-text-muted select-none pointer-events-auto"
    >
      <span>{attributionText}</span>
    </div>
  );
}
