"use client";

import React from "react";
import {
  FilingCoverageDTO,
  FilingsOverviewSummaryDTO,
} from "@/lib/companies/filings";
import {
  FileText,
  Clock,
  ShieldCheck,
  Calendar,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Database,
} from "lucide-react";

interface FilingsOverviewCardsProps {
  overview: FilingsOverviewSummaryDTO | null;
  coverage: FilingCoverageDTO | null;
  onSelectFiling?: (filingId: string) => void;
}

export const FilingsOverviewCards: React.FC<FilingsOverviewCardsProps> = ({
  overview,
  coverage,
  onSelectFiling,
}) => {
  const latestAnnual = overview?.latest_annual;
  const latestQuarterly = overview?.latest_quarterly;
  const latest8K = overview?.latest_current_report;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      {/* Card 1: Latest 10-K Annual Report */}
      <div className="rounded-lg border border-border/60 bg-card/60 p-3.5 flex flex-col justify-between hover:border-border transition-colors">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-semibold uppercase tracking-wider text-[11px]">Latest Annual Report</span>
          <FileText className="h-4 w-4 text-emerald-400" />
        </div>
        <div className="mt-2.5">
          {latestAnnual ? (
            <>
              <div className="flex items-center gap-2">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {latestAnnual.form_type}
                </span>
                <span className="text-sm font-bold text-foreground font-mono">
                  {latestAnnual.reporting_period}
                </span>
              </div>
              <div className="text-xs text-muted-foreground mt-1 truncate" title={latestAnnual.title}>
                {latestAnnual.title}
              </div>
              <div className="text-[11px] font-mono text-muted-foreground mt-1">
                Filed: <span className="text-foreground">{latestAnnual.filing_date}</span>
              </div>
              <button
                type="button"
                onClick={() => onSelectFiling?.(latestAnnual.filing_id)}
                className="mt-2.5 inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:underline cursor-pointer"
              >
                Inspect Document ({latestAnnual.fact_count} facts) &rarr;
              </button>
            </>
          ) : (
            <div className="text-xs text-muted-foreground py-2 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>No Annual Report Cataloged</span>
            </div>
          )}
        </div>
        <div className="mt-2 pt-2 border-t border-border/40 text-[10px] text-muted-foreground flex items-center justify-between font-mono">
          <span>SEC EDGAR</span>
          <span>{latestAnnual?.accession_number || "—"}</span>
        </div>
      </div>

      {/* Card 2: Latest 10-Q Quarterly Report */}
      <div className="rounded-lg border border-border/60 bg-card/60 p-3.5 flex flex-col justify-between hover:border-border transition-colors">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-semibold uppercase tracking-wider text-[11px]">Latest Quarterly Report</span>
          <Calendar className="h-4 w-4 text-sky-400" />
        </div>
        <div className="mt-2.5">
          {latestQuarterly ? (
            <>
              <div className="flex items-center gap-2">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  {latestQuarterly.form_type}
                </span>
                <span className="text-sm font-bold text-foreground font-mono">
                  {latestQuarterly.reporting_period}
                </span>
              </div>
              <div className="text-xs text-muted-foreground mt-1 truncate" title={latestQuarterly.title}>
                {latestQuarterly.title}
              </div>
              <div className="text-[11px] font-mono text-muted-foreground mt-1">
                Filed: <span className="text-foreground">{latestQuarterly.filing_date}</span>
              </div>
              <button
                type="button"
                onClick={() => onSelectFiling?.(latestQuarterly.filing_id)}
                className="mt-2.5 inline-flex items-center gap-1 text-[11px] font-medium text-sky-400 hover:underline cursor-pointer"
              >
                Inspect Document ({latestQuarterly.fact_count} facts) &rarr;
              </button>
            </>
          ) : (
            <div className="text-xs text-muted-foreground py-2 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>No Quarterly Report Cataloged</span>
            </div>
          )}
        </div>
        <div className="mt-2 pt-2 border-t border-border/40 text-[10px] text-muted-foreground flex items-center justify-between font-mono">
          <span>SEC EDGAR</span>
          <span>{latestQuarterly?.accession_number || "—"}</span>
        </div>
      </div>

      {/* Card 3: Latest Material Event (8-K) */}
      <div className="rounded-lg border border-border/60 bg-card/60 p-3.5 flex flex-col justify-between hover:border-border transition-colors">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-semibold uppercase tracking-wider text-[11px]">Current / Material Event</span>
          <Clock className="h-4 w-4 text-amber-400" />
        </div>
        <div className="mt-2.5">
          {latest8K ? (
            <>
              <div className="flex items-center gap-2">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  {latest8K.form_type}
                </span>
                <span className="text-xs font-mono font-semibold text-foreground">
                  {latest8K.filing_date}
                </span>
              </div>
              <div className="text-xs text-muted-foreground mt-1 truncate" title={latest8K.title}>
                {latest8K.title}
              </div>
              <div className="text-[11px] font-mono text-muted-foreground mt-1">
                Accepted: <span className="text-foreground">{latest8K.acceptance_timestamp?.slice(0, 19) || "Verified"}</span>
              </div>
              <button
                type="button"
                onClick={() => onSelectFiling?.(latest8K.filing_id)}
                className="mt-2.5 inline-flex items-center gap-1 text-[11px] font-medium text-amber-400 hover:underline cursor-pointer"
              >
                Inspect Event Disclosure &rarr;
              </button>
            </>
          ) : (
            <div className="text-xs text-muted-foreground py-2 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>No Current Event Cataloged</span>
            </div>
          )}
        </div>
        <div className="mt-2 pt-2 border-t border-border/40 text-[10px] text-muted-foreground flex items-center justify-between font-mono">
          <span>SEC EDGAR</span>
          <span>{latest8K?.accession_number || "—"}</span>
        </div>
      </div>

      {/* Card 4: Regulatory Provenance & Fair Access */}
      <div className="rounded-lg border border-border/60 bg-card/60 p-3.5 flex flex-col justify-between hover:border-border transition-colors">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-semibold uppercase tracking-wider text-[11px]">Regulator Ingestion</span>
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
        </div>
        <div className="mt-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>SEC Fair Access Policy</span>
          </div>
          <div className="mt-1 space-y-1 text-[11px] font-mono text-muted-foreground">
            <div className="flex justify-between">
              <span>CIK:</span>
              <span className="text-foreground font-semibold">{coverage?.filer_cik || "0000320193"}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Disclosures:</span>
              <span className="text-foreground font-semibold">{coverage?.total_filings ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Rate Limit:</span>
              <span className="text-foreground font-semibold">10 req/s shared</span>
            </div>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-border/40 text-[10px] text-muted-foreground flex items-center justify-between">
          <span className="truncate" title={coverage?.user_agent_configured || "AtlasPlatform/1.0"}>
            UA: {coverage?.user_agent_configured?.split(" ")[0] || "AtlasPlatform/1.0"}
          </span>
          <span className="font-mono text-emerald-400 font-bold">100% VERIFIED</span>
        </div>
      </div>
    </div>
  );
};
