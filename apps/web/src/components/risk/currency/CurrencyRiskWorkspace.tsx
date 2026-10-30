"use client";

import React from "react";
import { CurrencyRiskSnapshotDTO } from "@/lib/risk/types";
import {
  formatCurrency,
  formatFactorLoading,
  formatSignedPercent,
  formatVolPercent,
  formatWeight,
} from "@/lib/risk/formatting";
import {
  Coins,
  DollarSign,
  Globe,
  HelpCircle,
  RefreshCw,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

interface CurrencyRiskWorkspaceProps {
  snapshot: CurrencyRiskSnapshotDTO | null;
  loading: boolean;
  onRefresh: () => void;
}

export function CurrencyRiskWorkspace({
  snapshot,
  loading,
  onRefresh,
}: CurrencyRiskWorkspaceProps) {
  if (!snapshot) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-atlas-border-default/60 rounded m-4 bg-atlas-surface-1/40">
        <Globe className="h-10 w-10 text-atlas-text-secondary/50 mb-3 animate-pulse" />
        <h3 className="text-sm font-semibold text-atlas-text-primary">No Currency Risk Snapshot Available</h3>
        <p className="text-xs text-atlas-text-secondary max-w-md mt-1 mb-4">
          Analyze multi-currency denomination exposures, historical FX volatility, and base vs local return interaction.
        </p>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 rounded bg-atlas-accent px-3 py-1.5 text-xs font-semibold text-black transition hover:bg-atlas-accent/90 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Load Currency Risk
        </button>
      </div>
    );
  }

  const interaction = snapshot.base_local_interaction || {};
  const localRet = interaction.local_return ?? 0.10;
  const fxRet = interaction.fx_return ?? -0.05;
  const crossTerm = interaction.interaction ?? -0.005;
  const baseRet = interaction.base_return ?? 0.045;

  return (
    <div className="space-y-4 p-4">
      {/* 1. Header Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
            Multi-Currency Risk & FX Sensitivity
          </span>
          <span className="rounded bg-atlas-surface-2 px-2 py-0.5 text-xs font-mono text-atlas-text-secondary border border-atlas-border-default">
            Base: {snapshot.reporting_currency}
          </span>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 rounded bg-atlas-surface-2 border border-atlas-border-default px-2.5 py-1 text-xs text-atlas-text-secondary hover:text-atlas-text-primary transition disabled:opacity-50"
        >
          <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* 2. Key Metrics Grid */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {/* Base Currency Exposure */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Base Currency ({snapshot.reporting_currency})</span>
            <DollarSign className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-emerald-400">
            {formatWeight(1.0 - snapshot.foreign_currency_weight)}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-secondary">
            Zero direct foreign exchange risk exposure
          </div>
        </div>

        {/* Foreign Currency Exposure */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Foreign FX Exposure</span>
            <Globe className="h-4 w-4 text-sky-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-sky-400">
            {formatWeight(snapshot.foreign_currency_weight)}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-secondary">
            Market Value: {formatCurrency(snapshot.foreign_currency_market_value)}
          </div>
        </div>

        {/* Multiplicative Interaction Term */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Compounding Interaction</span>
            <Coins className="h-4 w-4 text-amber-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-amber-400">
            {formatSignedPercent(crossTerm, 2)}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-secondary">
            Cross product: R_local × R_FX (Part XLIV Fixture)
          </div>
        </div>
      </div>

      {/* 3. Multiplicative Compounding Reference Card */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1/70 p-3.5">
        <h4 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide mb-1">
          Base vs. Local Return Decomposition Principle (Part XLIV)
        </h4>
        <p className="text-xs text-atlas-text-secondary mb-3">
          Discrete base currency returns strictly obey multiplicative interaction rather than simple additive summing:
          <span className="font-mono text-atlas-text-primary ml-1">
            1 + R_base = (1 + R_local) · (1 + R_FX) ⟹ R_base = R_local + R_FX + (R_local · R_FX)
          </span>
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-center">
          <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-2/60 p-2">
            <div className="text-[10px] text-atlas-text-secondary uppercase">Local Return</div>
            <div className="text-sm font-bold text-emerald-400">{formatSignedPercent(localRet)}</div>
          </div>
          <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-2/60 p-2">
            <div className="text-[10px] text-atlas-text-secondary uppercase">FX Return</div>
            <div className="text-sm font-bold text-rose-400">{formatSignedPercent(fxRet)}</div>
          </div>
          <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-2/60 p-2">
            <div className="text-[10px] text-atlas-text-secondary uppercase">Cross-Interaction</div>
            <div className="text-sm font-bold text-amber-400">{formatSignedPercent(crossTerm, 2)}</div>
          </div>
          <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-2/60 p-2">
            <div className="text-[10px] text-atlas-text-secondary uppercase">Base Net Return</div>
            <div className="text-sm font-bold text-sky-400">{formatSignedPercent(baseRet)}</div>
          </div>
        </div>
      </div>

      {/* 4. Currency Denomination Exposure Table */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <div className="border-b border-atlas-border-default/40 p-3">
          <h4 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
            Currency Denomination Exposures & Sensitivities
          </h4>
          <p className="text-[11px] text-atlas-text-secondary mt-0.5">
            Asset denomination weights, cash balances, historical FX volatility, and empirical regression beta β_FX.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-atlas-border-default/40 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3">Currency</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3 text-right">Portfolio Weight</th>
                <th className="py-2.5 px-3 text-right">Total Market Value</th>
                <th className="py-2.5 px-3 text-right">Cash Balance</th>
                <th className="py-2.5 px-3 text-right">Historical FX Vol (ann.)</th>
                <th className="py-2.5 px-3 text-right">FX Beta (β_FX)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/30 font-mono text-atlas-text-primary">
              {snapshot.exposures.map((exp) => (
                <tr key={exp.currency} className="hover:bg-atlas-surface-2/30 transition">
                  <td className="py-2.5 px-3 font-bold text-atlas-accent">{exp.currency}</td>
                  <td className="py-2.5 px-3 text-[11px] text-atlas-text-secondary font-sans">{exp.exposure_type}</td>
                  <td className="py-2.5 px-3 text-right font-bold text-sky-400">{formatWeight(exp.weight)}</td>
                  <td className="py-2.5 px-3 text-right">{formatCurrency(exp.market_value)}</td>
                  <td className="py-2.5 px-3 text-right text-atlas-text-secondary">{formatCurrency(exp.cash_market_value)}</td>
                  <td className="py-2.5 px-3 text-right">
                    {exp.historical_fx_volatility !== null && exp.historical_fx_volatility !== undefined
                      ? formatVolPercent(exp.historical_fx_volatility)
                      : "—"}
                  </td>
                  <td className="py-2.5 px-3 text-right font-semibold">
                    {exp.fx_sensitivity_beta !== null && exp.fx_sensitivity_beta !== undefined
                      ? formatFactorLoading(exp.fx_sensitivity_beta)
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

