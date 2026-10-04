"use client";

import { ATLAS_MODULES } from "@/config/atlas-modules";
import { 
  AtlasSplit, 
  AtlasPanel, 
  AtlasResizeHandle,
  PageHeader,
  DataTable,
  Badge
} from "@/design-system";

const mockSavedItems = [
  { id: "1", title: "Technology Sector Screen", type: "Screener", date: "2024-09-01" },
  { id: "2", title: "Q3 Earnings Watchlist", type: "Watchlist", date: "2024-09-12" },
  { id: "3", title: "AAPL Options Chain", type: "Options", date: "2024-09-18" },
];

export default function SavedPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4 py-3 shrink-0">
        <PageHeader 
          title={ATLAS_MODULES.saved.label} 
          description={ATLAS_MODULES.saved.description}
          className="mb-0 pb-0 border-b-0"
        />
      </div>

      <div className="flex-1 overflow-hidden p-2">
        <AtlasSplit id="layout.saved" direction="horizontal" defaultLayout={[30, 70]}>
          {/* Library (Master) */}
          <AtlasPanel id="saved.library" minSize={20} defaultSize={30}>
            <div className="h-full flex flex-col bg-atlas-surface-1 border border-atlas-border-default rounded-sm">
              <div className="p-3 border-b border-atlas-border-default text-sm font-medium">
                Saved Items
              </div>
              <div className="flex-1 overflow-auto">
                <DataTable 
                  data={mockSavedItems}
                  keyExtractor={(r) => r.id}
                  columns={[
                    { key: "title", header: "Title" },
                    { 
                      key: "type", 
                      header: "Type",
                      cell: (r) => <Badge variant="outline">{r.type}</Badge>
                    }
                  ]}
                  onRowClick={() => {}}
                />
              </div>
            </div>
          </AtlasPanel>

          <AtlasResizeHandle withHandleIcon />

          {/* Preview (Detail) */}
          <AtlasPanel id="saved.preview" minSize={40} defaultSize={70}>
            <div className="h-full bg-atlas-surface-0 ml-1 rounded-sm border border-atlas-border-default flex flex-col items-center justify-center text-atlas-text-muted">
              Select an item to preview
            </div>
          </AtlasPanel>
        </AtlasSplit>
      </div>
    </div>
  );
}
