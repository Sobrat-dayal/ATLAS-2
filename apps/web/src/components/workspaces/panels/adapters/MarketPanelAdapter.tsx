"use client";

import React, { useEffect, useState } from "react";
import { ArrowDownRight, ArrowUpRight, Globe, TrendingUp } from "lucide-react";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";

interface MarketPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

interface MarketItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePct: number;
  category: string;
}

const DEFAULT_MARKET_ITEMS: MarketItem[] = [
  { symbol: "SPY", name: "S&P 500 ETF", price: 588.42, change: 3.25, changePct: 0.56, category: "Indices" },
  { symbol: "QQQ", name: "Invesco QQQ Trust", price: 504.18, change: 4.82, changePct: 0.97, category: "Indices" },
  { symbol: "DIA", name: "Dow Jones Industrial", price: 423.85, change: -0.65, changePct: -0.15, category: "Indices" },
  { symbol: "IWM", name: "Russell 2000 ETF", price: 221.30, change: 1.15, changePct: 0.52, category: "Indices" },
  { symbol: "NVDA", name: "NVIDIA Corp", price: 141.54, change: 2.80, changePct: 2.02, category: "Tech" },
  { symbol: "AAPL", name: "Apple Inc", price: 231.41, change: 1.10, changePct: 0.48, category: "Tech" },
  { symbol: "MSFT", name: "Microsoft Corp", price: 428.15, change: 2.45, changePct: 0.58, category: "Tech" },
  { symbol: "GOOGL", name: "Alphabet Inc", price: 169.23, change: -0.45, changePct: -0.26, category: "Tech" },
  { symbol: "US10Y", name: "US 10-Year Yield", price: 4.24, change: 0.02, changePct: 0.47, category: "Rates" },
  { symbol: "DXY", name: "US Dollar Index", price: 104.22, change: 0.18, changePct: 0.17, category: "FX" },
  { symbol: "CL", name: "WTI Crude Oil", price: 71.20, change: -0.85, changePct: -1.18, category: "Commodities" },
  { symbol: "GC", name: "Gold Comex", price: 2748.50, change: 14.20, changePct: 0.52, category: "Commodities" },
];

export function MarketPanelAdapter({
  panel,
  context,
  onUpdateContext,
}: MarketPanelAdapterProps) {
  const [selectedSymbol, setSelectedSymbol] = useState<string>(
    (context.INSTRUMENT as string) || "SPY"
  );

  useEffect(() => {
    if (context.INSTRUMENT && typeof context.INSTRUMENT === "string") {
      setSelectedSymbol(context.INSTRUMENT);
    }
  }, [context.INSTRUMENT]);

  const handleSelect = (item: MarketItem) => {
    setSelectedSymbol(item.symbol);
    if (!panel.independent_mode) {
      onUpdateContext({
        INSTRUMENT: item.symbol,
        COMPANY: item.symbol,
      });
    }
  };

  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
        <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
          <Globe className="w-3.5 h-3.5 text-blue-400" />
          <span>Global Markets Overview</span>
        </div>
        <span className="text-[10px] text-atlas-text-muted">Live Stream</span>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar p-2">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-default text-[10px] text-atlas-text-muted uppercase">
              <th className="py-1 px-2">Symbol</th>
              <th className="py-1 px-2">Name</th>
              <th className="py-1 px-2 text-right">Price</th>
              <th className="py-1 px-2 text-right">Change</th>
              <th className="py-1 px-2 text-right">% Chg</th>
            </tr>
          </thead>
          <tbody>
            {DEFAULT_MARKET_ITEMS.map((item) => {
              const isSelected = selectedSymbol === item.symbol;
              const isPositive = item.change >= 0;
              return (
                <tr
                  key={item.symbol}
                  onClick={() => handleSelect(item)}
                  className={`border-b border-atlas-border-subtle cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-blue-500/15 text-blue-400 font-semibold"
                      : "hover:bg-atlas-surface-hover text-atlas-text-primary"
                  }`}
                >
                  <td className="py-1.5 px-2 font-bold">{item.symbol}</td>
                  <td className="py-1.5 px-2 text-atlas-text-muted truncate max-w-[120px]">
                    {item.name}
                  </td>
                  <td className="py-1.5 px-2 text-right">{item.price.toFixed(2)}</td>
                  <td
                    className={`py-1.5 px-2 text-right ${
                      isPositive ? "text-emerald-400" : "text-rose-400"
                    }`}
                  >
                    {isPositive ? `+${item.change.toFixed(2)}` : item.change.toFixed(2)}
                  </td>
                  <td
                    className={`py-1.5 px-2 text-right flex items-center justify-end gap-0.5 ${
                      isPositive ? "text-emerald-400" : "text-rose-400"
                    }`}
                  >
                    {isPositive ? (
                      <ArrowUpRight className="w-3 h-3 shrink-0" />
                    ) : (
                      <ArrowDownRight className="w-3 h-3 shrink-0" />
                    )}
                    <span>{Math.abs(item.changePct).toFixed(2)}%</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

