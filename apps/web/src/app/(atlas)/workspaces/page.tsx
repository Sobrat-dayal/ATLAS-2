"use client";

import { ATLAS_MODULES } from "@/config/atlas-modules";
import { 
  AtlasSplit, 
  AtlasPanel, 
  AtlasResizeHandle, 
  AtlasInspector,
  PageHeader,
  DataTable,
  Badge
} from "@/design-system";

export default function WorkspacesPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4 py-3 shrink-0 border-b border-atlas-border-default">
        <PageHeader 
          title={ATLAS_MODULES.workspaces.label} 
          description={ATLAS_MODULES.workspaces.description}
          className="mb-0 pb-0 border-b-0"
        />
      </div>

      <div className="flex-1 overflow-hidden">
        <AtlasSplit id="layout.workspaces" direction="horizontal" defaultLayout={[65, 35]}>
          <AtlasPanel id="workspaces.main" minSize={40} defaultSize={65} className="p-4" scrollable>
            <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm h-full flex items-center justify-center text-atlas-text-muted">
               <p>Workspace Canvas Editor (Future)</p>
            </div>
          </AtlasPanel>

          <AtlasResizeHandle />

          <AtlasInspector 
            id="workspaces.inspector" 
            title="Widgets & Templates" 
            minSize={20} 
            maxSize={40}
            defaultSize={35}
          >
            <div className="p-4 space-y-6">
              <div>
                <h4 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider mb-3">Saved Layouts</h4>
                <div className="space-y-2">
                  <div className="p-3 border border-atlas-border-default rounded-sm hover:border-atlas-accent transition-colors cursor-pointer bg-atlas-surface-hover">
                    <div className="text-sm font-medium">Morning Research</div>
                    <div className="text-xs text-atlas-text-muted mt-1">3 Panels • News, Chart, Order Book</div>
                  </div>
                  <div className="p-3 border border-atlas-border-default rounded-sm hover:border-atlas-accent transition-colors cursor-pointer bg-atlas-surface-hover">
                    <div className="text-sm font-medium">Global Macro</div>
                    <div className="text-xs text-atlas-text-muted mt-1">2 Panels • Map, Event Feed</div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider mb-3">Available Widgets</h4>
                <div className="grid grid-cols-2 gap-2 text-sm text-center">
                  <div className="p-2 border border-atlas-border-subtle rounded-sm bg-atlas-surface-2">Chart</div>
                  <div className="p-2 border border-atlas-border-subtle rounded-sm bg-atlas-surface-2">News</div>
                  <div className="p-2 border border-atlas-border-subtle rounded-sm bg-atlas-surface-2">Positions</div>
                  <div className="p-2 border border-atlas-border-subtle rounded-sm bg-atlas-surface-2">Terminal</div>
                </div>
              </div>
            </div>
          </AtlasInspector>
        </AtlasSplit>
      </div>
    </div>
  );
}
