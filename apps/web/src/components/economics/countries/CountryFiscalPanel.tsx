"use client";

import React from "react";
import {
  Scale,
  Landmark,
  Receipt,
  DollarSign,
  AlertTriangle,
  Info,
  ShieldCheck,
  Calendar,
} from "lucide-react";
import { CountryFiscalSummaryDTO } from "@/lib/economics/countries";

interface CountryFiscalPanelProps {
  fiscal: CountryFiscalSummaryDTO | null;
}

export function CountryFiscalPanel({ fiscal }: CountryFiscalPanelProps) {
  if (!fiscal) {
    return (
      <div className="p-8 text-center text-atlas-text-muted text-xs bg-atlas-surface border border-atlas-border-subtle rounded">
        No sovereign fiscal accounts or government debt statistics available for this country.
      </div>
    );
  }

  const formatPct = (val?: number | null) => {
    if (val === undefined || val === null) return "—";
    const sign = val > 0 ? "+" : "";
    return `${sign}${val.toFixed(1)}%`;
  };

  const formatBillions = (val?: number | null) => {
    if (val === undefined || val === null) return "—";
    return `$${val.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}B`;
  };

  return (
    <div className="space-y-4">
      {/* Fiscal Header Banner */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                Government Finances, Fiscal Balances & Public Debt
              </h3>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-indigo-400 border border-atlas-border-subtle">
                {fiscal.reference_period}
              </span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-atlas-text-secondary border border-atlas-border-subtle">
                {fiscal.accounting_scope.replace(/_/g, " ")}
              </span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-atlas-background text-atlas-text-secondary border border-atlas-border-subtle">
                {fiscal.accounting_basis} BASIS
              </span>
            </div>
            <p className="text-xs text-atlas-text-muted mt-1">
              Sovereign government revenues, primary deficits, gross public debt stock, and debt-to-GDP burden.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto font-mono text-xs">
            <span className="px-2.5 py-1 rounded bg-atlas-background border border-atlas-border-subtle text-atlas-text-muted flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              <span>{fiscal.fiscal_year}</span>
            </span>
          </div>
        </div>

        {/* Primary Fiscal Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 pt-4 border-t border-atlas-border-subtle">
          {/* Card 1: Fiscal Balance % GDP */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Overall Fiscal Balance</span>
              <span className="font-mono text-[10px]">% of GDP</span>
            </div>
            <div
              className={`text-xl font-bold font-mono mt-1 ${
                (fiscal.fiscal_balance_pct_gdp || 0) < 0 ? "text-rose-400" : "text-emerald-400"
              }`}
            >
              {formatPct(fiscal.fiscal_balance_pct_gdp)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Net: {formatBillions(fiscal.fiscal_balance_billions)}
            </div>
          </div>

          {/* Card 2: Primary Balance % GDP */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Primary Fiscal Balance</span>
              <span className="font-mono text-[10px]">% of GDP</span>
            </div>
            <div
              className={`text-xl font-bold font-mono mt-1 ${
                (fiscal.primary_balance_pct_gdp || 0) < 0 ? "text-amber-400" : "text-emerald-400"
              }`}
            >
              {formatPct(fiscal.primary_balance_pct_gdp)}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Excluding interest expenses
            </div>
          </div>

          {/* Card 3: Gross Debt % GDP */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Gross Public Debt</span>
              <span className="font-mono text-[10px]">% of GDP</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-primary mt-1">
              {fiscal.gross_debt_pct_gdp !== null && fiscal.gross_debt_pct_gdp !== undefined
                ? `${fiscal.gross_debt_pct_gdp.toFixed(1)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Stock: {formatBillions(fiscal.gross_debt_billions)}
            </div>
          </div>

          {/* Card 4: Net Debt % GDP */}
          <div className="p-3 bg-atlas-background/50 border border-atlas-border-subtle rounded">
            <div className="text-[11px] text-atlas-text-muted flex items-center justify-between">
              <span>Net Public Debt</span>
              <span className="font-mono text-[10px]">% of GDP</span>
            </div>
            <div className="text-xl font-bold font-mono text-atlas-text-secondary mt-1">
              {fiscal.net_debt_pct_gdp !== null && fiscal.net_debt_pct_gdp !== undefined
                ? `${fiscal.net_debt_pct_gdp.toFixed(1)}%`
                : "—"}
            </div>
            <div className="text-[11px] font-mono text-atlas-text-muted mt-1">
              Less liquid financial assets
            </div>
          </div>
        </div>
      </div>

      {/* Revenue and Expenditure Decomposition Table */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-atlas-border-subtle flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Receipt className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs font-bold text-atlas-text-primary tracking-tight">
              Government Budget Execution Accounts ({fiscal.accounting_scope.replace(/_/g, " ")})
            </h4>
          </div>
          <span className="text-[11px] font-mono text-atlas-text-muted">
            Official Treasury / Finance Ministry Accounts
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-atlas-background/50 border-b border-atlas-border-subtle text-[11px] font-mono text-atlas-text-muted uppercase">
                <th className="py-2.5 px-4 font-semibold">Budget Category</th>
                <th className="py-2.5 px-4 font-semibold text-center">Accounting Scope</th>
                <th className="py-2.5 px-4 font-semibold text-right">Amount (USD Billions)</th>
                <th className="py-2.5 px-4 font-semibold text-right">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle font-mono">
              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-emerald-400">
                  Total Government Revenue
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    {fiscal.accounting_scope}
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-emerald-400">
                  {formatBillions(fiscal.total_revenue_billions)}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Total receipts, tax revenues & sovereign duties
                </td>
              </tr>

              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-secondary pl-8">
                  ↳ of which: Tax Revenue
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    Tax Authority
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right text-atlas-text-secondary">
                  {formatBillions(fiscal.tax_revenue_billions)}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Direct income, corporate, payroll & consumption taxes
                </td>
              </tr>

              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-rose-400">
                  Total Government Expenditure
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    {fiscal.accounting_scope}
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-rose-400">
                  {formatBillions(fiscal.total_expenditure_billions)}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Outlays, mandatory programs, capital & interest
                </td>
              </tr>

              <tr className="hover:bg-atlas-surface-elevated/50 transition-colors">
                <td className="py-2.5 px-4 font-sans font-medium text-atlas-text-secondary pl-8">
                  ↳ of which: Debt Interest Payments
                </td>
                <td className="py-2.5 px-4 text-center text-atlas-text-muted">
                  <span className="px-1.5 py-0.5 rounded bg-atlas-background border border-atlas-border-subtle text-[10px]">
                    Debt Service
                  </span>
                </td>
                <td className="py-2.5 px-4 text-right text-atlas-text-secondary">
                  {formatBillions(fiscal.interest_expenditure_billions)}
                </td>
                <td className="py-2.5 px-4 text-right font-sans text-atlas-text-muted text-[11px]">
                  Net interest paid on outstanding sovereign debt
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Methodological Scope & Debt/GDP Timing Note */}
        <div className="p-3 bg-atlas-background/40 border-t border-atlas-border-subtle text-[11px] text-atlas-text-muted flex items-start gap-2">
          <Info className="w-3.5 h-3.5 shrink-0 text-atlas-accent mt-0.5" />
          <span>
            {fiscal.notes ||
              "Government debt is a stock measured at end of period, whereas GDP is an annual flow. Debt-to-GDP ratios are computed strictly against compatible calendar/fiscal-year nominal GDP flows."}
          </span>
        </div>
      </div>
    </div>
  );
}
