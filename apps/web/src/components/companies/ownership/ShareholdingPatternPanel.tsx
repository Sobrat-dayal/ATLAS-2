"use client";

import React from "react";
import { ShareholdingPatternDTO } from "@/lib/companies/ownership";
import {
  PieChart,
  Shield,
  Layers,
  Users,
  Info,
  CheckCircle2,
} from "lucide-react";

interface ShareholdingPatternPanelProps {
  patterns: ShareholdingPatternDTO | null;
}

export const ShareholdingPatternPanel: React.FC<ShareholdingPatternPanelProps> = ({ patterns }) => {
  if (!patterns || patterns.categories.length === 0) {
    return (
      <div className="p-8 text-center border border-border/60 rounded-lg bg-card/40 text-muted-foreground text-xs">
        No formal shareholding pattern categorization available for this reporting period.
      </div>
    );
  }

  const colors = ["bg-primary", "bg-amber-500", "bg-sky-500", "bg-purple-500", "bg-emerald-500"];

  return (
    <div className="space-y-4">
      {/* Header / Intro */}
      <div className="flex items-center justify-between border-b border-border/50 pb-2">
        <div className="flex items-center gap-2">
          <PieChart className="h-4 w-4 text-primary" />
          <span className="font-semibold text-xs text-foreground">
            Macro Shareholding Distribution (As of {patterns.reporting_date})
          </span>
        </div>
        <span className="text-[11px] font-mono text-muted-foreground">
          Period: {patterns.reporting_period}
        </span>
      </div>

      {/* Visual Stacked Progress Bar */}
      <div className="space-y-1.5">
        <div className="h-4 w-full flex rounded-md overflow-hidden bg-muted/40 border border-border/60">
          {patterns.categories.map((cat, idx) => (
            <div
              key={cat.category_name}
              style={{ width: `${cat.percentage_of_total}%` }}
              className={`${colors[idx % colors.length]} transition-all`}
              title={`${cat.category_name}: ${cat.formatted_percentage}`}
            />
          ))}
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-4 text-xs pt-1">
          {patterns.categories.map((cat, idx) => (
            <div key={cat.category_name} className="flex items-center gap-1.5 font-mono text-[11px]">
              <span className={`inline-block w-2.5 h-2.5 rounded-xs ${colors[idx % colors.length]}`} />
              <span className="text-muted-foreground">{cat.category_name}:</span>
              <span className="font-bold text-foreground">{cat.formatted_percentage}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Category Breakdown Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
        {patterns.categories.map((cat) => (
          <div
            key={cat.category_name}
            className="rounded-lg border border-border/60 bg-card/60 p-4 flex flex-col justify-between"
          >
            <div>
              <div className="text-xs font-semibold text-foreground">{cat.category_name}</div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold font-mono text-primary">
                  {cat.formatted_percentage}
                </span>
                <span className="text-xs text-muted-foreground font-mono">
                  ({cat.formatted_shares} shs)
                </span>
              </div>
            </div>

            <div className="mt-3 pt-2.5 border-t border-border/40 space-y-1 text-[11px] text-muted-foreground font-mono">
              <div className="flex justify-between">
                <span>Holders:</span>
                <span className="text-foreground font-medium">
                  {cat.shareholder_count ? cat.shareholder_count.toLocaleString() : "Aggregate Float"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Pledged / Encumbered:</span>
                <span className="text-emerald-500 font-semibold">
                  {cat.pledged_percentage !== null && cat.pledged_percentage !== undefined
                    ? `${cat.pledged_percentage.toFixed(2)}%`
                    : "0.00% (Unencumbered)"}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Jurisdiction Notes */}
      <div className="p-3 rounded-lg border border-border/40 bg-muted/20 text-xs text-muted-foreground space-y-1">
        <div className="font-semibold text-foreground flex items-center gap-1.5">
          <Info className="h-3.5 w-3.5 text-primary" />
          <span>Cross-Jurisdiction Taxonomy Handling</span>
        </div>
        <p className="text-[11px]">
          Shareholding patterns vary strictly by regulatory regime. Indian SEBI filings require distinct promoter vs public promoter-group classifications and encumbrance tracking. US disclosures group shares by Form 13F institutions, Section 16 corporate insiders, and free public float. ATLAS preserves native jurisdiction taxonomy without artificial forced mappings.
        </p>
      </div>
    </div>
  );
};
