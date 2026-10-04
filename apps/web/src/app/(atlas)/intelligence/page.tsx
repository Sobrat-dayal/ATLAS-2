"use client";

import { ATLAS_MODULES } from "@/config/atlas-modules";
import { 
  AtlasSplit, 
  AtlasPanel, 
  AtlasResizeHandle, 
  AtlasInspector,
  PageHeader
} from "@/design-system";

export default function IntelligencePage() {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4 py-3 shrink-0 border-b border-atlas-border-default">
        <PageHeader 
          title={ATLAS_MODULES.intelligence.label} 
          description={ATLAS_MODULES.intelligence.description}
          className="mb-0 pb-0 border-b-0"
        />
      </div>

      <div className="flex-1 overflow-hidden">
        <AtlasSplit id="layout.intelligence.main" direction="horizontal" defaultLayout={[75, 25]}>
          <AtlasPanel id="intelligence.content" minSize={40} defaultSize={75}>
            <AtlasSplit id="layout.intelligence.content" direction="vertical" defaultLayout={[70, 30]}>
              <AtlasPanel id="intelligence.map" minSize={30} defaultSize={70} className="p-4 relative">
                <div className="absolute inset-0 m-4 border border-atlas-border-default rounded-sm bg-atlas-surface-2 flex items-center justify-center text-atlas-text-muted">
                  Global Signal Map
                </div>
              </AtlasPanel>
              <AtlasResizeHandle />
              <AtlasPanel id="intelligence.feed" minSize={20} defaultSize={30} className="border-t border-atlas-border-default bg-atlas-surface-1">
                <div className="p-3 border-b border-atlas-border-default text-sm font-medium">
                  Live Event Feed
                </div>
                <div className="p-4 text-sm text-atlas-text-muted">
                  Waiting for signals...
                </div>
              </AtlasPanel>
            </AtlasSplit>
          </AtlasPanel>

          <AtlasResizeHandle />

          <AtlasInspector 
            id="intelligence.inspector" 
            title="Signal Inspector" 
            minSize={20} 
            maxSize={40}
            defaultSize={25}
          >
            <div className="p-4 text-sm text-atlas-text-muted">
              Select an event to inspect source credibility and automated analysis.
            </div>
          </AtlasInspector>
        </AtlasSplit>
      </div>
    </div>
  );
}
