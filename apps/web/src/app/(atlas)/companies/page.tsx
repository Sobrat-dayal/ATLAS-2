"use client";

import { ATLAS_MODULES } from "@/config/atlas-modules";
import { 
  AtlasSplit, 
  AtlasPanel, 
  AtlasResizeHandle, 
  AtlasInspector,
  PageHeader,
  DataTable,
  Badge,
  Input
} from "@/design-system";

const mockCompanies = [
  { ticker: "AAPL", name: "Apple Inc.", marketCap: "3.2T", sector: "Technology" },
  { ticker: "MSFT", name: "Microsoft Corp.", marketCap: "3.1T", sector: "Technology" },
  { ticker: "NVDA", name: "NVIDIA Corp.", marketCap: "2.8T", sector: "Semiconductors" },
  { ticker: "GOOGL", name: "Alphabet Inc.", marketCap: "2.1T", sector: "Communication Services" },
];

export default function CompaniesPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4 py-3 shrink-0 border-b border-atlas-border-default">
        <PageHeader 
          title={ATLAS_MODULES.companies.label} 
          description={ATLAS_MODULES.companies.description}
          className="mb-0 pb-0 border-b-0"
        />
      </div>

      <div className="flex-1 overflow-hidden">
        <AtlasSplit id="layout.companies" direction="horizontal" defaultLayout={[75, 25]}>
          {/* Main Content */}
          <AtlasPanel id="companies.main" minSize={40} defaultSize={75} scrollable className="p-4">
            <div className="mb-4">
              <Input placeholder="Filter companies by ticker, name, sector..." className="max-w-md" />
            </div>
            <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm">
              <DataTable 
                data={mockCompanies}
                keyExtractor={(r) => r.ticker}
                columns={[
                  { key: "ticker", header: "Ticker" },
                  { key: "name", header: "Company Name" },
                  { key: "sector", header: "Sector" },
                  { key: "marketCap", header: "Market Cap", align: "right" }
                ]}
                onRowClick={() => {}}
              />
            </div>
          </AtlasPanel>

          <AtlasResizeHandle />

          {/* Inspector */}
          <AtlasInspector 
            id="companies.inspector" 
            title="Company Profile" 
            minSize={20} 
            maxSize={40}
            defaultSize={25}
          >
            <div className="p-4 space-y-4">
              <div>
                <h3 className="text-lg font-bold text-atlas-text-primary">AAPL</h3>
                <p className="text-sm text-atlas-text-muted">Apple Inc.</p>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="text-atlas-text-muted">Sector</div>
                <div className="text-right">Technology</div>
                
                <div className="text-atlas-text-muted">Industry</div>
                <div className="text-right">Consumer Electronics</div>
                
                <div className="text-atlas-text-muted">Employees</div>
                <div className="text-right">161,000</div>
              </div>
              
              <div className="pt-4 border-t border-atlas-border-subtle">
                <p className="text-sm text-atlas-text-secondary leading-relaxed">
                  Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.
                </p>
              </div>
            </div>
          </AtlasInspector>
        </AtlasSplit>
      </div>
    </div>
  );
}
