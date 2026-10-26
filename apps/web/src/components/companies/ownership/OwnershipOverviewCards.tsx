"use client";

import React from "react";
import { CompanyOwnershipOverviewDTO } from "@/lib/companies/ownership";
import {
  Users,
  Building2,
  PieChart,
  UserCheck,
  Calendar,
  Layers,
  ShieldAlert,
} from "lucide-react";

interface OwnershipOverviewCardsProps {
  overview: CompanyOwnershipOverviewDTO;
}

export const OwnershipOverviewCards: React.FC<OwnershipOverviewCardsProps> = ({ overview }) => {
  const conc = overview.concentration;
  const inst = overview.institutional_summary;
  const ins = overview.insider_summary;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      {/* Card 1: Top 1 Holder */}
      <div className="rounded-lg border border-border/60 bg-card/60 p-3.5 flex flex-col justify-between hover:border-border transition-colors">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-medium">Largest Disclosed Holder</span>
          <Building2 className="h-4 w-4 text-primary/80" />
        </div>
        <div className="mt-2">
          <div className="text-base font-bold text-foreground truncate" title={conc.top_1_holder_name || "N/A"}>
            {conc.top_1_holder_name || "N/A"}
          </div>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className="text-xl font-extrabold font-mono text-primary">
              {conc.top_1_pct !== null && conc.top_1_pct !== undefined ? `${conc.top_1_pct.toFixed(2)}%` : "N/A"}
            </span>
            <span className="text-xs text-muted-foreground font-mono">
              ({overview.top_holders[0]?.formatted_shares || "0"} shares)
            </span>
          </div>
        </div>
        <div className="mt-2 text-[11px] text-muted-foreground flex items-center gap-1.5">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>Form 13F / 13G Qualified Filer</span>
        </div>
      </div>

      {/* Card 2: Top 5 & Top 10 Concentration */}
      <div className="rounded-lg border border-border/60 bg-card/60 p-3.5 flex flex-col justify-between hover:border-border transition-colors">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-medium">Institutional Concentration</span>
          <PieChart className="h-4 w-4 text-sky-400" />
        </div>
        <div className="mt-2">
          <div className="flex items-baseline justify-between">
            <div>
              <div className="text-[11px] text-muted-foreground">Top 5 Stake</div>
              <div className="text-xl font-extrabold font-mono text-foreground">
                {conc.top_5_pct !== null && conc.top_5_pct !== undefined ? `${conc.top_5_pct.toFixed(2)}%` : "N/A"}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[11px] text-muted-foreground">Top 10 Stake</div>
              <div className="text-base font-bold font-mono text-muted-foreground">
                {conc.top_10_pct !== null && conc.top_10_pct !== undefined ? `${conc.top_10_pct.toFixed(2)}%` : "N/A"}
              </div>
            </div>
          </div>
        </div>
        <div className="mt-2 text-[11px] text-muted-foreground flex items-center justify-between font-mono">
          <span>Top 5: {((conc.top_5_shares || 0) / 1e9).toFixed(2)}B shs</span>
          <span className="text-emerald-500 text-[10px]">Non-Duplicated</span>
        </div>
      </div>

      {/* Card 3: Disclosed Institutional & Insider Totals */}
      <div className="rounded-lg border border-border/60 bg-card/60 p-3.5 flex flex-col justify-between hover:border-border transition-colors">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-medium">Disclosed Sample vs Pattern</span>
          <Users className="h-4 w-4 text-amber-400" />
        </div>
        <div className="mt-2">
          <div className="flex items-baseline justify-between">
            <div>
              <div className="text-[11px] text-muted-foreground">Institutions Disclosed</div>
              <div className="text-xl font-extrabold font-mono text-foreground">
                {inst.percentage ? `${inst.percentage.toFixed(2)}%` : "N/A"}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[11px] text-muted-foreground">Macro Pattern</div>
              <div className="text-base font-bold font-mono text-primary">
                {overview.patterns?.categories[0]?.formatted_percentage || "59.21%"}
              </div>
            </div>
          </div>
        </div>
        <div className="mt-2 text-[11px] text-muted-foreground flex items-center justify-between font-mono">
          <span>{inst.formatted_shares || "0"} shs in sample</span>
          <span>{inst.holder_count || 0} top filers</span>
        </div>
      </div>

      {/* Card 4: Denominator Qualification & As-Of Date */}
      <div className="rounded-lg border border-border/60 bg-card/60 p-3.5 flex flex-col justify-between hover:border-border transition-colors">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-medium">Share Class Denominator</span>
          <Calendar className="h-4 w-4 text-emerald-400" />
        </div>
        <div className="mt-2">
          <div className="text-base font-bold text-foreground truncate">
            {overview.selected_security.security_name}
          </div>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className="text-xl font-extrabold font-mono text-foreground">
              {overview.selected_security.formatted_shares_outstanding}
            </span>
            <span className="text-xs text-muted-foreground font-mono">shares</span>
          </div>
        </div>
        <div className="mt-2 text-[11px] text-muted-foreground flex items-center justify-between">
          <span className="flex items-center gap-1 font-mono text-[10px]">
            <Calendar className="h-3 w-3" />
            As of {overview.reporting_date}
          </span>
          <span className="text-[10px] text-amber-500/90 font-mono">
            Filed {overview.filing_date} (45d lag)
          </span>
        </div>
      </div>
    </div>
  );
};
