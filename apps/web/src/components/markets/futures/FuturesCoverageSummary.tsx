"use client";

import React from "react";
import {
  Activity,
  Layers,
  FileText,
  DollarSign,
  Scale,
  TrendingUp,
  BarChart,
  ShieldCheck,
} from "lucide-react";
import { FuturesCoverageSummary as CoverageType } from "@/lib/markets/futures";

export interface FuturesCoverageSummaryProps {
  coverage?: CoverageType | null;
  isLoading?: boolean;
}

export function FuturesCoverageSummary({
  coverage,
  isLoading,
}: FuturesCoverageSummaryProps) {
  if (isLoading && !coverage) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5 mb-5">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="p-3 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] animate-pulse h-20"
          />
        ))}
      </div>
    );
  }

  const cov = coverage || {
    total_commodities: 0,
    total_products: 0,
    total_contracts: 0,
    active_contracts: 0,
    contracts_with_last: 0,
    contracts_with_settlement: 0,
    contracts_with_volume: 0,
    contracts_with_open_interest: 0,
    exchanges_represented: [],
  };

  const cards = [
    {
      label: "Commodities",
      value: cov.total_commodities.toLocaleString(),
      sub: "Canonical Underlyings",
      icon: Layers,
    },
    {
      label: "Futures Products",
      value: cov.total_products.toLocaleString(),
      sub: "Contract Families",
      icon: Scale,
    },
    {
      label: "Listed Contracts",
      value: cov.total_contracts.toLocaleString(),
      sub: "All Expirations",
      icon: FileText,
    },
    {
      label: "Active Contracts",
      value: cov.active_contracts.toLocaleString(),
      sub: "Currently Tradable",
      icon: Activity,
    },
    {
      label: "With Trade Price",
      value: cov.contracts_with_last.toLocaleString(),
      sub: "Latest Executed",
      icon: DollarSign,
    },
    {
      label: "With Settlement",
      value: cov.contracts_with_settlement.toLocaleString(),
      sub: "Official Clearing",
      icon: ShieldCheck,
    },
    {
      label: "With Volume",
      value: cov.contracts_with_volume.toLocaleString(),
      sub: "Session Traded",
      icon: BarChart,
    },
    {
      label: "With Open Interest",
      value: cov.contracts_with_open_interest.toLocaleString(),
      sub: "Reported Positions",
      icon: TrendingUp,
    },
  ];

  return (
    <div className="mb-5">
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
        {cards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className="p-3 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] flex flex-col justify-between"
            >
              <div className="flex items-center justify-between gap-1 text-[var(--atlas-text-tertiary)]">
                <span className="text-[11px] font-medium uppercase tracking-wider truncate">
                  {card.label}
                </span>
                <Icon className="h-3.5 w-3.5 shrink-0 opacity-70" aria-hidden="true" />
              </div>
              <div className="mt-1.5">
                <div className="text-lg font-bold font-mono text-[var(--atlas-text-primary)]">
                  {card.value}
                </div>
                <div className="text-[10px] text-[var(--atlas-text-secondary)] truncate">
                  {card.sub}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {cov.exchanges_represented.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 mt-2 px-1 text-[11px] text-[var(--atlas-text-tertiary)]">
          <span className="font-medium text-[var(--atlas-text-secondary)]">Venues Represented:</span>
          {cov.exchanges_represented.map((ex) => (
            <span
              key={ex}
              className="px-1.5 py-0.5 rounded font-mono text-[10px] bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-[var(--atlas-text-secondary)]"
            >
              {ex}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
