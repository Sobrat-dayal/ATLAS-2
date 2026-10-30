"use client";

import { ATLAS_MODULES } from "@/config/atlas-modules";
import { PageHeader, AtlasFullscreen } from "@/design-system";
import { AtlasMap } from "@/components/maps/AtlasMap";

export default function MapsPage() {
  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="px-4 py-2 shrink-0 border-b border-atlas-border-default z-10 relative bg-atlas-bg-0">
        <PageHeader
          title={ATLAS_MODULES.maps.label}
          description={ATLAS_MODULES.maps.description}
          className="mb-0 pb-0 border-b-0"
          actions={<AtlasFullscreen />}
        />
      </div>

      <div className="flex-1 overflow-hidden relative">
        <AtlasMap />
      </div>
    </div>
  );
}
