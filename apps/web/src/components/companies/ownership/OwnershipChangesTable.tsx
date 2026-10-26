"use client";

import React, { useState } from "react";
import { OwnershipChangeDTO, PositionChangeStatus } from "@/lib/companies/ownership";
import {
  Search,
  TrendingUp,
  TrendingDown,
  Minus,
  Sparkles,
  UserX,
  Info,
  Building,
  CheckCircle2,
} from "lucide-react";

interface OwnershipChangesTableProps {
  items: OwnershipChangeDTO[];
  currentPeriod: string;
  priorPeriod: string;
}

export const OwnershipChangesTable: React.FC<OwnershipChangesTableProps> = ({
  items,
  currentPeriod,
  priorPeriod,
}) => {
  const [filterText, setFilterText] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  const filtered = items.filter((item) => {
    const matchesName = item.holder.name.toLowerCase().includes(filterText.toLowerCase());
    if (!matchesName) return false;

    if (statusFilter !== "ALL" && item.status !== statusFilter) {
      return false;
    }
    return true;
  });

  return (
    <div className="space-y-3">
      {/* Filter and Period Indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="flex items-center gap-2 w-full max-w-md">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search position changes by holder..."
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-md bg-muted/40 border border-border/60 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs rounded-md bg-muted/40 border border-border/60 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="ALL">All Changes</option>
            <option value="INCREASED">Increased</option>
            <option value="DECREASED">Decreased</option>
            <option value="NEW_HOLDING">Newly Disclosed</option>
            <option value="EXITED">Exited</option>
            <option value="UNCHANGED">Unchanged</option>
          </select>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
          <span className="text-[11px] bg-muted/50 px-2 py-0.5 rounded border border-border/40">
            Comparing {currentPeriod} vs {priorPeriod}
          </span>
          <span className="text-[11px] text-primary">{filtered.length} Disclosed Adjustments</span>
        </div>
      </div>

      {/* Changes Table */}
      <div className="overflow-x-auto rounded-lg border border-border/60 bg-card/40">
        <table className="w-full text-left text-xs">
          <thead className="bg-muted/50 border-b border-border/60 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            <tr>
              <th className="py-2.5 px-3">Shareholder Entity</th>
              <th className="py-2.5 px-3">Category</th>
              <th className="py-2.5 px-3 text-right">Prior Shares</th>
              <th className="py-2.5 px-3 text-right">Current Shares</th>
              <th className="py-2.5 px-3 text-right">Net Shares Change</th>
              <th className="py-2.5 px-3 text-right">Position % Change</th>
              <th className="py-2.5 px-3 text-right">Stake Impact (pp)</th>
              <th className="py-2.5 px-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-muted-foreground">
                  No position changes match the selected filter.
                </td>
              </tr>
            ) : (
              filtered.map((item) => {
                const isPositive = item.shares_change > 0;
                const isNegative = item.shares_change < 0;

                return (
                  <tr key={item.holder.holder_entity_id} className="hover:bg-muted/20 transition-colors">
                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-foreground flex items-center gap-1.5">
                        <Building className="h-3 w-3 text-primary/70 shrink-0" />
                        <span className="truncate max-w-[220px]" title={item.holder.name}>
                          {item.holder.name}
                        </span>
                      </div>
                      <div className="text-[10px] text-muted-foreground font-mono mt-0.5">
                        {item.holder.country || "United States"}
                      </div>
                    </td>

                    <td className="py-2.5 px-3 font-mono text-[11px] text-muted-foreground">
                      {item.holder.category.replace(/_/g, " ")}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono text-muted-foreground">
                      {(item.prior_shares / 1e6).toFixed(2)}M
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono font-medium text-foreground">
                      {(item.current_shares / 1e6).toFixed(2)}M
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono font-semibold">
                      {isPositive ? (
                        <span className="text-emerald-500">+{item.formatted_shares_change}</span>
                      ) : isNegative ? (
                        <span className="text-rose-500">{item.formatted_shares_change}</span>
                      ) : (
                        <span className="text-muted-foreground">0</span>
                      )}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono font-semibold">
                      {item.status === "NEW_HOLDING" ? (
                        <span className="text-emerald-500 text-[11px]">New</span>
                      ) : isPositive ? (
                        <span className="text-emerald-500">+{item.formatted_pct_change}</span>
                      ) : isNegative ? (
                        <span className="text-rose-500">{item.formatted_pct_change}</span>
                      ) : (
                        <span className="text-muted-foreground">0.00%</span>
                      )}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono text-primary font-medium">
                      {item.formatted_pp_change ? `${item.formatted_pp_change} pp` : "0.00 pp"}
                    </td>

                    <td className="py-2.5 px-3 text-center">
                      {item.status === "INCREASED" && (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                          <TrendingUp className="h-3 w-3" />
                          Increased
                        </span>
                      )}
                      {item.status === "DECREASED" && (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 font-mono">
                          <TrendingDown className="h-3 w-3" />
                          Decreased
                        </span>
                      )}
                      {item.status === "NEW_HOLDING" && (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono">
                          <Sparkles className="h-3 w-3" />
                          New
                        </span>
                      )}
                      {item.status === "EXITED" && (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
                          <UserX className="h-3 w-3" />
                          Exited
                        </span>
                      )}
                      {item.status === "UNCHANGED" && (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-semibold bg-muted/60 text-muted-foreground border border-border/40 font-mono">
                          <Minus className="h-3 w-3" />
                          Unchanged
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Methodology Qualification */}
      <div className="flex items-start gap-2 p-3 rounded-lg border border-border/40 bg-muted/20 text-xs text-muted-foreground">
        <Info className="h-4 w-4 text-primary shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-foreground">Position Changes vs Trade Execution: </span>
          Quarterly changes reflect the net difference between end-of-period regulatory holdings. They do not represent intraday trades, transaction costs, trade timestamps, or intra-quarter position fluctuations.
        </div>
      </div>
    </div>
  );
};
