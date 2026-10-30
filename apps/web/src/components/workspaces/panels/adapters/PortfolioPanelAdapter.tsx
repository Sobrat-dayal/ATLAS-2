"use client";

import React from "react";
import { Briefcase, DollarSign, PieChart } from "lucide-react";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";

interface PortfolioPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

const HOLDINGS = [
  { symbol: "AAPL", asset: "Apple Inc", shares: 450, price: 231.41, marketValue: 104134.50, weight: "24.8%" },
  { symbol: "MSFT", asset: "Microsoft Corp", shares: 220, price: 428.15, marketValue: 94193.00, weight: "22.4%" },
  { symbol: "NVDA", asset: "NVIDIA Corp", shares: 600, price: 141.54, marketValue: 84924.00, weight: "20.2%" },
  { symbol: "AMZN", asset: "Amazon.com Inc", shares: 310, price: 187.80, marketValue: 58218.00, weight: "13.9%" },
  { symbol: "SPY", asset: "S&P 500 ETF", shares: 80, price: 588.42, marketValue: 47073.60, weight: "11.2%" },
  { symbol: "USD", asset: "Cash & Equivalents", shares: 31400, price: 1.00, marketValue: 31400.00, weight: "7.5%" },
];

export function PortfolioPanelAdapter({
  panel,
  context,
  onUpdateContext,
}: PortfolioPanelAdapterProps) {
  const portfolioName = (context.PORTFOLIO as string) || "Flagship Multi-Asset Fund";
  const totalNav = HOLDINGS.reduce((acc, h) => acc + h.marketValue, 0);

  const handleSelectHolding = (symbol: string) => {
    if (symbol !== "USD" && !panel.independent_mode) {
      onUpdateContext({
        INSTRUMENT: symbol,
        COMPANY: symbol,
      });
    }
  };

  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
        <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
          <Briefcase className="w-3.5 h-3.5 text-blue-400" />
          <span>{portfolioName}</span>
        </div>
        <span className="text-[10px] text-emerald-400 font-bold">
          NAV: ${totalNav.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar p-2">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-default text-[10px] text-atlas-text-muted uppercase">
              <th className="py-1 px-2">Security</th>
              <th className="py-1 px-2 text-right">Qty</th>
              <th className="py-1 px-2 text-right">Price</th>
              <th className="py-1 px-2 text-right">Market Value</th>
              <th className="py-1 px-2 text-right">Weight</th>
            </tr>
          </thead>
          <tbody>
            {HOLDINGS.map((h) => (
              <tr
                key={h.symbol}
                onClick={() => handleSelectHolding(h.symbol)}
                className="border-b border-atlas-border-subtle hover:bg-atlas-surface-hover cursor-pointer transition-colors"
              >
                <td className="py-1.5 px-2">
                  <div className="font-bold text-atlas-text-primary">{h.symbol}</div>
                  <div className="text-[10px] text-atlas-text-muted">{h.asset}</div>
                </td>
                <td className="py-1.5 px-2 text-right text-atlas-text-primary">{h.shares.toLocaleString()}</td>
                <td className="py-1.5 px-2 text-right text-atlas-text-primary">${h.price.toFixed(2)}</td>
                <td className="py-1.5 px-2 text-right font-bold text-atlas-text-primary">
                  ${h.marketValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </td>
                <td className="py-1.5 px-2 text-right text-blue-400 font-semibold">{h.weight}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

