"use client";

import React from "react";
import {
  Globe,
  TrendingUp,
  Building2,
  LineChart,
  Landmark,
  Scale,
  Cpu,
} from "lucide-react";
import { NewsTabKey } from "@/lib/news/types";

interface NewsCategoryTabsProps {
  activeTab: NewsTabKey;
  onTabChange: (tab: NewsTabKey) => void;
}

const TABS: Array<{ key: NewsTabKey; label: string; icon: React.ComponentType<{ className?: string }> }> = [
  { key: "ALL", label: "All News", icon: Globe },
  { key: "MARKETS", label: "Markets", icon: TrendingUp },
  { key: "COMPANIES", label: "Companies", icon: Building2 },
  { key: "ECONOMICS", label: "Economics", icon: LineChart },
  { key: "CENTRAL_BANKS", label: "Central Banks", icon: Landmark },
  { key: "REGULATION", label: "Regulation", icon: Scale },
  { key: "TECHNOLOGY", label: "Technology", icon: Cpu },
];

export function NewsCategoryTabs({ activeTab, onTabChange }: NewsCategoryTabsProps) {
  return (
    <div className="flex items-center gap-1 overflow-x-auto py-1 scrollbar-none border-b border-zinc-200 dark:border-zinc-800">
      {TABS.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.key;
        return (
          <button
            key={tab.key}
            onClick={() => onTabChange(tab.key)}
            className={`flex items-center gap-2 px-3 py-2 text-xs font-medium rounded-t border-b-2 transition-all whitespace-nowrap ${
              isActive
                ? "border-zinc-900 dark:border-zinc-100 text-zinc-900 dark:text-zinc-100 bg-zinc-50 dark:bg-zinc-800/50"
                : "border-transparent text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-zinc-800/30"
            }`}
          >
            <Icon className={`w-3.5 h-3.5 ${isActive ? "text-zinc-900 dark:text-zinc-100" : "text-zinc-400"}`} />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
}
