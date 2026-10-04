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

const mockDatasets = [
  { id: "SEC", name: "SEC EDGAR Filings", rows: "450M", status: "Active" },
  { id: "FRED", name: "Federal Reserve Economic Data", rows: "2.1M", status: "Active" },
  { id: "BBG", name: "Bloomberg Ticks", rows: "8.2B", status: "Syncing" },
];

export default function DataPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4 py-3 shrink-0 border-b border-atlas-border-default">
        <PageHeader 
          title={ATLAS_MODULES.data.label} 
          description={ATLAS_MODULES.data.description}
          className="mb-0 pb-0 border-b-0"
        />
      </div>

      <div className="flex-1 overflow-hidden">
        <AtlasSplit id="layout.data.main" direction="horizontal" defaultLayout={[20, 80]}>
          {/* Datasets Sidebar */}
          <AtlasPanel id="data.datasets" minSize={15} defaultSize={20}>
            <div className="h-full bg-atlas-surface-1 border-r border-atlas-border-default flex flex-col">
              <div className="p-3 border-b border-atlas-border-default text-sm font-medium text-atlas-text-primary">
                Data Catalogs
              </div>
              <div className="flex-1 overflow-auto p-2 space-y-1">
                {mockDatasets.map(d => (
                  <div key={d.id} className="px-3 py-2 text-sm text-atlas-text-primary hover:bg-atlas-surface-hover rounded-sm cursor-pointer transition-colors">
                    {d.name}
                  </div>
                ))}
              </div>
            </div>
          </AtlasPanel>

          <AtlasResizeHandle />

          <AtlasPanel id="data.content" minSize={40} defaultSize={80}>
            {/* Nested Split: Query/Preview vs Schema Inspector */}
            <AtlasSplit id="layout.data.content" direction="horizontal" defaultLayout={[75, 25]}>
              <AtlasPanel id="data.preview" minSize={40} defaultSize={75} className="bg-atlas-surface-0 flex flex-col">
                {/* Vertical split: SQL editor vs Results (Simulated via flex for now, or we can use another split!) */}
                <AtlasSplit id="layout.data.preview.vertical" direction="vertical" defaultLayout={[30, 70]}>
                  <AtlasPanel id="data.query" minSize={20} defaultSize={30} className="p-4 border-b border-atlas-border-default">
                    <div className="font-mono text-sm text-atlas-blue mb-2">SELECT * FROM SEC_EDGAR LIMIT 100;</div>
                    <div className="text-xs text-atlas-text-muted">Press Ctrl+Enter to execute</div>
                  </AtlasPanel>
                  <AtlasResizeHandle />
                  <AtlasPanel id="data.results" minSize={20} defaultSize={70} className="p-4">
                    <div className="text-sm text-atlas-text-muted">Query Results Preview...</div>
                  </AtlasPanel>
                </AtlasSplit>
              </AtlasPanel>

              <AtlasResizeHandle />

              {/* Schema Inspector */}
              <AtlasInspector 
                id="data.schema" 
                title="Schema Inspector" 
                minSize={20} 
                maxSize={40}
                defaultSize={25}
              >
                <div className="p-4">
                  <p className="text-sm text-atlas-text-muted mb-4">Select a table to view its schema.</p>
                </div>
              </AtlasInspector>
            </AtlasSplit>
          </AtlasPanel>
        </AtlasSplit>
      </div>
    </div>
  );
}
