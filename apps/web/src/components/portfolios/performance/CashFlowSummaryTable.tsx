"use client";

import React, { useState } from "react";
import { formatCurrency, getCashFlowClassificationBadge } from "@/lib/portfolios/performance/formatting";
import { CashFlowClassification, PerformanceCashFlowDTO } from "@/lib/portfolios/performance/types";
import { ArrowDownRight, ArrowUpRight, Filter, Info } from "lucide-react";

interface CashFlowSummaryTableProps {
  flows: PerformanceCashFlowDTO[];
  baseCurrency: string;
}

export function CashFlowSummaryTable({ flows, baseCurrency }: CashFlowSummaryTableProps) {
  const [filterType, setFilterType] = useState<string>("ALL");

  const filteredFlows = flows.filter((f) => {
    if (filterType === "EXTERNAL_ONLY") {
      return (
        f.classification === "EXTERNAL_CONTRIBUTION" ||
        f.classification === "EXTERNAL_WITHDRAWAL"
      );
    }
    if (filterType === "INTERNAL_ONLY") {
      return (
        f.classification !== "EXTERNAL_CONTRIBUTION" &&
        f.classification !== "EXTERNAL_WITHDRAWAL"
      );
    }
    return true;
  });

  return (
    <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-4 shadow-xs">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default/40 pb-2.5">
        <div>
          <h4 className="text-xs font-semibold text-atlas-text-primary">
            Classified Cash Flow Journal
          </h4>
          <p className="text-[11px] text-atlas-text-secondary">
            Deterministic classification into external investor flows vs internal portfolio operations.
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-1.5 text-xs">
          <Filter className="h-3.5 w-3.5 text-atlas-text-tertiary" />
          <button
            onClick={() => setFilterType("ALL")}
            className={`rounded-sm px-2.5 py-1 text-xs transition-colors ${
              filterType === "ALL"
                ? "bg-atlas-accent text-white"
                : "text-atlas-text-secondary hover:bg-atlas-surface-2 hover:text-atlas-text-primary"
            }`}
          >
            All Flows ({flows.length})
          </button>
          <button
            onClick={() => setFilterType("EXTERNAL_ONLY")}
            className={`rounded-sm px-2.5 py-1 text-xs transition-colors ${
              filterType === "EXTERNAL_ONLY"
                ? "bg-atlas-accent text-white"
                : "text-atlas-text-secondary hover:bg-atlas-surface-2 hover:text-atlas-text-primary"
            }`}
          >
            External Only
          </button>
          <button
            onClick={() => setFilterType("INTERNAL_ONLY")}
            className={`rounded-sm px-2.5 py-1 text-xs transition-colors ${
              filterType === "INTERNAL_ONLY"
                ? "bg-atlas-accent text-white"
                : "text-atlas-text-secondary hover:bg-atlas-surface-2 hover:text-atlas-text-primary"
            }`}
          >
            Internal Trades & Fees
          </button>
        </div>
      </div>

      {/* Explanatory callout banner */}
      <div className="mt-3 flex items-start gap-2 rounded-sm border border-atlas-border-default/50 bg-atlas-surface-2/40 p-2.5 text-[11px] text-atlas-text-secondary">
        <Info className="h-4 w-4 shrink-0 text-atlas-accent mt-0.5" />
        <div>
          <span className="font-semibold text-atlas-text-primary">Perspective Accounting: </span>
          <span className="text-emerald-400 font-medium">Portfolio Flow:</span> Inflows are (+) contributions into portfolio valuation;
          {" "}<span className="text-blue-400 font-medium">Investor Flow (XIRR):</span> Contributions are (-) capital outlays by the investor, withdrawals and terminal liquidation are (+).
        </div>
      </div>

      {/* Table */}
      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-atlas-border-default/60 text-[11px] text-atlas-text-tertiary">
              <th className="py-2 pr-3 font-medium">Date</th>
              <th className="px-2 py-2 font-medium">Classification</th>
              <th className="px-2 py-2 font-medium">Description</th>
              <th className="px-2 py-2 text-right font-medium">Native Amount</th>
              <th className="px-2 py-2 text-right font-medium">FX Rate</th>
              <th className="px-2 py-2 text-right font-medium text-atlas-text-primary">
                Portfolio Flow ({baseCurrency})
              </th>
              <th className="py-2 pl-3 text-right font-medium text-atlas-text-secondary">
                Investor Flow (XIRR)
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/30">
            {filteredFlows.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-atlas-text-tertiary">
                  No cash flow events match the selected filter.
                </td>
              </tr>
            ) : (
              filteredFlows.map((cf) => {
                const badge = getCashFlowClassificationBadge(cf.classification);
                const pFlow = parseFloat(cf.portfolio_flow_amount);
                const iFlow = parseFloat(cf.investor_flow_amount);

                return (
                  <tr key={cf.id} className="hover:bg-atlas-surface-2/40 transition-colors">
                    <td className="py-2.5 pr-3 text-atlas-text-secondary whitespace-nowrap">
                      {new Date(cf.flow_date).toLocaleDateString()}
                    </td>
                    <td className="px-2 py-2.5 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center rounded-xs border px-1.5 py-0.5 text-[10px] font-sans font-medium ${badge.colorClass}`}
                      >
                        {badge.label}
                      </span>
                    </td>
                    <td className="px-2 py-2.5 font-sans text-atlas-text-primary max-w-xs truncate" title={cf.description}>
                      {cf.description}
                    </td>
                    <td className="px-2 py-2.5 text-right text-atlas-text-secondary whitespace-nowrap">
                      {formatCurrency(cf.native_amount, cf.native_currency)}
                    </td>
                    <td className="px-2 py-2.5 text-right text-atlas-text-tertiary">
                      {parseFloat(cf.fx_rate).toFixed(4)}
                    </td>
                    <td className="px-2 py-2.5 text-right whitespace-nowrap font-medium">
                      {pFlow > 0 ? (
                        <span className="text-emerald-400 flex items-center justify-end gap-0.5">
                          <ArrowUpRight className="h-3 w-3" />
                          +{formatCurrency(pFlow, baseCurrency)}
                        </span>
                      ) : pFlow < 0 ? (
                        <span className="text-blue-400 flex items-center justify-end gap-0.5">
                          <ArrowDownRight className="h-3 w-3" />
                          {formatCurrency(pFlow, baseCurrency)}
                        </span>
                      ) : (
                        <span className="text-atlas-text-tertiary">0.00</span>
                      )}
                    </td>
                    <td className="py-2.5 pl-3 text-right whitespace-nowrap font-mono text-atlas-text-secondary">
                      {iFlow > 0 ? (
                        <span className="text-blue-400">+{formatCurrency(iFlow, baseCurrency)}</span>
                      ) : iFlow < 0 ? (
                        <span className="text-emerald-400">{formatCurrency(iFlow, baseCurrency)}</span>
                      ) : (
                        <span className="text-atlas-text-tertiary">0.00</span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

