"use client";

import React from "react";
import {
  QuarterlyEarningsItemDTO,
  EarningsEventDTO,
  ConsensusSnapshotDTO,
  CompanyEarningsOverviewDTO,
} from "@/lib/companies/earnings/types";
import { Badge, Button } from "@/design-system";
import {
  Calendar,
  CheckCircle2,
  Clock,
  DollarSign,
  ExternalLink,
  HelpCircle,
  TrendingDown,
  TrendingUp,
  Zap,
} from "lucide-react";

export interface EarningsOverviewCardsProps {
  overview?: CompanyEarningsOverviewDTO | null;
  latestCompleted?: QuarterlyEarningsItemDTO | null;
  nextScheduled?: EarningsEventDTO | null;
  nextConsensus?: ConsensusSnapshotDTO | null;
}

export function EarningsOverviewCards({
  overview,
  latestCompleted,
  nextScheduled,
  nextConsensus,
}: EarningsOverviewCardsProps) {
  const latest = latestCompleted ?? overview?.latest_completed;
  const next = nextScheduled ?? overview?.next_scheduled;
  const consensus = nextConsensus ?? overview?.next_consensus;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* 1. Latest Reported Earnings Card */}
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4 space-y-3 shadow-xs">
        <div className="flex items-center justify-between pb-2 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-atlas-accent" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Latest Reported Results
            </h3>
            {latest && (
              <Badge variant="outline" className="font-mono text-[10px]">
                {latest.fiscal_period}
              </Badge>
            )}
          </div>

          {latest && (
            <Badge
              variant={
                latest.eps_classification === "BEAT"
                  ? "positive"
                  : latest.eps_classification === "MISS"
                  ? "negative"
                  : "default"
              }
              className="font-mono text-[10px] font-bold"
            >
              EPS {latest.eps_classification}
            </Badge>
          )}
        </div>

        {latest ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-[11px] text-atlas-text-muted font-mono">
              <span>Reported: {latest.announced_date || "—"}</span>
              <span className="uppercase">{latest.market_session.replace("_", " ")}</span>
            </div>

            {/* EPS & Revenue Comparison Grid */}
            <div className="grid grid-cols-2 gap-3 pt-1">
              {/* EPS Box */}
              <div className="bg-atlas-surface-2 border border-atlas-border-subtle rounded-xs p-2.5">
                <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
                  Diluted EPS (GAAP)
                </div>
                <div className="flex items-baseline justify-between mt-1">
                  <span className="text-base font-bold font-mono text-atlas-text-primary">
                    {latest.formatted_actual_eps}
                  </span>
                  <span className="text-[10px] font-mono text-atlas-text-muted">
                    Est: {latest.formatted_estimate_eps}
                  </span>
                </div>
                <div className="flex items-center gap-1 mt-1 text-[11px] font-mono">
                  {latest.eps_surprise_pct !== null && latest.eps_surprise_pct !== undefined && (
                    <span
                      className={`flex items-center font-bold ${
                        latest.eps_surprise_pct >= 0
                          ? "text-atlas-positive"
                          : "text-atlas-negative"
                      }`}
                    >
                      {latest.eps_surprise_pct >= 0 ? (
                        <TrendingUp className="w-3 h-3 mr-0.5" />
                      ) : (
                        <TrendingDown className="w-3 h-3 mr-0.5" />
                      )}
                      {latest.formatted_eps_surprise_pct}
                    </span>
                  )}
                  <span className="text-[10px] text-atlas-text-muted">surprise</span>
                </div>
              </div>

              {/* Revenue Box */}
              <div className="bg-atlas-surface-2 border border-atlas-border-subtle rounded-xs p-2.5">
                <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
                  Total Revenue
                </div>
                <div className="flex items-baseline justify-between mt-1">
                  <span className="text-base font-bold font-mono text-atlas-text-primary">
                    {latest.formatted_actual_revenue}
                  </span>
                  <span className="text-[10px] font-mono text-atlas-text-muted">
                    Est: {latest.formatted_estimate_revenue}
                  </span>
                </div>
                <div className="flex items-center gap-1 mt-1 text-[11px] font-mono">
                  {latest.revenue_surprise_pct !== null && latest.revenue_surprise_pct !== undefined && (
                    <span
                      className={`flex items-center font-bold ${
                        latest.revenue_surprise_pct >= 0
                          ? "text-atlas-positive"
                          : "text-atlas-negative"
                      }`}
                    >
                      {latest.revenue_surprise_pct >= 0 ? (
                        <TrendingUp className="w-3 h-3 mr-0.5" />
                      ) : (
                        <TrendingDown className="w-3 h-3 mr-0.5" />
                      )}
                      {latest.formatted_revenue_surprise_pct}
                    </span>
                  )}
                  <span className="text-[10px] text-atlas-text-muted">surprise</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="py-6 text-center text-atlas-text-muted text-xs font-mono">
            No completed earnings events on record for this company.
          </div>
        )}
      </div>

      {/* 2. Next Scheduled Earnings Announcement Card */}
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4 space-y-3 shadow-xs">
        <div className="flex items-center justify-between pb-2 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-atlas-accent" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Next Earnings Release
            </h3>
            {next && (
              <Badge variant="outline" className="font-mono text-[10px]">
                {next.fiscal_period}
              </Badge>
            )}
          </div>

          {next && (
            <Badge
              variant={next.is_confirmed ? "positive" : "outline"}
              className="font-mono text-[10px]"
            >
              {next.is_confirmed ? "CONFIRMED" : "ESTIMATED"}
            </Badge>
          )}
        </div>

        {next ? (
          <div className="space-y-3">
            <div className="flex flex-wrap items-center justify-between text-xs font-mono gap-2">
              <div className="flex items-center gap-1.5 text-atlas-text-primary font-bold text-sm">
                <Calendar className="w-4 h-4 text-atlas-text-muted" />
                <span>{next.announced_date || "Date Unconfirmed"}</span>
              </div>
              <div className="flex items-center gap-1 text-[11px] text-atlas-text-muted">
                <Clock className="w-3.5 h-3.5" />
                <span>
                  {next.announced_time || "4:30 PM"} {next.timezone} (
                  {next.market_session.replace("_", " ")})
                </span>
              </div>
            </div>

            {/* Next Consensus Expectations */}
            {consensus ? (
              <div className="grid grid-cols-2 gap-3 pt-1">
                <div className="bg-atlas-surface-2 border border-atlas-border-subtle rounded-xs p-2.5">
                  <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
                    Consensus EPS Estimate
                  </div>
                  <div className="text-base font-bold font-mono text-atlas-text-primary mt-1">
                    {consensus.formatted_eps}
                  </div>
                  <div className="text-[10px] text-atlas-text-muted font-mono mt-0.5">
                    Range: ${consensus.eps_low?.toFixed(2) || "—"} - ${consensus.eps_high?.toFixed(2) || "—"}
                  </div>
                </div>

                <div className="bg-atlas-surface-2 border border-atlas-border-subtle rounded-xs p-2.5">
                  <div className="text-[10px] text-atlas-text-muted uppercase font-mono">
                    Consensus Revenue Estimate
                  </div>
                  <div className="text-base font-bold font-mono text-atlas-text-primary mt-1">
                    {consensus.formatted_revenue}
                  </div>
                  <div className="text-[10px] text-atlas-text-muted font-mono mt-0.5">
                    Analyst Coverage: {consensus.analyst_count} firms
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-atlas-surface-2 border border-atlas-border-subtle rounded-xs p-3 text-center text-atlas-text-muted text-[11px] font-mono">
                Consensus estimates for {next.fiscal_period} are not yet published.
              </div>
            )}

            {/* Webcast Link */}
            {next.webcast_url && (
              <div className="pt-1 flex justify-end">
                <a
                  href={next.webcast_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[11px] text-atlas-accent hover:underline flex items-center gap-1 font-mono"
                >
                  <span>Official Investor Webcast</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}
          </div>
        ) : (
          <div className="py-6 text-center text-atlas-text-muted text-xs font-mono">
            Next earnings release date is currently unavailable.
          </div>
        )}
      </div>
    </div>
  );
}
