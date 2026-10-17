"use client";

import React from "react";
import { Activity, TrendingDown, TrendingUp } from "lucide-react";
import { MoverCategory } from "@/lib/markets/movers";

export interface MoverCategoryTabsProps {
  selectedCategory: MoverCategory;
  onSelectCategory: (category: MoverCategory) => void;
  supportedCategories?: MoverCategory[];
  activityLabel?: string | null;
  disabled?: boolean;
}

export function MoverCategoryTabs({
  selectedCategory,
  onSelectCategory,
  supportedCategories = ["gainers", "losers", "most_active"],
  activityLabel,
  disabled,
}: MoverCategoryTabsProps) {
  const tabs = [
    {
      id: "gainers" as MoverCategory,
      label: "Top Gainers",
      icon: TrendingUp,
      activeColor: "text-emerald-400 border-emerald-500",
    },
    {
      id: "losers" as MoverCategory,
      label: "Top Losers",
      icon: TrendingDown,
      activeColor: "text-rose-400 border-rose-500",
    },
    {
      id: "most_active" as MoverCategory,
      label: activityLabel ? `Most Active (${activityLabel})` : "Most Active",
      icon: Activity,
      activeColor: "text-blue-400 border-blue-500",
    },
  ];

  return (
    <div
      role="tablist"
      aria-label="Ranking category"
      className="flex items-center gap-2 border-b border-[var(--atlas-border-subtle)] pb-2"
    >
      {tabs.map((tab) => {
        const isSupported = supportedCategories.includes(tab.id);
        const isSelected = selectedCategory === tab.id;
        const Icon = tab.icon;

        if (!isSupported) {
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={false}
              disabled
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--atlas-text-tertiary)] opacity-40 cursor-not-allowed border-b-2 border-transparent"
              title="Not supported for selected universe"
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        }

        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isSelected}
            disabled={disabled}
            onClick={() => onSelectCategory(tab.id)}
            className={`inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium transition-all border-b-2 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 ${
              isSelected
                ? `${tab.activeColor} bg-zinc-800/60 font-semibold rounded-t`
                : "text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] hover:bg-zinc-800/30 border-transparent rounded-t"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <Icon className="h-3.5 w-3.5" />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
}
