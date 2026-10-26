"use client";

import React, { useState } from "react";
import { InsiderHoldingDTO } from "@/lib/companies/ownership";
import {
  Search,
  ExternalLink,
  UserCheck,
  TrendingUp,
  TrendingDown,
  Minus,
  Info,
  ShieldAlert,
  Award,
} from "lucide-react";

interface InsiderHoldingsTableProps {
  items: InsiderHoldingDTO[];
  reportingPeriod: string;
}

export const InsiderHoldingsTable: React.FC<InsiderHoldingsTableProps> = ({
  items,
  reportingPeriod,
}) => {
  const [filterText, setFilterText] = useState("");
  const [roleFilter, setRoleFilter] = useState<"ALL" | "OFFICERS" | "DIRECTORS">("ALL");

  const filtered = items.filter((item) => {
    const pos = item.position;
    const matchesText =
      pos.holder.name.toLowerCase().includes(filterText.toLowerCase()) ||
      (pos.insider_role && pos.insider_role.toLowerCase().includes(filterText.toLowerCase()));

    if (!matchesText) return false;

    if (roleFilter === "OFFICERS") return item.is_officer;
    if (roleFilter === "DIRECTORS") return item.is_director;
    return true;
  });

  return (
    <div className="space-y-3">
      {/* Search & Meta Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="flex items-center gap-2 w-full max-w-md">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search corporate insiders by name or executive title..."
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-md bg-muted/40 border border-border/60 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <div className="flex items-center rounded-md bg-muted/40 p-0.5 border border-border/60 text-[11px]">
            <button
              onClick={() => setRoleFilter("ALL")}
              className={`px-2 py-1 rounded font-medium transition-colors ${
                roleFilter === "ALL" ? "bg-card text-foreground shadow-xs font-semibold" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setRoleFilter("OFFICERS")}
              className={`px-2 py-1 rounded font-medium transition-colors ${
                roleFilter === "OFFICERS" ? "bg-card text-foreground shadow-xs font-semibold" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Officers
            </button>
            <button
              onClick={() => setRoleFilter("DIRECTORS")}
              className={`px-2 py-1 rounded font-medium transition-colors ${
                roleFilter === "DIRECTORS" ? "bg-card text-foreground shadow-xs font-semibold" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Directors
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
          <span className="text-[11px] bg-muted/50 px-2 py-0.5 rounded border border-border/40">
            {filtered.length} Disclosed Insiders
          </span>
          <span className="text-[11px] text-emerald-500/90">SEC Section 16(a) Compliant</span>
        </div>
      </div>

      {/* Insider Table */}
      <div className="overflow-x-auto rounded-lg border border-border/60 bg-card/40">
        <table className="w-full text-left text-xs">
          <thead className="bg-muted/50 border-b border-border/60 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            <tr>
              <th className="py-2.5 px-3">Reporting Insider</th>
              <th className="py-2.5 px-3">Corporate Role</th>
              <th className="py-2.5 px-3">Governance</th>
              <th className="py-2.5 px-3">Nature</th>
              <th className="py-2.5 px-3 text-right">Shares Held</th>
              <th className="py-2.5 px-3 text-right">% Stake</th>
              <th className="py-2.5 px-3 text-right">Last Change</th>
              <th className="py-2.5 px-3 text-right">Filing Date</th>
              <th className="py-2.5 px-3 text-center">Filing Reference</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-8 text-center text-muted-foreground">
                  No insider disclosures match the filter criteria.
                </td>
              </tr>
            ) : (
              filtered.map((item) => {
                const pos = item.position;
                const sharesDiff = item.shares_change_prior_filing || 0;

                return (
                  <tr key={pos.position_id} className="hover:bg-muted/20 transition-colors">
                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-foreground flex items-center gap-1.5">
                        <UserCheck className="h-3 w-3 text-emerald-500 shrink-0" />
                        <span className="truncate max-w-[200px]" title={pos.holder.name}>
                          {pos.holder.name}
                        </span>
                      </div>
                      <div className="text-[10px] text-muted-foreground font-mono mt-0.5">
                        {pos.holder.country || "United States"} • Individual Insider
                      </div>
                    </td>

                    <td className="py-2.5 px-3 font-medium text-foreground">
                      {pos.insider_role || "Key Executive"}
                    </td>

                    <td className="py-2.5 px-3">
                      <div className="flex items-center gap-1">
                        {item.is_officer && (
                          <span className="inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono">
                            Officer
                          </span>
                        )}
                        {item.is_director && (
                          <span className="inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono">
                            Director
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="py-2.5 px-3 font-mono text-[11px] text-muted-foreground">
                      {pos.ownership_form}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono font-medium text-foreground">
                      {pos.formatted_shares}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono font-semibold text-primary">
                      {pos.formatted_percentage || "<0.01%"}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono">
                      {sharesDiff > 0 ? (
                        <span className="inline-flex items-center gap-0.5 text-emerald-500 font-semibold text-[11px]">
                          <TrendingUp className="h-3 w-3" />
                          +{item.formatted_shares_change}
                        </span>
                      ) : sharesDiff < 0 ? (
                        <span className="inline-flex items-center gap-0.5 text-rose-500 font-semibold text-[11px]">
                          <TrendingDown className="h-3 w-3" />
                          {item.formatted_shares_change}
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-0.5 text-muted-foreground text-[11px]">
                          <Minus className="h-3 w-3" />
                          Unchanged
                        </span>
                      )}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono text-[11px] text-muted-foreground">
                      <div>{pos.filing_date}</div>
                      <div className="text-[9px] text-emerald-500/80">+{pos.filing_delay_days}d lag</div>
                    </td>

                    <td className="py-2.5 px-3 text-center">
                      <span
                        className="inline-flex items-center gap-1 font-mono text-[10px] text-primary/80 hover:text-primary cursor-pointer"
                        title={`Source Document ID: ${pos.source_document_id || "SEC-Form4"}`}
                      >
                        {pos.disclosure_type}
                        <ExternalLink className="h-2.5 w-2.5" />
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Notice on Form 4 vs Total Holdings */}
      <div className="flex items-start gap-2 p-3 rounded-lg border border-border/40 bg-muted/20 text-[11px] text-muted-foreground">
        <Info className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-foreground">SEC Section 16 Insider Integrity: </span>
          SEC Form 4 transactions report changes in beneficial ownership within 2 business days of execution. Position counts reflect post-transaction direct and indirect beneficial ownership certified by the reporting person. They do not constitute investment advice or trading signals.
        </div>
      </div>
    </div>
  );
};
