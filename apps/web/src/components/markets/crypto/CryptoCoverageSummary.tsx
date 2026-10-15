"use client";

import React from "react";
import { Coins, Building2, TrendingUp, Layers } from "lucide-react";
import { CryptoCoverageSummary as CoverageSummaryType } from "@/lib/markets/crypto";

export interface CryptoCoverageSummaryProps {
  summary: CoverageSummaryType | null | undefined;
  isLoading: boolean;
}

export function CryptoCoverageSummary({
  summary,
  isLoading,
}: CryptoCoverageSummaryProps) {
  const cards = [
    {
      id: "assets",
      label: "Digital Assets",
      value: summary?.total_assets ?? 0,
      subtext: "Native coins, tokens, stablecoins",
      icon: Coins,
      color: "text-amber-400",
      bg: "bg-amber-950/20 border-amber-800/30",
    },
    {
      id: "spot_markets",
      label: "Spot Markets",
      value: summary?.total_spot_markets ?? 0,
      subtext: "Exchange-specific trading pairs",
      icon: Layers,
      color: "text-sky-400",
      bg: "bg-sky-950/20 border-sky-800/30",
    },
    {
      id: "venues",
      label: "Verified Venues",
      value: summary?.total_venues ?? 0,
      subtext: "Coinbase, Binance, Kraken, Bitstamp",
      icon: Building2,
      color: "text-purple-300",
      bg: "bg-zinc-900 border-zinc-800",
    },
    {
      id: "active_quotes",
      label: "Live / Indicative Quotes",
      value: summary?.markets_with_quotes ?? 0,
      subtext: "Observing Level-1 prices & volume",
      icon: TrendingUp,
      color: "text-emerald-400",
      bg: "bg-emerald-950/20 border-emerald-800/30",
    },
  ];

  return (
    <section
      aria-label="Cryptocurrency market coverage statistics"
      className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5"
    >
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.id}
            className={`p-3 rounded-lg border ${card.bg} transition-all duration-200`}
          >
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="text-[11px] font-medium text-[var(--atlas-text-secondary)] uppercase tracking-wider truncate">
                {card.label}
              </span>
              <Icon className={`h-4 w-4 shrink-0 ${card.color}`} aria-hidden="true" />
            </div>

            <div className="flex items-baseline gap-2">
              {isLoading ? (
                <div className="h-6 w-12 bg-zinc-800 animate-pulse rounded my-0.5" />
              ) : (
                <span className="text-xl font-bold font-mono text-[var(--atlas-text-primary)]">
                  {card.value}
                </span>
              )}
            </div>

            <p className="text-[10px] text-[var(--atlas-text-tertiary)] truncate mt-0.5">
              {card.subtext}
            </p>
          </div>
        );
      })}
    </section>
  );
}
