"use client";

import React from "react";
import {
  ExternalLink,
  ShieldCheck,
  Target,
  TrendingDown,
  TrendingUp,
  Minus,
  Quote,
  Layers,
  Banknote,
  Calendar,
  Building,
} from "lucide-react";
import {
  CentralBankOverviewDTO,
  PolicyCycleKind,
  PolicyDecisionKind,
} from "@/lib/economics/central-banks";

interface CentralBankOverviewPanelProps {
  overview: CentralBankOverviewDTO;
  onNavigateTab: (tab: any) => void;
}

export function CentralBankOverviewPanel({
  overview,
  onNavigateTab,
}: CentralBankOverviewPanelProps) {
  const { institution, framework, instruments, latest_decision, latest_balance_sheet, current_policy_cycle, active_forward_guidance, active_programs_count } = overview;

  // Primary instrument
  const primaryInstrument = instruments[0];

  const getCycleBadge = (cycle: PolicyCycleKind) => {
    switch (cycle) {
      case "EASING":
        return {
          label: "EASING CYCLE",
          color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
          icon: <TrendingDown className="w-3.5 h-3.5" />,
        };
      case "TIGHTENING":
        return {
          label: "TIGHTENING CYCLE",
          color: "bg-rose-500/10 text-rose-400 border-rose-500/20",
          icon: <TrendingUp className="w-3.5 h-3.5" />,
        };
      case "HOLDING":
        return {
          label: "HOLDING / PAUSE",
          color: "bg-blue-500/10 text-blue-400 border-blue-500/20",
          icon: <Minus className="w-3.5 h-3.5" />,
        };
      default:
        return {
          label: "TRANSITIONAL",
          color: "bg-amber-500/10 text-amber-400 border-amber-500/20",
          icon: <Minus className="w-3.5 h-3.5" />,
        };
    }
  };

  const cycleBadge = getCycleBadge(current_policy_cycle);

  return (
    <div className="space-y-6">
      {/* 1. Master Header Card */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-atlas-text-primary tracking-tight">
                {institution.canonical_name}
              </h2>
              <span className={`text-[11px] font-mono font-semibold px-2.5 py-0.5 rounded border flex items-center gap-1.5 ${cycleBadge.color}`}>
                {cycleBadge.icon}
                {cycleBadge.label}
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs text-atlas-text-muted mt-2 flex-wrap">
              <span className="flex items-center gap-1">
                <Building className="w-3.5 h-3.5 text-atlas-accent" />
                {institution.headquarters_city}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-atlas-text-muted" />
                Established {institution.established_year}
              </span>
              <span>•</span>
              <span className="font-mono text-atlas-text-primary">
                Committee: {institution.primary_policy_committee}
              </span>
              <span>•</span>
              <a
                href={institution.official_website_url}
                target="_blank"
                rel="noreferrer"
                className="text-atlas-accent hover:underline flex items-center gap-1 font-mono text-[11px]"
              >
                Official Site <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          {/* Current Rate Display */}
          {primaryInstrument && (
            <div className="bg-atlas-background border border-atlas-border-subtle rounded-lg px-4 py-3 min-w-[200px] text-right">
              <div className="text-[11px] font-mono text-atlas-text-muted uppercase tracking-wider">
                {primaryInstrument.name}
              </div>
              <div className="text-2xl font-bold font-mono text-atlas-text-primary mt-0.5">
                {primaryInstrument.representation === "TARGET_RANGE"
                  ? `${primaryInstrument.current_lower_bound?.toFixed(2)}% - ${primaryInstrument.current_upper_bound?.toFixed(2)}%`
                  : `${primaryInstrument.current_rate?.toFixed(2)}%`}
              </div>
              <div className="text-[10px] text-atlas-text-muted mt-0.5">
                Effective: {primaryInstrument.effective_date}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 2. Grid: Mandate & Framework vs Latest Decision */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Mandate & Framework */}
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-atlas-accent" />
                <h3 className="text-sm font-semibold text-atlas-text-primary">
                  Monetary Policy Mandate & Inflation Target
                </h3>
              </div>
              <span className="text-[10px] font-mono text-atlas-text-muted">
                {framework.target_horizon}
              </span>
            </div>

            <div className="mt-4 space-y-3">
              <div>
                <span className="text-xs font-semibold text-atlas-text-primary">
                  {framework.mandate_title}
                </span>
                <p className="text-xs text-atlas-text-muted mt-1 leading-relaxed">
                  {framework.mandate_summary}
                </p>
              </div>

              <div className="pt-2 border-t border-atlas-border-subtle/50 grid grid-cols-2 gap-3">
                <div className="bg-atlas-background p-2.5 rounded border border-atlas-border-subtle">
                  <span className="text-[10px] uppercase font-mono text-atlas-text-muted block">
                    Inflation Metric
                  </span>
                  <span className="text-xs font-medium text-atlas-text-primary mt-0.5 block">
                    {framework.inflation_target_metric}
                  </span>
                </div>
                <div className="bg-atlas-background p-2.5 rounded border border-atlas-border-subtle">
                  <span className="text-[10px] uppercase font-mono text-atlas-text-muted block">
                    Official Target
                  </span>
                  <span className="text-sm font-bold font-mono text-atlas-accent mt-0.5 block">
                    {framework.target_lower_bound_pct != null && framework.target_upper_bound_pct != null
                      ? `${framework.target_lower_bound_pct.toFixed(1)}% - ${framework.target_upper_bound_pct.toFixed(1)}%`
                      : framework.inflation_target_pct != null
                      ? `${framework.inflation_target_pct.toFixed(1)}%`
                      : "Multi-objective"}
                  </span>
                  {framework.target_tolerance_band && (
                    <span className="text-[10px] text-atlas-text-muted block mt-0.5">
                      {framework.target_tolerance_band}
                    </span>
                  )}
                </div>
              </div>

              <div className="text-[11px] text-atlas-text-muted italic pt-1">
                Strategy: {framework.operating_strategy}
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-atlas-border-subtle flex items-center justify-between text-xs">
            <span className="text-[10px] text-atlas-text-muted font-mono truncate max-w-[280px]">
              Source: {framework.source_citation}
            </span>
            <button
              onClick={() => onNavigateTab("rates")}
              className="text-atlas-accent hover:underline font-medium text-xs"
            >
              View Instruments →
            </button>
          </div>
        </div>

        {/* Latest Verified Policy Decision */}
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-semibold text-atlas-text-primary">
                  Latest Officially Verified Policy Decision
                </h3>
              </div>
              {latest_decision && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-atlas-surface-elevated text-atlas-text-muted border border-atlas-border-subtle">
                  {latest_decision.official_identifier}
                </span>
              )}
            </div>

            {latest_decision ? (
              <div className="mt-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-[11px] text-atlas-text-muted font-mono block">
                      Announced: {new Date(latest_decision.announced_at).toLocaleString()}
                    </span>
                    <span className="text-[11px] text-atlas-text-muted font-mono block mt-0.5">
                      Effective: {latest_decision.effective_at}
                    </span>
                  </div>

                  {latest_decision.rate_changes[0] && (
                    <div className="text-right">
                      <span
                        className={`text-sm font-mono font-bold px-2 py-1 rounded inline-block ${
                          (latest_decision.rate_changes[0].change_bps ?? 0) < 0
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : (latest_decision.rate_changes[0].change_bps ?? 0) > 0
                            ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                            : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                        }`}
                      >
                        {(latest_decision.rate_changes[0].change_bps ?? 0) > 0 ? "+" : ""}
                        {latest_decision.rate_changes[0].change_bps} bps
                      </span>
                    </div>
                  )}
                </div>

                <div className="bg-atlas-background p-3 rounded border border-atlas-border-subtle">
                  <span className="text-[10px] font-mono uppercase text-atlas-text-muted block">
                    Official Rationale
                  </span>
                  <p className="text-xs text-atlas-text-primary mt-1 leading-relaxed line-clamp-3">
                    "{latest_decision.policy_rationale}"
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-xs text-atlas-text-muted mt-4">
                No official decision records available.
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-atlas-border-subtle flex items-center justify-between text-xs">
            <span className="text-[10px] text-emerald-400 font-mono">
              Status: OFFICIALLY_CONFIRMED
            </span>
            <button
              onClick={() => onNavigateTab("decisions")}
              className="text-atlas-accent hover:underline font-medium text-xs"
            >
              Full Decision History →
            </button>
          </div>
        </div>
      </div>

      {/* 3. Forward Guidance Quote Box */}
      {active_forward_guidance && (
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Quote className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-atlas-text-primary">
                  Official Published Forward Guidance ({active_forward_guidance.guidance_kind})
                </span>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  {active_forward_guidance.status}
                </span>
              </div>
              <p className="text-xs text-atlas-text-primary italic mt-1.5 leading-relaxed bg-atlas-background p-3 rounded border border-atlas-border-subtle">
                "{active_forward_guidance.verbatim_excerpt}"
              </p>
              <div className="text-[10px] text-atlas-text-muted mt-1.5 flex items-center justify-between font-mono">
                <span>Conditions: {active_forward_guidance.explicit_conditions}</span>
                <span>Published: {new Date(active_forward_guidance.published_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4. Quick Key Balance Sheet & Program Figures */}
      {latest_balance_sheet && (
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
          <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
            <div className="flex items-center gap-2">
              <Banknote className="w-4 h-4 text-atlas-accent" />
              <h3 className="text-sm font-semibold text-atlas-text-primary">
                Balance Sheet & Liquidity Summary ({latest_balance_sheet.currency})
              </h3>
            </div>
            <span className="text-[10px] font-mono text-atlas-text-muted">
              As of {latest_balance_sheet.reference_date} ({latest_balance_sheet.reporting_frequency})
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4">
            <div className="bg-atlas-background p-3 rounded border border-atlas-border-subtle">
              <span className="text-[10px] font-mono text-atlas-text-muted uppercase block">
                Total Assets
              </span>
              <span className="text-base font-bold font-mono text-atlas-text-primary mt-1 block">
                {latest_balance_sheet.total_assets_billions.toLocaleString()} B
              </span>
            </div>
            <div className="bg-atlas-background p-3 rounded border border-atlas-border-subtle">
              <span className="text-[10px] font-mono text-atlas-text-muted uppercase block">
                Securities Holdings
              </span>
              <span className="text-base font-bold font-mono text-atlas-text-primary mt-1 block">
                {latest_balance_sheet.securities_holdings_billions.toLocaleString()} B
              </span>
            </div>
            <div className="bg-atlas-background p-3 rounded border border-atlas-border-subtle">
              <span className="text-[10px] font-mono text-atlas-text-muted uppercase block">
                Reserve Balances
              </span>
              <span className="text-base font-bold font-mono text-atlas-text-primary mt-1 block">
                {latest_balance_sheet.reserve_balances_billions.toLocaleString()} B
              </span>
            </div>
            <div className="bg-atlas-background p-3 rounded border border-atlas-border-subtle">
              <span className="text-[10px] font-mono text-atlas-text-muted uppercase block">
                Active Programs (QE/QT)
              </span>
              <span className="text-base font-bold font-mono text-atlas-accent mt-1 block">
                {active_programs_count} Programs
              </span>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-atlas-border-subtle flex items-center justify-between text-xs">
            <span className="text-[10px] text-atlas-text-muted font-mono">
              {latest_balance_sheet.accounting_notes}
            </span>
            <button
              onClick={() => onNavigateTab("balance-sheet")}
              className="text-atlas-accent hover:underline font-medium text-xs"
            >
              Full Balance Sheet & Runoff Details →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
