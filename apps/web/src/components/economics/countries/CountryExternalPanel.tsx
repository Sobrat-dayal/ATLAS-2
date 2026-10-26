"use client";

import React from "react";
import {
  Globe,
  ArrowUpRight,
  ArrowDownLeft,
  DollarSign,
  TrendingDown,
  TrendingUp,
  Scale,
  ShieldCheck,
  Info,
} from "lucide-react";
import { CountryExternalSummaryDTO } from "@/lib/economics/countries";

interface CountryExternalPanelProps {
  external: CountryExternalSummaryDTO | null;
}

export function CountryExternalPanel({ external }: CountryExternalPanelProps) {
  if (!external) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded">
        No international trade, balance of payments, or reserve statistics available for this country.
      </div>
    );
  }

  const formatPct = (val?: number | null) => {
    if (val === undefined || val === null) return "—";
    const sign = val > 0 ? "+" : "";
    return `${sign}${val.toFixed(1)}%`;
  };

  const formatBillions = (val?: number | null) => {
    if (val === undefined || val === null) return "—";
    return `$${val.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}B`;
  };

  return (
    <div className="space-y-4">
      {/* External Sector Banner */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                International Trade, Balance of Payments & Foreign Reserves
              </h3>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-cyan-400 border border-atlas-border-subtle">
                {external.reference_period}
              </span>
            </div>
            <p className="text-xs text-atlas-text-muted mt-1">
              Merchandise customs trade, services trade, current account balance, financial flows (FDI), and sovereign FX reserves.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto font-mono text-xs">
            <span className="px-2.5 py-1 rounded bg-atlas-background border border-atlas-border-subtle text-atlas-text-primary flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-atlas-accent" />
              <span>IMF BPM6 Standard</span>
            </span>
          </div>
        </div>

        {/* Primary Trade & External Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 pt-4 border-t border-atlas-border-subtle">
          {/* Card 1: Current Account % GDP */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Current Account Balance</span>
              <span className="font-mono text-[10px]">% of GDP</span>
            </div>
            <div
              className={`text-xl font-bold font-mono mt-1 ${
                (external.current_account_pct_gdp || 0) < 0 ? "text-amber-400" : "text-emerald-400"
              }`}
            >
              {formatPct(external.current_account_pct_gdp)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Net: {formatBillions(external.current_account_balance_billions)}
            </div>
          </div>

          {/* Card 2: Merchandise Trade Balance */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Goods Trade Balance</span>
              <span className="font-mono text-[10px]">Merchandise</span>
            </div>
            <div
              className={`text-xl font-bold font-mono mt-1 ${
                (external.merchandise_trade_balance_billions || 0) < 0 ? "text-rose-400" : "text-emerald-400"
              }`}
            >
              {formatBillions(external.merchandise_trade_balance_billions)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Customs trade basis
            </div>
          </div>

          {/* Card 3: Foreign Exchange Reserves */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>FX Reserves</span>
              <span className="font-mono text-[10px]">{external.fx_reserves_currency}</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {formatBillions(external.foreign_exchange_reserves_billions)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Sovereign foreign liquidity
            </div>
          </div>

          {/* Card 4: Net FDI Inflows */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>FDI Net Inflows</span>
              <span className="font-mono text-[10px]">Financial Account</span>
            </div>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
              {formatBillions(external.fdi_net_inflow_billions)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Direct foreign corporate investment
            </div>
          </div>
        </div>
      </div>

      {/* Trade Flows Table */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-atlas-border-subtle flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-cyan-400" />
            <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
              International Trade in Goods & Services (BPM6 Decomposition)
            </h4>
          </div>
          <span className="text-[11px] font-mono text-atlas-text-muted">
            Total Trade Balance: {formatBillions(external.total_trade_balance_billions)}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-atlas-background/50 border-b border-atlas-border-subtle text-[11px] font-mono text-atlas-text-muted uppercase">
                <th className="py-2.5 px-4 font-semibold">Account Category</th>
                <th className="py-2.5 px-4 font-semibold text-right">Exports (USD B)</th>
                <th className="py-2.5 px-4 font-semibold text-right">Imports (USD B)</th>
                <th className="py-2.5 px-4 font-semibold text-right">Net Balance (USD B)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle font-mono">
              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary">
                  Merchandise Goods Trade (Customs Basis)
                </td>
                <td className="py-2.5 px-4 text-right text-emerald-400">
                  {formatBillions(external.goods_exports_billions)}
                </td>
                <td className="py-2.5 px-4 text-right text-rose-400">
                  {formatBillions(external.goods_imports_billions)}
                </td>
                <td
                  className={`py-2.5 px-4 text-right font-bold ${
                    (external.merchandise_trade_balance_billions || 0) < 0 ? "text-rose-400" : "text-emerald-400"
                  }`}
                >
                  {formatBillions(external.merchandise_trade_balance_billions)}
                </td>
              </tr>

              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary">
                  Commercial Services Trade (BOP Basis)
                </td>
                <td className="py-2.5 px-4 text-right text-emerald-400">
                  {formatBillions(external.services_exports_billions)}
                </td>
                <td className="py-2.5 px-4 text-right text-rose-400">
                  {formatBillions(external.services_imports_billions)}
                </td>
                <td
                  className={`py-2.5 px-4 text-right font-bold ${
                    (external.services_trade_balance_billions || 0) < 0 ? "text-rose-400" : "text-emerald-400"
                  }`}
                >
                  {formatBillions(external.services_trade_balance_billions)}
                </td>
              </tr>

              <tr className="bg-atlas-background/30 font-semibold">
                <td className="py-2.5 px-4 font-sans text-atlas-text-primary">
                  Total Goods & Services Balance
                </td>
                <td className="py-2.5 px-4 text-right text-atlas-text-muted">—</td>
                <td className="py-2.5 px-4 text-right text-atlas-text-muted">—</td>
                <td
                  className={`py-2.5 px-4 text-right ${
                    (external.total_trade_balance_billions || 0) < 0 ? "text-rose-400" : "text-emerald-400"
                  }`}
                >
                  {formatBillions(external.total_trade_balance_billions)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="p-3 bg-atlas-background/40 border-t border-atlas-border-subtle text-[11px] text-atlas-text-muted flex items-start gap-2">
          <Info className="w-3.5 h-3.5 shrink-0 text-atlas-accent mt-0.5" />
          <span>
            {external.notes ||
              "Current account balance includes goods & services trade, net primary income (yields on foreign investments), and secondary transfers. It is distinct from customs goods trade."}
          </span>
        </div>
      </div>
    </div>
  );
}
