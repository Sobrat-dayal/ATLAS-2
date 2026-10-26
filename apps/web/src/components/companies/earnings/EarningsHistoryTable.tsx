"use client";

import React, { useState } from "react";
import {
  QuarterlyEarningsItem,
  SurpriseClassification,
} from "@/lib/companies/earnings/types";
import {
  Calendar,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Info,
  CheckCircle2,
} from "lucide-react";

interface EarningsHistoryTableProps {
  items: QuarterlyEarningsItem[];
  currency?: string;
  onSelectPeriod?: (periodId: string) => void;
}

export const EarningsHistoryTable: React.FC<EarningsHistoryTableProps> = ({
  items,
  currency = "USD",
  onSelectPeriod,
}) => {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const toggleRow = (fiscalPeriod: string) => {
    setExpandedRow((prev) => (prev === fiscalPeriod ? null : fiscalPeriod));
    if (onSelectPeriod) {
      onSelectPeriod(fiscalPeriod);
    }
  };

  const getClassificationBadge = (classification: SurpriseClassification) => {
    switch (classification) {
      case SurpriseClassification.BEAT:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 px-1.5 py-0.5 text-xs font-semibold text-emerald-500 border border-emerald-500/20">
            <ArrowUpRight className="h-3 w-3" />
            BEAT
          </span>
        );
      case SurpriseClassification.MISS:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-rose-500/10 px-1.5 py-0.5 text-xs font-semibold text-rose-500 border border-rose-500/20">
            <ArrowDownRight className="h-3 w-3" />
            MISS
          </span>
        );
      case SurpriseClassification.IN_LINE:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-amber-500/10 px-1.5 py-0.5 text-xs font-semibold text-amber-500 border border-amber-500/20">
            <Minus className="h-3 w-3" />
            IN-LINE
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-muted/30 px-1.5 py-0.5 text-xs font-medium text-muted-foreground border border-border/40">
            <HelpCircle className="h-3 w-3" />
            N/A
          </span>
        );
    }
  };

  if (!items || items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center border border-border/50 rounded-lg bg-card/40">
        <Calendar className="h-8 w-8 text-muted-foreground/40 mb-2" />
        <p className="text-sm font-medium text-foreground">No Historical Earnings Data</p>
        <p className="text-xs text-muted-foreground mt-1 max-w-sm">
          No historical quarterly financial results or consensus comparisons are registered for this company.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-foreground">
            Quarterly Results & Consensus History
          </h3>
          <p className="text-xs text-muted-foreground">
            Verified actual financial results compared against pre-announcement analyst consensus snapshots
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-emerald-500" /> Beat
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-rose-500" /> Miss
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-amber-500" /> In-Line
          </span>
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-border/60 bg-card/40">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-border/60 bg-muted/20 text-muted-foreground uppercase tracking-wider font-semibold">
              <th scope="col" className="px-3 py-2.5">Fiscal Period</th>
              <th scope="col" className="px-3 py-2.5">Announced Date</th>
              <th scope="col" className="px-3 py-2.5">Session</th>
              <th scope="col" className="px-3 py-2.5 text-right">Actual EPS</th>
              <th scope="col" className="px-3 py-2.5 text-right">Consensus EPS</th>
              <th scope="col" className="px-3 py-2.5 text-right">EPS Surprise</th>
              <th scope="col" className="px-3 py-2.5 text-right">Actual Revenue</th>
              <th scope="col" className="px-3 py-2.5 text-right">Consensus Rev</th>
              <th scope="col" className="px-3 py-2.5 text-right">Rev Surprise</th>
              <th scope="col" className="px-3 py-2.5 text-center">Result</th>
              <th scope="col" className="px-2 py-2.5 text-center w-8"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40 font-mono">
            {items.map((row) => {
              const isExpanded = expandedRow === row.fiscal_period;
              const hasEpsSurprise = row.eps_surprise_pct !== null && row.eps_surprise_pct !== undefined;
              const hasRevSurprise = row.revenue_surprise_pct !== null && row.revenue_surprise_pct !== undefined;

              return (
                <React.Fragment key={row.fiscal_period}>
                  <tr
                    onClick={() => toggleRow(row.fiscal_period)}
                    className="hover:bg-muted/30 cursor-pointer transition-colors duration-150"
                  >
                    {/* Fiscal Period */}
                    <td className="px-3 py-2.5 font-sans font-semibold text-foreground whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <span>{row.fiscal_period}</span>
                        {row.is_restated && (
                          <span className="rounded bg-amber-500/10 px-1 py-0.2 text-[10px] font-medium text-amber-500 border border-amber-500/20">
                            Restated
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Announced Date */}
                    <td className="px-3 py-2.5 text-muted-foreground whitespace-nowrap font-sans">
                      {row.announced_date || "—"}
                    </td>

                    {/* Market Session */}
                    <td className="px-3 py-2.5 whitespace-nowrap font-sans">
                      {row.market_session ? (
                        <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {row.market_session === "AFTER_MARKET"
                            ? "After Close"
                            : row.market_session === "BEFORE_MARKET"
                            ? "Before Open"
                            : row.market_session.replace("_", " ")}
                        </span>
                      ) : (
                        <span className="text-muted-foreground/60">—</span>
                      )}
                    </td>

                    {/* Actual EPS */}
                    <td className="px-3 py-2.5 text-right font-medium text-foreground whitespace-nowrap">
                      {row.formatted_actual_eps}
                    </td>

                    {/* Consensus EPS */}
                    <td className="px-3 py-2.5 text-right text-muted-foreground whitespace-nowrap">
                      {row.formatted_estimate_eps}
                    </td>

                    {/* EPS Surprise */}
                    <td className="px-3 py-2.5 text-right whitespace-nowrap">
                      {hasEpsSurprise ? (
                        <div className="flex flex-col items-end">
                          <span
                            className={`font-semibold ${
                              row.eps_classification === SurpriseClassification.BEAT
                                ? "text-emerald-500"
                                : row.eps_classification === SurpriseClassification.MISS
                                ? "text-rose-500"
                                : "text-foreground"
                            }`}
                          >
                            {row.formatted_eps_surprise_pct}
                          </span>
                          {row.eps_surprise_abs !== null && row.eps_surprise_abs !== undefined && (
                            <span className="text-[10px] text-muted-foreground">
                              {row.eps_surprise_abs >= 0 ? `+${row.eps_surprise_abs.toFixed(2)}` : row.eps_surprise_abs.toFixed(2)}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-muted-foreground/60">—</span>
                      )}
                    </td>

                    {/* Actual Revenue */}
                    <td className="px-3 py-2.5 text-right font-medium text-foreground whitespace-nowrap">
                      {row.formatted_actual_revenue}
                    </td>

                    {/* Consensus Revenue */}
                    <td className="px-3 py-2.5 text-right text-muted-foreground whitespace-nowrap">
                      {row.formatted_estimate_revenue}
                    </td>

                    {/* Revenue Surprise */}
                    <td className="px-3 py-2.5 text-right whitespace-nowrap">
                      {hasRevSurprise ? (
                        <div className="flex flex-col items-end">
                          <span
                            className={`font-semibold ${
                              row.revenue_classification === SurpriseClassification.BEAT
                                ? "text-emerald-500"
                                : row.revenue_classification === SurpriseClassification.MISS
                                ? "text-rose-500"
                                : "text-foreground"
                            }`}
                          >
                            {row.formatted_revenue_surprise_pct}
                          </span>
                        </div>
                      ) : (
                        <span className="text-muted-foreground/60">—</span>
                      )}
                    </td>

                    {/* Beat/Miss Classification Badge */}
                    <td className="px-3 py-2.5 text-center whitespace-nowrap font-sans">
                      {getClassificationBadge(row.eps_classification)}
                    </td>

                    {/* Expansion indicator */}
                    <td className="px-2 py-2.5 text-center text-muted-foreground">
                      {isExpanded ? (
                        <ChevronUp className="h-3.5 w-3.5 mx-auto" />
                      ) : (
                        <ChevronDown className="h-3.5 w-3.5 mx-auto" />
                      )}
                    </td>
                  </tr>

                  {/* Expanded Detail Inspector */}
                  {isExpanded && (
                    <tr className="bg-muted/10 border-b border-border/40 font-sans">
                      <td colSpan={11} className="px-4 py-3">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                          {/* Financial Fact Details */}
                          <div className="rounded border border-border/40 p-3 bg-card/60 space-y-1.5">
                            <div className="flex items-center gap-1.5 font-semibold text-foreground">
                              <CheckCircle2 className="h-3.5 w-3.5 text-primary" />
                              Reported Financial Results
                            </div>
                            <div className="text-muted-foreground space-y-1 mt-1 font-mono text-[11px]">
                              <div className="flex justify-between">
                                <span>Fiscal Period:</span>
                                <span className="text-foreground">{row.fiscal_period}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Fiscal Year:</span>
                                <span className="text-foreground">{row.fiscal_year}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Reporting Currency:</span>
                                <span className="text-foreground">{row.currency || currency}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Data Source:</span>
                                <span className="text-foreground">{row.source}</span>
                              </div>
                            </div>
                          </div>

                          {/* Consensus Methodology */}
                          <div className="rounded border border-border/40 p-3 bg-card/60 space-y-1.5">
                            <div className="flex items-center gap-1.5 font-semibold text-foreground">
                              <Info className="h-3.5 w-3.5 text-sky-500" />
                              Analyst Consensus Metadata
                            </div>
                            <div className="text-muted-foreground space-y-1 mt-1 font-mono text-[11px]">
                              <div className="flex justify-between">
                                <span>Methodology:</span>
                                <span className="text-foreground">Mean Consensus</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Pre-Release Cutoff:</span>
                                <span className="text-foreground">Strict (T-0 pre-mkt)</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Status:</span>
                                <span className="text-foreground">{row.status}</span>
                              </div>
                            </div>
                          </div>

                          {/* Surprise Methodology */}
                          <div className="rounded border border-border/40 p-3 bg-card/60 space-y-1.5">
                            <div className="flex items-center gap-1.5 font-semibold text-foreground">
                              <HelpCircle className="h-3.5 w-3.5 text-muted-foreground" />
                              Surprise Computation Policy
                            </div>
                            <div className="text-muted-foreground space-y-1 mt-1 text-[11px]">
                              <p>
                                <span className="font-semibold text-foreground">EPS Surprise:</span> (Actual - Estimate) / |Estimate| × 100
                              </p>
                              <p>
                                <span className="font-semibold text-foreground">Revenue Surprise:</span> (Actual - Estimate) / |Estimate| × 100
                              </p>
                              <p className="text-[10px] text-muted-foreground/80 pt-0.5">
                                Strict pre-release temporal matching enforced. No post-announcement revision leakage.
                              </p>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
