"use client";

import React from "react";
import { AlertTriangle, ShieldAlert, TrendingDown } from "lucide-react";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";

interface RiskPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

const RISK_KPI_CARDS = [
  { label: "Annualized Volatility (σ)", value: "16.84%", note: "Rolling 252d" },
  { label: "Portfolio Beta (vs SPY)", value: "1.14", note: "Benchmark Beta" },
  { label: "Historical VaR (95%, 1d)", value: "$6,240.50", note: "1.49% of NAV" },
  { label: "Parametric VaR (99%, 10d)", value: "$21,480.00", note: "5.11% of NAV" },
  { label: "Expected Shortfall (CVaR 95%)", value: "$8,950.00", note: "Tail risk expectation" },
  { label: "Max Drawdown (3Y)", value: "-14.28%", note: "Recovered in 42 days" },
];

export function RiskPanelAdapter({}: RiskPanelAdapterProps) {
  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
        <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
          <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
          <span>Market-Risk & VaR Analytics</span>
        </div>
        <span className="text-[10px] text-amber-400 font-bold">Model Validated</span>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar p-3">
        <div className="grid grid-cols-2 gap-2 mb-3">
          {RISK_KPI_CARDS.map((kpi) => (
            <div
              key={kpi.label}
              className="p-2.5 rounded-sm bg-atlas-surface-1 border border-atlas-border-default flex flex-col justify-between"
            >
              <span className="text-[10px] text-atlas-text-muted">{kpi.label}</span>
              <div className="mt-1">
                <span className="text-sm font-bold text-rose-400">{kpi.value}</span>
                <span className="text-[10px] text-atlas-text-muted block mt-0.5">{kpi.note}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="border border-atlas-border-default rounded-sm p-2 bg-atlas-surface-1">
          <div className="text-[10px] font-semibold text-atlas-text-muted uppercase mb-1">
            Top Marginal Risk Contributors
          </div>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-[11px]">
              <span className="font-bold text-blue-400">NVDA</span>
              <span className="text-atlas-text-primary">31.4% Risk Contribution</span>
            </div>
            <div className="flex items-center justify-between text-[11px]">
              <span className="font-bold text-blue-400">AAPL</span>
              <span className="text-atlas-text-primary">26.2% Risk Contribution</span>
            </div>
            <div className="flex items-center justify-between text-[11px]">
              <span className="font-bold text-blue-400">MSFT</span>
              <span className="text-atlas-text-primary">22.8% Risk Contribution</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

