"use client";

import { ATLAS_MODULES } from "@/config/atlas-modules";
import { 
  AtlasSplit, 
  AtlasPanel, 
  AtlasResizeHandle, 
  AtlasInspector,
  PageHeader,
  AtlasFullscreen
} from "@/design-system";
import { Layers, MapPin } from "lucide-react";

export default function MapsPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4 py-3 shrink-0 border-b border-atlas-border-default z-10 relative bg-atlas-bg-0">
        <PageHeader 
          title={ATLAS_MODULES.maps.label} 
          description={ATLAS_MODULES.maps.description}
          className="mb-0 pb-0 border-b-0"
          actions={<AtlasFullscreen />}
        />
      </div>

      <div className="flex-1 overflow-hidden relative">
        <AtlasSplit id="layout.maps" direction="horizontal" defaultLayout={[15, 65, 20]}>
          {/* Left Layers Panel */}
          <AtlasInspector 
            id="maps.layers" 
            title="Layers" 
            minSize={10} 
            maxSize={30}
            defaultSize={15}
            defaultCollapsed={true}
          >
            <div className="p-4 flex flex-col items-center justify-center text-atlas-text-muted h-full opacity-50">
              <Layers className="w-8 h-8 mb-2" />
              <p className="text-sm">No active layers</p>
            </div>
          </AtlasInspector>

          <AtlasResizeHandle />

          {/* Main Map Content - No background, simulates map canvas */}
          <AtlasPanel id="maps.canvas" minSize={40} defaultSize={65}>
            <div className="h-full w-full bg-atlas-surface-1 flex flex-col items-center justify-center text-atlas-text-muted">
               <MapPin className="w-12 h-12 mb-4 text-atlas-border-strong" />
               <p className="text-xl font-medium text-atlas-text-secondary">Global Geospatial Canvas</p>
               <p className="text-sm mt-2">Map Engine Initializing...</p>
            </div>
          </AtlasPanel>

          <AtlasResizeHandle />

          {/* Right Inspector */}
          <AtlasInspector 
            id="maps.inspector" 
            title="Region Inspector" 
            minSize={15} 
            maxSize={40}
            defaultSize={20}
          >
            <div className="p-4 text-sm text-atlas-text-muted">
              Select a location on the map to view metadata, satellite imagery feeds, and regional risk metrics.
            </div>
          </AtlasInspector>
        </AtlasSplit>
      </div>
    </div>
  );
}
