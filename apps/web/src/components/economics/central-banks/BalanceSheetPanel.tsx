"use client";

import React from "react";
import { Banknote, Layers, ArrowDownRight, ArrowUpRight } from "lucide-react";
import {
  CentralBankBalanceSheetSummaryDTO,
  CentralBankPolicyProgramDTO,
} from "@/lib/economics/central-banks";

interface BalanceSheetPanelProps {
  balanceSheet: CentralBankBalanceSheetSummaryDTO | null;
  programs: CentralBankPolicyProgramDTO[];
}

export function BalanceSheetPanel({
  balanceSheet,
  programs,
}: BalanceSheetPanelProps) {
  if (!balanceSheet) {
    return (
      <div className="p-8 bg-atlas-surface border border-atlas-border-subtle rounded-lg text-center text-xs text-atlas-text-muted">
        Balance sheet data is not currently published or available for this monetary authority.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 1. Key Aggregates Cards */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <Banknote className="w-4 h-4 text-atlas-accent" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Consolidated Balance Sheet Position ({balanceSheet.currency})
            </h3>
          </div>
          <span className="text-xs font-mono text-atlas-text-muted">
            As of {balanceSheet.reference_date} ({balanceSheet.reporting_frequency})
          </span>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
          <div className="bg-atlas-background p-3.5 rounded border border-atlas-border-subtle">
            <span className="text-[10px] font-mono uppercase text-atlas-text-muted block">
              Total Assets
            </span>
            <span className="text-xl font-bold font-mono text-atlas-text-primary mt-1 block">
              {balanceSheet.total_assets_billions.toLocaleString()} B
            </span>
          </div>

          <div className="bg-atlas-background p-3.5 rounded border border-atlas-border-subtle">
            <span className="text-[10px] font-mono uppercase text-atlas-text-muted block">
              Total Liabilities
            </span>
            <span className="text-xl font-bold font-mono text-atlas-text-primary mt-1 block">
              {balanceSheet.total_liabilities_billions.toLocaleString()} B
            </span>
          </div>

          <div className="bg-atlas-background p-3.5 rounded border border-atlas-border-subtle">
            <span className="text-[10px] font-mono uppercase text-atlas-text-muted block">
              Securities Holdings
            </span>
            <span className="text-xl font-bold font-mono text-atlas-accent mt-1 block">
              {balanceSheet.securities_holdings_billions.toLocaleString()} B
            </span>
          </div>

          <div className="bg-atlas-background p-3.5 rounded border border-atlas-border-subtle">
            <span className="text-[10px] font-mono uppercase text-atlas-text-muted block">
              Bank Reserve Balances
            </span>
            <span className="text-xl font-bold font-mono text-indigo-400 mt-1 block">
              {balanceSheet.reserve_balances_billions.toLocaleString()} B
            </span>
          </div>
        </div>

        {/* Detailed Items Table */}
        <div className="mt-5 overflow-x-auto">
          <span className="text-[10px] uppercase font-mono text-atlas-text-muted block mb-2">
            Disclosed Asset & Liability Line Items
          </span>
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-atlas-border-subtle bg-atlas-background/50 font-mono text-[11px] text-atlas-text-muted uppercase">
                <th className="py-2 px-3">Position Name</th>
                <th className="py-2 px-3">Category</th>
                <th className="py-2 px-3">Side</th>
                <th className="py-2 px-3 text-right">Value ({balanceSheet.currency} Billions)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle/50 font-mono">
              {balanceSheet.items.map((item) => (
                <tr key={item.item_id} className="hover:bg-atlas-surface-elevated/30">
                  <td className="py-2.5 px-3 font-semibold text-atlas-text-primary font-sans">
                    {item.name}
                  </td>
                  <td className="py-2.5 px-3 text-atlas-text-muted">{item.category}</td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        item.account_side === "ASSET"
                          ? "bg-emerald-500/10 text-emerald-400"
                          : "bg-blue-500/10 text-blue-400"
                      }`}
                    >
                      {item.account_side}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right font-bold text-atlas-text-primary">
                    {item.value_billions.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="text-[10px] text-atlas-text-muted font-mono pt-3 border-t border-atlas-border-subtle mt-4">
          Notes: {balanceSheet.accounting_notes}
        </div>
      </div>

      {/* 2. Asset Purchase Programs (QE) & Balance Sheet Reduction (QT) */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-atlas-accent" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Monetary Policy Programs (QE / QT Runoff / Targeted Liquidity)
            </h3>
          </div>
          <span className="text-xs font-mono text-atlas-text-muted">
            {programs.length} Verified Programs
          </span>
        </div>

        <div className="mt-4 space-y-4">
          {programs.length > 0 ? (
            programs.map((prog) => (
              <div
                key={prog.program_id}
                className="bg-atlas-background p-4 rounded-lg border border-atlas-border-subtle space-y-2"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        prog.program_kind === "BALANCE_SHEET_RUNOFF"
                          ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                          : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      }`}
                    >
                      {prog.program_kind === "BALANCE_SHEET_RUNOFF" ? "QUANTITATIVE TIGHTENING" : prog.program_kind}
                    </span>
                    <h4 className="text-sm font-bold text-atlas-text-primary font-sans">
                      {prog.name}
                    </h4>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {prog.status}
                  </span>
                </div>

                <p className="text-xs text-atlas-text-primary leading-relaxed">
                  {prog.description}
                </p>

                <div className="flex items-center gap-4 text-[10px] font-mono text-atlas-text-muted pt-2 border-t border-atlas-border-subtle/50 flex-wrap">
                  <span>Announced: {prog.announced_date}</span>
                  <span>•</span>
                  <span>Effective: {prog.effective_start}</span>
                  {prog.current_holdings_billions != null && (
                    <>
                      <span>•</span>
                      <span className="text-atlas-text-primary font-bold">
                        Current Portfolio: {prog.current_holdings_billions.toLocaleString()} B
                      </span>
                    </>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 bg-atlas-background rounded text-xs text-atlas-text-muted text-center">
              No active quantitative easing or balance sheet runoff programs currently reported for this central bank.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
