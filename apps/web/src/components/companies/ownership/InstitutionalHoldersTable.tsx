"use client";

import React, { useState } from "react";
import { InstitutionalHoldingDTO } from "@/lib/companies/ownership";
import {
  Search,
  ExternalLink,
  TrendingUp,
  TrendingDown,
  Minus,
  Sparkles,
  Info,
  Building,
  ShieldCheck,
} from "lucide-react";

interface InstitutionalHoldersTableProps {
  items: InstitutionalHoldingDTO[];
  reportingPeriod: string;
}

export const InstitutionalHoldersTable: React.FC<InstitutionalHoldersTableProps> = ({
  items,
  reportingPeriod,
}) => {
  const [filterText, setFilterText] = useState("");

  const filtered = items.filter((item) =>
    item.position.holder.name.toLowerCase().includes(filterText.toLowerCase())
  );

  return (
    <div className="space-y-3">
      {/* Search & Meta Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="relative w-full max-w-xs">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Filter institutional managers..."
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-md bg-muted/40 border border-border/60 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="font-mono text-[11px] bg-muted/50 px-2 py-0.5 rounded border border-border/40">
            {filtered.length} Disclosed Managers
          </span>
          <span className="font-mono text-[11px] text-amber-500/90">
            Period: {reportingPeriod} (45-Day Regulatory Lag)
          </span>
        </div>
      </div>

      {/* Institutional Table */}
      <div className="overflow-x-auto rounded-lg border border-border/60 bg-card/40">
        <table className="w-full text-left text-xs">
          <thead className="bg-muted/50 border-b border-border/60 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            <tr>
              <th className="py-2.5 px-3 w-12 text-center">Rank</th>
              <th className="py-2.5 px-3">Institutional Holder</th>
              <th className="py-2.5 px-3">Ownership Nature</th>
              <th className="py-2.5 px-3 text-right">Shares Held</th>
              <th className="py-2.5 px-3 text-right">% of Class</th>
              <th className="py-2.5 px-3 text-right">Q/Q Change</th>
              <th className="py-2.5 px-3 text-right">Indicative Value</th>
              <th className="py-2.5 px-3 text-right">Filed</th>
              <th className="py-2.5 px-3 text-center">Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-8 text-center text-muted-foreground">
                  No institutional holdings match the filter.
                </td>
              </tr>
            ) : (
              filtered.map((item, idx) => {
                const pos = item.position;
                const changeStatus = item.status;
                const sharesDiff = item.shares_change_prior_quarter || 0;

                return (
                  <tr key={pos.position_id} className="hover:bg-muted/20 transition-colors">
                    <td className="py-2.5 px-3 text-center font-mono text-[11px] text-muted-foreground">
                      {idx + 1}
                    </td>

                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-foreground flex items-center gap-1.5">
                        <Building className="h-3 w-3 text-primary/70 shrink-0" />
                        <span className="truncate max-w-[220px]" title={pos.holder.name}>
                          {pos.holder.name}
                        </span>
                      </div>
                      <div className="text-[10px] text-muted-foreground font-mono mt-0.5">
                        {pos.holder.country || "United States"} • LEI / CIK Qualified
                      </div>
                    </td>

                    <td className="py-2.5 px-3">
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-muted/60 text-muted-foreground border border-border/40 font-mono">
                        {pos.ownership_form.replace(/_/g, " ")}
                      </span>
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono font-medium text-foreground">
                      {pos.formatted_shares}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono font-semibold text-primary">
                      {pos.formatted_percentage || "N/A"}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono">
                      {changeStatus === "NEW_HOLDING" ? (
                        <span className="inline-flex items-center gap-0.5 text-emerald-500 font-semibold text-[11px]">
                          <Sparkles className="h-3 w-3" />
                          New
                        </span>
                      ) : sharesDiff > 0 ? (
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

                    <td className="py-2.5 px-3 text-right font-mono text-muted-foreground">
                      {pos.formatted_market_value || "—"}
                    </td>

                    <td className="py-2.5 px-3 text-right font-mono text-[11px] text-muted-foreground">
                      <div>{pos.filing_date}</div>
                      <div className="text-[9px] text-amber-500/80">+{pos.filing_delay_days}d lag</div>
                    </td>

                    <td className="py-2.5 px-3 text-center">
                      <span
                        className="inline-flex items-center gap-1 font-mono text-[10px] text-primary/80 hover:text-primary cursor-pointer"
                        title={`Source Document ID: ${pos.source_document_id || "SEC-13F"}`}
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

      {/* Critical Regulatory Disclaimer */}
      <div className="flex items-start gap-2 p-3 rounded-lg border border-border/40 bg-muted/20 text-[11px] text-muted-foreground">
        <Info className="h-4 w-4 text-sky-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-foreground">SEC Form 13F Scope Qualification: </span>
          Institutional investment managers exercising investment discretion over $100M+ in Section 13(f) securities report long equity holdings on a 45-day post-quarter lag. Form 13F does not reflect beneficial economic ownership, short positions, total fund holdings, or foreign-listed securities.
        </div>
      </div>
    </div>
  );
};
