"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

interface MarketTabItem {
  id: string;
  label: string;
  href?: string;
  badge?: string;
  isImplemented: boolean;
}

const MARKET_TABS: MarketTabItem[] = [
  { id: "overview", label: "Overview", href: "/markets", isImplemented: true },
  { id: "equities", label: "Equities", href: "/markets/equities", isImplemented: true },
  { id: "etfs", label: "ETFs & Funds", href: "/markets/funds", isImplemented: true },
  { id: "fx", label: "FX", href: "/markets/fx", isImplemented: true },
  { id: "crypto", label: "Cryptocurrency", href: "/markets/crypto", isImplemented: true },
  { id: "bonds", label: "Bonds", href: "/markets/bonds", isImplemented: true },
  { id: "futures", label: "Futures & Commodities", href: "/markets/futures", isImplemented: true },
  { id: "movers", label: "Movers", badge: "Stage 63", isImplemented: false },
  { id: "heatmaps", label: "Heatmaps", badge: "Stage 64", isImplemented: false },
  { id: "cross-asset", label: "Cross-Asset", badge: "Stage 65", isImplemented: false },
];

export function MarketsNavigationTabs() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Markets subviews navigation"
      className="flex items-center gap-1 overflow-x-auto pb-1 mb-5 no-scrollbar border-b border-[var(--atlas-border-subtle)]"
    >
      {MARKET_TABS.map((tab) => {
        const isActive =
          tab.isImplemented &&
          (tab.id === "overview"
            ? pathname === "/markets"
            : pathname.startsWith(tab.href || ""));

        if (!tab.isImplemented) {
          return (
            <div
              key={tab.id}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--atlas-text-tertiary)] opacity-60 cursor-not-allowed select-none whitespace-nowrap"
              title={`${tab.label} will be implemented in ${tab.badge}`}
            >
              <span>{tab.label}</span>
              {tab.badge && (
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-zinc-800 text-zinc-500 border border-zinc-700/50">
                  {tab.badge}
                </span>
              )}
            </div>
          );
        }

        return (
          <Link
            key={tab.id}
            href={tab.href!}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-t-md whitespace-nowrap transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50 ${
              isActive
                ? "bg-[var(--atlas-surface-card)] text-emerald-400 border-b-2 border-emerald-400 font-semibold"
                : "text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-card)]/40"
            }`}
          >
            <span>{tab.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
