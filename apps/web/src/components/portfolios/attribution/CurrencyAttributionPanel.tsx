"use client";

import React from "react";
import {
  formatBps,
  formatPercent,
  formatWeight,
  getEffectColorClass,
} from "@/lib/portfolios/attribution/formatting";
import { AttributionRunDTO } from "@/lib/portfolios/attribution/types";
import { Coins, Globe2 } from "lucide-react";

interface CurrencyAttributionPanelProps {
  run: AttributionRunDTO;
}

export function CurrencyAttributionPanel({ run }: CurrencyAttributionPanelProps) {
  const currencies = run.currency_effects || [];

  return (
    <div className="space-y-4">
      {/* Methodology Explainer Banner */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="flex items-start gap-3">
          <div className="rounded bg-atlas-accent/10 p-2 text-atlas-accent">
            <Coins className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Multi-Currency Performance Attribution (Base Currency: {run.reporting_currency})
            </h3>
            <p className="mt-1 text-xs text-atlas-text-secondary leading-relaxed">
              Decomposes unhedged international asset returns into local currency market movement, foreign exchange rate fluctuation,
              and the compounding cross-product interaction term:
              <span className="ml-1 inline-block font-mono font-semibold text-atlas-accent">
                R_base = R_local + R_FX + (R_local · R_FX)
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Currency Effects Table */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <div className="border-b border-atlas-border-default/40 p-4">
          <h4 className="text-sm font-semibold text-atlas-text-primary">
            Currency Breakdown & Local Return Decomposition
          </h4>
          <p className="text-xs text-atlas-text-secondary">
            Analysis of foreign exchange impact across all portfolio holdings and cash balances.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="border-b border-atlas-border-default/60 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary">
              <tr>
                <th className="px-3 py-2.5 font-medium font-sans">Currency</th>
                <th className="px-3 py-2.5 text-right font-medium">Portfolio Weight</th>
                <th className="px-3 py-2.5 text-right font-medium">Local Return (R_local)</th>
                <th className="px-3 py-2.5 text-right font-medium">FX Movement (R_FX)</th>
                <th className="px-3 py-2.5 text-right font-medium">Cross-Product (R_L · R_FX)</th>
                <th className="px-3 py-2.5 text-right font-bold text-atlas-text-primary">
                  Total Base Return (R_base)
                </th>
                <th className="px-3 py-2.5 text-right font-semibold text-atlas-accent">
                  Total Currency Effect
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/40 text-atlas-text-primary">
              {currencies.map((c) => (
                <tr key={c.currency} className="hover:bg-atlas-surface-2/40 transition-colors">
                  <td className="px-3 py-2 font-sans font-bold flex items-center gap-1.5">
                    <Globe2 className="h-3.5 w-3.5 text-atlas-text-muted" />
                    <span>{c.currency}</span>
                    {c.currency === run.reporting_currency && (
                      <span className="rounded bg-atlas-surface-3 px-1 text-[10px] text-atlas-text-muted font-normal font-sans">
                        Base
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-right">{formatWeight(c.portfolio_weight)}</td>
                  <td className="px-3 py-2 text-right">{formatPercent(c.local_return, 2, true)}</td>
                  <td className={`px-3 py-2 text-right ${getEffectColorClass(c.fx_return)}`}>
                    {formatPercent(c.fx_return, 2, true)}
                  </td>
                  <td className={`px-3 py-2 text-right ${getEffectColorClass(c.cross_product_effect)}`}>
                    {formatPercent(c.cross_product_effect, 2, true)}
                  </td>
                  <td className={`px-3 py-2 text-right font-bold ${getEffectColorClass(c.total_base_return)}`}>
                    {formatPercent(c.total_base_return, 2, true)}
                  </td>
                  <td className={`px-3 py-2 text-right font-semibold ${getEffectColorClass(c.total_currency_effect)}`}>
                    {formatPercent(c.total_currency_effect, 2, true)} ({formatBps(c.total_currency_effect)})
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

