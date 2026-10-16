"use client";

import React from "react";
import { FileText, Layers, TrendingUp } from "lucide-react";

export type FuturesTab = "contracts" | "commodities" | "spot";

export interface FuturesMarketTabsProps {
  activeTab: FuturesTab;
  onSelectTab: (tab: FuturesTab) => void;
  contractsCount?: number;
  commoditiesCount?: number;
  spotCount?: number;
}

export function FuturesMarketTabs({
  activeTab,
  onSelectTab,
  contractsCount,
  commoditiesCount,
  spotCount,
}: FuturesMarketTabsProps) {
  const tabs = [
    {
      id: "contracts" as FuturesTab,
      label: "Futures Contracts",
      count: contractsCount,
      icon: FileText,
    },
    {
      id: "commodities" as FuturesTab,
      label: "Commodities Catalog",
      count: commoditiesCount,
      icon: Layers,
    },
    {
      id: "spot" as FuturesTab,
      label: "Spot Benchmarks",
      count: spotCount,
      icon: TrendingUp,
    },
  ];

  return (
    <div
      role="tablist"
      aria-label="Futures workspace sub-views"
      className="flex items-center gap-1 border-b border-[var(--atlas-border-subtle)] pb-2 mb-4 overflow-x-auto no-scrollbar"
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        const Icon = tab.icon;

        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => onSelectTab(tab.id)}
            className={`inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50 ${
              isActive
                ? "bg-[var(--atlas-surface-card)] text-emerald-400 border border-[var(--atlas-border-subtle)] font-semibold shadow-xs"
                : "text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-card)]/50"
            }`}
          >
            <Icon className="h-3.5 w-3.5" aria-hidden="true" />
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span
                className={`px-1.5 py-0.2 rounded-full font-mono text-[10px] ${
                  isActive
                    ? "bg-emerald-950/60 text-emerald-300 border border-emerald-800/40"
                    : "bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-tertiary)]"
                }`}
              >
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
