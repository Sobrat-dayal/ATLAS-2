"use client";

import React, { useEffect, useState } from "react";
import { ArrowDownRight, ArrowUpRight, ListOrdered, Plus } from "lucide-react";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";

interface WatchlistPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

interface WatchItem {
  id: string;
  symbol: string;
  name: string;
  last: number;
  change: number;
  changePct: number;
  volume: string;
}

const DEFAULT_WATCHLIST: WatchItem[] = [
  { id: "1", symbol: "AAPL", name: "Apple Inc", last: 231.41, change: 1.10, changePct: 0.48, volume: "48.2M" },
  { id: "2", symbol: "MSFT", name: "Microsoft Corp", last: 428.15, change: 2.45, changePct: 0.58, volume: "22.1M" },
  { id: "3", symbol: "NVDA", name: "NVIDIA Corp", last: 141.54, change: 2.80, changePct: 2.02, volume: "62.4M" },
  { id: "4", symbol: "GOOGL", name: "Alphabet Inc", last: 169.23, change: -0.45, changePct: -0.26, volume: "18.9M" },
  { id: "5", symbol: "AMZN", name: "Amazon.com Inc", last: 187.80, change: 1.95, changePct: 1.05, volume: "31.5M" },
  { id: "6", symbol: "META", name: "Meta Platforms", last: 592.10, change: 5.60, changePct: 0.95, volume: "14.2M" },
  { id: "7", symbol: "TSLA", name: "Tesla Inc", last: 260.48, change: -3.40, changePct: -1.29, volume: "55.8M" },
];

export function WatchlistPanelAdapter({
  panel,
  context,
  onUpdateContext,
}: WatchlistPanelAdapterProps) {
  const [items] = useState<WatchItem[]>(DEFAULT_WATCHLIST);
  const [selectedSymbol, setSelectedSymbol] = useState<string>(
    (context.INSTRUMENT as string) || "AAPL"
  );

  useEffect(() => {
    if (context.INSTRUMENT && typeof context.INSTRUMENT === "string") {
      setSelectedSymbol(context.INSTRUMENT);
    }
  }, [context.INSTRUMENT]);

  const handleSelect = (item: WatchItem) => {
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
          <ListOrdered className="w-3.5 h-3.5 text-blue-400" />
          <span>Equities Watchlist</span>
        </div>
        <span className="text-[10px] text-atlas-text-muted">{items.length} items</span>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar p-1">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-default text-[10px] text-atlas-text-muted uppercase">
              <th className="py-1 px-2">Ticker</th>
              <th className="py-1 px-2 text-right">Last</th>
              <th className="py-1 px-2 text-right">Chg</th>
              <th className="py-1 px-2 text-right">% Chg</th>
              <th className="py-1 px-2 text-right">Vol</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => {
              const isSelected = selectedSymbol === item.symbol;
              const isPositive = item.change >= 0;
              return (
                <tr
                  key={item.id}
                  onClick={() => handleSelect(item)}
                  className={`border-b border-atlas-border-subtle cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-blue-500/15 text-blue-400 font-semibold"
                      : "hover:bg-atlas-surface-hover text-atlas-text-primary"
                  }`}
                >
                  <td className="py-1.5 px-2 font-bold">{item.symbol}</td>
                  <td className="py-1.5 px-2 text-right">{item.last.toFixed(2)}</td>
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
                  <td className="py-1.5 px-2 text-right text-atlas-text-muted">{item.volume}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

