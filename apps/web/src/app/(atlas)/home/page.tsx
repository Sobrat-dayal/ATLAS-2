"use client";

import { ATLAS_MODULES } from "@/config/atlas-modules";
import { 
  PageHeader, 
  MetricCard, 
  Panel, 
  PanelHeader, 
  PanelContent, 
  DataTable, 
  Badge 
} from "@/design-system";

const mockMarketData = [
  { symbol: "S&P 500", price: 5123.41, change: 1.2 },
  { symbol: "NASDAQ", price: 16234.52, change: -0.5 },
  { symbol: "DOW JONES", price: 39012.33, change: 0.1 },
  { symbol: "VIX", price: 13.24, change: -2.3 },
  { symbol: "BTC/USD", price: 63124.00, change: 4.2 },
];

export default function HomePage() {
  return (
    <div className="p-4 md:p-6 space-y-6">
      <PageHeader 
        title={ATLAS_MODULES.home.label} 
        description={ATLAS_MODULES.home.description}
      />
      
      {/* Top Metric Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Global Risk Indicator" 
          value={34} 
          delta={-2.1} 
          format="number"
          trend="down"
        />
        <MetricCard 
          title="S&P 500" 
          value={5123.41} 
          delta={1.2} 
          format="currency" 
        />
        <MetricCard 
          title="Total Portfolio Value" 
          value={12450000} 
          delta={4.5} 
          format="compact" 
          prefix="$"
        />
        <MetricCard 
          title="Active Agents" 
          value={4} 
          format="number"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Panel>
            <PanelHeader title="Market Overview" />
            <PanelContent noPadding>
              <DataTable 
                data={mockMarketData}
                keyExtractor={(r) => r.symbol}
                columns={[
                  { key: "symbol", header: "Index / Asset" },
                  { 
                    key: "price", 
                    header: "Price", 
                    align: "right",
                    cell: (r) => r.price.toLocaleString("en-US", { minimumFractionDigits: 2 })
                  },
                  {
                    key: "change",
                    header: "24h Change",
                    align: "right",
                    cell: (r) => (
                      <span className={r.change > 0 ? "text-atlas-positive" : r.change < 0 ? "text-atlas-negative" : "text-atlas-neutral"}>
                        {r.change > 0 ? "+" : ""}{r.change.toFixed(2)}%
                      </span>
                    )
                  }
                ]}
              />
            </PanelContent>
          </Panel>
        </div>

        <div className="space-y-6">
          <Panel>
            <PanelHeader title="Active Tasks" />
            <PanelContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-atlas-text-primary">Data Pipeline</div>
                    <div className="text-xs text-atlas-text-muted mt-0.5">Ingesting SEC filings...</div>
                  </div>
                  <Badge variant="outline">Running</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-atlas-text-primary">Portfolio Sync</div>
                    <div className="text-xs text-atlas-text-muted mt-0.5">Broker connection</div>
                  </div>
                  <Badge variant="positive">Completed</Badge>
                </div>
              </div>
            </PanelContent>
          </Panel>
        </div>
      </div>
    </div>
  );
}
