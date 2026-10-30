"use client";

import React, { useEffect, useState } from "react";
import { Building2, DollarSign, FileSpreadsheet, PieChart } from "lucide-react";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";

interface CompanyPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

interface FinancialMetric {
  label: string;
  value: string;
  yoy: string;
}

const COMPANY_FACTS: Record<string, { name: string; sector: string; metrics: FinancialMetric[] }> = {
  AAPL: {
    name: "Apple Inc.",
    sector: "Technology Hardware",
    metrics: [
      { label: "Revenue (TTM)", value: "$391.04B", yoy: "+2.02%" },
      { label: "Gross Profit", value: "$180.68B", yoy: "+6.85%" },
      { label: "Operating Income", value: "$123.22B", yoy: "+7.79%" },
      { label: "Net Income", value: "$100.37B", yoy: "+3.48%" },
      { label: "Free Cash Flow", value: "$108.81B", yoy: "+9.29%" },
      { label: "EPS (Diluted)", value: "$6.42", yoy: "+5.10%" },
      { label: "P/E Ratio", value: "36.05x", yoy: "+12.4%" },
      { label: "Market Cap", value: "$3.52T", yoy: "+22.1%" },
    ],
  },
  MSFT: {
    name: "Microsoft Corporation",
    sector: "Systems Software & Cloud",
    metrics: [
      { label: "Revenue (TTM)", value: "$245.12B", yoy: "+15.67%" },
      { label: "Gross Profit", value: "$171.01B", yoy: "+17.20%" },
      { label: "Operating Income", value: "$109.43B", yoy: "+23.89%" },
      { label: "Net Income", value: "$88.14B", yoy: "+21.80%" },
      { label: "Free Cash Flow", value: "$74.07B", yoy: "+18.25%" },
      { label: "EPS (Diluted)", value: "$11.80", yoy: "+21.52%" },
      { label: "P/E Ratio", value: "36.28x", yoy: "+5.8%" },
      { label: "Market Cap", value: "$3.18T", yoy: "+18.4%" },
    ],
  },
  NVDA: {
    name: "NVIDIA Corporation",
    sector: "Semiconductors & AI Compute",
    metrics: [
      { label: "Revenue (TTM)", value: "$96.31B", yoy: "+122.40%" },
      { label: "Gross Profit", value: "$73.17B", yoy: "+152.18%" },
      { label: "Operating Income", value: "$60.85B", yoy: "+174.45%" },
      { label: "Net Income", value: "$53.05B", yoy: "+168.20%" },
      { label: "Free Cash Flow", value: "$46.75B", yoy: "+180.12%" },
      { label: "EPS (Diluted)", value: "$2.13", yoy: "+165.05%" },
      { label: "P/E Ratio", value: "66.45x", yoy: "+35.2%" },
      { label: "Market Cap", value: "$3.47T", yoy: "+185.0%" },
    ],
  },
};

export function CompanyPanelAdapter({
  panel,
  context,
}: CompanyPanelAdapterProps) {
  const symbol =
    (!panel.independent_mode && ((context.COMPANY as string) || (context.INSTRUMENT as string))) ||
    (panel.configuration?.symbol as string) ||
    "AAPL";

  const company = COMPANY_FACTS[symbol] || {
    name: `${symbol} Corporation`,
    sector: "Diversified Equities",
    metrics: [
      { label: "Revenue (TTM)", value: "$45.20B", yoy: "+5.20%" },
      { label: "Operating Income", value: "$8.40B", yoy: "+4.10%" },
      { label: "Net Income", value: "$6.12B", yoy: "+3.85%" },
      { label: "Free Cash Flow", value: "$5.45B", yoy: "+2.90%" },
      { label: "EPS (Diluted)", value: "$3.15", yoy: "+4.20%" },
      { label: "P/E Ratio", value: "24.50x", yoy: "+1.2%" },
    ],
  };

  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
        <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
          <Building2 className="w-3.5 h-3.5 text-blue-400" />
          <span>{company.name} ({symbol})</span>
        </div>
        <span className="text-[10px] text-atlas-text-muted">{company.sector}</span>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar p-3">
        <div className="grid grid-cols-2 gap-2">
          {company.metrics.map((m) => (
            <div
              key={m.label}
              className="p-2 rounded-sm bg-atlas-surface-1 border border-atlas-border-default flex flex-col justify-between"
            >
              <span className="text-[10px] text-atlas-text-muted">{m.label}</span>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-xs font-bold text-atlas-text-primary">{m.value}</span>
                <span className="text-[10px] text-emerald-400">{m.yoy}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

