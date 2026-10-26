"use client";

import React from "react";
import {
  TrendingUp,
  Percent,
  Users,
  Landmark,
  FileText,
  DollarSign,
  Scale,
  Calendar,
  ShieldCheck,
  Building2,
} from "lucide-react";
import {
  CountryEconomicsOverviewDTO,
  CountryEconomicProfileDTO,
} from "@/lib/economics/countries";

interface CountryEconomicsOverviewProps {
  overview: CountryEconomicsOverviewDTO | null;
  profile: CountryEconomicProfileDTO | null;
  onNavigateCategory: (category: string) => void;
}

export function CountryEconomicsOverview({
  overview,
  profile,
  onNavigateCategory,
}: CountryEconomicsOverviewProps) {
  if (!overview || !profile) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded animate-pulse">
        Loading sovereign economic intelligence profile...
      </div>
    );
  }

  const formatPct = (val?: number | null) => {
    if (val === undefined || val === null) return "—";
    const sign = val > 0 ? "+" : "";
    return `${sign}${val.toFixed(1)}%`;
  };

  const formatCurrency = (val?: number | null, unit: string = "B") => {
    if (val === undefined || val === null) return "—";
    return `$${val.toLocaleString(undefined, { maximumFractionDigits: 1 })}${unit}`;
  };

  return (
    <div className="space-y-4">
      {/* Sovereign Context Header */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-md bg-atlas-accent/10 border border-atlas-accent/20 flex items-center justify-center font-mono font-bold text-base text-atlas-accent">
              {profile.iso_code}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-atlas-text-primary tracking-tight">
                  {profile.name}
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-atlas-background text-atlas-text-secondary border border-atlas-border-subtle">
                  {profile.scope_kind}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" />
                  <span>{overview.data_freshness_status}</span>
                </span>
              </div>
              <div className="text-xs text-atlas-text-muted mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
                <span>
                  <strong>Central Bank:</strong> {profile.central_bank_name}
                </span>
                <span>•</span>
                <span>
                  <strong>Statistical Authority:</strong> {profile.statistical_agency}
                </span>
                <span>•</span>
                <span>
                  <strong>Reporting Currency:</strong> {profile.currency_code}
                </span>
              </div>
            </div>
          </div>

          {/* Standards & Accounting Framework */}
          <div className="flex flex-wrap items-center gap-2 self-start md:self-auto text-[11px] font-mono text-atlas-text-secondary">
            <div className="px-2.5 py-1 rounded bg-atlas-background border border-atlas-border-subtle flex items-center gap-1.5">
              <FileText className="w-3 h-3 text-atlas-accent" />
              <span>{profile.national_accounts_standard}</span>
            </div>
            <div className="px-2.5 py-1 rounded bg-atlas-background border border-atlas-border-subtle flex items-center gap-1.5">
              <Calendar className="w-3 h-3 text-atlas-text-muted" />
              <span>{profile.fiscal_year_structure}</span>
            </div>
          </div>
        </div>

        {profile.notes && (
          <div className="mt-3 pt-3 border-t border-atlas-border-subtle text-[11px] text-atlas-text-muted">
            {profile.notes}
          </div>
        )}
      </div>

      {/* Headline Metric Grid (Independent Periods per Canonical Discipline) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Metric 1: Real GDP Growth */}
        <div
          onClick={() => onNavigateCategory("gdp")}
          className="p-3.5 bg-atlas-surface hover:bg-atlas-surface-elevated border border-atlas-border-subtle rounded cursor-pointer transition-all hover:border-atlas-accent/50"
        >
          <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
            <span className="flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-blue-400" />
              Real GDP Growth
            </span>
            <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle">
              {overview.headline_gdp_period || "—"}
            </span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-bold font-mono text-atlas-text-primary">
              {formatPct(overview.headline_real_gdp_growth_yoy)}
            </span>
            <span className="text-xs text-atlas-text-muted font-mono">YoY</span>
          </div>
          {overview.headline_real_gdp_growth_qoq !== undefined && overview.headline_real_gdp_growth_qoq !== null && (
            <div className="text-[11px] text-atlas-text-secondary mt-1 font-mono">
              QoQ Annualized: {formatPct(overview.headline_real_gdp_growth_qoq)}
            </div>
          )}
          <div className="text-[10px] text-atlas-text-muted mt-2 pt-2 border-t border-atlas-border-subtle flex justify-between">
            <span>Nominal GDP: {formatCurrency(overview.nominal_gdp_usd_billions)}</span>
            <span>Per Capita: ${overview.gdp_per_capita_usd?.toLocaleString() || "—"}</span>
          </div>
        </div>

        {/* Metric 2: CPI Inflation */}
        <div
          onClick={() => onNavigateCategory("inflation")}
          className="p-3.5 bg-atlas-surface hover:bg-atlas-surface-elevated border border-atlas-border-subtle rounded cursor-pointer transition-all hover:border-atlas-accent/50"
        >
          <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
            <span className="flex items-center gap-1.5">
              <Percent className="w-3.5 h-3.5 text-rose-400" />
              CPI Inflation
            </span>
            <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle">
              {overview.headline_cpi_period || "—"}
            </span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-bold font-mono text-atlas-text-primary">
              {formatPct(overview.headline_cpi_inflation_yoy)}
            </span>
            <span className="text-xs text-atlas-text-muted font-mono">Headline YoY</span>
          </div>
          <div className="text-[11px] text-atlas-text-secondary mt-1 font-mono">
            Core CPI YoY: {formatPct(overview.core_cpi_inflation_yoy)}
          </div>
          <div className="text-[10px] text-atlas-text-muted mt-2 pt-2 border-t border-atlas-border-subtle flex justify-between">
            <span>Target: 2.0%</span>
            <span>Policy Anchor</span>
          </div>
        </div>

        {/* Metric 3: Labor Market & Unemployment */}
        <div
          onClick={() => onNavigateCategory("labor")}
          className="p-3.5 bg-atlas-surface hover:bg-atlas-surface-elevated border border-atlas-border-subtle rounded cursor-pointer transition-all hover:border-atlas-accent/50"
        >
          <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
            <span className="flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-amber-400" />
              Unemployment Rate
            </span>
            <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle">
              {overview.unemployment_period || "—"}
            </span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-bold font-mono text-atlas-text-primary">
              {overview.unemployment_rate !== null && overview.unemployment_rate !== undefined
                ? `${overview.unemployment_rate.toFixed(1)}%`
                : "—"}
            </span>
            <span className="text-xs text-atlas-text-muted font-mono">% of Labor Force</span>
          </div>
          <div className="text-[11px] text-atlas-text-secondary mt-1 font-mono">
            Population: {overview.total_population_millions ? `${overview.total_population_millions.toFixed(1)}M` : "—"}
          </div>
          <div className="text-[10px] text-atlas-text-muted mt-2 pt-2 border-t border-atlas-border-subtle">
            <span>National Labor Force Survey Standards</span>
          </div>
        </div>

        {/* Metric 4: Monetary Policy Rate */}
        <div
          onClick={() => onNavigateCategory("monetary")}
          className="p-3.5 bg-atlas-surface hover:bg-atlas-surface-elevated border border-atlas-border-subtle rounded cursor-pointer transition-all hover:border-atlas-accent/50"
        >
          <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
            <span className="flex items-center gap-1.5">
              <Landmark className="w-3.5 h-3.5 text-emerald-400" />
              Central Bank Policy Rate
            </span>
            <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle">
              {overview.policy_rate_period || "—"}
            </span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-xl font-bold font-mono text-atlas-text-primary">
              {overview.policy_interest_rate !== null && overview.policy_interest_rate !== undefined
                ? `${overview.policy_interest_rate.toFixed(2)}%`
                : "—"}
            </span>
            <span className="text-xs text-atlas-text-muted font-mono">Effective / Upper Bound</span>
          </div>
          <div className="text-[11px] text-atlas-text-secondary mt-1 font-mono">
            {profile.central_bank_name.split("(")[0].trim()}
          </div>
          <div className="text-[10px] text-atlas-text-muted mt-2 pt-2 border-t border-atlas-border-subtle">
            <span>Sovereign Monetary Area</span>
          </div>
        </div>
      </div>

      {/* Secondary Structural Indicators Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Fiscal Position */}
        <div
          onClick={() => onNavigateCategory("fiscal")}
          className="p-3 bg-atlas-surface hover:bg-atlas-surface-elevated border border-atlas-border-subtle rounded cursor-pointer transition-colors"
        >
          <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
            <span className="flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5 text-indigo-400" />
              Government Finances & Public Debt
            </span>
          </div>
          <div className="flex items-center justify-between mt-2 font-mono text-xs">
            <span className="text-atlas-text-muted">General Gov Debt:</span>
            <span className="font-bold text-atlas-text-primary">
              {overview.general_gov_debt_pct_gdp !== null && overview.general_gov_debt_pct_gdp !== undefined
                ? `${overview.general_gov_debt_pct_gdp.toFixed(1)}% of GDP`
                : "—"}
            </span>
          </div>
          <div className="flex items-center justify-between mt-1 font-mono text-xs">
            <span className="text-atlas-text-muted">Fiscal Balance:</span>
            <span
              className={`font-bold ${
                (overview.fiscal_balance_pct_gdp || 0) < 0 ? "text-rose-400" : "text-emerald-400"
              }`}
            >
              {formatPct(overview.fiscal_balance_pct_gdp)} of GDP
            </span>
          </div>
        </div>

        {/* External Balance & FX Reserves */}
        <div
          onClick={() => onNavigateCategory("external")}
          className="p-3 bg-atlas-surface hover:bg-atlas-surface-elevated border border-atlas-border-subtle rounded cursor-pointer transition-colors"
        >
          <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
            <span className="flex items-center gap-1.5">
              <DollarSign className="w-3.5 h-3.5 text-cyan-400" />
              External Sector & Reserves
            </span>
          </div>
          <div className="flex items-center justify-between mt-2 font-mono text-xs">
            <span className="text-atlas-text-muted">Current Account:</span>
            <span
              className={`font-bold ${
                (overview.current_account_pct_gdp || 0) < 0 ? "text-amber-400" : "text-emerald-400"
              }`}
            >
              {formatPct(overview.current_account_pct_gdp)} of GDP
            </span>
          </div>
          <div className="flex items-center justify-between mt-1 font-mono text-xs">
            <span className="text-atlas-text-muted">FX Reserves:</span>
            <span className="font-bold text-atlas-text-primary">
              {formatCurrency(overview.fx_reserves_billions)}
            </span>
          </div>
        </div>

        {/* Structural Demographics */}
        <div
          onClick={() => onNavigateCategory("demographics")}
          className="p-3 bg-atlas-surface hover:bg-atlas-surface-elevated border border-atlas-border-subtle rounded cursor-pointer transition-colors"
        >
          <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
            <span className="flex items-center gap-1.5">
              <Building2 className="w-3.5 h-3.5 text-purple-400" />
              Demographics & Population
            </span>
          </div>
          <div className="flex items-center justify-between mt-2 font-mono text-xs">
            <span className="text-atlas-text-muted">Total Population:</span>
            <span className="font-bold text-atlas-text-primary">
              {overview.total_population_millions
                ? `${overview.total_population_millions.toFixed(1)} Million`
                : "—"}
            </span>
          </div>
          <div className="flex items-center justify-between mt-1 font-mono text-xs">
            <span className="text-atlas-text-muted">GDP Per Capita:</span>
            <span className="font-bold text-atlas-text-primary">
              ${overview.gdp_per_capita_usd?.toLocaleString() || "—"} USD
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
