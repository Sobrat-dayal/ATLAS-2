"use client";

import React from "react";
import {
  TrendingUp,
  AlertCircle,
  PieChart,
  FileSpreadsheet,
  Info,
  CheckCircle2,
  Layers,
} from "lucide-react";
import {
  CountryGDPDecompositionDTO,
  CountryProductionDecompositionDTO,
} from "@/lib/economics/countries";

interface CountryGDPPanelProps {
  gdp: CountryGDPDecompositionDTO | null;
  production: CountryProductionDecompositionDTO | null;
}

export function CountryGDPPanel({ gdp, production }: CountryGDPPanelProps) {
  if (!gdp) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded">
        No national accounts GDP decomposition available for this country.
      </div>
    );
  }

  const formatCurrency = (val: number, curr: string = gdp.currency) => {
    return `${val.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })} ${curr}B`;
  };

  return (
    <div className="space-y-4">
      {/* GDP Header Metrics Banner */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                National Accounts: Gross Domestic Product (SNA / NIPA)
              </h3>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-atlas-accent border border-atlas-border-subtle">
                {gdp.reference_period}
              </span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-atlas-text-secondary border border-atlas-border-subtle">
                {gdp.price_basis}
              </span>
            </div>
            <p className="text-xs text-atlas-text-muted mt-1">
              Authoritative expenditure & production-side national accounts from official statistics bureau.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="text-right">
              <div className="text-[10px] text-atlas-text-muted">Nominal GDP</div>
              <div className="text-sm font-mono font-bold text-atlas-text-primary">
                {formatCurrency(gdp.nominal_gdp_billions)}
              </div>
            </div>
            <div className="h-6 w-px bg-atlas-border-subtle" />
            <div className="text-right">
              <div className="text-[10px] text-atlas-text-muted">Real GDP (Chained)</div>
              <div className="text-sm font-mono font-bold text-atlas-text-primary">
                {formatCurrency(gdp.real_gdp_billions)}
              </div>
            </div>
            {gdp.gdp_deflator_index && (
              <>
                <div className="h-6 w-px bg-atlas-border-subtle" />
                <div className="text-right">
                  <div className="text-[10px] text-atlas-text-muted">GDP Deflator</div>
                  <div className="text-sm font-mono font-bold text-atlas-text-secondary">
                    {gdp.gdp_deflator_index.toFixed(1)}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Growth and Per Capita Highlights */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 pt-4 border-t border-atlas-border-subtle text-xs">
          <div>
            <span className="text-atlas-text-muted text-[11px]">Real YoY Growth:</span>
            <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
              {gdp.real_growth_yoy !== null && gdp.real_growth_yoy !== undefined
                ? `${gdp.real_growth_yoy > 0 ? "+" : ""}${gdp.real_growth_yoy.toFixed(1)}%`
                : "—"}
            </div>
          </div>
          <div>
            <span className="text-atlas-text-muted text-[11px]">Real QoQ Annualized:</span>
            <div className="text-base font-bold font-mono text-blue-400 mt-0.5">
              {gdp.real_growth_qoq_ann !== null && gdp.real_growth_qoq_ann !== undefined
                ? `${gdp.real_growth_qoq_ann > 0 ? "+" : ""}${gdp.real_growth_qoq_ann.toFixed(1)}%`
                : "—"}
            </div>
          </div>
          <div>
            <span className="text-atlas-text-muted text-[11px]">GDP Per Capita (USD):</span>
            <div className="text-base font-bold font-mono text-atlas-text-primary mt-0.5">
              ${gdp.gdp_per_capita_usd?.toLocaleString() || "—"}
            </div>
          </div>
          <div>
            <span className="text-atlas-text-muted text-[11px]">Population Reference:</span>
            <div className="text-xs font-mono text-atlas-text-secondary mt-1">
              {gdp.per_capita_population_period ? `Census/Est (${gdp.per_capita_population_period})` : "—"}
            </div>
          </div>
        </div>
      </div>

      {/* Non-Additivity / Statistical Discrepancy Qualification */}
      <div
        className={`p-3 rounded-lg border text-xs flex items-start gap-2.5 ${
          gdp.is_strictly_additive
            ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-300"
            : "bg-amber-500/5 border-amber-500/20 text-amber-300"
        }`}
      >
        {gdp.is_strictly_additive ? (
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400 mt-0.5" />
        ) : (
          <AlertCircle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
        )}
        <div>
          <div className="font-semibold text-xs">
            {gdp.is_strictly_additive
              ? "National Accounts Additive Reconciliation Verified"
              : "Chain-Linked Volume Non-Additivity Disclosure (SNA Methodology)"}
          </div>
          <p className="text-[11px] text-atlas-text-muted mt-0.5">
            {gdp.non_additive_reason ||
              "In chained volume accounts, component sub-indices are chain-linked independently using Fisher or Laspeyres formulas and are not strictly additive outside reference base years."}
          </p>
        </div>
      </div>

      {/* Section 1: GDP by Expenditure Approach */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-atlas-border-subtle flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-atlas-accent" />
            <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
              GDP Expenditure Decomposition: C + I + G + (X - M)
            </h4>
          </div>
          <span className="text-[11px] font-mono text-atlas-text-muted">
            Total: {formatCurrency(gdp.total_calculated)}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-atlas-background/50 border-b border-atlas-border-subtle text-[11px] font-mono text-atlas-text-muted uppercase">
                <th className="py-2.5 px-4 font-semibold">Expenditure Component</th>
                <th className="py-2.5 px-4 font-semibold text-center">NIPA Code</th>
                <th className="py-2.5 px-4 font-semibold text-right">Value ({gdp.currency}B)</th>
                <th className="py-2.5 px-4 font-semibold text-right">Share of GDP (%)</th>
                <th className="py-2.5 px-4 font-semibold text-right">Growth Contribution (%p)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle font-mono">
              {gdp.components.map((comp) => {
                const isNegative = comp.value < 0;
                return (
                  <tr key={comp.component_id} className="hover:bg-atlas-surface-elevated/50 transition-colors">
                    <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary">
                      {comp.name}
                    </td>
                    <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                      <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                        {comp.code}
                      </span>
                    </td>
                    <td className={`py-2.5 px-4 text-right font-bold ${isNegative ? "text-rose-400" : "text-atlas-text-primary"}`}>
                      {comp.value.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
                    </td>
                    <td className="py-2.5 px-4 text-right text-atlas-text-secondary">
                      {comp.share_of_gdp_pct.toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      {comp.contribution_to_growth_pct_points !== null && comp.contribution_to_growth_pct_points !== undefined ? (
                        <span className={comp.contribution_to_growth_pct_points >= 0 ? "text-emerald-400" : "text-rose-400"}>
                          {comp.contribution_to_growth_pct_points > 0 ? "+" : ""}
                          {comp.contribution_to_growth_pct_points.toFixed(2)} %p
                        </span>
                      ) : (
                        <span className="text-atlas-text-muted">—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 2: GDP by Production / Sector Approach (Gross Value Added) */}
      {production && production.sectors.length > 0 && (
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-atlas-border-subtle flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
                Gross Value Added (GVA) by Production Sector: Agriculture, Industry & Services
              </h4>
            </div>
            <span className="text-[11px] font-mono text-atlas-text-muted">
              Total GVA: {formatCurrency(production.total_gva_billions, production.currency)}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-atlas-background/50 border-b border-atlas-border-subtle text-[11px] font-mono text-atlas-text-muted uppercase">
                  <th className="py-2.5 px-4 font-semibold">Production Sector</th>
                  <th className="py-2.5 px-4 font-semibold text-center">Classification</th>
                  <th className="py-2.5 px-4 font-semibold text-right">GVA ({production.currency}B)</th>
                  <th className="py-2.5 px-4 font-semibold text-right">Share of GVA (%)</th>
                  <th className="py-2.5 px-4 font-semibold text-right">Sector Growth YoY</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-subtle font-mono">
                {production.sectors.map((sec) => (
                  <tr key={sec.sector_id} className="hover:bg-atlas-surface-elevated/50 transition-colors">
                    <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-primary">
                      {sec.name}
                    </td>
                    <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                      <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                        {sec.code}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right font-bold text-atlas-text-primary">
                      {sec.value_added_billions.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
                    </td>
                    <td className="py-2.5 px-4 text-right text-atlas-text-secondary">
                      {sec.share_of_gva_pct.toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      {sec.growth_yoy !== null && sec.growth_yoy !== undefined ? (
                        <span className={sec.growth_yoy >= 0 ? "text-emerald-400" : "text-rose-400"}>
                          {sec.growth_yoy > 0 ? "+" : ""}{sec.growth_yoy.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-atlas-text-muted">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-3 bg-atlas-background/40 border-t border-atlas-border-subtle text-[11px] text-atlas-text-muted flex items-start gap-2">
            <Info className="w-3.5 h-3.5 shrink-0 text-atlas-accent mt-0.5" />
            <span>
              {production.notes ||
                "Gross Value Added (GVA) measures net output by sector at basic prices. Under SNA national accounting, GDP at market prices equals Total GVA plus taxes on products less subsidies on products."}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
