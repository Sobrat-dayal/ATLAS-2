"use client";

import React from "react";
import {
  Activity,
  Layers,
  LineChart,
  PieChart,
  ShieldAlert,
  Sliders,
  TrendingUp,
} from "lucide-react";

export type OptionsViewMode =
  | "OVERVIEW"
  | "CHAIN"
  | "VOLATILITY"
  | "ACTIVITY"
  | "STRATEGIES"
  | "POSITIONS";

interface OptionsNavigationProps {
  currentView: OptionsViewMode;
  onViewChange: (view: OptionsViewMode) => void;
  selectedSymbol: string;
  underlyingPrice?: number;
  currency?: string;
  hasAdjustedContracts?: boolean;
  onOpenAdjustments?: () => void;
  legCount: number;
}

export function OptionsNavigation({
  currentView,
  onViewChange,
  selectedSymbol,
  underlyingPrice,
  currency = "USD",
  hasAdjustedContracts,
  onOpenAdjustments,
  legCount,
}: OptionsNavigationProps) {
  const views: { id: OptionsViewMode; label: string; icon: React.ReactNode; badge?: string | number }[] = [
    { id: "OVERVIEW", label: "Overview", icon: <TrendingUp className="w-4 h-4" /> },
    { id: "CHAIN", label: "Options Chain", icon: <Layers className="w-4 h-4" /> },
    { id: "VOLATILITY", label: "Volatility & Skew", icon: <LineChart className="w-4 h-4" /> },
    { id: "ACTIVITY", label: "Open Interest & Volume", icon: <Activity className="w-4 h-4" /> },
    {
      id: "STRATEGIES",
      label: "Strategy Builder",
      icon: <Sliders className="w-4 h-4" />,
      badge: legCount > 0 ? legCount : undefined,
    },
    { id: "POSITIONS", label: "Positions", icon: <PieChart className="w-4 h-4" /> },
  ];

  const prefix = currency === "INR" ? "₹" : currency === "EUR" ? "€" : "$";

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-zinc-800 bg-zinc-950/70 px-4 py-2.5 gap-3">
      <div className="flex items-center gap-3">
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-bold tracking-tight text-white">{selectedSymbol}</span>
          {underlyingPrice !== undefined && (
            <span className="font-mono text-sm text-zinc-300">
              {prefix}{underlyingPrice.toFixed(2)}
            </span>
          )}
        </div>

        {hasAdjustedContracts && (
          <button
            onClick={onOpenAdjustments}
            className="flex items-center gap-1.5 px-2 py-0.5 text-xs font-medium text-amber-300 bg-amber-500/15 border border-amber-500/30 rounded-md hover:bg-amber-500/25 transition-colors"
            title="Nonstandard corporate-action adjusted contracts exist"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Corporate Action Adjusted</span>
          </button>
        )}
      </div>

      <nav className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
        {views.map((v) => {
          const isActive = currentView === v.id;
          return (
            <button
              key={v.id}
              onClick={() => onViewChange(v.id)}
              className={`flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors whitespace-nowrap ${
                isActive
                  ? "bg-zinc-800 text-cyan-400 border border-zinc-700 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
              }`}
            >
              {v.icon}
              <span>{v.label}</span>
              {v.badge !== undefined && (
                <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  {v.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
