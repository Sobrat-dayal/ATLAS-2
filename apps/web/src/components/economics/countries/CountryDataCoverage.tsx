"use client";

import React from "react";
import { Check, X, ShieldCheck, Database, Calendar, Building2 } from "lucide-react";
import { CountryCoverageResponseDTO } from "@/lib/economics/countries";

interface CountryDataCoverageProps {
  coverage: CountryCoverageResponseDTO | null;
}

export function CountryDataCoverage({ coverage }: CountryDataCoverageProps) {
  if (!coverage) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded">
        Coverage matrix loading...
      </div>
    );
  }

  const items = [
    { label: "GDP Expenditure Decomposition", available: coverage.has_gdp_decomposition, domain: "National Accounts" },
    { label: "Gross Value Added (GVA) by Sector", available: coverage.has_production_gva, domain: "Production Accounts" },
    { label: "CPI Headline & Core Components", available: coverage.has_inflation_components, domain: "Prices & Inflation" },
    { label: "Labor Force & Household Surveys", available: coverage.has_labor_survey, domain: "Labor Market" },
    { label: "Industrial Production & Retail Sales", available: coverage.has_industry_indicators, domain: "Real Activity" },
    { label: "Monetary Aggregates & Bank Credit", available: coverage.has_monetary_aggregates, domain: "Monetary Sector" },
    { label: "Government Fiscal & Public Debt Accounts", available: coverage.has_fiscal_accounts, domain: "Fiscal Finances" },
    { label: "International Trade & Balance of Payments", available: coverage.has_external_bop, domain: "External Sector" },
    { label: "Population & Age Structure Demographics", available: coverage.has_demographics, domain: "Demographics" },
  ];

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-bold text-atlas-text-primary tracking-tight flex items-center gap-2">
            <Database className="w-3.5 h-3.5 text-atlas-accent" />
            <span>Sovereign Data Coverage & Official Statistical Lineage</span>
          </h3>
          <p className="text-[11px] text-atlas-text-muted mt-0.5">
            Verified canonical economic series coverage for {coverage.profile.name} ({coverage.profile.iso_code}).
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-[10px] text-atlas-text-muted self-start sm:self-auto">
          <span className="px-2 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle">
            {coverage.profile.supported_series_count} Verified Series
          </span>
          <span className="px-2 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle">
            {coverage.profile.earliest_observation_period} → {coverage.profile.latest_observation_period}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-2 border-t border-atlas-border-subtle text-xs">
        {items.map((item, idx) => (
          <div
            key={idx}
            className="p-2.5 rounded bg-atlas-background/50 border border-atlas-border-subtle flex items-center justify-between"
          >
            <div>
              <div className="font-medium text-atlas-text-primary text-[11px]">{item.label}</div>
              <div className="text-[10px] text-atlas-text-muted">{item.domain}</div>
            </div>
            {item.available ? (
              <span className="p-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" title="Verified Available">
                <Check className="w-3 h-3" />
              </span>
            ) : (
              <span className="p-1 rounded bg-atlas-surface text-atlas-text-muted border border-atlas-border-subtle" title="Unavailable">
                <X className="w-3 h-3" />
              </span>
            )}
          </div>
        ))}
      </div>

      <div className="pt-2 border-t border-atlas-border-subtle text-[11px] text-atlas-text-muted flex flex-wrap items-center justify-between gap-2">
        <span className="flex items-center gap-1.5">
          <Building2 className="w-3 h-3 text-atlas-accent" />
          Statistical Authority: <strong>{coverage.profile.statistical_agency}</strong>
        </span>
        <span className="flex items-center gap-1.5 font-mono text-[10px]">
          <ShieldCheck className="w-3 h-3 text-emerald-400" />
          Zero fabricated estimates · Canonical source observations only
        </span>
      </div>
    </div>
  );
}
