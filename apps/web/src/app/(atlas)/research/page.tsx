"use client";

import { ATLAS_MODULES } from "@/config/atlas-modules";
import { 
  AtlasSplit, 
  AtlasPanel, 
  AtlasResizeHandle, 
  AtlasInspector,
  PageHeader,
  PanelContent,
  DataTable,
  Badge,
  Input
} from "@/design-system";

const mockResearchDocs = [
  { id: "1", title: "Global Macro Outlook Q3", type: "Report", date: "2024-09-01", status: "Published" },
  { id: "2", title: "Semiconductor Supply Chain Analysis", type: "Equity", date: "2024-09-12", status: "Draft" },
  { id: "3", title: "Federal Reserve Rate Decision Impact", type: "Macro", date: "2024-09-18", status: "Published" },
  { id: "4", title: "Energy Sector Transition Risks", type: "Commodity", date: "2024-09-20", status: "Review" },
];

export default function ResearchPage() {
  return (
    <div className="flex h-full flex-col">
      {/* Top Header remains fixed outside the layout splits */}
      <div className="px-4 py-3 shrink-0">
        <PageHeader 
          title={ATLAS_MODULES.research.label} 
          description={ATLAS_MODULES.research.description}
          className="mb-0 pb-0 border-b-0"
        />
      </div>

      <div className="flex-1 overflow-hidden p-2">
        <AtlasSplit id="layout.research" direction="horizontal" defaultLayout={[30, 70]}>
          {/* Library (Master) */}
          <AtlasPanel id="research.library" minSize={20} defaultSize={30}>
            <div className="h-full flex flex-col bg-atlas-surface-1 border border-atlas-border-default rounded-sm">
              <div className="p-3 border-b border-atlas-border-default">
                <Input placeholder="Search research library..." className="w-full" />
              </div>
              <div className="flex-1 overflow-auto">
                <DataTable 
                  data={mockResearchDocs}
                  keyExtractor={(r) => r.id}
                  columns={[
                    { key: "title", header: "Document Title" },
                    { 
                      key: "status", 
                      header: "Status",
                      cell: (r) => (
                        <Badge variant={r.status === 'Published' ? 'positive' : 'outline'}>
                          {r.status}
                        </Badge>
                      )
                    }
                  ]}
                  onRowClick={() => {}}
                />
              </div>
            </div>
          </AtlasPanel>

          <AtlasResizeHandle withHandleIcon />

          {/* Document Preview (Detail) */}
          <AtlasPanel id="research.document" minSize={40} defaultSize={70}>
            <div className="h-full bg-atlas-surface-0 ml-1 rounded-sm border border-atlas-border-default flex flex-col items-center justify-center text-atlas-text-muted">
              <svg className="w-12 h-12 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Select a document to preview
            </div>
          </AtlasPanel>
        </AtlasSplit>
      </div>
    </div>
  );
}
