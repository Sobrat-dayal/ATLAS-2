"use client";

import React from "react";
import {
  Landmark,
  Percent,
  Coins,
  CreditCard,
  Building,
  Info,
  ShieldCheck,
} from "lucide-react";
import { CountryMonetarySummaryDTO } from "@/lib/economics/countries";

interface CountryMonetaryPanelProps {
  monetary: CountryMonetarySummaryDTO | null;
}

export function CountryMonetaryPanel({ monetary }: CountryMonetaryPanelProps) {
  if (!monetary) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded">
        No monetary aggregates, credit indicators, or policy rate statistics available for this country.
      </div>
    );
  }

  const formatPct = (val?: number | null) => {
    if (val === undefined || val === null) return "—";
    const sign = val > 0 ? "+" : "";
    return `${sign}${val.toFixed(1)}%`;
  };

  return (
    <div className="space-y-4">
      {/* Monetary Banner */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                Monetary Conditions, Broad Money & Private Sector Credit
              </h3>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-emerald-400 border border-atlas-border-subtle">
                {monetary.reference_period}
              </span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-atlas-text-secondary border border-atlas-border-subtle">
                {monetary.monetary_area_name}
              </span>
            </div>
            <p className="text-xs text-atlas-text-muted mt-1">
              Central bank policy rate environment, money supply expansion (M1/M2), and domestic financial intermediation.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto font-mono text-xs">
            <span className="px-2.5 py-1 rounded bg-atlas-background border border-atlas-border-subtle text-atlas-text-primary flex items-center gap-1.5">
              <Landmark className="w-3.5 h-3.5 text-atlas-accent" />
              <span>{monetary.central_bank_name}</span>
            </span>
          </div>
        </div>

        {/* Monetary Highlights Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 pt-4 border-t border-atlas-border-subtle">
          {/* Card 1: Policy Rate */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Percent className="w-3.5 h-3.5 text-emerald-400" />
                Policy Interest Rate
              </span>
              <span className="font-mono text-[10px]">Benchmark</span>
            </div>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
              {monetary.policy_rate !== null && monetary.policy_rate !== undefined
                ? `${monetary.policy_rate.toFixed(2)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              {monetary.policy_rate_target_range ? `Target: ${monetary.policy_rate_target_range}` : "Central Bank Benchmark"}
            </div>
          </div>

          {/* Card 2: M2 Money Supply */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Coins className="w-3.5 h-3.5 text-blue-400" />
                M2 Broad Money Growth
              </span>
              <span className="font-mono text-[10px]">YoY</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {formatPct(monetary.m2_growth_yoy)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              M1 Narrow Money: {formatPct(monetary.m1_growth_yoy)}
            </div>
          </div>

          {/* Card 3: Domestic Credit to Private Sector */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <CreditCard className="w-3.5 h-3.5 text-purple-400" />
                Domestic Private Credit
              </span>
              <span className="font-mono text-[10px]">% GDP</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {monetary.domestic_credit_to_private_sector_pct_gdp !== null &&
              monetary.domestic_credit_to_private_sector_pct_gdp !== undefined
                ? `${monetary.domestic_credit_to_private_sector_pct_gdp.toFixed(1)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Banking system private depth
            </div>
          </div>

          {/* Card 4: Bank Lending Growth */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5 text-amber-400" />
                Bank Lending Growth
              </span>
              <span className="font-mono text-[10px]">YoY</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {formatPct(monetary.bank_lending_growth_yoy)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Commercial credit expansion
            </div>
          </div>
        </div>
      </div>

      {/* Stage 91 Boundary Notice */}
      <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded-lg text-[11px] text-atlas-text-muted flex items-start gap-2">
        <Info className="w-3.5 h-3.5 shrink-0 text-atlas-accent mt-0.5" />
        <div>
          <span className="font-semibold text-atlas-text-secondary">Stage Boundary Preservation:</span> Country Economics provides source-qualified sovereign monetary indicators and policy rate context. Comprehensive central bank balance sheet analysis, meeting minutes, policy voting records, and speech archives will be delivered in Stage 91 — Central Banks.
        </div>
      </div>

      {monetary.notes && (
        <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded-lg text-[11px] text-atlas-text-muted">
          {monetary.notes}
        </div>
      )}
    </div>
  );
}
