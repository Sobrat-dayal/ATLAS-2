"use client";

import React from "react";
import {
  Percent,
  Flame,
  Apple,
  Factory,
  BarChart2,
  Calendar,
  CheckCircle2,
  Info,
} from "lucide-react";
import { CountryInflationSummaryDTO } from "@/lib/economics/countries";

interface CountryInflationPanelProps {
  inflation: CountryInflationSummaryDTO | null;
}

export function CountryInflationPanel({ inflation }: CountryInflationPanelProps) {
  if (!inflation) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded">
        No sovereign inflation or price index statistics available for this country.
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
      {/* Inflation Header Banner */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                Consumer Price Index (CPI) & Price Stability Intelligence
              </h3>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-rose-400 border border-atlas-border-subtle">
                {inflation.reference_period}
              </span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-atlas-text-secondary border border-atlas-border-subtle">
                Base: {inflation.cpi_index_base}
              </span>
            </div>
            <p className="text-xs text-atlas-text-muted mt-1">
              Official headline CPI, core inflation (ex-food & energy), component price indices, and producer inflation.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-atlas-background border border-atlas-border-subtle text-atlas-text-secondary">
              {inflation.seasonal_adjustment.replace(/_/g, " ")}
            </span>
          </div>
        </div>

        {/* Headline vs Core Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 pt-4 border-t border-atlas-border-subtle">
          {/* Card 1: Headline CPI YoY */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Headline CPI Inflation</span>
              <span className="font-mono text-[10px]">YoY</span>
            </div>
            <div className="text-xl font-bold font-mono text-rose-400 mt-1">
              {formatPct(inflation.headline_yoy)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Index Level: {inflation.cpi_index_level.toFixed(2)} pts
            </div>
          </div>

          {/* Card 2: Headline CPI MoM */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Monthly CPI Change</span>
              <span className="font-mono text-[10px]">MoM</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {formatPct(inflation.headline_mom)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Monthly sequential rate
            </div>
          </div>

          {/* Card 3: Core CPI YoY */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Core CPI (Ex-Food & Energy)</span>
              <span className="font-mono text-[10px]">YoY</span>
            </div>
            <div className="text-xl font-bold font-mono text-amber-400 mt-1">
              {formatPct(inflation.core_yoy)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Policy guidance anchor
            </div>
          </div>

          {/* Card 4: Core CPI MoM */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Core Monthly Change</span>
              <span className="font-mono text-[10px]">MoM</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {formatPct(inflation.core_mom)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Underlying price pressure
            </div>
          </div>
        </div>
      </div>

      {/* Component and Upstream Price Indices Table */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-atlas-border-subtle flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-atlas-accent" />
            <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
              Inflation Components & Upstream Price Indices
            </h4>
          </div>
          <span className="text-[11px] font-mono text-atlas-text-muted">
            Official Sub-Indices
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-atlas-background/50 border-b border-atlas-border-subtle text-[11px] font-mono text-atlas-text-muted uppercase">
                <th className="py-2.5 px-4 font-semibold">Price Component / Upstream Metric</th>
                <th className="py-2.5 px-4 font-semibold text-center">Type</th>
                <th className="py-2.5 px-4 font-semibold text-right">Rate YoY (%)</th>
                <th className="py-2.5 px-4 font-semibold text-right">Economic Meaning</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle font-mono">
              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary flex items-center gap-2">
                  <Apple className="w-3.5 h-3.5 text-emerald-400" />
                  Food & Non-Alcoholic Beverages
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    CPI Basket
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-atlas-text-primary">
                  {formatPct(inflation.food_inflation_yoy)}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Agricultural commodity pass-through
                </td>
              </tr>

              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary flex items-center gap-2">
                  <Flame className="w-3.5 h-3.5 text-rose-400" />
                  Energy & Fuel Sub-Index
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    CPI Basket
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-atlas-text-primary">
                  {formatPct(inflation.energy_inflation_yoy)}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Gasoline, electricity & heating utilities
                </td>
              </tr>

              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary flex items-center gap-2">
                  <Factory className="w-3.5 h-3.5 text-blue-400" />
                  Producer Price Index (PPI)
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    Factory Gate
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-atlas-text-primary">
                  {formatPct(inflation.ppi_yoy)}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Wholesale & domestic manufacturing output prices
                </td>
              </tr>

              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary flex items-center gap-2">
                  <Percent className="w-3.5 h-3.5 text-purple-400" />
                  GDP Implicit Price Deflator
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    Broad Economy
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-atlas-text-primary">
                  {formatPct(inflation.gdp_deflator_yoy)}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Economy-wide domestic production price deflator
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {inflation.notes && (
          <div className="p-3 bg-atlas-background/40 border-t border-atlas-border-subtle text-[11px] text-atlas-text-muted flex items-start gap-2">
            <Info className="w-3.5 h-3.5 shrink-0 text-atlas-accent mt-0.5" />
            <span>{inflation.notes}</span>
          </div>
        )}
      </div>
    </div>
  );
}
