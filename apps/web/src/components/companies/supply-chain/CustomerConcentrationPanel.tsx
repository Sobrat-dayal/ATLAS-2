"use client";

import React from "react";
import {
  AlertTriangle,
  Building2,
  DollarSign,
  FileText,
  Info,
  Layers,
  PieChart,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { ConcentrationResponseDTO } from "@/lib/companies/supply-chain";

interface CustomerConcentrationPanelProps {
  concentration: ConcentrationResponseDTO | null;
}

export function CustomerConcentrationPanel({
  concentration,
}: CustomerConcentrationPanelProps) {
  if (!concentration) {
    return (
      <div className="p-8 text-center text-atlas-text-muted bg-atlas-surface border border-atlas-border-subtle rounded-md">
        No concentration or revenue dependency data available.
      </div>
    );
  }

  const hasCustomerConcentration = concentration.customer_concentration.length > 0;
  const hasSupplierConcentration = concentration.supplier_concentration.length > 0;

  return (
    <div className="space-y-4">
      {/* Overview Banner */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded-md flex items-start gap-3">
        <Info className="w-4 h-4 text-atlas-accent mt-0.5 shrink-0" />
        <div className="text-xs text-atlas-text-secondary leading-relaxed">
          <span className="font-semibold text-atlas-text-primary">Institutional Concentration Standard:</span>{" "}
          {concentration.qualitative_summary} Concentration metrics are source-qualified directly from
          audited financial statement segment footnotes (ASC 280 / IFRS 8). ATLAS strictly preserves
          anonymous disclosures without guessing company names.
        </div>
      </div>

      {/* Customer Concentration Section */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-md overflow-hidden">
        <div className="p-3 border-b border-atlas-border-subtle bg-atlas-surface-subtle/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <PieChart className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-semibold text-atlas-text-primary">
              Disclosed Customer Revenue Dependencies (ASC 280 Segment Disclosures)
            </h3>
          </div>
          <span className="text-[11px] font-mono text-atlas-text-muted">
            Fiscal Period: {concentration.reporting_period}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-atlas-border-subtle bg-atlas-surface-subtle text-atlas-text-muted font-medium text-[11px]">
                <th className="py-2.5 px-3">Disclosed Counterparty</th>
                <th className="py-2.5 px-3">Identity Status</th>
                <th className="py-2.5 px-3">Reported %</th>
                <th className="py-2.5 px-3">Dollar Exposure</th>
                <th className="py-2.5 px-3">Financial Scope</th>
                <th className="py-2.5 px-3">Denominator Context</th>
                <th className="py-2.5 px-3">Disclosed Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle text-atlas-text-secondary">
              {!hasCustomerConcentration ? (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-atlas-text-muted">
                    No customer accounts for &gt;10% of consolidated revenue based on SEC Form 10-K disclosures.
                  </td>
                </tr>
              ) : (
                concentration.customer_concentration.map((obs) => (
                  <tr key={obs.observation_id} className="hover:bg-atlas-surface-subtle/50 transition-colors">
                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-atlas-text-primary flex items-center gap-1.5">
                        <Building2 className="w-3.5 h-3.5 text-atlas-text-muted shrink-0" />
                        <span>{obs.counterparty_name}</span>
                      </div>
                      {obs.notes && (
                        <div className="text-[10px] text-atlas-text-muted mt-0.5 font-mono">{obs.notes}</div>
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      {obs.is_anonymous ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          <AlertTriangle className="w-2.5 h-2.5" />
                          ANONYMOUS IN FILING
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          DISCLOSED NAME
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      {obs.source_reported_percentage != null ? (
                        <span className="font-mono text-xs font-bold text-emerald-400">
                          {obs.source_reported_percentage.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-atlas-text-muted">—</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-atlas-text-primary">
                      {obs.exposure_amount_usd != null
                        ? `$${(obs.exposure_amount_usd / 1e9).toFixed(2)}B USD`
                        : "Undisclosed in 10-K"}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="font-mono text-[10px] bg-atlas-surface-subtle px-1.5 py-0.5 rounded border border-atlas-border-subtle">
                        {obs.scope.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-atlas-text-muted max-w-xs truncate">
                      {obs.denominator_description}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="text-[11px] font-mono text-atlas-text-secondary flex items-center gap-1">
                        <FileText className="w-3 h-3 text-atlas-text-muted" />
                        {obs.evidence_reference}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Supplier Concentration & Critical Inputs Section */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-md overflow-hidden">
        <div className="p-3 border-b border-atlas-border-subtle bg-atlas-surface-subtle/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <h3 className="text-xs font-semibold text-atlas-text-primary">
              Critical Supplier & Single-Source Input Dependencies
            </h3>
          </div>
          <span className="text-[11px] font-mono text-atlas-text-muted">
            Risk Factor Disclosures (Item 1A)
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-atlas-border-subtle bg-atlas-surface-subtle text-atlas-text-muted font-medium text-[11px]">
                <th className="py-2.5 px-3">Supplier Name</th>
                <th className="py-2.5 px-3">Critical Input / Component</th>
                <th className="py-2.5 px-3">Dependency Measure</th>
                <th className="py-2.5 px-3">Purchasing Scope</th>
                <th className="py-2.5 px-3">Disclosed Evidence Reference</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle text-atlas-text-secondary">
              {!hasSupplierConcentration ? (
                <tr>
                  <td colSpan={5} className="py-6 text-center text-atlas-text-muted">
                    No single-source or critical supplier concentration disclosed.
                  </td>
                </tr>
              ) : (
                concentration.supplier_concentration.map((obs) => (
                  <tr key={obs.observation_id} className="hover:bg-atlas-surface-subtle/50 transition-colors">
                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-atlas-text-primary flex items-center gap-1.5">
                        <Building2 className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                        <span>{obs.counterparty_name}</span>
                      </div>
                      <div className="text-[10px] text-atlas-text-muted mt-0.5 font-mono">
                        {obs.is_anonymous ? "Anonymous in filing" : "Identified Corporate Entity"}
                      </div>
                    </td>
                    <td className="py-2.5 px-3 font-medium text-atlas-text-primary">
                      {obs.notes || "Critical manufacturing service"}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="font-mono text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-1.5 py-0.5 rounded font-semibold">
                        CRITICAL SINGLE-SOURCE FOUNDRY
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-atlas-text-muted">
                      {obs.denominator_description}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="text-[11px] font-mono text-atlas-text-secondary flex items-center gap-1">
                        <FileText className="w-3 h-3 text-atlas-text-muted" />
                        {obs.evidence_reference}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
